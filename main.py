from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import QTimer
import sys
import os
import cv2
from FaceRecognizer import FaceRecognizer
import time


path = os.getcwd()
print(path)
filename = path + os.sep + "ui" + os.sep + "main.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(filename)


class MainUi(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.btn_lock.clicked.connect(self.onclick_btn_lock)
        self.btn_cancel.clicked.connect(self.onclick_btn_cancel)
        self.btn_capture.clicked.connect(self.onclick_btn_capture)
        self.btn_calc.clicked.connect(self.onclick_btn_calc)
        self.txt_name.setFocus(True)
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.name = ""
        self.fr = FaceRecognizer()
        self.frame = None
        self.faces = None
        self.folder = "users"

    def update_image(self):
        if self.cap.isOpened():
            success, frame = self.cap.read()
            if success:
                self.frame = frame.copy()
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.faces = self.fr.face_detect(rgb)
                rgb = self.fr.draw_faces(rgb, self.faces)
                self.faces = self.fr.faces_shape(frame, self.faces)
                rgb = self.fr.draw_shape(rgb, self.faces)
                h, w, c = frame.shape
                image = QtGui.QImage(rgb.data, w, h, c * w, QtGui.QImage.Format_RGB888)
                image = QtGui.QPixmap.fromImage(image)
                self.lab_image.setPixmap(image)

    def onclick_btn_lock(self):
        name = self.txt_name.toPlainText()
        self.name = name.strip()
        if len(self.name) > 0:
            self.btn_lock.setEnabled(False)
            self.btn_cancel.setEnabled(True)
            self.btn_capture.setEnabled(True)
            self.btn_calc.setEnabled(True)
            self.txt_name.setEnabled(False)
            self.cap = cv2.VideoCapture(0)
            self.timer.start(50)
        else:
            QtWidgets.QMessageBox.about(None, "提示", "請先輸入名稱")

    def onclick_btn_cancel(self):
        self.btn_lock.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.btn_capture.setEnabled(False)
        self.btn_calc.setEnabled(False)
        self.txt_name.setEnabled(True)
        self.txt_name.setText("")
        self.txt_name.setFocus(True)
        self.timer.stop()
        self.cap.release()
        self.name = ""
        self.frame = None
        self.faces = None

    def onclick_btn_capture(self):
        if self.faces is not None and len(self.faces) == 1:
            user_folder = self.folder + os.sep + self.name
            if not os.path.isdir(user_folder):
                os.makedirs(user_folder)

            for face in self.faces:
                image_name = str(int(time.time()))
                image = self.frame[face['p1'][1]:face['p2'][1], face['p1'][0]:face['p2'][0]]
                cv2.imwrite(user_folder + os.sep + image_name + ".jpg", image)

            QtWidgets.QMessageBox.about(None, "提示", "成功存檔！")
        else:
            QtWidgets.QMessageBox.about(None, "提示", "請確保只有一張人臉！")

    def onclick_btn_calc(self):
        user_folder = self.folder + os.sep + self.name
        self.fr.calc_128D_by_path(user_folder, True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainUi()
    window.show()
    app.exec_()