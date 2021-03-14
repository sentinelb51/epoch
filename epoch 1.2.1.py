from math import modf
from os import system
from random import uniform
from time import time, sleep

from pynput.keyboard import KeyCode
from pynput.keyboard import Listener as kb_listener
from pynput.mouse import Button, Controller
from pynput.mouse import Listener as ms_listener

system("mode 40,5")
system("title [-] Epoch 1.2.1")
print()
user_cps = None
while not user_cps:
    try:
        user_cps = float(input(" CPS: "))
        if not 7 < user_cps < 21:
            user_cps = None
            print(" Invalid range, expected 8-20")
    except ValueError:
        print(" Invalid input")
    else:
        if user_cps > 16.8:
            print(" [!] You are using unsafe settings")
print(" Press [ to exit and ] to toggle")

toggle = KeyCode(char=']')
exit_key = KeyCode(char='[')

button = Button.left
cps = 1 / user_cps
active = False
running = True
fatigue = 8
just_started = True
held = False


def on_click(x, y, button, pressed):
    if button == Button.left:
        global held
        held = not held


def on_press(key):
    global active
    if key == toggle:
        if active:
            active = False
            system("title [-] Epoch 1.2.1")
        else:
            active = True
            system("title [+] Epoch 1.2.1")
    elif key == exit_key:
        global running
        keyboard_handler.stop(), mouse_handler.stop()
        running = False


keyboard_handler = kb_listener(on_press=on_press)
mouse_handler = ms_listener(on_click=on_click)
keyboard_handler.start(), mouse_handler.start()

mouse = Controller()

while running:
    while active and held:
        mouse.click(button)

        decimals, whole = modf(time())
        chance = whole % 10

        if chance == 9:
            variation = decimals * uniform(0.008, 0.1) * fatigue
        elif chance % 4 == 0:
            variation = -decimals * uniform(0.004, 0.02)
        else:
            variation = decimals * uniform(0.002, 0.0088) * fatigue

        sleep(cps + variation)

        if just_started:
            fatigue -= 0.1
        else:
            fatigue += 0.01

        if fatigue < 1:
            just_started = False
    sleep(0.5)  # This is the reaction time to toggling state
    fatigue = 8
    just_started = True
