import pygame
import os
import cv2
import numpy as np

# Initialize pygame mixer
pygame.init()
pygame.mixer.init()

# Load sounds
sounds = []
sound_files = ['DO.wav', 'RE.wav', 'ME.wav', 'FA.wav', 'SON.wav', 'RA.wav', 'T.wav']
sound_folder = "."  # Folder where the sound files are stored

for sound_file in sound_files:
    sound_path = os.path.join(sound_folder, sound_file)
    if os.path.exists(sound_path):
        sounds.append(pygame.mixer.Sound(sound_path))
    else:
        sounds.append(None)  # Append None if file not found

# Define color ranges in HSV
color_ranges = {
    "red": [(0, 50, 50), (10, 255, 255)],
    "orange": [(11, 50, 50), (25, 255, 255)],
    "yellow": [(26, 50, 50), (35, 255, 255)],
    "green": [(36, 50, 50), (85, 255, 255)],
    "blue": [(86, 50, 50), (125, 255, 255)],
    "indigo": [(126, 50, 50), (140, 255, 255)],
    "pink": [(141, 50, 50), (170, 255, 255)],
}

# Map colors to sound indices
color_to_sound = {
    "red": 0,
    "orange": 1,
    "yellow": 2,
    "green": 3,
    "blue": 4,
    "indigo": 5,
    "pink": 6,
}

# Recordings storage
recordings = {}
current_recording = []
recording_mode = False
naming_mode = False
recording_name = ""

# Function to detect color
def detect_color(hsv_frame, x, y):
    for color, (lower, upper) in color_ranges.items():
        mask = cv2.inRange(hsv_frame, np.array(lower), np.array(upper))
        if mask[y, x]:
            return color
    return None

# Function to play sound by color
def play_sound_by_color(color):
    if color in color_to_sound:
        sound_index = color_to_sound[color]
        sound = sounds[sound_index]
        if sound:
            sound.play()

# Function to play a recording
def play_recording(recording_name):
    if recording_name in recordings:
        for color in recordings[recording_name]:
            play_sound_by_color(color)

# Adjust brightness and contrast using CLAHE
def adjust_brightness_contrast(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

# Draw buttons on the frame
def draw_buttons(frame):
    height, width, _ = frame.shape
    button_width = 150
    button_height = 50

    # Define button positions
    record_button = (10, height - 60, button_width, button_height)
    stop_button = (170, height - 60, button_width, button_height)

    # Draw buttons
    cv2.rectangle(frame, (record_button[0], record_button[1]),
                  (record_button[0] + record_button[2], record_button[1] + record_button[3]), (0, 255, 0), -1)
    cv2.putText(frame, "Record", (record_button[0] + 10, record_button[1] + 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.rectangle(frame, (stop_button[0], stop_button[1]),
                  (stop_button[0] + stop_button[2], stop_button[1] + stop_button[3]), (0, 0, 255), -1)
    cv2.putText(frame, "Stop", (stop_button[0] + 30, stop_button[1] + 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    return record_button, stop_button

# Draw recording list on the frame
def draw_recording_list(frame):
    height, width, _ = frame.shape
    y_offset = 20
    for idx, name in enumerate(recordings.keys()):
        y_position = y_offset + idx * 30
        cv2.putText(frame, name, (width - 200, y_position),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
    return width - 200, y_offset, 200, len(recordings) * 30

# Start capturing from webcam
cap = cv2.VideoCapture(1)  # Change to 0 for the default webcam
x_position = 0  # Initial position of scanning line
playback_speed = 2  # Default scanning speed

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Adjust brightness and contrast
    frame = adjust_brightness_contrast(frame)

    # Convert frame to HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define y-position of scanning line
    line_y = frame.shape[0] // 2

    # Detect color at scanning line position
    color_detected = detect_color(hsv_frame, x_position, line_y)

    # Add detected color to the current recording if in recording mode
    if color_detected:
        if recording_mode:
            current_recording.append(color_detected)
        play_sound_by_color(color_detected)

    # Display scanning line
    cv2.line(frame, (x_position, 0), (x_position, frame.shape[0]), (255, 255, 255), 2)

    # Display detected color text
    if color_detected:
        cv2.putText(frame, f"Detected Color: {color_detected}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Show playback speed
    cv2.putText(frame, f"Speed: {playback_speed}x", (10, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show naming prompt if in naming mode
    if naming_mode:
        cv2.putText(frame, f"Enter name: {recording_name}_", (10, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    # Draw buttons and get their positions
    record_button, stop_button = draw_buttons(frame)
    recording_list_area = draw_recording_list(frame)

    # Show the frame
    cv2.imshow("Color Detection and Sound", frame)

    # Update scanning line position
    x_position += playback_speed
    if x_position >= frame.shape[1]:  # Reset to the left side if it reaches the right
        x_position = 0

    # Handle mouse input for button clicks
    def on_mouse(event, x, y, flags, param):
        global recording_mode, naming_mode, recording_name
        if event == cv2.EVENT_LBUTTONDOWN:
            if record_button[0] <= x <= record_button[0] + record_button[2] and record_button[1] <= y <= record_button[1] + record_button[3]:
                recording_mode = True
                naming_mode = False
                current_recording.clear()
                print("Recording started...")
            elif stop_button[0] <= x <= stop_button[0] + stop_button[2] and stop_button[1] <= y <= stop_button[1] + stop_button[3]:
                recording_mode = False
                if current_recording:
                    naming_mode = True
                    print("Recording stopped. Enter name in the video window.")
            # Check if a recording name is clicked
            else:
                list_x, list_y, list_width, list_height = recording_list_area
                if list_x <= x <= list_x + list_width and list_y <= y <= list_y + list_height:
                    idx = (y - list_y) // 30
                    if 0 <= idx < len(recordings):
                        name = list(recordings.keys())[idx]
                        print(f"Playing recording: {name}")
                        play_recording(name)

    cv2.setMouseCallback("Color Detection and Sound", on_mouse)

    # Handle keyboard input
    key = cv2.waitKey(1) & 0xFF
    if naming_mode:
        if key == 13:  # Enter key
            if recording_name.strip():
                recordings[recording_name.strip()] = current_recording.copy()
                print(f"Recording saved as '{recording_name.strip()}'.")
                current_recording.clear()
                recording_name = ""
                naming_mode = False
        elif key == 8:  # Backspace
            recording_name = recording_name[:-1]
        elif key != 255:  # Other keys
            recording_name += chr(key)

    if key == ord('q'):  # Quit on 'q' key
        break

cap.release()
cv2.destroyAllWindows()



