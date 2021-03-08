import cv2
import os
import numpy as np
import face_recognition

from PIL import Image
import pickle

SCALE_FACTOR = 0.5

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(BASE_DIR, "Images")


# face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')


def find_encodings(images):
    encode_list = []
    for image in images:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(image)[0]
        encode_list.append(encode)
    return encode_list


current_id = 0
label_ids = {}
y_labels = []
x_locations = []
x_encodings = []

for root, dirs, files in os.walk(image_dir):
    for file in files:
        if file.endswith("jpg") or file.endswith('png'):
            path = os.path.join(root, file)
            label = os.path.basename(root).replace(" ", "-")
            print(label, path)
            if label not in label_ids:
                label_ids[label] = current_id
                current_id += 1
            id_ = label_ids[label]
            # print(label_ids)
            # y_labels.append(label) # some number
            # x_train.append(path) # verify this image, turn into a NUMPY arrray, GRAY
            # pil_image = Image.open(path).convert("L")  # grayscale
            # size = (550, 550)
            # final_image = pil_image.resize(size, Image.ANTIALIAS)
            image = cv2.imread(path, -1)
            final_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # image_array = np.array(final_image, "uint8")
            # image_array = cv2.resize(final_image, (400, 400), cv2.INTER_AREA)
            image_array = cv2.resize(final_image, (0, 0), None, SCALE_FACTOR, SCALE_FACTOR)
            # print(image_array)
            # faces = face_cascade.detectMultiScale(image_array, scaleFactor=1.5, minNeighbors=5)
            face_locations = face_recognition.face_locations(image_array)
            face_encodings = face_recognition.face_encodings(image_array)
            # print(faces)

            for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                # print(image_array)
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                roi = image_array[top:bottom, left: right]
                # cv2.imshow('ROI Image', roi)

                cv2.rectangle(image_array, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.imshow('Face Image', image_array)
                print(id_)
                # cv2.waitKey()

                x_locations.append(roi)
                x_encodings.append(encoding)
                y_labels.append(id_)

print(len(y_labels))
print(len(x_encodings))
print(label_ids)

with open("labels-to-name.pickle", 'wb') as f:
    pickle.dump(label_ids, f)

with open("face-encodings.pickle", 'wb') as f:
    pickle.dump(x_encodings, f)

with open('face-labels.pickle', 'wb') as f:
    pickle.dump(y_labels, f)

# print(label_ids)

# encodeListKnown = find_encodings(images)
# print(encodeListKnown)
cv2.destroyAllWindows()
