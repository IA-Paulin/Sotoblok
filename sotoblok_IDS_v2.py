from time import sleep
import cv2 as cv
import numpy as np
import threading
from pyueye import ueye
import struct
import os
import copy

import wake2
import sys

from find_edge import find_edge_v2 as fe

import find_points as fp
import binarizacia
import calibration

import function as f

# Глобальные переменные
addr = 0x20
frm = 0x20  # адрес от кого (адрес скрипта)
to = 0x01  # адрес кому ( адрес сервера)
line_cut_mass = []


# функция записывает данные в файл полученные при анализе контура
def writer_data(file_name, mas):
    file = open(file_name, 'w')
    for m in mas:
        for k in m:
            file.write(str(k) + ' ')
        file.write('\n')
    file.close()


def writer_data_alfa(file_name, mas):
    file = open(file_name, 'w')
    for k in mas:
        file.write(str(k) + ' ')
        file.write('\n')
    file.close()


def main():
    # init camera
    hcam = ueye.HIDS(0)
    ret = ueye.is_InitCamera(hcam, None)
    print(f"initCamera returns {ret}")

    # set color mode
    m_nColorMode = ueye.IS_CM_BGR8_PACKED
    ret = ueye.is_SetColorMode(hcam, ueye.IS_CM_BGR8_PACKED)
    print(f"SetColorMode IS_CM_BGR8_PACKED returns {ret}")

    # set region of interest
    width = 1280
    height = 1080
    rect_aoi = ueye.IS_RECT()
    rect_aoi.s32X = ueye.int(0)
    rect_aoi.s32Y = ueye.int(0)
    rect_aoi.s32Width = ueye.int(width)
    rect_aoi.s32Height = ueye.int(height)
    ueye.is_AOI(hcam, ueye.IS_AOI_IMAGE_SET_AOI, rect_aoi, ueye.sizeof(rect_aoi))
    print(f"AOI IS_AOI_IMAGE_SET_AOI returns {ret}")

    # allocate memory
    mem_ptr = ueye.c_mem_p()
    mem_id = ueye.int()
    bitspixel = 24  # for colormode = IS_CM_BGR8_PACKED
    ret = ueye.is_AllocImageMem(hcam, width, height, bitspixel,
                                mem_ptr, mem_id)
    print(f"AllocImageMem returns {ret}")

    # set active memory region
    ret = ueye.is_SetImageMem(hcam, mem_ptr, mem_id)
    print(f"SetImageMem returns {ret}")

    # continuous capture to memory
    ret = ueye.is_CaptureVideo(hcam, ueye.IS_DONT_WAIT)
    print(f"CaptureVideo returns {ret}")

    # get data from camera and display
    lineinc = width * int((bitspixel + 7) / 8)

    # setting fps ( для замедления камеры )
    fps = ueye.c_double()
    ueye.is_SetFrameRate(hcam, 3, fps)
    print('fps = ', fps)

    x = ueye.c_double(1)
    y = ueye.c_double(0)
    ueye.is_SetAutoParameter(hcam, ueye.IS_SET_ENABLE_AUTO_GAIN, x, y)

    print('*******************************************')
    print('width = ', width)
    print('height = ', height)
    print('bitspixel = ', bitspixel)
    print('lineinc = ', lineinc)
    print('m_nColorMode = ', m_nColorMode)

    om = 1
    om_big = 1
    points = []
    sota = 60

    print('СТАРТ ПРОГРАММЫ')

    while True:
        global line_cut
        img = ueye.get_data(mem_ptr, width, height, bitspixel, lineinc, copy=True)
        img = np.reshape(img, (height, width, 3))

        # img = cv.resize(img, (0, 0), fx=0.5, fy=0.5)

        img_sniper = img.copy()

        h, w, _ = img.shape

        cv.line(img_sniper, (0, int(h / 2)), (w, int(h / 2)), (0, 0, 255), 1)
        cv.line(img_sniper, (int(w / 2), 0), (int(w / 2), h), (0, 0, 255), 1)

        cv.imshow('IP Camera stream', img_sniper)
        cv.waitKey(1)

        # Производим калибровку для общего снимка (поиск точек контура)
        if e_cal_big.wait(timeout=0):
            print('Калибровка большого снимка')
            file_name = './calibrovka_big.jpg'
            cv.imwrite(file_name, img)

            om_big, al_big = calibration.calibration(file_name)  # проводим калибровку
            om_big = om_big * 1.04575  # вводим коэфициент для точности калибровки
            print('one_mm = ', om_big)
            print('angle = ', al_big)
            e_cal_big.clear()

            # Передаем количество пикселей в миллиметре и угол на сервер
            data = struct.pack('<ff', om_big, al_big)
            wake.tx(frm, to, 0x21, data)
            sleep(0.1)

        # Производим калибровку для снимка с приближением (поиск точек реза)
        if e_cal_small.wait(timeout=0):
            print('Калибровка малого снимка')
            file_name = './calibrovka_small.jpg'
            cv.imwrite(file_name, img)

            om, al = calibration.calibration(file_name)  # проводим калибровку
            om = om * 1.04575  # вводим коэфициент для точности калибровки
            print('one_mm = ', om)
            print('angle = ', al)
            e_cal_small.clear()

            # Передаем количество пикселей в миллиметре и угол на сервер
            data = struct.pack('<ff', om, al)
            wake.tx(frm, to, 0x22, data)
            sleep(0.1)

        # Производим определения контура заготовки сотоблока
        if e_fe.wait(timeout=0):
            print('Контур сотоблока')
            file_name = './contur_sotoblok.jpg'
            file_name = os.path.abspath(file_name)
            cv.imwrite(file_name, img)

            start = 10  # размер матрицы от центра т.е цент +start в право и ввер  и -start влево и вниц, при start =10 матрица 20х20
            step = 6  # шаг сканирования матрицы

            print('om_big =', om_big)
            print(file_name)
            # TODO не забудь удалить это введено для тестов
            om_big = 13
            # ****************************
            koor = fe.find_conturs_cotoblok(file_name, start, step, om_big)  # определяем контур сотоблока
            e_fe.clear()

            if koor == -1:
                data = 1
                wake.tx(frm, to, 0x23, data)
            else:
                writer_data('./log/koor.txt', koor)
                # Передаем  массив точек контура объекта
                for i in range(len(koor)):
                    data = struct.pack('<ff', koor[i][0], koor[i][1])
                    wake.tx(frm, to, 0x23, data)
                sleep(0.1)

        # Производим определения точек реза сотоблока
        if e_fp.wait(timeout=0):
            print('Поиск узлов')
            file_name = './start.jpg'
            cv.imwrite(file_name, img)

            s = binarizacia.binariz(file_name)  # проводим бинаризацию, возвращает путь обработанного файла

            if s == -1:  # необходимо проверять яркость изображения, если изображение засвечено, дальнейшая обработка не возможна
                print('Image brightness')
                e_fp.clear()
            else:
                print('om =', om)
                print('line_cut_mass in prer = ', line_cut_mass)
                points, alfa = fp.find_point(s, om, line_cut_mass)
                writer_data('./log/points_cut.txt', points)
                writer_data_alfa('./log/alfa.txt', alfa)
                e_fp.clear()

                # передаем координаты реза на сервер
                if len(points) == len(alfa):
                    for i in range(len(points)):
                        data = struct.pack('<fff', points[i][0], points[i][1], alfa[i])
                        wake.tx(frm, to, 0x24, data)
                else:
                    data = 1
                    wake.tx(frm, to, 0x24, data)

                sleep(0.1)

        # Завершаем работу камеры
        if e_exit.wait(timeout=0):
            data = struct.pack('<H', 0)
            wake.tx(frm, to, 0x26, data)

            print('Завершение работы камеры')
            break

    e_exit.clear()
    print('END PROGRAMM')
    cv.destroyAllWindows()

    # cleanup
    ret = ueye.is_StopLiveVideo(hcam, ueye.IS_FORCE_VIDEO_STOP)
    print(f"StopLiveVideo returns {ret}")
    ret = ueye.is_ExitCamera(hcam)
    print(f"ExitCamera returns {ret}")


def segment(data):
    global line_cut_mass

    print('line cut = ', data)
    number_koor = len(data)
    print(number_koor)
    print('<' + str(int(number_koor / 2)) + 'H')
    if (number_koor / 2) % 2 == 0:
        koor_line = struct.unpack('<' + str(int(number_koor / 2)) + 'H', data)
        print('koor_line = ', koor_line)
        line_cut = copy.copy(koor_line)
        print(line_cut)
        print(type(line_cut))
        line_cut = list(line_cut)
        print(type(line_cut))
        print(type(line_cut))

        ln = []
        count = 0
        line_cut_mass = []
        for i in line_cut:
            if count < 4:
                ln.append(i)
                count += 1
            else:
                line_cut_mass.append(ln)
                count = 1
                ln = []
                ln.append(i)
        line_cut_mass.append(ln)
        print('*******************************')
        print(line_cut)
        print(line_cut_mass)
    else:
        print('unpaired number of coordinates ')


def points(data):
    global line_cut_mass

    number_point = int((len(data)) / 2)
    print(number_point)

    if number_point % 2 == 0:
        point_name = [chr(i) for i in range(65, 65 + int((number_point / 2)))]
        print(point_name)

        ls = struct.unpack('<' + str(number_point) + 'H', data)
        print(ls)

        points_koor = []
        for i in range(int(number_point / 2)):
            point = ls[0:2]
            points_koor.append(point)
            ls = ls[2:]

        print('points_koor = ', points_koor)

        points_koor1 = points_koor[1:]
        points_koor = points_koor[:-1]

        print('points_koor1 = ', points_koor1)
        print('points_koor = ', points_koor)

        segmen_name = dict(zip(point_name, points_koor))
        print(segmen_name)

        for i, j in zip(points_koor, points_koor1):
            i = list(i)
            j = list(j)

            line_cut_mass.append(i + j)
        print(line_cut_mass)

    else:
        print('unpaired number of coordinates ')


def rx(frm, to, cmd, data):
    global wake

    print('rx')
    if to == 0 or to == addr:
        if cmd == 0x21:
            e_cal_big.set()  # Калибровка большого снимка
        elif cmd == 0x22:
            e_cal_small.set()  # Калибровка малого снимка
        elif cmd == 0x23:
            e_fe.set()  # поиск контура сотоблока
        elif cmd == 0x24:
            # segment(data)
            points(data)
            e_fp.set()  # поиск точек реза
        elif cmd == 0x25:
            e_power_cam.set()  # запуск камеры
        elif cmd == 0x26:
            e_exit.set()  # завершение работы камеры
        elif cmd == 0x27:
            e_end_script.set()  # завершение программы
            wake.stop()
        else:
            pass


e_fp = threading.Event()
e_cal_big = threading.Event()
e_cal_small = threading.Event()
e_fe = threading.Event()
e_exit = threading.Event()
e_power_cam = threading.Event()
e_end_script = threading.Event()

e = threading.Event()

l = len(sys.argv)
if l <= 1:
    wake = wake2.wake2(('localhost', 20000), rx)
else:
    wake = wake2.wake2((sys.argv[1], 20000), rx)

count_script = 0
while True:

    start = False

    if e_end_script.wait(timeout=0.1):
        print('End script')
        e_end_script.clear()
        data = struct.pack('<H', 0)
        wake.tx(frm, to, 0x27, data)
        break

    elif e_power_cam.wait(timeout=0.1):
        print('start initializetion cam')
        e_power_cam.clear()
        start = True

        if start:
            data = struct.pack('<H', 0)
            wake.tx(frm, to, 0x25, data)
            main()
        else:
            print('Camera not start, initialization failed')
            data = struct.pack('<H', 1)
            wake.tx(frm, to, 0x25, data)

    else:
        if count_script % 10 == 0:
            print('Camera off')
    count_script += 1
