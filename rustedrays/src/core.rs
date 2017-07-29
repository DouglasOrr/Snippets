use mat;
use mat::{Vec3, Angle};
use std::sync::Arc;

// Core

#[derive(Clone, Debug)]
pub struct Color {
    pub red: f32,
    pub green: f32,
    pub blue: f32
}
impl Color {
    pub fn red() -> Color { Color::rgb(1.0, 0.0, 0.0) }
    pub fn green() -> Color { Color::rgb(0.0, 1.0, 0.0) }
    pub fn blue() -> Color { Color::rgb(0.0, 0.0, 1.0) }
    pub fn black() -> Color { Color::rgb(0.0, 0.0, 0.0) }
    pub fn white() -> Color { Color::rgb(1.0, 1.0, 1.0) }
    pub fn gray(i: f32) -> Color { Color::rgb(i, i, i) }
    pub fn rgb(r: f32, g: f32, b: f32) -> Color {
        Color { red: r, green: g, blue: b }
    }
    pub fn add(&self, x: &Color) -> Color {
        Color {
            red: self.red + x.red,
            green: self.green + x.green,
            blue: self.blue + x.blue
        }
    }
    pub fn scale(&self, t: f32) -> Color {
        Color {
            red: self.red * t,
            green: self.green * t,
            blue: self.blue * t
        }
    }
    pub fn tint(&self, t: &Color) -> Color {
        Color {
            red: self.red * t.red,
            green: self.green * t.green,
            blue: self.blue * t.blue
        }
    }
}

#[derive(Clone, Debug)]
pub struct Ray {
    start: Vec3,
    dir: Vec3,
    ttl: u32
}
impl Ray {
    fn new(start: Vec3, dir: Vec3, ttl: u32) -> Ray {
        assert!((1.0 - dir.norm()).abs() < 1E-4);
        assert!(ttl != 0);
        Ray {
            start: start,
            dir: dir,
            ttl: ttl
        }
    }
}

// Object

#[derive(Debug)]
struct Collision {
    distance: f32,
    color: Color,
    position: Vec3,
    norm: Vec3
}

pub trait Object: Send + Sync {
    fn distance(&self, ray: &Ray) -> Option<Collision>;
}

pub struct Sphere {
    pub center: Vec3,
    pub radius: f32,
    pub color: Color
}
impl Sphere {
    fn make_collision(&self, ray: &Ray, distance: f32) -> Collision {
        let position = ray.start + ray.dir.scale(distance);
        Collision {
            distance: distance,
            color: self.color.clone(),
            position: position,
            norm: (position - self.center).unit()
        }
    }
}
impl Object for Sphere {
    fn distance(&self, ray: &Ray) -> Option<Collision> {
        let offset = self.center - ray.start;
        let b = -2.0 * ray.dir.dot(&offset);
        let c = offset.dot(&offset) - self.radius * self.radius;
        match mat::solve_quadratic(1.0, b, c) {
            Some((x, y)) if (0.0 < x && x < y) => Some(self.make_collision(ray, x)),
            Some((x, y)) if (0.0 < y) => Some(self.make_collision(ray, y)),
            _ => None
        }
    }
}

pub struct Plane {
    pub point: Vec3,
    pub norm: Vec3,
    pub color: Color
}
impl Object for Plane {
    fn distance(&self, ray: &Ray) -> Option<Collision> {
        let height = (self.point - ray.start).dot(&self.norm);
        let distance = height / ray.dir.dot(&self.norm);
        if 0.0 < distance {
            Some(Collision {
                distance: distance,
                norm: self.norm.scale(-height.signum()),
                position: ray.start + ray.dir.scale(distance),
                color: self.color.clone()
            })
        } else { None }
    }
}

// Camera

/// A camera looks at a scene by casting rays through a fixed size
/// grid of pixels.
pub trait Camera {
    fn spawn(&self, x: u32, y: u32) -> Ray;
    fn bounds(&self) -> (u32, u32);
}

/// A camera with a flat array of pixels which the scene is projected onto
pub struct FlatCamera {
    origin: Vec3,
    top_left: Vec3,
    x_inc: Vec3,
    y_inc: Vec3,
    bounds: (u32, u32),
    ttl: u32
}
impl FlatCamera {
    pub fn new(origin: &Vec3, direction: &Vec3, up: &Vec3, fov_width: Angle,
               bounds: (u32, u32), ttl: u32) -> FlatCamera {
        // basis vectors
        let forward = direction.unit();
        let screen_up = (*up - forward.scale(up.dot(&forward))).unit();
        let screen_right = forward.cross(&screen_up);
        let centre = *origin + forward;
        // dimensions
        let screen_w = 2.0 * (fov_width.rad() / 2.0).tan();
        let screen_pixel_size = screen_w / (bounds.0 as f32);
        // results
        let x_inc = screen_right.scale(screen_pixel_size);
        let y_inc = screen_up.scale(screen_pixel_size);
        let top_left = centre
            - x_inc.scale((bounds.0 as f32) / 2.0 - 0.5)
            - y_inc.scale((bounds.1 as f32) / 2.0 - 0.5);
        FlatCamera {
            origin: origin.clone(),
            top_left: top_left,
            x_inc: x_inc,
            y_inc: y_inc,
            bounds: bounds,
            ttl: ttl
        }
    }
}
impl Camera for FlatCamera {
    fn spawn(&self, x: u32, y: u32) -> Ray {
        assert!(x < self.bounds.0 && y < self.bounds.1,
                "Pixel being spawned is not within the camera's bounds");
        let screen = self.top_left + self.x_inc.scale(x as f32) + self.y_inc.scale((self.bounds.1 - y - 1) as f32);
        Ray {ttl: self.ttl,
             start: self.origin.clone(),
             dir: (screen - self.origin).unit()}
    }
    fn bounds(&self) -> (u32, u32) { self.bounds }
}

// Light

pub struct Light {
    pub position: Vec3,
    pub color: Color
}

// Environment

pub trait Environment {
    fn trace(&self, ray: Ray) -> Color;
}

/// A solid color background (very simple, for testing)
pub struct Background {
    pub background: Color
}
impl Environment for Background {
    fn trace(&self, ray: Ray) -> Color { self.background.clone() }
}

/// A list of objects that are all tested for collisions with every ray
pub struct ObjectList {
    pub scene: Vec<Arc<Object>>,
    pub lights: Vec<Light>,
    pub background: Color,
    pub ambient: Color,
    pub collision_guard: f32
}
impl ObjectList {
    fn closest(&self, ray: &Ray) -> Option<Collision> {
        let mut collide_dist = ::std::f32::INFINITY;
        let mut collide: Option<Collision> = None;
        for obj in self.scene.iter() {
            if let Some(collision) = obj.distance(&ray) {
                if collision.distance < collide_dist {
                    collide_dist = collision.distance;
                    collide = Some(collision);
                }
            }
        }
        collide
    }
    fn color(&self, collision: &Collision) -> Color {
        let start = collision.position + collision.norm.scale(self.collision_guard);
        // ambient
        let mut result = collision.color.tint(&self.ambient);
        // diffuse
        for light in self.lights.iter() {
            let to_light = light.position - start;
            let light_distance = to_light.norm();
            let light_direction = to_light.unit();
            let diffuse_score = collision.norm.dot(&light_direction);
            // No point casting light rays back through the object
            if 0.0 < diffuse_score {
                let ray = Ray::new(start, light_direction, 1);
                match self.closest(&ray) {
                    Some(Collision{distance, ..}) if distance < light_distance => {},
                    _ => { // diffuse component exists
                        result = collision.color.tint(&light.color).scale(diffuse_score).add(&result);
                    }
                }
            }
        }
        result
    }
}
impl Environment for ObjectList {
    fn trace(&self, ray: Ray) -> Color {
        match self.closest(&ray) {
            Some(collision) => self.color(&collision),
            None => self.background.clone()
        }
    }
}
