# Python-based Video Cropper and Compressor

This project is a Python application that allows users to trim and compress video files using a graphical user interface. It combines OpenCV for video processing with Tkinter for the GUI, and uses FFmpeg for video trimming and compression.

## Features

- Load multiple video files from a selected folder
- Play, pause, and navigate through videos
- Set start and end points for trimming
- Trim videos and save them to a specified output folder
- User-friendly timeline interface for easy navigation
- Support for various video formats (mp4, avi, mov)

## Requirements

- Python 3.x
- OpenCV (cv2)
- NumPy
- Tkinter (usually comes with Python)
- FFmpeg (must be installed and added to system PATH)

## Installation

1. Clone this repository or download the source code.
2. Install the required Python packages:
3. Ensure FFmpeg is installed on your system and added to the PATH.

## Usage

1. Run the script
2. Click "Load Video Folder" to select a folder containing video files.
3. Select "Select Save Folder" to choose where trimmed videos will be saved.
4. Use the interface to navigate through videos, set trim points, and save trimmed versions.

## Controls

- Space bar: Play/Pause video
- 'n' key: Next video
- 'p' key: Previous video
- Mouse click on timeline: Jump to that point in the video
- "Start" button: Set start point for trimming
- "End" button: Set end point for trimming
- "Save" button: Save the trimmed video

## Notes

- Ensure FFmpeg is correctly installed and accessible from the command line for the trimming functionality to work.
- The application supports mp4, avi, and mov video formats.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/Zamiul-rashid/Python-based-video-cropper-and-compressor.-/issues) if you want to contribute.

## License

[MIT](https://choosealicense.com/licenses/mit/)
