"""Download open datasets into data/NAME/ and record where each file came from.

usage: omalaka-download [NAME ...] [--data data]     (no NAME: every dataset but synthetic-madlad)
       omalaka-download --list
synthetic-madlad needs a GPU and takes options: run omalaka-synthetic instead.
"""
import argparse
from pathlib import Path

from .datasets import registry


def main(argv=None):
    sets = registry()
    p = argparse.ArgumentParser()
    p.add_argument("names", nargs="*", metavar="NAME", help=", ".join(sets))
    p.add_argument("--data", default="data")
    p.add_argument("--list", action="store_true", help="show every dataset with its licence and status")
    args = p.parse_args(argv)
    if args.list:
        for name, mod in sets.items():
            i = mod.INFO
            print(f"{name:18} {i['kind']:9} {','.join(i['langs']):6} {i['licence']:13} {i['status']}")
        return
    if unknown := set(args.names) - set(sets):
        p.error(f"unknown dataset(s): {', '.join(sorted(unknown))}")
    for name in args.names or [n for n, m in sets.items() if m.INFO["kind"] != "synthetic"]:
        print(f"{name}: {sets[name].fetch(Path(args.data) / name)} rows", flush=True)


if __name__ == "__main__":
    main()
