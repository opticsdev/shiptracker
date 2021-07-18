from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import  pyqtSignal, pyqtSlot, QThread
from PyQt5.QtGui import QImage, QPixmap
import sys
import numpy as np
import cv2

import shiptracker_gui


class TrackerApp(QtWidgets.QMainWindow, shiptracker_gui.Ui_Form):
    def __init__(self, parent=None):
        super(TrackerApp, self).__init__(parent)
        self.setupUi(self)


class PyTrackerCtrl():
    """PyCalc Controller class."""

    def __init__(self, view):
        """Controller initializer."""
        self._view = view
        # Connect signals and slots
        self._connectSpinBoxSignals()
        self.thread = VideoThread()

    def calc_ifov(self):
        pix_pitch = self._view.pitchBox.value()
        efl = self._view.eflBox.value()
        print(f'EFL: {efl}, Pitch: {pix_pitch}')
        ifov = (pix_pitch / 1000) / efl  # in rad
        ifov_asec = ifov * 180 / 3.1415926 * 3600  # in asec
        self._view.uradBox.setValue(ifov * 1e6)
        self._view.asecBox.setValue(ifov_asec)
        print(self._view.uradBox.value())

    def _connectSpinBoxSignals(self):
        self._view.pitchBox.valueChanged.connect(self.calc_ifov)

        self._view.eflBox.valueChanged.connect(self.calc_ifov)
        print('GUI Ready')

    def _closeEvent(self, event):
        self.thread.stop()
        event.accept()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.imageView.setPixmap(qt_img)




class Camera():
    def __init__(self, cam_num):
        """Setup camera and populate basic parameter space"""
        self.cam_num = None
        self.gain = 1

    def __str__(self):
        return f'OpenCV Camera {self.cam_num}'

    def initialize(self):
        self.cam = cv2.VideoCapture(self.cam_num)

    def close_camera(self):
        self.cam.release()

    def grab_frame(self):
        ret, self.cur_frame = self.cam.read()
        if ret:
            self.change_pixmap_signal.emit(self.cur_frame)
        return self.cur_frame

    def grab_sequence(self, num_frames):
        movie = []
        for _ in range(num_frames):
            movie.append(self.get_frame())
        return movie

    def set_props(self):
        pass

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self, cam):
        super().__init__()
        self._run_flag = True
        self.cam = cam

    def run(self):
        while self._run_flag:
            ret, cv_img = self.cam.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
        # shut down capture system


    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


def main():

    app = QApplication(sys.argv)
    view = TrackerApp()
    view.show()
    appCtrl = PyTrackerCtrl(view=view)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
