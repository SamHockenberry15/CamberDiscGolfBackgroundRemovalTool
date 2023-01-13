from PyQt5.QtCore import QObject, pyqtSignal
from PIL import Image, ImageDraw
import numpy as np
import cv2 as cv

class Worker(QObject):

    progress = pyqtSignal(int)
    uiStatus = pyqtSignal(bool)
    finished = pyqtSignal()
    #Scaled percentage for hough circle image processing
    scale_percent = 10

    def __init__(self, inputFiles, outputDir, transparent):
        super(Worker, self).__init__()
        self.inputFiles = inputFiles
        self.outputDir = outputDir
        self.pbNum = int(90/(len(inputFiles)*2))
        self.imageNames = []
        self.tempTransparentBackgroundPictures = []
        self.tempWhiteBackgroundPictures = []
        self.finWhiteBackgroundPictures = []
        self.finTransparentBackgroundPictures = []
        self.transparent = transparent

    def run(self):
        self.uiStatus.emit(False)
        self.executePhotoEditing()

    def executePhotoEditing(self):
        if len(self.inputFiles) != 0 and len(self.outputDir) != 0:
            for img in self.inputFiles:
                input = cv.imread(img,cv.IMREAD_UNCHANGED)
                input = cv.cvtColor(input, cv.COLOR_BGR2RGB)
                splitDir = img.split('\\')
                name = splitDir[-1]
                open_cv_image = np.array(input)
                # Convert RGB to BGR
                curr = open_cv_image[:, :, ::-1].copy()

                dim = self.getScaledDim(curr.shape[0],curr.shape[1],self.scale_percent)

                detected_circles = self.detectCircles(curr, dim)

                if detected_circles is not None:
                    # Convert the circle parameters a, b and r to integers.
                    detected_circles = np.uint16(np.around(detected_circles))
                    pt = detected_circles[0, 0]

                    minX, maxX, minY, maxY = self.getCoordinates(pt)

                    original_height = open_cv_image.shape[0]
                    original_width = open_cv_image.shape[1]
                    lum_img = Image.new("L", [original_width, original_height], 0)

                    draw = ImageDraw.Draw(lum_img)
                    draw.pieslice([(minX, minY), (maxX, maxY)], 0, 360,
                                  fill=255, outline="white")
                    img_arr = np.array(open_cv_image)
                    lum_img_arr = np.array(lum_img)
                    final_img_arr = np.dstack((img_arr, lum_img_arr))

                    intMinX = int(minX)
                    intMaxX = int(maxX)
                    intMinY = int(minY)
                    intMaxY = int(maxY)

                    final_img_arr = final_img_arr[intMinY:intMaxY, intMinX:intMaxX, :]
                    fin_img = Image.fromarray(final_img_arr)
                    fin_img = fin_img.rotate(270, fillcolor=(255, 255, 255))
                    whiteBackground = Image.new("RGB", (int(maxX - minX), int(maxY - minY)), (255, 255, 255))
                    whiteBackground.paste(fin_img, box=None, mask=fin_img.split()[3])
                    self.imageNames.append(name)
                    self.progress.emit(self.pbNum)
                    self.saveFile(whiteBackground, name)

            self.progress.emit(100 - (len(self.inputFiles) * 3 * self.pbNum))
            self.finished.emit()

    def getScaledDim(self,height, width, scale_percent):
        scaled_width = width * scale_percent / 100
        scaled_height = height * scale_percent / 100
        scaled_width_int = int(scaled_width)
        scaled_height_int = int(scaled_height)
        return scaled_width_int, scaled_height_int

    def detectCircles(self, img, dim):
        resized = cv.resize(img, dim, interpolation=cv.INTER_AREA)
        imgray = cv.cvtColor(resized, cv.COLOR_BGR2GRAY)
        gray_blurred = cv.blur(imgray, (3, 3))
        return cv.HoughCircles(gray_blurred,
                                           cv.HOUGH_GRADIENT, 1, 85, param1=50,
                                           param2=30, minRadius=70, maxRadius=0)

    def getCoordinates(self, point):
        a, b, r = point[0], point[1], point[2]
        #Required to remove approximate error that comes from changing double -> int
        y_offset = 30
        #Required to shrink circle to edges of disc
        radius_offset = 0.15

        a = a * self.scale_percent
        b = b * self.scale_percent
        r = r * (self.scale_percent - radius_offset)

        return abs(a - r), r + a, abs(b - r + y_offset), r + b + y_offset


    def saveFile(self, img, nameWithExt):
        splitArr = str(nameWithExt).split('.')
        name = splitArr[0]
        if(self.transparent):
            print("Not implemented yet with new rewrite")
            # transP = self.tempTransparentBackgroundPictures[imgNum]
            # transP.save(self.outputDir+'\\\\'+name+'Transparent.png')
        whiteP = img
        whiteP.save(self.outputDir+'\\\\'+name+'White.png')
        self.progress.emit(self.pbNum)
