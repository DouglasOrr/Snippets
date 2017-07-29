use std::ops::{Add, Sub};

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Vec3 {
    pub x: f32,
    pub y: f32,
    pub z: f32
}

impl Add for Vec3 {
    type Output = Vec3;
    fn add(self, rhs: Vec3) -> Vec3 {
        Vec3 {
            x: self.x + rhs.x,
            y: self.y + rhs.y,
            z: self.z + rhs.z
        }
    }
}
impl Sub for Vec3 {
    type Output = Vec3;
    fn sub(self, rhs: Vec3) -> Vec3 {
        Vec3 {
            x: self.x - rhs.x,
            y: self.y - rhs.y,
            z: self.z - rhs.z
        }
    }
}
impl Vec3 {
    pub fn zero() -> Vec3 { Vec3 { x: 0.0, y: 0.0, z: 0.0 } }
    pub fn x() -> Vec3 { Vec3 { x: 1.0, .. Vec3::zero() } }
    pub fn y() -> Vec3 { Vec3 { y: 1.0, .. Vec3::zero() } }
    pub fn z() -> Vec3 { Vec3 { z: 1.0, .. Vec3::zero() } }

    pub fn scale(&self, factor: f32) -> Vec3 {
        Vec3 {
            x: self.x * factor,
            y: self.y * factor,
            z: self.z * factor
        }
    }
    pub fn norm(&self) -> f32 {
        self.dot(&self).sqrt()
    }
    pub fn unit(&self) -> Vec3 {
        self.scale(1.0 / self.norm())
    }
    pub fn dot(&self, rhs: &Vec3) -> f32 {
        self.x * rhs.x + self.y * rhs.y + self.z * rhs.z
    }
    pub fn cross(&self, rhs: &Vec3) -> Vec3 {
        Vec3 {
            x: self.y * rhs.z - self.z * rhs.y,
            y: self.z * rhs.x - self.x * rhs.z,
            z: self.x * rhs.y - self.y * rhs.x
        }
    }
}

#[test]
fn check_vec() {
    let x = Vec3::x();
    let y = Vec3::y();
    let z = Vec3::z();
    assert_eq!(x.dot(&y), 0.0);
    assert_eq!(y.dot(&z), 0.0);
    assert_eq!(x.cross(&y), z);
    assert_eq!(y.cross(&z), x);
    assert_eq!(z.cross(&x), y);
}

pub fn solve_quadratic(a: f32, b: f32, c: f32) -> Option<(f32,f32)> {
    let det = b*b - 4.0*a*c;
    if 0.0 <= det {
        let detrt = det.sqrt();
        Some(((-b + detrt) / (2.0 * a),
              (-b - detrt) / (2.0 * a)))
    } else { None }
}

#[test]
fn check_quadratic() {
    assert_eq!(solve_quadratic(1.0, -2.0, -3.0), Some((3.0, -1.0)));
    assert_eq!(solve_quadratic(4.0, -24.0, 36.0), Some((3.0, 3.0)));
}

/// Angle stored in radians
#[derive(Debug, PartialEq)]
pub struct Angle(f32);

const RAD_TO_DEG: f32 = 180.0 / ::std::f32::consts::PI;
impl Angle {
    pub fn from_degrees(x: f32) -> Angle { Angle(x / RAD_TO_DEG) }
    pub fn from_radians(x: f32) -> Angle { Angle(x) }
    pub fn rad(&self) -> f32 { self.0 }
    pub fn deg(&self) -> f32 { self.rad() * RAD_TO_DEG }
}

#[test]
fn check_angle() {
    assert_eq!(Angle::from_degrees(360.0).rad(), 2.0 * ::std::f32::consts::PI);
    assert_eq!(Angle::from_radians(::std::f32::consts::PI).deg(), 180.0);
    assert_eq!(Angle::from_radians(::std::f32::consts::PI / 2.0), Angle::from_degrees(90.0));
}
