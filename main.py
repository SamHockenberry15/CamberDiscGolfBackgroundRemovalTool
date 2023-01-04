import easygui as eg
from PyQt5.QtCore import QThread

from Worker import Worker
import os
import onnxruntime as ort

from PyQt5 import QtWidgets
import sys

import camberUIDialog

# PyInstaller command: pyinstaller -F camberUIDialog.py -n "Camber Disc Golf Background Removal Tool" --icon=camberShirtLogo.png  --add-data "u2net.onnx;." --add-data "camberShirtLogo.png;."
# -w for release product
class Main():

    def run(self):
        try:
            app = QtWidgets.QApplication(sys.argv)
            mainWindow = QtWidgets.QMainWindow()
            self.ui = camberUIDialog.Ui_MainWindow()
            self.ui.setupUi(mainWindow)
            self.finishSetup()
            mainWindow.show()
            sys.exit(app.exec_())
        except Exception as e:
            print(e)

    def finishSetup(self):
        self.ui.inputFileButton.clicked.connect(self.selectInputFiles)
        self.ui.outputDirButton.clicked.connect(self.selectOutputDir)
        self.ui.executeButton.clicked.connect(self.startEditing)

        try:
            wd = sys._MEIPASS
        except AttributeError:
            wd = os.getcwd()
        file_path = os.path.join(wd, 'u2net.onnx')
        self.session = ort.InferenceSession(file_path)

    def selectInputFiles(self):
        self.inputFiles = eg.fileopenbox(title='Select image file(s)', multiple=True)
        self.ui.inputSelection.setText(str(self.inputFiles))

    def selectOutputDir(self):
        self.outputDir = eg.diropenbox(title='Select output directory')
        self.ui.outputSelection.setText(str(self.outputDir))

    def startEditing(self):
        self.ui.progressBar.setValue(0)
        self.ui.mainLabel.setText("Started!")

        self.threadsDone = False
        self.thread = QThread()

        self.worker = Worker(self.inputFiles, self.outputDir, self.session,
                             self.ui.transparentCheckbox.isChecked())


        if len(self.inputFiles) > 3:
            self.thread2 = QThread()
            indx = int(len(self.inputFiles) / 2)
            self.worker = Worker(self.inputFiles[0:indx], self.outputDir, self.session,
                                 self.ui.transparentCheckbox.isChecked())
            self.worker2 = Worker(self.inputFiles[indx::], self.outputDir, self.session,
                                  self.ui.transparentCheckbox.isChecked())

            self.worker2.moveToThread(self.thread2)
            self.thread2.started.connect(self.worker2.run)
            self.worker2.progress.connect(self.reportProgress)
            self.worker2.uiStatus.connect(self.setUiStatus)
            self.worker2.finished.connect(self.finished)
            self.thread2.start()

        self.worker.progress.connect(self.reportProgress)
        self.worker.uiStatus.connect(self.setUiStatus)
        self.worker.finished.connect(self.finished)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def setUiStatus(self, value):
        self.ui.inputFileButton.setEnabled(value)
        self.ui.outputDirButton.setEnabled(value)
        self.ui.executeButton.setEnabled(value)
        self.ui.inputSelection.setReadOnly(not value)
        self.ui.outputSelection.setReadOnly(not value)

    def reportProgress(self, newVal):
        val = self.ui.progressBar.value()
        self.ui.progressBar.setValue(newVal + val)

#Left off needing to resolve the "Started" and "Finished" labels when working with 2 Threads
    def finished(self):
        if not self.threadsDone and hasattr(self,"thread2"):
            self.threadsDone = True
        elif not hasattr(self,"thread2") or self.threadsDone:
            self.thread.quit()
            if hasattr(self, "thread2"):
                self.thread2.quit()
                delattr(self, "thread2")
            self.setUiStatus(True)
            self.ui.mainLabel.setText("Finished!")
            self.ui.progressBar.setValue(100)

if __name__ == "__main__":
    Main().run()
