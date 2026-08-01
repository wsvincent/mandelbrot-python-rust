# Build the Rust extension module into the local virtualenv.
develop:
    uvx maturin@1 develop --release

# Build a release wheel.
build:
    uvx maturin@1 build --release

# Pure-Python escape_count -- the slow one.
run-python *ARGS:
    .venv/bin/python -m mandelbrot --mode python {{ARGS}}

# Rust escape_count, called per pixel from the same Python loop.
run-rust *ARGS:
    .venv/bin/python -m mandelbrot --mode rust {{ARGS}}

# Time both and check they agree.
bench *ARGS:
    ./bench.sh {{ARGS}}
