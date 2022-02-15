from flask import Flask, request, jsonify

import pandas as pd
import pickle
import logging
from datetime import datetime

import os

logging.getLogger("__main__")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(name)s %(levelname)s %(message)s",
    datefmt="%m-%d %H:%M",
)

app = Flask(__name__)


@app.route('/top-plants', methods=['POST'])
def predictor():
    json = request.json

    return jsonify(status='ok', predict=None)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')