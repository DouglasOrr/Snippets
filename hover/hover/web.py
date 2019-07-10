"""Webapp for trying out the game as a human."""

import flask as F
import hover_game as G
import numpy as np


def _create_runner():
    global _runner
    _runner = G.Runner(seed=None, difficulty=[1])


_runner = None
_create_runner()
app = F.Flask(__name__)


@app.route('/')
def route_index():
    return F.redirect(F.url_for('static', filename='index.html'))


@app.route('/game/start', methods=['POST'])
def route_game_start():
    _create_runner()
    return F.jsonify(dict(gameid=str(id(_runner))))


@app.route('/static/lib/<path:path>', methods=['GET'])
def route_static_lib(path):
    return F.send_from_directory('/opt/web', path)


@app.route('/game/state', methods=['GET', 'POST'])
def route_game_state():
    if F.request.method == 'POST':
        form = F.request.form
        left = form['thrust_left'].lower() == 'true'
        right = form['thrust_right'].lower() == 'true'
        _runner.step(np.array([left, right], dtype=np.bool))
    return F.jsonify(dict(gameid=str(id(_runner)),
                          outcome=str(_runner.state().outcome),
                          html=_runner.to_svg()))
