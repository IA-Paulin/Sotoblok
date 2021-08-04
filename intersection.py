import math
import cv2 as cv


def intersection(img,lineA, lineB):

    root = True

    img_c = img.copy()

    x1 = lineA[0]
    x2 = lineA[2]
    y1 = lineA[1]
    y2 = lineA[3]

    x3 = lineB[0]
    x4 = lineB[2]
    y3 = lineB[1]
    y4 = lineB[3]

    a = x2 - x1
    b = y2 - y1
    c = y4 - y3
    d = x4 - x3

    AandB = a * d + b * c  # Скалярное произведение
    modAB = (a ** 2 + b ** 2) ** 0.5 * (d ** 2 + c ** 2) ** 0.5  # Произведение длин векторов

    cos = AandB / modAB # Тут происходит деление на 0!
    print('cos =', cos)
    print('a, b, d, c = ',a, b, d, c)

    #TODO необходимо в будущем обработать ситуацию когда грань и рез совпадают

    # Значение могут получаться больше 1 и -1
    if (cos > 1) or (cos < -1):
        cos = int(cos)
        print('cos int = ', cos)

    rad = math.acos(cos)



    print('rad = ',rad)
    degree = int(math.degrees(rad))
    print('degree = ',degree)

    point = []

    if degree == 0 or degree == 180:
        return None
    elif degree == 90:
        if lineA[0] == lineA[2]:
            x = lineA[0]
            y = lineB[1]
        else:
            x = lineB[0]
            y = lineA[1]

        # проверка на совпадение линии реза и грани с осями.
        if (x2 == x1) or (y3 == y4):
            if x == x2 and y == y3:
                pass
            else:
                root = False
        elif (y2 == y1) or (x3 == x4):
            if x == x3 and y == y2:
                pass
            else:
                root = False
        else:
            # по каноническому уравнению прямой расчитываем значение правой и левой части
            lx_1 = (x - x1) / (x2 - x1)
            ry_1 = (y - y1) / (y2 - y1)

            lx_2 = (x - x3) / (x4 - x3)
            ry_2 = (y - y3) / (y4 - y3)

            if lx_1 == ry_1 and lx_2 == ry_2:
                pass
            else:
                root = False





    else:
        try:
            y = (x1 * b * c - y1 * c * a + y3 * d * b - x3 * b * c) / ((b * d) - (c * a))

            if b == 0:
                x = ((y - y3) * d + x3 * c) / c
            else:
                x = ((y - y1) * a + x1 * b) / b



        except ZeroDivisionError:
            root = False
            print('корней нет')

    if root:
        point.append(x)
        point.append(y)

        '''
        if x3 == 1058 and x4 == 1009:
            print(point)
            cv.line(img_c, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv.line(img_c, (x3, y3), (x4, y4), (0, 255, 0), 2)
            cv.circle(img_c, (int(point[0]), int(point[1])), 2, (0, 0, 255), 2)
            cv.imshow('inter', img_c)
            cv.waitKey(0)
            cv.destroyAllWindows()
        '''
    return point


'''
l1 = [1,6,3,6]
l2 = [1,3,5,7]

a = intersection(l1,l2)

if a == None:
    print('рез и грань совпадают')
else:
    print('x = ', a[0], 'y = ', a[1])
'''


def two_del_five(edge):
    a = edge[2] - edge[0]
    b = edge[3] - edge[1]

    x = int((2 * a) / 5) + edge[0]
    y = int((2 * b) / 5) + edge[1]

    point = []
    point.append(x)
    point.append(y)

    return point


def knife(img, edge, x_cut, y_cut, R=20):

    img_c = img.copy()

    if edge[1] > edge[3]:
        y = edge[1]
        x = edge[0]
    else:
        y = edge[3]
        x = edge[2]

    horizont = [0, y, x, y]

    a = edge[2] - edge[0]
    b = edge[3] - edge[1]
    c = horizont[3] - horizont[1]
    d = horizont[2] - horizont[0]

    AandB = a * d + b * c  # Скалярное произведение
    modAB = (a ** 2 + b ** 2) ** 0.5 * (d ** 2 + c ** 2) ** 0.5  # Произведение длин векторов

    cos = AandB / modAB
    print(cos)
    print(a, b, d, c)

    rad = math.acos(cos)
    print(rad)
    degree = (math.degrees(rad)) * (1)
    print('градус = ', degree)


    if degree > 90:
        degree = 180 - degree




    print('градус после = ', degree)

    '''
    fi =0
    for i in range(5):
        fi = fi+70
        r = math.radians(fi)
        xm = R * math.cos(r) + x
        ym = R * math.sin(r) + y 

        cv.circle(img, (int(xm),int(ym)),3,(0,255,255),3)
        cv.imshow('inter',img)
        cv.waitKey(0)
        cv.destroyAllWindows()
    '''
    #alfa = 180 - degree #значение угла в системе координат изображения
    alfa = 90 - degree  # строим перпендикуляр
    print('alfa1 = ', alfa)

    #требуется для построения перпендикуляра, особенность векторного произ. и зеркальной системы координат.
    if ((a > 0) and (b > 0)) or ((a < 0) and (b < 0)):
        alfa = alfa * (-1)
        print('new alfa = ', alfa)

    rad = math.radians(alfa)
    x1 = R * math.cos(rad) + x_cut
    y1 = R * math.sin(rad) + y_cut

    if alfa >= 0:
        alfa = alfa - 180
    else:
        alfa = alfa + 180

    print('alfa2 = ', alfa)

    rad = math.radians(alfa)
    x2 = R * math.cos(rad) + x_cut
    y2 = R * math.sin(rad) + y_cut


    print('x1 = ', x1)
    print('y1 = ', y1)
    print('x2 = ', x2)
    print('y2 = ', y2)
    print('edge = ', edge)
    print('x_cut = ', x_cut)
    print('y_cut =', y_cut)


    knife = []
    knife.append(x1)
    knife.append(y1)
    knife.append(x2)
    knife.append(y2)
    knife.append(alfa)

    ''' 
    for i in range(0,400,10):
        rad = math.radians(i)
        x2 = R * math.cos(rad) + 100
        y2 = R * math.sin(rad) + 100
        cv.circle(img_c,(int(x2),int(y2)), 10, (0,255,0), 3)
        cv.imshow('knife', img_c)
        cv.waitKey(0)
        cv.destroyAllWindows()
    
    
    
    cv.line(img_c, (int(knife[0]), int(knife[1])), (int(knife[2]), int(knife[3])), (255, 0, 0), 3)
    cv.line(img_c, (int(horizont[0]), int(horizont[1])), (int(horizont[2]), int(horizont[3])), (255, 255, 0), 3 )    
    

    
    cv.imshow('knife', img_c)
    cv.waitKey(0)
    cv.destroyAllWindows()
    '''


    return knife
