import cv2 as cv
import copy
from tqdm import tqdm

import function as f
import number2 as n2
import elipse
import number3 as n3
import intersection


def find_point(filename, one_mm, line_cut):
    # filename = './start-bin.bmp'
    img = cv.imread(filename, cv.IMREAD_COLOR)

    h, w, _ = img.shape  # Получаем высоту и ширину изображения

    # img = f.anti_nois(img)

    img_th = f.morf(img)  # Проводим морфологию (эрозия + скелетолизация + расширение)

    cv.imshow('img', img)
    cv.imshow('img_morf', img_th)
    cv.waitKey()
    cv.destroyAllWindows()

    # img_th = f.dilation_3(img_th)

    proverka = False  # Условие для добавление точки
    img1 = img.copy()  # Создаем копию изоб. для рисования

    # ШАГ ПЕРВЫЙ
    print('step1')
    red_point = []  # Будем заносить точки хвоста
    for i in tqdm(range(h)):  # Движемся по оси У
        for j in range(w):  # Движемся по оси Х

            proverka = False  # Обнуление условия
            if all(img_th[i, j] > [180, 180, 180]):  # Если пиксель белый
                proverka = f.method_circl(img_th, j, i, 12, 3,
                                          4)  # 30 - радиус, 5 - шаг дуги, 4 - прыжок  #1d  10-r 2-s 4-j

            if proverka:
                point = [i, j]
                red_point.append(point)

    img2 = img.copy()  # Создаем копию для изоб. 1

    # Получаем черное изображение
    img2 = cv.bitwise_not(img)
    img2 = cv.bitwise_and(img, img2)

    # По точкам из шага один наносим точки белым цветом
    for p in red_point:
        i = p[0]
        j = p[1]
        img2[i, j] = [255, 255, 255]

    cv.imshow('img2_posle1', img2)
    cv.waitKey()
    cv.destroyAllWindows()

    # ШАГ ВТОРОЙ (ИДЕНТИЧЕН ПЕРВОМУ)
    print('step2')
    img_elips = n2.number2(img2, red_point)

    # ШАГ ТРЕТИЙ, ОПРЕДЕЛЯЕМ ВЕРШИНЫ СОТ
    print('step3')
    points = elipse.elipse(img_elips)

    img3 = img.copy()  # Создаем копию исходника для четвертого шага

    # ШАГ ЧЕТВЕРТЫЙ, СОЕДИНЯЕМ ВЕРШИНЫ КОТОРЫЕ ПОЛУЧИЛИ -> ПОЛУЧАЕМ ГРАНИ
    print('step4')
    line_edge, img3 = n3.number3(img3, points)

    # TODO здесь формируем линию реза, она должна передаваться из вне или загружена из файла, это тестовый пример
    '''
    ls1 = [0, 50, 50, 50]
    ls2 = [50, 50, 70, 90]
    ls3 = [70, 90, 110, 80]
    ls4 = [110, 80, 160, 110]
    ls5 = [160, 110, w, h]
    
    cv.line(img3, (ls2[0], ls2[1]), (ls2[2], ls2[3]), (0, 255, 255), 3)
    cv.line(img3, (ls3[0], ls3[1]), (ls3[2], ls3[3]), (0, 255, 255), 3)
    cv.line(img3, (ls4[0], ls4[1]), (ls4[2], ls4[3]), (0, 255, 255), 3)
    cv.line(img3, (ls5[0], ls5[1]), (ls5[2], ls5[3]), (0, 255, 255), 3)
    '''
    for seg in line_cut:
        cv.line(img3, (seg[0], seg[1]), (seg[2], seg[3]), (0, 255, 255), 3)

    # line_cut = [ls1, ls2, ls3, ls4, ls5]  # Формируем кусочную линию реза

    points = []  # Массив точек пересечения граней и линии реза
    edge_for_cut = []  # Массив граней подверженных резу

    # Проверяем линию реза на пересечение с гранями
    for i in line_cut:

        if i[0] >= i[2]:
            max_x_i = i[0]
            min_x_i = i[2]
        else:
            max_x_i = i[2]
            min_x_i = i[0]

        for j in line_edge:

            point = intersection.intersection(img, i, j)  # Получаем точку пересечения

            # print('point = ', point)

            # Если точки нет продолжаем
            if point == None or len(point) == 0:
                continue

            # TODO здесь происходит добавление точки пересечения и грани
            # TODO необходимо пересмотреть условия, т.к алгоритм работает не для любой траектории, условия добавлены нужно продолжить тестирование
            if True:  # i[0] != i[2]:   #Если Х не равны

                if j[0] >= j[2]:
                    max_x = j[0]
                    min_x = j[2]
                else:
                    max_x = j[2]
                    min_x = j[0]

                if j[1] >= j[3]:
                    max_y = j[1]
                    min_y = j[3]
                else:
                    max_y = j[3]
                    min_y = j[1]

                if point[0] >= min_x and point[0] <= max_x and point[1] >= min_y and point[1] <= max_y and \
                        point[0] >= min_x_i and point[0] <= max_x_i:
                    points.append(point)
                    edge_for_cut.append(j)

    edge_cut = copy.deepcopy(edge_for_cut)  # Создаем копию массива граней которые будут резатся

    # Избавляемся от задублированных граней
    for i in edge_for_cut:
        count = 0
        for j in edge_cut:
            if i[0] == j[2] and i[1] == j[3]:
                edge_cut.pop(count)
                edge_for_cut.pop(count)
            count += 1

    img4 = img.copy()

    # ШАГ ПЯТЫЙ, ВЫЧЕСЛЯЕМ ТОЧКУ РЕЗА И ОПРЕДЕЛЯЕМ УГОЛ ДЛЯ ПОЗИЦИОНИРОВАНИЯ НОЖА
    print('step5')
    # TODO требуется добавить в функцию knife возврат угла а не координат
    points = []  # список точек реза
    alfa_cut = []
    for edge in edge_cut:
        p = intersection.two_del_five(edge)
        points.append(p)
        # cv.circle(img3, (int(p[0]), int(p[1])), 2, (90, 0, 40), 3)

        knife = intersection.knife(img3, edge, p[0], p[1])
        alfa_cut.append(knife[4])
        cv.line(img3, (int(knife[0]), int(knife[1])), (int(knife[2]), int(knife[3])), (255, 0, 0), 3)

    print('#список точек реза')
    print(points[:20])
    print('#список угла реза')
    print(alfa_cut[:20])

    # Выделяем цветом грани подверженные резу
    for edge in edge_cut:
        cv.line(img3, (edge[0], edge[1]), (edge[2], edge[3]), (0, 255, 100), 2)

    print('one_mm =', one_mm)
    koor = f.translation_koordinate(img, one_mm, points)
    print('Координаты реза в миллиметрах')

    print('колличество точек = ', len(koor))
    print('колличество углов = ', len(alfa_cut))

    count = 0
    for k in koor:
        count += 1
        print(count, '. ', k)

    # ТЕСТИРОВАНИЕ КАЛИБРОВКИ С НАЛОЖЕНИЕМ ТЕКСТА
    img4 = img.copy()
    img_orig = img4.copy()  # cv.imread('./scrin.bmp', cv.IMREAD_COLOR)
    i = 0
    for p in points:
        cv.circle(img4, (int(p[0]), int(p[1])), 2, (0, 200, 0), 3)
        cv.circle(img_orig, (int(p[0]), int(p[1])), 2, (0, 0, 200), 3)
        # text = str(p[0]) + ';' + str(p[1])
        # cv.putText(img4, text,(int(p[0]), int(p[1]) - 10), cv.FONT_HERSHEY_SIMPLEX, 1,(255.,0,255), 1 )

        text1 = str(round(koor[i][0], 2)) + ';' + str(round(koor[i][1], 2))
        cv.putText(img4, text1, (int(p[0]), int(p[1]) - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv.putText(img_orig, text1, (int(p[0]), int(p[1]) - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        i += 1

    cv.imshow('img3', img3)
    cv.imshow('img4', img4)
    cv.imshow('img_orig', img_orig)
    cv.imwrite('./pictures/koordin_points.jpg', img4)
    cv.imwrite('./pictures/knife.jpg', img3)
    cv.imwrite('./pictures/img_orig_points.jpg', img_orig)
    cv.waitKey(0)
    cv.destroyAllWindows()

    return koor, alfa_cut

# find_point('./foto_cam/start-bin.bmp',13.65)
