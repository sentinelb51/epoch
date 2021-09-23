from os import system
from random import getrandbits, uniform, randint, choice
from threading import Thread
from time import sleep

from pynput.keyboard import KeyCode
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Button, Controller
from pynput.mouse import Listener as MouseListener
from ctypes import windll, WinDLL

kernel32 = windll.kernel32
WinMM = WinDLL("winmm")
WinMM.timeBeginPeriod(15)
kernel32.SetThreadPriority(kernel32.GetCurrentThread(), 31)


def introduction():
    system("cls")
    system("mode 36,6")
    system("title \u200b")
    user_cps = None
    while not user_cps:
        print("\n--- Epoch ---\n".center(36))
        try:
            user_cps = float(input(" CPS: "))

            toggle_key = KeyCode(char=input(" Toggle key: "))
            exit_key = KeyCode(char=input(" Exit key: "))
        except ValueError:
            print(" Invalid input provided")
        else:
            return (0.5 / user_cps * 750), toggle_key, exit_key, int(user_cps)


cps, toggle, close, raw_cps = introduction()


def get_randomisation(base):
    randomisation = []

    def get_delay(base_delay, high=False, low=False):

        if iteration % choice((50, 80, 100)) == 0:
            return (base_delay * uniform(1.3, 2.6)) / 1000

        if high:
            return base_delay * uniform(uniform(1.0, 1.3), uniform(1.2, 1.6)) / 1000
        elif low:
            return base_delay * uniform(uniform(0.82, 0.86), uniform(0.88, 0.97)) / 1000
        else:
            return (base_delay + getrandbits(6)) / randint(1000, 1350)

    fatigue = 0

    for iteration in range(2750):

        if fatigue > 0:
            randomisation.append(get_delay(base, high=True))
            fatigue -= 1
        elif fatigue < 0:
            randomisation.append(get_delay(base, low=True))
            fatigue += 1
        else:
            if iteration % raw_cps == 0:
                if getrandbits(1):
                    fatigue += randint(randint(1, 3), randint(3, raw_cps))
                else:
                    fatigue -= randint(randint(2, 4), randint(9, raw_cps))

            if getrandbits(1):
                randomisation.append(get_delay(base * uniform(0.86, 0.94)))
            else:
                randomisation.append(get_delay(base * uniform(1.05, 1.25)))

    return randomisation


class Epoch(Thread):
    def __init__(self):
        super().__init__()
        self.button = Button.left
        self.toggleable = False
        self.running = True
        self.held = False
        self.pattern = get_randomisation(cps)

    def exit(self):
        self.running = False

    def on_click(self, _, __, button, ___):
        if self.toggleable and button == self.button:
            self.held = not self.held

    def on_press(self, key):

        if key == toggle:
            self.held = False
            self.toggleable = not self.toggleable

            if not self.toggleable:
                self.pattern = get_randomisation(cps)

        elif key == close:
            self.exit()

    def run(self):
        while self.running:
            for x in self.pattern:
                if not self.held:
                    sleep(0.15)
                    break

                mouse.press(self.button)
                sleep(x)
                mouse.release(self.button)
                sleep(x)


click_thread = Epoch()
mouse = Controller()
mouse_handler = MouseListener(on_click=click_thread.on_click)
keyboard_handler = KeyboardListener(on_press=click_thread.on_press)

click_thread.start()
mouse_handler.start()
keyboard_handler.start()
