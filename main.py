import time
import random
import subprocess
import microsoftteams as teams
import zoom as zoomapp
from tqdm import tqdm


# Experiment parameters
ITERATIONS_PER_TASK = 15

# Task definitions
TASKS = [
    "camera_on_off",
    "blur_no_blur",
    "screen_share"
]

# Counters
counters = {
    "camera_on_off": {"teams": 0, "zoom": 0},
    "blur_no_blur": {"teams": 0, "zoom": 0},
    "screen_share": {"teams": 0, "zoom": 0},
}

def fibonacci_warmup(duration_s):       
    print(f"Warming up CPU with Fibonacci for {duration_s//60} minutes...")
    a, b = 0, 1
    for _ in tqdm(range(int(duration_s)), desc="Warmup", ncols=60):
        loop_start = time.time()
        while time.time() - loop_start < 1:
            a, b = b, a + b
            if b > 1e10:
                a, b = 0, 1
    print("Warmup complete.\n")

# def start_energibridge():


# def stop_energibridge():


def print_counters():
    print("\nProgress counters:")
    for task in TASKS:
        print(f"  {task}: Teams={counters[task]['teams']}  Zoom={counters[task]['zoom']}")
    print()

def run_camera_on_off(app):
    print(f"\n[{app.upper()}] Running camera ON/OFF test...")
    if app == "teams":
        teams.openMicroTeams()
        time.sleep(5)
        teams.useMicroTeamsApp()
        teams.switchMenu()
        time.sleep(2)
        teams.navigateToMeet()
        teams.noCameraSetting()
        print("Camera OFF (recording)")
        # start_energibridge()
        time.sleep(30)
        # stop_energibridge()
        print("Camera ON (recording)")
        teams.cameraopencommand()
        # start_energibridge()
        time.sleep(30)
        # stop_energibridge()
        teams.killTeams()
    else:
        zoomapp.openZoom()
        time.sleep(zoomapp.JOIN_WAIT)
        print("Camera OFF (recording)")
        # start_energibridge()
        time.sleep(30)
        # stop_energibridge()
        print("Camera ON (recording)")
        zoomapp.cameraSettingNoBlur()
        # start_energibridge()
        time.sleep(30)
        # stop_energibridge()
        zoomapp.killZoom()

def run_blur_no_blur(app):
    print(f"\n[{app.upper()}] Running BLUR/NO BLUR test...")
    if app == "teams":
        teams.openMicroTeams()
        time.sleep(5)
        teams.useMicroTeamsApp()
        teams.switchMenu()
        teams.navigateToMeet()
        print("No Blur (recording)")
        teams.cameraSettingNoBlur()
        # start_energibridge()
        time.sleep(30)
        # stop_energibridge()
        print("Blur (recording)")
        teams.turnOnBlurinMeeting()
        # start_energibridge()
        time.sleep(30)
        # stop_energibridge()
        teams.killTeams()
    else:
        zoomapp.openZoom()
        time.sleep(zoomapp.JOIN_WAIT)
        print("No Blur (recording)")
        zoomapp.cameraSettingNoBlur()
        # start_energibridge()
        time.sleep(30)
        # stop_energibridge()
        print("Blur (recording)")
        x, y = zoomapp.zoom_window_xy(0.85, 0.20)
        zoomapp.cameraSettingWithBlur(x, y, down_presses=3)
        # start_energibridge()
        time.sleep(30)
        # stop_energibridge()
        zoomapp.killZoom()

def run_screen_share(app):
    print(f"\n[{app.upper()}] Running SCREEN SHARE test...")
    if app == "teams":
        teams.openMicroTeams()
        time.sleep(5)
        teams.useMicroTeamsApp()
        time.sleep(5)
        teams.switchMenu()
        time.sleep(5)
        teams.navigateToMeet()
        teams.noCameraSetting2()
        print("No Screen Share (recording)")
        # start_energibridge()
        time.sleep(30)
        # stop_energibridge()
        print("Screen Sharing (recording)")
        teams.screenShare()
        # start_energibridge()
        time.sleep(30)
        # stop_energibridge()
        teams.killTeams()
    else:
        zoomapp.openZoom()
        time.sleep(zoomapp.JOIN_WAIT)
        print("No Screen Share (recording)")
        # start_energibridge()
        time.sleep(30)
        # stop_energibridge()
        print("Screen Sharing (recording)")
        zoomapp.screenShare()
        # start_energibridge()
        time.sleep(30)
        # stop_energibridge()
        zoomapp.stop_sharing_screen()
        zoomapp.killZoom()

def main():
    print("=== Automated Teams/Zoom Energy Experiment ===\n")
    fibonacci_warmup(300) # 5 minute warmup
    for task in TASKS:
        print(f"\n--- Starting task: {task} ---")
        for i in range(ITERATIONS_PER_TASK * 2):
            available = [app for app in ["teams", "zoom"] if counters[task][app] < ITERATIONS_PER_TASK]
            if not available:
                break
            app = random.choice(available)
            print(f"\nIteration {i+1} for {task}: {app.upper()}")
            try:
                if task == "camera_on_off":
                    run_camera_on_off(app)
                elif task == "blur_no_blur":
                    run_blur_no_blur(app)
                elif task == "screen_share":
                    run_screen_share(app)
                else:
                    print(f"Unknown task: {task}")
                    continue
                counters[task][app] += 1
                print_counters()
            except Exception as e:
                print(f"[ERROR] {e}")
                try:
                    teams.killTeams()
                except Exception:
                    pass
                try:
                    zoomapp.killZoom()
                except Exception:
                    pass
                time.sleep(5)
            print("Cooldown: waiting 1 minute before next iteration...")
            time.sleep(60)
    print("\n=== Experiment complete! ===")
    print_counters()

if __name__ == "__main__":
    main()