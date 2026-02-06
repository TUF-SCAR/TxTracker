# A service for syncing transaction data to Google Drive.
# On Android, it uses the Storage Access Framework to let the user choose a file location,
# then writes a JSON export of the transactions. It also has an auto-sync feature that triggers at the end of each month.

import json
import time
from kivy.app import App
from kivy.utils import platform
from kivy.storage.jsonstore import JsonStore
from datetime import date, datetime, timedelta


class DriveSyncService:
    def __init__(self):
        self.uri = None
        self._status_cb = None
        self._resolver = None
        self._activity = None
        self._Intent = None
        self._request_code = 1234
        self._pending_payload = None
        self._pending_auto_date = None
        self.last_auto_sync_key = None

        if platform == "android":
            from jnius import autoclass
            from android import activity

            self._Intent = autoclass("android.content.Intent")
            self._Uri = autoclass("android.net.Uri")
            self._PythonActivity = autoclass("org.kivy.android.PythonActivity")
            self._Activity = autoclass("android.app.Activity")
            self._activity = self._PythonActivity.mActivity
            self._resolver = self._activity.getContentResolver()
            activity.bind(on_activity_result=self._on_activity_result)
            self._load_link()
        else:
            self._set_status("Drive sync available on Android only")

    def set_status_callback(self, cb):
        self._status_cb = cb

    def _set_status(self, msg: str):
        if self._status_cb:
            self._status_cb(msg)

    def link_drive(
        self, title: str = "txtracker_sync.json", payload=None, auto_date=None
    ):
        if platform != "android":
            self._set_status("Drive sync available on Android only")
            return

        self._pending_payload = payload
        self._pending_auto_date = auto_date
        intent = self._Intent(self._Intent.ACTION_OPEN_DOCUMENT)
        intent.addCategory(self._Intent.CATEGORY_OPENABLE)
        intent.setType("application/json")
        intent.addFlags(self._Intent.FLAG_GRANT_READ_URI_PERMISSION)
        intent.addFlags(self._Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
        intent.addFlags(self._Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)
        intent.putExtra(self._Intent.EXTRA_TITLE, title)
        self._activity.startActivityForResult(intent, self._request_code)

    def _on_activity_result(self, request, result, intent):
        if request != self._request_code:
            return
        if result != self._Activity.RESULT_OK or intent is None:
            self._pending_payload = None
            self._pending_auto_date = None
            self._set_status("Drive link cancelled")
            return

        self.uri = intent.getData()

        try:
            flags = intent.getFlags() & (
                self._Intent.FLAG_GRANT_READ_URI_PERMISSION
                | self._Intent.FLAG_GRANT_WRITE_URI_PERMISSION
            )
            self._resolver.takePersistableUriPermission(self.uri, flags)
        except Exception:
            pass

        self._save_link()

        if self._pending_payload is not None:
            out = self._resolver.openOutputStream(self.uri, "wt")
            data = json.dumps(
                self._pending_payload, ensure_ascii=False, indent=2
            ).encode()
            out.write(data)
            out.close()
            self._pending_payload = None
            self._pending_auto_date = None
            self._set_status("Drive sync complete")
        else:
            self._set_status("Drive linked")

    def sync_db(self, db):
        if platform != "android":
            self._set_status("Drive sync available on Android only")
            return

        payload = {
            "exported_at": int(time.time()),
            "transactions": db.list_txns(),
        }

        if self.uri and self._write_to_uri(self.uri, payload):
            self._set_status("Drive sync complete")
            return

        self._set_status("Pick a Drive file to link")
        timestamp = time.strftime("%Y-%m-%d")
        filename = f"TxTracker_sync_{timestamp}.json"
        self.link_drive(title=filename, payload=payload, auto_date=None)

    def auto_sync_if_due(self, db):
        if platform != "android":
            return

        now = datetime.now()
        today = now.date()

        next_day = today + timedelta(days=1)
        is_month_end = next_day.month != today.month
        if not is_month_end:
            return

        if now.minute != 0:
            return
        if now.hour not in (11, 23):
            return

        slot = "am" if now.hour == 11 else "pm"
        key = f"{today.isoformat()}-{slot}"
        if self.last_auto_sync_key == key:
            return

        payload = {
            "exported_at": int(time.time()),
            "transactions": db.list_txns(),
        }
        if self.uri and self._write_to_uri(self.uri, payload):
            self._set_status("Auto Drive sync complete")
            self.last_auto_sync_key = key
            return

        filename = f"TxTracker_sync_{today.strftime('%Y-%m-%d')}.json"
        self.link_drive(title=filename, payload=payload, auto_date=today)
        self.last_auto_sync_key = key

    def _write_to_uri(self, uri, payload) -> bool:
        try:
            out = self._resolver.openOutputStream(uri, "wt")
            data = json.dumps(payload, ensure_ascii=False, indent=2).encode()
            out.write(data)
            out.close()
            return True
        except Exception:
            return False

    def _store(self):
        app = App.get_running_app()
        base = app.user_data_dir if app else "."
        return JsonStore(f"{base}/drive_state.json")

    def _save_link(self):
        try:
            st = self._store()
            st.put("drive", uri=self.uri.toString() if self.uri else "")
        except Exception:
            pass

    def _load_link(self):
        try:
            st = self._store()
            if st.exists("drive"):
                uri_str = st.get("drive").get("uri")
                if uri_str:
                    self.uri = self._Uri.parse(uri_str)
                    return True
        except Exception:
            pass
        return False
