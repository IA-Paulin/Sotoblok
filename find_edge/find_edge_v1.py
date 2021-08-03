import cv2 as cv
import numpy as np

import function as f



def find_conturs_cotoblok(file_name, sota, one_mm):

    ''' Данная функция на вход получает путь к изображению и параметр сота ( отвечает за поиск правой ( смотрим на сотоблок) точки на контуре сотоблока
    при сканировании, линейно),
    открывает данное изображение, затем проводит бинаризацию и морфологию,
    находит основные точки на контурах, формируем 2 массива, точки правого и левого контура,
    производим соединение этих точек'''

    #Предварительная подготовка данных
    #file_name = './edge_sotoblok.png'
    #file_name =  './sot1.png'

    img_gr = cv.imread(file_name, cv.IMREAD_GRAYSCALE)
    img_or = cv.imread(file_name, cv.IMREAD_COLOR)

    t, th = cv.threshold(img_gr, 180, 255, cv.THRESH_BINARY)

    cv.imshow('img', th)
    cv.imshow('img_o', img_or)
    cv.imshow('img_g', img_gr)

    cv.waitKey()
    cv.destroyAllWindows()

    #Морфология
    kernel = np.ones((5, 5), np.uint8)  # 5x5
    dilation = cv.dilate(th, kernel, iterations=1)

    kernel = np.ones((3, 3), np.uint8)
    eros = cv.erode(dilation, kernel, iterations=2)

    h, w, _ = img_or.shape

    #список 2-х контуров
    point_contur_l = []
    point_contur_r = []

    img = img_or.copy() #копируем изображение для последующей визуализации

    #Основной алгоритм
    for i in range(0, h, 10):
        #Данные которые обнуляются при каждом проходе ( по линии)
        one_entry = False # фиксирует обнаружение левой точки
        black_pix = 0     # считает количество черных пикселей на проходе
        point_end = []    # найденная точка ( правая)

        for j in range(w):
            color = th[i, j]
            point = []  # найденная точка ( правая)

            #обнаружение белых точек и проверка на повторение черных пикселей
            if color > 170 and black_pix < sota:

                #добавление точки
                y = i
                x = j
                point.append(x)
                point.append(y)

                if black_pix == 0:
                    one_entry = True

                    point = tuple(point)

                    point_contur_l.append(point)

                black_pix = 0

            if one_entry:
                black_pix += 1

            if black_pix > sota or black_pix +j == w:

                point_end.append(x)
                point_end.append(y)
                porog = point_end[0] - point_contur_l[-1][0] # если разница по икс не большая (porog) то не берем ти точки

                if porog > 20:

                    point_end = tuple(point_end)

                    point_contur_r.append(point_end)
                else:
                    del point_contur_l[-1]
                break

    # Отрисовка точек ********************************************


    for p in point_contur_l:
        print(p)
        cv.circle(img_or, p, 2, (0, 0, 255), 2)

    print('*************************************')
    for p in point_contur_r:
        print(p)
        cv.circle(img_or, p, 2, (0, 255, 0), 2)



    # Отрисовка линий ********************************************
    for i in range(1, len(point_contur_l)):
        cv.line(img, point_contur_l[i - 1], point_contur_l[i], (0, 0, 255), 2)

    for i in range(1, len(point_contur_r)):
        cv.line(img, point_contur_r[i - 1], point_contur_r[i], (0, 0, 255), 2)

    cv.line(img, point_contur_l[0], point_contur_r[0], (0, 0, 255), 2)
    cv.line(img, point_contur_l[-1], point_contur_r[-1], (0, 0, 255), 2)




    #ПЕРЕВОД КООРДИНАТ В МИЛЛИМЕТРЫ
    print('one_mm =', one_mm)
    koor_r = f.translation_koordinate(img, one_mm, point_contur_r)
    print('Координаты (правые) реза в миллиметрах')
    count = 0
    for k in koor_r:
        count += 1
        print(count, '. ', k)

    koor_l = f.translation_koordinate(img, one_mm, point_contur_l)
    print('Координаты (левые) реза в миллиметрах')
    count = 0
    for k in koor_l:
        count += 1
        print(count, '. ', k)



    img4 = img.copy()
    img_orig = img_or.copy()
    i = 0
    for p in point_contur_r:
        cv.circle(img4, (int(p[0]), int(p[1])), 2, (0, 200, 0), 3)
        cv.circle(img_orig, (int(p[0]), int(p[1])), 2, (0, 0, 200), 3)
        # text = str(p[0]) + ';' + str(p[1])
        # cv.putText(img4, text,(int(p[0]), int(p[1]) - 10), cv.FONT_HERSHEY_SIMPLEX, 1,(255.,0,255), 1 )

        text1 = str(round(koor_r[i][0], 2)) + ';' + str(round(koor_r[i][1], 2))
        cv.putText(img4, text1, (int(p[0]), int(p[1]) - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv.putText(img_orig, text1, (int(p[0]), int(p[1]) - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        i += 1

    i = 0
    for p in point_contur_l:
        cv.circle(img4, (int(p[0]), int(p[1])), 2, (0, 200, 0), 3)
        cv.circle(img_orig, (int(p[0]), int(p[1])), 2, (0, 0, 200), 3)
        # text = str(p[0]) + ';' + str(p[1])
        # cv.putText(img4, text,(int(p[0]), int(p[1]) - 10), cv.FONT_HERSHEY_SIMPLEX, 1,(255.,0,255), 1 )

        text1 = str(round(koor_l[i][0], 2)) + ';' + str(round(koor_l[i][1], 2))
        cv.putText(img4, text1, (int(p[0]), int(p[1]) - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv.putText(img_orig, text1, (int(p[0]), int(p[1]) - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        i += 1

    '''
    cv.imshow('img_or', img_or)
    cv.imshow('img1', eros)
    cv.imshow('img', img)
    cv.imshow('img4', img4)
    cv.imshow('img_orig', img_orig)
    cv.waitKey()
    cv.destroyAllWindows()
    '''

    cv.imwrite('./fe_v1/result_edge.png', img)
    cv.imwrite('./fe_v1/result_point.png', img_or)
    cv.imwrite('./fe_v1/result_bin.png', eros)

    cv.imwrite('./fe_v1/img4.png', img4)
    cv.imwrite('./fe_v1/img_orig.png', img_orig)

    return koor_r, koor_l




file_name = './sot6.png'
sota = 100
one_mm = 13.65
find_conturs_cotoblok(file_name, sota,one_mm)
