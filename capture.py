import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
import subprocess
import os
import shutil


class VideoTrimmer:
    def __init__(self):
        self.video_path = None
        self.cap = None
        self.start_time = 0
        self.end_time = 0
        self.current_time = 0
        self.total_time = 0
        self.fps = 0
        self.playing = True
        self.output_dir = None
        self.trimming = False
        self.frame = None
        self.timeline_height = 50
        self.timeline_y = 130
        self.dragging_timeline = False

    def select_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov")])
        if self.video_path:
            self.cap = cv2.VideoCapture(self.video_path)
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_time = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) / self.fps)
            self.end_time = self.total_time
            self.select_output_directory()
            self.process_video()

    def select_output_directory(self):
        self.output_dir = filedialog.askdirectory(title="Select Output Directory")

    def process_video(self):
        cv2.namedWindow("Video Trimmer")
        cv2.setMouseCallback("Video Trimmer", self.mouse_callback)

        while True:
            ret, self.frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            self.current_time = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000

            self.draw_interface()

            cv2.imshow("Video Trimmer", self.frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def draw_interface(self):
        # Draw time
        cv2.rectangle(self.frame, (10, 10), (300, 40), (0, 0, 0), -1)
        cv2.putText(self.frame, f"Time: {self.format_time(self.current_time)}", (15, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

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
        if not self.output_dir:
            print("No output directory selected.")
            return

        if self.start_time >= self.end_time:
            print("Invalid trim range. Make sure to set both start and end times correctly.")
            return

        # Check if FFmpeg is available in the system path
        if shutil.which('ffmpeg') is None:
            print("FFmpeg is not found in the system PATH.")
            print("Please make sure FFmpeg is correctly installed and added to the system PATH.")
            return

        input_file = self.video_path
        output_file = os.path.join(self.output_dir, "trimmed_video.mp4")
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
    root.withdraw()

    trimmer = VideoTrimmer()
    trimmer.select_video()