from threading import Thread
from os import system
from random import getrandbits, uniform
from time import sleep

from pynput.keyboard import KeyCode
from pynput.keyboard import Listener as kb_listener
from pynput.mouse import Button, Controller
from pynput.mouse import Listener as ms_listener

system("mode 40,5")
system("title \u200b")
print()
user_cps = None
while not user_cps:
    try:
        user_cps = float(input(" CPS: "))
    except ValueError:
        print(" Invalid input provided")
print(" Press [ to exit and ] to toggle")

toggle = KeyCode(char=']')
exit_key = KeyCode(char='[')

cps = 1 / user_cps * 850


def wrapper():
    minimum = 1.25
    maximum = 1.0

    def compile_pattern(min_delay, max_delay, seq):
        if seq % 20 == 0:
            if getrandbits(1):
                min_delay, max_delay = 0.5, 1.0
                jitter = 0
            else:
                jitter = getrandbits(8)
        elif seq % 50 == 0:
            if getrandbits(1):
                jitter = getrandbits(9)
            else:
                min_delay, max_delay = 0.5, 0.7
                jitter = 0
        else:
            jitter = getrandbits(5)

        delay = cps * uniform(min_delay, max_delay)
        delay += jitter

        return delay / 2000

    delays = []

    falling_edge = True
    for sequence in range(1250):
        delays.append(compile_pattern(minimum, maximum, sequence))
        maximum += uniform(0.0007, 0.0016)
        if falling_edge:
            if minimum > 0.65:
                if sequence < user_cps:
                    minimum -= uniform(0.009, 0.015)
                else:
                    minimum -= uniform(0.0005, 0.0015)
            else:
                falling_edge = False
                maximum = 1.0
        else:
            minimum += uniform(0.001, 0.005)

            if minimum > 1.4:
                falling_edge = True

    return tuple(delays)

class Epoch(Thread):
    def __init__(self):
        super(Epoch, self).__init__()
        self.button = Button.left
        self.toggleable = False
        self.running = True
        self.held = False
        self.pattern = wrapper()

    def exit(self):
        self.running = False

    def on_click(self, _, __, button, ___):
        if button == self.button and self.toggleable:
            self.held = not self.held

    def on_press(self, key):

        if key == toggle:
            self.held = False
            self.toggleable = not self.toggleable

            if not self.toggleable:
                self.pattern = wrapper()

        elif key == exit_key:
            self.exit()

    def run(self):
        while self.running:
            for x in self.pattern:
                sleep(x)
                if not self.held:
                    sleep(0.4)
                    break

                mouse.press(self.button)
                sleep(x)
                mouse.release(self.button)


mouse = Controller()
click_thread = Epoch()
mouse_handler = ms_listener(on_click=click_thread.on_click)
keyboard_handler = kb_listener(on_press=click_thread.on_press)


click_thread.start()
mouse_handler.start()
keyboard_handler.start()
