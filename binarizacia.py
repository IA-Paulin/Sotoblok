import cv2 as cv
import numpy as np


def binariz(file_name):
    img = cv.imread(file_name, cv.IMREAD_GRAYSCALE)
    ret, th = cv.threshold(img, 128, 255, cv.THRESH_BINARY)  # 170

    # ret, th = cv.threshold(img, 130, 255, cv.THRESH_BINARY_INV)

    h, w = img.shape

    print(h, w)

    '''Высчитываем среднию яркость изображения'''
    # *********************************************************
    mas_brigh = []
    for i in range(h):
        for j in range(w):
            brightness = img[i, j]
            mas_brigh.append(brightness)

    arr_mas = np.asarray(mas_brigh)
    print(arr_mas)

    arr_sum = np.sum(arr_mas, axis=0)

    print('brightness = ', arr_sum)

    threshold = arr_sum / (h * w)

    print(threshold)
    # *********************************************************


    cv.imshow('img', img)
    cv.imshow('th', th)
    cv.waitKey()
    cv.destroyAllWindows()
    s = './foto_cam/start-bin.bmp'

    if arr_sum > 300000000:
        return -1

    cv.imwrite(s, th)
    return s


#binariz('./exsp/test74.bmp')
