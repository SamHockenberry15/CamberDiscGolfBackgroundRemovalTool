from PyQt5.QtCore import QObject, pyqtSignal
from rembg import remove
from PIL import Image
from rembg.session_simple import SimpleSession

import numpy as np
import cv2 as cv


class Worker(QObject):
    imageNames = []
    transparentBackgroundPictures = []
    whiteBackgroundPictures = []

    progress = pyqtSignal(int)
    uiStatus = pyqtSignal(bool)
    finished = pyqtSignal()

    def __init__(self, inputFiles, outputDir, session):
        super(Worker, self).__init__()
        self.inputFiles = inputFiles
        self.outputDir = outputDir
        self.pbNum = int(98/(len(inputFiles)*3))
        self.imageNames = []
        self.transparentBackgroundPictures = []
        self.tempWhiteBackgroundPictures = []
        self.session = SimpleSession("u2net.onnx", session)

    def run(self):
        self.uiStatus.emit(False)
        self.executePhotoEditing()
        self.findEdgesOfImage()
        self.saveFiles()

    def executePhotoEditing(self):
        if len(self.inputFiles) != 0 and len(self.outputDir) != 0:
            for img in self.inputFiles:
                input = Image.open(img)
                splitDir = img.split('\\')
                name = splitDir[-1]
                output = remove(input, alpha_matting=True, session=self.session)
                self.progress.emit(self.pbNum)
                transP = output.rotate(270)
                self.transparentBackgroundPictures.append(transP)

                output.load()
                input_again_width, input_again_height = output.size
                whiteBackground = Image.new("RGB", (input_again_width + 50, input_again_height + 50), (255, 255, 255))
                whiteBackground.paste(output, mask=output.split()[3])
                finalWhiteBackground = whiteBackground.rotate(270, fillcolor=(255, 255, 255))

                self.tempWhiteBackgroundPictures.append(finalWhiteBackground)
                self.imageNames.append(name)
                self.progress.emit(self.pbNum)

    def findEdgesOfImage(self):
        for img in self.tempWhiteBackgroundPictures:
            open_cv_image = np.array(img)
            # pic = open_cv_image[:,:,0]
            # Convert RGB to BGR
            curr = open_cv_image[:, :, ::-1].copy()

            imgray = cv.cvtColor(curr, cv.COLOR_BGR2GRAY)
            gray_blurred = cv.blur(imgray, (3, 3))
            detected_circles = cv.HoughCircles(gray_blurred,
                                                cv.HOUGH_GRADIENT, 1, 20, param1=50,
                                                param2=30, minRadius=0, maxRadius=0)

            if detected_circles is not None:
                # Convert the circle parameters a, b and r to integers.
                detected_circles = np.uint16(np.around(detected_circles))
                pt = detected_circles[0,0]

                a, b, r = pt[0], pt[1], pt[2]

                minX = abs(a-r)
                maxX = r+a
                minY = abs(b-r)
                maxY = r+b

                newPic = open_cv_image[minY:maxY, minX:maxX,:]
                self.whiteBackgroundPictures.append(Image.fromarray(newPic))

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
        self.finished.emit()
