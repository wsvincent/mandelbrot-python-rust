"""Type stub for the compiled Rust extension module.

The implementation lives in `src/lib.rs`. This file exists so that Python
tooling can see the module's API without importing the compiled `.so` --
and, in PyCharm 2026.2+ with the Rust plugin, so you can jump straight from
the declaration here to the `#[pyfunction]` that implements it, and back.

Keep the name here identical to the Rust one or that navigation breaks.
"""

def escape_count(cx: float, cy: float, max_iter: int) -> tuple[float, int]:
    """Iterate z = z^2 + c and return `(smoothed escape count, iterations)`.

    A drop-in replacement for `mandelbrot.compute.escape_count`.
    """
