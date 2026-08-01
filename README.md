# 🌾 SMAPI Mod Preloader

A lightweight and fast profile manager for **Stardew Valley** with **SMAPI**. Switch between different mod sets in a single keypress before starting your game!

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Game](https://img.shields.io/badge/Stardew%20Valley-v1.6+-brightgreen.svg)

---

##  Features

*  **Instant Launch:** Select your desired mod preset with a single key press (no Enter needed).
*  **Profile Management:** Support for up to **9 custom mod profiles** (`Mods_ProfileName`).
*  **Safe & Non-Destructive:** Automatically backs up your original `Mods` folder into `Mods_Backup` on first launch.
*  **Zero Overhead:** Launches `StardewModdingAPI.exe` and closes itself immediately to free up system resources.
*  **Auto-Restore on Exit/Uninstall:** Includes an built-in option to safely restore your original mod setup and remove all preloader files seamlessly.

---

## 🛠️ Installation & Setup

1. **Download:** Install the latest `SMAPImodpreloader.exe` from the [Releases](../../releases) tab (or compile from source).
2. **Place:** Unzip folder somwere and run `installer.exe`.
3. **Steam Launch Options (Optional):**
   If you want Steam to launch this preloader automatically when clicking **Play**:
   * Open **Steam** -> Right-click **Stardew Valley** -> **Properties**.
   * In **Launch Options**, paste the path to `SMAPImodpreloader.exe` from concole
  
## 🛠️ Option 2: Manual Installation
1. **Download:** Download SMAPImodpreloader.exe and place it into your main Stardew Valley game folder.
2. **Configure Steam Launch Options Manually:**
   *Open Steam -> Right-click Stardew Valley -> Properties -> General -> Launch Options.
3. Enter th path to your SMAPImodpreloader.exe wrapped in quotes, followed by %command%
   *(Exemple: "C:\Program Files (x86)\Steam\steamapps\common\Stardew Valley\SMAPImodpreloader.exe" %command% )
---

##  How to Use

1. Run `SMAPImodpreloader.exe`.
2. **First Run:** If you don't have profiles yet, press `[0]` to open **Settings Menu**.
3. Create a new profile (e.g., `Farm` or `Vanillaplus`). This will create a `Mods_Farm` folder in your game directory.
4. Put your desired mods inside the newly created `Mods_ProfileName` folder.
5. Next time you open the preloader, press `[1]`–`[9]` to choose your active profile and launch SMAPI!

---

## ⚙️ Settings Menu Options

* `[1]` **Create a new profile:** Add up to 9 custom mod presets.
* `[2]` **Rename a profile:** Instantly rename existing mod setups.
* `[3]` **Delete a profile:** Remove a profile and its mod contents completely.
* `[6]` **Uninstall this program:** Restores your original `Mods_Backup` folder back to `Mods`, cleans up preloader files, and self-deletes.

---

## ⚠️ Antivirus / Windows Defender Note

> **Note regarding False Positives:**
> Because this executable is packaged using PyInstaller without an expensive commercial code-signing certificate, **Windows Defender or SmartScreen may show a warning** (*"Unknown Publisher"* / *False Positive*).
> 
> * **To run:** Click **"More info"** -> **"Run anyway"**.
> * **Alternative:** You can review the open-source Python script (`SMAPImodpreloader.py`) and compile it yourself using PyInstaller!
