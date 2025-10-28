# 🚀 Gesture-Based Volume Control System

Control your system's volume in real-time by simply pinching your fingers. This project uses computer vision to track your hand and maps the distance between your thumb and index finger to your computer's master volume.

It also features a live web dashboard built with Flask and Socket.IO to monitor the camera feed, recognized gestures, and performance metrics.

---

## ✨ Features

* **Real-time Volume Control:** Adjusts your Windows system volume based on your hand gesture.
* **Live Web Dashboard:** A clean UI to see all the data in one place.
* **Live Camera Feed:** Streams your webcam feed directly to the browser.
* **Gesture Recognition:** Detects and displays your current gesture (Pinch, Open Hand, Closed).
* **Performance Metrics:** Tracks key data like finger distance, volume %, and processing time (ms).
* **Data Visualization:** A live-updating chart shows the history of your volume and finger distance.
* **Secure Access:** Includes a simple login page to protect the dashboard.
* **Stream Controls:** Start and Stop the gesture detection from the web UI.


> **Note:** Replace the line above with a screenshot or, even better, a GIF of your project working! This is the most important part of a "beautiful" README.

---

## 💻 Tech Stack

This project combines several technologies:

* **🐍 Backend:**
    * **Python:** The core programming language.
    * **Flask:** A micro web framework for the server.
    * **Flask-SocketIO:** Enables real-time, bi-directional communication between the server and client.

* 📹 **Computer Vision & Gesture:**
    * **OpenCV:** For capturing and processing the webcam feed.
    * **Mediapipe:** For high-fidelity hand tracking and landmark detection.

* 🔊 **System Audio:**
    * **pycaw:** A Python library to control Windows Core Audio.

* 🌐 **Frontend:**
    * **HTML5 / CSS3:** For the structure and styling of the web dashboard.
    * **JavaScript (ES6+):** For client-side logic and DOM manipulation.
    * **Socket.IO (Client):** To receive real-time data from the server.
    * **Chart.js:** To render the live data graphs.

---

## ⚙️ How It Works

1.  **Server Setup:** A Flask server is initialized with Socket.IO.
2.  **User Login:** The user must log in via the `/login` page (credentials are hardcoded in `app.py`).
3.  **Start Stream:** When the user clicks "Start" on the dashboard, a `start_stream` event is sent to the server.
4.  **Gesture Loop:** The server starts the `process_gestures` function in a background thread.
5.  **CV Processing:**
    * OpenCV captures a frame from the webcam.
    * Mediapipe processes the frame to find hand landmarks.
6.  **Volume Calculation:**
    * The script calculates the distance between the thumb tip (Landmark 4) and the index finger tip (Landmark 8).
    * This distance is interpolated from a pixel range (e.g., 30-250) to a volume scalar (0.0-1.0).
    * `pycaw` uses this scalar to set the system's master volume.
7.  **Data Streaming:**
    * The video frame is encoded as Base64 and sent to the client via a `video_frame` event.
    * All metrics (volume %, distance, gesture, etc.) are sent via an `update_data` event.
8.  **Frontend Update:** The client-side JavaScript listens for these events and updates the dashboard elements (video, metrics, gesture status, and chart) instantly.
9.  **Stop Stream:** Clicking "Stop" sets a flag that gracefully terminates the gesture processing loop on the server.

---

## 🔧 Installation & Setup

Follow these steps to get the project running on your local machine.

### Prerequisites

* Python 3.7+
* A webcam
* A Windows operating system (for `pycaw`)

### 1. Clone the Repository



2.. Create a Virtual Environment


# On Windows
python -m venv venv
venv\Scripts\activate



3. Install Dependencies

flask
flask-socketio
opencv-python
mediapipe
numpy
pycaw
comtypes


pip install -r requirements.txt

4. Project Structure

![Uploading image.png…]()




    How to Use
Run the Server: From your terminal (with the virtual environment activated), run:


python app.py

```bash
git clone [https://github.com/your-username/your-project-repo.git](https://github.com/your-username/your-project-repo.git)
cd your-project-repo
