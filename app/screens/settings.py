from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton


class SettingsScreen(BoxLayout):
    def __init__(self, db, drive_sync, **kwargs):
        super().__init__(**kwargs)

        self.db = db
        self.drive_sync = drive_sync
        self.drive_sync.set_status_callback(self._set_status)

        # ---------- HARD-CODE ALIGNMENT CONTROLS ----------
        # Change these if you want to manually align Settings better.
        self._page_pad_x = dp(10)  # outer page left/right padding
        self._content_pad_x = dp(6)  # inner scroll content left/right padding
        self._panel_width = dp(
            320
        )  # MAIN hardcoded width for all setting cards/buttons
        self._panel_inner_x = dp(
            14
        )  # inner left/right padding inside backup/import buttons
        self._row_spacing = dp(14)  # space between rows
        self._choice_button_width = dp(132)  # width of right-side value button
        # -----------------------------------------------

        self.db = db
        self.orientation = "vertical"
        self.padding = (self._page_pad_x, dp(4), self._page_pad_x, dp(8))

        self.store = self._get_store()

        self._panel_cards = []
        self._section_labels = []
        self._value_buttons = []
        self._action_buttons = []
        self._choice_rows = []

        scroll = ScrollView(do_scroll_x=False)
        self.add_widget(scroll)

        self.root_column = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            spacing=self._row_spacing,
            padding=(self._content_pad_x, dp(8), self._content_pad_x, dp(24)),
        )
        self.root_column.bind(minimum_height=self.root_column.setter("height"))
        scroll.add_widget(self.root_column)

        # ---------- Status ----------
        self.status_card = self._panel_card(height=dp(118))
        self.status_card.orientation = "vertical"
        self.status_card.spacing = dp(4)
        self.status_card.padding = (dp(16), dp(14), dp(16), dp(14))

        self.status_title = MDLabel(text="Status", size_hint_y=None, height=dp(22))
        self.status_title.font_name = "Nunito-ExtraBold"
        self.status_title.font_size = "18sp"

        self.status_label = MDLabel(
            text="Ready",
            size_hint_y=None,
            height=dp(36),
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

        self.status_card.add_widget(self.status_title)
        self.status_card.add_widget(self.status_label)
        self.status_card.add_widget(self.last_backup_label)
        self.root_column.add_widget(self.status_card)

        # ---------- Backup ----------
        self.root_column.add_widget(self._section_title("Backup & Restore"))
        self.root_column.add_widget(
            self._action_button(
                "LINK DRIVE FILE",
                lambda *_: self.drive_sync.link_drive(),
            )
        )
        self.root_column.add_widget(
            self._action_button(
                "BACKUP NOW",
                lambda *_: self.drive_sync.sync_db(self.db),
            )
        )
        self.root_column.add_widget(
            self._action_button(
                "IMPORT TRANSACTIONS FROM JSON",
                lambda *_: self.drive_sync.import_json(
                    self.db,
                    on_complete=self._after_import,
                ),
            )
        )

        # ---------- Entry ----------
        self.root_column.add_widget(self._section_title("Entry Preferences"))

        self.root_column.add_widget(
            self._choice_row(
                "Keep date & time after save",
                "keep_datetime_after_save",
                [("off", "Off"), ("on", "On")],
            )
        )

        self.root_column.add_widget(
            self._choice_row(
                "Keep note after save",
                "default_note_retain",
                [("off", "Off"), ("on", "On")],
                legacy_fallback="keep_note_after_save",
            )
        )

        # ---------- Appearance ----------
        self.root_column.add_widget(self._section_title("Appearance"))

        self.root_column.add_widget(
            self._choice_row(
                "Background dim strength",
                "bg_dim_strength",
                [
                    ("off", "Off"),
                    ("low", "Low"),
                    ("medium", "Medium"),
                    ("high", "High"),
                ],
                on_change=self._after_pref_change,
            )
        )

        self.root_column.add_widget(
            self._choice_row(
                "Card transparency style",
                "card_transparency",
                [
                    ("normal", "Normal"),
                    ("glass", "Glass"),
                    ("dark", "Dark"),
                ],
                on_change=self._after_pref_change,
            )
        )

        self.root_column.add_widget(
            self._choice_row(
                "Accent color",
                "accent_color",
                [
                    ("red", "Red"),
                    ("blue", "Blue"),
                    ("purple", "Purple"),
                    ("green", "Green"),
                ],
                on_change=self._after_pref_change,
            )
        )

        self.root_column.add_widget(
            self._choice_row(
                "Larger UI text",
                "large_ui_text",
                [("off", "Off"), ("on", "On")],
                on_change=self._after_pref_change,
            )
        )

        self.root_column.add_widget(
            self._choice_row(
                "Layout spacing",
                "compact_mode",
                [("normal", "Normal"), ("compact", "Compact")],
                on_change=self._after_pref_change,
            )
        )

        self.root_column.add_widget(
            self._choice_row(
                "Corner style",
                "corner_style",
                [
                    ("soft", "Soft"),
                    ("rounded", "Rounded"),
                    ("extra", "Extra"),
                ],
                on_change=self._after_pref_change,
            )
        )

        # ---------- Navigation ----------
        self.root_column.add_widget(self._section_title("Navigation"))

        self.root_column.add_widget(
            self._choice_row(
                "Bottom dock height",
                "dock_height_mode",
                [("normal", "Normal"), ("tall", "Tall")],
                on_change=self._after_pref_change,
            )
        )

        self.root_column.add_widget(
            self._choice_row(
                "Bottom dock lift",
                "dock_lift_mode",
                [("normal", "Normal"), ("high", "High")],
                on_change=self._after_pref_change,
            )
        )

        self.root_column.add_widget(
            self._choice_row(
                "Show labels under nav icons",
                "show_nav_labels",
                [("on", "Yes"), ("off", "No")],
                on_change=self._after_pref_change,
            )
        )

        self.root_column.add_widget(
            self._choice_row(
                "Animation speed",
                "animation_speed",
                [
                    ("normal", "Normal"),
                    ("fast", "Fast"),
                    ("off", "Off"),
                ],
                on_change=self._after_pref_change,
            )
        )

        # ---------- Add Screen ----------
        self.root_column.add_widget(self._section_title("Add Screen"))

        self.root_column.add_widget(
            self._choice_row(
                "Auto focus item on open",
                "auto_focus_item_on_open",
                [("off", "Off"), ("on", "On")],
            )
        )

        self.root_column.add_widget(
            self._choice_row(
                "Auto reopen keyboard after save",
                "auto_reopen_keyboard_after_save",
                [("off", "Off"), ("on", "On")],
            )
        )

        self.root_column.add_widget(
            self._choice_row(
                "Save status timeout",
                "save_status_timeout",
                [
                    ("normal", "Normal"),
                    ("short", "Short"),
                    ("long", "Long"),
                ],
            )
        )

        self.root_column.add_widget(
            self._choice_row(
                "Amount font size mode",
                "amount_font_size_mode",
                [
                    ("auto", "Auto"),
                    ("smaller", "Smaller"),
                    ("bigger", "Bigger"),
                ],
            )
        )

        # ---------- About ----------
        self.root_column.add_widget(self._section_title("About"))

        self.about_card = self._panel_card(height=dp(96))
        self.about_card.orientation = "vertical"
        self.about_card.padding = (dp(16), dp(14), dp(16), dp(14))

        self.about_title = MDLabel(text="TxTracker", size_hint_y=None, height=dp(24))
        self.about_title.font_name = "Nunito-ExtraBold"
        self.about_title.font_size = "18sp"

        self.about_version = MDLabel(
            text="Version 2.0 Release",
            size_hint_y=None,
            height=dp(24),
            theme_text_color="Hint",
        )
        self.about_version.font_name = "Nunito-SemiBold"
        self.about_version.font_size = "14sp"

        self.about_card.add_widget(self.about_title)
        self.about_card.add_widget(self.about_version)
        self.root_column.add_widget(self.about_card)

        self.refresh_status()
        self.apply_prefs()

    def _get_store(self):
        app = App.get_running_app()
        base = app.user_data_dir if app else "."
        return JsonStore(f"{base}/settings.json")

    def _get_pref(self, key, default, legacy_fallback=None):
        if self.store.exists("prefs"):
            data = self.store.get("prefs")
            if key in data:
                return data.get(key, default)
            if legacy_fallback and legacy_fallback in data:
                old = data.get(legacy_fallback)
                if isinstance(default, str):
                    return "on" if old else "off"
                return old
        return default

    def _set_pref(self, key, value):
        data = {}
        if self.store.exists("prefs"):
            data = dict(self.store.get("prefs"))
        data[key] = value
        self.store.put("prefs", **data)

    def _panel_card(self, height):
        card = MDCard(
            size_hint=(None, None),
            width=self._panel_width,
            pos_hint={"center_x": 0.5},
            height=height,
            radius=[dp(18)],
            md_bg_color=(0.08, 0.09, 0.11, 0.96),
            elevation=0,
        )
        self._panel_cards.append(card)
        return card

    def _section_title(self, text: str):
        lbl = MDLabel(text=text, size_hint_y=None, height=dp(28))
        lbl.font_name = "Cause-Black"
        lbl.font_size = "22sp"
        self._section_labels.append(lbl)
        return lbl

    def _action_button(self, text: str, callback):
        wrap = self._panel_card(height=dp(58))
        wrap.padding = (dp(14), 0, dp(14), 0)

        btn = MDFlatButton(
            text=text,
            size_hint=(1, 1),
            theme_text_color="Custom",
            text_color=self._accent_rgba(),
        )
        btn.font_name = "Inter_24pt-Bold"
        btn.font_size = "14sp"

        btn.bind(on_release=callback)
        wrap.add_widget(btn)
        self._action_buttons.append(btn)
        return wrap

    def _choice_row(self, title, key, options, on_change=None, legacy_fallback=None):
        row = self._panel_card(height=dp(66))
        row.orientation = "horizontal"
        row.padding = (dp(16), dp(10), dp(16), dp(10))
        row.spacing = dp(10)

        label = MDLabel(
            text=title,
            halign="left",
            valign="middle",
        )
        label.font_name = "Nunito-SemiBold"
        label.font_size = "15sp"

        btn = MDFlatButton(
            text="",
            size_hint=(None, None),
            width=self._choice_button_width,
            height=dp(40),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
        )
        btn.font_name = "Inter_24pt-Bold"
        btn.font_size = "13sp"

        current_value = self._get_pref(
            key, options[0][0], legacy_fallback=legacy_fallback
        )
        btn.text = self._label_for_value(options, current_value)

        def cycle_value(*_):
            value_list = [v for v, _ in options]
            if current_value_holder["value"] not in value_list:
                current_value_holder["value"] = options[0][0]

            idx = value_list.index(current_value_holder["value"])
            idx = (idx + 1) % len(options)
            new_value = value_list[idx]
            current_value_holder["value"] = new_value
            self._set_pref(key, new_value)
            btn.text = self._label_for_value(options, new_value)

            if on_change:
                on_change(new_value)
            else:
                self._after_pref_change()

        current_value_holder = {"value": current_value}

        btn.bind(on_release=cycle_value)

        row.add_widget(label)
        row.add_widget(btn)

        self._value_buttons.append(btn)
        self._choice_rows.append((label, btn))
        return row

    def _label_for_value(self, options, value):
        for k, label in options:
            if k == value:
                return label
        return options[0][1]

    def _accent_rgba(self):
        accent = self._get_pref("accent_color", "red")
        palette = {
            "red": (0.914, 0.094, 0.153, 1.0),
            "blue": (0.18, 0.52, 0.98, 1.0),
            "purple": (0.62, 0.33, 0.95, 1.0),
            "green": (0.18, 0.72, 0.38, 1.0),
        }
        return palette.get(accent, palette["red"])

    def _card_alpha(self):
        mode = self._get_pref("card_transparency", "normal")
        return {
            "glass": 0.74,
            "normal": 0.92,
            "dark": 0.98,
        }.get(mode, 0.92)

    def _corner_radius(self):
        mode = self._get_pref("corner_style", "soft")
        return {
            "soft": dp(14),
            "rounded": dp(18),
            "extra": dp(26),
        }.get(mode, dp(18))

    def apply_prefs(self):
        accent = self._accent_rgba()
        alpha = self._card_alpha()
        radius = self._corner_radius()
        large_ui = self._get_pref("large_ui_text", "off") == "on"
        compact = self._get_pref("compact_mode", "normal") == "compact"

        self.root_column.spacing = dp(10) if compact else self._row_spacing
        self.root_column.padding = (
            self._content_pad_x,
            dp(6) if compact else dp(8),
            self._content_pad_x,
            dp(20) if compact else dp(24),
        )

        for card in self._panel_cards:
            card.md_bg_color = (0.08, 0.09, 0.11, alpha)
            card.radius = [radius]
            card.width = self._panel_width

        for lbl in self._section_labels:
            lbl.font_size = "24sp" if large_ui else "22sp"

        self.status_title.font_size = "19sp" if large_ui else "18sp"
        self.status_label.font_size = "15sp" if large_ui else "14sp"
        self.last_backup_label.font_size = "13sp" if large_ui else "12sp"
        self.about_title.font_size = "19sp" if large_ui else "18sp"
        self.about_version.font_size = "15sp" if large_ui else "14sp"

        for btn in self._action_buttons:
            btn.text_color = accent
            btn.font_size = "15sp" if large_ui else "14sp"

        for _, btn in self._choice_rows:
            btn.text_color = accent
            btn.font_size = "14sp" if large_ui else "13sp"

        for label, _ in self._choice_rows:
            label.font_size = "16sp" if large_ui else "15sp"

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

    def _after_pref_change(self, *_):
        self.apply_prefs()
        app = App.get_running_app()
        if not app:
            return

        if hasattr(app, "root_ui"):
            try:
                app.root_ui.apply_visual_prefs()
            except Exception:
                pass
            try:
                app.root_ui.add_screen.apply_prefs()
            except Exception:
                pass

    def _after_import(self, imported_count, skipped_count):
        app = App.get_running_app()
        if app and hasattr(app, "refresh_history"):
            app.refresh_history()
        if app and hasattr(app, "refresh_reports"):
            app.refresh_reports()

        self._set_status(
            f"Imported {imported_count} transaction(s), skipped {skipped_count} duplicate(s)"
        )
