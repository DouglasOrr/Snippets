from .. import web


def test_webapp_home():
    client = web.app.test_client()
    home = client.get('/', follow_redirects=True)
    assert home.status == '200 OK'
    assert 'Hover' in home.data.decode('utf8')


def test_static_lib():
    client = web.app.test_client()
    for file in ['jquery.js', 'bootstrap.css']:
        lib = client.get('/static/lib/{}'.format(file))
        assert lib.status == '200 OK'
        assert lib.get_data()


def test_webapp_game():
    client = web.app.test_client()
    start = client.post('/game/start')
    assert start.status == '200 OK'
    assert type(start.get_json()['gameid']) is str

    restart = client.post('/game/start')
    assert restart.status == '200 OK'
    assert start.get_json()['gameid'] != restart.get_json()['gameid']

    state = client.get('/game/state')
    assert state.status == '200 OK'
    assert state.get_json()['gameid'] == restart.get_json()['gameid']

    restate = client.get('/game/state')
    assert restate.status == '200 OK'
    assert state.get_json()['ship_state'] == restate.get_json()['ship_state']
    assert state.get_json()['html'] == restate.get_json()['html']

    step = client.post('/game/state', data=dict(
        thrust_left='False',
        thrust_right='True',
    ))
    assert step.status == '200 OK'
    assert step.get_json()['ship_state'] != state.get_json()['ship_state']
    assert step.get_json()['html'] != state.get_json()['html']
