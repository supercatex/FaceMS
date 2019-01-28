import dlib, os, cv2
import numpy as np
import pandas as pd


class FaceRecognizer:

    def __init__(self, shape_dat='', face_dat=''):
        # define model path.
        if shape_dat == '':
            shape_dat = 'libs/shape_predictor_68_face_landmarks.dat'
        if face_dat == '':
            face_dat = 'libs/dlib_face_recognition_resnet_model_v1.dat'

        # initialize objects.
        self.face_cascade = cv2.CascadeClassifier('libs/haarcascade_frontalface_default.xml')

        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(shape_dat)
        self.recognizer = dlib.face_recognition_model_v1(face_dat)
        self.orientation_str = ['front', 'left', 'right', '3', '4', '5', '6']

        self.description_filename = 'description.xlsx'
        self.users = {}

    def face_detect_cv(self, color_image):
        gray = cv2.cvtColor(color_image, cv2.COLOR_RGB2GRAY)
        rects = self.face_cascade.detectMultiScale(gray, minSize=(150, 150))
        faces = []
        for (x, y, w, h) in rects:
            face = {}
            face['d'] = dlib.rectangle(left=int(x), top=int(y), right=int(x + w), bottom=int(y + h))
            face['p1'] = (x, y)
            face['p2'] = (x + w, y + h)
            face['w'] = w
            face['h'] = h
            face['score'] = 0
            face['orientation'] = 0
            face['orientation_str'] = self.orientation_str[0]
            face['shape'] = None
            face['description'] = None
            face['display_name'] = 'unknown'
            face['distance'] = 0
            faces.append(face)
        return faces

    # Step 1.
    def face_detect(self, color_image, multi_detect=0):
        # face detect
        faces = []
        dets, scores, orientations = self.detector.run(color_image, multi_detect)
        for i, d in enumerate(dets):
            x1 = d.left()
            y1 = d.top()
            x2 = d.right()
            y2 = d.bottom()
            face = {}
            face['d'] = d
            face['p1'] = (x1, y1)
            face['p2'] = (x2, y2)
            face['w'] = int(x2 - x1)
            face['h'] = int(y2 - y1)
            face['score'] = scores[i]
            face['orientation'] = orientations[i]
            face['orientation_str'] = self.orientation_str[int(orientations[i])]
            face['shape'] = None
            face['description'] = None
            face['display_name'] = 'unknown'
            face['distance'] = 0
            faces.append(face)
        return faces

    # Step 2.
    def face_shape(self, color_image, face):
        # predict face shape
        shape = self.predictor(color_image, face['d'])
        face['shape'] = shape
        return face

    def faces_shape(self, color_image, faces):
        for face in faces:
            face = self.face_shape(color_image, face)
        return faces

    # Step 3.
    def face_description(self, color_image, face):
        # recognize face description
        if face['shape'] == None:
            face = self.face_shape(color_image, face)
        description = self.recognizer.compute_face_descriptor(color_image, face['shape'])
        v = np.array(description)
        face['description'] = v
        return face

    def faces_description(self, color_image, faces):
        for face in faces:
            face = self.face_description(color_image, face)
        return faces

    def draw_faces(self, color_image, faces, c=(0, 255, 0), w=2):
        image = color_image.copy()
        for face in faces:
            cv2.rectangle(image, face['p1'], face['p2'], c, w)
        return image

    def draw_shape(self, color_image, faces, c=(255, 0, 0), w=2, r=3):
        image = color_image.copy()
        for face in faces:
            shape = face['shape']
            for i in range(68):
                cv2.circle(image, (shape.part(i).x, shape.part(i).y), r, c, w)
        return image

    def calc_128D_by_path(self, path, export=False):
        for _, _, filenames in os.walk(path):
            descriptions = []

            for filename in filenames:
                if filename[-4:] != '.jpg': continue

                image = cv2.imread("%s/%s" % (path, filename), cv2.IMREAD_COLOR)
                color_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                faces = self.face_detect(color_image)
                for face in faces:
                    face = self.face_shape(color_image, face)
                    face = self.face_description(color_image, face)
                    descriptions.append(face['description'])

            desc = np.average(descriptions, axis=0)
            print(desc)

            if export:
                writer = pd.ExcelWriter("%s/%s" % (path, self.description_filename))
                data = pd.DataFrame(desc)
                data.to_excel(writer, '128D', float_format='%.9f')
                writer.save()

            return desc
        return None

    def load_users(self, path):
        for _, folders, _ in os.walk(path):
            for folder in folders:
                filepath = "%s/%s/%s" % (path, folder, self.description_filename)
                if os.path.exists(filepath):
                    data = pd.read_excel(filepath)
                    desc = data.iloc[:, :].values.tolist()
                    desc = np.array(desc).reshape(1, -1)[0]
                    username = folder
                    self.users[username] = desc

    def recognize(self, color_image, multi_detect=0, threshold=0.4):
        faces = self.face_detect(color_image, multi_detect)
        for face in faces:
            face = self.face_shape(color_image, face)
            face = self.face_description(color_image, face)
            desc = face['description']

            dists = {}
            for key, val in self.users.items():
                dist = np.sqrt(np.sum(np.square(val - desc)))
                dists[key] = dist

            dists_sorted = sorted(dists.items(), key=lambda d: d[1])
            print(dists_sorted)

            if len(dists_sorted) > 0:
                if dists_sorted[0][1] < threshold:
                    face['display_name'] = dists_sorted[0][0]
                    face['distance'] = dists_sorted[0][1]
        return faces
