from PyQt5 import QtWidgets, uic, QtGui, Qt
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
        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.update_image)
        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(self.update_test_image)
        self.name = ""
        self.fr = FaceRecognizer()
        self.frame = None
        self.faces = None
        self.folder = "users"
        self.tree_view.doubleClicked.connect(self.ondbclick_tree_view)
        self.tab_main.currentChanged.connect(self.onchanged_tab_main)
        self.btn_start.clicked.connect(self.onclick_btn_start)
        self.btn_recognize.clicked.connect(self.onclick_btn_recognize)
        self.btn_upload.clicked.connect(self.onclick_btn_upload)
        self.model = QtGui.QStandardItemModel()

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

    def update_test_image(self):
        if self.cap.isOpened():
            success, frame = self.cap.read()
            if success:
                self.frame = frame.copy()
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.faces = self.fr.face_detect(rgb, multi_detect=1)
                rgb = self.fr.draw_faces(rgb, self.faces)
                h, w, c = frame.shape
                image = QtGui.QImage(rgb.data, w, h, c * w, QtGui.QImage.Format_RGB888)
                image = QtGui.QPixmap.fromImage(image)
                self.lab_test_image.setPixmap(image)

    def onclick_btn_lock(self):
        name = self.txt_name.toPlainText()
        self.name = name.strip()
        if len(self.name) > 0:
            self.btn_lock.setEnabled(False)
            self.btn_cancel.setEnabled(True)
            self.btn_capture.setEnabled(True)
            self.btn_calc.setEnabled(True)
            self.txt_name.setEnabled(False)
            self.timer2.stop()
            self.cap = cv2.VideoCapture(0)
            self.timer1.start(10)

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
        self.timer1.stop()
        self.timer2.stop()
        if self.cap is not None:
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

    def ondbclick_tree_view(self, index):
        name = index.model().itemData(index)[0]
        os.system("explorer.exe %s" % (self.folder + os.sep + name))

    def onchanged_tab_main(self, index):
        if index == 2:
            self.onclick_btn_cancel()
            self.fr.load_users(self.folder)
        else:
            self.onclick_btn_cancel()
            self.timer1.stop()
            self.timer2.stop()
            if self.cap is not None:
                self.cap.release()
            self.name = ""
            self.frame = None
            self.faces = None

        if index == 1:
            self.model = QtGui.QStandardItemModel()
            self.model.setHorizontalHeaderLabels(["名稱"])
            self.model.setRowCount(0)
            root = self.model.invisibleRootItem()
            for _, folder_names, _ in os.walk(self.folder):
                for folder_name in folder_names:
                    item = QtGui.QStandardItem(folder_name)
                    item.setEditable(False)
                    root.appendRow([item])
            self.tree_view.setModel(self.model)
            self.tree_view.expandAll()

    def onclick_btn_start(self):
        self.btn_start.setEnabled(False)
        self.btn_upload.setEnabled(False)
        self.btn_recognize.setEnabled(True)
        self.cap = cv2.VideoCapture(0)
        self.timer1.stop()
        self.timer2.start(10)

    def onclick_btn_recognize(self):
        rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.faces = self.fr.face_detect(rgb, multi_detect=1)
        self.faces = self.fr.faces_shape(rgb, self.faces)
        self.faces = self.fr.faces_description(rgb, self.faces)
        self.faces = self.fr.recognize(rgb, multi_detect=1)

        rgb = self.fr.draw_faces(rgb, self.faces)
        for face in self.faces:
            rgb = cv2.putText(rgb, face["display_name"], (face['p1'][0], face['p1'][1] - 2), cv2.FONT_HERSHEY_PLAIN, 0.8, (0, 255, 0), 1,
                              cv2.LINE_AA)

        h, w, c = self.frame.shape
        image = QtGui.QImage(rgb.data, w, h, c * w, QtGui.QImage.Format_RGB888)
        image = QtGui.QPixmap.fromImage(image)
        self.lab_test_image.setPixmap(image)

        self.btn_start.setEnabled(True)
        self.btn_upload.setEnabled(True)
        self.btn_recognize.setEnabled(False)
        self.timer2.stop()

    def onclick_btn_upload(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "QFileDialog.getOpenFileName()",
            "",
            "JPEG Files (*.jpg);;PNG Files (*.png)",
            options=options
        )
        if filename:
            print(filename)
            image = cv2.imread(filename, cv2.IMREAD_COLOR)
            self.frame = image.copy()
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, c = self.frame.shape
            image = QtGui.QImage(rgb.data, w, h, c * w, QtGui.QImage.Format_RGB888)
            image = QtGui.QPixmap.fromImage(image)
            self.lab_test_image.setPixmap(image)

            self.btn_start.setEnabled(False)
            self.btn_upload.setEnabled(False)
            self.btn_recognize.setEnabled(True)
            self.timer1.stop()
            self.timer2.stop()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainUi()
    window.show()
    app.exec_()