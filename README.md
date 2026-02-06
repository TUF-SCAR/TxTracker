# 📊 TxTracker

A clean, offline-first personal expense tracker built with Python (Kivy & KivyMD)

TxTracker is a minimal, privacy-focused expense tracking app designed for Android and desktop.
It focuses on clarity, speed, and local-first data ownership — no accounts, no ads, no cloud lock-in.
I made this for myself, designed for me. If you want you can fork this and edit, need help? ask me.

---

## ✨ Features

### 🧾 Add Transactions

- Date & time picker (future dates disabled)
- Item name, amount (₹ INR formatting), optional note
- Large, responsive amount input with live formatting
- Clear validation feedback

### 📜 History

- Grouped transaction list by date
- Clean card-based layout
- Tap to view full details
- Instant refresh after adding transactions

### 📈 Reports

- Daily / monthly summaries
- Expandable charts
- Dynamic scaling for readability
- Smooth animations

### 🔁 Optional Drive Sync

- Export & sync data to Google Drive
- Offline-first (app works without internet)
- Sync triggers safely without blocking UI

---

## 🧠 Design Philosophy

- Offline-first — your data stays on your device
- No accounts — no login, no tracking
- Fast UI — no heavy animations, no clutter
- Consistent layout — mobile & desktop parity
- Readable codebase — Python-only UI (no KV)

---

## 📱 Platforms

| Platform            | Status       |
| ------------------- | ------------ |
| Android (14+)       | ✅ Stable    |
| Android (arm64-v8a) | ✅ Supported |
| Windows             | ✅ Supported |
| Linux               | ✅ Supported |
| macOS               | ⚠️ Untested  |

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
│ │ └─ reports.py # Reports screen
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

buildozer android debug

---

## 🔐 Data & Privacy

- All data stored locally in SQLite
- No analytics
- No background tracking
- Optional Drive sync is user-initiated
- Database files are ignored from Git

---

## 🧾 Versioning

- App version: 1.1 (stable)
- Repository version: 1.1
- Semantic versioning used
- Full history in Channel_Log.md

---

## 🧑‍💻 Author

TUF SCAR
Computer Engineering student

---

## 📜 License

MIT License — see the LICENSE file for details.

---

## 🧠 Notes

- This app intentionally avoids over-engineering
- KivyMD 1.2.0 is retained for stability
- UI logic is kept Python-only for clarity
