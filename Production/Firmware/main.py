# Prerequisites
import board
import busio
import digitalio
 
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.scanners.digitalio import MatrixScanner
from kmk.scanners.keypad import KeysScanner
from kmk.scanners.encoder import RotaryioEncoder
 
import adafruit_pcf8574

keyboard = KMKKeyboard()
#------------------------
# I2C Configuration
# what am i supposed to write for frequency?
i2c = busio.I2C(scl=board.D5, sda=board.D4, frequency=100_000)
pcf = adafruit_pcf8574.PCF8574(i2c, address=0x38)
#------------------------
# Matrix
colpins = [pcf.get_pin(0), pcf.get_pin(1), pcf.get_pin(2)]
rowpins = [pcf.get_pin(3), pcf.get_pin(4), pcf.get_pin(5), pcf.get_pin(6)]

matrix = MatrixScanner(
    cols=colpins,
    rows=rowpins,
    diode_orientation=DiodeOrientation.ROW2COL,
    pull=digitalio.Pull.UP,
)
#------------------------
# Rotary Encoders with Switches
encoder_switches = KeysScanner(
    pins = [board.D8, board.D7],
    value_when_pressed = False,
    pull = True,
)
encoder_1 = RotaryioEncoder(pin_a=board.D0, pin_b=board.D1, divisor=4)
encoder_2 = RotaryioEncoder(pin_a=board.D2, pin_b=board.D3, divisor=4)
#------------------------
# Coding the matrix
keyboard.matrix = [matrix, encoder_switches, encoder_1, encoder_2]
keyboard.keymap = [
    [
    KC.N7, KC.N8, KC.N9,
    KC.N4, KC.N5, KC.N6,
    KC.N1, KC.N2, KC.N3,
    KC.N0, KC.NO, KC.NO,

    KC.MUTE, KC.PSCR,
    KC.VOLD, KC.VOLU,
    KC.BRID, KC.BRIU,
    ]
]
#------------------------
# Final Lines
if __name__ == '__main__':
    keyboard.go()