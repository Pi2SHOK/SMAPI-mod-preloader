import os
import shutil
import sys
import msvcrt
import urllib.request
import json
import subprocess
import ctypes
import zipfile

CURRENT_VERSION = "v1.2.0"          
GITHUB_API_URL = "https://api.github.com/repos/Pi2SHOK/SMAPI-mod-preloader/releases/latest"
GITHUB_RELEASE_URL = "https://github.com/Pi2SHOK/SMAPI-mod-preloader/releases/latest"
SMAPI_EXE = "StardewModdingAPI.exe"
MODS_FOLDER = "Mods"
STATE_FILE = ".active_profile"
TARGET_EXE_NAME = "SMAPImodpreloader.exe"

NEW_VERSION_AVAILABLE = False
LATEST_VERSION_STR = ""
LATEST_DOWNLOAD_URL = ""

if os.name == 'nt':
    os.system('')


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def parse_version(v_str):
    clean_str = v_str.lstrip('v').strip()
    return tuple(map(int, clean_str.split('.')))


def print_header():
    clear_screen()
    print("\033[32m=====================")
    print(" SMAPI Mod Preloader ")
    print("=====================\033[0m\n")


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
    
    print(f"\n\033[36mLaunching SMAPI with profile '{profile_name}'...\033[0m")

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
                    sys.stdout.write(f"\r\033[33mDownloading: [{bar}] {percent:.1f}% ({mb_downloaded:.2f}/{mb_total:.2f} MB)\033[0m")
                else:
                    mb_downloaded = downloaded / (1024 * 1024)
                    sys.stdout.write(f"\r\033[33mDownloading: {mb_downloaded:.2f} MB\033[0m")
                sys.stdout.flush()
        print()


def update_self():
    print_header()
    
    if not LATEST_DOWNLOAD_URL:
        print("\033[31mError: Release archive not found on GitHub!\033[0m")
        print("\033[31mTry to download it manually from the GitHub releases page.\033[0m")
        input("\nPress Enter to return...")
        return

    print(f"\033[33mStarting update to {LATEST_VERSION_STR}...\033[0m")
    
    current_exe = os.path.abspath(sys.argv[0])
    temp_download = "update_download.tmp"
    extract_folder = "update_extracted"
    temp_new_exe = current_exe + ".new"
    bat_file = "update_temp.bat"

    try:
        download_progress(LATEST_DOWNLOAD_URL, temp_download)
        print("\033[33mExtracting archive...\033[0m")

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

        print("\033[32mUpdate downloaded successfully!\033[0m")
        input("\nPress Enter to restart Preloader...")

        bat_content = f"""@echo off
timeout /t 1 /nobreak > nul
move /y "{temp_new_exe}" "{current_exe}" > nul
if exist "{temp_download}" del /f /q "{temp_download}"
if exist "{extract_folder}" rmdir /s /q "{extract_folder}"
start "" "{current_exe}"
del "%~f0"
"""
        with open(bat_file, "w", encoding="utf-8") as f:
            f.write(bat_content)

        subprocess.Popen([bat_file], shell=True)
        sys.exit()

    except urllib.error.HTTPError as e:
        print(f"\033[31mFailed to update (Server Error): HTTP {e.code} - {e.reason}\033[0m")
        if e.code == 404:
            print("\033[31mReason: The requested file was not found on GitHub. Check file name in release.\033[0m")
    except urllib.error.URLError as e:
        print(f"\033[31mFailed to update (Network Error): {e.reason}\033[0m")
        print("\033[31mReason: Connection failed. Check your internet connection or firewall.\033[0m")
    except zipfile.BadZipFile:
        print("\033[31mFailed to update: Downloaded file is corrupted or not a valid ZIP archive.\033[0m")
    except Exception as e:
        print(f"\033[31mFailed to update: {e}\033[0m")
    finally:
        if os.path.exists(temp_download):
            try: os.remove(temp_download)
            except Exception: pass
        if os.path.exists(extract_folder):
            try: shutil.rmtree(extract_folder, ignore_errors=True)
            except Exception: pass
        if os.path.exists(temp_new_exe):
            try: os.remove(temp_new_exe)
            except Exception: pass
        if os.path.exists(bat_file):
            try: os.remove(bat_file)
            except Exception: pass

    input("\nPress Enter to return to menu...")


def settings_menu():
    while True:
        print_header()
        print(f"\033[34mCurrent version: {CURRENT_VERSION}\033[0m")
        print("")
        print("\033[33m--- SETTINGS MENU ---\033[0m")
        print("[1] Create a new profile")
        print("[2] Rename a profile")
        print("[3] Delete a profile")
        
        if NEW_VERSION_AVAILABLE:
            print(f"\033[33m[4] Update program to {LATEST_VERSION_STR}\033[0m")

        print("[6] Uninstall this program")
        print("[0] Back to main menu\n")

        key = get_key()

        if key == '1':
            print_header()
            profiles = get_profiles()
            
            if len(profiles) >= 9:
                print("\033[31mCannot create new profile! Limit reached (maximum 9 profiles).\033[0m")
            else:
                print("Enter new profile name (or '0' to cancel):")
                name = input("> ").strip()
                
                if name == '0' or not name:
                    print("\033[33mCreation cancelled.\033[0m")
                elif name.lower() == "backup":
                    print("\033[31mName 'Backup' is reserved by the system!\033[0m")
                else:
                    folder_name = f"Mods_{name}"
                    if not os.path.exists(folder_name):
                        os.makedirs(folder_name)
                        print(f"\033[32mProfile '{name}' successfully created!\033[0m")
                    else:
                        print("\033[31mA profile with this name already exists!\033[0m")
            
            input("\nPress Enter to continue...")

        elif key == '2':
            profiles = get_profiles()
            if not profiles:
                print("\033[31m\nNo profiles available.\033[0m")
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
                        print("\033[33mRenaming cancelled.\033[0m")
                    elif new_name.lower() == "backup":
                        print("\033[31mName 'Backup' is reserved by the system!\033[0m")
                    else:
                        os.rename(f"Mods_{old_name}", f"Mods_{new_name}")
                        print("\033[32mProfile renamed successfully!\033[0m")
                    input("\nPress Enter to continue...")

        elif key == '3':
            profiles = get_profiles()
            if not profiles:
                print("\033[31m\nNo profiles available.\033[0m")
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
                    print(f"\033[31mDelete profile '{target_name}'?\033[0m")
                    print("[1] Yes")
                    print("[2] No")
                    
                    confirm = get_key()
                    if confirm == '1':
                        shutil.rmtree(f"Mods_{target_name}")
                        print(f"\033[32m\nProfile '{target_name}' deleted.\033[0m")
                    else:
                        print("\nDeletion cancelled.")
                    input("\nPress Enter to continue...")

        elif key == '4' and NEW_VERSION_AVAILABLE:
            update_self()

        elif key == '6':
            print_header()
            print("\033[31mAre you sure you want to uninstall this program?\033[0m")
            print("[1] Yes")
            print("[2] No")
            
            confirm = get_key()
            if confirm == '1':
                print_header()
                
                if os.path.exists("Mods_Backup"):
                    if not os.path.exists(MODS_FOLDER):
                        os.rename("Mods_Backup", MODS_FOLDER)
                        print("\033[32mMods_Backup folder successfully restored to 'Mods'!\033[0m\n")
                    else:
                        print("\033[33mFolder 'Mods' already exists, Mods_Backup left unchanged.\033[0m\n")

                if os.path.exists(STATE_FILE):
                    os.remove(STATE_FILE)

                print("\033[32mPreloader program successfully uninstalled!\033[0m\n")
                
                smapi_path = os.path.abspath(SMAPI_EXE)
                print("\033[33mChange your Steam launch options back to:\033[0m")
                print(f'\033[36m"{smapi_path}" %command%\033[0m\n')
                
                input("Press Enter to close and remove the program...")
                
                exe_path = os.path.abspath(sys.argv[0])
                bat_file = "uninstall_temp.bat"
                bat_content = f"""@echo off
timeout /t 1 /nobreak > nul
del /f /q "{exe_path}"
del "%~f0"
"""
                with open(bat_file, "w", encoding="utf-8") as f:
                    f.write(bat_content)
                subprocess.Popen([bat_file], shell=True)
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
            print(f"\033[33m[!] New update available: {LATEST_VERSION_STR} (Current: {CURRENT_VERSION})\033[0m")
            print(f"\033[33m    Go to the [0] Settings menu and press [4] Update\033[0m")
            print(f"\033[33m    or download at: {GITHUB_RELEASE_URL}\033[0m\n")

        profiles = get_profiles()

        if profiles:
            print("Available profiles:")
            for idx, profile in enumerate(profiles, 1):
                print(f"[{idx}] {profile}")
            print()
        else:
            print("\033[31mNo profiles found. Create a new one in settings.\033[0m\n")

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