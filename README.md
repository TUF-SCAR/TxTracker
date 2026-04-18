# 📊 TxTracker

A clean, offline-first personal expense tracker built with Python (Kivy & KivyMD)

TxTracker is a minimal, privacy-focused expense tracking app designed for Android.
It focuses on clarity, speed, and local-first data ownership — no accounts, no ads, no cloud lock-in.

I made this for myself, designed for me. If you want you can fork this and edit, need help? ask me.

---

## ✨ Features

### 🧾 Add Transactions

- Date & time picker (future dates disabled)
- Item name, amount (₹ INR formatting), optional note
- Large, responsive amount input with live formatting
- Clear validation feedback
- Fast-entry behavior settings:
  - keep date & time after save
  - default note retain
  - auto focus item on open
  - auto reopen keyboard after save
  - save status timeout
  - amount font size mode

### 📜 History

- Grouped transaction list
- Card-based layout
- Tap a card to view full details
- Soft delete + undo
- Instant refresh after adding transactions

### 📈 Reports

- This Week / This Month / This Year summaries
- Expandable charts
- Dynamic scaling
- Smooth animations
- Custom chart widget with tuned label spacing
- Reports visuals intentionally kept stable for this release

### ⚙️ Settings

- Separate settings screen opened from the gear icon
- Backup/import controls
- Backup status + last backup time
- Appearance customisation:
  - background dim strength
  - card transparency
  - accent color
  - larger UI text
  - compact or normal spacing
  - corner style
- Navigation customisation:
  - dock height
  - dock lift
  - show/hide nav labels
  - animation speed
- Add screen behavior controls

### 🔁 Backup & Import

- Create JSON backup file
- Backup transactions to Drive-linked JSON
- Import transactions from JSON
- Duplicate skipping during import
- Offline-first app behavior

---

## 🧠 Design Philosophy

- Offline-first — your data stays on your device
- No accounts — no login, no tracking
- Fast UI — no clutter
- Python-only UI — no KV language
- Built for personal use first

---

## 📱 Platforms

| Platform            | Status                    |
| ------------------- | ------------------------- |
| Android (14+)       | ⚠️ Final signed test next |
| Android (arm64-v8a) | ⚠️ Final signed test next |
| Windows             | ✅ Supported              |
| Linux               | ✅ Supported              |
| macOS               | ⚠️ Untested               |

---

## 🛠 Tech Stack

- Language: Python 3
- UI: Kivy + KivyMD
- Database: SQLite
- Charts: Custom lightweight widgets
- Android Build: Buildozer + python-for-android
- Architecture: Offline-first, local storage

---

## 📦 Project Structure

TxTracker/  
├─ main.py # App entry point  
├─ buildozer.spec # Android build config  
├─ requirements.txt  
│
├─ app/  
│ ├─ db.py # SQLite database layer  
│ ├─ utils.py # Helpers (formatting, conversions)  
│ │  
│ ├─ screens/  
│ │ ├─ add.py # Add transaction screen  
│ │ ├─ history.py # History screen  
│ │ ├─ reports.py # Reports screen  
│ │ └─ settings.py
│ │  
│ ├─ services/  
│ │ └─ drive_sync.py # Google Drive sync logic  
│ │  
│ └─ widgets/  
│ └─ line_chart.py # Custom chart widget  
│  
├─ assets/  
│ ├─ fonts/  
│ └─ background.png  
│  
├─ Channel_Log.md # Full changelog  
├─ .gitignore  
└─ README.md

---

## 🚀 Building the Android APK

### Prerequisites

- Linux / WSL (Ubuntu recommended)
- Python 3.10+
- Java 17
- Buildozer installed

### Build

```bash
buildozer android debug
```

---

## 🔐 Data & Privacy

- All data stored locally in SQLite
- No analytics
- No background tracking
- Backup/import is user-controlled
- Database files are ignored from Git

---

## 🧾 Versioning

- App version: 2.0 (stable)
- Repository version: 2.0
- Full history in `Channel_Log.md`

---

## 🧑‍💻 Author

TUF SCAR
Computer Engineering student

---

## 📜 License

MIT License — see the `LICENSE` file for details.

---

## 🧠 Notes

- This app intentionally avoids over-engineering
- KivyMD 1.2.0 is retained for stability
- UI logic is kept Python-only for clarity
- Drive/JSON backup and import are implemented
- The 2.0 release focuses on stability, fast entry, and broad UI customisation
