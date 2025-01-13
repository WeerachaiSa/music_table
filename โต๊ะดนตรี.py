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
    "blue": [(26, 50, 50), (85, 255, 255)],
    "green": [(86, 50, 50), (125, 255, 255)],
    "purple": [(126, 50, 50), (170, 255, 255)],
}

# Map colors to sound indices
color_to_sound = {
    "red": 0,
    "orange": 1,
    "blue": 2,
    "green": 3,
    "purple": 4,
}

# Recordings storage
recordings = {}
current_recording = []
recording_mode = False
naming_mode = False
recording_name = ""
playing_recording = None

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

# Function to play a recording in a loop
def play_recording(recording_name):
    global playing_recording
    if recording_name in recordings:
        playing_recording = recordings[recording_name][:]  # Copy the list

# Adjust brightness and contrast using CLAHE
def adjust_brightness_contrast(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

# Draw recording list on the frame
def draw_recording_list(frame):
    global playing_recording
    height, width, _ = frame.shape
    y_offset = 20
    button_width = 80
    button_height = 30

    for idx, name in enumerate(recordings.keys()):
        y_position = y_offset + idx * (button_height + 10)

        # Draw name box
        cv2.putText(frame, name, (width - 300, y_position + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Draw play/stop button
        button_color = (0, 255, 0) if playing_recording != recordings[name] else (0, 0, 255)
        cv2.rectangle(frame, (width - 100, y_position), (width - 100 + button_width, y_position + button_height),
                      button_color, -1)
        button_text = "Play" if playing_recording != recordings[name] else "Stop"
        cv2.putText(frame, button_text, (width - 100 + 5, y_position + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return width - 100, y_offset, button_width, len(recordings) * (button_height + 10)

# Start capturing from webcam
cap = cv2.VideoCapture(1)  # Change to 0 for the default webcam
x_position = 0  # Initial position of scanning line
playback_speed = 2  # Default scanning speed
exit_program = False  # Variable to control exit

while not exit_program:
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

    # Play a recording if currently active
    if playing_recording:
        if playing_recording:
            play_sound_by_color(playing_recording.pop(0))
        else:
            playing_recording = None

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

    # Draw recording list
    recording_list_area = draw_recording_list(frame)

    # Show the frame
    cv2.imshow("Color Detection and Sound", frame)

    # Update scanning line position
    x_position += playback_speed
    if x_position >= frame.shape[1]:  # Reset to the left side if it reaches the right
        x_position = 0

    # Handle keyboard input
    key = cv2.waitKey(1) & 0xFF

    if key == ord('1'):  # Numlock key 1 for starting recording
        recording_mode = True
        naming_mode = False
        current_recording.clear()
        print("Recording started...")

    elif key == ord('2'):  # Numlock key 2 for stopping recording
        recording_mode = False
        if current_recording:
            naming_mode = True
            print("Recording stopped. Enter name in the video window.")

    elif naming_mode:
        if key == 13:  # Enter key
            if recording_name.strip():
                recordings[recording_name.strip()] = current_recording.copy()
                print(f"Recording saved as: {recording_name.strip()}")
            recording_name = ""
            naming_mode = False
        elif key == 8:  # Backspace key
            recording_name = recording_name[:-1]
        elif 32 <= key <= 126:  # Printable characters
            recording_name += chr(key)

    elif key == ord('+'):  # Increase playback speed
        playback_speed += 1
        print(f"Playback speed increased to: {playback_speed}x")

    elif key == ord('-'):  # Decrease playback speed
        playback_speed = max(1, playback_speed - 1)  # Ensure speed is at least 1
        print(f"Playback speed decreased to: {playback_speed}x")

    elif key == ord('q'):  # Quit the application
        exit_program = True

cap.release()
cv2.destroyAllWindows()







