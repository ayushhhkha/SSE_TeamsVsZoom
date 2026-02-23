import os
import time
import subprocess


import pyautogui
import pygetwindow as gw

# Configurations

MEETING_LINK = "https://us05web.zoom.us/j/6474533966?pwd=YkF1bzhyOVZYUmJQdlAxRnVPejhEdz09"
MEETING_LINK_1 = "zoommtg://zoom.us/join?confno=6474533966&pwd=YkF1bzhyOVZYUmJQdlAxRnVPejhEdz09"
MEETING_ID = "6474533966"
PWD = "YkF1bzhyOVZYUmJQdlAxRnVPejhEdz09"

ZOOM_EXE = "C:\\Users\\carol\\AppData\\Roaming\\Zoom\\bin\\Zoom.exe" # Change this later

JOIN_WAIT = 20

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2

try:
    pyautogui.useImageNotFoundException(False)
except Exception:
    pass

# Helper functions

def useZoomApp(timeout_s: float = 30.0) -> bool:
    start = time.time()
    while time.time() - start < timeout_s:
        candidates = (
            gw.getWindowsWithTitle("Zoom Meeting")
            + gw.getWindowsWithTitle("Meeting")
            + gw.getWindowsWithTitle("Zoom")
        )

        seen = set()
        uniq = []
        for w in candidates:
            if w._hWnd not in seen and w.title:
                seen.add(w._hWnd)
                uniq.append(w)

        for w in uniq:
            try:
                if w.isMinimized:
                    w.restore()
                w.activate()
                time.sleep(0.5)
                return True
            except Exception:
                pass

        time.sleep(0.5)

    return False

def hard_focus_zoom(timeout_s: float = 30.0) -> bool:
    start = time.time()
    while time.time() - start < timeout_s:
        if useZoomApp(timeout_s=2.0):
            time.sleep(0.2)
            active = gw.getActiveWindow()
            if active and ("zoom" in (active.title or "").lower()):
                return True
        time.sleep(0.3)
    return False

def get_zoom_window_rect():
    windows = gw.getWindowsWithTitle("Zoom")
    for w in windows:
        if w.title:
            if w.isMinimized:
                w.restore()
            return w.left, w.top, w.width, w.height
    raise RuntimeError("Zoom window not found")

def zoom_window_xy(rel_x_frac: float, rel_y_frac: float):
    left, top, width, height = get_zoom_window_rect()
    x = int(left + width * rel_x_frac)
    y = int(top + height * rel_y_frac)
    return x, y


# Main functions

def openZoom():
    subprocess.Popen([ZOOM_EXE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5)
    
    zoom_uri = (
        f"zoommtg://zoom.us/join?confno={MEETING_ID}&pwd={PWD}"
    )
    
    os.startfile(
        zoom_uri
    )

def cameraSettingNoBlur() -> None:
    if not hard_focus_zoom():
        raise RuntimeError("Could not focus Zoom window!")
    pyautogui.hotkey("alt", "v")
    
def screenShare(open_wait_s: float = 4) -> None:
    if not hard_focus_zoom():
        raise RuntimeError("Could not focus Zoom window!")
    
    pyautogui.hotkey("alt", "s")
    time.sleep(open_wait_s)
    
    pyautogui.press("enter")
    
def stop_sharing_screen() -> None:
    if not useZoomApp():
        raise RuntimeError("Could not focus Zoom window!")
    
    pyautogui.hotkey("alt", "s")
    
def cameraSettingWithBlur(
    right_click_x: int,
    right_click_y: int,
    down_presses: int = 3,
):
    if not hard_focus_zoom():
        raise RuntimeError("Could not focus Zoom window!")
    
    pyautogui.moveTo(right_click_x, right_click_y, duration=0.1)
    time.sleep(0.2)
    pyautogui.click(button="right")
    time.sleep(0.4)

    for _ in range(down_presses):
        pyautogui.press("down")
        time.sleep(0.1)

    pyautogui.press("enter")

def killZoom(wait_s: float = 2.0) -> None:
    subprocess.run(["taskkill", "/F", "/T", "/IM", "Zoom.exe"],
                   stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL,
                   check=False,
                   )
    
    time.sleep(wait_s)

# Testing it all out

print("Opening Zoom Meeting...")
openZoom()

print(f"Waiting {JOIN_WAIT} seconds for Zoom to launch/join...")
time.sleep(JOIN_WAIT)

print("Toggling camera...")
cameraSettingNoBlur()

print("Sharing screen...")
screenShare()

time.sleep(10)

print("Stop sharing screen...")
stop_sharing_screen()

time.sleep(3)

print("Toggling blurring of the background...")
x, y = zoom_window_xy(0.85, 0.20)
cameraSettingWithBlur(
    right_click_x=x,
    right_click_y=y,
    down_presses=3
)

time.sleep(5)

cameraSettingWithBlur(
    right_click_x=x,
    right_click_y=y,
    down_presses=3
)



print("Done!")

killZoom()

# To run, just type in terminal: python zoom.py