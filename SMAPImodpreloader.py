import os
import shutil
import sys
import msvcrt
import urllib.request
import json
import subprocess
import zipfile
import urllib.error

CURRENT_VERSION = "v1.2.2"

GITHUB_API_URL = "https://api.github.com/repos/Pi2SHOK/SMAPI-mod-preloader/releases/latest"

SMAPI_EXE = "StardewModdingAPI.exe"
TARGET_EXE_NAME = "SMAPImodpreloader.exe"
MODS_FOLDER = "Mods"

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
    if not isinstance(v_str, str):
        raise ValueError("Version must be a string")

    clean_str = v_str.strip()
    if clean_str.lower().startswith("v"):
        clean_str = clean_str[1:]

    parts = clean_str.split(".")

    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        raise ValueError(f"Invalid version format: {v_str}")

    return tuple(map(int, parts))


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
        if (
            os.path.isdir(item)
            and item.startswith("Mods_")
            and item != "Mods_Backup"
            and len(item) > len("Mods_")
        ):
            creation_time = os.path.getctime(item)
            profile_name = item[len("Mods_"):]
            profiles.append((creation_time, profile_name))

    profiles.sort(key=lambda x: x[0])
    return [name for _, name in profiles]


def run_smapi(profile_name):
    profile_folder = f"Mods_{profile_name}"
    smapi_path = os.path.abspath(SMAPI_EXE)

    if not os.path.isfile(smapi_path):
        print(f"{Color.RED}SMAPI не найден: {smapi_path}{Color.RESET}")
        input("\nPress Enter to continue...")
        return

    if not os.path.isdir(profile_folder):
        print(f"{Color.RED}Profile not found: {profile_name}{Color.RESET}")
        input("\nPress Enter to continue...")
        return

    if os.path.exists(MODS_FOLDER) and not os.path.islink(MODS_FOLDER):
        if os.path.exists("Mods_Backup"):
            print(f"{Color.RED}Mods_Backup already exists.{Color.RESET}")
            input("\nPress Enter to continue...")
            return
        os.rename(MODS_FOLDER, "Mods_Backup")

    os.rename(profile_folder, MODS_FOLDER)

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(profile_name)

    print(f"\n{Color.CYAN}Launching SMAPI with profile '{profile_name}'...{Color.RESET}")

    try:
        subprocess.run([smapi_path], cwd=os.path.dirname(smapi_path), check=False)
    except OSError as error:
        print(f"{Color.RED}Failed to launch SMAPI: {error}{Color.RESET}")
    finally:
        restore_active_profile()

    sys.exit()


def check_for_updates():
    try:
        req = urllib.request.Request(
            GITHUB_API_URL,
            headers={"User-Agent": "SMAPI-Mod-Preloader-App"},
        )

        with urllib.request.urlopen(req, timeout=3.0) as response:
            data = json.loads(response.read().decode())
            latest = data.get("tag_name", "").strip()

        if latest and parse_version(latest) > parse_version(CURRENT_VERSION):
            download_url = (
                "https://github.com/Pi2SHOK/SMAPI-mod-preloader/"
                f"releases/download/{latest}/"
                "SMAPI-mod-preloader-main.zip"
            )
            return True, latest, download_url

    except Exception:
        pass

    return False, "", ""


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


def update_self(latest_version_str, latest_download_url):
    print_header()

    if not latest_download_url:
        print(f"{Color.RED}Error: Release archive not found on GitHub!{Color.RESET}")
        input("\nPress Enter to return...")
        return

    print(f"{Color.YELLOW}Starting update to {latest_version_str}...{Color.RESET}")

    current_exe = os.path.abspath(sys.argv[0])
    temp_download = os.path.abspath("update_download.tmp")
    extract_folder = os.path.abspath("update_extracted")
    temp_new_exe = os.path.abspath(current_exe + ".new")
    bat_file = os.path.abspath("update_temp.bat")

    update_scheduled = False

    try:
        download_progress(latest_download_url, temp_download)

        print(f"{Color.YELLOW}Extracting archive...{Color.RESET}")

        with zipfile.ZipFile(temp_download, "r") as zip_ref:
            base_path = os.path.abspath(extract_folder)

            for member in zip_ref.infolist():
                target_path = os.path.abspath(
                    os.path.join(extract_folder, member.filename)
                )

                if not target_path.startswith(base_path + os.sep):
                    raise ValueError("Unsafe path in ZIP archive")

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

        update_scheduled = True
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
        if not update_scheduled:
            for path in (temp_download, temp_new_exe, bat_file):
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except OSError:
                        pass

            if os.path.exists(extract_folder):
                shutil.rmtree(extract_folder, ignore_errors=True)

    input("\nPress Enter to return to menu...")


def settings_menu(update_available, latest_version_str, latest_download_url):
    while True:
        print_header()
        print(f"{Color.DARK_BLUE}Current version: {CURRENT_VERSION}{Color.RESET}")
        print("")
        print(f"{Color.YELLOW}--- SETTINGS MENU ---{Color.RESET}")
        print("[1] Create a new profile")
        print("[2] Rename a profile")
        print("[3] Delete a profile")

        if update_available:
            print(f"{Color.YELLOW}[4] Update program to {latest_version_str}{Color.RESET}")

        print("[6] Uninstall this program")
        print("[0] Back to main menu\n")

        key = get_key()

        if key == "1":
            print_header()
            profiles = get_profiles()

            if len(profiles) >= 9:
                print(
                    f"{Color.RED}"
                    "Cannot create new profile! Limit reached."
                    f"{Color.RESET}"
                )
            else:
                print("Enter new profile name (or '0' to cancel):")
                name = input("> ").strip()

                invalid_chars = r'\/:*?"<>|'

                if name == "0" or not name:
                    print(f"{Color.YELLOW}Creation cancelled.{Color.RESET}")
                elif (
                    name.lower() == "backup"
                    or name in {".", ".."}
                    or any(char in name for char in invalid_chars)
                ):
                    print(f"{Color.RED}Invalid profile name!{Color.RESET}")
                elif os.path.exists(f"Mods_{name}"):
                    print(
                        f"{Color.RED}"
                        "A profile with this name already exists!"
                        f"{Color.RESET}"
                    )
                else:
                    os.makedirs(f"Mods_{name}")
                    print(
                        f"{Color.GREEN}"
                        f"Profile '{name}' created successfully!"
                        f"{Color.RESET}"
                    )

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
                    elif (
                        new_name.lower() == "backup"
                        or any(char in new_name for char in r'\/:*?"<>|')
                        or new_name in {".", ".."}
                    ):
                        print(f"{Color.RED}Invalid profile name!{Color.RESET}")
                    elif os.path.exists(f"Mods_{new_name}"):
                        print(
                            f"{Color.RED}"
                            "A profile with this name already exists!"
                            f"{Color.RESET}"
                        )
                    else:
                        os.rename(
                            f"Mods_{old_name}",
                            f"Mods_{new_name}",
                        )
                        print(
                            f"{Color.GREEN}"
                            "Profile renamed successfully!"
                            f"{Color.RESET}"
                        )
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

        elif key == "4" and update_available:
            update_self(latest_version_str, latest_download_url)


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
    if os.name == "nt":
        os.system("title SMAPI Mod Preloader")

    restore_active_profile()

    update_available, latest_version_str, latest_download_url = (
        check_for_updates()
    )

    while True:
        print_header()

        if update_available:
            print(
                f"{Color.YELLOW}[!] New update available: "
                f"{latest_version_str} (Current: {CURRENT_VERSION})"
                f"{Color.RESET}"
            )
            print(
                f"{Color.YELLOW}    Go to the [0] Settings menu "
                f"and press [4] Update{Color.RESET}\n"
            )

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

        if key == "0":
            settings_menu(
                update_available,
                latest_version_str,
                latest_download_url,
            )
        elif key.isdigit():
            idx = int(key) - 1
            if 0 <= idx < len(profiles):
                run_smapi(profiles[idx])


if __name__ == "__main__":
    main()