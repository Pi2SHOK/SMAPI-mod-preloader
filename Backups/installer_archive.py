import os
import shutil
import sys
import winreg
from pathlib import Path

# Поддержка ANSI-цветов в консоли Windows
os.system("")

# Палитра цветов для консоли
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"
DARK_BLUE = "\033[34m"

GAME_FOLDER_NAME = "Stardew Valley"
TARGET_FILE_NAME = "SMAPImodpreloader.exe"


def set_console_title(title: str) -> None:
    if os.name == "nt":
        import ctypes

        ctypes.windll.kernel32.SetConsoleTitleW(title)


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


def main() -> None:
    set_console_title("SMAPI Preloader Installer")

    # Заголовок
    print(f"{DARK_BLUE}{'=' * 55}")
    print(f"{BOLD}          SMAPI PRELOADER INSTALLER FOR STARDEW")
    print(f"{'=' * 55}{RESET}\n")

    # Определение пути к файлу
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

    # Пункт [1/3]
    print(CYAN + "=" * 55)
    print(f"{BOLD}{YELLOW}[1/3] Searching for Stardew Valley folder...{RESET}")
    print(CYAN + "=" * 55 + RESET)

    game_path = find_steam_game_path(GAME_FOLDER_NAME)

    if not game_path:
        print(f"{RED}X Could not automatically find Stardew Valley.{RESET}")
        custom_path_str = input(f"{CYAN}Enter the path to the game folder manually: {RESET}").strip('"')
        game_path = Path(custom_path_str)

        if not game_path.exists():
            print(f"{RED}X Specified path does not exist! Aborting.{RESET}\n")
            input("Press Enter to exit...")
            sys.exit(1)

    print(f"{GREEN}./ Folder found:{RESET} {game_path}\n")

    # Пункт [2/3]
    print(CYAN + "=" * 55)
    print(f"{BOLD}{YELLOW}[2/3] Installing {TARGET_FILE_NAME} to game folder...{RESET}")
    print(CYAN + "=" * 55 + RESET)

    target_path = game_path / TARGET_FILE_NAME
    try:
        shutil.copy2(source_file, target_path)
        print(f"{GREEN}./ File successfully copied to the game folder!{RESET}\n")
    except PermissionError:
        print(f"{RED}X Access denied. Please run the program as administrator.{RESET}\n")
        input("Press Enter to exit...")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}X Error copying file: {e}{RESET}\n")
        input("Press Enter to exit...")
        sys.exit(1)

    # Пункт [3/3]
    print(CYAN + "=" * 55)
    print(f"{BOLD}{YELLOW}[3/3] Configure Launch Options in Steam:{RESET}")
    print(CYAN + "=" * 55 + RESET)

    command_line = f'"{target_path}" %command%'

    print(f"\n{RED}Copy the line below and paste it into Steam launch options:{RESET}")
    print(f"\n{BOLD}{GREEN}{command_line}{RESET}\n")

    print(CYAN + "=" * 55 + RESET)
    input(f"\n{BOLD}Installation complete! Press Enter to close...{RESET}")


if __name__ == "__main__":
    main()