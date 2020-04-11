import xml.etree.ElementTree as ET

from .. import render


def test_render():
    scene = render.Scene(
        bodies=(
            render.Body(
                10, 20, -.5,
                (render.PolygonShape(((-1, -1), (1, -1), (0, 1)), 'red'),
                 render.PolygonShape(((-1, -2), (1, -2), (1, -1), (-1, -1)), 'blue'))
            ),
            render.Body(
                60, 40, .3,
                (render.PolygonShape(((-1, -1), (1, -1), (0, 1)), 'yellow'),)
            )
        ),
        bounds=[0, 100, 0, 50],
        width=400,
    )

    # Only test some basic facts (e.g. "is valid XML")
    # - most meaningful tests here are more visual
    svg = ET.fromstring(render.draw(scene))
    assert len(svg.findall('*/g')) == 2
    assert set(node.attrib['fill'] for node in svg.findall('*/*/path')) \
        == {'red', 'blue', 'yellow'}
