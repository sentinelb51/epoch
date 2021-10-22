import time
from ctypes import windll, WinDLL
from os import system
from random import getrandbits, uniform, randint, choice
from threading import Thread
from time import sleep

from pynput.keyboard import KeyCode
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Button, Controller
from pynput.mouse import Listener as MouseListener

kernel32 = windll.kernel32
WinMM = WinDLL("winmm")
WinMM.timeBeginPeriod(15)
kernel32.SetThreadPriority(kernel32.GetCurrentThread(), 31)

logo: str = """\n
 ██████  ██████  ██████  ██████  █▓   ░█
 █▓░░░░  █▓░░░█  █░░░░█  █░░░░░  █▓   ░█
 ██████  █████░  █▓  ░█  █▓      ███████
 █▓      █▓      █▓  ░█  █▓      █▓   ░█
 ██████  █▓      ██████  ██████  █▓   ░█
 \n""".center(43)

closing: str = """\n
██████  ██████  ██████  ██████  █▓   ░█
  █▓░░░░  █▓░░░█  █░░░░█  █░░░░░  █▓   ░█
██████  █████░  █▓  ░█  █▓      ███████
  █▓      █▓      █▓  ░█  █▓      █▓   ░█
██████  █▓      ██████  ██████  █▓   ░█
 \n""".center(43)


def introduction():
    system("cls")
    system("mode 43,11")
    system("title \u200b")
    user_cps = None
    while not user_cps:
        print(logo)
        try:
            user_cps = float(input(" [CPS] _ "))
            toggle_key = KeyCode(char=input(" [TOGGLE-KEY] _ "))
            exit_key = KeyCode(char=input(" [EXIT-KEY] _ "))
        except ValueError:
            print(" Invalid input provided")
        else:
            return 0.5 / user_cps * 1000, toggle_key, exit_key, int(user_cps)


cps, toggle, close, raw_cps = introduction()


def get_randomisation(base):
    randomisation = []

    def get_delay(base_delay, high=False, low=False) -> float:

        if iteration % choice((50, 80, 100, 120)) == 0:
            return (base_delay + getrandbits(7)) / randint(1000, 1200)
        elif high:
            return base_delay * uniform(uniform(1.15, 1.2), uniform(1.2, 1.72)) / 1000
        elif low:
            return base_delay * uniform(uniform(0.65, 0.75), uniform(0.7, 0.97)) / 1000
        else:
            if getrandbits(1):
                return (base_delay + getrandbits(4)) / randint(900, 1000)
            else:
                return (base_delay + getrandbits(4)) / randint(1000, 1100)

    fatigue = 0

    for iteration in range(1250):

        if fatigue > 0:
            randomisation.append(get_delay(base, high=True))
            fatigue -= 1
        elif fatigue < 0:
            randomisation.append(get_delay(base, low=True))
            fatigue += 1
        else:
            if iteration % raw_cps == 0:
                if getrandbits(1):
                    fatigue += randint(randint(3, 8), randint(8, raw_cps))
                else:
                    fatigue -= randint(randint(4, 6), randint(6, raw_cps))

            if getrandbits(1):
                randomisation.append(get_delay(base * uniform(0.9, 1.00)))
            else:
                randomisation.append(get_delay(base * uniform(1.00, 1.1)))

    return (x for x in randomisation)


class Epoch(Thread):
    def __init__(self):
        super().__init__()
        self.mouse = Controller()
        self.button = Button.left
        self.toggleable = False
        self.running = True
        self.held = False
        self.pattern = get_randomisation(cps)
        self.cycles = 0

        self.keymap = {
            toggle: self.toggle,
            close: self.exit
        }

    def regenerate(self):
        if self.cycles % 2 == 0:
            offset = 0.5 / (raw_cps * uniform(1.075, 1.175)) * 1000
        else:
            offset = 0.5 / (raw_cps * uniform(0.95, 1.05)) * 1000

        self.pattern = get_randomisation(offset)
        self.cycles += 1

    def exit(self):
        self.running = False
        system("cls")
        print(closing)
        time.sleep(0.4)
        system("cls")
        exit(0)

    def toggle(self):
        self.held = False
        self.toggleable = not self.toggleable

        if not self.toggleable:
            self.regenerate()

    def on_click(self, _, __, button, ___):
        if self.toggleable and button == self.button:
            self.held = not self.held

    def on_press(self, key):
        action = self.keymap.get(key, None)
        if action:
            action()

    def run(self):
        while self.running:
            while self.held:
                try:
                    delay = self.pattern.__next__()
                except StopIteration:
                    self.regenerate()
                    delay = self.pattern.__next__()

                self.mouse.press(self.button)
                sleep(delay)
                self.mouse.release(self.button)
                sleep(delay)
            sleep(0.1)


click_thread = Epoch()
mouse_handler = MouseListener(on_click=click_thread.on_click)
keyboard_handler = KeyboardListener(on_press=click_thread.on_press)

click_thread.start()
mouse_handler.start()
keyboard_handler.start()
