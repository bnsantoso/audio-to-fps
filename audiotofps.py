import tkinter as tk
import time
from tkinter import ttk
from tkinter import filedialog
from pygame import mixer
from mutagen import File

start_time = 0
pause_time = 0
unpause_time = 0
pause_total_t = 0
updateSlider_state = False
pause_state = False
hold_pause = 0

def update_slider():
    global start_time
    if updateSlider.get():
        current_time_up = delta_time() * 1000
    else:
        current_time_up = round(time_slider.get()/1000) * 1000
    if current_time_up > max_value_slider:
        current_time_up = 0
        reseto()
    time_slider.set(current_time_up)
    time_label.config(text=format_time(current_time_up))
    if playing.get():
        root.after(10, update_slider)

def delta_time():
    now_time = (time.time() - start_time)
    return now_time

def format_time(milliseconds):
    minutes = int(milliseconds / 60000)
    seconds = int((milliseconds / 1000) % 60)
    millis = int(milliseconds % 1000)
    fps = int(fps_entry.get())
    if fps > 60:
        fps = 60
    frame_count = int((milliseconds / 1000) * fps)
    return f"[{minutes:02d}:{seconds:02d}.{millis:03d}] [Frame: {frame_count}]"

def reseto():
    playing.set(False)
    play_button.config(text="Play")
    pause_resume_button.config(state=tk.DISABLED)
    time_slider.set(0)
    time_label.config(text="[00:00.000] [Frame: 0]")
    
def play_button_pressed():
    global playing, start_time
    if playing.get():
        playing.set(False)
        pause_resume_button.config(text="Pause")
        mixer.music.stop()
        reseto()
        time_slider.set(0)
    else:
        updateSlider.set(True)
        reseto()
        playing.set(True)
        play_button.config(text="Stop")
        pause_resume_button.config(text="Pause")
        pause_resume_button.config(state=tk.NORMAL)
        mixer.music.play()
        start_time = time.time()
        update_slider()

def pause_resume_button_pressed():
    global playing, start_time, pause_time, updateSlider_state, pause_state
    if playing.get():
        playing.set(False)
        pause_resume_button.config(text="Resume")
        mixer.music.pause()
        pause_time = time.time()
        updateSlider_state = False
        pause_state = True
        #print(f"pause : {pause_time}")
    else:
        playing.set(True)
        pause_resume_button.config(text="Pause")
        update_slider()
        mixer.music.unpause()
        unpause_time = time.time()
        pause_total_t = unpause_time - pause_time 
        #print(f"{unpause_time} - {pause_time} = {pause_total_t}  <--- pause_total_t")
        if not updateSlider_state:
            #print(f"{start_time} <--- start_time before")
            start_time = start_time + pause_total_t
            #print(f"{start_time} + {pause_total_t} = {start_time} <--- start_time after")
        else:
            start_time = start_time + ( unpause_time - hold_pause )
        updateSlider_state = False
        pause_state = False

def update_time_label(event):
    updateSlider.set(False)
    current_time = round(time_slider.get()/1000)
    time_label.config(text=format_time(current_time*1000))
    
def update_audio(event):
    global start_time, updateSlider_state, hold_pause
    current_time = round(time_slider.get()/1000)
    mixer.music.set_pos(current_time)
    unpause_time = time.time()
    hold_pause = unpause_time
    start_time = unpause_time - current_time
    updateSlider_state = True
    updateSlider.set(True)

def forward_pressed():
    global start_time, updateSlider_state, hold_pause, pause_state
    current_time = round(time_slider.get()/1000) + 4
    mixer.music.set_pos(current_time)
    time_label.config(text=format_time(current_time*1000))
    now_time = time.time()
    hold_pause = now_time
    start_time = now_time - current_time
    updateSlider_state = True
    updateSlider.set(True)
    if pause_state:
        update_slider()

def backward_pressed():
    global start_time, updateSlider_state, hold_pause, pause_state
    current_time = round(time_slider.get()/1000) - 4
    if current_time < 0:
        current_time = 0
    mixer.music.set_pos(current_time)
    time_label.config(text=format_time(current_time*1000))
    now_time = time.time()
    hold_pause = now_time
    start_time = now_time - current_time
    updateSlider_state = True
    updateSlider.set(True)
    if pause_state:
        update_slider()

def slider_presed(event):
    global pause_time
    pause_time = time.time()

def select_file():
    file_path = filedialog.askopenfilename(
        filetypes=(("Audio Files", "*.mp3;*.wav;*.ogg"), ("All Files", "*.*"))
    )
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(tk.END, file_path)
    extract_audio_length(file_path)
    file_path = file_path_entry.get()
    mixer.init()
    mixer.music.load(file_path)
    reseto()

def extract_audio_length(file_path):
    global audio_length
    audio_length = 0  
    audio = File(file_path)
    if audio is not None and hasattr(audio.info, "length"):
        audio_length = audio.info.length
        update_slider_max()

def update_slider_max():
    global max_value_slider
    max_value_slider = audio_length * 1000  
    time_slider.config(to=max_value_slider)
    update_slider()

def validate_int(value):
    if value.isdigit():
        return True
    else:
        return False

root = tk.Tk()
root.title("Audio to FPS")
root.geometry("500x240")
    
validate_cmd = root.register(validate_int)

playing = tk.BooleanVar()
playing.set(False)

updateSlider = tk.BooleanVar()
updateSlider.set(True)

time_label = tk.Label(root, text="[00:00.000] [Frame: 0]", font=("Helvetica", 24))
time_label.pack(pady=10)

time_slider = ttk.Scale(root, from_=0, to=300000, orient=tk.HORIZONTAL)
time_slider.pack(fill=tk.X, padx=10, pady=10)
time_slider.bind("<B1-Motion>", update_time_label)  
time_slider.bind("<ButtonPress-1>", slider_presed)
time_slider.bind("<ButtonRelease-1>", update_audio)

button_frame = tk.Frame(root)
button_frame.pack()

fps_label = tk.Label(root, text="FPS:")
fps_label.pack()
fps_entry = ttk.Entry(root, validate="key", validatecommand=(validate_cmd, "%P"), width=3)
fps_entry.insert(tk.END, "30")  
fps_entry.pack()

file_button = ttk.Button(button_frame, text="Select File", command=select_file)
file_button.pack()

play_button = ttk.Button(button_frame, text="Play", command=play_button_pressed)
play_button.pack(side=tk.LEFT)

pause_resume_button = ttk.Button(button_frame, text="Pause", command=pause_resume_button_pressed, state=tk.DISABLED)
pause_resume_button.pack(side=tk.LEFT)

backward_button = ttk.Button(button_frame, text="Backward", command=backward_pressed)
backward_button.pack(side=tk.LEFT)

forward_button = ttk.Button(button_frame, text="Forward", command=forward_pressed)
forward_button.pack(side=tk.LEFT)

file_path_entry = tk.Entry(root, width=50)
file_path_entry.pack(fill=tk.X, padx=10, pady=10)

root.mainloop()
