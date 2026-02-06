# TxTracker — Channel Log

All notable changes to this project will be documented in this file.

Versioning format: { finished }.{ all_types_of_changes }

---

## 🚀 [1.2] — Drive Link Persistence + Release Prep

### Added

- Drive link now **persists after app restart** (saved URI + auto-load on launch)
- Persisted Drive permission using `takePersistableUriPermission` (so Android doesn’t “forget” the file)

### Changed

- Drive picker uses **Open Document** (select an existing JSON and overwrite it on every sync)
- UI accent red updated from dull red to brighter red: `rgba(233, 24, 39, 0.8)`

### Notes

- No database changes
- No breaking changes
- Repo version: **1.2**

---

## 🛠 [1.1] — Post-Release Cleanup & UX Improvements

### Added

- Status message auto-reset on Add screen (10-second timeout)
- Improved internal code organization and readability
- Safer Git ignore rules for Android, Buildozer, and local data

### Changed

- Add screen layout consistency across Android and desktop
- Minor spacing and sizing refinements using `dp()`
- Versioning clarified between app releases and repository changes

### Fixed

- Status text persisting indefinitely after save/error
- Minor layout shifts caused by system navigation bar
- Internal build and packaging edge cases

### Notes

- No database changes
- No breaking changes
- Android app version is now **1.1**
- There was a error in version **1.0** I forgot to import ceil correctly opss
- I would have put this app on Google Play Store but it costs 25$ - 2200₹ so NO

---

## ✅ [1.0] — Reports Charts + History Redesign + Drive Sync + Picker UX

### Added

- **Drive sync (Google Drive)**
  - Link Drive file + sync JSON export
  - Auto-sync on month-end at 11:00 AM/PM (app open required)
- **History note/details popup**
  - Tap card to view full Item + Note in a styled dialog
- **Tabbed background pan**
  - Background image pans to left/middle/right thirds per tab
  - Sideways slide transition synced to background

---

### Changed

- **Reports charts**
  - Expand/collapse inside cards with smooth animation
  - Line chart axes + labels (days/months) and dynamic scale (max capped to 90%)
  - Line/dots match selected card color; smoother line rendering
- **History screen**
  - RecycleView-based list with section/group headers
  - Spacing + fonts refined; clipping fixes
  - Amount column adjusted to keep values on one line
- **Date & time pickers**
  - Themed to match app colors (primary/secondary split)
  - Future dates disabled inside the picker calendar
  - Time picker Cancel clears the field

---

### Fixed

- Chart label brightness + readability
- History delete callback crash
- RV clipping/bleed artifacts
- Popup radius error (border_radius)

---

### Status

- UI/UX: **polished**
- Reports: **stable**
- History: **stable**
- Drive sync: **MVP**

---

## ✅ [0.7] — Final UI Lock-In + Font System + Hero Amount Polish

### Added

- **Full custom font system**
  - Multiple font families loaded manually from `/fonts`
  - Fonts applied per-widget using `font_name`
  - Supports mixing fonts across:
    - Titles
    - Amount display
    - Section labels
    - Input text
    - Buttons

- **Hero amount cursor**
  - Visible blinking cursor added to the amount display
  - Cursor appears directly inside the ₹ amount header
  - No visible textfield — amount feels native and clean

- **Background image support**
  - Static background image rendering (`assets/bg.png`)
  - Automatically scales to window size
  - Gradient system fully removed

---

### Changed

- **Add screen UI finalized**
  - Matches reference layout closely:
    - Amount outside card
    - Pills grouped inside rounded card
    - Proper vertical spacing hierarchy
  - Section headers:
    - ITEM NAME
    - DETAILS
  - Card radius and padding tuned to match reference

- **Hero amount behavior**
  - Indian comma grouping while typing (`1,50,000`)
  - Dynamic font scaling:
    - Expands horizontally first
    - Shrinks font size only when necessary
  - Prevents vertical wrapping completely

- **Save button redesigned**
  - Full-width pill-shaped button
  - Rounded radius
  - Custom font
  - Reference-accurate size and placement

- **Bottom dock polish**
  - Stable fixed positioning
  - Consistent icon + label spacing
  - Active tab coloring refined

---

### Fixed

- Fixed amount text wrapping vertically (`150\n000`)
- Fixed amount shortening (`…`) appearing unexpectedly
- Fixed overlapping hero amount and form card
- Fixed MDTextField underline showing through pills
- Fixed hidden focus confusion while typing amount
- Fixed layout jumps caused by `size_hint_y`

---

### Removed

- Removed gradient ellipse background system
- Removed experimental layout wrappers
- Removed unused shorten logic on amount label
- Removed conflicting MDTextField modes

---

### Technical Notes

- Window locked to mobile-accurate resolution:
  - **412 × 815**
- Desktop preview now matches mobile layout
- No KV language used — Python-only UI
- KivyMD **1.2.0** retained for stability
- Amount input system:
  - Hidden numeric `MDTextField` (input only)
  - Visible `MDLabel` (display only)
  - Cursor rendered manually for clarity

---

### Status

- UI design: **final**
- Amount system: **final**
- Fonts: **final**
- Navigation: **stable**
- Database: **unchanged**

---

## [0.6] — Add UI Overhaul + Custom Bottom Dock

### Added

- **Custom bottom dock navigation** (Add / History / Reports) built manually (no KivyMD BottomNavigation), with active-state styling + tab switching logic. :contentReference[oaicite:1]{index=1}
- **Hero amount header** on Add screen: big ₹ + amount display, with the amount editable via a focused input (tap/click on the hero amount to focus). :contentReference[oaicite:2]{index=2}

### Changed

- Add screen form layout moved closer to the reference:
  - Section labels (**ITEM NAME**, **DETAILS**)
  - “Pill row” inputs with left icons + optional right chevron (Date/Time). :contentReference[oaicite:3]{index=3}
- Amount display now formats using **Indian grouping commas** while typing (e.g., 1,50,000), and it auto-adjusts sizing to fit the header area.
- Saving now **strips commas** from the amount string before converting to paise. :contentReference[oaicite:5]{index=5}
- Date & time picking flow: **MDDatePicker → MDTimePicker**, and Add screen shows `YYYY-MM-DD • hh:mm AM/PM`. :contentReference[oaicite:6]{index=6}

### Fixed

- Tab switching now triggers refresh safely using `Clock.schedule_once(...)` when moving to History/Reports. :contentReference[oaicite:7]{index=7}
- “Save” now refreshes History + Reports after inserting a transaction. :contentReference[oaicite:8]{index=8}

### Notes

- UI is still a **WIP toward the reference look** (background + field polish still pending), but navigation + amount formatting are in place.

---

## [0.5] — Date/Time Schema Upgrade + Reports Refresh Reliability

### Added

- **New date/time storage (split fields)**
  - `date` stored as `YYYY-MM-DD`
  - `time` stored as `HH:MM` (24h, used for sorting)
- Time is displayed in **12-hour format** (readability) while keeping 24h storage for sorting
- **Add screen now displays selected time in 12-hour format**
  - Storage remains `HH:MM` (24h) for sorting/DB
  - UI shows `h:MM AM/PM` after selecting date + time

### Improvements

- Reports refresh reliably when switching to the **Reports** tab (**scheduled on the next UI tick**)
- Reports refresh immediately after saving a transaction (**no restart needed**)
- Amount handling simplified:
  - Expense-only and stored as **positive paise**
  - UI displays values as **₹** (no negative-sign logic)

### Bug Fixes

- Fixed Reports sometimes showing **₹0 even when transactions exist today**
  - Root cause: totals used an **end-exclusive** range (`date < end_date`) but Reports passed `end_date = today`
  - Fix: Reports now uses `end_date = tomorrow` (exclusive), so **today is included**
- Fixed “This Week” totals showing **₹0 on Sundays** when expenses were added the same day (same end-exclusive issue)
- Fixed Reports not updating until app restart (tab-switch refresh timing issue)

### Database & Logic Changes

- **Schema change (breaking vs v0.4):**
  - Replaced `date_time_ms` timestamp model with split `date` + `time`
  - Updated sorting to: `ORDER BY date DESC, time DESC, id DESC`
  - Reports compute sums using date ranges: `start_date <= date < end_date` (end-exclusive)
- Soft-deleted transactions remain excluded from totals (`deleted = 0`)

### Technical Notes

- Week definition: **Sunday → Saturday**
- `time` stored in 24h for correct sorting, displayed in **12h format**
- Expense-only model (no income tracking)
- Amounts stored as **positive paise** (displayed as ₹ in UI)

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
