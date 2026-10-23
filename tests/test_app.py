import pytest

import app


@pytest.fixture()
def client():
    app.app.config.update(TESTING=True)
    with app.app.test_client() as test_client:
        yield test_client


def test_set_rejects_out_of_range_mode(client):
    response = client.post('/api/set', json={'mode': 13})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'mode must be between 1 and 12'}


def test_set_returns_updated_state(client, monkeypatch):
    monkeypatch.setattr(app, 'update_state', lambda data: {
        'mode': data.get('mode', 1),
        'speed': data.get('speed', 2),
        'brightness': data.get('brightness', 3),
    })

    response = client.post('/api/set', json={'mode': 4})

    assert response.status_code == 200
    assert response.get_json() == {
        'ok': True,
        'state': {'mode': 4, 'speed': 2, 'brightness': 3},
    }


def test_health_reports_device_state(client, monkeypatch):
    monkeypatch.setattr(app, 'read_state', lambda: {
        'mode': 1,
        'speed': 2,
        'brightness': 3,
    })

    response = client.get('/api/health')

    assert response.status_code == 200
    assert response.get_json() == {
        'status': 'ok',
        'device': {'mode': 1, 'speed': 2, 'brightness': 3},
    }


def test_health_reports_unavailable_device(client, monkeypatch):
    monkeypatch.setattr(
        app,
        'read_state',
        lambda: (_ for _ in ()).throw(RuntimeError('not connected')),
    )

    response = client.get('/api/health')

    assert response.status_code == 503
    assert response.get_json() == {
        'status': 'unavailable',
        'error': 'not connected',
    }
