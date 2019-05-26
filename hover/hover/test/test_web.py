from .. import web


def test_webapp_home():
    client = web.app.test_client()
    home = client.get('/', follow_redirects=True)
    assert home.status == '200 OK'
    assert 'Hover' in home.data.decode('utf8')


def test_webapp_game():
    client = web.app.test_client()
    start = client.post('/game/start')
    assert start.status == '200 OK'
    assert 0 < start.get_json()['timestep'] <= 1

    restart = client.post('/game/start')
    assert restart.status == '200 OK'
    assert start.get_json()['gameid'] != restart.get_json()['gameid']

    state = client.get('/game/state')
    assert state.status == '200 OK'
    assert state.get_json()['gameid'] == restart.get_json()['gameid']

    restate = client.get('/game/state')
    assert restate.status == '200 OK'
    assert state.get_json()['state'] == restate.get_json()['state']

    step = client.post('/game/state', data=dict(
        thrust_left='False',
        thrust_right='True',
        ticks='10',
    ))
    assert step.status == '200 OK'
    assert step.get_json()['state'] != state.get_json()['state']
