import cv2 as cv
import numpy as np
import copy

import function as f
import os


def matrix_koord(a, b, img, st, end):
    ''' получаем координаты матрицы a - текущая координата у изображения
     b - текущая координата по х
     img - изображенте для получения ширины и высоты
      st, end  - начало и конец координат матрицы '''
    X = []
    Y = []

    h, w = img.shape

    end_count_x = end
    end_count_y = end

    for k in range(st, end + 1):

        y = a + k
        x = b + k

        # проверка на границы изображения, для правельного определения контура
        if x + end >= w - 1:
            x = w - end_count_x
            end_count_x -= 1
            if end_count_x == 0:
                break

        if y + end >= h - 1:
            y = h - end_count_y
            end_count_y -= 1
            if end_count_y == 0:
                break

        X.append(x)
        Y.append(y)
    # формируем массив координат матрицы
    mat_koor = []
    for y in Y:

        for x in X:
            koor = [0, 0]

            koor[0] = y
            koor[1] = x

            mat_koor.append(koor)

    return mat_koor


# m = matrix_koord(2,2)
# print(m)
# print(len(m))


def find_conturs_cotoblok(file_name, start, step,
                          one_mm):  # start - определяет размер сканируемой матрицы: step - шаг движения матрицы по изображению
    # Предварительная подготовка данных
    # file_name = './edge_sotoblok.png'
    # file_name =  './sot1.png'

    img_gr = cv.imread(file_name, cv.IMREAD_GRAYSCALE)
    img_or = cv.imread(file_name, cv.IMREAD_COLOR)

    t, th = cv.threshold(img_gr, 100, 255, cv.THRESH_BINARY)

    img = th.copy()
    img_p = img_or.copy()
    img_cont = img_or.copy()
    img_koor = img_or.copy()
    or_kor = img.copy()

    h, w, _ = img_or.shape

    koor_edge_sotobloka = []

    # сканируем все изображение
    for i in range(start, h, step):
        for j in range(start, w, step):

            point = []

            mat_koor = matrix_koord(i, j, img_gr, -start, start)

            matrix = []
            for m in mat_koor:
                z = th[m[0], m[1]]
                matrix.append(z)

            arr = np.array(matrix)

            mean_arr = np.mean(arr, axis=0)
            # print('mean = ', mean_arr)

            # проверка на пороговое значение матрицы
            if mean_arr > 18:
                point.append(j)
                point.append(i)
                point = tuple(point)
                koor_edge_sotobloka.append(point)

                for m in mat_koor:
                    img[m[0], m[1]] = 255

    # найденные точки помечаем красным кругом
    for p in koor_edge_sotobloka:
        cv.circle(img_p, p, 2, (0, 0, 255), 2)

    # находим все контуры на изображении
    cnt, h = cv.findContours(img.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    if cnt:
        cv.drawContours(img_or, cnt, -1, (0, 255, 0), 2)
    else:
        return -1


    big_cont = []
    long_cont = 0

    # поиск наибольшего контура

    print('contur = ', cnt)

    for c in cnt:
        max = len(c)
        if max > long_cont:
            long_cont = max
            big_cont = copy.copy(c)

    cv.drawContours(img_or, big_cont, -1, (0, 255, 0), 2)  # рисуем наибольший контур
    big_cont = big_cont.reshape((len(big_cont), 2))  # меняем форму для получения точек координат

    # рисуем ломаную по точкам
    for i in range(1, len(big_cont)):
        cv.line(img_cont, (big_cont[i - 1][0], big_cont[i - 1][1]), (big_cont[i][0], big_cont[i][1]), (0, 0, 255), 1)

        # cv.circle(img_cont, (big_cont[i][0], big_cont[i][1]), 2, (255,0,0), 2)

    # замыкаем контур
    cv.line(img_cont, (big_cont[-1][0], big_cont[-1][1]), (big_cont[0][0], big_cont[0][1]), (0, 0, 255), 1)

    # ПЕРЕВОД КООРДИНАТ В МИЛЛИМЕТРЫ
    print('one_mm =', one_mm)
    koor_r = f.translation_koordinate(img_koor, one_mm, big_cont)
    print('Координаты контура в миллиметрах')
    count = 0

    for k in koor_r:
        count += 1
        print(count, '. ', k)

    i = 0
    for p in big_cont:
        cv.circle(img_koor, (int(p[0]), int(p[1])), 2, (0, 200, 0), 3)
        # cv.circle(img_koor, (int(p[0]), int(p[1])), 2, (0, 0, 200), 3)
        # text = str(p[0]) + ';' + str(p[1])
        # cv.putText(img4, text,(int(p[0]), int(p[1]) - 10), cv.FONT_HERSHEY_SIMPLEX, 1,(255.,0,255), 1 )

        text1 = str(round(koor_r[i][0], 2)) + ';' + str(round(koor_r[i][1], 2))
        cv.putText(img_koor, text1, (int(p[0]), int(p[1]) - 10), cv.FONT_HERSHEY_SIMPLEX, 0.2, (0, 255, 255), 1)
        cv.putText(or_kor, text1, (int(p[0]), int(p[1]) - 10), cv.FONT_HERSHEY_SIMPLEX, 0.2, (0, 255, 255), 1)
        i += 1

    '''
    cv.imshow('img', img)
    cv.imshow('th', th)
    cv.imshow('img_gr', img_gr)
    cv.imshow('img_p', img_p)
    cv.imshow('img_or', img_or)
    cv.imshow('img_cont', img_cont)
    cv.imshow('img_koor', img_koor)
    cv.waitKey()
    cv.destroyAllWindows()
    '''
    cv.imwrite('./fe_v2/img-v2.png', img)
    cv.imwrite('./fe_v2/th-v2.png', th)
    # cv.imwrite('./img-gr-v2.png', img_gr)
    # cv.imwrite('./img_p-v2.png', img_p)
    cv.imwrite('./fe_v2/img_or-contur.png', img_or)
    cv.imwrite('./fe_v2/result_edge.png', img_cont)
    cv.imwrite('./fe_v2/img_koor.png', img_koor)

    return koor_r


#print(os.path.abspath('./'))
#file_name = '/dev/media/HDD/DATA/myWork/PythonProject/Sotoblok/release/calibrovka_small.jpg'
#file_name = '/dev/media/HDD/DATA/myWork/PythonProject/Sotoblok/release/contur_sotoblok.jpg'
#a =find_conturs_cotoblok(file_name, 3, 3, 13)
#print(a)