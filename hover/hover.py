import io

import flask as F
import Box2D as B
import numpy as np


class Render:
    @classmethod
    def fixture(cls, fixture, fill, out):
        out.write('<path fill="{fill}" d="'.format(fill=fill))
        dx, dy = fixture.shape.vertices[0]
        out.write('M {} {}'.format(dx, dy))
        for (dx, dy) in fixture.shape.vertices[1:]:
            out.write(' L {} {}'.format(dx, dy))
        out.write('"/>')

    @classmethod
    def body(cls, body, fill, out):
        out.write('<g transform="translate({x},{y}) rotate({angle})">'.format(
            angle=body.angle * 180/np.pi, x=body.position.x, y=body.position.y,
        ))
        for fixture in body.fixtures:
            cls.fixture(fixture, fill, out)
        out.write('</g>')

    @classmethod
    def scene(cls, bodies_and_fills, viewbox, width, out):
        (xmin, xmax), (ymin, ymax) = viewbox
        height = (ymax-ymin)/(xmax-xmin) * width
        out.write('<svg viewBox="{viewbox}" width="{width}" height="{height}">'.format(
            viewbox='{} {} {} {}'.format(xmin, ymin, xmax-xmin, ymax-ymin),
            width=width, height=height))
        out.write('<g transform="scale(1,-1) translate(0, {dy})">'.format(dy=-(ymax+ymin)))
        for body, fill in bodies_and_fills:
            cls.body(body, fill, out)
        out.write('</g></svg>')

    @classmethod
    def render(cls, bodies_and_fills, viewbox, width):
        out = io.StringIO()
        cls.scene(bodies_and_fills, viewbox, width, out)
        return out.getvalue()


class Game:
    def __init__(self):
        self.timestep = 1/30
        self.thrust = 15
        self.hwidth = 0.4
        self.hheight = 2

        self.world = B.b2World(gravity=(0, -10))
        self.ground = self.world.CreateStaticBody(
            position=[0, -10],
            shapes=B.b2PolygonShape(box=(50, 10)),
        )
        self.rocket = self.world.CreateDynamicBody(position=[0, 10])
        self.rocket.CreatePolygonFixture(box=(self.hwidth, self.hheight),
                                         density=1,
                                         friction=1)

    def draw(self):
        return Render.render([(self.ground, 'black'), (self.rocket, 'blue')],
                             ((-30, 30), (-1, 29)),
                             800)

    def _repr_html_(self):
        return self.draw()

    def step(self, thrust_left, thrust_right):
        thrust_v = self.rocket.GetWorldVector([0, self.rocket.mass * self.thrust])
        if thrust_left:
            self.rocket.ApplyForce(thrust_v, self.rocket.GetWorldPoint([-self.hwidth, -self.hheight]), True)
        if thrust_right:
            self.rocket.ApplyForce(thrust_v, self.rocket.GetWorldPoint([self.hwidth, -self.hheight]), True)
        self.world.Step(self.timestep, 5, 5)


################################################################################
# Webapp for playing around

app = F.Flask(__name__)

app_game = Game()


@app.route('/')
def route_index():
    return F.redirect(F.url_for('static', filename='index.html'))


@app.route('/game/start', methods=['POST'])
def route_game_start():
    global app_game
    app_game = Game()
    return F.jsonify(dict(gameid=str(id(app_game)),
                          timestep=app_game.timestep))


@app.route('/game/state', methods=['GET', 'POST'])
def route_game_state():
    if F.request.method == 'POST':
        form = F.request.form
        app_game.step(form['thrust_left'].lower() == 'true',
                      form['thrust_right'].lower() == 'true')
    return F.jsonify(dict(gameid=str(id(app_game)), html=app_game.draw()))
