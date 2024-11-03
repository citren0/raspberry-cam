from flask import Flask, Response, render_template
import cv2
from flask_socketio import SocketIO, emit
import base64
import time
import threading
from threading import Lock
import sys

app = Flask(__name__)
socketio = SocketIO(app)
frame = ""
lock = Lock()


def generate_frames():
    global lock
    global frame
    camera = cv2.VideoCapture(0)
    while True:
        ret, img = camera.read()
        if ret:
            _, buffer = cv2.imencode('.jpg', img)
            buff = base64.b64encode(buffer).decode('utf-8')
            with lock:
                frame = f"data:image/jpeg;base64,{buff}\n\n"
            time.sleep(0.05)

# Flask routes.
@app.route('/')
def index():
    return render_template('index.html')


# SocketIO "routes".
@socketio.on('get_frame')
def get_frame():
    global lock
    global frame
    with lock:
        emit('video_frame', {'image': frame}, broadcast=True)



def main():
    producer = threading.Thread(target=generate_frames, args=())
    producer.start()

    socketio.run(app, debug=True, port=5000, host="192.168.0.140", use_reloader=False)


if __name__ == "__main__":
    main()