import time
import subprocess
import pyautogui
import pygetwindow as gw
# import os

# os.system('start "" "https://teams.microsoft.com/l/meetup-join/XXXX"')              

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2
iteration = 1

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


def switchMenu():
    # ctrl 1 and 2 to make it go to meet menu section in case of some issues
    pyautogui.hotkey("ctrl", "1")
    time.sleep(1)
    pyautogui.hotkey("ctrl", "2")
    time.sleep(1)

# ensures teams is hard closed so when we open it everything is reset to default settings
def killTeams():
    subprocess.run(
        ["taskkill", "/F", "/IM", "ms-teams.exe", "/T"],
        shell=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["taskkill", "/F", "/IM", "Teams.exe", "/T"],
        shell=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("Teams killed")

def cameraSettingWithBlur():
    # open camera and blur 
    pyautogui.hotkey("ctrl", "shift", "o")
    pyautogui.press("right", presses=1, interval=0.8)
    pyautogui.press("enter")
    time.sleep(1)

    pyautogui.press("enter")
    pyautogui.press("right", presses=1, interval=0.8)
    pyautogui.press("enter")
    time.sleep(1)

    pyautogui.press("esc", interval=0.8)

    pyautogui.press("tab", presses=11, interval=0.4)
    pyautogui.press("enter")

def cameraSettingNoBlur():
    # open camera and have no blur
    pyautogui.hotkey("ctrl", "shift", "o")
    pyautogui.press("right", presses=1, interval=0.8)
    pyautogui.press("enter")
    time.sleep(1)

    pyautogui.press("enter")
    time.sleep(1)

    pyautogui.press("esc", interval=0.8)

    pyautogui.press("tab", presses=11, interval=0.4)
    pyautogui.press("enter")

def noCameraSetting():
    # camera auto off 
    pyautogui.press("tab", presses=7, interval=0.4)
    pyautogui.press("enter")
    time.sleep(30)  
    pyautogui.hotkey("ctrl", "shift", "o")

def noCameraSetting2():
    # camera auto off 
    pyautogui.press("tab", presses=7, interval=0.4)
    pyautogui.press("enter")


def cameraopencommand():
    pyautogui.hotkey("ctrl", "shift", "o")


def screenShare():
    # screen share
    pyautogui.hotkey("ctrl", "shift", "e")  
    pyautogui.press("tab", presses=3, interval=0.8)
    pyautogui.press("enter")        


def turnOnBlurinMeeting():
    time.sleep(3)
    pyautogui.press("left")
    pyautogui.press("enter")
    pyautogui.press("tab")
    pyautogui.press("right")
    pyautogui.press("enter")
    pyautogui.press("esc")


# select the options cameraBlur, cameraNoblur and camerano
def optionSelect():
    # cameraSettingWithBlur()
    # cameraSettingNoBlur()
    noCameraSetting()


def navigateToMeet():
    switchMenu()

    # navigate to the join meet 
    pyautogui.press("tab", presses=4, interval=0.4)
    pyautogui.press("right", presses=2, interval=0.4)
    pyautogui.press("enter")
    time.sleep(2)



def experimentation():

    for i in range(iteration):
        print(f"\nIteration {i + 1}")

        openMicroTeams()
        time.sleep(9)

        useMicroTeamsApp()

        navigateToMeet()

        time.sleep(5)
        killTeams()  
        time.sleep(5)

    print("made it till here")


# experimentation()
