# NeuroBeat Protocol v5.0

**Advanced Cyberpunk Music Library Manager**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white) ![Flet](https://img.shields.io/badge/UI-Flet-purple?style=for-the-badge&logo=flutter&logoColor=white) ![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge) [![Spanish](https://img.shields.io/badge/Lang-Español-red?style=for-the-badge&logo=google-translate&logoColor=white)](README.es.md)

**NeuroBeat Protocol** is a powerful, visually immersive desktop application designed to organize, clean, and repair large local music collections. Built with Python and Flet, it features a "Night City" inspired Cyberpunk interface and separates core logic from the UI for professional performance.

## 📸 Screenshots

| **System Dashboard** | **Conflict Resolution** | **Tag Fixing**
|:---:|:---:|:---:|
| ![Library View](assets/screenshots/library_view.png) | ![Duplicates View](assets/screenshots/duplicates_view.png) | ![Repair View](assets/screenshots/repair_view.png) |
| *Full library overview with bitrate analysis* | *Smart duplicate detection with safety switches* | *Automatic Tag Repair* |

## Key Features

### 1. Deep System Scan (`DATA_LIBRARY`)
*   Recursively scans folders and subfolders for audio files (`.mp3`, `.flac`, `.wav`, `.ogg`, `.m4a`).
*   Displays technical details: **Bitrate**, **Format**, and **Metadata**.
*   Sorts hierarchy: Artist → Album → Title.

### 2. Smart Conflict Detection (`CONFLICT_DETECTED`)
*   **Fuzzy Logic:** Identifies duplicates based on normalized Artist/Title combinations.
*   **Quality First:** Automatically suggests keeping the highest quality version (highest bitrate/duration) and marking lower quality copies for deletion.
*   **"Purge" vs "Secure":** Interactive switches to manually override the deletion decision.
*   **Safety Net:** Deleted files are sent to the **OS Recycle Bin** (via `Send2Trash`), not permanently destroyed.

### 3. Metadata Patching (`METADATA_PATCH`)
*   **Auto-Inference:** Detects missing Artist tags and infers them from:
    *   "Album Artist" tag.
    *   Parent Folder name.
*   **Inline Editing:** Edit the suggested artist name directly within the table before applying.
*   **Write Capability:** Uses `Mutagen` to permanently write the corrected tags to the audio files.

### 4. Cyberpunk UI/UX
*   **Theme:** Dark mode with Neon Red/Cyan accents ("Arasaka" style).
*   **Typography:** Google Fonts integration (`Orbitron` for headers, `Rajdhani` for body, `Roboto Mono` for data).
*   **Responsiveness:** Fluid layout built with Flet.

---

## Installation

### Prerequisites
*   Python 3.14 installed.

### 1. Clone or Download
Download the project files to your local machine.

### 2. Install Dependencies
Run the following command in your terminal to install the required libraries:

```bash
pip install flet mutagen send2trash
```
---

## How To Run

1. Navigate to the project folder.
2. Run the main interface file
```bash
python main_flet.py
```
3. Click `INIT_SYSTEM_SCAN` and select your music folder.

---

## Project Structure
The project follows a modular Separation of Concerns architecture:

```text
/NeuroBeat-Protocol
│
├── assets/                  # Resources folder
│   ├── icon.png             # Window icon (App logo)
│   └── screenshots/         # Screenshots for README
│       ├── library_view.png
│       ├── duplicates_view.png
│       └── repair_view.png
│
├── main_flet.py             # FRONTEND: Contains only UI code (Flet)
├── music_logic.py           # BACKEND: Contains scanning, tagging, and file ops
└── README.md                # Documentation
```

---

## Usage Guide

### 1. Scanning
Click the cyan button `INIT_SYSTEM_SCAN` at the top right. Select your root music directory. The progress bar will indicate the scan status.

### 2. Managing Duplicates
Go to the `CONFLICT_DETECTED` tab.

* The system groups duplicates together
* Red (PURGE): Marked for deletion.
* Cyan (SECURE): Marked to keep.
* Toggle switcher to change the action.
* Click `PURGE MARKED`to move selected files to the Trash. The library refreshes automatically

### Fixing Tags
Go to the `METADATA_PATCH` tab.

* Review files with missing Artist tags.
* **Edit:** Click the text field in the "Suggested" column to manually correct the name.
* **Save:** Click the floppy disk icon to write tag to the file.

---

## Safety Mechanisms

* **Recycle Bin:** This app uses the `Send2Trash` library. It nevers executes a permanent `os.remove`. You can always restore files from your system's trash can.
* **Read-Only Default:** The scan is read-only until you explicity click "Purge" or "Save".

---

## Credits
Developed with Python & Flet.

* **UI Engine:** [Flet](https://flet.dev/)
* **Audio Handling:** [Mutagen](https://mutagen.readthedocs.io/en/latest/)

---

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

Distributed under the MIT License. This means you can use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software.

---

## 📞 Contact

**Project Lead** - Alejandro Giraldo

Project Link: [https://github.com/Malegiraldo22/NeuroBeat-Protocol](https://github.com/Malegiraldo22/NeuroBeat-Protocol)

---

<div align="center">
  <p><i>"Wake up, Samurai. We have a library to burn."</i></p>
  <img src="https://img.shields.io/badge/Status-Stable-success?style=for-the-badge" alt="Status Stable">
</div>