import pygame
import os
import tkinter as tk
from tkinter import messagebox

def play_sound(sound):
    if sound:
        sound.play()
    else:
        messagebox.showerror("Error", "Sound file not found!")

def main():
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

    # Create GUI
    root = tk.Tk()
    root.title("Sound Player")

    tk.Label(root, text="Press a button to play a sound", font=("Arial", 14)).pack(pady=10)

    buttons = ["DO", "RE", "ME", "FA", "SON", "RA", "T"]
    for i, label in enumerate(buttons):
        button = tk.Button(root, text=label, font=("Arial", 12), width=10, command=lambda i=i: play_sound(sounds[i]))
        button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
