import os
import time
import random
import subprocess
import microsoftteams as teams
import zoom as zoomapp
from tqdm import tqdm


# Experiment parameters
ITERATIONS_PER_TASK = 30

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

RESULTS_DIR = "results"
ENERGIBRIDGE = "C:/code/EnergiBridge/target/release/energibridge.exe"  # full path if not on PATH, e.g. r"C:\tools\energibridge.exe"

def run_energibridge(app: str, test: str, iteration: int, duration_s: int = 30):
    """Wrap `timeout /t <duration_s>` with EnergiBridge.
    Output: results/<app>_<test>_<iteration>.csv  e.g. teams_camera_off_1.csv
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)
    label = f"{app}_{test}_{iteration}"
    out = os.path.join(RESULTS_DIR, f"{label}.csv")
    print(f"  [EnergiBridge] measuring '{label}' for {duration_s}s -> {out}")
    subprocess.run(
        [
            ENERGIBRIDGE,
            "--output", out,
            "--summary",
            "--",
            "timeout", "/t", str(duration_s), "/nobreak",
        ],
        check=False,
    )
    print(f"  [EnergiBridge] done.")


def print_counters():
    print("\nProgress counters:")
    for task in TASKS:
        print(f"  {task}: Teams={counters[task]['teams']}  Zoom={counters[task]['zoom']}")
    print()

def run_camera_on_off(app, iteration):
    print(f"\n[{app.upper()}] Running camera ON/OFF test...")
    if app == "teams":
        teams.openMicroTeams()
        time.sleep(5)
        teams.useMicroTeamsApp()
        teams.switchMenu()
        time.sleep(2)
        teams.navigateToMeet()
        print("Camera OFF (recording)")
        teams.noCameraSetting()
        run_energibridge(app, "camera_off", iteration)
        print("Camera ON (recording)")
        teams.cameraopencommand()
        run_energibridge(app, "camera_on", iteration)
        teams.killTeams()
    else:
        zoomapp.openZoom()
        time.sleep(zoomapp.JOIN_WAIT)
        print("Camera OFF (recording)")
        run_energibridge(app, "camera_off", iteration)
        print("Camera ON (recording)")
        zoomapp.cameraSettingNoBlur()
        run_energibridge(app, "camera_on", iteration)
        zoomapp.killZoom()

def run_blur_no_blur(app, iteration):
    print(f"\n[{app.upper()}] Running BLUR/NO BLUR test...")
    if app == "teams":
        teams.openMicroTeams()
        time.sleep(5)
        teams.useMicroTeamsApp()
        teams.switchMenu()
        teams.navigateToMeet()
        teams.noCameraSetting()
        print("No Blur (recording)")
        teams.camOnBlurOff()
        run_energibridge(app, "noblur", iteration)
        print("Blur (recording)")
        teams.turnOnBlurinMeeting()
        run_energibridge(app, "blur", iteration)
        teams.turnOffBlurinMeeting()
        teams.killTeams()
    else:
        zoomapp.openZoom()
        time.sleep(zoomapp.JOIN_WAIT)
        print("No Blur (recording)")
        zoomapp.cameraSettingNoBlur()
        run_energibridge(app, "noblur", iteration)
        print("Blur (recording)")
        x, y = zoomapp.zoom_window_xy(0.85, 0.20)
        zoomapp.cameraSettingWithBlur(x, y, down_presses=3)
        run_energibridge(app, "blur", iteration)
        time.sleep(5)
        zoomapp.cameraSettingWithBlur(x, y, down_presses=3)
        zoomapp.killZoom()

def run_screen_share(app, iteration):
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
        run_energibridge(app, "noshare", iteration)
        print("Screen Sharing (recording)")
        teams.screenShare()
        run_energibridge(app, "share", iteration)
        teams.killTeams()
    else:
        zoomapp.openZoom()
        time.sleep(zoomapp.JOIN_WAIT)
        print("No Screen Share (recording)")
        run_energibridge(app, "noshare", iteration)
        print("Screen Sharing (recording)")
        zoomapp.screenShare()
        run_energibridge(app, "share", iteration)
        zoomapp.stop_sharing_screen()
        zoomapp.killZoom()

def main():
    print("=== Automated Teams/Zoom Energy Experiment ===\n")
    fibonacci_warmup(300) # 5 minute warmup
    for task in TASKS:
        print(f"\n--- Starting task: {task} ---")
        pool = ["teams"] * ITERATIONS_PER_TASK + ["zoom"] * ITERATIONS_PER_TASK
        random.shuffle(pool)
        for i, app in enumerate(pool):
            print(f"\nIteration {i+1}/{len(pool)} for {task}: {app.upper()}")
            try:
                iteration = counters[task][app] + 1
                if task == "camera_on_off":
                    run_camera_on_off(app, iteration)
                elif task == "blur_no_blur":
                    run_blur_no_blur(app, iteration)
                elif task == "screen_share":
                    run_screen_share(app, iteration)
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