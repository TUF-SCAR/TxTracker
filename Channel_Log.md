# TxTracker — Channel Log

All notable changes to this project will be documented in this file.

Versioning format: MAJOR.MINOR

---

## [0.1] — Core Expense Tracker Foundation

### Added

- Android-first expense tracking application built using **Python + Kivy**
- Clean modular project structure suitable for long-term scaling
- GitHub repository initialized with proper `.gitignore`

### Core Features

- Expense-only transaction tracking (no income support by design)
- Manual data entry (no autofill or auto-detection)
- Supports integer and decimal amounts (e.g. `120`, `120.50`)
- All expenses are stored as **negative values internally**

### Add Expense Screen

- Input fields:
  - Date & Time (manual entry – parsing planned)
  - Item name
  - Amount (₹)
  - Optional note
- Save button with validation
- Real-time save feedback
- Automatic conversion of rupees → paise to prevent float precision errors

### Database System

- SQLite local database
- Automatic database initialization on app start
- Transaction schema includes:
  - Unique transaction ID
  - Date/time (milliseconds)
  - Item name
  - Amount stored in paise
  - Optional note
  - Created timestamp
  - Soft delete flag

### History Screen

- Scrollable transaction list
- Transactions sorted newest → oldest
- Live refresh without restarting the app
- Displays:
  - Transaction ID
  - Item name
  - Amount
  - Note (if present)

### Delete & Undo System

- Soft delete implementation (no permanent deletion)
- Instant delete button per transaction
- Undo bar with single-step restore
- Deleted records remain safely stored in database

### Architecture

- ScreenManager-based navigation
- Bottom navigation bar:
  - Add
  - History
  - Reports (placeholder)
- Modular separation:
  - `screens/` — UI logic
  - `services/` — external integrations (Drive sync later)
  - `utils.py` — currency handling & helpers
  - `db.py` — database abstraction

### Developer Features

- Desktop preview support (no Android build required during development)
- Database ignored from Git for safety
- Ready for Buildozer Android packaging
- Designed for offline-first operation

---

### Planned for Next Versions

- Manual date/time parsing
- Weekly / monthly / yearly totals
- Report charts
- Google Drive automatic sync
- Encrypted PIN lock
- Optional trash screen
- Export & visualization web dashboard
