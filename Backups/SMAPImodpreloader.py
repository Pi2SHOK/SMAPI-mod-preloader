import os
import shutil
import sys
import msvcrt

SMAPI_EXE = "StardewModdingAPI.exe"
MODS_FOLDER = "Mods"
STATE_FILE = ".active_profile"

# Поддержка ANSI-цветов в консоли Windows
if os.name == 'nt':
    os.system('')

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Зеленый заголовок программы
def print_header():
    clear_screen()
    print("\033[32m=====================")
    print(" SMAPI Mod Preloader ")
    print("=====================\033[0m\n")

# Считывание одного символа без нажатия Enter
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
            profiles.append(item[5:])
    return sorted(profiles)

def run_smapi(profile_name):
    profile_folder = f"Mods_{profile_name}"
    
    # 1. Защита оригинальной папки Mods (при самом первом запуске)
    if os.path.exists(MODS_FOLDER) and not os.path.islink(MODS_FOLDER):
        if not os.path.exists("Mods_Backup"):
            os.rename(MODS_FOLDER, "Mods_Backup")

    # 2. Переименовываем выбранную выкладку в активную папку Mods
    if os.path.exists(profile_folder):
        os.rename(profile_folder, MODS_FOLDER)
        # Сохраняем имя текущей активной выкладки
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            f.write(profile_name)
    
    print(f"\n\033[36mLaunching SMAPI with profile '{profile_name}'...\033[0m")
    
    # 3. Запускаем StardewModdingAPI.exe
    os.startfile(SMAPI_EXE)
    
    # 4. Закрываем прелоадер
    sys.exit()

def settings_menu():
    while True:
        print_header()
        print("\033[33m--- SETTINGS MENU ---\033[0m")
        print("[1] Create a new profile")
        print("[2] Rename a profile")
        print("[3] Delete a profile")
        print("[6] Uninstall this program")
        print("[0] Back to main menu\n")

        key = get_key()

        # [1] Создание новой выкладки
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

        # [2] Переименование выкладки
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

        # [3] Удаление выкладки
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

        # [6] Удаление программы
        elif key == '6':
            print_header()
            print("\033[31mAre you sure you want to uninstall this program?\033[0m")
            print("[1] Yes")
            print("[2] No")
            
            confirm = get_key()
            if confirm == '1':
                print_header()
                
                # Если существует резервная папка Mods_Backup, возвращаем её в Mods
                if os.path.exists("Mods_Backup"):
                    if not os.path.exists(MODS_FOLDER):
                        os.rename("Mods_Backup", MODS_FOLDER)
                        print("\033[32mMods_Backup folder successfully restored to 'Mods'!\033[0m\n")
                    else:
                        print("\033[33mFolder 'Mods' already exists, Mods_Backup left unchanged.\033[0m\n")

                # Удаление служебного файла .active_profile
                if os.path.exists(STATE_FILE):
                    os.remove(STATE_FILE)

                print("\033[32mPreloader program successfully uninstalled!\033[0m\n")
                
                smapi_path = os.path.abspath(SMAPI_EXE)
                print("\033[33mChange your Steam launch options back to:\033[0m")
                print(f'\033[36m"{smapi_path}" %command%\033[0m\n')
                
                input("Press Enter to close the program...")
                
                script_path = os.path.abspath(sys.argv[0])
                os.remove(script_path)
                sys.exit()

        # [0] Выход из меню настроек
        elif key == '0':
            break

def main():
    if os.name == 'nt':
        os.system('title SMAPI Mod Preloader')

    restore_active_profile()

    while True:
        print_header()
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