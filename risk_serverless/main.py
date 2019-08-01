import numpy as np


def simulate_attacker_win_probability(attack, defend, simulations):
    """Compute the probability of winning a Risk battle by simulating dice rolls."""
    # Create outcome thresholds, which are indexed by number of dice thrown
    t_defend_lose_2 = np.array([[0, 0, 0],
                                [0, 0, 0],
                                [0, 0, 1770],
                                [0, 0, 2890]])
    t_defend_lose_1 = np.array([[0, 0, 0],
                                [0, 3240, 1980],
                                [0, 4500, 2520],
                                [0, 5130, 2611]])
    t_defend_lose_at_least_one = t_defend_lose_2 + t_defend_lose_1

    armies_attack = np.full(simulations, attack)
    armies_defend = np.full(simulations, defend)
    while True:
        roll_attack = np.clip(armies_attack - 1, 0, 3)
        roll_defend = np.clip(armies_defend, 0, 2)
        roll_min = np.minimum(roll_attack, roll_defend)
        if (roll_min == 0).all():
            return (armies_defend == 0).mean()

        p = np.random.randint(0, 7776, armies_attack.shape)
        defender_losses = ((p < t_defend_lose_at_least_one[roll_attack, roll_defend]).astype(np.int32) +
                           (p < t_defend_lose_2[roll_attack, roll_defend]))
        armies_defend -= defender_losses
        armies_attack -= roll_min - defender_losses


def odds(request):
    attack = np.clip(int(request.args['attack']), 1, 100)
    defend = np.clip(int(request.args['defend']), 1, 100)
    simulations = np.clip(int(request.args.get('simulations', 1000)), 1, 10000)
    attacker_win_probability = simulate_attacker_win_probability(attack=attack, defend=defend, simulations=simulations)
    return dict(attack=int(attack), defend=int(defend), simulations=int(simulations),
                attacker_win_probability=float(attacker_win_probability))


if __name__ == '__main__':
    import flask
    app = flask.Flask(__name__)

    @app.route('/')
    def route_index():
        return flask.redirect('static/index.html')

    @app.route('/odds')
    def route_odds():
        return odds(flask.request)

    app.run('0.0.0.0', 7777, debug=True)
