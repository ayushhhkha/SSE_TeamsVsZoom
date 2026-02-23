import csv
import os
import time
import webbrowser
from datetime import datetime
import subprocess


import pyautogui
import mss
import pygetwindow as gw

from typing import Optional, Tuple

# Configurations

MEETING_LINK = "https://us05web.zoom.us/j/6474533966?pwd=YkF1bzhyOVZYUmJQdlAxRnVPejhEdz09"
MEETING_LINK_1 = "zoommtg://zoom.us/join?confno=6474533966&pwd=YkF1bzhyOVZYUmJQdlAxRnVPejhEdz09"
MEETING_ID = "6474533966"
PWD = "YkF1bzhyOVZYUmJQdlAxRnVPejhEdz09"

ZOOM_EXE = "C:\\Users\\carol\\AppData\\Roaming\\Zoom\\bin\\Zoom.exe"

JOIN_WAIT = 10
CONFIDENCE = 0.70
SEARCH_TIMEOUT = 20

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2

try:
    pyautogui.useImageNotFoundException(False)
except Exception:
    pass

# Helper functions

def focus_zoom_window(timeout_s: float = 30.0) -> bool:
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
        if focus_zoom_window(timeout_s=2.0):
            time.sleep(0.2)
            active = gw.getActiveWindow()
            if active and ("zoom" in (active.title or "").lower()):
                return True
        time.sleep(0.3)
    return False

# Cause I'm working on two screens
def get_primary_monitor_region() -> Tuple[int, int, int, int]:
    with mss.mss() as sct:
        mon = sct.monitors[1]
        return (mon["left"], mon["top"], mon["width"], mon["height"])
    
def primary_xy(rel_x: int, rel_y: int) -> tuple[int, int]:
    left, top, _, _ = get_primary_monitor_region()
    return left + rel_x, top + rel_y

def find_on_primary_screen_center(
    image_path:str, 
    confidence: float = 0.85, 
    timeout_s: float = 25.0, 
    region: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[pyautogui.Point]:
    
    if region is None:
        region = get_primary_monitor_region()
    
    start = time.time()
    while time.time() - start < timeout_s:
        try:
            loc = pyautogui.locateCenterOnScreen(image_path, confidence=confidence, region=region)
        except Exception:
            loc = None
        
        if loc:
            pyautogui.moveTo(loc.x, loc.y, duration=0.1)
            pyautogui.click()
            return True
        
        time.sleep(0.5)
        
    return None

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

def open_meeting_link(meeting_link: str) -> None:
    webbrowser.open(meeting_link)

def open_zoom_meeting():
    subprocess.Popen([ZOOM_EXE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5)
    
    zoom_uri = (
        f"zoommtg://zoom.us/join?confno={MEETING_ID}&pwd={PWD}"
    )
    
    os.startfile(
        zoom_uri
    )

def toggle_camera() -> None:
    if not hard_focus_zoom():
        raise RuntimeError("Could not focus Zoom window!")
    pyautogui.hotkey("alt", "v")
    
def share_primary_screen(open_wait_s: float = 4) -> None:
    if not hard_focus_zoom():
        raise RuntimeError("Could not focus Zoom window!")
    
    pyautogui.hotkey("alt", "s")
    time.sleep(open_wait_s)
    
    pyautogui.press("enter")
    
def stop_sharing_screen() -> None:
    if not focus_zoom_window():
        raise RuntimeError("Could not focus Zoom window!")
    
    pyautogui.hotkey("alt", "s")
    
def toggle_blur_via_keyboard(
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

def hard_close_zoom(wait_s: float = 2.0) -> None:
    subprocess.run(["taskkill", "/F", "/T", "/IM", "Zoom.exe"],
                   stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL,
                   check=False,
                   )
    
    time.sleep(wait_s)

# Testing it all out

print("Opening Zoom Meeting...")
# webbrowser.open(MEETING_LINK)
open_zoom_meeting()

print(f"Waiting {JOIN_WAIT} seconds for Zoom to launch/join...")
time.sleep(JOIN_WAIT)

print("Focusing Zoom window...")
focused = focus_zoom_window()
print("Focused: ", focused)

time.sleep(1)

print("Toggling camera...")
toggle_camera()

print("Sharing screen...")
share_primary_screen()

time.sleep(10)

print("Stop sharing screen...")
stop_sharing_screen()

time.sleep(3)

print("Toggling blurring of the background...")
x, y = zoom_window_xy(0.85, 0.20)
toggle_blur_via_keyboard(
    right_click_x=x,
    right_click_y=y,
    down_presses=3
)

time.sleep(5)

toggle_blur_via_keyboard(
    right_click_x=x,
    right_click_y=y,
    down_presses=3
)



print("Done!")

hard_close_zoom()

# To run, just type in terminal: python zoom.py