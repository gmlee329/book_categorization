import os
import time
import tqdm
import numpy as np

# import for server
from flask import Flask, render_template, request, Response, jsonify
from queue import Queue, Empty
from waitress import serve
import threading
import time

# flask server
app = Flask(__name__)

@app.route('/health')
def health():
    return "ok", 200


@app.route('/')
def main():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
