from pathlib import Path
from time import perf_counter

from flask import Flask, jsonify, request, send_from_directory

from hid_controller import find_device, read_state, update_state


app = Flask(__name__, static_folder=str(Path(__file__).parent))
VALUE_RANGES = {
    'mode': range(1, 13),
    'speed': range(0, 5),
    'brightness': range(0, 5),
}
last_error = None


@app.errorhandler(OSError)
@app.errorhandler(RuntimeError)
def handle_hid_error(error):
    global last_error
    last_error = str(error)
    return jsonify({'error': f'HID device unavailable: {error}'}), 503


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/state')
def get_state():
    return jsonify(read_state())


@app.route('/api/health')
def health():
    try:
        state = read_state()
    except (OSError, RuntimeError) as error:
        return jsonify({
            'status': 'unavailable',
            'error': str(error),
        }), 503
    return jsonify({'status': 'ok', 'device': state})


@app.route('/api/diagnostics')
def diagnostics():
    started = perf_counter()
    device = find_device()
    read_state()
    return jsonify({
        'connected': True,
        'product': device.get('product_string') or 'Unknown',
        'path': device['path'].decode(errors='replace'),
        'vendor_id': f"{device['vendor_id']:04x}",
        'product_id': f"{device['product_id']:04x}",
        'interface': device.get('interface_number'),
        'response_time_ms': round((perf_counter() - started) * 1000, 2),
        'last_error': last_error,
    })


@app.route('/api/set', methods=['POST'])
def set_state():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Request must contain a valid JSON object'}), 400

    for name, valid_values in VALUE_RANGES.items():
        if name in data:
            value = data[name]
            if isinstance(value, bool) or not isinstance(value, int):
                return jsonify({'error': f'{name} must be an integer'}), 400
            if value not in valid_values:
                first, last = valid_values.start, valid_values.stop - 1
                return jsonify({
                    'error': f'{name} must be between {first} and {last}'
                }), 400

    return jsonify({'ok': True, 'state': update_state(data)})
