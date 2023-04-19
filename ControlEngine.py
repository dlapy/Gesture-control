import cv2
import mediapipe as mp
import pyautogui as pag
import eel
from threading import Thread
from gests import handle_gesture
from cam import devices
import sys
from PyQt5 import sip
from PyQt5.QtCore import QUrl
from PyQt5 import QtGui
from PyQt5.QtWidgets import (QApplication, QMainWindow)
from PyQt5.QtWebEngineWidgets import *
import time

mpHands = mp.solutions.hands
mpDraw = mp.solutions.drawing_utils

# cap.release()
# cv2.destroyAllWindows()

cap = cv2.VideoCapture(devices[0])

step = 2

x = 0
y = 0

finger_connected = False


def process_hand_landmarks(hand_landmarks, prev_x, prev_y):
    global finger_connected

    # Получение ширины и высоты изображения
    h, w, c = img.shape

    # Определение координат пальцев
    thumb = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_TIP]  # большой палец
    indexFinger = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]  # указательный палец
    middleFinger = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_TIP]  # средний палец
    wrist = hand_landmarks.landmark[mpHands.HandLandmark.WRIST]  # запясье

    # Определение расстояния между кончиками пальцев для различных жестов
    distance_go = ((indexFinger.x - middleFinger.x) ** 2 + (indexFinger.y - middleFinger.y) ** 2) ** 0.5
    distance_left_click = ((thumb.x - indexFinger.x) ** 2 + (thumb.y - indexFinger.y) ** 2) ** 0.5
    distance_right_click = ((thumb.x - wrist.x) ** 2 + (thumb.y - wrist.y) ** 2) ** 0.5

    # Проверка, находятся ли кончики пальцев(большой и указательный) достаточно близко друг к другу

    if distance_go < 0.03:  # Значение 0.03 определено экспериментально
        # Определение координат для перемещения курсора мыши
        x, y = int(indexFinger.x * w), int(indexFinger.y * h)

        if prev_x != 0 and prev_y != 0:
            dx = x - prev_x
            dy = y - prev_y
        else:
            dx = dy = 0

        # Перемещение курсора мыши, если пальцы только что соединились
        if not finger_connected:
            try:
                pag.moveRel(dx * step, dy * step)
            except pag.FailSafeException:
                dx = dy = 0
                pass

        # Установка флага соединения пальцев
        finger_connected = True

        return x, y

    elif distance_left_click < 0.03:  # Значение 0.03 определено экспериментально
        finger_connected = True
        ges = "OK"
        handle_gesture(ges, finger_connected)  # Обработка жеста "OK"
        return prev_x, prev_y

    elif distance_right_click < 0.1:
        finger_connected = True
        ges = "RC"
        handle_gesture(ges, finger_connected)  # Обработка жеста "RC" (RIGHT CLICK)
        return prev_x, prev_y

    else:
        finger_connected = False
        return prev_x, prev_y


def present(hand_landmarks, g):
    if g == 10:

        if hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].x < hand_landmarks.landmark[
            mpHands.HandLandmark.WRIST].x:
            # движение влево
            pag.press('left')
            # time.sleep(1)
        elif hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].x > hand_landmarks.landmark[
            mpHands.HandLandmark.WRIST].x:
            # движение вправо
            pag.press('right')
            # time.sleep(1)

        return True
    elif g > 10:
        return True
    else:
        return False

active_auto = False
active_present = False
# функция вызова автономного режима
@eel.expose
def auto_lock():
    global active_auto,active_present
    if active_auto == False:
        if active_present == True:
            active_present = False
        active_auto = True
        thread2 = Thread(target=move_cursor_with_gestures)
        thread2.start()
    else:
        active_auto = False
# функция вызова режима презентации
@eel.expose
def present_lock():
    global active_present,active_auto
    if active_present == False:
        if active_auto == True:
            active_auto = False
        active_present = True
        thread3 = Thread(target=move_cursor_with_gestures)
        thread3.start()
    else:
        active_present = False


def move_cursor_with_gestures():
    global cap, finger_connected, img, x, y,active_auto,active_present

    with mpHands.Hands(max_num_hands=1) as hands:
        g = 3
        while True:
            if active_auto == False and active_present == False:
                break
            # Получение кадра из видеопотока
            ret, frame = cap.read()

            # Преобразование изображения в RGB-формат
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.flip(img, 1)

            # Обнаружение руки на кадре
            results = hands.process(img)

            # Рисование обнаруженной руки на кадре
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mpDraw.draw_landmarks(img, hand_landmarks, mpHands.HAND_CONNECTIONS)

                    # Обработка жестов рук avt
                    if active_auto == True:
                        x, y = process_hand_landmarks(hand_landmarks, x, y)
                    # Обработка жестов рук present
                    if active_present == True:
                        a = present(hand_landmarks, g)
                        # print(a)
                        if a == True:
                            g = 0
                        g += 1

# создает локальный сервер
def create_hosts():
    eel.init('interface')
    eel.start('index.html', mode=None)

# создает окно
class MYAPP(QMainWindow):
    def __init__(self):
        super(MYAPP, self).__init__()

        self.webEngineView = QWebEngineView(self)
        self.setCentralWidget(self.webEngineView)
        self.setWindowIcon(QtGui.QIcon('interface/img/icon.png'))

        url = QUrl.fromUserInput("http://localhost:8000/index.html")
        self.webEngineView.setUrl(url)
        if url.isValid():
            self.webEngineView.load(url)

if __name__ == "__main__":
    thread1 = Thread(target=create_hosts)
    thread1.start()
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = MYAPP()
    ex.setFixedSize(850, 600)
    ex.setWindowTitle("ControlEngine")
    ex.show()
    sys.exit(app.exec_())