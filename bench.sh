#!/usr/bin/env bash
#
# Render the same viewport with each implementation and report the speedup.
# Extra arguments are passed through to every run, e.g.
#
#     ./bench.sh --width 1600 --height 1200 --max-iter 2000
#
set -euo pipefail

cd "$(dirname "$0")"

if [[ -d .venv ]]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
fi

if ! python -c 'import mandelbrot._fast' 2>/dev/null; then
    echo "building the Rust extension module first..."
    uvx maturin@1 develop --release
fi

timings=""
iters=""
for mode in python rust; do
    echo
    echo "=== $mode ==============================================="
    out=$(python -m mandelbrot --mode "$mode" --quiet "$@")
    echo "$out"
    timings="$timings $(echo "$out" | awk '/compute/ {print $2}')"
    iters="$iters $(echo "$out" | awk '/iters/ {print $2}')"
done

echo
echo "=== Result ======================================================"
# shellcheck disable=SC2086
python - $timings $iters <<'EOF'
import sys
py, rs = (float(a) for a in sys.argv[1:3])
counts = [float(a) for a in sys.argv[3:5]]

# Both modes walk the same viewport, so the iteration total must agree.
if len(set(counts)) == 1:
    print(f"  workload{' ' * 33}{counts[0]:8.1f} M iterations")
else:
    print(f"  workload{' ' * 33}MISMATCH {counts} -- modes disagree")

print(f"  {'mode':<12}{'escape_count':<16}{'time':>9}{'throughput':>16}{'speedup':>11}")
for mode, what, secs in (
    ("python", "pure Python", py),
    ("rust", "Rust", rs),
):
    print(
        f"  {mode:<12}{what:<16}{secs:8.3f}s"
        f"{counts[0] / secs:12.0f} M/s"
        f"{py / secs:10.1f}x"
    )
EOF

# Both modes should produce exactly the same pixels. Compare the decompressed
# image data rather than the PNG bytes, so compression choices don't matter.
python - <<'EOF'
import struct, zlib

def pixels(path):
    data = open(path, "rb").read()[8:]
    idat = b""
    while data:
        n = struct.unpack(">I", data[:4])[0]
        if data[4:8] == b"IDAT":
            idat += data[8 : 8 + n]
        data = data[12 + n :]
    return zlib.decompress(idat)

ref = pixels("img/mandelbrot-python.png")
same = pixels("img/mandelbrot-rust.png") == ref
print(f"  {'pixels':<28}{'identical' if same else 'DIFFER -- implementations have drifted'}")
EOF
echo
