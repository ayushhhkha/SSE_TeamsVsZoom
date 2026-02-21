import time
import subprocess
import pyautogui
import pygetwindow as gw

pyautogui.FAILSAFE = True
iteration = 2

# need this to open the app
def openMicroTeams():
    subprocess.Popen("start ms-teams:", shell=True)
    print("im open")

#this just ensures that the automation works on the app and not like random places 
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

# this only works when u start from beginning the app and already have a link open for the meet 
# and also when the video is off

# first time open the camera and enable blur
def firstJoin():
    # open camera settings
    pyautogui.hotkey("ctrl", "shift", "o")
    pyautogui.press("right", presses=1, interval=0.8)
    pyautogui.press("enter")
    time.sleep(1)

    pyautogui.press("enter")
    pyautogui.press("right", presses=1, interval=0.8)
    pyautogui.press("enter")
    time.sleep(1)

    pyautogui.press("esc", interval=0.8)

    # go to Join now
    pyautogui.press("tab", presses=11, interval=0.4)
    pyautogui.press("enter")

#second time the camera is auto open 
def extraJoin():
    time.sleep(1)
    pyautogui.press("tab", presses=7, interval=0.4)
    pyautogui.press("enter")


def navigateToMeet(firstTime):
    # ctrl 1 and 2 to make it go to meet menu section in case of some issues
    pyautogui.hotkey("ctrl", "1")
    time.sleep(1)
    pyautogui.hotkey("ctrl", "2")
    time.sleep(1)

    # navigate to the join meet 
    pyautogui.press("tab", presses=4, interval=0.4)
    pyautogui.press("right", presses=2, interval=0.4)
    pyautogui.press("enter")
    time.sleep(2)

    #pre join menu 
    if firstTime:
        firstJoin()
    else:
        extraJoin()

    # screen share
    time.sleep(2)
    pyautogui.hotkey("ctrl", "shift", "e")  
    time.sleep(1)
    pyautogui.press("tab", presses=3, interval=0.8)
    pyautogui.press("enter")

    # how long the screen share will be (for now put it 10 sec for testing)
    time.sleep(10)

    # leave meeting
    pyautogui.hotkey("ctrl", "shift", "e")
    time.sleep(1)
    pyautogui.hotkey("ctrl", "shift", "h")


def experimentation():

    openMicroTeams()
    time.sleep(5)

    for i in range(iteration):
        print(f"\nIteration {i + 1}")

        useMicroTeamsApp()

        firstTime = (i == 0)
        navigateToMeet(firstTime)

        time.sleep(5)

    print("made it till here")


experimentation()