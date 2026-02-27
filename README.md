# Sustainable Software Engineering: Comparison of the Microsoft Team and Zoom Application

## Introduction

This repository contains an automation of measure the energy Microsoft Team and Zoom use based on variables such as using video, background blurring and screen sharing.

## Setup and Usage

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set up the script prerequisites:

- Open Microsoft Teams using a personal account

- Navigate to _Meet_ -> _Create a meeting link_

- Open Zoom meeting

- Create a new meeting

- Open _zoom.py_ script and replace the existing ``MEETING_ID`` and ``PWD`` values to corresponding meeting information

- Update ``ZOOM_EXE`` variable with an accurate path to the _zoom.exe_ file on local machine

- Ensure all settings are set to default. The camera should be off and blurring should be disabled.
  
-  Force shut down both applications.

-  Ensure the location of EnergiBridge is updated in the main.py based on the users computer location.
  
-  Ensure it is in zen mode: 100% brightness, 30% volume, wireless connection, all non-essential applications are stopped, the device notification should be turned off and the laptop should be plugged in.


2. Run the automation script:

   ```bash
   python main.py
   ```

3. Run the Energy Analysis Script:

    ```bash
   python energy_analysis.py
   ```
   

