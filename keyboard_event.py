from queue import Queue
import time
import ctypes
from unbind_all import unbind

#SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions

PUL = ctypes.POINTER(ctypes.c_ulong)

key = {
    "up": 0x48, "down": 0x50, "left": 0x4D, "right": 0x4B,
    "z": 0x2C, "Enter": 0x1C, "Shift": 0x2A,
    # アルファベット
    "A": 0x1E, "B": 0x30, "C": 0x2E, "D": 0x20, "E": 0x12, "F": 0x21, "G": 0x22, "H": 0x23,
    "I": 0x17, "J": 0x24, "K": 0x25, "L": 0x26, "M": 0x32, "N": 0x31, "O": 0x18, "P": 0x19,
    "Q": 0x10, "R": 0x13, "S": 0x1F, "T": 0x14, "U": 0x16, "V": 0x2F, "W": 0x11, "X": 0x2D,
    "Y": 0x15, "Z": 0x2C,
    # 数字
    "0": 0x0B, "1": 0x02, "2": 0x03, "3": 0x04, "4": 0x05, "5": 0x06, "6": 0x07, "7": 0x08, "8": 0x09, "9": 0x0A,
    # ピリオド
    ".": 0x34,
    # コロン
    ":": 0x27
}

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


# Actuals Functions
def PressKey(hexKeyCodes):
    if isinstance(hexKeyCodes, int):
        hexKeyCodes = [hexKeyCodes]
    inputs = []
    extra = ctypes.c_ulong(0)
    for hexKeyCode in hexKeyCodes:
        ii_ = Input_I()
        ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
        inputs.append(Input(ctypes.c_ulong(1), ii_))
    nInputs = len(inputs)
    LPINPUT = Input * nInputs
    ctypes.windll.user32.SendInput(nInputs, LPINPUT(*inputs), ctypes.sizeof(Input))


def ReleaseKey(hexKeyCodes):
    if isinstance(hexKeyCodes, int):
        hexKeyCodes = [hexKeyCodes]
    inputs = []
    extra = ctypes.c_ulong(0)
    for hexKeyCode in hexKeyCodes:
        ii_ = Input_I()
        ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
        inputs.append(Input(ctypes.c_ulong(1), ii_))
    nInputs = len(inputs)
    LPINPUT = Input * nInputs
    ctypes.windll.user32.SendInput(nInputs, LPINPUT(*inputs), ctypes.sizeof(Input))

def SafePressKey(key_name,waiter=0.1):
    try:
        if type(key_name) is int:
            hexCode= key_name
        else:
            hexCode= key[key_name]
        PressKey(hexCode)
        time.sleep(waiter)
        ReleaseKey(hexCode)
    except Exception as e:
        unbind(ReleaseKey)
        raise e()
    
