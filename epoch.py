import ctypes
import time
from ctypes import WinDLL, wintypes
from os import system
from random import choice, getrandbits, randint, uniform
from threading import Thread
from time import sleep

from pynput.keyboard import KeyCode
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Button, Controller
from pynput.mouse import Listener as MouseListener

# todo: consider ditching pynput

class CURSORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("hCursor", wintypes.HANDLE),
        ("ptScreenPos", wintypes.POINT),
    ]


CURSOR_SHOWING = 0x00000001
USER32 = ctypes.WinDLL("user32", use_last_error=True)

CONSOLE_WIDTH = 44
CONSOLE_HEIGHT = 14

logo = """\n
 █████▓  ██████  ██████▓  █████▓  ██▓  ░██
 █▓░░░░  █▓░░░█░░█▓  ░█▓  █▓░░░░  ██▓  ░██
  ███▓   ██████ ░░░░░░░░░ █▓       ███████
 █▓   ░░░█▓      █▓░ ░█▓░░█▓   ░░░██▓ ░░██
 █████▓  █▓░░░░  ██████▓  █████▓  ██▓  ░██
 \n""".center(CONSOLE_WIDTH)

def clear() -> None:
    system("cls")

def setup_timer_priority() -> None:
    winmm = WinDLL("winmm")

    if winmm.timeBeginPeriod(1) != 0:
        exit("timeBeginPeriod failed")


def configure_console() -> None:
    clear()
    system(f"mode {CONSOLE_WIDTH},{CONSOLE_HEIGHT}")
    system("title \u200b")


def request_user_settings():
    while True:
        clear()
        print(logo)
        try:
            user_cps = int(input(" [CPS] _ "))
            toggle_key = KeyCode(char=input(" [TOGGLE KEY] _ "))
            exit_key = KeyCode(char=input(" [EXIT KEY] _ "))
            inventory_mode = bool(int(input(" [INVENTORY MODE] (1/0) _ ")))
        except ValueError:
            print(" Invalid input provided")
            continue

        # 0.5 to get half-click delay, 1000 to convert to milliseconds
        base_delay_ms = 0.5 / user_cps * 1000
        return base_delay_ms, toggle_key, exit_key, user_cps, inventory_mode

def is_cursor_visible() -> bool:
    ci = CURSORINFO()
    ci.cbSize = ctypes.sizeof(CURSORINFO)
    if not USER32.GetCursorInfo(ctypes.byref(ci)):
        raise ctypes.WinError(ctypes.get_last_error())
    return bool(ci.flags & CURSOR_SHOWING)

def get_delay(iteration: int, base_delay: float, *, high_delay=False, low_delay=False) -> float:
    if iteration % choice((50, 80, 100, 120)) == 0:
        return (base_delay + getrandbits(7)) / randint(1000, 1200)

    if high_delay:
        return base_delay * uniform(uniform(1.00, 1.09), uniform(1.1, 1.35)) / 1000

    if low_delay:
        return base_delay * uniform(uniform(0.68, 0.77), uniform(0.79, 0.99)) / 1000

    base = base_delay + getrandbits(4)
    denominator = randint(900, 1000) if getrandbits(1) else randint(1000, 1100)
    return base / denominator


def random_delay_pattern(base_delay_ms: float, raw_cps: int):
    balance = 0  # Positive balance = lower CPS; negative balance = higher CPS
    iteration = 0

    while True:
        # print("balance:", balance, "iteration:", iteration)
        if balance > 0:
            delay = get_delay(iteration, base_delay_ms, high_delay=True)
            balance -= 1
        elif balance < 0:
            delay = get_delay(iteration, base_delay_ms, low_delay=True)
            balance += 1
        else:
            if raw_cps and iteration % raw_cps == 0:
                if getrandbits(1):
                    balance += randint(randint(3, raw_cps), randint(raw_cps, raw_cps * 5))
                else:
                    balance -= randint(randint(4, raw_cps), randint(raw_cps, raw_cps * 2))

            base = base_delay_ms * uniform(0.9, 1.0) if getrandbits(1) else base_delay_ms * uniform(1.0, 1.1)
            delay = get_delay(iteration, base)

        iteration += 1
        yield delay

class Epoch(Thread):
    def __init__(self, delay_ms: float, toggle_key: str, exit_key: str, raw_cps: int, inventory_mode: bool):
        super().__init__(daemon=True)
        self.mouse = Controller()
        self.running = True
        self.button = Button.left
        self.inventory_mode = inventory_mode
        self.raw_cps = raw_cps
        self.toggleable = False
        self.held = False
        self.pattern_generator = random_delay_pattern(delay_ms, raw_cps)
        self.cycles = 0
        self.keybinds = {
            toggle_key: self.toggle,
            exit_key: self.exit_app,
        }

    def regenerate(self):
        # multiplier = uniform(1.075, 1.175) if self.cycles % 2 == 0 else uniform(0.95, 1.05)  # maybe don't do this
        multiplier = 1
        offset = 0.5 / (self.raw_cps * multiplier) * 1000
        self.pattern_generator = random_delay_pattern(offset, self.raw_cps)
        self.cycles += 1

    def exit_app(self):
        time.sleep(5)
        clear()
        print(logo.replace("█", "▓").center(CONSOLE_WIDTH))
        time.sleep(0.6)
        clear()
        self.running = False

    def toggle(self):
        self.held = False
        self.toggleable = not self.toggleable

        if not self.toggleable:
            self.regenerate()

    def on_click(self, _, __, button, ___):
        if self.toggleable and button == self.button:
            self.held = not self.held

    def on_press(self, key):
        if action := self.keybinds.get(key):
            action()

    def run(self):
        while self.running:

            if self.inventory_mode and is_cursor_visible():
                sleep(0.1)
                continue

            if self.held:
                delay = next(self.pattern_generator)
                self.mouse.press(self.button)
                sleep(delay)
                self.mouse.release(self.button)
                sleep(delay)
            else:
                sleep(0.1)

setup_timer_priority()
configure_console()
delay_ms, toggle_key, exit_key, raw_cps, inventory_mode = request_user_settings()
click_thread = Epoch(delay_ms, toggle_key, exit_key, raw_cps, inventory_mode)
mouse_handler = MouseListener(on_click=click_thread.on_click)
keyboard_handler = KeyboardListener(on_press=click_thread.on_press)
click_thread.start()
mouse_handler.start()
keyboard_handler.start()
click_thread.join()