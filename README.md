# mandelbrot-python-rust

A command line tool rendering images of the [Mandelbrot set](https://en.wikipedia.org/wiki/Mandelbrot_set) in pure Python and with core function, `escape_count`, rewritten in Rust with [PyO3](https://pyo3.rs) and [maturin](https://www.maturin.rs). `src/lib.rs` is deliberately tiny — one `#[pyfunction]` and nothing else.

![Seahorse Valley](img/seahorse-valley.png)

## The numbers

Same viewport, same **453 million iterations** of `z = z² + c`, same everything
— except which `escape_count` gets called. Run on an Apple M4 Max.

| mode | `escape_count` | time | throughput | speedup |
| --- | --- | ---: | ---: | ---: |
| `python` | pure Python | 20.73 s | 22 M iter/s | 1× |
| `rust` | Rust | 1.06 s | 427 M iter/s | **19×** |

**Pure Python**

![Python Mode](img/mode-python.png)

**Rust**

![Rust Mode](img/mode-rust.png)

Python still owns the pixel loop, the palette, the progress bar and the PNG
writer, and still crosses into Rust 480,000 times — once per pixel. One
function moved — 20.7 s down to 1.1 s, 22 M iter/s up to 427 M — and it's
worth **19×**.

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
