import threading
from os import system
from random import getrandbits, choice, uniform
from time import sleep


from pynput.keyboard import KeyCode
from pynput.keyboard import Listener as kb_listener
from pynput.mouse import Button, Controller
from pynput.mouse import Listener as ms_listener

system("mode 40,5")
system("title [-] Epoch 1.3.1")
print()
user_cps = None
while not user_cps:
    try:
        user_cps = float(input(" CPS: "))
    except ValueError:
        print(" Invalid input")
print(" Press [ to exit and ] to toggle")

toggle = KeyCode(char=']')
exit_key = KeyCode(char='[')

cps = 1 / user_cps * 1000


def wrapper():
    minimum = 1.0
    maximum = 1.5
    falling_edge = True

    def compile_pattern(min_delay, max_delay, seq):
        rising_edge = getrandbits(1)
        if seq % 40 == 0:
            if rising_edge:
                min_delay = 0.5
                max_delay = 1.2
            jitter = getrandbits(6)
        else:
            jitter = getrandbits(5)

        delay = cps * uniform(min_delay, max_delay)
        delay += jitter if rising_edge else -jitter

        return delay / 1000

    delays = []
    for sequence in range(5000):
        delays.append(compile_pattern(minimum, maximum, sequence))
        maximum += uniform(0.0004, 0.001)
        if falling_edge:
            if minimum > 0.6:
                minimum -= uniform(0.0003, 0.0015)
            else:
                falling_edge = False
        else:
            minimum += uniform(0.0001, 0.0025)

            if minimum > 15:
                falling_edge = True

    return tuple(delays)

class Epoch(threading.Thread):
    def __init__(self, button):
        super(Epoch, self).__init__()
        self.button = button
        self.toggleable = False
        self.running = True
        self.held = False
        self.pattern = wrapper()

    def exit(self):
        self.running = False

    def on_click(self, x, y, button, pressed):
        if button == self.button:
            if self.toggleable:
                self.held = not self.held

    def on_press(self, key):
        if key == toggle:
            if self.toggleable:
                self.toggleable = False
                system("title [-] Epoch 1.3.1")
            else:
                self.toggleable = True
                system("title [+] Epoch 1.3.1")
        elif key == exit_key:
            self.running = False
            click_thread.exit()
            exit()

    def run(self):
        while self.running:
            for x in self.pattern:
                if not self.held:
                    sleep(0.4)
                    break

                mouse.click(self.button)
                sleep(x)


mouse = Controller()
click_thread = Epoch(Button.left)
click_thread.start()

keyboard_handler = kb_listener(on_press=click_thread.on_press)
keyboard_handler.start()

mouse_handler = ms_listener(on_click=click_thread.on_click)
mouse_handler.start()
