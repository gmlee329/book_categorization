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
from book_categorization import BookCategorization
from book_info import BookInfo

# static variable
token_file_dir = './model/token'
model_file_dir = './model/CNN_model.json'
weights_file_dir = './model/CNN_model.h5'
total_page = 1
count = 3

# flask server
app = Flask(__name__)

# model pre-loading
BC = BookCategorization()
pretrained_model = BC.get_pretrained_model_from_json(model_file_dir, weights_file_dir)
tokenizer = BC.get_tokenizer_from_json(token_file_dir)
okt = BC.get_okt()

BI = BookInfo()
url_dict = BI.get_books_url_dict(total_page)
contents_dict = BI.get_books_title_and_img(url_dict, count)

# request queue setting
requests_queue = Queue()
BATCH_SIZE = 1
CHECK_INTERVAL = 0.1

# request handling
def handle_requests_by_batch():
    try:
        while True:
            requests_batch = []
            while not (len(requests_batch) >= BATCH_SIZE):
                try:
                    requests_batch.append(
                        requests_queue.get(timeout=CHECK_INTERVAL))
                except Empty:
                    continue

            batch_outputs = []

            for request in requests_batch:
                batch_outputs.append(run(request["input"][0]))

            for request, output in zip(requests_batch, batch_outputs):
                request["output"] = output

    except Exception as e:
        while not requests_queue.empty():
            requests_queue.get()
        print('batch()_error', e)


# request processing
threading.Thread(target=handle_requests_by_batch).start()

# run model
def run(text):
    try:
        category = BC.predict(text, model=pretrained_model, tokenizer=tokenizer, okt=okt)
        books = []
        print(category, type(category))
        for content in contents_dict[category[0]]:
            book = {'title' : content[0],
                    'imgURL' : content[1],
                    'link' : content[2]}
            books.append(book)
        print(books)
        result = {
            "category" : category[0],
            "accuracy" : category[1],
            "books" : books
        }

        return result

    except Exception as e:
        print('run()_error', e)
        return 500

# routing
@app.route("/prediction", methods=['POST'])
def prediction():
    try:
        # only get one request at a time
        if requests_queue.qsize() > BATCH_SIZE:
            return jsonify({'message': 'TooManyReqeusts'}), 429

        # check image format
        try:
            text = request.form['content']
        except Exception:
            return jsonify({'message': 'Content is not string type'}), 400

        # put data to request_queue
        req = {'input': [text]}
        requests_queue.put(req)

        # wait output
        while 'output' not in req:
            time.sleep(CHECK_INTERVAL)

        # send output
        result = req['output']

        if result == 500:
            return jsonify({'message': 'Error! An unknown error occurred on the server'}), 500
        
        result = jsonify(result)
        return result

    except Exception as e:
        print(e)
        return jsonify({'message': 'Error! Unable to process request'}), 400


@app.route('/health')
def health():
    return "ok", 200


@app.route('/')
def main():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
