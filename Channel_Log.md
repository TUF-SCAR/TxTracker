# TxTracker — Channel Log

All notable changes to this project will be documented in this file.

Versioning format: MAJOR.MINOR

---

## [0.4] — Reports System & Core Stability Update

### Added

- Fully functional **Reports screen**
- Automatic calculation of:
  - Weekly expense total
  - Monthly expense total
  - Yearly expense total
- Real-time report refresh when switching tabs
- Expense totals calculated using selected transaction date & time
- Positive spending display while storing expenses internally as negative paise
- SQLite index on `date_time_ms` for faster report queries

### Improvements

- History screen now loads automatically on app startup
- Reports screen updates without restarting the app
- Pixel-style Add Expense layout refinement
- Improved card spacing and padding
- Cleaner dark theme consistency across all screens
- Faster navigation between tabs
- Improved database performance for large transaction lists

### Bug Fixes

- Fixed Reports always showing ₹0
- Fixed incorrect SQL column references
- Fixed mismatch between transaction date and report calculations
- Fixed history appearing empty until second app launch
- Fixed database connection leaks during report calculations
- Fixed inconsistent behavior between Windows and WSL environments

### Database & Logic Changes

- Reports now correctly query `date_time_ms`
- All calculations use millisecond timestamps
- Soft-deleted transactions are excluded from totals
- Decimal-safe rupees → paise conversion maintained
- Existing databases remain fully compatible (no migration required)

### Technical Notes

- Expense-only model (all values stored as negative paise)
- Reports display values as positive totals for clarity
- No automatic income tracking
- No recurring transactions
- No background services added

---

## [0.3] — UI Polish & History Stability

### Added

- Pixel-inspired dark UI foundation
- Rounded Material-style cards
- Improved spacing and padding across screens
- Bottom navigation layout finalized
- History screen now loads immediately on app start
- Automatic history refresh after saving transactions

### Improvements

- Add Expense screen layout centered correctly
- Fixed top input field touching card edge
- Consistent padding between fields
- Cleaner visual hierarchy for inputs and buttons
- Transaction list readability improved

### Bug Fixes

- Fixed History tab not appearing until app restart
- Fixed history not refreshing after save
- Fixed WSL2 runtime errors:
  - `libmtdev.so.1` missing
  - clipboard provider errors

### Technical Notes

- Installed Linux dependencies:
  - `libmtdev1`
  - `xclip`
  - `xsel`
- No database schema changes
- No breaking API changes
- Existing data remains fully compatible

---

## [0.2] — Date & Time Picker + Virtual Env

### Added

- Project virtual environment setup (`.venv`) for consistent installs and builds
- KivyMD integration for native-style pickers
- Tap Date & Time field → Date picker → Time picker
- Picker-selected date/time is saved into the database (not system time)
- History continues sorting by saved date/time and refreshes automatically after save

### Developer Notes

- Run inside venv:
  - `source .venv/bin/activate`
  - `python main.py`
- `requirements.txt` updated to include KivyMD

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
