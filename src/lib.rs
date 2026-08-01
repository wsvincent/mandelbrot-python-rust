#[pyo3::pymodule]
mod _fast {
    use pyo3::prelude::*;

    const LOG2: f64 = std::f64::consts::LN_2;
    
    #[pyfunction]
    fn escape_count(cx: f64, cy: f64, max_iter: u32) -> (f64, u32) {
        let mut x = 0.0f64;
        let mut y = 0.0f64;
        let mut x2 = 0.0f64;
        let mut y2 = 0.0f64;
        let mut i = 0u32;
        while x2 + y2 <= 4.0 && i < max_iter {
            y = 2.0 * x * y + cy;
            x = x2 - y2 + cx;
            x2 = x * x;
            y2 = y * y;
            i += 1;
        }

        if i >= max_iter {
            return (-1.0, i);
        }

        // Continuous (fractional) escape count, so bands don't show as hard edges.
        let log_zn = (x2 + y2).ln() / 2.0;
        let nu = (log_zn / LOG2).ln() / LOG2;
        (i as f64 + 1.0 - nu, i)
    }
}
