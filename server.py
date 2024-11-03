from flask import Flask, Response, render_template
import cv2
from flask_socketio import SocketIO, emit
import base64
import time
import threading


app = Flask(__name__)
socketio = SocketIO(app)

frame = ""


def generate_frames():
    camera = cv2.VideoCapture(0)
    while True:
        ret, img = camera.read()
        if ret:
            _, buffer = cv2.imencode('.jpg', img)
            buff = base64.b64encode(buffer).decode('utf-8')
            frame = f"data:image/jpeg;base64,{buff}\n\n"        


# Flask routes.
@app.route('/')
def index():
    return render_template('index.html')


# SocketIO "routes".
@socketio.on('video_stream')
def handle_video():
    while True:
        emit('video_frame', {'image': frame}, broadcast=True)
        time.sleep(0.05)




def main():
    producer = threading.Thread(target=generate_frames, args=())
    producer.start()

    socketio.run(app, debug=True, port=5000, host="192.168.0.140", use_reloader=False)


if __name__ == "__main__":
    main()