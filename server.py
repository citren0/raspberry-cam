from flask_socketio import SocketIO, emit
import base64
import time
import threading
from threading import Lock
import sys
import pyaudio
import base64
import struct

app = Flask(__name__)
socketio = SocketIO(app)

frame = ""
frame_lock = Lock()

audio = b""
audio_lock = Lock()


# Threads
def generate_frames():
    global frame_lock
    global frame
    camera = cv2.VideoCapture(0)
    while True:
        ret, img = camera.read()
        if ret:
            _, buffer = cv2.imencode('.jpg', img)
            buff = base64.b64encode(buffer).decode('utf-8')
            with frame_lock:
                frame = f"data:image/jpeg;base64,{buff}\n\n"
            time.sleep(0.05)

def generate_audio():
    global audio_lock
    global audio
    # Audio configuration
    CHUNK = 4410
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 44100

    mic = pyaudio.PyAudio()
    stream = mic.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    while True:
        with audio_lock:
            audio = stream.read(CHUNK)
        time.sleep(0.1)


# Flask routes.
@app.route('/')
def index():
    return render_template('index.html')


# SocketIO "routes".
@socketio.on('get_frame')
def get_frame():
    global frame_lock
    global frame
    with frame_lock:
        emit('video_frame', {'image': frame}, broadcast=False)

@socketio.on('get_audio')
def get_audio():
    global audio_lock
    global audio
    with audio_lock:
        emit('audio_data', {'data': list(struct.unpack('f' * (len(audio) // 4), audio))}, broadcast=False)


def main():
    frame_producer = threading.Thread(target=generate_frames, args=())
    frame_producer.start()

    audio_producer = threading.Thread(target=generate_audio, args=())
    audio_producer.start()

    socketio.run(app, debug=True, port=5000, host="0.0.0.0", use_reloader=False)


if __name__ == "__main__":
    main()