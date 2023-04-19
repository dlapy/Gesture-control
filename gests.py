import pyautogui

#finger_connected = False

def handle_gesture(gesture, finger_connected):
    if gesture == "OK":
        if finger_connected:
            pyautogui.click(button='left')
            pyautogui.sleep(0.5)
    elif gesture == "RC":
        if finger_connected:
            pyautogui.click(button='right')
            pyautogui.sleep(0.5)