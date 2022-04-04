from flask import Flask, jsonify, request, abort
import requests
from pathlib import Path
import json

app = Flask(__name__)


def safe_filename(unsafe):
    keepcharacters = (' ','.','_')
    return "".join(c for c in unsafe if c.isalnum() or c in keepcharacters)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if path.startswith("favicon"):
        abort(404)

    filename = safe_filename(path)
    filepath = Path(f"./mbcache/{filename}")

    if filepath.exists():
        print(f"Cache hit for {path}")
        with filepath.open() as f:
            asjson = json.load(f)
        return jsonify(asjson)

    print(f"Requesting from https://api.mapbox.com/{path}?{request.query_string.decode()}")
    resp = requests.get(f"https://api.mapbox.com/{path}?{request.query_string.decode()}")

    if resp.status_code == 200:
        # cache to disk
        filepath.open("w").write(resp.text)
        return jsonify(resp.json())

    print(f"Got {resp.status_code} for request {path}")
    print(resp.text)
    return jsonify({"error": f"Got {resp.status_code} for request {path}"})


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8001)