from os import system
from random import getrandbits, uniform, randint
from threading import Thread
from time import sleep
from statistics import stdev, mean

from pynput.keyboard import KeyCode
from pynput.keyboard import Listener as kb_listener
from pynput.mouse import Button, Controller
from pynput.mouse import Listener as ms_listener


def introduction():
    system("cls")
    system("mode 30,5")
    system("title \u200b")
    user_cps = None
    while not user_cps:
        print()
        print("Epoch".center(30))
        try:
            user_cps = float(input(" CPS: "))

            toggle_key = KeyCode(char=input(" Toggle key: "))
            exit_key = KeyCode(char=input(" Exit key: "))
        except ValueError:
            print(" Invalid input provided")
        else:
            return (1 / user_cps * 1000), toggle_key, exit_key, user_cps


cps, toggle, close, raw_cps = introduction()


def get_randomisation():
    delays = []

    def get_delay(seq, minimum, maximum, force_min=False, force_max=False):

        if force_max:
            base = cps * maximum
        elif force_min:
            base = cps * minimum
        else:
            base = cps * uniform(minimum, maximum)

        if seq % randint(20, 40) == 0:
            noise = getrandbits(9)

        elif seq % randint(2, 15) == 0:
            noise = getrandbits(8)
        else:
            noise = getrandbits(5) + getrandbits(4)

        delay = base + noise
        if sequence < raw_cps:
            return delay / 2500
        return delay / 3000

    max_minimum = uniform(1.1, 1.6)
    min_minimum = uniform(0.6, 0.78)
    minimum = 1.5
    maximum = 1.2
    rise = False

    for sequence in range(750):
        drop_chance = uniform(0.0, 1.0)
        spike_chance = uniform(0.0, 1.0)

        if rise:
            minimum += uniform(0.0002, 0.0015)
        else:
            minimum -= uniform(0.002, 0.03)

        maximum += uniform(0.0003, 0.001)

        if minimum >= max_minimum:
            rise = False
        elif minimum < min_minimum:
            rise = True

        # print(minimum, maximum, spike_chance, drop_chance)
        real = get_delay(sequence, minimum, maximum,
                         force_min=True if spike_chance > uniform(0.84, 0.99) else False,
                         force_max=True if drop_chance > uniform(0.8, 0.99) else False
                         )
        delays.append(real)
    print(f"Std dev: {stdev(delays)}, Mean: {mean(delays)}")
    return tuple(delays)


class Epoch(Thread):
    def __init__(self):
        super().__init__()
        self.button = Button.left
        self.toggleable = False
        self.running = True
        self.held = False
        self.pattern = get_randomisation()

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
                self.pattern = get_randomisation()

        elif key == close:
            self.exit()

    def run(self):
        while self.running:
            for x in self.pattern:
                sleep(x)
                if not self.held:
                    sleep(0.25)
                    break

                mouse.press(self.button)
                sleep(x)
                mouse.release(self.button)


click_thread = Epoch()
mouse = Controller()
mouse_handler = ms_listener(on_click=click_thread.on_click)
keyboard_handler = kb_listener(on_press=click_thread.on_press)

click_thread.start()
mouse_handler.start()
keyboard_handler.start()
