import os
import sys
import time
import shutil
import colorama
from colorama import Fore, Style
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip
from shutil import which
from pyfiglet import Figlet

colorama.init(autoreset=True)

DOWNLOAD_FOLDER = "downloads"
VIDEOS_FOLDER = "videos"

def clear_console():
    """
    Clears the console screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner():
    """
    Displays the 'YT CONVERT' banner using ASCII art and adds a credit line below it.
    """
    f = Figlet(font='slant')  # Puedes cambiar la fuente aquí si lo deseas
    banner = f.renderText('YT CONVERT')
    credit = "👑 Script Created by Naeaex - Follow me on Github for more scripts www.github.com/Naeaerc20"
    print(f"{Fore.GREEN}{banner}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{credit}{Style.RESET_ALL}")

def print_progress_bar(percentage, bar_length=40):
    """
    Prints a progress bar to the console.
    """
    filled_length = int(bar_length * percentage // 100)
    bar = '#' * filled_length + '-' * (bar_length - filled_length)
    print(f"\r[{bar}] {percentage:.2f}% ", end='')

def progress_hook(d):
    """
    Hook function to handle progress updates from yt_dlp.
    """
    if d['status'] == 'downloading':
        if d.get('total_bytes'):
            total = d['total_bytes']
        elif d.get('total_bytes_estimate'):
            total = d['total_bytes_estimate']
        else:
            total = None

        if total:
            percentage = d['downloaded_bytes'] / total * 100
            print_progress_bar(percentage)
    elif d['status'] == 'finished':
        print_progress_bar(100)
        print()  # Move to the next line

def convert_mp4_to_mp3(mp4_path, mp3_path):
    """
    Convert an MP4 file to MP3 using MoviePy.
    """
    try:
        with VideoFileClip(mp4_path) as video:
            audio = video.audio
            if audio is None:
                print(f"{Fore.RED}Error: No audio track found!")
                return False
            audio.write_audiofile(mp3_path)
        return True
    except Exception as e:
        print(f"{Fore.RED}Error during conversion: {e}")
        return False

def sanitize_filename(name):
    """
    Sanitize the filename by removing invalid characters.
    """
    return "".join(c for c in name if c.isalnum() or c in " .-_").rstrip()

def check_ffmpeg_installed():
    """
    Check if FFmpeg is installed and accessible.
    """
    if which('ffmpeg') is None:
        print(f"{Fore.RED}[ERROR] FFmpeg is not installed. Please install FFmpeg to proceed.")
        sys.exit(1)

def prompt_user_choice(prompt, choices):
    """
    Prompt the user with a question and return their choice.
    """
    choice = ''
    while choice not in choices:
        choice = input(prompt).strip().lower()
        if choice not in choices:
            print(f"{Fore.RED}Invalid choice. Please enter one of {', '.join(choices).upper()}.\n")
    return choice

def main():
    clear_console()
    check_ffmpeg_installed()
    display_banner()

    while True:
        print(f"{Fore.YELLOW}Welcome to the {Style.BRIGHT}YouTube MP4-to-MP3 Converter!")
        youtube_url = input(f"{Fore.GREEN}Please enter the YouTube video URL: {Style.RESET_ALL}").strip()

        if not youtube_url:
            print(f"{Fore.RED}[ERROR] No URL entered. Please try again.\n")
            continue

        # Prompt for filename choice
        filename_choice = prompt_user_choice(
            "Do you want to use the video title as the filename? (Y/N): ",
            ['y', 'n']
        )

        # Initialize base_name
        base_name = ""

        # Temporary ydl_opts to fetch video info without setting outtmpl
        temp_ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }

        try:
            print(f"\n{Fore.BLUE}[INFO] {Style.RESET_ALL}Fetching video information...")
            with YoutubeDL(temp_ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=False)
                uploader = info_dict.get('uploader', 'Unknown')
                print(f"{Fore.MAGENTA}[INFO]{Style.RESET_ALL} Channel: {uploader}")
                if filename_choice == 'y':
                    base_name = sanitize_filename(info_dict.get('title', 'downloaded_video'))
                else:
                    custom_name = input(f"{Fore.GREEN}Please enter your desired filename (without extension): {Style.RESET_ALL}").strip()
                    if not custom_name:
                        print(f"{Fore.RED}[ERROR] No filename entered. Using video title as fallback.\n")
                        base_name = sanitize_filename(info_dict.get('title', 'downloaded_video'))
                    else:
                        base_name = sanitize_filename(custom_name)
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Failed to fetch video information. Details: {e}\n")
            continue

        # Prompt for user action
        print("\nWhat would you like to do with the video?")
        print("1. Download and Convert to MP3")
        print("2. Only Download MP4")
        print("3. Download MP4 and Convert to MP3")
        action = prompt_user_choice("Enter your choice (1/2/3): ", ['1', '2', '3'])

        download_mp4 = False
        convert_mp3 = False
        save_mp4 = False

        if action == '1':
            download_mp4 = True
            convert_mp3 = True
            save_mp4 = False  # Only keep MP3
        elif action == '2':
            download_mp4 = True
            convert_mp3 = False
            save_mp4 = True  # Save MP4 without converting
        elif action == '3':
            download_mp4 = True
            convert_mp3 = True
            save_mp4 = True  # Save both MP4 and MP3

        # Ensure necessary directories exist
        if download_mp4 and save_mp4:
            if not os.path.exists(VIDEOS_FOLDER):
                os.makedirs(VIDEOS_FOLDER)
        if convert_mp3:
            if not os.path.exists(DOWNLOAD_FOLDER):
                os.makedirs(DOWNLOAD_FOLDER)

        # Set output template based on user choices
        if download_mp4 and not convert_mp3:
            outtmpl = os.path.join(VIDEOS_FOLDER, f"{base_name}.%(ext)s")
            format_choice = 'bestvideo+bestaudio/best'
        else:
            outtmpl = os.path.join(DOWNLOAD_FOLDER, f"{base_name}.%(ext)s")
            format_choice = 'bestvideo+bestaudio/best'

        ydl_opts = {
            'format': format_choice,
            'outtmpl': outtmpl,
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook],
        }

        try:
            print(f"{Fore.MAGENTA}[INFO]{Style.RESET_ALL} Title: {base_name}")
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=False)
                print(f"{Fore.MAGENTA}[INFO]{Style.RESET_ALL} Channel: {info_dict.get('uploader', 'Unknown')}\n")
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Failed to fetch video information. Details: {e}\n")
            continue

        # Determine download path
        if download_mp4 and not convert_mp3:
            download_path = os.path.join(VIDEOS_FOLDER, f"{base_name}.mp4")
        else:
            download_path = os.path.join(DOWNLOAD_FOLDER, f"{base_name}.mp4")

        print(f"{Fore.BLUE}[DOWNLOAD] {Style.RESET_ALL}Starting download of {base_name}...")

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Failed to download video. Details: {e}\n")
            continue

        # Verify download
        if not os.path.exists(download_path):
            # If the downloaded file is not mp4, find the correct extension
            possible_extensions = ['mp4', 'webm', 'mkv', 'flv', 'avi']
            found = False
            for ext in possible_extensions:
                potential_path = os.path.join(DOWNLOAD_FOLDER if convert_mp3 else VIDEOS_FOLDER, f"{base_name}.{ext}")
                if os.path.exists(potential_path):
                    download_path = potential_path
                    found = True
                    break
            if not found:
                print(f"{Fore.RED}[ERROR] Downloaded video file not found.\n")
                continue

        if download_mp4 and not convert_mp3:
            print(f"\n{Fore.GREEN}[SUCCESS] {Style.RESET_ALL}Video downloaded successfully and saved to '{VIDEOS_FOLDER}' folder!")
        else:
            print(f"\n{Fore.GREEN}[SUCCESS] {Style.RESET_ALL}Video downloaded successfully!")
            # If save_mp4 is True and action is 3, copy MP4 to 'videos' folder
            if save_mp4 and action == '3':
                destination_path = os.path.join(VIDEOS_FOLDER, os.path.basename(download_path))
                try:
                    shutil.copy(download_path, destination_path)
                    print(f"{Fore.YELLOW}[INFO] {Style.RESET_ALL}Copied MP4 file to '{VIDEOS_FOLDER}' folder.")
                except Exception as e:
                    print(f"{Fore.RED}[ERROR] Failed to copy MP4 to '{VIDEOS_FOLDER}'. Details: {e}\n")
        time.sleep(1)

        # Convert to MP3 if requested
        if convert_mp3:
            mp3_filename = f"{base_name}.mp3"
            mp3_path = os.path.join(DOWNLOAD_FOLDER, mp3_filename)
            print(f"\n{Fore.BLUE}[CONVERTING] {Style.RESET_ALL}Converting MP4 to MP3...")
            # Simple spinner during conversion
            spinner = ['|', '/', '-', '\\']
            for i in range(20):
                sys.stdout.write(f"\r{Fore.CYAN}Converting {spinner[i % len(spinner)]}")
                sys.stdout.flush()
                time.sleep(0.1)
            sys.stdout.write('\r' + ' ' * 30 + '\r')
            if convert_mp4_to_mp3(download_path, mp3_path):
                print(f"{Fore.GREEN}[SUCCESS] {Style.RESET_ALL}Conversion to MP3 completed!")
                # Remove MP4 if not saving
                if not save_mp4:
                    if os.path.exists(download_path):
                        os.remove(download_path)
                        print(f"{Fore.YELLOW}[INFO] {Style.RESET_ALL}Removed MP4 file: {os.path.basename(download_path)}")
            else:
                print(f"{Fore.RED}[FAILED] {Style.RESET_ALL}Could not convert to MP3.\n")
                continue

        print(f"{Fore.GREEN}[DONE] {Style.RESET_ALL}Your files are located in the respective folders.\n")
        print(f"{Fore.CYAN}Thank you for using the YouTube MP4-to-MP3 Converter! Have a great day! 👋")

        # Ask if the user wants to process another video
        again = prompt_user_choice("Do you want to download/convert another video? (Y/N): ", ['y', 'n'])
        if again == 'n':
            print(f"{Fore.CYAN}Goodbye! 👋")
            break
        else:
            print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    main()
