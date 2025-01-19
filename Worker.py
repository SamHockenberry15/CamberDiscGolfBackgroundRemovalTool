from PyQt5.QtCore import QObject, pyqtSignal
from PIL import Image, ImageDraw
import numpy as np
import cv2 as cv

class Worker(QObject):

    progress = pyqtSignal(int)
    uiStatus = pyqtSignal(bool)
    finished = pyqtSignal(int, int)
    #Scaled percentage for hough circle image processing
    scale = .3
    minRadius = 0
    croppedSuccessfully = 0
    unableToBeCropped = 0

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
        self.executePhotoEditing(cv.COLOR_BGR2HSV)

    def executePhotoEditing(self, colorSpace):
        if len(self.inputFiles) != 0 and len(self.outputDir) != 0:
            for img in self.inputFiles:
                input = cv.imread(img,cv.IMREAD_UNCHANGED)
                input = cv.resize(input,(0,0),fx = self.scale, fy = self.scale)
                self.minRadius = int(int(input.shape[0]) * (3/8))

                # cv.imshow("output", input)  Have a recursive call ONCE changing the input params of the cvtColor - inverse color space for White color objects
                # cv.waitKey(0)
                input_hsv = cv.cvtColor(input, colorSpace)
                # input_hsv = cv.bitwise_not(input)
                splitDir = img.split('\\')
                name = splitDir[-1]
                open_cv_image = np.array(input_hsv)
                # Convert RGB to BGR
                curr = open_cv_image[:, :, ::-1].copy()

                # dim = self.getScaledDim(curr.shape[0],curr.shape[1],self.scale_percent)

                detected_circles = self.detectCircles(curr)

                # show the output image
                # imgray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
                # input_hsv = cv.cvtColor(curr, cv.COLOR_BGR2GRAY)
                # cv.imshow("output", np.hstack([input_hsv, input]))
                # cv.waitKey(0)


                if detected_circles is not None:
                    self.croppedSuccessfully = self.croppedSuccessfully + 1
                    # Convert the circle parameters a, b and r to integers.
                    detected_circles = np.uint16(np.around(detected_circles))
                    pt = detected_circles[0, 0]

                    # convert the (x, y) coordinates and radius of the circles to integers
                    # DEBUG to see images and circles
                    # detected_circles = np.round(detected_circles[0, :]).astype("int")
                    # # loop over the (x, y) coordinates and radius of the circles
                    # for (x, y, r) in detected_circles:
                    #     # draw the circle in the output image, then draw a rectangle
                    #     # corresponding to the center of the circle
                    #     cv.circle(input, (x, y), r, (0, 255, 0), 4)
                    #     cv.rectangle(input, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
                    # # show the output image
                    # cv.imshow("output", np.hstack([input_hsv, input]))
                    # cv.waitKey(0)

                    minX, maxX, minY, maxY = self.getCoordinates(pt)

                    original_height = open_cv_image.shape[0]
                    original_width = open_cv_image.shape[1]
                    lum_img = Image.new("L", [original_width, original_height], 0)

                    try:
                        draw = ImageDraw.Draw(lum_img)
                        draw.pieslice([(minX, minY), (maxX, maxY)], 0, 360,
                                  fill=255, outline="white")
                    except:
                        print("error now -->   " + img)
                    img_arr = np.array(open_cv_image)
                    img_arr = cv.cvtColor(img_arr, cv.COLOR_HSV2RGB)
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
                else:
                    self.unableToBeCropped = self.unableToBeCropped + 1
                    print("No circles found for: " + img)

            self.progress.emit(100 - (len(self.inputFiles) * 3 * self.pbNum))
            self.finished.emit(self.croppedSuccessfully, self.unableToBeCropped)

    def getScaledDim(self,height, width, scale_percent):
        scaled_width = width * scale_percent / 100
        scaled_height = height * scale_percent / 100
        scaled_width_int = int(scaled_width)
        scaled_height_int = int(scaled_height)
        return scaled_width_int, scaled_height_int

    def detectCircles(self, img):
        imgray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        gray_blurred = cv.blur(imgray, (3, 3))
        # cv.imshow("output", gray_blurred)
        # cv.waitKey(0)
        # return cv.HoughCircles(gray_blurred,
        #                        cv.HOUGH_GRADIENT, 1.2, 85, param1=50,
        #                        param2=60, minRadius=355, maxRadius=400)
        return cv.HoughCircles(gray_blurred,
                                           cv.HOUGH_GRADIENT_ALT, 1.5, self.minRadius-25, param1=300,
                                           param2=.9, minRadius=self.minRadius, maxRadius=int(self.minRadius+45))

    def getCoordinates(self, point):
        #radius +1 to account for circle rim width
        a, b, r = point[0], point[1], point[2]+1
        #Required to remove approximate error that comes from changing double -> int
        # y_offset = 30
        #Required to shrink circle to edges of disc
        radius_offset = 0.15

        # a = a * self.scale_percent
        # b = b * self.scale_percent
        # r = r * (self.scale_percent - radius_offset)

        return abs(a - r), r + a, abs(b - r), r + b


    def saveFile(self, img, nameWithExt):
        splitArr = str(nameWithExt).split('.')
        name = splitArr[0]
        if self.transparent:
            print("Not implemented yet with new rewrite")
            # transP = self.tempTransparentBackgroundPictures[imgNum]
            # transP.save(self.outputDir+'\\\\'+name+'Transparent.png')
        whiteP = img
        whiteP.save(self.outputDir+'\\\\'+name+'White.png')
        self.progress.emit(self.pbNum)
