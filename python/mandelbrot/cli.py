"""Command line interface."""

import argparse
import sys
import time
from pathlib import Path

from mandelbrot.compute import MODES, load_fast, render
from mandelbrot.image import write_png

# Renders land here rather than cluttering the project root.
IMG_DIR = Path("img")

# "Seahorse Valley", the region of the set centred on -0.75 + 0.1i.
DEFAULTS = {
    "width": 800,
    "height": 600,
    "max_iter": 5000,
    "centre_x": -0.7447,
    "centre_y": 0.1125,
    "span": 0.0095,
    "density": 0.25,
}


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="mandelbrot",
        description="Render the Mandelbrot set to a PNG.",
    )
    p.add_argument(
        "-m", "--mode", choices=MODES, default="python",
        help="which escape_count implementation to use (default: python)",
    )
    p.add_argument("-w", "--width", type=int, default=DEFAULTS["width"],
                   help="image width in pixels")
    p.add_argument("-H", "--height", type=int, default=DEFAULTS["height"],
                   help="image height in pixels")
    p.add_argument("-i", "--max-iter", type=int, default=DEFAULTS["max_iter"],
                   help="iteration limit")
    p.add_argument("-x", "--centre-x", type=float, default=DEFAULTS["centre_x"],
                   help="view centre, real part")
    p.add_argument("-y", "--centre-y", type=float, default=DEFAULTS["centre_y"],
                   help="view centre, imaginary part")
    p.add_argument("-s", "--span", type=float, default=DEFAULTS["span"],
                   help="view width in the complex plane")
    p.add_argument("-d", "--density", type=float, default=DEFAULTS["density"],
                   help="palette cycling density")
    p.add_argument("-o", "--output", default=None,
                   help="output PNG path (default: img/mandelbrot-<mode>.png)")
    p.add_argument("-q", "--quiet", action="store_true",
                   help="suppress the progress bar")
    return p.parse_args(argv)


def progress_bar(done, total):
    filled = 30 * done // total
    bar = "#" * filled + "-" * (30 - filled)
    sys.stderr.write(f"\r  rendering [{bar}] {100 * done // total:3d}%")
    sys.stderr.flush()


def main(argv=None):
    args = parse_args(argv)
    output = Path(args.output) if args.output else IMG_DIR / f"mandelbrot-{args.mode}.png"
    output.parent.mkdir(parents=True, exist_ok=True)

    print(f"mode {args.mode}")
    print(f"  {args.width}x{args.height}, max_iter={args.max_iter}")
    print(f"  centre {args.centre_x:+.6f}{args.centre_y:+.6f}i, span {args.span}")

    on_row = None if args.quiet else progress_bar

    # Load the extension before starting the clock. The first load of a
    # freshly built .so costs the OS a few hundred milliseconds to validate,
    # which would otherwise land in the timing and flatter pure Python.
    if args.mode != "python":
        load_fast()

    t0 = time.perf_counter()
    raw, iterations = render(
        args.width,
        args.height,
        args.centre_x,
        args.centre_y,
        args.span,
        args.max_iter,
        args.density,
        mode=args.mode,
        on_row=on_row,
    )
    t1 = time.perf_counter()
    if on_row is not None:
        sys.stderr.write("\n")

    write_png(output, args.width, args.height, raw)
    t2 = time.perf_counter()

    pixels = args.width * args.height
    compute = t1 - t0
    print(f"  compute  {compute:8.3f} s   ({pixels / compute:,.0f} px/s)")
    print(
        f"  iters    {iterations / 1e6:8.1f} M   "
        f"({iterations / compute / 1e6:,.1f} M iter/s)"
    )
    print(f"  encode   {t2 - t1:8.3f} s")
    print(f"  total    {t2 - t0:8.3f} s   -> {output}")


if __name__ == "__main__":
    main()
