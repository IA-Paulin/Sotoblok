import cv2 as cv
import numpy as np
import os


def calibration(file_name):
    w_mm = 20

    # f = os.path.abspath('./calibration/calib.bmp')
    f = os.path.abspath(file_name)
    print(f)

    # fn = './calibration/calib.bmp'  # имя файла, который будем анализировать
    img = cv.imread(f)

    # cv.imshow('img', img)
    # cv.waitKey(0)

    hsv_min = np.array((0, 110, 0), np.uint8)
    hsv_max = np.array((255, 255, 255), np.uint8)
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)  # меняем цветовую модель с BGR на HSV
    thresh = cv.inRange(hsv, hsv_min, hsv_max)  # применяем цветовой фильтр

    # hsv_min = np.array((17, 25, 0), np.uint8)
    # hsv_max = np.array((255, 200, 226), np.uint8)
    # hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)  # меняем цветовую модель с BGR на HSV
    # thresh2 = cv.inRange(hsv, hsv_min, hsv_max)  # применяем цветовой фильтр

    # thresh = cv.bitwise_or(thresh, thresh2)

    cv.imshow('img', thresh)
    cv.waitKey(0)
    cv.destroyAllWindows()

    contours0, hierarchy = cv.findContours(thresh.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    square = []

    big_area = 0
    for cnt in contours0:
        rect = cv.minAreaRect(cnt)  # пытаемся вписать прямоугольник
        box = cv.boxPoints(rect)  # поиск четырех вершин прямоугольника
        box = np.int0(box)  # округление координат
        area = int(rect[1][0] * rect[1][1])

        if area > big_area:
            big_area = area
            big_rect = rect
            big_box = box

    area = big_area
    rect = big_rect
    box = big_box

    ls = []
    print('area = ', area)
    if area > 4000:
        # cv.drawContours(img, [box], 0, (255, 255, 0), 2)  # рисуем прямоугольник

        cv.drawContours(img, [box], 0, (0, 0, 255), 2)  # рисуем прямоугольник

        cv.imshow('img', img)
        cv.waitKey(0)
        cv.destroyAllWindows()

        a = rect[1]
        b = rect[2]

        ls.append(a)
        ls.append(b)
    else:
        return -3, 0

    if ls:
        square.append(ls)

    print("Calib = ", square)

    angle = square[0][1]
    if square:

        if -1 <= angle <= 1 or -91 <= angle <= -89 or 89 <= angle <= 91:
            cv.imwrite('./calibration/calib_' + '.png', img)
        else:
            print('Calibration: angle = ', angle)
            cv.imwrite('./calibration/defect/defect-calib_' + '.png', img)
            return -1, angle
    else:
        cv.imwrite('./calibration/calib_notFound_' + '.png', img)
        return -2, 0

    if square[0][0][0] >= square[0][0][1]:
        w_pix = round(square[0][0][1], 2)
    else:
        w_pix = round(square[0][0][0], 2)

    print('w_pix = ', w_pix)

    one_mm = (w_pix / w_mm )
    # cv.imwrite('defect-calib.bmp', img)

    return one_mm, angle


#print(calibration('kub4.jpg'))
