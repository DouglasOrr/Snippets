/// Some basic image helper utilities for the Mandelbrot rendering Dojo.
pub mod util;

/// Our custom, beautiful, Mandelbrot rendering.
pub mod mandelbrot;

extern crate image;
extern crate num;
extern crate argparse;

fn main() {
    // Parameters
    let mut iterations = 20;
    let mut width_px = 500u32;
    let (mut xmin, mut xmax) = (-2.0, 0.8);
    let (mut ymin, mut ymax) = (-1.2, 1.2);
    let mut out = "mandelbrot.png".to_string();
    let mut mode = mandelbrot::Mode::Basic;
    {
        let mut ap = argparse::ArgumentParser::new();
        ap.set_description("Render a visualisation of the Mandelbrot set");
        ap.refer(&mut iterations)
            .add_option(&["-n", "--iterations"], argparse::Store,
                        "Number of Mandelbrot iterations to run");
        ap.refer(&mut width_px)
            .add_option(&["-w", "--width"], argparse::Store,
                        "Width (in pixels) of the image to render (height is computed from aspect ratio)");
        ap.refer(&mut xmin)
            .add_option(&["-l", "--xmin"], argparse::Store, "Minimum x value (left of image)");
        ap.refer(&mut xmax)
            .add_option(&["-r", "--xmax"], argparse::Store, "Maximum x value (right of image)");
        ap.refer(&mut ymin)
            .add_option(&["-b", "--ymin"], argparse::Store, "Minimum y value (bottom of image)");
        ap.refer(&mut ymax)
            .add_option(&["-t", "--ymax"], argparse::Store, "Maximum y value (top of image)");
        ap.refer(&mut out)
            .add_option(&["-o", "--out"], argparse::Store, "Output image file (format is deduced from the extension - but only png appears to work)");
        ap.refer(&mut mode)
            .add_option(&["-m", "--mode"], argparse::Store, "Which rendering mode to use");
        ap.parse_args_or_exit();
    }

    // Main program
    let scale = width_px as f32 / (xmax - xmin);
    let height_px = (scale * (ymax - ymin) + 0.5) as u32;
    println!("# Rendering scene ({:}x{:} for {:} iterations, {:?})...",
             width_px, height_px, iterations, mode);
    let buf = ::image::ImageBuffer::from_fn(width_px, height_px, |x, y| {
        mandelbrot::render((x as f32 + 0.5) / scale + xmin,
                           (y as f32 + 0.5) / scale + ymin,
                           iterations, mode)
    });
    println!("# Saving {:}...", &out);
    if let Err(err) = buf.save(std::path::Path::new(&out)) {
        println!("!!! Failed to write to {:?}, error: {:}", out, err);
    }
}
