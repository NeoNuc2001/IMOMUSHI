import copy
import time
from flask import Flask, render_template
from flask_socketio import SocketIO
from datetime import datetime
import threading
import ctypes

from keyboard_event import PressKey, ReleaseKey, key
import psutil
import multiprocessing
from collections import deque

app = Flask(__name__)
socketio = SocketIO(app)


active_keys_queue = deque()
active_keys_queue_lock = threading.Lock()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('tap_event')
def handle_tap_event(data):
    print(f"タップイベント:  {datetime.now()} {data}")
    global active_keys
    idx = data['panel']
    flg = data['touching']
    vk = []
    for i in idx:
        x = i % 16
        y = i // 16
        s = slider_keymap[y][x]
        vk.append((s, flg))
    for s, flg in vk:
        active_keys_queue.put((key[s.upper()], flg))
        


def loop_tap_event(active_keys_queue, stop_flg):
    from keyboard_event import PressKey, ReleaseKey  # Import inside for multiprocessing compatibility
    current_active_keys = set()
    while not stop_flg.value:
        active_keys = set()
        deactive_keys = set()

        while not active_keys_queue.empty():
            data = active_keys_queue.get()
            idx = data[0]
            flg = data[1]
            if flg:
                active_keys.add(idx)
            else:
                deactive_keys.add(idx)
        # すでに押されているキーを解除
        active_keys = active_keys - current_active_keys

        # 逆に押されていないキーを削除
        deactive_keys = deactive_keys & current_active_keys

        current_active_keys = active_keys | current_active_keys
        current_active_keys = current_active_keys - deactive_keys
        if active_keys:
            PressKey(active_keys)
        if deactive_keys:
            ReleaseKey(deactive_keys)

        
# 仮想キーコードに変換（英字・数字・記号のみ対応）
# def char_to_vk(c):
#     vk_map = {
#         '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34, '5': 0x35,
#         '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39, '0': 0x30,
#         'A': 0x41, 'B': 0x42, 'C': 0x43, 'D': 0x44, 'E': 0x45,
#         'F': 0x46, 'G': 0x47, 'H': 0x48, 'I': 0x49, 'J': 0x4A,
#         'K': 0x4B, 'L': 0x4C, 'M': 0x4D, 'N': 0x4E, 'O': 0x4F,
#         'P': 0x50, 'Q': 0x51, 'R': 0x52, 'S': 0x53, 'T': 0x54,
#         'U': 0x55, 'V': 0x56, 'W': 0x57, 'X': 0x58, 'Y': 0x59,
#         'Z': 0x5A, ',': 0xBC, '.': 0xBE
#     }
#     return vk_map.get(c.upper(), None)

# キー押下・離す


pressed_keys = set()

# def press_key(vk):
#     KEYEVENTF_KEYDOWN = 0x0000
#     if vk not in pressed_keys:
#         ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYDOWN, 0)
#         pressed_keys.add(vk)
#         print(f"キー押下: {vk} ({chr(vk)})")


# def unpress_key(vk):
#     KEYEVENTF_KEYUP = 0x0002
#     if vk in pressed_keys:
#         ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
#         pressed_keys.discard(vk)
#         print(f"キー離す: {vk} ({chr(vk)})")


def timestamp_to_datetime(ts):
    """ミリ秒のタイムスタンプをdatetimeオブジェクトに変換"""
    return datetime.fromtimestamp(ts / 1000.0)


# def handle_tap_queue():
#     global tap_queue
#     while True:
#         if tap_queue:
#             tap_data = tap_queue.popleft()
#             x, y = tap_data['x'], tap_data['y']
#             x *= 16
#             x = int(x)
#             y = 1 if y >= 0.5 else 0
#             s = slider_keymap[y][x]
#             pyautogui.press(s)
        
# def get_ave_reaction_time():
#     while True:
#         time.sleep(10)
#         if len(tap_positions) < 2:
#             continue
#         time_data = [timestamp_to_datetime(ts["timestamp"]) for ts in tap_positions[-10:]]
#         time_diff = [(time_data[i] - time_data[i-1]).total_seconds() for i in range(1, len(time_data))]
#         ave_reaction_time = sum(time_diff) / len(time_diff) if time_diff else 0
#         print("平均応答時間:", 1/ave_reaction_time)
def auto_air():
    i = 0
    try:
        last_air_flg = False
        print("自動エアーを開始します。")
        while not stop_flg.value:
            # Check if "app.exe" is the foreground window
            # Get the foreground window handle
            foreground_window = ctypes.windll.user32.GetForegroundWindow()
            # Get the process ID of the foreground window
            pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(foreground_window, ctypes.byref(pid))
            # Get the executable name from the process ID
            window_title = ""
            exe_name = ""
            try:
                proc = psutil.Process(pid.value)
                exe_name = proc.name().lower()
            except Exception:
                exe_name = ""
            # Get window title as fallback
            length = ctypes.windll.user32.GetWindowTextLengthW(foreground_window)
            buff = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(foreground_window, buff, length + 1)
            window_title = buff.value.lower()
            # Check both exe name and window title for "app.exe"
            # 右シフトが押されているかどうかをチェック
            right_shift_pressed = (ctypes.windll.user32.GetAsyncKeyState(0xA1) & 0x8000) != 0
            
            if (("app.exe" in exe_name or "app.exe" in window_title) and not right_shift_pressed):
                if not last_air_flg:
                    print("自動エアーを開始します。")
                    last_air_flg = True
                # Then press the air keys
                k = air_keymap[i % len(air_keymap)]
                vk = key[k.upper()]
                if vk:
                    PressKey(vk)
                time.sleep(1/60)
                # First unbind all air keys
                for k in air_keymap:
                    vk = key[k.upper()]
                    if vk:
                        ReleaseKey(vk)
                i += 1
            else:
                if last_air_flg:
                    print("自動エアーを停止します。")
                    last_air_flg = False
                time.sleep(0.2)
    except KeyboardInterrupt as e:
        pass
    finally:
        print("自動エアーを停止します。")
stop_flg = multiprocessing.Value('b', False)
if __name__ == '__main__':
    slider_keymap_str = "1AQZ2SWX3DEC4FRV5GTB6HYN7JUM8KI90OLP,." + "D"
    slider_keymap = [
        [i for i in slider_keymap_str[1:-1:2]],
        [i for i in slider_keymap_str[0:-1:2]],
    ]
    air_keymap_str = "0opl"
    air_keymap = [i for i in air_keymap_str]
    print("スライダーキー:", slider_keymap)

    # multiprocessing用のキューとフラグを作成
    active_keys_queue = multiprocessing.Queue()
    stop_flg = multiprocessing.Value('b', False)

    try:
        th_air = threading.Thread(target=auto_air)
        th_air.daemon = True
        th_air.start()

        # loop_tap_eventをプロセスとして起動
        proc_tap = multiprocessing.Process(target=loop_tap_event, args=(active_keys_queue, stop_flg))
        proc_tap.daemon = True
        proc_tap.start()
        
        socketio.run(app, host='0.0.0.0', port=5000)
    except Exception as e:
        print("サーバーを停止します。")
        socketio.stop()
        stop_flg.value = True
    finally:
        th_air.join()
        proc_tap.join()
