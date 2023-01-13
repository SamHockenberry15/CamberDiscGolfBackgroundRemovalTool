import sys

from PyQt5.QtCore import QThread
from PyQt5 import QtWidgets

from Worker import Worker
import easygui as eg

class Main():

    def run(self):
        app = QtWidgets.QApplication(sys.argv)
        mainWindow = QtWidgets.QMainWindow()
        self.ui = camberUIDialog.Ui_MainWindow()
        self.ui.setupUi(mainWindow)
        self.finishSetup()
        mainWindow.show()
        sys.exit(app.exec_())


    def finishSetup(self):
        self.ui.inputFileButton.clicked.connect(self.selectInputFiles)
        self.ui.outputDirButton.clicked.connect(self.selectOutputDir)
        self.ui.executeButton.clicked.connect(self.startEditing)

    def selectInputFiles(self):
        self.inputFiles = eg.fileopenbox(title='Select image file(s)', multiple=True)
        self.ui.inputSelection.setText(str(self.inputFiles))

    def selectOutputDir(self):
        self.outputDir = eg.diropenbox(title='Select output directory')
        self.ui.outputSelection.setText(str(self.outputDir))

    def startEditing(self):
        self.isFinished = False
        try:
            if hasattr(self,"thread"):
                self.thread.quit()
            if hasattr(self,"thread2"):
                self.thread2.quit()

            self.ui.progressBar.setValue(0)
            self.ui.mainLabel.setText("Started!")

            self.threadsDone = False
            self.thread = QThread()

            self.worker = Worker(self.inputFiles, self.outputDir,
                                 self.ui.transparentCheckbox.isChecked())


            if len(self.inputFiles) > 3:
                self.thread2 = QThread()
                indx = int(len(self.inputFiles) / 2)
                self.worker = Worker(self.inputFiles[0:indx], self.outputDir,
                                     self.ui.transparentCheckbox.isChecked())
                self.worker2 = Worker(self.inputFiles[indx::], self.outputDir,
                                      self.ui.transparentCheckbox.isChecked())

                self.worker2.moveToThread(self.thread2)
                self.worker2.progress.connect(self.reportProgress)
                self.worker2.uiStatus.connect(self.setUiStatus)
                self.thread2.started.connect(self.worker2.run)
                self.worker2.finished.connect(self.endThread2)
                self.thread2.start()

            self.worker.progress.connect(self.reportProgress)
            self.worker.uiStatus.connect(self.setUiStatus)
            self.worker.moveToThread(self.thread)
            self.worker.finished.connect(self.endThread)
            self.thread.started.connect(self.worker.run)
            self.thread.start()

        except Exception as e:
            print(e)

    def setUiStatus(self, value):
        self.ui.inputFileButton.setEnabled(value)
        self.ui.outputDirButton.setEnabled(value)
        self.ui.executeButton.setEnabled(value)
        self.ui.inputSelection.setReadOnly(not value)
        self.ui.outputSelection.setReadOnly(not value)

    def reportProgress(self, newVal):
        val = self.ui.progressBar.value()
        self.ui.progressBar.setValue(newVal + val)

    def endThread(self):
        self.thread.quit()
        if self.isFinished or not hasattr(self,"thread2"):
            self.endExec()
        else:
            self.isFinished = True

    def endThread2(self):
        self.thread2.quit()
        if self.isFinished:
            self.endExec()
        else:
            self.isFinished = True

    def endExec(self):
        self.setUiStatus(True)
        self.ui.mainLabel.setText("Finished!")
        self.ui.progressBar.setValue(100)

    def finished(self):
        if hasattr(self,"thread2") and self.thread.isFinished() and self.thread2.isFinished():
            self.setUiStatus(True)
            self.ui.mainLabel.setText("Finished!")
            self.ui.progressBar.setValue(100)
        elif self.thread.isFinished() and not hasattr(self,"thread2"):
            self.setUiStatus(True)
            self.ui.mainLabel.setText("Finished!")
            self.ui.progressBar.setValue(100)

import camberUIDialog
# PyInstaller command: pyinstaller -F mainProgram.py -n "Camber Disc Golf Background Removal Tool" --icon=camberShirtLogo.png --add-data "camberShirtLogo.png;."

if __name__ == "__main__":
    Main().run()
# -w for release product
