# TidaLuna Installer

A modern, OLED-themed GUI installer for **[TidaLuna](https://github.com/Inrixia/TidaLuna)** (the TIDAL Client mod). 

This tool automates the manual installation process, ensuring the correct version is found, files are backed up safely, and the mod is applied correctly.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features

*   **Auto-Detection:** Automatically finds your latest TIDAL installation directory (even after TIDAL updates).
*   **Safe Install:** Backs up your `original.asar` so you never lose the base client.
*   **Auto-Fetch:** Downloads the very latest release of TidaLuna directly from GitHub.
*   **MacOS Fix:** Automatically runs the required `codesign` command for Mac users.
*   **Uninstaller:** One-click button to remove Luna and restore stock TIDAL.
*   **Zero-Dependency Run:** The script automatically installs required libraries (`customtkinter`, `requests`) if they are missing.

## How to Run (Source)

1. Download `installer.py`.
2. Ensure you have Python installed.
3. Run the script:
   ```bash
   python installer.py
