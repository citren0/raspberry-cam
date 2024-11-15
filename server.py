from flask import Flask, Response, render_template
from picamera2 import Picamera2
from flask_socketio import SocketIO, emit
import base64
import time
import threading
from threading import Lock
import pyaudio
import base64
import struct
from dotenv import load_dotenv
import os
import numpy as np
import cv2

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)

frame = ""
frame_lock = Lock()

audio = b""
audio_lock = Lock()

secret = "asdf"


# Threads
def generate_frames():
    global frame_lock
    global frame
    picam = Picamera2()
    picam.configure(picam.create_video_configuration())
    picam.start()
    while True:
        img = picam.capture_array()
        frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        _, buffer = cv2.imencode('.jpg', frame_rgb)
        buff = base64.b64encode(buffer).decode('utf-8')
        with frame_lock:
            frame = f"data:image/jpeg;base64,{buff}\n\n"
        time.sleep(0.10)

def generate_audio():
    global audio_lock
    global audio
    # Audio configuration
    CHUNK = 2205
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 22050

    mic = pyaudio.PyAudio()
    stream = mic.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    while True:
        with audio_lock:
            audio = stream.read(CHUNK, exception_on_overflow=False)
        time.sleep(0.1)


# Flask routes.
@app.route('/')
def index():
    return render_template('index.html')


# SocketIO "routes".
@socketio.on('get_frame')
def get_frame(msg=None):
    global frame_lock
    global frame
    global secret
    if msg != None and 'secret' in msg and msg['secret'] == os.getenv('SERVER_SECRET'):
        with frame_lock:
            emit('video_frame', {'image': frame}, broadcast=False)

@socketio.on('get_audio')
def get_audio(msg=None):
    global audio_lock
    global audio
    global secret
    if msg != None and 'secret' in msg and msg['secret'] == os.getenv('SERVER_SECRET'):
        with audio_lock:
            emit('audio_data', {'data': list(struct.unpack('f' * (len(audio) // 4), audio))}, broadcast=False)


def main():
    frame_producer = threading.Thread(target=generate_frames, args=())
    frame_producer.start()

    audio_producer = threading.Thread(target=generate_audio, args=())
    audio_producer.start()

    socketio.run(app, debug=False, port=5000, host="0.0.0.0", use_reloader=False)


if __name__ == "__main__":
    main()