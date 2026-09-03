import os
import shutil
import subprocess

RELEASE_NAME = "SMAPI-mod-preloader-main"
RELEASE_DIR = os.path.join("dist", RELEASE_NAME)

# Путь к иконке внутри папки Backups
# Если ваша иконка называется иначе, замените "icon.ico" на правильное имя (например, "my_icon.ico")
ICON_PATH = os.path.join("Backups", "icon.ico")

def build():
    cmd_installer = ["py", "-m", "PyInstaller", "--onefile", "--console"]
    cmd_preloader = ["py", "-m", "PyInstaller", "--onefile", "--console"]

    # Проверяем наличие иконки в папке Backups
    if os.path.exists(ICON_PATH):
        cmd_installer.append(f"--icon={ICON_PATH}")
        cmd_preloader.append(f"--icon={ICON_PATH}")
        print(f"✅ Найдена иконка: {ICON_PATH}")
    else:
        print(f"⚠️ Иконка не найдена по пути: {ICON_PATH}")
        print("   Собираем со стандартной иконкой Windows.")

    cmd_installer.append("installer.py")
    cmd_preloader.append("SMAPImodpreloader.py")

    # Запуск сборки installer.py
    print("\n[1/2] Собираем installer.py...")
    subprocess.run(cmd_installer, check=True)

    # Запуск сборки SMAPImodpreloader.py
    print("\n[2/2] Собираем SMAPImodpreloader.py...")
    subprocess.run(cmd_preloader, check=True)

    print("\n=== 2. Подготовка папки релиза ===")
    if os.path.exists(RELEASE_DIR):
        shutil.rmtree(RELEASE_DIR)
    
    os.makedirs(RELEASE_DIR, exist_ok=True)

    files_to_copy = [
        "README.md",
        "LICENSE",
        ".gitignore",
        os.path.join("dist", "installer.exe"),
        os.path.join("dist", "SMAPImodpreloader.exe"),
    ]

    print(f"\n=== 3. Копирование файлов в {RELEASE_DIR} ===")
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy(file, RELEASE_DIR)
            print(f"Скопирован: {file}")
        else:
            print(f"⚠️ Файл не найден (пропущен): {file}")

    print("\n=== 4. Создание ZIP-архива ===")
    zip_path = os.path.join("dist", RELEASE_NAME)
    shutil.make_archive(zip_path, 'zip', RELEASE_DIR)
    print(f"✅ Успешно создан архив: {zip_path}.zip")

    print("\n=== 5. Очистка временных файлов ===")
    if os.path.exists("build"):
        shutil.rmtree("build")
        
    for exe in ["installer.exe", "SMAPImodpreloader.exe"]:
        root_exe = os.path.join("dist", exe)
        if os.path.exists(root_exe):
            os.remove(root_exe)

if __name__ == "__main__":
    build()