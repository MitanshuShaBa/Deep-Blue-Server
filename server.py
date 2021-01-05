import time
import cv2
import pickle
import face_recognition
import numpy as np
from flask import Flask, render_template, Response

app = Flask(__name__)
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
    return render_template('index.html')


def gen():
    """Video streaming generator function."""
    cap = cv2.VideoCapture(0)

    # Read until video is completed
    while cap.isOpened():
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
                    name = label_names[faceLabels[matchIndex]].upper()
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 12), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

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


if __name__ == "__main__":
    app.run('localhost', 5000, debug=True)
