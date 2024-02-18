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

# Save the arguments to a configuration file
def save_to_config_file(args):
    try:
        config['DEFAULT'] = {'Delay': args.delay, 'Source': args.source, 'Destination': args.destination}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        console.print("Configuration file written successfully", style="bold green")
    except Exception as e:
        console.print(f"Error writing to configuration file: {e}", style="bold red")

def read_config_file(config):
    if config_file_exists:
        try:
            config.read('config.ini')
        except Exception as e:
            console.print(f"Error loading configuration file: {e}", style="bold red")
    # If configuration file doesn't exist, prompt user for input
    else:
        console.print("First launch detected. Please enter the source and destination.", style="bold yellow")

def get_args():
    if config_file_exists:
        source_default = config.get('DEFAULT', 'Source', fallback='')
        destination_default = config.get('DEFAULT', 'Destination', fallback='')
        return source_default, destination_default
    
    source_default = input("Enter the source folder: ").replace('\\', '\\\\')
    while not os.path.isdir(source_default):
        console.print("Invalid source folder. Please try again.", style="bold red")
        source_default = input("Enter the source folder: ").replace('\\', '\\\\')

    destination_default = input("Enter the destination folder: ").replace('\\', '\\\\')
    while not os.path.isdir(destination_default):
        console.print("Invalid destination folder. Please try again.", style="bold red")
        destination_default = input("Enter the destination folder: ").replace('\\', '\\\\')
    return source_default, destination_default

# Function to parse command line arguments
def parse_arguments():
    # Load the configuration file
    config = configparser.ConfigParser()
    config_file_exists = os.path.isfile('config.ini')

    read_config_file(config)

    # Define command line arguments
    parser = argparse.ArgumentParser(description='Move files with a delay.')
    
    # If configuration file exists, use its values as default
    # Otherwise, prompt user for input and replace single backslashes with double backslashes
    delay_default = config.getint('DEFAULT', 'Delay', fallback=1) if config_file_exists else 1

    source_default, destination_default = get_args()

    parser.add_argument('--delay', type=int, default=delay_default, help='The delay before moving files in seconds.')
    parser.add_argument('--source', type=str, default=source_default, help='The source folder.')
    parser.add_argument('--destination', type=str, default=destination_default, help='The destination folder.')
    
    args = parser.parse_args()

    # After the first setup, ask the user if they want to add more source/destination pairs
    if config_file_exists:
        save_to_config_file(args)
        return args

    add_more = input("Do you want to add more source/destination pairs? (yes/no): ")
    if add_more.lower() == 'yes':
        more_sources = []
        more_destinations = []
        while True:
            more_source = input("Enter an additional source folder (or 'done' to finish): ").replace('\\', '\\\\')
            if more_source.lower() == 'done': break

            while not os.path.isdir(more_source):
                console.print("Invalid source folder. Please try again.", style="bold red")
                more_source = input("Enter an additional source folder (or 'done' to finish): ").replace('\\', '\\\\')
            more_sources.append(more_source)

            more_destination = input("Enter an additional destination folder (or 'done' to finish): ").replace('\\', '\\\\')
            if more_destination.lower() == 'done': break

            while not os.path.isdir(more_destination):
                console.print("Invalid destination folder. Please try again.", style="bold red")
                more_destination = input("Enter an additional destination folder (or 'done' to finish): ").replace('\\', '\\\\')
            more_destinations.append(more_destination)

        # Save the additional source/destination pairs to the configuration file
        for i, (source, destination) in enumerate(zip(more_sources, more_destinations)):
            config[f'PAIR{i+1}'] = {'Source': source, 'Destination': destination}

    save_to_config_file(args)

    return args

# Function to create destination folder if it doesn't exist
def create_destination_folder(destination):
    if os.path.exists(destination): return
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
    console.print("\nFile Transfer Settings\n", style="bold red")
    console.print(table)

    # Print monitoring status
    console.print("\nMonitoring the source folder for new files...", style="bold green")

# Function to move the file to the destination folder
def move_file(event, destination, delay):
    source_file = event.src_path

    # Check if the file is a PNG
    if not source_file.lower().endswith('.png'): return

    # Calculate new file path
    new_path = os.path.join(destination, os.path.relpath(source_file, args.source))

    try:
        # Wait for the delay time before moving the file
        if delay <= 2: time.sleep(delay)

        with Progress() as progress:
            task = progress.add_task("[cyan]Moving file...", total=delay)
            for _ in range(delay):
                time.sleep(1)
                progress.update(task, advance=1)

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