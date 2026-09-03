import msvcrt
import os
import atexit
import pathlib
import shutil
import subprocess
import sys
import winreg
import random
import time
import ctypes
import re
from pathlib import Path

os.system("")

GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"
DARK_BLUE = "\033[34m"

GAME_FOLDER_NAME = "Stardew Valley"
TARGET_FILE_NAME = "SMAPImodpreloader.exe"
SHOULD_DELETE_FOLDER = False
TARGET_FOLDER_PATH = None
FOLDER_TO_REMOVE = ["SMAPI-mod-preloader-main",
                    "SMAPI-mod-preloader",
                    "SMAPI-mod-preloader-unstable"
]


if os.name == 'nt':
    os.system('')


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def set_console_title(title: str) -> None:
    if os.name == "nt":

        ctypes.windll.kernel32.SetConsoleTitleW(title)


def get_key():
    char = msvcrt.getch()
    try:
        return char.decode('utf-8')
    except UnicodeDecodeError:
        return ''


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def find_steam_game_path(folder_name: str) -> Path | None:
    possible_paths = []

    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"
        ) as key:
            steam_path, _ = winreg.QueryValueEx(key, "InstallPath")
            possible_paths.append(
                Path(steam_path) / "steamapps" / "common" / folder_name
            )
    except Exception:
        pass

    default_drives = ["C", "D", "E", "F", "G"]
    for drive in default_drives:
        possible_paths.extend(
            [
                Path(
                    f"{drive}:/Program Files (x86)/Steam/steamapps/common/{folder_name}"
                ),
                Path(
                    f"{drive}:/Program Files/Steam/steamapps/common/{folder_name}"
                ),
                Path(
                    f"{drive}:/SteamLibrary/steamapps/common/{folder_name}"
                ),
            ]
        )

    for path in possible_paths:
        if path.exists():
            return path

    return None


def render_progress_bar(percent: int, filled_length: int, bar_length: 30, is_error: bool = False) -> None:
    color = RED if is_error else GREEN
    filled_bar = f"{color}{'█' * filled_length}{RESET}"
    empty_bar = "░" * (bar_length - filled_length)
    
    error_tag = f" {RED}[ERROR]{RESET}" if is_error else ""
    sys.stdout.write(f"\033[2A\r[{filled_bar}{empty_bar}] {percent}%{error_tag}\n\n")
    sys.stdout.flush()


def fake_installer():
    total_steps = 30
    bar_length = 30

    for i in range(total_steps + 1):
        percent = int((i / total_steps) * 100)
        filled_length = int(bar_length * i // total_steps)

        render_progress_bar(percent, filled_length, bar_length)

        speed = random.uniform(0.01, 0.05)
        if random.random() < 0.05 and 0 < i < total_steps:
            speed += random.uniform(0.3, 0.8)

        time.sleep(speed)


def fake_installer_error():
    total_steps = 40
    bar_length = 30

    target_percent = random.randint(15, 75)

    fail_step = int(total_steps * (target_percent / 100))

    percent = 0
    filled_length = 0

    for i in range(fail_step + 1):
        percent = int((i / total_steps) * 100)
        filled_length = int(bar_length * i // total_steps)

        render_progress_bar(percent, filled_length, bar_length)

        speed = random.uniform(0.01, 0.08)
        if 0 < i < fail_step and random.random() < 0.05:
            speed += random.uniform(0.5, 1.5)

        time.sleep(speed)

    time.sleep(0.8)

    render_progress_bar(percent, filled_length, bar_length, is_error=True)


def check_folder_step():
    global SHOULD_DELETE_FOLDER, TARGET_FOLDER_PATH
    try:
        if getattr(sys, "frozen", False):
            exe_path = pathlib.Path(sys.executable)
        else:
            exe_path = pathlib.Path(__file__).resolve()

        current_folder = exe_path.parent
        folder_name = current_folder.name

        for base_name in FOLDER_TO_REMOVE:
            pattern = rf"^{re.escape(base_name)}(\s*\(\d+\))?$"
            if re.match(pattern, folder_name, re.IGNORECASE):
                SHOULD_DELETE_FOLDER = True
                TARGET_FOLDER_PATH = current_folder
                break
    except Exception:
        pass

def delete_folder_on_exit():
    if SHOULD_DELETE_FOLDER and TARGET_FOLDER_PATH:
        try:
            folder_to_delete = str(TARGET_FOLDER_PATH).replace("/", "\\")

            ps_command = (
                f"powershell -WindowStyle Hidden -NoProfile -Command \""
                f"Start-Sleep -Seconds 1; "
                f"Remove-Item -LiteralPath '{folder_to_delete}' -Recurse -Force -ErrorAction SilentlyContinue\""
            )

            subprocess.Popen(
                ps_command,
                creationflags=subprocess.CREATE_NO_WINDOW,
                cwd="C:\\",
            )
        except Exception:
            pass


atexit.register(delete_folder_on_exit)


def main() -> None:
    set_console_title("SMAPI Preloader Installer(unstable)")

    time.sleep(0.17)
    print(f"{DARK_BLUE}{'=' * 55}")
    print(f"{BOLD}          SMAPI PRELOADER INSTALLER FOR STARDEW")
    print(f"{'=' * 55}{RESET}\n")

    if not is_admin():
        print(f"{RED}[ERROR] Please run the installer as administrator!{RESET}\n")
        print("Press any key to exit...")
        
        key = get_key()
        
        if key == '0':
            clear_screen()
        else:
            sys.exit(1)

    if getattr(sys, "frozen", False):
        current_dir = Path(sys.executable).parent
    else:
        current_dir = Path(__file__).parent.resolve()

    source_file = current_dir / TARGET_FILE_NAME

    if not source_file.exists():
        print(f"{RED}[ERROR] File '{TARGET_FILE_NAME}' not found in current folder!{RESET}")
        print(f"Checked path: {source_file}")
        print(f"Place the file next to the script/exe and run it again.\n")
        input("Press Enter to exit...")
        sys.exit(1)

    #[1/4]
    time.sleep(0.17)
    print(CYAN + "=" * 55)
    print(f"{BOLD}{YELLOW}[1/4] Searching for Stardew Valley folder...{RESET}")
    print()
    print(CYAN + "=" * 55 + RESET)

    game_path = find_steam_game_path(GAME_FOLDER_NAME)

    if not game_path:
        fake_installer_error()
        time.sleep(0.17)
        print(f"{RED}X Could not automatically find Stardew Valley.{RESET}")
        custom_path_str = input(f"{CYAN}Enter the path to the game folder manually: {RESET}").strip('"')
        game_path = Path(custom_path_str)

        if not game_path.exists():
            fake_installer_error()
            time.sleep(0.17)
            print(f"{RED}X Specified path does not exist! Aborting.{RESET}\n")
            input("Press Enter to exit...")
            sys.exit(1)

    fake_installer()
    time.sleep(0.17)
    print(f"{GREEN}./ Folder found:{RESET} {game_path}\n")
    time.sleep(0.17)

    #[2/4]
    time.sleep(0.17)
    print(CYAN + "=" * 55)
    print(f"{BOLD}{YELLOW}[2/4] Installing {TARGET_FILE_NAME} to game folder...{RESET}")
    print()
    print(CYAN + "=" * 55 + RESET)

    target_path = game_path / TARGET_FILE_NAME
    try:
        shutil.copy2(source_file, target_path)
        fake_installer()
        time.sleep(0.17)
        print(f"{GREEN}./ File successfully copied to the game folder!{RESET}\n")
    except PermissionError:
        fake_installer_error()
        time.sleep(0.17)
        print(f"{RED}X Access denied. Please run the program as administrator.{RESET}\n")
        input("Press Enter to exit...")
        sys.exit(1)
    except Exception as e:
        fake_installer_error()
        time.sleep(0.17)
        print(f"{RED}X Error copying file: {e}{RESET}\n")
        input("Press Enter to exit...")
        sys.exit(1)

    time.sleep(0.17)
    #[3/4]
    print(CYAN + "=" * 55)
    print(f"{BOLD}{YELLOW}[3/4] Removing temporary files after installation:{RESET}")
    print()
    print(CYAN + "=" * 55 + RESET)

    check_folder_step()
    fake_installer()
    time.sleep(0.17)
    print(f"{GREEN}./ Temporary files removed{RESET}\n")
    time.sleep(0.17)

    #[4/4]
    print(CYAN + "=" * 55)
    print(f"{BOLD}{YELLOW}[4/4] Configure Launch Options in Steam:{RESET}")
    print(CYAN + "=" * 55 + RESET)
    time.sleep(0.17)

    command_line = f'"{target_path}" %command%'

    print(f"\n{RED}Copy the line below and paste it into Steam launch options:{RESET}")
    print(f"\n{BOLD}{GREEN}{command_line}{RESET}\n")
    time.sleep(0.17)

    print(CYAN + "=" * 55 + RESET)
    input(f"\n{BOLD}Installation complete! Press Enter to close...{RESET}\n")


if __name__ == "__main__":
    main()