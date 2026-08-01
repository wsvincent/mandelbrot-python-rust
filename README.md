# mandelbrot-python-rust

A command line tool rendering images of the [Mandelbrot set](https://en.wikipedia.org/wiki/Mandelbrot_set) in pure Python and with core function, `escape_count`, rewritten in Rust with [PyO3](https://pyo3.rs) and [maturin](https://www.maturin.rs).

![Seahorse Valley](img/seahorse-valley.png)

`src/lib.rs` is deliberately tiny — one `#[pyfunction]` and nothing else.

## The numbers

At the default 800×600 with a 5000 iteration limit, the viewport works out to
**453 million iterations** of `z = z² + c`, which is the real unit of work here
— the pixel count is fixed, but how many times each pixel goes round the loop
is what the iteration limit actually buys you.

| mode | `escape_count` | time | throughput | speedup |
| --- | --- | ---: | ---: | ---: |
| `python` | pure Python | 20.96 s | 22 M iter/s | 1× |
| `rust` | Rust | 1.14 s | 397 M iter/s | **18×** |

Nothing else changes between the two runs. Python still owns the pixel loop,
the palette, the progress bar and the PNG writer, and still crosses into Rust
480,000 times — once per pixel. The only difference is which `escape_count`
gets called, and it's worth 18×.

Raising the iteration limit widens the gap rather than just scaling both sides:
Python holds flat at 22 M iter/s however long the loop runs, while Rust climbs
from 329 M iter/s at `--max-iter 1000` to 397 M iter/s at 5000. The per-call
cost of crossing into Rust is fixed, so the longer each call stays in the loop,
the less that crossing costs relative to the work it does.

## Setup

Requires Python 3.10+, a Rust toolchain via [rustup](https://rustup.rs), and
[uv](https://docs.astral.sh/uv/).

```sh
uv venv
uv pip install pip          # maturin develop shells out to pip
just develop                # or: uvx maturin@1 develop --release
```

`develop` compiles `src/lib.rs` and installs it into `.venv` as
`mandelbrot._fast`.

## Running it

```sh
just bench                  # both modes, side by side
just run-python             # pure-Python escape_count
just run-rust               # Rust escape_count
```

Or drive it directly:

```sh
.venv/bin/python -m mandelbrot \
    --mode rust \
    --width 1600 --height 1200 --max-iter 10000 \
    --centre-x -0.7447 --centre-y 0.1125 --span 0.0095 \
    --output img/seahorse.png
```

Each run reports what it did:

```
mode rust
  800x600, max_iter=5000
  centre -0.744700+0.112500i, span 0.0095
  compute     1.142 s   (420,398 px/s)
  iters       453.0 M   (396.7 M iter/s)
  encode      0.025 s
  total       1.167 s   -> img/mandelbrot-rust.png
```
