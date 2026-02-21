import csv
import os
import time
import webbrowser
from datetime import datetime

import pyautogui
import mss
import pygetwindow as gw

from typing import Optional, Tuple

# Configurations

MEETING_LINK = "https://us05web.zoom.us/j/6474533966?pwd=YkF1bzhyOVZYUmJQdlAxRnVPejhEdz09"

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


# Main functions

def open_meeting_link(meeting_link: str) -> None:
    webbrowser.open(meeting_link)
    
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


# Testing it all out

print("Opening Zoom Meeting...")
webbrowser.open(MEETING_LINK)

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
x, y = primary_xy(300, 300)
toggle_blur_via_keyboard(
    right_click_x=x,
    right_click_y=y,
    down_presses=3
)



print("Done!")

# To run, just type in terminal: python zoom.py