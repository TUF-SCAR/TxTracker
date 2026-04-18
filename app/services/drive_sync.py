import json
import time
from datetime import datetime, timedelta
from kivy.app import App
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform


class DriveSyncService:
    def __init__(self):
        self.uri = None
        self._status_cb = None
        self._resolver = None
        self._activity = None
        self._Intent = None
        self._request_code = 1234

        self._pending_payload = None
        self._pending_action = None
        self._pending_import_db = None
        self._pending_import_complete_cb = None

        self.last_auto_sync_key = None
        self.last_backup_at = None

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
            self._load_meta()
        else:
            self._set_status("Drive sync available on Android only")

    def set_status_callback(self, cb):
        self._status_cb = cb

    def _set_status(self, msg: str):
        if self._status_cb:
            self._status_cb(msg)

    def _build_backup_payload(self, db):
        txns = db.list_txns()
        return {
            "schema_version": 1,
            "source": "txtracker_backup",
            "exported_at": int(time.time()),
            "transaction_count": len(txns),
            "transactions": txns,
        }

    def link_drive(self, title: str = "txtracker_backup.json", payload=None):
        if platform != "android":
            self._set_status("Drive sync available on Android only")
            return

        self._pending_action = "create_backup_file"
        self._pending_payload = payload

        intent = self._Intent(self._Intent.ACTION_CREATE_DOCUMENT)
        intent.addCategory(self._Intent.CATEGORY_OPENABLE)
        intent.setType("application/json")
        intent.putExtra(self._Intent.EXTRA_TITLE, title)
        intent.addFlags(self._Intent.FLAG_GRANT_READ_URI_PERMISSION)
        intent.addFlags(self._Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
        intent.addFlags(self._Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)

        self._activity.startActivityForResult(intent, self._request_code)

    def import_json(self, db, on_complete=None):
        if platform != "android":
            self._set_status("JSON import available on Android only")
            return

        self._pending_action = "import_json"
        self._pending_import_db = db
        self._pending_import_complete_cb = on_complete

        intent = self._Intent(self._Intent.ACTION_OPEN_DOCUMENT)
        intent.addCategory(self._Intent.CATEGORY_OPENABLE)
        intent.setType("application/json")
        intent.addFlags(self._Intent.FLAG_GRANT_READ_URI_PERMISSION)
        intent.addFlags(self._Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)

        self._activity.startActivityForResult(intent, self._request_code)

    def _on_activity_result(self, request, result, intent):
        if request != self._request_code:
            return

        if result != self._Activity.RESULT_OK or intent is None:
            self._clear_pending()
            self._set_status("Action cancelled")
            return

        uri = intent.getData()
        if uri is None:
            self._clear_pending()
            self._set_status("No file selected")
            return

        if self._pending_action == "create_backup_file":
            self._handle_create_backup_file(intent, uri)
        elif self._pending_action == "import_json":
            self._handle_import_json(intent, uri)
        else:
            self._clear_pending()
            self._set_status("Unknown action")

    def _persist_permissions(self, intent, uri, include_write=False):
        try:
            flags = intent.getFlags() & self._Intent.FLAG_GRANT_READ_URI_PERMISSION
            if include_write:
                flags |= (
                    intent.getFlags() & self._Intent.FLAG_GRANT_WRITE_URI_PERMISSION
                )

            self._resolver.takePersistableUriPermission(uri, flags)
        except Exception:
            pass

    def _handle_create_backup_file(self, intent, uri):
        self.uri = uri
        self._persist_permissions(intent, uri, include_write=True)
        self._save_link()

        if self._pending_payload is not None:
            ok, err = self._write_to_uri(uri, self._pending_payload)
            if ok:
                self._mark_backup_complete()
                self._set_status("Drive backup complete")
            else:
                self._set_status(f"Drive backup failed: {err}")
        else:
            self._set_status("Drive linked")

        self._clear_pending()

    def _handle_import_json(self, intent, uri):
        self._persist_permissions(intent, uri, include_write=False)

        try:
            raw_text = self._read_text_from_uri(uri)
        except Exception as e:
            self._clear_pending()
            self._set_status(f"Could not read JSON file: {e}")
            return

        try:
            payload = json.loads(raw_text)
        except Exception:
            self._clear_pending()
            self._set_status("Invalid JSON file")
            return

        if isinstance(payload, dict):
            transactions = payload.get("transactions", [])
        elif isinstance(payload, list):
            transactions = payload
        else:
            transactions = None

        if not isinstance(transactions, list):
            self._clear_pending()
            self._set_status("Invalid transactions format")
            return

        db = self._pending_import_db
        if db is None:
            self._clear_pending()
            self._set_status("Import database not available")
            return

        imported_count, skipped_count = db.import_transactions(
            transactions, skip_duplicates=True
        )

        if self._pending_import_complete_cb:
            try:
                self._pending_import_complete_cb(imported_count, skipped_count)
            except Exception:
                pass

        self._set_status(
            f"Imported {imported_count} transaction(s), skipped {skipped_count}"
        )
        self._clear_pending()

    def sync_db(self, db):
        if platform != "android":
            self._set_status("Drive sync available on Android only")
            return

        payload = self._build_backup_payload(db)

        if self.uri:
            ok, err = self._write_to_uri(self.uri, payload)
            if ok:
                self._mark_backup_complete()
                self._set_status("Drive backup complete")
                return

            self._set_status(
                f"Linked Drive file failed: {err}. Create a new backup file"
            )

        timestamp = time.strftime("%Y-%m-%d")
        filename = f"TxTracker_backup_{timestamp}.json"
        self.link_drive(title=filename, payload=payload)

    def auto_sync_if_due(self, db):
        if platform != "android":
            return

        now = datetime.now()
        today = now.date()
        next_day = today + timedelta(days=1)
        is_month_end = next_day.month != today.month

        if not is_month_end:
            return

        # allow first 5 minutes of the hour instead of exact minute only
        if now.minute > 5:
            return

        if now.hour not in (11, 23):
            return

        slot = "am" if now.hour == 11 else "pm"
        key = f"{today.isoformat()}-{slot}"

        if self.last_auto_sync_key == key:
            return

        payload = self._build_backup_payload(db)

        if self.uri:
            ok, err = self._write_to_uri(self.uri, payload)
            if ok:
                self.last_auto_sync_key = key
                self._mark_backup_complete()
                self._save_meta()
                self._set_status("Auto Drive backup complete")
                return

        filename = f"TxTracker_backup_{today.strftime('%Y-%m-%d')}.json"
        self.link_drive(title=filename, payload=payload)
        self.last_auto_sync_key = key
        self._save_meta()

    def _write_to_uri(self, uri, payload):
        try:
            out = self._resolver.openOutputStream(uri, "wt")
            if out is None:
                return False, "could not open output stream"

            data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            out.write(data)
            out.close()
            return True, None

        except Exception as e:
            return False, str(e)

    def _read_text_from_uri(self, uri) -> str:
        stream = self._resolver.openInputStream(uri)
        if stream is None:
            raise ValueError("could not open selected file")

        chunks = bytearray()
        while True:
            b = stream.read()
            if b == -1:
                break
            chunks.append(b)

        stream.close()

        raw = bytes(chunks)
        try:
            return raw.decode("utf-8-sig")
        except Exception:
            return raw.decode("utf-8")

    def _mark_backup_complete(self):
        self.last_backup_at = int(time.time())
        self._save_meta()

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

    def _save_meta(self):
        try:
            st = self._store()
            st.put(
                "drive_meta",
                last_auto_sync_key=self.last_auto_sync_key or "",
                last_backup_at=self.last_backup_at or 0,
            )
        except Exception:
            pass

    def _load_meta(self):
        try:
            st = self._store()
            if st.exists("drive_meta"):
                data = st.get("drive_meta")
                key = data.get("last_auto_sync_key") or None
                backup_at = data.get("last_backup_at") or None
                self.last_auto_sync_key = key
                self.last_backup_at = backup_at
        except Exception:
            pass

    def _clear_pending(self):
        self._pending_payload = None
        self._pending_action = None
        self._pending_import_db = None
        self._pending_import_complete_cb = None
