import time
import subprocess
import pyautogui
import pygetwindow as gw

pyautogui.FAILSAFE = True


def openMicroTeams():
    subprocess.Popen("start ms-teams:", shell=True)
    print("im open")


def useMicroTeamsApp():

    for _ in range(60):
        winsobj = gw.getWindowsWithTitle("Microsoft Teams")
        if winsobj:
            win = winsobj[0]

            if win.isMinimized:
                win.restore()
                time.sleep(0.5)

            x, y = win.center
            pyautogui.click(x, y)

            time.sleep(0.5)
            return

        time.sleep(0.5)


def navigateToMeet():
    pyautogui.hotkey("ctrl", "1")
    time.sleep(1)

    pyautogui.hotkey("ctrl", "2")
    time.sleep(1)

    pyautogui.press("tab", presses=4, interval=0.4)
    pyautogui.press("right", presses=2, interval=0.4)
    pyautogui.press("enter")
    pyautogui.press("tab", presses=8, interval=0.4)
    pyautogui.press("enter")

    time.sleep(2)
    pyautogui.hotkey("ctrl", "shift", "o")
    pyautogui.hotkey("ctrl", "shift", "e")

    pyautogui.press("tab", presses=3, interval=0.8)
    pyautogui.press("enter")
    # pyautogui.press("enter")
    time.sleep(10)

    pyautogui.hotkey("ctrl", "shift", "e")
    time.sleep(1)
    pyautogui.hotkey("ctrl", "shift", "H")

openMicroTeams()
time.sleep(1)
useMicroTeamsApp()
navigateToMeet()

print("made it till here")

