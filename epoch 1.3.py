from os import system
from random import getrandbits
from time import sleep

from pynput.keyboard import KeyCode
from pynput.keyboard import Listener as kb_listener
from pynput.mouse import Button, Controller
from pynput.mouse import Listener as ms_listener

system("mode 40,4")
system("title [-] Epoch 1.3")
print()
user_cps = None
while not user_cps:
    try:
        user_cps = float(input(" CPS: "))
    except ValueError:
        print(" Invalid arguments provided")
        system("pause>nul")
        user_cps = None
    else:
        print(" Press [ to exit and ] to toggle")

toggle = KeyCode(char=']')
exit_key = KeyCode(char='[')

left_click = Button.left
right_click = Button.right
cps = 1 / user_cps * 1000
toggleable = False
running = True
held = False


def on_click(x, y, button, pressed):
    if toggleable:
        global held
        if button == left_click:
            held = not held


def on_press(key):
    if key == toggle:
        global toggleable
        if toggleable:
            toggleable = False
            system("title [-] Epoch 1.3")
        else:
            toggleable = True
            system("title [+] Epoch 1.3")
    elif key == exit_key:
        global running
        running = False


keyboard_handler = kb_listener(on_press=on_press)
mouse_handler = ms_listener(on_click=on_click)
keyboard_handler.start(), mouse_handler.start()

mouse = Controller()


def compile_pattern():
    chance = getrandbits(2)
    seed = getrandbits(3)

    if chance == seed:
        delay = cps + getrandbits(5)
    else:
        delay = cps + getrandbits(seed)

    return delay / 1000


pattern = tuple([compile_pattern() for x in range(1500)])

while running:

    for x in pattern:
        if not held:
            sleep(0.5)
            break

        mouse.click(left_click)
        sleep(x)
