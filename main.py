"""
# Hello , DDT #

By Qingqiu
Apr. 2019
"""
import win32gui
import win32ui
import win32con
import win32api
import cv2
import math
import os
import re
import random
import time
import PyHook3 as ph
import pythoncom as pc
import numpy as np
import tensorflow as tf
from tensorflow import keras as kr

# we get a model that can recognize different numbers after training
# - using MNIST data set
# + using data set gathered on the internet
# basing on a cnn


def trainWithCNN(cols, rows, epochs):
    """
    # to train
    # then get one model

    retval -> None
    """
    if not os.path.exists('./models/trainedWithCNN{}X{}.h5'.format(cols, rows)):
        # -- to construct the structure of the network
        inputs = kr.layers.Input(shape=[cols, rows, 1])
        convoluted = kr.layers.Conv2D(filters=8, kernel_size=[2, 2], strides=[
            1, 1], activation=tf.nn.relu, data_format='channels_last', padding='same')(inputs)
        pooled = kr.layers.MaxPooling2D(pool_size=[2, 2], strides=[
                                        1, 1], data_format='channels_last')(convoluted)
        flattened = kr.layers.Flatten()(pooled)
        densed = kr.layers.Dense(100, activation=tf.nn.relu)(flattened)
        softmaxed = kr.layers.Dense(10, activation=tf.nn.softmax)(densed)
        # then we create an instance
        theClassifier = kr.models.Model(inputs=inputs, outputs=softmaxed)
        # to configure
        theClassifier.compile(optimizer=kr.optimizers.Adam(
        ), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        # -- then we should process data
        contentsTrain, labelsTrain, contentsTest, labelsTest = prepareData()
        # -- to train and test
        # to train
        theClassifier.fit(contentsTrain, labelsTrain, epochs=epochs)
        # to test
        loss, acc = theClassifier.evaluate(
            contentsTest, labelsTest)
        print('Loss and accuracy: {},{}.'.format(loss, acc))
        # then save
        theClassifier.save(
            './models/trainedWithCNN{}X{}.h5'.format(cols, rows))
    else:
        pass


def trainWithBPNN(cols, rows, epochs):
    """
    #

    retval -> None
    """
    if not os.path.exists('./models/trainedWithBPNN{}X{}.h5'.format(cols, rows)):
        # -- construct the network
        # basic structure
        inputs = kr.layers.Input(shape=[cols, rows, 1])
        flattened = kr.layers.Flatten()(inputs)
        inputLayer = kr.layers.Dense(1024, activation=tf.nn.relu)(flattened)
        hiddenLayer = kr.layers.Dense(100, activation=tf.nn.relu)(inputLayer)
        outputLayer = kr.layers.Dense(
            10, activation=tf.nn.softmax)(hiddenLayer)
        theClassifier = kr.models.Model(inputs=inputs, outputs=outputLayer)
        # cofiguration
        theClassifier.compile(optimizer=kr.optimizers.Adam(
        ), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        # prepare data
        contentsTrain, labelsTrain, contentsTest, labelsTest = prepareData()
        # to train
        theClassifier.fit(contentsTrain, labelsTrain, epochs=epochs)
        # to test
        loss, acc = theClassifier.evaluate(
            contentsTest, labelsTest)
        print('Loss and accuracy: {},{}.'.format(loss, acc))
        # then save
        theClassifier.save(
            './models/trainedWithBPNN{}X{}.h5'.format(cols, rows))
    else:
        pass


def train(cols, rows, epochs, WithCNN):
    if WithCNN:
        trainWithCNN(cols, rows, epochs)
    else:
        trainWithBPNN(cols, rows, epochs)


def prepareData():
    """
    # in order to train

    retval -> [tuple] 
        # (contentsTrain,labelsTrain,contentsTest,labelsTest)
        # all are numpy ndarraies and have been reshaped
    """
    trainDataList, testDataList = [], []
    flagTrainOrTest, classLast = 0, 0
    for fileName in os.listdir('./res/yinshua/'):
        tmpImg = cv2.bitwise_not(cv2.imread(
            './res/yinshua/'+fileName, 0)).tolist()
        tmpClass = int(re.findall('img(.*)-', fileName)[0])-1
        if classLast == tmpClass:
            if flagTrainOrTest == 2:
                flagTrainOrTest = 0
                testDataList.append((tmpImg, tmpClass))
            else:
                flagTrainOrTest += 1
                trainDataList.append((tmpImg, tmpClass))
        else:
            classLast = tmpClass
            flagTrainOrTest = 1
            trainDataList.append((tmpImg, tmpClass))
    #
    random.shuffle(trainDataList)
    trainData = np.split(np.array(trainDataList), 2, axis=-1)
    testData = np.split(np.array(testDataList), 2, axis=-1)
    contentsTrain, contentsTest = [], []
    for content in trainData[0]:
        contentsTrain.append(content[0])
    for content in testData[0]:
        contentsTest.append(content[0])
    return np.asfarray(contentsTrain).reshape(len(trainDataList), 16, 16, 1)/255.0, trainData[1].reshape(len(trainDataList),), np.asfarray(contentsTest).reshape(len(testDataList), 16, 16, 1)/255.0, testData[1].reshape(len(testDataList),)


def getPixelColor(x, y):
    gdi32 = windll.gdi32
    user32 = windll.user32
    hdc = user32.GetDC(None)  # 获取颜色值
    pixel = gdi32.GetPixel(hdc, x, y)  # 提取RGB值
    r = pixel & 0x0000ff
    g = (pixel & 0x00ff00) >> 8
    b = pixel >> 16
    return r, g, b


def windowCapture(targetArea=[(0, 0), (100, 100)], isDistance=0):
    """
    # while get [(x1,y1),(x2,y2)] , copy certain area of active window at that moment
    # generate one file named 'oneShot.jpg' under folder './tmp'

    retval -> None
    """
    # get active window's divice context at the moment
    windowDC = win32gui.GetWindowDC(0)
    mfcDC = win32ui.CreateDCFromHandle(windowDC)  # obviously
    # emmm
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitmap = win32ui.CreateBitmap()
    saveBitmap.CreateCompatibleBitmap(
        mfcDC, targetArea[1][0], targetArea[1][1])
    saveDC.SelectObject(saveBitmap)
    saveDC.BitBlt((0, 0), targetArea[1],
                  mfcDC, targetArea[0], win32con.SRCCOPY)
    saveBitmap.SaveBitmapFile(
        saveDC, ('./tmp/oneShot.jpg' if isDistance==0 else ('./tmp/anotherShot.jpg' if isDistance==1 else './tmp/anoanotherShot.jpg')))
    pass


def imagePreProcess(img, isDistance):
    """
    # seperate one image into several pieces containing single number

    retval -> [list]
        # single number list
    """
    imgWidth, imgHeight = img.shape[1], img.shape[0]
    imgGray = np.zeros((imgHeight, imgWidth), np.uint8)
    # -- to get foreground
    if isDistance==0:
        aimR,aimG,aimB,aimSqrt = 0,194,0,75
        rect = (3, 3, 80, 30)
        aimWidth,aimHeight = 15,6
    elif isDistance==1:
        aimR,aimG,aimB,aimSqrt = 97,189,204,95
        rect = (5, 5, 48, 26)
        aimWidth,aimHeight = 15,8
    elif isDistance==2:
        aimR,aimG,aimB,aimSqrt = 240,191,39,80
        rect = (5, 2, 70, 23)
        aimWidth,aimHeight = 25,8
    mask = np.zeros(img.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5,
                cv2.GC_INIT_WITH_RECT)  # 函数返回值为mask,bgdModel,fgdModel
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')  # 0和2做背景
    img = img*mask2[:, :, np.newaxis]  # 使用蒙板来获取前景区域
    for i in range(imgHeight):
        for j in range(imgWidth):
            if math.sqrt(math.pow(img[i, j][0]-aimB, 2)+math.pow(img[i, j][1]-aimG, 2)+math.pow(img[i, j][2]-aimR, 2)) < aimSqrt:
                imgGray[i, j] = 255
    imgGray = imgGray.reshape(imgHeight, imgWidth, 1)
    # -- for testing
    # cv2.imshow('imgGray', cv2.resize(imgGray, (imgWidth*10, imgHeight*10)))
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    # -- seperate
    numbersList, oneNumber = [], []
    flagNumHere = False
    for i in range(imgWidth):
        posTop, posBottom = 0, imgHeight-1
        for j in range(imgHeight):
            if not imgGray[j, i] == 0:
                posTop = j
                break
        for j in range(imgHeight-1, -1, -1):
            if not imgGray[j, i] == 0:
                posBottom = j
                break
        if posBottom-posTop < imgHeight-1:
            #
            if not flagNumHere:
                flagNumHere = True
                oneNumber.append(i-1)  # add start row
                oneNumber.append(posTop-3)  # add start collumn
                oneNumber.append(posBottom+3)  # add end collumn
            else:
                # try to update
                tmpTop, tmpBottom = posTop-3, posBottom+3
                oneNumber[1] = tmpTop if tmpTop < oneNumber[1] else oneNumber[1]
                oneNumber[2] = tmpBottom if tmpBottom > oneNumber[2] else oneNumber[2]
        else:
            #
            if flagNumHere:
                flagNumHere = False
                if (i-oneNumber[0] <= aimWidth) and (oneNumber[2]-oneNumber[1]-6 >= aimHeight):
                    oneNumber.append(i+1)
                    oneNumberList = [[0.0 for k in range(
                        oneNumber[2]-oneNumber[1]+1)] for l in range(oneNumber[2]-oneNumber[1]+1)]
                    for k in range(oneNumber[2]-oneNumber[1]+1):
                        tmpStart = math.floor(
                            (oneNumber[2]-oneNumber[1]-oneNumber[3]+oneNumber[0])/2)
                        tmpEnd = tmpStart+oneNumber[3]-oneNumber[0]
                        tmpIndex = 0
                        for l in range(tmpStart, tmpEnd):
                            oneNumberList[k][l] = imgGray[oneNumber[1] + k][oneNumber[0]+tmpIndex]
                            tmpIndex += 1
                    numbersList.append(oneNumberList)
                oneNumber = []
    # -- return
    return numbersList


def recognizeNumbers(theClassifier, imgs, cols, rows):
    """
    # to recognize numbers

    retval -> [list]
        # severval results 
    """
    res = []
    for img in imgs:
        try:
            res.append(np.argmax(theClassifier.predict(cv2.resize(np.array(img, dtype=np.float32).reshape(
                len(img), len(img), 1), (rows, cols)).reshape(1, cols, rows, 1)/255.0), axis=-1)[0])
        except e:
            print('Error: ', e)
            return -1
    return res


# keyboard and mouse event
# host key is 'T'
# quit key is 'Q'
# alt key is 'K'


# two global variables (alt key here is 'K')
flagKeyHostHasBeenPressedDown, flagKeyAltHasBeenPressedDown = False, False
strengthTableBasic = [[10, 19, 25, 30, 36, 40, 44, 48, 51, 54, 57, 60, 63, 66, 69, 72, 74, 76, 78, 80],  # 20 deg
                      [14, 20, 24.7, 28.7, 32.3, 35.7, 38.8, 41.8, 44.7, 47.5, 50.2,
                          52.8, 55.3, 57.9, 60.3, 62.7, 65.7, 67.5, 69.8, 72.1],  # 30 deg
                      [14.1, 20.1, 24.8, 28.8, 32.5, 35.9, 39, 42, 44.9, 48.3,
                          50.5, 53, 55.5, 58, 60.5, 63, 65.5, 68, 70, 72.5],  # 50 deg
                      [13, 21, 26, 32, 37, 41, 44, 49, 53, 56, 58, 61, 64, 67, 70, 73, 76, 79, 82, 85]]  # 65 deg
strengthTableEL = [[16, 20, 30, 37, 42, 48, 53, 57, 61, 65, 69, 73, 77, 79, 83, 86, 89, 92, 95, 97],  # 45 deg of EL
                   [17, 30, 37, 45, 52, 59, 65, 69, 74, 77, 84,
                    89, 93, 97, 100, 100, 100, 100, 100, 100]]  # 65 deg of EL
theClassifier = None  # anoanother global variable
weaponType = 0  # default is 'ELing'
targetDegree = 65 
windDir = 1 # 1 and -1


def adjustDegree(nowDegree,aimDegree,windForce,windDirection):
    rounds = aimDegree-nowDegree+round(windDirection*windForce*(2 if (aimDegree==65 or aimDegree==50) else 1))
    while rounds:
        if rounds>0:
            # up
            win32api.keybd_event(38, 0, 0, 0)
            time.sleep(0.05) # to pretend to be a human
            win32api.keybd_event(38, 0, win32con.KEYEVENTF_KEYUP, 0)
            rounds -= 1
        else:
            # down
            win32api.keybd_event(40, 0, 0, 0)
            time.sleep(0.05) # to pretend to be a human
            win32api.keybd_event(40, 0, win32con.KEYEVENTF_KEYUP, 0)
            rounds += 1
    pass

def pressToFire(aimStrength):
    win32api.keybd_event(32, 0, 0, 0)
    time.sleep(round(aimStrength/100*4.1,2))
    win32api.keybd_event(32, 0, win32con.KEYEVENTF_KEYUP, 0)
    pass


def onKeyDown(ev):
    global flagKeyHostHasBeenPressedDown, flagKeyAltHasBeenPressedDown, weaponType,targetDegree,windDir
    if ev.Key == 'Q' or ev.Key == 'q':
        os._exit(0)  # sys.exit doesn't work
    elif ev.Key == 'T' or ev.Key == 't':
        flagKeyHostHasBeenPressedDown = True
    elif ev.Key == 'K' or ev.Key == 'k':
        print('Altering ..')
        flagKeyAltHasBeenPressedDown = True
    else:
        if flagKeyAltHasBeenPressedDown:
            if ev.Key == '7' or ev.Key=='Numpad7':
                weaponType = 0
                print('Weapon used now is: {}.'.format('ELing'))
            elif ev.Key == '8' or ev.Key=='Numpad8':
                weaponType = 1
                print('Weapon used now is: {}.'.format('CanCrawl'))
            elif ev.Key == '9' or ev.Key=='Numpad9':
                weaponType = 2
                print('Weapon used now is: {}.'.format('Others'))
            elif ev.Key == '4' or ev.Key=='Numpad4':
                targetDegree = 45
                print('Target-degree now is: {}.'.format('45deg'))
            elif ev.Key == '5' or ev.Key=='Numpad5':
                targetDegree = 50
                print('Target-degree now is: {}.'.format('50deg'))
            elif ev.Key == '6' or ev.Key=='Numpad6':
                targetDegree = 65
                print('Target-degree now is: {}.'.format('65deg'))
            elif ev.Key == '3' or ev.Key=='Numpad3':
                targetDegree = 30
                print('Target-degree now is: {}.'.format('30deg'))
            elif ev.Key == '2' or ev.Key=='Numpad2':
                targetDegree = 20
                print('Target-degree now is: {}.'.format('20deg'))
            elif ev.Key == '1' or ev.Key=='Numpad1':
                windDir = 1
                print('Wind direction now is: {}.'.format('+'))
            elif ev.Key == '0' or ev.Key=='Numpad0':
                windDir = -1
                print('Wind direction now is: {}.'.format('-'))
            flagKeyAltHasBeenPressedDown = False
            flagKeyHostHasBeenPressedDown = False
    return True


def onMouseDown(ev):
    global flagKeyHostHasBeenPressedDown
    if flagKeyHostHasBeenPressedDown:
        # -- which strength table
        strengthTable = strengthTableEL if weaponType == 0 else strengthTableBasic
        # -- try to get distance
        windowCapture([(ev.Position[0]-86, ev.Position[1]-36),
                       (86, 36)])
        print('Distance Captured.')
        # -- try to get degree
        windowCapture([(392, 1020),
                       (58, 36)], 1)
        print('Degree Captured.')
        # -- try to wind force
        windowCapture([(920, 28),
                       (75, 27)], 2)
        print('Wind force Captured.')
        # -- do prediction
        # degree
        resDeg = recognizeNumbers(theClassifier, imagePreProcess(
            cv2.imread('./tmp/anotherShot.jpg'),1), 16, 16)
        print('recognized..(degree is {})'.format(resDeg))
        if not resDeg == -1 and len(resDeg) == 2:
            # guess degree
            theDegree = resDeg[0]*10+resDeg[1]*1
        else:
            print('Cannot recognize the degree.')
            return True
        # wind force
        resWind = recognizeNumbers(theClassifier, imagePreProcess(
            cv2.imread('./tmp/anoanotherShot.jpg'),2), 16, 16)
        print('recognized..(Wind force is {})'.format(resWind))
        if not resWind == -1 and len(resWind) == 2:
            # guess degree
            theWindForce = resWind[0]*1+resWind[1]*0.1
        else:
            print('Bad wind :(')
            return True
        # distance
        resDis = recognizeNumbers(theClassifier, imagePreProcess(
            cv2.imread('./tmp/oneShot.jpg'),0), 16, 16)
        print('recognized..(distance is {})'.format(resDis))
        if not resDis == -1 and len(resDis) >= 2:
            # guess distance
            strength = 0
            if len(resDis) >= 3:
                aimIndex, indexAfterDot = (
                    resDis[0]*10+resDis[1]*1 - 2) if weaponType == 1 else (resDis[0]*10+resDis[1]*1-1), 2
            else:
                aimIndex, indexAfterDot = (
                    resDis[0]-2) if weaponType == 1 else (resDis[0]-1), 1
            if weaponType==0:
                if targetDegree==45:
                    degreeIndex = 0
                elif targetDegree==65:
                    degreeIndex = 1
                else:
                    print('Strange Degree :(')
                    return True
            else:
                if targetDegree==20:
                    degreeIndex = 0
                elif targetDegree==30:
                    degreeIndex = 1
                elif targetDegree==50:
                    degreeIndex = 2
                elif targetDegree==65:
                    degreeIndex = 3
                else:
                    print('Strange Degree :(')
                    return True
            strength += strengthTable[degreeIndex][aimIndex]
            strength += 0.1*resDis[indexAfterDot]*(strengthTable[degreeIndex][aimIndex+1]-strengthTable[degreeIndex][aimIndex])
            # then fight against ur sucked life
            # that's to say press space btn for a while
            # timeNeedToPress = round(strength/100*4.1, 3)
            # win32api.keybd_event(32, 0, 0, 0)
            # time.sleep(timeNeedToPress)
            # win32api.keybd_event(32, 0, win32con.KEYEVENTF_KEYUP, 0)
            adjustDegree(theDegree,targetDegree,theWindForce if (not weaponType==0) else 0,windDir)
            pressToFire(strength)
        flagKeyHostHasBeenPressedDown = False
    return True


def run(cols, rows, epochs, WithCNN):
    """
    ## weapon type:
    > 0: ELing
    > 1: Spider
    > 2: others
    """
    global theClassifier
    train(cols, rows, epochs, WithCNN)
    theClassifier = kr.models.load_model(
        './models/trainedWith{}{}X{}.h5'.format('CNN'if WithCNN else'BPNN', cols, rows))
    hkmng = ph.HookManager()
    # keyboard
    hkmng.KeyDown = onKeyDown
    # hkmng.KeyUp = onKeyUp
    hkmng.HookKeyboard()
    # mouse
    hkmng.MouseLeftDown = onMouseDown
    hkmng.HookMouse()
    # start to listening
    print('I\'m watching on you!')
    pc.PumpMessages()
    pass


if __name__ == '__main__':
    # trainWithCNN(16,16,5)
    # print(recognizeNumbers(kr.models.load_model('./models/trainedWithBPNN16X16.h5'),
    #                  imagePreProcess(cv2.imread('./tmp/anoanotherShot.jpg'), 2), 16, 16))
    run(16, 16, 5, False)
    pass
