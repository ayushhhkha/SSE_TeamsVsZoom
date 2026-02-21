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
CONFIDENCE = 0.85
SEARCH_TIMEOUT = 20

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2

try:
    pyautogui.useImageNotFoundException(False)
except Exception:
    pass

# Functions for later!

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

def get_primary_monitor_region() -> Tuple[int, int, int, int]:
    with mss.mss() as sct:
        mon = sct.monitors[1]
        return (mon["left"], mon["top"], mon["width"], mon["height"])
    
def open_meeting_link(meeting_link: str) -> None:
    webbrowser.open(meeting_link)
    
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
            return loc
        
        time.sleep(0.5)
        
    return None

def toggle_camera() -> None:
    pyautogui.hotkey("alt", "v")
    
def share_primary_screen(open_wait_s: float = 4) -> None:
    if not focus_zoom_window():
        raise RuntimeError("Could not focus Zoom window!")
    
    pyautogui.hotkey("alt", "s")
    time.sleep(open_wait_s)
    
    pyautogui.press("enter")
    
def stop_sharing_screen() -> None:
    if not focus_zoom_window():
        raise RuntimeError("Could not focus Zoom window!")
    
    pyautogui.hotkey("alt", "s")
    
    
# Testing it all out

print("Opening Zoom Meeting...")
webbrowser.open(MEETING_LINK)

print(f"Waiting {JOIN_WAIT} seconds for Zoom to launch/join...")
time.sleep(JOIN_WAIT)

print("Focusing Zoom window...")
focused = focus_zoom_window()
print("Focused: ", focused)

time.sleep(1)

print("Toggling camera!")
toggle_camera()

share_primary_screen()

time.sleep(10)

stop_sharing_screen()


print("Done! Zoom should now be in a meeting!")

# To run, just type in terminal: python zoom.py