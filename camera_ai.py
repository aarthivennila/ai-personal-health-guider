import cv2
import mediapipe as mp
import numpy as np
import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("health_data.json")

# Create JSON if not exists
if not DATA_FILE.exists():
    with open(DATA_FILE, "w") as f:
        json.dump({"history": []}, f, indent=4)

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    angle = np.abs(
        np.arctan2(c[1]-b[1], c[0]-b[0]) -
        np.arctan2(a[1]-b[1], a[0]-b[0])
    ) * 180.0 / np.pi
    return 360-angle if angle > 180 else angle

cap = cv2.VideoCapture(0)
counter = 0
stage = None

with mp_pose.Pose() as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        try:
            lm = result.pose_landmarks.landmark
            shoulder = [lm[11].x, lm[11].y]
            elbow = [lm[13].x, lm[13].y]
            wrist = [lm[15].x, lm[15].y]

            angle = calculate_angle(shoulder, elbow, wrist)

            if angle > 160:
                stage = "up"
            if angle < 90 and stage == "up":
                stage = "down"
                counter += 1

        except:
            pass

        cv2.putText(img, f"REPS: {counter}", (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 3)

        mp_draw.draw_landmarks(img, result.pose_landmarks,
                               mp_pose.POSE_CONNECTIONS)

        cv2.imshow("Camera Workout AI", img)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

# Save workout to JSON
with open(DATA_FILE, "r") as f:
    data = json.load(f)

data["history"].append({
    "date": datetime.now().isoformat(),
    "exercise": "Push Ups",
    "reps": counter,
    "form_score": min(100, counter * 5)
})

with open(DATA_FILE, "w") as f:
    json.dump(data, f, indent=4)

print("Workout saved to health_data.json")
