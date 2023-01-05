from PyQt5.QtCore import QObject, pyqtSignal
from rembg import remove
from PIL import Image
from rembg.session_simple import SimpleSession

import numpy as np
import cv2 as cv


class Worker(QObject):

    progress = pyqtSignal(int)
    uiStatus = pyqtSignal(bool)
    finished = pyqtSignal()

    def __init__(self, inputFiles, outputDir, session, transparent):
        super(Worker, self).__init__()
        self.inputFiles = inputFiles
        self.outputDir = outputDir
        self.pbNum = int(90/(len(inputFiles)*2))
        self.imageNames = []
        self.tempTransparentBackgroundPictures = []
        self.tempWhiteBackgroundPictures = []
        self.finWhiteBackgroundPictures = []
        self.finTransparentBackgroundPictures = []
        self.session = SimpleSession("u2net.onnx", session)
        self.transparent = transparent

    def run(self):
        self.uiStatus.emit(False)
        self.executePhotoEditing()

    def executePhotoEditing(self):
        if len(self.inputFiles) != 0 and len(self.outputDir) != 0:
            for img in self.inputFiles:
                input = Image.open(img)
                splitDir = img.split('\\')
                name = splitDir[-1]
                output = remove(input, alpha_matting=True, session=self.session)
                transP = output.rotate(270)
                self.tempTransparentBackgroundPictures.append(transP)

                output.load()
                input_again_width, input_again_height = output.size
                whiteBackground = Image.new("RGB", (input_again_width + 50, input_again_height + 50), (255, 255, 255))
                whiteBackground.paste(output, mask=output.split()[3])
                finalWhiteBackground = whiteBackground.rotate(270, fillcolor=(255, 255, 255))

                self.tempWhiteBackgroundPictures.append(finalWhiteBackground)
                self.imageNames.append(name)
                self.progress.emit(self.pbNum)

            self.cropImages()
            self.progress.emit(100 - (len(self.inputFiles) * 3 * self.pbNum))
            self.finished.emit()

    def cropImages(self):
        for num in range(0,len(self.tempWhiteBackgroundPictures)):
            open_cv_image = np.array(self.tempWhiteBackgroundPictures[num])
            # Convert RGB to BGR
            curr = open_cv_image[:, :, ::-1].copy()

            imgray = cv.cvtColor(curr, cv.COLOR_BGR2GRAY)
            gray_blurred = cv.blur(imgray, (3, 3))
            detected_circles = cv.HoughCircles(gray_blurred,
                                                cv.HOUGH_GRADIENT, 1, 20, param1=50,
                                                param2=30, minRadius=350, maxRadius=0)

            if detected_circles is not None:
                # Convert the circle parameters a, b and r to integers.
                detected_circles = np.uint16(np.around(detected_circles))
                pt = detected_circles[0,0]

                a, b, r = pt[0], pt[1], pt[2]

                minX = abs(a-r)
                maxX = r+a
                minY = abs(b-r)
                maxY = r+b

                newWhitePic = open_cv_image[minY:maxY, minX:maxX, :]
                self.saveFile(Image.fromarray(newWhitePic),num)


    def saveFile(self, img, imgNum):
        nameWithExt = str(self.imageNames[imgNum])
        splitArr = nameWithExt.split('.')
        name = splitArr[0]
        if(self.transparent):
            transP = self.tempTransparentBackgroundPictures[imgNum]
            transP.save(self.outputDir+'\\\\'+name+'Transparent.png')
        whiteP = img
        whiteP.save(self.outputDir+'\\\\'+name+'White.png')
        self.progress.emit(self.pbNum)

    def saveFiles(self):
        for i in range(0,len(self.imageNames)):
            nameWithExt = str(self.imageNames[i])
            splitArr = nameWithExt.split('.')
            name = splitArr[0]
            if(self.transparent):
                transP = self.tempTransparentBackgroundPictures[i]
                transP.save(self.outputDir+'\\\\'+name+'Transparent.png')
            whiteP = self.finWhiteBackgroundPictures[i]
            whiteP.save(self.outputDir+'\\\\'+name+'White.png')
            self.progress.emit(self.pbNum)
        self.progress.emit(100-(len(self.inputFiles)*3*self.pbNum))
        self.finished.emit()
