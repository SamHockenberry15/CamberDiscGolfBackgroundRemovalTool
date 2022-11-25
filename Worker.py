from PyQt5.QtCore import QObject, pyqtSignal
from rembg import remove
from PIL import Image

class Worker(QObject):
    imageNames = []
    transparentBackgroundPictures = []
    whiteBackgroundPictures = []

    progress = pyqtSignal(int)
    uiStatus = pyqtSignal(bool)
    finishedLabel = pyqtSignal()

    def __init__(self, inputFiles, outputDir):
        super(Worker, self).__init__()
        self.inputFiles = inputFiles
        self.outputDir = outputDir
        self.pbNum = int(98/(len(inputFiles)*3))

    def run(self):
        self.uiStatus.emit(False)
        self.executePhotoEditing()
        self.saveFiles()

    def executePhotoEditing(self):
        if len(self.inputFiles) != 0 and len(self.outputDir) != 0:
            for img in self.inputFiles:
                input = Image.open(img)
                splitDir = img.split('\\')
                name = splitDir[-1]
                output = remove(input, alpha_matting=True)
                self.progress.emit(self.pbNum)
                transP = output.rotate(270)
                self.transparentBackgroundPictures.append(transP)

                output.load()
                input_again_width, input_again_height = output.size
                whiteBackground = Image.new("RGB", (input_again_width + 50, input_again_height + 50), (255, 255, 255))
                whiteBackground.paste(output, mask=output.split()[3])
                finalWhiteBackground = whiteBackground.rotate(270, fillcolor=(255, 255, 255))

                self.whiteBackgroundPictures.append(finalWhiteBackground)
                self.imageNames.append(name)
                self.progress.emit(self.pbNum)

            self.saveFiles()

    def saveFiles(self):
        for i in range(0,len(self.imageNames)):
            nameWithExt = str(self.imageNames[i])
            splitArr = nameWithExt.split('.')
            name = splitArr[0]
            transP = self.transparentBackgroundPictures[i]
            whiteP = self.whiteBackgroundPictures[i]
            transP.save(self.outputDir+'\\\\'+name+'Transparent.png')
            whiteP.save(self.outputDir+'\\\\'+name+'White.png')
            self.progress.emit(self.pbNum)
        self.progress.emit(100-(len(self.inputFiles)*3*self.pbNum))
        self.uiStatus.emit(True)
        self.finishedLabel.emit()