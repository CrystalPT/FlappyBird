import os
import sys
import subprocess
import requests
import hashlib
import time
from datetime import datetime

# Configuration
GITHUB_USER = "CrystalPT"  # Replace with the GitHub username
REPO_NAME = "FlappyBird"  # Replace with the repository name
BRANCH = "main"  # Or whichever branch you want to track
MAIN_FILE = "flappy.exe"  # The main game file to run
CHECK_INTERVAL = 120  # Check for updates every hour (in seconds) 3600
LOCAL_DIR = os.path.join(os.path.expanduser("~"), "flappy_bird")  # Local installation directory

# GitHub raw content URL format
RAW_CONTENT_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}"


# Function to get file list from GitHub
def get_github_file_list():
    try:
        # This assumes you have a file named 'filelist.txt' in your repo listing all game files
        # Another approach would be to use the GitHub API to list all files in the repo
        response = requests.get(f"{RAW_CONTENT_URL}/filelist.txt", timeout=10)
        if response.status_code == 200:
            return [line.strip() for line in response.text.splitlines() if line.strip()]
        else:
            print(f"Failed to get file list from GitHub. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting file list: {e}")
        return None


# Function to download a file from GitHub
def download_file(filename):
    try:
        print(f"Downloading {filename}...")
        response = requests.get(f"{RAW_CONTENT_URL}/{filename}", timeout=30)
        if response.status_code == 200:
            local_path = os.path.join(LOCAL_DIR, filename)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"Failed to download {filename}. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False


# Function to check if a file needs updating
def file_needs_update(filename):
    try:
        # Get the remote file's content to compare
        response = requests.get(f"{RAW_CONTENT_URL}/{filename}", timeout=10)
        if response.status_code != 200:
            print(f"Failed to check {filename}. Status code: {response.status_code}")
            return False

        remote_content = response.content
        remote_hash = hashlib.md5(remote_content).hexdigest()

        # Check if local file exists and compare hash
        local_path = os.path.join(LOCAL_DIR, filename)
        if not os.path.exists(local_path):
            return True  # File doesn't exist locally, so it needs to be downloaded

        with open(local_path, 'rb') as f:
            local_content = f.read()
            local_hash = hashlib.md5(local_content).hexdigest()

        return local_hash != remote_hash
    except Exception as e:
        print(f"Error checking update for {filename}: {e}")
        return False


# Function to check for updates and download if needed
def check_for_updates():
    print(f"Checking for updates at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")

    # First, check if the main game file exists locally
    if not os.path.exists(os.path.join(LOCAL_DIR, MAIN_FILE)):
        print("Game not installed locally. Performing initial installation...")
        # Ensure the directory exists
        os.makedirs(LOCAL_DIR, exist_ok=True)

        # Get file list from GitHub
        file_list = get_github_file_list()
        if not file_list:
            print("Failed to get file list. Cannot install the game.")
            return False

        # Download all files
        all_successful = True
        for filename in file_list:
            success = download_file(filename)
            if not success:
                all_successful = False

        return all_successful

    # Game is already installed, check for updates
    file_list = get_github_file_list()
    if not file_list:
        print("Failed to get file list. Using existing version.")
        return True  # Use existing version

    # Check each file for updates
    updates_needed = False

    for filename in file_list:
        if file_needs_update(filename):
            updates_needed = True
            success = download_file(filename)
            if not success:
                print(f"Warning: Failed to update {filename}")

    if updates_needed:
        print("Game updated successfully!")
    else:
        print("Game is already up to date.")

    return True


# Function to run the game
def run_game():
    game_path = os.path.join(LOCAL_DIR, MAIN_FILE)
    if os.path.exists(game_path):
        print(f"Starting Flappy Bird...")
        try:
            # Run the game from its directory to ensure relative paths work
            original_dir = os.getcwd()
            os.chdir(LOCAL_DIR)
            subprocess.run([sys.executable, MAIN_FILE])
            os.chdir(original_dir)
        except Exception as e:
            print(f"Error running the game: {e}")
    else:
        print(f"Game file not found: {game_path}")


# Main application loop
def main():
    print("===== Flappy Bird Auto-Update Launcher =====")

    while True:
        # Check for updates
        update_successful = check_for_updates()

        if update_successful:
            # Run the game
            run_game()

            # Ask if the user wants to check for updates again
            print("\nOptions:")
            print("1. Check for updates and play again")
            print("2. Exit")

            choice = input("Enter your choice (1/2): ")
            if choice == '2':
                print("Thanks for playing! Goodbye.")
                break
        else:
            print("Update check failed. Please try again later.")
            retry = input("Retry update check? (y/n): ")
            if retry.lower() != 'y':
                break

        # Wait for a moment before checking again
        print(f"Will check for updates in {CHECK_INTERVAL // 60} minutes...")
        # You can remove the sleep for manual testing
        # time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nLauncher terminated.")