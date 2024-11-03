from flask import Flask, Response, render_template
import cv2
from flask_socketio import SocketIO, emit
import base64
import time
import threading

app = Flask(__name__)
socketio = SocketIO(app)

camera = ""
lock = ""

def get_frame():
    if lock != "":
        with lock:
            ret, img = camera.read()
            if ret:
                _, buffer = cv2.imencode('.jpg', img)
                frame = base64.b64encode(buffer).decode('utf-8')
                return f"data:image/jpeg;base64,{frame}\n\n"
    else:
        return f"data:image/jpeg;base64,asdf\n\n"


# Flask routes.
@app.route('/')
def index():
    return render_template('index.html')


# SocketIO "routes".
@socketio.on('get_frame')
def get_frame_socket():
    emit('video_frame', {'image': get_frame()}, broadcast=True)




def main():
    lock = threading.Lock()
    camera = cv2.VideoCapture(0)
    socketio.run(app, debug=True, port=5000, host="192.168.0.140", use_reloader=False)


if __name__ == "__main__":
    main()