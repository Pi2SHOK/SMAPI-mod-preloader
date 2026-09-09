import os
import shutil
import sys
import msvcrt
import urllib.request
import json
import subprocess
import ctypes
import zipfile

CURRENT_VERSION = "v1.2.1"

GITHUB_API_URL = "https://api.github.com/repos/Pi2SHOK/SMAPI-mod-preloader/releases/latest"
GITHUB_RELEASE_URL = "https://github.com/Pi2SHOK/SMAPI-mod-preloader/releases/latest"

SMAPI_EXE = "StardewModdingAPI.exe"
TARGET_EXE_NAME = "SMAPImodpreloader.exe"
MODS_FOLDER = "Mods"

NEW_VERSION_AVAILABLE = False
LATEST_VERSION_STR = ""
LATEST_DOWNLOAD_URL = ""

STATE_FILE = ".active_profile"

class Color:
    RESET = "\033[0m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    DARK_BLUE = "\033[34m"

if os.name == 'nt':
    os.system('')


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def parse_version(v_str):
    clean_str = v_str.lstrip('v').strip()
    return tuple(map(int, clean_str.split('.')))


def print_header():
    clear_screen()
    print(f"{Color.GREEN}=====================")
    print(" SMAPI Mod Preloader ")
    print(f"====================={Color.RESET}\n")


def get_key():
    char = msvcrt.getch()
    try:
        return char.decode('utf-8')
    except UnicodeDecodeError:
        return ''


def restore_active_profile():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                active_name = f.read().strip()
            
            if active_name and os.path.exists(MODS_FOLDER):
                target_folder = f"Mods_{active_name}"
                if not os.path.exists(target_folder):
                    os.rename(MODS_FOLDER, target_folder)
            
            os.remove(STATE_FILE)
        except Exception:
            pass


def get_profiles():
    profiles = []
    for item in os.listdir("."):
        if os.path.isdir(item) and item.startswith("Mods_") and item != "Mods_Backup":
            creation_time = os.path.getctime(item)
            profile_name = item[5:]
            profiles.append((creation_time, profile_name))

    profiles.sort(key=lambda x: x[0])
    return [name for _, name in profiles]


def run_smapi(profile_name):
    profile_folder = f"Mods_{profile_name}"
    
    if os.path.exists(MODS_FOLDER) and not os.path.islink(MODS_FOLDER):
        if not os.path.exists("Mods_Backup"):
            os.rename(MODS_FOLDER, "Mods_Backup")

    if os.path.exists(profile_folder):
        os.rename(profile_folder, MODS_FOLDER)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            f.write(profile_name)
    
    print(f"\n{Color.CYAN}Launching SMAPI with profile '{profile_name}'...{Color.RESET}")

    if os.name == 'nt':
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd != 0:
            ctypes.windll.user32.ShowWindow(hwnd, 0)

    try:
        subprocess.run([SMAPI_EXE])
    except Exception:
        pass
    
    restore_active_profile()
    sys.exit()


def check_for_updates():
    global NEW_VERSION_AVAILABLE, LATEST_VERSION_STR, LATEST_DOWNLOAD_URL
    
    try:
        req = urllib.request.Request(
            GITHUB_API_URL, 
            headers={'User-Agent': 'SMAPI-Mod-Preloader-App'}
        )
        with urllib.request.urlopen(req, timeout=3.0) as response:
            data = json.loads(response.read().decode())
            latest_version_str = data.get("tag_name", "").strip()
            
            if latest_version_str:
                latest_ver = parse_version(latest_version_str)
                current_ver = parse_version(CURRENT_VERSION)
                
                if latest_ver > current_ver:
                    NEW_VERSION_AVAILABLE = True
                    LATEST_VERSION_STR = latest_version_str
                    LATEST_DOWNLOAD_URL = f"https://github.com/Pi2SHOK/SMAPI-mod-preloader/releases/download/{latest_version_str}/SMAPI-mod-preloader-main.zip"
                    return

    except Exception:
        pass

    try:
        req = urllib.request.Request(
            GITHUB_RELEASE_URL, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=3.0) as response:
            final_url = response.geturl()
            latest_version_str = final_url.split('/')[-1].strip()
            
            if latest_version_str and latest_version_str != "latest":
                latest_ver = parse_version(latest_version_str)
                current_ver = parse_version(CURRENT_VERSION)
                
                if latest_ver > current_ver:
                    NEW_VERSION_AVAILABLE = True
                    LATEST_VERSION_STR = latest_version_str
                    LATEST_DOWNLOAD_URL = f"https://github.com/Pi2SHOK/SMAPI-mod-preloader/releases/download/{latest_version_str}/SMAPI-mod-preloader-main.zip"
    except Exception:
        pass


def download_progress(url, dest_path):
    req = urllib.request.Request(url, headers={'User-Agent': 'SMAPI-Mod-Preloader-App'})
    with urllib.request.urlopen(req) as response:
        total_size = response.getheader('Content-Length')
        if total_size is not None:
            total_size = int(total_size)
        
        downloaded = 0
        block_size = 8192
        
        with open(dest_path, "wb") as f:
            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                f.write(buffer)
                downloaded += len(buffer)
                
                if total_size:
                    percent = downloaded / total_size * 100
                    bar_length = 30
                    filled = int(bar_length * downloaded // total_size)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    mb_downloaded = downloaded / (1024 * 1024)
                    mb_total = total_size / (1024 * 1024)
                    sys.stdout.write(f"\r{Color.YELLOW}Downloading: [{bar}] {percent:.1f}% ({mb_downloaded:.2f}/{mb_total:.2f} MB){Color.RESET}")
                else:
                    mb_downloaded = downloaded / (1024 * 1024)
                    sys.stdout.write(f"\r{Color.YELLOW}Downloading: {mb_downloaded:.2f} MB{Color.RESET}")
                sys.stdout.flush()
        print()


def update_self():
    print_header()
    
    if not LATEST_DOWNLOAD_URL:
        print(f"{Color.RED}Error: Release archive not found on GitHub!{Color.RESET}")
        print(f"{Color.RED}Try to download it manually from the GitHub releases page.{Color.RESET}")
        input("\nPress Enter to return...")
        return

    print(f"{Color.YELLOW}Starting update to {LATEST_VERSION_STR}...{Color.RESET}")

    current_exe = os.path.abspath(sys.argv[0])
    temp_download = os.path.abspath("update_download.tmp")
    extract_folder = os.path.abspath("update_extracted")
    temp_new_exe = os.path.abspath(current_exe + ".new")
    bat_file = os.path.abspath("update_temp.bat")

    try:
        download_progress(LATEST_DOWNLOAD_URL, temp_download)
        print(f"{Color.YELLOW}Extracting archive...{Color.RESET}")

        if zipfile.is_zipfile(temp_download):
            with zipfile.ZipFile(temp_download, 'r') as zip_ref:
                zip_ref.extractall(extract_folder)
            
            extracted_exe = None
            for root, dirs, files in os.walk(extract_folder):
                for file in files:
                    if file.lower() == TARGET_EXE_NAME.lower():
                        extracted_exe = os.path.join(root, file)
                        break
                if extracted_exe:
                    break
            
            if not extracted_exe:
                for root, dirs, files in os.walk(extract_folder):
                    for file in files:
                        if file.endswith(".exe"):
                            extracted_exe = os.path.join(root, file)
                            break
                    if extracted_exe:
                        break

            if not extracted_exe:
                raise Exception(f"Executable file '{TARGET_EXE_NAME}' not found inside downloaded ZIP archive!")
            
            shutil.copy(extracted_exe, temp_new_exe)
        else:
            shutil.copy(temp_download, temp_new_exe)

        print(f"{Color.GREEN}Update downloaded successfully!{Color.RESET}")
        input("\nPress Enter to restart Preloader...")

        bat_content = f"""@echo off
timeout /t 2 /nobreak > nul
:retry
copy /y "{temp_new_exe}" "{current_exe}" > nul
if errorlevel 1 (
    timeout /t 1 /nobreak > nul
    goto retry
)
del /f /q "{temp_new_exe}" > nul
if exist "{temp_download}" del /f /q "{temp_download}" > nul
if exist "{extract_folder}" rmdir /s /q "{extract_folder}" > nul
start "" "{current_exe}"
del "%~f0"
"""
        with open(bat_file, "w", encoding="utf-8") as f:
            f.write(bat_content)

        os.startfile(bat_file)
        sys.exit()

    except urllib.error.HTTPError as e:
        print(f"{Color.RED}Failed to update (Server Error): HTTP {e.code} - {e.reason}{Color.RESET}")
    except urllib.error.URLError as e:
        print(f"{Color.RED}Failed to update (Network Error): {e.reason}{Color.RESET}")
    except zipfile.BadZipFile:
        print(f"{Color.RED}Failed to update: Downloaded file is corrupted or not a valid ZIP archive.{Color.RESET}")
    except Exception as e:
        print(f"{Color.RED}Failed to update: {e}{Color.RESET}")
    finally:
        if os.path.exists(temp_download):
            try: os.remove(temp_download)
            except Exception: pass
        if os.path.exists(extract_folder):
            try: shutil.rmtree(extract_folder, ignore_errors=True)
            except Exception: pass

    input("\nPress Enter to return to menu...")


def settings_menu():
    while True:
        print_header()
        print(f"{Color.DARK_BLUE}Current version: {CURRENT_VERSION}{Color.RESET}")
        print("")
        print(f"{Color.YELLOW}--- SETTINGS MENU ---{Color.RESET}")
        print("[1] Create a new profile")
        print("[2] Rename a profile")
        print("[3] Delete a profile")
        
        if NEW_VERSION_AVAILABLE:
            print(f"{Color.YELLOW}[4] Update program to {LATEST_VERSION_STR}{Color.RESET}")

        print("[6] Uninstall this program")
        print("[0] Back to main menu\n")

        key = get_key()

        if key == '1':
            print_header()
            profiles = get_profiles()
            
            if len(profiles) >= 9:
                print(f"{Color.RED}Cannot create new profile! Limit reached (maximum 9 profiles).{Color.RESET}")
            else:
                print("Enter new profile name (or '0' to cancel):")
                name = input("> ").strip()
                
                if name == '0' or not name:
                    print(f"{Color.YELLOW}Creation cancelled.{Color.RESET}")
                elif name.lower() == "backup":
                    print(f"{Color.RED}Name 'Backup' is reserved by the system!{Color.RESET}")
                else:
                    folder_name = f"Mods_{name}"
                    if not os.path.exists(folder_name):
                        os.makedirs(folder_name)
                        print(f"{Color.GREEN}Profile '{name}' successfully created!{Color.RESET}")
                    else:
                        print(f"{Color.RED}A profile with this name already exists!{Color.RESET}")

            input("\nPress Enter to continue...")

        elif key == '2':
            profiles = get_profiles()
            if not profiles:
                print(f"{Color.RED}\nNo profiles available.{Color.RESET}")
                input("\nPress Enter to continue...")
                continue

            print_header()
            print("Select profile to rename:")
            for idx, p in enumerate(profiles, 1):
                print(f"[{idx}] {p}")
            print("[0] Cancel")
            
            choice_key = get_key()
            if choice_key == '0':
                continue
            elif choice_key.isdigit():
                choice = int(choice_key) - 1
                if 0 <= choice < len(profiles):
                    old_name = profiles[choice]
                    print_header()
                    print(f"Selected profile: {old_name}")
                    print("Enter new profile name (or '0' to cancel):")
                    new_name = input("> ").strip()
                    
                    if new_name == '0' or not new_name:
                        print(f"{Color.YELLOW}Renaming cancelled.{Color.RESET}")
                    elif new_name.lower() == "backup":
                        print(f"{Color.RED}Name 'Backup' is reserved by the system!{Color.RESET}")
                    else:
                        os.rename(f"Mods_{old_name}", f"Mods_{new_name}")
                        print(f"{Color.GREEN}Profile renamed successfully!{Color.RESET}")
                    input("\nPress Enter to continue...")

        elif key == '3':
            profiles = get_profiles()
            if not profiles:
                print(f"{Color.RED}\nNo profiles available.{Color.RESET}")
                input("\nPress Enter to continue...")
                continue

            print_header()
            print("Select profile to delete:")
            for idx, p in enumerate(profiles, 1):
                print(f"[{idx}] {p}")
            print("[0] Cancel")
            
            choice_key = get_key()
            if choice_key == '0':
                continue
            elif choice_key.isdigit():
                choice = int(choice_key) - 1
                if 0 <= choice < len(profiles):
                    target_name = profiles[choice]
                    print_header()
                    print(f"{Color.RED}Delete profile '{target_name}'?{Color.RESET}")
                    print("[1] Yes")
                    print("[2] No")
                    
                    confirm = get_key()
                    if confirm == '1':
                        shutil.rmtree(f"Mods_{target_name}")
                        print(f"{Color.GREEN}\nProfile '{target_name}' deleted.{Color.RESET}")
                    else:
                        print(f"{Color.YELLOW}\nDeletion cancelled.{Color.RESET}")
                    input("\nPress Enter to continue...")

        elif key == '4' and NEW_VERSION_AVAILABLE:
            update_self()

        elif key == '6':
            print_header()
            print(f"{Color.RED}Are you sure you want to uninstall this program?{Color.RESET}")
            print("[1] Yes")
            print("[2] No")
            
            confirm = get_key()
            if confirm == '1':
                print_header()
                
                if os.path.exists("Mods_Backup"):
                    if not os.path.exists(MODS_FOLDER):
                        os.rename("Mods_Backup", MODS_FOLDER)
                        print(f"{Color.GREEN}Mods_Backup folder successfully restored to 'Mods'!{Color.RESET}\n")
                    else:
                        print(f"{Color.YELLOW}Folder 'Mods' already exists, Mods_Backup left unchanged.{Color.RESET}\n")

                if os.path.exists(STATE_FILE):
                    os.remove(STATE_FILE)

                print(f"{Color.GREEN}Preloader program successfully uninstalled!{Color.RESET}\n")
                
                smapi_path = os.path.abspath(SMAPI_EXE)
                print(f"{Color.YELLOW}Change your Steam launch options back to:{Color.RESET}")
                print(f'{Color.CYAN}"{smapi_path}" %command%{Color.RESET}\n')

                input("Press Enter to close and remove the program...")
                
                exe_path = os.path.abspath(sys.argv[0])
                bat_file = os.path.abspath("uninstall_temp.bat")
                bat_content = f"""@echo off
timeout /t 2 /nobreak > nul
:retry
del /f /q "{exe_path}" > nul
if exist "{exe_path}" (
    timeout /t 1 /nobreak > nul
    goto retry
)
del "%~f0"
"""
                with open(bat_file, "w", encoding="utf-8") as f:
                    f.write(bat_content)

                os.startfile(bat_file)
                sys.exit()

        elif key == '0':
            break


def main():
    if os.name == 'nt':
        os.system('title SMAPI Mod Preloader')

    restore_active_profile()
    check_for_updates()

    while True:
        print_header()
        
        if NEW_VERSION_AVAILABLE:
            print(f"{Color.YELLOW}[!] New update available: {LATEST_VERSION_STR} (Current: {CURRENT_VERSION}){Color.RESET}")
            print(f"{Color.YELLOW}    Go to the [0] Settings menu and press [4] Update{Color.RESET}")
            print(f"{Color.YELLOW}    or download at: {GITHUB_RELEASE_URL}{Color.RESET}\n")

        profiles = get_profiles()

        if profiles:
            print("Available profiles:")
            for idx, profile in enumerate(profiles, 1):
                print(f"[{idx}] {profile}")
            print()
        else:
            print(f"{Color.RED}No profiles found. Create a new one in settings.{Color.RESET}\n")

        print("[0] Settings menu")

        key = get_key()

        if key == '0':
            settings_menu()
        elif key.isdigit():
            idx = int(key) - 1
            if 0 <= idx < len(profiles):
                run_smapi(profiles[idx])


if __name__ == "__main__":
    main()