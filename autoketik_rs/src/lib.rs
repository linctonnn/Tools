use pyo3::prelude::*;
use std::{thread, time};

#[pyfunction]
fn autoketik(message: &str) {
    for c in message.chars() {
        print!("{}", c);
        std::io::Write::flush(&mut std::io::stdout()).unwrap();
        thread::sleep(time::Duration::from_millis(50));
    }
    println!();
}

#[pymodule]
fn autoketik_rs(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(autoketik, m)?)?;
    Ok(())
}
