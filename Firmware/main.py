# Imports
# CircuitPython Import
import board
import busio
import adafruit_pcf8574
from keypad import Event as KeyEvent
# KMK Import
from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners import Scanner
from kmk.keys import KC
# KMK Key Scanners Import
from kmk.scanners.keypad import KeysScanner
from kmk.scanners.encoder import RotaryioEncoder
# Extra Import
from kmk.extensions.media_keys import MediaKeys
from kmk.modules.layers import Layers
from kmk.modules.mouse_keys import MouseKeys
#--------------------------------------------------
# The Beginning
keyboard = KMKKeyboard()
# Extras
keyboard.extensions.append(MediaKeys())
keyboard.modules.append(MouseKeys())
keyboard.modules.append(Layers())
#--------------------------------------------------
# PCF8574AT Defining
class PCF8574Matrix(Scanner):
    def __init__(self, pcf, row_pins, col_pins, offset=0):
        self.pcf = pcf
        self.row_pins = row_pins
        self.col_pins = col_pins
        self.offset = offset
        self.ncols = len(col_pins)
        self._count = len(row_pins) * len(col_pins)
        self.state = bytearray(self._count)
        self._pending = []
        pcf.write_gpio(0xFF)

    @property
    def key_count(self):
        return self._count

    def scan_for_changes(self):
        if not self._pending:
            for r, rpin in enumerate(self.row_pins):
                self.pcf.write_gpio(0xFF & ~(1 << rpin))
                val = self.pcf.read_gpio()
                for c, cpin in enumerate(self.col_pins):
                    pressed = 0 if (val >> cpin) & 1 else 1
                    idx = r * self.ncols + c
                    if self.state[idx] != pressed:
                        self.state[idx] = pressed
                        self._pending.append((idx + self.offset, bool(pressed)))
            self.pcf.write_gpio(0xFF)
        if self._pending:
            kn, pressed = self._pending.pop(0)
            return KeyEvent(kn, pressed)
        return None
#--------------------------------------------------
## I2C Configuration
i2c = busio.I2C(scl=board.D5, sda=board.D4, frequency=100_000)
pcf = adafruit_pcf8574.PCF8574(i2c, address=0x38)
#--------------------------------------------------
# Rotary Encoders & Switches
encoder_switches = KeysScanner(
    pins = [board.D8, board.D7],
    value_when_pressed = False,
    pull = True,
)
encoder_1 = RotaryioEncoder(pin_a=board.D0, pin_b=board.D1, divisor=4)
encoder_2 = RotaryioEncoder(pin_a=board.D2, pin_b=board.D3, divisor=4)
#--------------------------------------------------
# Keyswitches
mechanicalmatrix = PCF8574Matrix(pcf, row_pins=[3, 4, 5, 6], col_pins=[0, 1, 2])
keyboard.matrix = [mechanicalmatrix, encoder_switches, encoder_1, encoder_2]
#--------------------------------------------------
#Keymapping
keyboard.keymap = [
    # Layer 0
    [
    KC.N7, KC.N8, KC.N9,
    KC.N4, KC.N5, KC.N6,
    KC.N1, KC.N2, KC.N3,
    KC.N0, KC.NO, KC.NO,

    KC.AUDIO_MUTE, KC.TG(1),
    KC.AUDIO_VOL_UP, KC.AUDIO_VOL_DOWN,
    KC.BRIGHTNESS_UP, KC.BRIGHTNESS_DOWN,
    ],
    # Layer 1
    [
    KC.MB_LMB, KC.UP, KC.MB_RMB,
    KC.LEFT, KC.DOWN,   KC.RGHT,
    KC.NO,  KC.NO, KC.NO,
    KC.NO,   KC.NO,   KC.NO,

    KC.NO, KC.TG(1),
    KC.MW_DOWN, KC.MW_UP,
    KC.MW_DOWN, KC.MW_UP,
    ],
]
#------------------------
# Final Lines - Run the Code
if __name__ == '__main__':
    keyboard.go()
