from dataclasses import dataclass
import io
import typing as T

import numpy as np


@dataclass(frozen=True)
class PolygonShape:
    vertices: T.Tuple[T.Tuple[float]]
    color: T.Text


@dataclass(frozen=True)
class Body:
    x: float
    y: float
    angle: float
    shapes: T.Tuple[PolygonShape]


@dataclass(frozen=True)
class Scene:
    bodies: T.Tuple[Body]
    bounds: T.Tuple[float]  # left, right, top, bottom
    width: int


def draw_shape(shape, out):
    out.write('<path fill="{fill}" d="'.format(fill=shape.color))
    dx, dy = shape.vertices[0]
    out.write('M {} {}'.format(dx, dy))
    for (dx, dy) in shape.vertices[1:]:
        out.write(' L {} {}'.format(dx, dy))
    out.write('"/>')


def draw_body(body, out):
    out.write('<g transform="translate({x},{y}) rotate({angle})">'.format(
        x=body.x, y=body.y, angle=body.angle * 180/np.pi,
    ))
    for shape in body.shapes:
        draw_shape(shape, out)
    out.write('</g>')


def draw_scene(scene, out):
    xmin, xmax, ymin, ymax = scene.bounds
    height = (ymax-ymin)/(xmax-xmin) * scene.width
    out.write('<svg viewBox="{viewbox}" width="{width}" height="{height}">'.format(
        viewbox='{} {} {} {}'.format(xmin, ymin, xmax-xmin, ymax-ymin),
        width=scene.width, height=height))
    out.write('<g transform="scale(1,-1) translate(0, {dy})">'.format(dy=-(ymax+ymin)))
    for body in scene.bodies:
        draw_body(body, out)
    out.write('</g></svg>')


def draw(scene):
    out = io.StringIO()
    draw_scene(scene, out)
    return out.getvalue()
