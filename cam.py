import cv2

devices = []

for i in range(10):
    cap = cv2.VideoCapture(i)
    if cap.read()[0]:
        devices.append(i)
        cap.release()
print(devices)