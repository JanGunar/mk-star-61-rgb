import hid_controller


def test_mock_backend_reads_and_updates_state(monkeypatch):
    monkeypatch.setenv('STAR61_MOCK_HID', '1')
    monkeypatch.setattr(
        hid_controller,
        'MOCK_STATE',
        {'mode': 1, 'speed': 1, 'brightness': 4},
    )

    assert hid_controller.find_device()['product_string'] == 'MK Star 61 (mock)'
    assert hid_controller.read_state() == {
        'mode': 1,
        'speed': 1,
        'brightness': 4,
    }

    state = hid_controller.update_state({'mode': 6, 'brightness': 2})

    assert state == {'mode': 6, 'speed': 1, 'brightness': 2}
