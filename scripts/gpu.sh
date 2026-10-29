#!/bin/bash
# Run a command on the GPU, booking it first when the machine is shared.
#
#   scripts/gpu.sh --hours 2 --vram 12 -- uv run omalaka-train ...
#
# If OMALAKA_GPU_RUN points to a booking tool with the interface
#   TOOL run --owner OWNER --vram GB --hours H -- COMMAND...
# the command runs under it as OMALAKA_GPU_OWNER (default: omalaka).
# Otherwise it just runs. OMALAKA_GPU_PRE is an optional command run first,
# for example to unload a local LLM server that holds GPU memory.
set -euo pipefail
hours=2 vram=12
while [ $# -gt 0 ]; do
  case "$1" in
    --hours) hours=$2; shift 2 ;;
    --vram) vram=$2; shift 2 ;;
    --) shift; break ;;
    *) break ;;
  esac
done
[ $# -gt 0 ] || { echo "usage: $0 [--hours H] [--vram GB] -- COMMAND..." >&2; exit 2; }
if [ -n "${OMALAKA_GPU_PRE:-}" ]; then bash -c "$OMALAKA_GPU_PRE" || true; fi
if [ -n "${OMALAKA_GPU_RUN:-}" ]; then
  exec python "$OMALAKA_GPU_RUN" run --owner "${OMALAKA_GPU_OWNER:-omalaka}" --vram "$vram" --hours "$hours" -- "$@"
fi
exec "$@"
