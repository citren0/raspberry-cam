from flask import Flask, Response, render_template
import cv2
from flask_socketio import SocketIO, emit
import base64
import time
from picamera2 import Picamera2
# import pyaudio

app = Flask(__name__)
socketio = SocketIO(app)

# def generate_audio():
#     chunk = 1024
#     p = pyaudio.PyAudio()

#     stream = p.open(format=pyaudio.paInt16,
#                     channels=1,
#                     rate=44100,
#                     input=True,
#                     frames_per_buffer=chunk)

#     while True:
#         data = stream.read(chunk)
#         audio_data = base64.b64encode(data).decode('utf-8')
#         yield audio_data


def generate_frames():
    cam = Picamera2()
    height = 480
    width = 640
    middle = (int(width / 2), int(height / 2))
    cam.configure(cam.create_video_configuration(main={"format": 'RGB888', "size": (width, height)}))
    while True:
        img = cam.capture_array()
        if ret:
            _, buffer = cv2.imencode('.jpg', img)
            frame = base64.b64encode(buffer).decode('utf-8')
            yield f"data:image/jpeg;base64,{frame}\n\n"


# Flask routes.
@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('video_stream')
def handle_video():
    for frame in generate_frames():
        emit('video_frame', {'image': frame}, broadcast=True)
        time.sleep(0.05)

# @socketio.on('audio_stream')
# def handle_audio():
#     for audio in generate_audio():
#         emit('audio_data', {'audio': audio}, broadcast=True)
#         time.sleep(0.01)


def main():
    socketio.run(app, debug=True)


if __name__ == "__main__":
    main()