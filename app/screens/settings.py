from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton
from kivymd.uix.selectioncontrol import MDSwitch


class SettingsScreen(BoxLayout):
    def __init__(self, db, drive_sync, **kwargs):
        super().__init__(**kwargs)

        self.db = db
        self.drive_sync = drive_sync
        self.drive_sync.set_status_callback(self._set_status)

        self.orientation = "vertical"
        self.padding = (dp(8), dp(4), dp(8), dp(8))

        self.store = self._get_store()

        scroll = ScrollView(do_scroll_x=False)
        self.add_widget(scroll)

        root = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            spacing=dp(14),
            padding=(dp(8), dp(8), dp(8), dp(24)),
        )
        root.bind(minimum_height=root.setter("height"))
        scroll.add_widget(root)

        # ---------- Status ----------
        self.status_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(120),
            radius=[dp(20)],
            padding=(dp(16), dp(14), dp(16), dp(14)),
            md_bg_color=(0.05, 0.06, 0.07, 0.94),
            elevation=0,
            spacing=dp(4),
        )

        status_title = MDLabel(
            text="Status",
            size_hint_y=None,
            height=dp(24),
        )
        status_title.font_name = "Nunito-ExtraBold"
        status_title.font_size = "18sp"

        self.status_label = MDLabel(
            text="Ready",
            size_hint_y=None,
            height=dp(40),
            theme_text_color="Hint",
            valign="top",
        )
        self.status_label.font_name = "Nunito-SemiBold"
        self.status_label.font_size = "14sp"
        self.status_label.text_size = (0, None)

        self.last_backup_label = MDLabel(
            text="Last backup: never",
            size_hint_y=None,
            height=dp(20),
            theme_text_color="Hint",
            valign="middle",
        )
        self.last_backup_label.font_name = "Nunito-SemiBold"
        self.last_backup_label.font_size = "12sp"

        self.status_card.add_widget(status_title)
        self.status_card.add_widget(self.status_label)
        self.status_card.add_widget(self.last_backup_label)
        root.add_widget(self.status_card)

        # ---------- Backup & Restore ----------
        root.add_widget(self._section_title("Backup & Restore"))
        root.add_widget(
            self._action_button(
                "LINK DRIVE FILE", lambda *_: self.drive_sync.link_drive()
            )
        )
        root.add_widget(
            self._action_button(
                "BACKUP NOW", lambda *_: self.drive_sync.sync_db(self.db)
            )
        )
        root.add_widget(
            self._action_button(
                "IMPORT TRANSACTIONS FROM JSON",
                lambda *_: self.drive_sync.import_json(
                    self.db, on_complete=self._after_import
                ),
            )
        )

        # ---------- Entry Preferences ----------
        root.add_widget(self._section_title("Entry Preferences"))

        self.keep_date_switch = self._switch_row(
            root,
            "Keep date after save",
            self._get_pref("keep_date_after_save", True),
            lambda _, value: self._set_pref("keep_date_after_save", value),
        )

        self.keep_time_switch = self._switch_row(
            root,
            "Keep time after save",
            self._get_pref("keep_time_after_save", True),
            lambda _, value: self._set_pref("keep_time_after_save", value),
        )

        self.keep_note_switch = self._switch_row(
            root,
            "Keep note after save",
            self._get_pref("keep_note_after_save", False),
            lambda _, value: self._set_pref("keep_note_after_save", value),
        )

        # ---------- Future ----------
        root.add_widget(self._section_title("More Options"))

        future_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(72),
            radius=[dp(18)],
            padding=(dp(16), dp(12), dp(16), dp(12)),
            md_bg_color=(0.08, 0.09, 0.11, 0.96),
            elevation=0,
        )

        future_text = MDLabel(
            text="App Customisations are planned to release in future",
            theme_text_color="Hint",
        )
        future_text.font_name = "Nunito-SemiBold"
        future_text.font_size = "13sp"
        future_text.text_size = (0, None)

        future_card.add_widget(future_text)
        root.add_widget(future_card)

        # ---------- About ----------
        root.add_widget(self._section_title("About"))

        about_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(96),
            radius=[dp(20)],
            padding=(dp(16), dp(14), dp(16), dp(14)),
            md_bg_color=(0.05, 0.06, 0.07, 0.94),
            elevation=0,
        )

        about_1 = MDLabel(
            text="TxTracker",
            size_hint_y=None,
            height=dp(24),
        )
        about_1.font_name = "Nunito-ExtraBold"
        about_1.font_size = "18sp"

        about_2 = MDLabel(
            text="Version 1.4-dev",
            size_hint_y=None,
            height=dp(24),
            theme_text_color="Hint",
        )
        about_2.font_name = "Nunito-SemiBold"
        about_2.font_size = "14sp"

        about_card.add_widget(about_1)
        about_card.add_widget(about_2)
        root.add_widget(about_card)

        self.refresh_status()

    def _get_store(self):
        app = App.get_running_app()
        base = app.user_data_dir if app else "."
        return JsonStore(f"{base}/settings.json")

    def _get_pref(self, key, default):
        if self.store.exists("prefs"):
            return self.store.get("prefs").get(key, default)
        return default

    def _set_pref(self, key, value):
        data = {}
        if self.store.exists("prefs"):
            data = dict(self.store.get("prefs"))
        data[key] = bool(value)
        self.store.put("prefs", **data)

    def _section_title(self, text: str):
        lbl = MDLabel(
            text=text,
            size_hint_y=None,
            height=dp(28),
        )
        lbl.font_name = "Cause-Black"
        lbl.font_size = "22sp"
        return lbl

    def _action_button(self, text: str, callback):
        btn = MDFlatButton(
            text=text,
            size_hint=(1, None),
            height=dp(52),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
        )
        btn.font_name = "Inter_24pt-Bold"
        btn.font_size = "16sp"

        wrap = MDCard(
            size_hint_y=None,
            height=dp(58),
            radius=[dp(18)],
            padding=(dp(16), 0, dp(16), 0),
            md_bg_color=(0.08, 0.09, 0.11, 0.96),
            elevation=0,
        )
        wrap.add_widget(btn)
        btn.bind(on_release=callback)
        return wrap

    def _switch_row(self, parent, text, active, callback):
        from kivy.clock import Clock

        card = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(62),
            radius=[dp(18)],
            padding=(dp(16), dp(10), dp(16), dp(10)),
            md_bg_color=(0.08, 0.09, 0.11, 0.96),
            elevation=0,
            spacing=dp(12),
        )

        label = MDLabel(
            text=text,
            halign="left",
            valign="middle",
        )
        label.font_name = "Nunito-SemiBold"
        label.font_size = "15sp"

        switch_wrap = BoxLayout(
            orientation="horizontal",
            size_hint=(None, 1),
            width=dp(52),
        )

        switch = MDSwitch()
        switch.bind(active=callback)

        def set_initial_state(*_):
            switch.active = active

        Clock.schedule_once(set_initial_state, 0)

        switch_wrap.add_widget(switch)
        card.add_widget(label)
        card.add_widget(switch_wrap)
        parent.add_widget(card)
        return switch

    def _set_status(self, text: str):
        self.status_label.text = text
        self.refresh_status_meta()

    def refresh_status(self):
        initial_status = (
            "Drive linked" if self.drive_sync.uri else "Drive sync: not linked"
        )
        self.status_label.text = initial_status
        self.refresh_status_meta()

    def refresh_status_meta(self):
        last_backup_at = getattr(self.drive_sync, "last_backup_at", None)
        if last_backup_at:
            try:
                from datetime import datetime

                dt = datetime.fromtimestamp(last_backup_at)
                self.last_backup_label.text = (
                    f"Last backup: {dt.strftime('%Y-%m-%d %I:%M %p')}"
                )
            except Exception:
                self.last_backup_label.text = "Last backup: available"
        else:
            self.last_backup_label.text = "Last backup: never"

    def _after_import(self, imported_count, skipped_count):
        app = App.get_running_app()
        if app and hasattr(app, "refresh_history"):
            app.refresh_history()
        if app and hasattr(app, "refresh_reports"):
            app.refresh_reports()

        self._set_status(
            f"Imported {imported_count} transaction(s), skipped {skipped_count} duplicate(s)"
        )
