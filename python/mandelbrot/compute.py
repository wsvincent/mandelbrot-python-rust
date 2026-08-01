import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Imported only for editors and type checkers. At runtime load_fast()
    # imports it lazily, so `--mode python` still works with nothing built.
    from mandelbrot import _fast

LOG2 = math.log(2.0)

MODES = ("python", "rust")

# The classic "Ultra Fractal" gradient used by the Mandelbrot images on
# Wikipedia: (stop position, R, G, B). The final stop repeats the first so
# that the palette cycles smoothly.
PALETTE = (
    (0.0000, (0, 7, 100)),
    (0.1600, (32, 107, 203)),
    (0.4200, (237, 255, 255)),
    (0.6425, (255, 170, 0)),
    (0.8575, (0, 2, 0)),
    (1.0000, (0, 7, 100)),
)


def escape_count(cx, cy, max_iter):
    x = 0.0
    y = 0.0
    x2 = 0.0
    y2 = 0.0
    i = 0
    while x2 + y2 <= 4.0 and i < max_iter:
        y = 2.0 * x * y + cy
        x = x2 - y2 + cx
        x2 = x * x
        y2 = y * y
        i += 1

    if i >= max_iter:
        return -1.0, i

    # Continuous (fractional) escape count, so bands don't show as hard edges.
    log_zn = math.log(x2 + y2) / 2.0
    nu = math.log(log_zn / LOG2) / LOG2
    return i + 1.0 - nu, i


def colour(v, density):
    """Map a smoothed escape count onto the palette."""
    if v < 0.0:
        return 0, 0, 0  # inside the set

    # sqrt spreads out the low escape counts, which is where all the detail
    # is; the fractional part cycles the palette across the image.
    t = math.sqrt(v) * density
    t -= math.floor(t)

    for i in range(len(PALETTE) - 1):
        pos0, c0 = PALETTE[i]
        pos1, c1 = PALETTE[i + 1]
        if t <= pos1:
            f = (t - pos0) / (pos1 - pos0)
            return (
                int(c0[0] + f * (c1[0] - c0[0])),
                int(c0[1] + f * (c1[1] - c0[1])),
                int(c0[2] + f * (c1[2] - c0[2])),
            )
    return PALETTE[-1][1]


def load_fast() -> "_fast":
    try:
        from mandelbrot import _fast
    except ImportError as exc:  # pragma: no cover - depends on build state
        raise SystemExit(
            "the Rust extension module is not built.\n"
            "Build it into the current environment with:\n\n"
            "    uvx maturin@1 develop --release\n"
        ) from exc
    return _fast


def render(
    width,
    height,
    centre_x,
    centre_y,
    span,
    max_iter,
    density,
    mode="python",
    on_row=None,
):

    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}, expected one of {MODES}")

    # This line is the whole demo. Everything below it is identical either
    # way -- only the implementation of escape_count changes. Ctrl-click
    # either one to land on its source, Python here or Rust via `_fast.pyi`.
    escape = escape_count if mode == "python" else load_fast().escape_count

    scale = span / width
    left = centre_x - span / 2.0
    top = centre_y + (height * scale) / 2.0

    raw = bytearray()
    iterations = 0
    for py in range(height):
        raw.append(0)  # PNG per-scanline filter type: none
        cy = top - py * scale
        for px in range(width):
            cx = left + px * scale
            v, n = escape(cx, cy, max_iter)
            iterations += n
            r, g, b = colour(v, density)
            raw.append(r)
            raw.append(g)
            raw.append(b)
        if on_row is not None and (py % 16 == 0 or py == height - 1):
            on_row(py + 1, height)
    return bytes(raw), iterations
