use image::Pixel;

/// Create a `Rgba<u8>` pixel from (r,g,b,a) components in the range [0..1]
///
/// # Examples
/// ```
/// rgba(0.0, 1.0, 1.0, 0.5)  // is semi-transparent cyan
/// ```
pub fn rgba(r: f32, g: f32, b: f32, a: f32) -> ::image::Rgba<u8> {
    fn to_u8(i: f32) -> u8 { (255.0 * i) as u8 }
    ::image::Rgba::from_channels(to_u8(r), to_u8(g), to_u8(b), to_u8(a))
}

#[test]
fn rgba_test() {
    let px = |r,g,b,a| { ::image::Rgba::from_channels(r, g, b, a) };
    assert_eq!(rgba(1.0, 0.0, 0.0, 1.0), px(255,0,0,255));
    assert_eq!(rgba(0.0, 0.5, 0.0, 0.0), px(0,127,0,0));
    assert_eq!(rgba(1.0, 0.5, 0.25, 0.125), px(255,127,63,31));
}

/// Create a `Rgba<u8>` pixel from (h,s,v,a) components
/// (see [HSV](https://en.wikipedia.org/wiki/HSL_and_HSV))
///
/// - _hue_ has the range [0..2*PI], where 0 is red
/// - _saturation_ has the range [0..1], where 0 is greyscale, 1 is full color
/// - _value_ has the range [0..1], where 0 is black, 1 is bright color
/// - _alpha_ has the range [0..1], where 0 is transparent, 1 is opaque
pub fn hsva(hue: f32, saturation: f32, value: f32, alpha: f32) -> ::image::Rgba<u8> {
    let (r, g, b) = hsv_to_rgb(hue, saturation, value);
    rgba(r, g, b, alpha)
}

#[test]
fn hsva_test() {
    use ::std::f32::consts::PI;
    // red
    assert_eq!(hsva(0.0, 1.0, 1.0, 1.0), rgba(1.0, 0.0, 0.0, 1.0));
    assert_eq!(hsva(2.0*PI, 1.0, 1.0, 1.0), rgba(1.0, 0.0, 0.0, 1.0));
    // semi-transparent yellow
    assert_eq!(hsva(PI / 3.0, 1.0, 1.0, 0.4), rgba(1.0, 1.0, 0.0, 0.4));
    // black ({hue, saturation} = ignored)
    assert_eq!(hsva(0.82, 0.77, 0.0, 1.0), rgba(0.0, 0.0, 0.0, 1.0));
    // 75% grey (hue = ignored)
    assert_eq!(hsva(0.82, 0.0, 0.75, 1.0), rgba(0.75, 0.75, 0.75, 1.0));
}

/// Helper function for HSV->RGB conversion
/// [conversion algorithm](https://en.wikipedia.org/wiki/HSL_and_HSV).
fn hsv_to_rgb(h: f32, s: f32, v: f32) -> (f32, f32, f32) {
    let c = v * s;
    let hn = h / (::std::f32::consts::PI / 3.0);
    let x = c * (1.0 - (hn % 2.0 - 1.0).abs());
    let (r1, g1, b1) =
        if        hn < 1.0 { (c, x, 0.0)
        } else if hn < 2.0 { (x, c, 0.0)
        } else if hn < 3.0 { (0.0, c, x)
        } else if hn < 4.0 { (0.0, x, c)
        } else if hn < 5.0 { (x, 0.0, c)
        } else {             (c, 0.0, x)
        };
    let m = v - c;
    (r1 + m, g1 + m, b1 + m)
}

// TODO I think we hit https://github.com/rust-lang/rust/issues/25368 here - maybe fixed soon?
// extern crate threadpool;
// /// A multithreaded version of `image::ImageBuffer::from_fn`.
// pub fn image_from_fn<P, F>(w: u32, h: u32, f: F) -> ::image::ImageBuffer<P, Vec<P::Subpixel>>
//     where P: Pixel + 'static, P::Subpixel: 'static, F: Fn(u32, u32) -> P {
//         let (tx, rx) = ::std::sync::mpsc::channel();
//         let pool = ::threadpool::ThreadPool::new(4);
//         for row in 0..h {
//             let txi = tx.clone();
//             pool.execute(move || {
//                 println!("Rendering row {:?}", row);
//                 let pixels = Vec::with_capacity(w as usize);
//                 for col in 0..w {
//                     pixels.extend(f(col, row).channels());
//                 }
//                 tx.send((row, pixels)).unwrap();
//             });
//         }
//         drop(tx);
//         while let Ok((row, pixels)) = rx.recv() {
//             println!("Receiving row {:?}", row);
//         }
//         ::image::ImageBuffer::from_fn(w, h, f)
//     }
