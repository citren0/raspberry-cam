from flask import Flask, Response, render_template
from picamera2 import Picamera2
import base64
import time
import threading
from threading import Lock
import base64
import numpy as np
import cv2

app = Flask(__name__)

frame = ""
frame_lock = Lock()

audio = b""
audio_lock = Lock()


# Threads
def generate_frames():
    global frame_lock
    global frame
    picam = Picamera2()
    picam.configure(picam.create_still_configuration())
    picam.start()
    while True:
        img = picam.capture_array()
        _, buffer = cv2.imencode('.jpg', img)
        buff = base64.b64encode(buffer).decode('utf-8')
        with frame_lock:
            frame = f"data:image/jpeg;base64,{buff}\n\n"
        time.sleep(0.10)


# Flask routes.
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/frame')
def get_frame(msg=None):
    global frame_lock
    global frame
    with frame_lock:
        return frame


def main():
    frame_producer = threading.Thread(target=generate_frames, args=())
    frame_producer.start()

    app.run(app, debug=True, port=5000, host="0.0.0.0", use_reloader=False)


if __name__ == "__main__":
    main()