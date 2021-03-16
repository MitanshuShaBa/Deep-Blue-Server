import datetime
import time
import cv2
import pickle
import face_recognition
import numpy as np
from flask import Flask, render_template, Response, request, json, jsonify, redirect, url_for, session, has_app_context
import requests
import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__, static_folder='static')
db_name = 'tmp.db'
app.secret_key = 'Deep Blue'
cred = credentials.Certificate("deep-blue-asst-firebase-adminsdk-w87p0-6efd8bff07.json")
firebase_app = firebase_admin.initialize_app(cred)
firestore_db = firestore.client(firebase_app)
FRAMES_TO_CAPTURE = 6
ASK_NAME = False
CAM_ON = True

conn = sqlite3.connect(db_name)
conn.execute('''CREATE TABLE IF NOT EXISTS info
            (id integer PRIMARY KEY, name text, temp real, displayName text)''')
try:
    conn.execute('''
                INSERT INTO info(id, name, temp, displayName) VALUES (1,NULL,NULL,NULL)
                ''')
except sqlite3.IntegrityError:
    pass
conn.commit()
conn.close()

with open('face-encodings.pickle', 'rb') as f:
    encodeListKnown = pickle.load(f)
    print('encoding list loaded')

with open('face-labels.pickle', 'rb') as f:
    faceLabels = pickle.load(f)
    print('labels list loaded')

with open("labels-to-name.pickle", 'rb') as f:
    label_names = pickle.load(f)
    print('names for labels loaded')
    label_names = {v: k for k, v in label_names.items()}


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html', getName=ASK_NAME)


def gen():
    """Video streaming generator function."""
    global ASK_NAME
    curr_frame = 0

    cap = cv2.VideoCapture(0)

    def mark_attendance(user_id):
        print(user_id, 'was seen')
        cap.release()
        r = requests.post('http://localhost:5000/face_info', json={"name": user_id})
        CAM_ON = False

    # Read until video is completed
    while CAM_ON:
        # Capture frame-by-frame
        ret, img = cap.read()
        if ret:
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                # print(faceDis)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    # name = classNames[matchIndex].upper()
                    name = label_names[faceLabels[matchIndex]]
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name.upper(), (x1 + 6, y2 - 12), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    mark_attendance(name)
                else:
                    if curr_frame < FRAMES_TO_CAPTURE:
                        print("Saving Frame")
                        cv2.imwrite(f"{datetime.datetime.now()}.jpg", img)
                        curr_frame += 1
                    else:
                        ASK_NAME = True
                        cap.release()

            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            time.sleep(0.01)
        else:
            break


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/log")
def log():
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM info''')
    rows = cur.fetchall()
    conn.close()
    _, name, temp, displayName = rows[0]
    return {"name": name, "temp": temp, "displayName": displayName}


@app.route('/temp', methods=['POST'])
def set_temp():
    """201 created 409 conflict"""
    conn = sqlite3.connect(db_name)
    temp = request.json['temp']
    try:
        conn.execute(f'''UPDATE info SET temp="{temp}" WHERE id=1 ''')
        conn.commit()
    except sqlite3.OperationalError as e:
        return Response(str(e), status=409)
    conn.close()

    return app.response_class(
        response=json.dumps({"temp": temp}),
        status=201,
        mimetype='application/json'
    )


@app.route('/face_info', methods=['POST'])
def set_info():
    conn = sqlite3.connect(db_name)
    name = request.json['name']
    conn.execute(f'''UPDATE info SET name="{name}" WHERE id=1 ''')
    conn.commit()
    conn.close()

    return {"name": name}

@app.route('/displayName', methods=['POST'])
def set_display_name():
    conn = sqlite3.connect(db_name)
    name = request.json['displayName']
    conn.execute(f'''UPDATE info SET displayName="{displayName}" WHERE id=1 ''')
    conn.commit()
    conn.close()

    return {"displayName": displayName}


@app.route('/reset')
def reset():
    conn = sqlite3.connect(db_name)
    conn.execute(f'''UPDATE info SET name=NULL, temp=NULL, displayName=NULL WHERE id=1 ''')
    conn.commit()
    conn.close()

    return "Reset"


@app.route("/info")
def info():
    return render_template("info.html")


@app.route("/username/<userid>")
def get_name(userid):
    doc = firestore_db.collection("users").document(userid).get()
    return doc.to_dict()


@app.route("/visit_log", methods=["POST"])
def log_to_firebase():
    user_id = request.json['user_id']
    temp = request.json['temp']
    purpose = request.json['purpose']

    firestore_db.collection('visitation_log').add({"is_wearing_mask": False, "purpose": purpose, "temperature": temp,
                                                   "time_of_entry": firestore.SERVER_TIMESTAMP, "time_of_exit": None,
                                                   "user_id": user_id})

    return "Added to firestore database"


if __name__ == "__main__":
    app.run('localhost', 5000, debug=True)
