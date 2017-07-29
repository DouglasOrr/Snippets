mod core;
mod mat;

extern crate image;
extern crate threadpool;

use image::Pixel;
use mat::{Vec3, Angle};
use core::{Camera, Environment};
use std::sync::{Arc, Mutex};

fn to_argb(c: core::Color) -> image::Rgba<u8> {
    // a simple tone mapping function
    let to_chan = |c: f32| -> u8 { (255.0 * (1.0 - (-c).exp())) as u8 };
    image::Rgba::from_channels(to_chan(c.red), to_chan(c.green), to_chan(c.blue), 255)
}

fn render_example_scene() {
    println!("# Building scene...");
    let (width, height) = (4000, 4000);
    let ttl = 10;

    let camera = Arc::new(core::FlatCamera::new(
        &Vec3{x:0.0, y:0.0, z:10.0},
        &Vec3{x:0.0, y:1.0, z:0.0},
        &Vec3{x:0.0, y:0.0, z:1.0},
        Angle::from_degrees(45.0),
        (width, height),
        ttl));

    // Objects
    let s0 = core::Sphere {
        center: Vec3{x:0.0, y:50.0, z:10.0},
        radius: 10.0,
        color: core::Color::rgb(1.0, 0.0, 0.0)
    };
    let p0 = core::Plane {
        point: Vec3{x:0.0, y: 0.0, z:0.0},
        norm: Vec3{x:0.0, y: 0.0, z:1.0},
        color: core::Color::gray(0.8)
    };
    let scene = vec![Arc::new(s0) as Arc<core::Object>,
                     Arc::new(p0) as Arc<core::Object>];
    // Lights
    let l0 = core::Light {
        position: Vec3{x:-100.0, y:20.0, z:100.0},
        color: core::Color::gray(0.9)
    };
    let l1 = core::Light {
        position: Vec3{x:100.0, y:20.0, z:100.0},
        color: core::Color::gray(0.7)
    };
    let lights = vec![l0, l1];
    // Env
    let env = Arc::new(core::ObjectList{
        scene: scene,
        background: core::Color::black(),
        ambient: core::Color::gray(0.1),
        lights: lights,
        collision_guard: 1E-5
    });

    // multithreaded renderer (currently pretty ugly!)
    println!("# Rendering scene...");
    let nchan = image::Rgba::<u8>::channel_count() as u32;
    let nvals = (height * width * nchan) as usize;
    let pixels = Arc::new(Mutex::new(vec![0u8; nvals]));
    let pool = threadpool::ThreadPool::new(4);
    let (tx, rx) = std::sync::mpsc::channel();
    for y in 0..height {
        let tx = tx.clone();
        let pixels = pixels.clone();
        let env = env.clone();
        let camera = camera.clone();
        pool.execute(move || {
            // 1. render all pixels in a row
            let mut row = vec![0u8; (nchan * width) as usize];
            for x in 0..width {
                let pixel = to_argb(env.trace(camera.spawn(x, y)));
                let (r, g, b, a) = pixel.channels4();
                row[(x*nchan) as usize] = r;
                row[(x*nchan+1) as usize] = g;
                row[(x*nchan+2) as usize] = b;
                row[(x*nchan+3) as usize] = a;
            }
            // 2. copy them into the result
            let mut pixels = pixels.lock().unwrap();
            for i in 0..(width*nchan) {
                pixels[(y*width*nchan+i) as usize] = row[i as usize];
            }
            // 3. notify the master that we've done our job
            tx.send(y).unwrap();
        });
    }
    // wait for all rows to be written
    for y in 0..height {
        rx.recv().unwrap();
    }
    let pixels = pixels.lock().unwrap();
    let buf = image::ImageBuffer::<image::Rgba<u8>>::from_vec(width, height, pixels.clone())
        .expect("Invalid pixels buffer");

    // singlethreaded renderer
    // println!("# Rendering scene...");
    // let buf = image::ImageBuffer::from_fn(width, height, |x, y| {
    //     to_argb(env.trace(camera.spawn(x, y)))
    // });

    let out = std::path::Path::new("scene.png");
    println!("# Writing {}...", out.to_str().expect("Bad path"));
    if let Err(err) = buf.save(out) {
        println!("!!! Failed to write to {:?}, error: {:}", out, err);
    }
}

fn main() {
    render_example_scene();
}
