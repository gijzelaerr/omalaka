"""Fine-tune a translation model Oshiwambo -> English on DATA/train.jsonl.

usage: omalaka-train MODEL OUT_DIR [--data splits] [--lora] [--epochs N] [--batch B] [--lr LR]
Resumable: every --save-every steps the full state (weights, optimizer,
scheduler, position in the data, RNG) goes to OUT_DIR/last, and the adapter
alone to OUT_DIR/ckpt-STEP for scoring. Run the same command again after a
crash or reboot and it carries on from OUT_DIR/last.
MODEL: facebook/m2m100_418M, facebook/m2m100_1.2B or google/madlad400-3b-mt.
"""
import argparse
import json
import math
import random
import shutil
import time
from pathlib import Path

import sacrebleu
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, get_linear_schedule_with_warmup

from .common import AUTOCAST, DEVICE, RELIGIOUS, Translator, is_madlad, load_jsonl


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("model")
    p.add_argument("out")
    p.add_argument("--data", default="splits", help="directory with train.jsonl and dev.jsonl (omalaka-prepare)")
    p.add_argument("--lora", action="store_true")
    p.add_argument("--epochs", type=float, default=1.0)
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--accum", type=int, default=1)
    p.add_argument("--lr", type=float, default=None)
    p.add_argument("--max-len", type=int, default=128)
    p.add_argument("--eval-every", type=int, default=1500)
    p.add_argument("--checkpointing", action="store_true", help="trade speed for memory (MADLAD 3B)")
    p.add_argument("--max-steps", type=int, help="stop early (smoke test)")
    p.add_argument("--max-minutes", type=float, help="stop after this long, with a final evaluation")
    p.add_argument("--save-every", type=int, default=0, help="resumable state and a scored checkpoint every N steps")
    p.add_argument("--drop-religious", action="store_true", help="leave out pairs whose English has religious wording")
    args = p.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    random.seed(7)
    torch.manual_seed(7)

    tok = AutoTokenizer.from_pretrained(args.model)
    dtype = torch.bfloat16 if args.lora else torch.float32
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model, dtype=dtype).to(DEVICE)
    if args.lora:
        from peft import LoraConfig, get_peft_model
        targets = ["q", "k", "v", "o", "wi_0", "wi_1", "wo"] if is_madlad(args.model) else \
            ["q_proj", "k_proj", "v_proj", "out_proj", "fc1", "fc2"]
        model = get_peft_model(model, LoraConfig(r=32, lora_alpha=64, lora_dropout=0.05, target_modules=targets))
        model.print_trainable_parameters()
    if args.checkpointing:
        model.gradient_checkpointing_enable()
        model.enable_input_require_grads()
    lr = args.lr or (3e-4 if args.lora else 5e-5)

    translator = Translator(model, tok, args.model)
    train = load_jsonl(Path(args.data) / "train.jsonl")
    if args.drop_religious:
        train = [r for r in train if not RELIGIOUS.search(r["tgt"])]
    dev = load_jsonl(Path(args.data) / "dev.jsonl")[:300]


    def batches(epoch):
        """Length-bucketed batches: sort chunks of 100 batches by length, then shuffle the batches.

        Seeded per epoch, so a resumed run sees the same order and can skip ahead.
        """
        rng = random.Random(7 + epoch)
        data = train[:]
        rng.shuffle(data)
        size = args.batch * 100
        groups = []
        for i in range(0, len(data), size):
            chunk = sorted(data[i:i + size], key=lambda r: len(r["src"]))
            groups += [chunk[j:j + args.batch] for j in range(0, len(chunk), args.batch)]
        rng.shuffle(groups)
        return groups


    def encode(rows):
        enc = tok([translator.source(r["src"]) for r in rows], text_target=[r["tgt"] for r in rows],
                  max_length=args.max_len, truncation=True, padding=True, return_tensors="pt")
        enc["labels"][enc["labels"] == tok.pad_token_id] = -100
        return {k: v.to(DEVICE) for k, v in enc.items()}


    def evaluate():
        model.eval()
        hyps = translator.translate([r["src"] for r in dev], beams=1)
        model.train()
        return sacrebleu.corpus_chrf([h for h in hyps], [[r["tgt"] for r in dev]], word_order=2).score


    steps_per_epoch = math.ceil(len(train) / args.batch / args.accum)
    total = min(int(steps_per_epoch * args.epochs), args.max_steps or 10**9)
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=lr, weight_decay=0.0)
    sched = get_linear_schedule_with_warmup(opt, min(500, total // 10), total)
    log = open(out / "train_log.jsonl", "a", encoding="utf-8")
    step, best, epoch, skip, spent = 0, -1.0, 0, 0, 0.0
    state_file = out / "last" / "state.pt"
    if state_file.exists():
        state = torch.load(state_file, weights_only=False)
        if args.lora:
            from peft import set_peft_model_state_dict
            from safetensors.torch import load_file
            set_peft_model_state_dict(model, load_file(out / "last" / "adapter_model.safetensors"))
        else:
            model.load_state_dict(state["model"])
        opt.load_state_dict(state["opt"])
        sched.load_state_dict(state["sched"])
        step, best, epoch, skip, spent = state["step"], state["best"], state["epoch"], state["batch"], state["spent"]
        total = state["total"]
        torch.set_rng_state(state["rng"])
        print(f"resumed at step {step}/{total} (epoch {epoch}, batch {skip})", flush=True)
    else:
        print(f"{len(train)} pairs, {total} steps, lr {lr}, start dev chrF++ {evaluate():.1f}", flush=True)


    def save_state(batch_done):
        """Write to last.tmp and swap, so a crash mid-save keeps the previous state."""
        tmp, last = out / "last.tmp", out / "last"
        if tmp.exists():
            shutil.rmtree(tmp)
        tmp.mkdir()
        state = {"opt": opt.state_dict(), "sched": sched.state_dict(), "step": step, "best": best,
                 "epoch": epoch, "batch": batch_done, "total": total, "rng": torch.get_rng_state(),
                 "spent": spent + time.time() - started}
        if args.lora:
            model.save_pretrained(tmp)
        else:
            state["model"] = model.state_dict()
        torch.save(state, tmp / "state.pt")
        if last.exists():
            shutil.rmtree(last)
        tmp.rename(last)
        if args.lora:
            model.save_pretrained(out / f"ckpt-{step}")
            tok.save_pretrained(out / f"ckpt-{step}")


    model.train()
    started, running = time.time(), 0.0
    first_step = step
    while step < total:
        groups = batches(epoch)
        for i, rows in enumerate(groups):
            if i < skip:
                continue
            with torch.autocast(AUTOCAST, dtype=torch.bfloat16):
                loss = model(**encode(rows)).loss / args.accum
            loss.backward()
            running += loss.item()
            if (i + 1) % args.accum:
                continue
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step()
            sched.step()
            opt.zero_grad(set_to_none=True)
            step += 1
            if step % 100 == 0:
                rate = (step - first_step) / (time.time() - started)
                print(f"step {step}/{total} loss {running * args.accum / (100 * args.accum):.3f} {rate:.2f} it/s "
                      f"eta {(total - step) / rate / 60:.0f} min", flush=True)
                running = 0.0
            out_of_time = args.max_minutes and spent + time.time() - started > args.max_minutes * 60
            if out_of_time:
                total = step
            if step % args.eval_every == 0 or step == total:
                score = evaluate()
                log.write(json.dumps({"step": step, "dev_chrf": score, "t": time.time() - started}) + "\n")
                log.flush()
                print(f"step {step} dev chrF++ {score:.1f}", flush=True)
                if score > best:
                    best = score
                    model.save_pretrained(out / "best")
                    tok.save_pretrained(out / "best")
            if args.save_every and (step % args.save_every == 0 or step >= total):
                save_state(i + 1)
            if step >= total:
                break
        else:
            epoch, skip = epoch + 1, 0
            continue
        skip = 0
    print(f"done, best dev chrF++ {best:.1f}, {(spent + time.time() - started) / 60:.0f} min", flush=True)
    (out / "DONE").write_text(str(step))


if __name__ == "__main__":
    main()
