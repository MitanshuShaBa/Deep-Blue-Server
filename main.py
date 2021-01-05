import cv2
import numpy as np
import face_recognition
import os
import pickle
from datetime import datetime

path = 'Images'
images = []
# classNames = []
# myList = os.listdir(path)
# print(myList)
# for cl in myList:
#     curImg = cv2.imread(f'{path}/{cl}')
#     images.append(curImg)
#     classNames.append(os.path.splitext(cl)[0])
# print(classNames)


def find_encodings(images):
    encode_list = []
    for image in images:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(image)[0]
        encode_list.append(encode)
    return encode_list


def markAttendance(name):
    pass


# encodeListKnown = find_encodings(images)
# print('Encoding Complete')
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

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    # img = captureScreen()
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
            # print(name)
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 12), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            # markAttendance(name)

    cv2.imshow('Face Recognition', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
