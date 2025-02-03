import cv2
import numpy as np
import mediapipe as mp

from datetime import datetime

import config_utils

config = config_utils.read_config('./config.json')

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
	max_num_hands=1, 
	min_detection_confidence=0.5, 
	min_tracking_confidence=0.5
)

mp_drawing = mp.solutions.drawing_utils

# Create a blank canvas
color_idx = 0
brush_color = config['brush_color'][0]
brush_thickness = config['brush_thickness']
current_action = "Idle"
canvas = config_utils.create_canvas(config)

# Function to recognize gestures
def recognize_gesture(landmarks):
	fingers = []
	for i in [8, 12, 16, 20]:  # Check tips of fingers
		if landmarks[i].y < landmarks[i - 2].y:  # Tip above PIP joint
			fingers.append(1)
		else:
			fingers.append(0)

	thumb = landmarks[4].x < landmarks[3].x  # Thumb extended
	return fingers, thumb

# Main function
cap = cv2.VideoCapture(0)
drawing = False
while cap.isOpened():
	ret, frame = cap.read()
	if not ret:
		break
	
	frame = cv2.flip(frame, 1)  # Flip for mirror effect
	h, w, _ = frame.shape
	rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	result = hands.process(rgb_frame)

	if result.multi_hand_landmarks:
		for hand_landmarks in result.multi_hand_landmarks:
			mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
			landmarks = hand_landmarks.landmark
			fingers, thumb = recognize_gesture(landmarks)
			
			print(sum(fingers))
			print(f'Fingers: {fingers}, Thumb: {thumb}')

			if fingers == [1, 0, 0, 0] and not thumb:  # Pointing Finger: Draw
				current_action = "Idle"
				drawing = False
				
			elif fingers == [1, 0, 0, 0] and thumb and not drawing:  # Pointing Finger: Draw
				current_action = "Drawing"
				drawing = True
				
			elif fingers == [1, 1, 0, 0]:  # Two Fingers: Change brush color
				current_action = "Changing Brush Color"
				color_idx = (color_idx + 1) % len(config['brush_color'])
				brush_color = config['brush_color'][color_idx]
				
			elif sum(fingers) == 3:  # Fist: Clear the screen
				current_action = "Clearing Screen"
				canvas = config_utils.create_canvas(config)
				
			elif thumb and sum(fingers) == 4:  # Thumbs Up: Save drawing
				current_action = "Saving Drawing"
				filename = f"drawing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
				cv2.imwrite(filename, canvas)
				print(f"Saved drawing as {filename}")
				
			else:
				current_action = "Idle"

			if drawing:
				x, y = int(landmarks[8].x * w), int(landmarks[8].y * h)
				cv2.circle(canvas, (x, y), brush_thickness, brush_color, -1)

	output = cv2.addWeighted(frame, 0.5, canvas, 0.5, 0)

	cv2.putText(output, f"Action: {current_action}", (10, 50), 
				cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

	cv2.imshow("Camera", output)
	
	if cv2.waitKey(1) & 0xFF == 27:
		break

cap.release()
cv2.destroyAllWindows()
