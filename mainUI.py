from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QThread
import sys
import easygui as eg

from Worker import Worker


class Ui(QtWidgets.QMainWindow):
    inputFiles = []
    outputDir = ''

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('camberUIDialog.ui', self)

        self.inputFileButton.clicked.connect(self.selectInputFiles)
        self.outputDirButton.clicked.connect(self.selectOutputDir)
        self.executeButton.clicked.connect(self.startEditing)

        self.show()

    def selectInputFiles(self):
        self.inputFiles = eg.fileopenbox(title='Select image file(s)', multiple=True)
        self.inputSelection.setText(str(self.inputFiles))

    def selectOutputDir(self):
        self.outputDir = eg.diropenbox(title='Select output directory')
        self.outputSelection.setText(str(self.outputDir))

    def startEditing(self):
        self.mainLabel.setText("Started!")

        self.thread = QThread()
        self.worker = Worker(self.inputFiles,self.outputDir)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.reportProgress)
        self.worker.uiStatus.connect(self.setUiStatus)
        self.worker.finishedLabel.connect(self.setLabelFinished)
        self.thread.start()

    def setUiStatus(self, value):
        self.inputFileButton.setEnabled(value)
        self.outputDirButton.setEnabled(value)
        self.executeButton.setEnabled(value)
        self.inputSelection.setReadOnly(not value)
        self.outputSelection.setReadOnly(not value)

    def reportProgress(self, newVal):
        val = self.progressBar.value()
        self.progressBar.setValue(newVal + val)

    def setLabelFinished(self):
        self.mainLabel.setText("Finished!")



app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()