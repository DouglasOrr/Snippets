use util;

/// Select between some pretty rendering modes
#[derive(Debug, PartialEq, Clone, Copy)]
pub enum Mode {
    Basic,
    Fancy
}
#[derive(Debug, PartialEq, Clone)]
pub struct ParseModeError {
    value: String
}
impl ::std::str::FromStr for Mode {
    type Err = ParseModeError;
    fn from_str(s: &str) -> Result<Mode, ParseModeError> {
        match &s.to_lowercase() as &str {
            "basic" => Ok(Mode::Basic),
            "fancy" => Ok(Mode::Fancy),
            _ => Err(ParseModeError{value: s.to_string()})
        }
    }
}

type Complex = ::num::complex::Complex<f32>;

fn step(z: &Complex, a: &Complex) -> Complex {
    z * z + a
}
fn iterate(a: &Complex, n: u32) -> f32 {
    let mut z = *a;
    for _ in 1..n {
        z = step(&z, &a);
    }
    z.norm()
}
fn escape(a: &Complex, max_iter: u32) -> Option<u32> {
    let mut z = *a;
    for i in 1..max_iter {
        z = step(&z, &a);
        if 2f32 < z.norm() { return Some(i) }
    }
    return None
}
fn contains(a: &Complex, n: u32) -> bool {
    iterate(a, n) <= 2f32
}

/// Render a single pixel of a Mandelbrot visualization
pub fn render(x: f32, y: f32, max_iterations: u32, mode: Mode) -> ::image::Rgba<u8> {
    match escape(&Complex::new(x, y), max_iterations) {
        None => util::rgba(0.0, 0.0, 0.0, 1.0),
        Some(_) if mode == Mode::Basic => util::rgba(0.0, 0.0, 0.0, 0.0),
        Some(n) if mode == Mode::Fancy => {
            let i = (n as f32 / max_iterations as f32).powf(0.2);
            let hue = ((i + 0.5) % 1.0) * 2.0 * ::std::f32::consts::PI;
            util::hsva(hue, 1.0, 1.0, 1.0)
        },
        Some(_) => panic!("Unexpected case - unknown mode?")
    }
}
