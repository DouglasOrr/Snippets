import math, controllers
from flask import Flask, jsonify, request, redirect, url_for
from pendulum import *

class Sim:
    THRESHOLD = math.pi / 3

    def __init__(self):
        self.set_controller('none')
        self.restart()

    def set_controller(self, name):
        self.controller_name = name
        self.controller = ManualControl(10, controllers.ALL[name])

    def restart(self):
        self.simulation = Simulation(SineNoise(
            lambda t: 0.5 + t / 20,
            [(0.73, 1), (2, 1), (2.9, 0.5), (13, 0.5)])
        )
        self.stopped = False
        self.manual = False
        self.last_controller_name = 'none'

    def step(self, dt, manual_control):
        if not self.stopped:
            self.last_controller_name = self.controller_name
            self.controller.control = manual_control
            self.manual = self.manual or manual_control
            n = int(math.ceil(dt / self.simulation.dt))
            for i in range(0, n):
                self.simulation.step(self.controller)
                if Sim.THRESHOLD < abs(self.simulation.theta):
                    self.stopped = True
                    break

    def state(self):
        return {'theta': self.simulation.theta,
                't': self.simulation.t,
                'stopped': self.stopped,
                'threshold': Sim.THRESHOLD,
                'manual': self.manual,
                'auto': self.last_controller_name}

app = Flask(__name__)
simulation = Sim()

@app.route('/')
def index():
    return redirect(url_for('static', filename='pendulum.html'))

@app.route("/step", methods=['POST'])
def step():
    simulation.step(float(request.form['dt']), int(request.form.get('control', '0')))
    return jsonify(simulation.state())

@app.route("/restart", methods=['POST'])
def restart():
    simulation.restart()
    return ""

@app.route("/controllers", methods=['GET'])
def list_controllers():
    return jsonify({'controllers': sorted(controllers.ALL.keys())})

@app.route("/controller", methods=['POST'])
def set_controller():
    simulation.set_controller(request.form['name'])
    return ""

if __name__ == "__main__":
    app.run(debug=True)
