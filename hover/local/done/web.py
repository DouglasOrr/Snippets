"""Webapp for trying out the game as a human."""

import flask as F

from . import core


app = F.Flask(__name__)

_game = core.Game()


@app.route('/')
def route_index():
    return F.redirect(F.url_for('static', filename='index.html'))


@app.route('/game/start', methods=['POST'])
def route_game_start():
    global _game
    _game = core.Game()
    return F.jsonify(dict(gameid=str(id(_game)),
                          timestep=_game.timestep))


@app.route('/game/state', methods=['GET', 'POST'])
def route_game_state():
    if F.request.method == 'POST':
        form = F.request.form
        left = form['thrust_left'].lower() == 'true'
        right = form['thrust_right'].lower() == 'true'
        nticks = max(1, int(form['ticks']))
        for n in range(nticks):
            _game.step((left, right))
    return F.jsonify(dict(gameid=str(id(_game)),
                          state=_game.state._asdict(),
                          html=_game.draw()))
