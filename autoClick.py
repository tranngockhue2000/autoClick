from pywinauto import Application
import cv2
import numpy as np
import time
import random
import glob
from PIL import ImageGrab
import ctypes
from ctypes import wintypes


# Define mouse input structures
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long), ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]

    _anonymous_ = ("_input",)
    _fields_ = [("type", ctypes.c_ulong), ("_input", _INPUT)]


def send_click(x, y):
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)
    abs_x = int(x * 65536 / screen_width)
    abs_y = int(y * 65536 / screen_height)

    input_array = (INPUT * 3)(
        INPUT(type=0, _input=INPUT._INPUT(
            mi=MOUSEINPUT(dx=abs_x, dy=abs_y, mouseData=0, dwFlags=0x8000 | 0x0001, time=0, dwExtraInfo=None))),
        # MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE
        INPUT(type=0,
              _input=INPUT._INPUT(mi=MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=0x0002, time=0, dwExtraInfo=None))),
        # MOUSEEVENTF_LEFTDOWN
        INPUT(type=0,
              _input=INPUT._INPUT(mi=MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=0x0004, time=0, dwExtraInfo=None)))
        # MOUSEEVENTF_LEFTUP
    )

    ctypes.windll.user32.SendInput(len(input_array), input_array, ctypes.sizeof(INPUT))


def find_and_click(template, window_rect):
    screenshot = ImageGrab.grab(bbox=(window_rect.left, window_rect.top, window_rect.right, window_rect.bottom))
    screenshot_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    top_left = max_loc
    h, w = template.shape

    click_x = window_rect.left + top_left[0] + w // 2
    click_y = window_rect.top + top_left[1] + h // 2

    send_click(click_x, click_y)


template_images = glob.glob('templates/*.png')

app = Application(backend="uia").connect(title_re="Telegram.*")
window = app.top_window()
window_rect = window.rectangle()

window.minimize()

while True:
    for template_path in template_images:
        template_image = cv2.imread(template_path, 0)
        find_and_click(template_image, window_rect)
        time.sleep(random.uniform(1, 3))
