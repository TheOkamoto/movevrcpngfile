import os
import time
import shutil
import watchdog.events
import watchdog.observers
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Move files with a delay.')
parser.add_argument('--delay', type=int, default=1, help='The delay before moving files in seconds.')
parser.add_argument('--source', type=str, required=True, help='The source folder.')
parser.add_argument('--destination', type=str, required=True, help='The destination folder.')
args = parser.parse_args()

# Verifies if the destination folder exists
if not os.path.exists(args.destination):
    os.makedirs(args.destination)

# Function to move the file to the destination folder
def move_file(event):
    source_file = event.src_path
    if not source_file.lower().endswith('.png'):  # Check if the file is a PNG
        return
    new_path = os.path.join(args.destination, os.path.relpath(source_file, args.source))
    try:
        time.sleep(args.delay)  # Wait for the delay time before moving the file
        os.makedirs(os.path.dirname(new_path), exist_ok=True)  # Create the directory if it doesn't exist
        shutil.move(source_file, new_path)
        print(f"File '{source_file}' moved to '{new_path}' successfully")
    except (PermissionError, IOError) as e:
        print(f"Error moving file '{source_file}': {e}")

# Monitor the folder for new files
class FolderWatchdog(watchdog.events.FileSystemEventHandler):
    def on_created(self, event):
        move_file(event)

if __name__ == "__main__":
    observer = watchdog.observers.Observer()
    observer.schedule(FolderWatchdog(), args.source, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()