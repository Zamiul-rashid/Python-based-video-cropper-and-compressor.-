import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, Listbox, SINGLE
import subprocess
import os
import shutil
import threading

class VideoTrimmer:
    def __init__(self, root):
        self.video_path = None
        self.cap = None
        self.start_time = 0
        self.end_time = 0
        self.current_time = 0
        self.total_time = 0
        self.fps = 0
        self.playing = True
        self.output_dir = None
        self.save_dir = None
        self.trimming = False
        self.frame = None
        self.timeline_height = 50
        self.timeline_y = 130
        self.dragging_timeline = False
        self.video_files = []
        self.current_video_index = 0

        # Initialize Tkinter GUI
        self.root = root
        self.root.title("Video Trimmer")

        self.frame_list = tk.Frame(self.root)
        self.frame_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.listbox = Listbox(self.frame_list, selectmode=SINGLE)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        self.load_folder_button = tk.Button(self.root, text="Load Video Folder", command=self.select_video_folder)
        self.load_folder_button.pack()

        self.select_save_folder_button = tk.Button(self.root, text="Select Save Folder", command=self.select_save_folder)
        self.select_save_folder_button.pack()

        # Start video processing thread
        self.video_thread = threading.Thread(target=self.process_video, daemon=True)
        self.video_thread.start()

    def select_video_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder with Videos")
        if folder_path:
            self.output_dir = folder_path
            self.video_files = [f for f in os.listdir(folder_path) if f.endswith(('.mp4', '.avi', '.mov'))]
            if self.video_files:
                self.listbox.delete(0, tk.END)
                for video_file in self.video_files:
                    self.listbox.insert(tk.END, video_file)
                self.load_video(0)
            else:
                print("No video files found in the selected folder.")

    def select_save_folder(self):
        folder_path = filedialog.askdirectory(title="Select Save Folder")
        if folder_path:
            self.save_dir = folder_path
            print(f"Save folder set to: {self.save_dir}")

    def on_select(self, event):
        selected_index = event.widget.curselection()
        if selected_index:
            self.load_video(selected_index[0])

    def load_video(self, index):
        if 0 <= index < len(self.video_files):
            self.current_video_index = index
            self.video_path = os.path.join(self.output_dir, self.video_files[index])
            self.cap = cv2.VideoCapture(self.video_path)
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_time = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) / self.fps)
            self.end_time = self.total_time
            self.current_time = 0
            self.start_time = 0
            self.trimming = False

    def process_video(self):
        cv2.namedWindow("Video Trimmer")
        cv2.setMouseCallback("Video Trimmer", self.mouse_callback)

        while True:
            if self.cap and self.cap.isOpened() and self.playing:
                ret, self.frame = self.cap.read()
                if not ret:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue

                self.current_time = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000

                self.draw_interface()
                self.frame = cv2.resize(self.frame, (1280, 720))
                cv2.imshow("Video Trimmer", self.frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('n'):
                self.load_video((self.current_video_index + 1) % len(self.video_files))
            elif key == ord('p'):
                self.load_video((self.current_video_index - 1) % len(self.video_files))
            elif key == ord(' '):  # Space bar for pause/play
                self.playing = not self.playing

        self.cap.release()
        cv2.destroyAllWindows()

    def draw_interface(self):
        # Draw time, current video name, and index
        cv2.rectangle(self.frame, (10, 10), (self.frame.shape[1] - 10, 40), (0, 0, 0), -1)
        cv2.putText(self.frame, f"Time: {self.format_time(self.current_time)} | Video [{self.current_video_index + 1}/{len(self.video_files)}]: {self.video_files[self.current_video_index]}", 
                    (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Draw buttons
        cv2.rectangle(self.frame, (10, 50), (110, 90), (0, 255, 0), -1)
        cv2.putText(self.frame, "Start", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        cv2.rectangle(self.frame, (120, 50), (220, 90), (0, 0, 255), -1)
        cv2.putText(self.frame, "End", (150, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        cv2.rectangle(self.frame, (230, 50), (330, 90), (255, 0, 0), -1)
        cv2.putText(self.frame, "Save", (260, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # Draw trimming status
        status = "Trimming" if self.trimming else "Not Trimming"
        cv2.putText(self.frame, f"Status: {status}", (15, 120), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Draw timeline
        timeline_width = self.frame.shape[1] - 20
        cv2.rectangle(self.frame, (10, self.timeline_y), (10 + timeline_width, self.timeline_y + self.timeline_height), (200, 200, 200), -1)
        
        # Draw current time marker
        marker_x = int(10 + (self.current_time / self.total_time) * timeline_width)
        cv2.line(self.frame, (marker_x, self.timeline_y), (marker_x, self.timeline_y + self.timeline_height), (0, 0, 255), 2)

        # Draw start and end markers
        start_x = int(10 + (self.start_time / self.total_time) * timeline_width)
        end_x = int(10 + (self.end_time / self.total_time) * timeline_width)
        cv2.rectangle(self.frame, (start_x, self.timeline_y), (end_x, self.timeline_y + self.timeline_height), (0, 255, 0), 2)

        # Draw instructions
        cv2.putText(self.frame, "Press 'n' for next video, 'p' for previous video, space to pause/play", 
                    (15, self.frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if 10 <= x <= 110 and 50 <= y <= 90:  # Start button
                self.start_time = self.current_time
                self.trimming = True
                print(f"Start time set to: {self.format_time(self.start_time)}")
            elif 120 <= x <= 220 and 50 <= y <= 90:  # End button
                if self.trimming:
                    self.end_time = self.current_time
                    self.trimming = False
                    print(f"End time set to: {self.format_time(self.end_time)}")
                else:
                    print("Please set start time first.")
            elif 230 <= x <= 330 and 50 <= y <= 90:  # Save button
                self.save_trimmed_video()
            elif self.timeline_y <= y <= self.timeline_y + self.timeline_height:
                self.dragging_timeline = True
                self.update_time_from_timeline(x)

        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging_timeline = False

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.dragging_timeline:
                self.update_time_from_timeline(x)

    def update_time_from_timeline(self, x):
        timeline_width = self.frame.shape[1] - 20
        time_ratio = (x - 10) / timeline_width
        self.current_time = max(0, min(self.total_time, time_ratio * self.total_time))
        self.cap.set(cv2.CAP_PROP_POS_MSEC, int(self.current_time * 1000))

    def format_time(self, seconds):
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def save_trimmed_video(self):
        if not self.save_dir:
            print("No save directory selected.")
            return

        if self.start_time >= self.end_time:
            print("Invalid trim range. Make sure to set both start and end times correctly.")
            return

        if shutil.which('ffmpeg') is None:
            print("FFmpeg is not found in the system PATH.")
            print("Please make sure FFmpeg is correctly installed and added to the system PATH.")
            return

        input_file = self.video_path
        original_name = os.path.splitext(self.video_files[self.current_video_index])[0]
        output_file = os.path.join(self.save_dir, f"{original_name}_trimmed.mp4")
        start_time = self.format_time(self.start_time)
        duration = self.format_time(self.end_time - self.start_time)

        ffmpeg_cmd = [
            "ffmpeg",
            "-i", input_file,
            "-ss", start_time,
            "-t", duration,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-strict", "experimental",
            output_file
        ]

        try:
            subprocess.run(ffmpeg_cmd, check=True)
            print(f"Trimmed video saved to: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while saving the video: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    trimmer = VideoTrimmer(root)
    root.mainloop()
