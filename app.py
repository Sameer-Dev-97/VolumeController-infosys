import cv2
import mediapipe as mp
import numpy as np
import math
import base64
import time
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, disconnect

# --- Pycaw setup for Windows Volume Control ---
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

try:
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    vol_min, vol_max, _ = volume.GetVolumeRange()
except Exception as e:
    print(f"Error initializing pycaw: {e}")
    volume = None
    vol_min, vol_max = 0.0, 1.0

# --- Flask & SocketIO Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key' 
socketio = SocketIO(app)

# --- Mediapipe Hand Setup ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# --- Webcam Setup ---
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 360)



stream_active = False
task_running = False

def process_gestures():
    """
    Main loop to capture video, process gestures, and emit data.
    (This function's content remains unchanged)
    """
    global stream_active, task_running
    
    print("Stream starting...")
    while cap.isOpened() and stream_active:
        start_time = time.time()
        
        success, img = cap.read()
        if not success:
            continue

        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        vol_percent = 0
        distance = 0
        gesture = "N/A"
        finger_count = 0

        if results.multi_hand_landmarks:
            hand_lm = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(img, hand_lm, mp_hands.HAND_CONNECTIONS)

            lm4 = hand_lm.landmark[4]
            lm8 = hand_lm.landmark[8]
            h, w, _ = img.shape
            x1, y1 = int(lm4.x * w), int(lm4.y * h)
            x2, y2 = int(lm8.x * w), int(lm8.y * h)
            
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)

            distance = math.hypot(x2 - x1, y2 - y1)
            vol_scalar = np.interp(distance, [30, 250], [0.0, 1.0])
            vol_percent = int(vol_scalar * 100)

            if volume:
                try:
                    volume.SetMasterVolumeLevelScalar(vol_scalar, None)
                except Exception as e:
                    print(f"Error setting volume: {e}")

            bar_height = np.interp(vol_percent, [0, 100], [300, 100])
            cv2.rectangle(img, (50, 100), (85, 300), (0, 255, 0), 3)
            cv2.rectangle(img, (50, int(bar_height)), (85, 300), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{vol_percent}%', (40, 330), cv2.FONT_HERSHEY_PLAIN,
                        2, (0, 255, 0), 3)
            
            tip_ids = [4, 8, 12, 16, 20] 
            landmarks = hand_lm.landmark
            for id in tip_ids[1:]:
                if landmarks[id].y < landmarks[id - 2].y:
                    finger_count += 1
            if landmarks[tip_ids[0]].x > landmarks[tip_ids[0] - 1].x:
                finger_count += 1
            cv2.putText(img, f'Fingers: {finger_count}', (170, 50), 
                        cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

            gesture = "N/A" 
            if finger_count == 0:
                gesture = "Closed"
            elif finger_count >= 4:
                gesture = "Open Hand"
            elif distance < 60 and finger_count <= 2:
                gesture = "Pinch"

        _, buffer = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        socketio.emit('video_frame', {'image': img_base64})

        end_time = time.time()
        response_time = int((end_time - start_time) * 1000)

        socketio.emit('update_data', {
            'volume': vol_percent,
            'distance': round(distance, 2),
            'gesture': gesture,
            'finger_count': finger_count,
            'response_time': response_time
        })
        
        socketio.sleep(0.01)
    
    print("Stream loop stopped.")
    task_running = False

# --- Login page---
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles the login page."""
    error = None
    if request.method == 'POST':
        # check for username and password
        if request.form['username'] == 'sameer' and request.form['password'] == 'sameer':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = 'Invalid Credentials. Please try again.'
   
    return render_template('login.html', error=error)

# --- Logout Route ---
@app.route('/logout')
def logout():
    """Logs the user out."""
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# --- Protected Index Route ---
@app.route('/')
def index():
    """Serves the main application page, protected by login."""
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    """Client connects, check for session."""
    if 'logged_in' not in session or not session['logged_in']:
        print("Unauthenticated client tried to connect.")
        disconnect()
        return
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    global stream_active
    stream_active = False
    print('Client disconnected, stopping stream.')

@socketio.on('start_stream')
def handle_start_stream():
    """Client requested to start the stream."""
    
    if 'logged_in' not in session or not session['logged_in']:
        return
        
    global stream_active, task_running
    if not task_running:
        stream_active = True
        task_running = True
        socketio.start_background_task(target=process_gestures)
        print("Stream started by client.")
    else:
        print("Stream already running.")

@socketio.on('stop_stream')
def handle_stop_stream():
    """Client requested to stop the stream."""
    global stream_active
    stream_active = False
    print("Stream stop requested by client.")

# --- Main Execution ---
if __name__ == '__main__':
    print("Starting Flask server... Open http://127.0.0.1:5000/login in your browser.")
    socketio.run(app, debug=True, use_reloader=False, host='127.0.0.1', port=5000)