import math
import cv2
import time
import numpy as np
import handtracker as htm
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Width and Height of Camera
wCam, hCam = 640, 480

# Camera and Variables Initialization
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(detectionCon=0.8)
prevTime = 0

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

while True:
    success, img = cap.read()

    # Find Hands and its co-ordinates
    img = detector.findHand(img)
    lmList = detector.findPosition(img, draw=False)

    # Selecting only thumb and index finger landmarks
    if len(lmList) != 0:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 12, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 12, (255, 0, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 12, (255, 0, 0), cv2.FILLED)

        # Volume and Line Range Adjustment
        length = math.hypot(x2 - x1, y2 - y1)
        vol = np.interp(length, [20, 140], [minVol, maxVol])
        volume.SetMasterVolumeLevel(vol, None)

        # Draw volume bar rectangle
        bar_width = 15
        bar_height = int(np.interp(length, [20, 140], [0, 100]))
        cv2.rectangle(img, (50, 450), (50 + bar_width, 450 - bar_height), (0, 255, 0), cv2.FILLED)  # Volume bar

        # Display volume percentage
        vol_percentage = int(np.interp(length, [20, 140], [0, 100]))
        cv2.putText(img, f"{vol_percentage}%", (50 + bar_width + 10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

        if length <= 20:
            cv2.circle(img, (cx, cy), 12, (0, 255, 0), cv2.FILLED)

    # Calculate FPS and Display it
    currentTime = time.time()
    fps = 1 / (currentTime - prevTime)
    prevTime = currentTime
    fps_text = f"FPS: {int(fps)}"
    cv2.putText(img, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

    # Display the main image
    cv2.imshow("Img", img)

    # Add a delay to limit the frame rate to a reasonable value (e.g., 30 fps)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
