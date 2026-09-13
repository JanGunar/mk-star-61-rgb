from flask import Flask, request, jsonify, send_from_directory
import hid

app = Flask(__name__, static_folder='.')
DEVICE_PATH = b'/dev/hidraw1'

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/state')
def get_state():
    with hid.Device(path=DEVICE_PATH) as d:
        current = d.get_feature_report(10, 42)
    return jsonify({
        'mode': current[1],
        'speed': current[3],
        'brightness': current[4],
    })

@app.route('/api/set', methods=['POST'])
def set_state():
    data = request.json
    with hid.Device(path=DEVICE_PATH) as d:
        current = bytearray(d.get_feature_report(10, 42))
        if 'mode' in data:
            current[1] = data['mode']
        if 'speed' in data:
            current[3] = data['speed']
        if 'brightness' in data:
            current[4] = data['brightness']
        d.send_feature_report(bytes(current))
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(port=8000)