import argparse
import os
import time
import shutil
import watchdog.events
import watchdog.observers
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
import configparser

# Initialize console as a global variable
console = Console()

# Function to parse command line arguments
def parse_arguments():
    # Load the configuration file
    config = configparser.ConfigParser()
    try:
        config.read('config.ini')
    except Exception as e:
        console.print(f"Error loading configuration file: {e}", style="bold red")

    parser = argparse.ArgumentParser(description='Move files with a delay.')
    parser.add_argument('--delay', type=int, default=config.getint('DEFAULT', 'Delay', fallback=1), help='The delay before moving files in seconds.')
    parser.add_argument('--source', type=str, default=config.get('DEFAULT', 'Source', fallback=''), help='The source folder.')
    parser.add_argument('--destination', type=str, default=config.get('DEFAULT', 'Destination', fallback=''), help='The destination folder.')
    args = parser.parse_args()

    # Save the arguments to a configuration file
    try:
        config['DEFAULT'] = {'Delay': args.delay, 'Source': args.source, 'Destination': args.destination}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        console.print("Configuration file written successfully", style="bold green")
    except Exception as e:
        console.print(f"Error writing to configuration file: {e}", style="bold red")

    return args

# Function to create destination folder if it doesn't exist
def create_destination_folder(destination):
    if not os.path.exists(destination):
        os.makedirs(destination)

# Function to initialize console and print settings
def print_settings(source, destination, delay):
    # Create and populate table with file transfer settings
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Source", style="dim", width=45)
    table.add_column("Destination", style="dim", width=45)
    table.add_column("Delay", style="dim", width=5)
    table.add_row(source, destination, str(delay))

    # Print file transfer settings
    console.print("File Transfer Settings", style="bold red")
    console.print(table)

    # Print monitoring status
    console.print("\nMonitoring the source folder for new files...", style="bold green")

# Function to move the file to the destination folder
def move_file(event, destination, delay):
    source_file = event.src_path

    # Check if the file is a PNG
    if not source_file.lower().endswith('.png'):
        return

    # Calculate new file path
    new_path = os.path.join(destination, os.path.relpath(source_file, args.source))

    try:
        # Wait for the delay time before moving the file
        if delay > 2:
            with Progress() as progress:
                task = progress.add_task("[cyan]Moving file...", total=delay)
                for _ in range(delay):
                    time.sleep(1)
                    progress.update(task, advance=1)
        else:
            time.sleep(delay)

        os.makedirs(os.path.dirname(new_path), exist_ok=True)  # Create the directory if it doesn't exist
        shutil.move(source_file, new_path)
        console.print(f"File '{source_file}' moved to '{new_path}' successfully", style="bold blue")
    except (PermissionError, IOError) as e:
        console.print(f"Error moving file '{source_file}': {e}", style="bold red")
# Monitor the folder for new files
class FolderWatchdog(watchdog.events.FileSystemEventHandler):
    def __init__(self, destination, delay):
        self.destination = destination
        self.delay = delay

    def on_created(self, event):
        move_file(event, self.destination, self.delay)

if __name__ == "__main__":
    args = parse_arguments()
    create_destination_folder(args.destination)
    print_settings(args.source, args.destination, args.delay)

    observer = watchdog.observers.Observer()
    observer.schedule(FolderWatchdog(args.destination, args.delay), args.source, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()