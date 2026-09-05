import os
import shutil
import subprocess
import sys

RED_BG = "\033[41m\033[97m\033[1m"
RED_TEXT = "\033[91m\033[1m"
RESET = "\033[0m"

BUILDER_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(BUILDER_DIR, ".."))

RELEASE_NAME = "SMAPI-mod-preloader-main"

ROOT_DIST_DIR = os.path.join(PARENT_DIR, "dist")
RELEASE_DIR = os.path.join(ROOT_DIST_DIR, RELEASE_NAME)


def find_script_path(file_name):
    local_path = os.path.join(BUILDER_DIR, file_name)
    if os.path.exists(local_path):
        return local_path

    parent_path = os.path.join(PARENT_DIR, file_name)
    if os.path.exists(parent_path):
        return parent_path

    return None


ICON_PATH = find_script_path("icon.ico")


def run_pyinstaller(script_name):
    script_path = find_script_path(script_name)

    if not script_path:
        print(f"{RED_TEXT}[ERROR] File '{script_name}' not found in builder dir or parent dir!{RESET}")
        sys.exit(1)

    cmd = [
        "py",
        "-m",
        "PyInstaller",
        "--onefile",
        f"--specpath={BUILDER_DIR}",
        f"--distpath={ROOT_DIST_DIR}",
        f"--workpath={os.path.join(BUILDER_DIR, 'build')}",
        script_path,
    ]

    if ICON_PATH and os.path.exists(ICON_PATH):
        cmd.append(f"--icon={ICON_PATH}")

    subprocess.run(cmd, check=True)


def build():
    os.system("")

    print("\n[1/2] Building installer.py...")
    run_pyinstaller("installer.py")

    print("\n[2/2] Building SMAPImodpreloader.py...")
    run_pyinstaller("SMAPImodpreloader.py")

    if os.path.exists(RELEASE_DIR):
        shutil.rmtree(RELEASE_DIR)

    os.makedirs(RELEASE_DIR, exist_ok=True)

    readme_path = find_script_path("README.md")
    license_path = find_script_path("LICENSE")

    files_to_copy = [
        readme_path,
        license_path,
        os.path.join(ROOT_DIST_DIR, "installer.exe"),
        os.path.join(ROOT_DIST_DIR, "SMAPImodpreloader.exe"),
    ]

    for file in files_to_copy:
        if file and os.path.exists(file):
            try:
                shutil.copy(file, RELEASE_DIR)
                print(f"Copied: {os.path.basename(file)}")
            except Exception as e:
                print(f"[!] Failed to copy {os.path.basename(file)}: {e}")
        else:
            print("[!] File not found (skipped)")

    zip_path = os.path.join(ROOT_DIST_DIR, RELEASE_NAME)
    shutil.make_archive(zip_path, "zip", RELEASE_DIR)

    build_temp_dir = os.path.join(BUILDER_DIR, "build")
    if os.path.exists(build_temp_dir):
        shutil.rmtree(build_temp_dir)

    for exe in ["installer.exe", "SMAPImodpreloader.exe"]:
        spec_file = os.path.join(BUILDER_DIR, exe.replace(".exe", ".spec"))
        if os.path.exists(spec_file):
            os.remove(spec_file)

        root_exe = os.path.join(ROOT_DIST_DIR, exe)
        if os.path.exists(root_exe):
            os.remove(root_exe)
        else:
            msg1 = "[WARNING / ERROR]"
            msg2 = f"File {exe} was not found in dist during cleanup!"
            msg3 = "It may have been moved or blocked by an antivirus."

            max_len = max(len(msg1), len(msg2), len(msg3)) + 4

            print()
            print(f"{RED_BG}{' ' * max_len}{RESET}")
            print(f"{RED_BG}  {msg1.ljust(max_len - 2)}{RESET}")
            print(f"{RED_BG}  {msg2.ljust(max_len - 2)}{RESET}")
            print(f"{RED_BG}  {msg3.ljust(max_len - 2)}{RESET}")
            print(f"{RED_BG}{' ' * max_len}{RESET}\n")


if __name__ == "__main__":
    build()