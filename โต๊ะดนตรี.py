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

# Adjust brightness and contrast using CLAHE
def adjust_brightness_contrast(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

# Playback a recording
def playback_recording(recording):
    for color in recording:
        play_sound_by_color(color)
        pygame.time.wait(500)  # Add a delay between sounds

# Start capturing from webcam
cap = cv2.VideoCapture(0)  # Change to 0 for the default webcam
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

    # Show recording status
    if recording_mode:
        cv2.putText(frame, "Recording: ON", (10, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # Show the frame
    cv2.imshow("Color Detection and Sound", frame)

    # Update scanning line position
    x_position += playback_speed
    if x_position >= frame.shape[1]:  # Reset to the left side if it reaches the right
        x_position = 0
        if recording_mode and current_recording:  # Ask to save the recording if not empty
            print("Recording complete. Enter a name to save the recording, or press Enter to discard:")
            name = input().strip()
            if name:
                recordings[name] = current_recording.copy()
                print(f"Recording saved as '{name}'.")
            current_recording.clear()

    # Handle keyboard input
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # Quit on 'q' key
        break
    elif key == ord('+'):  # Increase speed
        playback_speed = min(playback_speed + 1, 10)  # Cap at 10x
    elif key == ord('-'):  # Decrease speed
        playback_speed = max(playback_speed - 1, 1)  # Minimum 1x
    elif key == ord('p'):  # Play a recording
        print("Available recordings:")
        for name in recordings:
            print(f"- {name}")
        print("Enter the name of the recording to play:")
        name = input().strip()
        if name in recordings:
            print(f"Playing recording '{name}'...")
            playback_recording(recordings[name])
        else:
            print("Recording not found.")
    elif key == ord('r'):  # Toggle recording mode
        recording_mode = not recording_mode
        if recording_mode:
            print("Recording started...")
            current_recording.clear()
        else:
            print("Recording stopped.")

cap.release()
cv2.destroyAllWindows()


