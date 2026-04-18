from kivy.app import App
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.core.text import Label as CoreLabel
from kivy.uix.anchorlayout import AnchorLayout
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from app.utils import rupees_to_paise, time_24_to_12


class AddScreen(BoxLayout):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)

        self.db = db
        self.orientation = "vertical"
        self.padding = (dp(12), dp(18), dp(12), dp(12))
        self.spacing = dp(6)

        self.selected_date = None
        self.selected_date_str = None
        self.selected_time_str = None

        self._cursor_ev = None
        self._cursor_on = False
        self._status_reset_event = None
        self._accent_rgba = (0.914, 0.094, 0.153, 1.0)
        self._amount_font_bias = 0

        self.main_card = MDCard(
            orientation="vertical",
            padding=(dp(18), dp(18), dp(18), dp(18)),
            spacing=dp(10),
            size_hint=(0.92, None),
            radius=[dp(24)],
        )
        self.main_card.md_bg_color = (0.08, 0.09, 0.11, 0.92)
        self.main_card.elevation = 0
        self.main_card.height = dp(400)
        self.main_card.pos_hint = {"center_x": 0.5}

        self.date_time_input = MDTextField(
            hint_text="Date & Time*",
            readonly=True,
        )
        self.date_time_input.font_name_hint_text = "Nunito-Medium"
        self.date_time_input.bind(on_touch_down=self.date_time_touch)

        self.item_input = MDTextField(hint_text="Item*")
        self.item_input.font_name_hint_text = "Nunito-Medium"

        hero_wrap = AnchorLayout(size_hint_y=None, height=dp(72))
        hero_wrap.padding = (0, 0, 0, dp(28))
        self.hero_wrap = hero_wrap

        hero_row = BoxLayout(
            orientation="horizontal",
            size_hint=(None, None),
            height=dp(72),
            spacing=dp(2),
        )
        self.hero_row = hero_row
        hero_row.width = dp(120)
        hero_row.bind(minimum_width=hero_row.setter("width"))

        self.hero_rupee = MDLabel(
            text="₹",
            halign="right",
            font_style="H3",
            size_hint=(None, None),
            size=(dp(26), dp(72)),
        )
        self.hero_rupee.font_name = "Inter_24pt-Medium"
        self.hero_rupee.theme_text_color = "Custom"
        self.hero_rupee.text_color = (1, 1, 1, 1)

        self.hero_amount = MDLabel(
            text="0",
            halign="left",
            font_style="H3",
            size_hint=(None, None),
            height=dp(72),
        )
        self.hero_amount.font_name = "Roboto-Regular"
        self.hero_amount.text_size = (None, None)
        self.hero_amount.theme_text_color = "Custom"
        self.hero_amount.text_color = (1, 1, 1, 0.90)

        self.hero_cursor = MDLabel(
            text="|",
            halign="left",
            font_style="H3",
            size_hint=(None, None),
            size=(dp(10), dp(72)),
        )
        self.hero_cursor.theme_text_color = "Custom"
        self.hero_cursor.padding = (0, 0, 0, dp(7))
        self.hero_cursor.text_color = self._accent_rgba
        self.hero_cursor.opacity = 0

        hero_row.add_widget(self.hero_rupee)
        hero_row.add_widget(self.hero_amount)
        hero_row.add_widget(self.hero_cursor)
        hero_wrap.add_widget(hero_row)

        self.add_transaction_label = MDLabel(
            text="Add Transaction",
            halign="center",
            size_hint_y=None,
            height=dp(34),
        )
        self.add_transaction_label.font_name = "Cause-Black"
        self.add_transaction_label.font_size = "28sp"

        self.total_amount_label = MDLabel(
            text="TOTAL AMOUNT",
            halign="center",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(18),
        )
        self.total_amount_label.font_name = "Nunito-Black"
        self.total_amount_label.font_size = "12sp"

        top_section = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(8),
        )
        top_section.add_widget(self.add_transaction_label)
        top_section.add_widget(BoxLayout(size_hint_y=None, height=dp(5)))
        top_section.add_widget(self.total_amount_label)
        top_section.add_widget(hero_wrap)
        top_section.bind(minimum_height=top_section.setter("height"))

        self.add_widget(top_section)

        self.amount_input = MDTextField(
            text="",
            hint_text="",
            input_filter="float",
            multiline=False,
            size_hint=(None, None),
            opacity=0,
        )
        self.amount_input.input_type = "number"
        self.amount_input.mode = "rectangle"
        self.amount_input.bind(focus=self._on_amount_focus)
        self.amount_input.bind(text=self._on_amount_text)
        self.amount_input.size = (dp(220), dp(72))
        self.amount_input.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.hero_wrap.add_widget(self.amount_input)

        self.note_input = MDTextField(hint_text="Note (optional)")
        self.note_input.font_name_hint_text = "Nunito-Medium"

        self.status_label = MDLabel(
            text="Fill details and press Save",
            halign="center",
            size_hint_y=None,
            height=dp(24),
        )
        self.status_label.font_name = "ComicSansMS3"
        self._status_default_text = self.status_label.text

        self.save_button = MDCard(
            size_hint=(1, None),
            height=dp(42),
            radius=[dp(18)],
            md_bg_color=self._accent_rgba,
            padding=(dp(16), 0, dp(16), 0),
            elevation=0,
        )

        button_row = BoxLayout(orientation="horizontal")
        self.button_text = MDLabel(
            text="Save Transaction",
            halign="center",
            valign="middle",
            bold=True,
        )
        self.button_text.font_name = "Inter_24pt-Bold"
        self.button_text.font_size = "22sp"
        self.button_text.theme_text_color = "Custom"
        self.button_text.text_color = (0, 0, 0, 1)
        button_row.add_widget(self.button_text)

        self.save_button.add_widget(button_row)
        self.save_button.bind(on_press=self.on_save)

        self.date_time_input.mode = "line"
        self.item_input.mode = "line"
        self.note_input.mode = "line"

        for f in (self.date_time_input, self.item_input, self.note_input):
            f.size_hint_y = None
            f.height = dp(48)
            f.fill_color = (0, 0, 0, 0)
            f.line_color_normal = (0, 0, 0, 0)
            f.line_color_focus = (0, 0, 0, 0)
            f.md_bg_color = (0, 0, 0, 0)
            f.background_color = (0, 0, 0, 0)
            f.line_width = 0
            f.line_width_focus = 0

        self.pill_cards = []

        def pill_row(field, left_icon, right_icon=None, on_right=None):
            p = MDCard(
                size_hint_y=None,
                height=dp(70),
                radius=[dp(18)],
                md_bg_color=(0.05, 0.06, 0.07, 0.85),
                padding=(dp(10), dp(8), dp(10), dp(8)),
                elevation=0,
            )

            row = BoxLayout(orientation="horizontal", spacing=dp(8))

            left = MDIconButton(icon=left_icon, disabled=True)
            left.user_font_size = "18sp"
            left.theme_text_color = "Custom"
            left.text_color = (1, 1, 1, 0.70)
            left.size_hint = (None, None)
            left.size = (dp(36), dp(36))

            field.size_hint_x = 1
            row.add_widget(left)

            field_wrap = AnchorLayout(anchor_y="bottom")
            field_wrap.add_widget(field)
            row.add_widget(field_wrap)

            if right_icon:
                right = MDIconButton(icon=right_icon)
                right.user_font_size = "20sp"
                right.theme_text_color = "Custom"
                right.text_color = (1, 1, 1, 0.70)
                right.size_hint = (None, None)
                right.size = (dp(36), dp(36))

                if on_right:
                    right.bind(on_press=lambda *_: on_right())

                row.add_widget(right)

            p.add_widget(row)
            self.pill_cards.append(p)
            return p

        self.item_name_label = MDLabel(
            text="ITEM NAME",
            font_style="Caption",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(16),
        )
        self.item_name_label.font_name = "Nunito-Black"
        self.item_name_label.font_size = "14sp"

        self.details_label = MDLabel(
            text="DETAILS",
            font_style="Caption",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(16),
        )
        self.details_label.font_name = "Nunito-Black"
        self.details_label.font_size = "14sp"

        self.main_card.add_widget(self.item_name_label)
        self.main_card.add_widget(pill_row(self.item_input, "tag-outline"))

        self.main_card.add_widget(self.details_label)
        self.main_card.add_widget(pill_row(self.note_input, "pencil-outline"))

        self.main_card.add_widget(
            pill_row(
                self.date_time_input,
                "calendar-month-outline",
                "chevron-down",
                self.open_date_picker,
            )
        )

        self.main_card.add_widget(self.status_label)
        self.main_card.add_widget(self.save_button)

        self.add_widget(self.main_card)
        self.apply_prefs()
        self._fit_hero_amount()

    def _store(self):
        app = App.get_running_app()
        base = app.user_data_dir if app else "."
        return JsonStore(f"{base}/settings.json")

    def _get_pref(self, key, default, legacy_fallback=None):
        store = self._store()
        if store.exists("prefs"):
            data = store.get("prefs")
            if key in data:
                return data.get(key, default)
            if legacy_fallback and legacy_fallback in data:
                old = data.get(legacy_fallback)
                if isinstance(default, str):
                    return "on" if old else "off"
                return old
        return default

    def _accent_rgba_from_pref(self):
        accent = self._get_pref("accent_color", "red")
        palette = {
            "red": (0.914, 0.094, 0.153, 1.0),
            "blue": (0.18, 0.52, 0.98, 1.0),
            "purple": (0.62, 0.33, 0.95, 1.0),
            "green": (0.18, 0.72, 0.38, 1.0),
        }
        return palette.get(accent, palette["red"])

    def _card_alpha_from_pref(self):
        mode = self._get_pref("card_transparency", "normal")
        return {
            "glass": 0.74,
            "normal": 0.92,
            "dark": 0.98,
        }.get(mode, 0.92)

    def _corner_radius_from_pref(self):
        mode = self._get_pref("corner_style", "rounded")
        return {
            "soft": dp(16),
            "rounded": dp(24),
            "extra": dp(32),
        }.get(mode, dp(24))

    def _status_timeout_seconds(self):
        mode = self._get_pref("save_status_timeout", "normal")
        return {
            "short": 3,
            "normal": 5,
            "long": 8,
        }.get(mode, 5)

    def apply_prefs(self):
        self._accent_rgba = self._accent_rgba_from_pref()
        alpha = self._card_alpha_from_pref()
        radius = self._corner_radius_from_pref()
        large_ui = self._get_pref("large_ui_text", "off") == "on"
        compact = self._get_pref("compact_mode", "normal") == "compact"
        amount_mode = self._get_pref("amount_font_size_mode", "auto")

        self._amount_font_bias = {
            "auto": 0,
            "smaller": -6,
            "bigger": 6,
        }.get(amount_mode, 0)

        self.padding = (
            (dp(10), dp(14), dp(10), dp(10))
            if compact
            else (dp(12), dp(18), dp(12), dp(12))
        )
        self.spacing = dp(4) if compact else dp(6)

        self.main_card.md_bg_color = (0.08, 0.09, 0.11, alpha)
        self.main_card.radius = [radius]
        self.main_card.height = dp(382) if compact else dp(400)
        self.main_card.padding = (
            (dp(16), dp(16), dp(16), dp(16))
            if compact
            else (dp(18), dp(18), dp(18), dp(18))
        )
        self.main_card.spacing = dp(8) if compact else dp(10)

        for pill in self.pill_cards:
            pill.radius = [max(dp(14), radius - dp(6))]
            pill.md_bg_color = (0.05, 0.06, 0.07, min(alpha, 0.90))
            pill.height = dp(64) if compact else dp(70)

        self.save_button.radius = [max(dp(14), radius - dp(6))]
        self.save_button.md_bg_color = self._accent_rgba
        self.save_button.height = dp(40) if compact else dp(42)

        self.hero_cursor.text_color = self._accent_rgba

        self.add_transaction_label.font_size = "30sp" if large_ui else "28sp"
        self.total_amount_label.font_size = "13sp" if large_ui else "12sp"
        self.item_name_label.font_size = "15sp" if large_ui else "14sp"
        self.details_label.font_size = "15sp" if large_ui else "14sp"
        self.status_label.font_size = "15sp" if large_ui else "14sp"
        self.button_text.font_size = "24sp" if large_ui else "22sp"

        self.item_input.font_size = "17sp" if large_ui else "16sp"
        self.note_input.font_size = "17sp" if large_ui else "16sp"
        self.date_time_input.font_size = "17sp" if large_ui else "16sp"

        self._fit_hero_amount()

    def on_open(self):
        if self._get_pref("auto_focus_item_on_open", "on") == "on":
            Clock.schedule_once(
                lambda *_: setattr(self.item_input, "focus", True), 0.08
            )

    def set_status(self, text: str):
        self.status_label.text = text

        if self._status_reset_event is not None:
            self._status_reset_event.cancel()
            self._status_reset_event = None

        self._status_reset_event = Clock.schedule_once(
            self._reset_status,
            self._status_timeout_seconds(),
        )

    def _reset_status(self, *_):
        self.status_label.text = self._status_default_text
        self._status_reset_event = None

    def _clear_amount_ui(self):
        self.amount_input.text = ""
        self.hero_amount.text = "0"
        self._fit_hero_amount()

    def _refresh_date_time_display(self):
        if self.selected_date_str and self.selected_time_str:
            display_time = time_24_to_12(self.selected_time_str)
            self.date_time_input.text = f"{self.selected_date_str} • {display_time}"
        else:
            self.date_time_input.text = ""

    def on_save(self, instance):
        if self.selected_date_str is None or self.selected_time_str is None:
            self.set_status("Pick date & time")
            return

        date_str = self.selected_date_str
        time_str = self.selected_time_str

        item = self.item_input.text.strip()
        amount_text = self.amount_input.text.strip()
        note = self.note_input.text.strip()

        if not item:
            self.set_status("Item required")
            return

        try:
            amount = rupees_to_paise(amount_text)
        except Exception:
            self.set_status("Invalid amount")
            return

        self.db.add_transaction(date_str, time_str, item, amount, note)
        self.set_status("Saved")

        app = App.get_running_app()
        if app and hasattr(app, "refresh_history"):
            app.refresh_history()
        if app and hasattr(app, "refresh_reports"):
            app.refresh_reports()

        keep_datetime = self._get_pref("keep_datetime_after_save", "on") == "on"
        keep_note = (
            self._get_pref(
                "default_note_retain",
                "off",
                legacy_fallback="keep_note_after_save",
            )
            == "on"
        )
        reopen_keyboard = (
            self._get_pref("auto_reopen_keyboard_after_save", "on") == "on"
        )

        self.item_input.text = ""
        self._clear_amount_ui()

        if not keep_note:
            self.note_input.text = ""

        if not keep_datetime:
            self.selected_date = None
            self.selected_date_str = None
            self.selected_time_str = None

        self._refresh_date_time_display()

        self.amount_input.focus = False
        self.item_input.focus = reopen_keyboard

    def _format_inr_display(self, raw: str) -> str:
        if not raw:
            return "0"

        keep_dot = raw.endswith(".")
        if "." in raw:
            int_part, frac_part = raw.split(".", 1)
        else:
            int_part, frac_part = raw, ""

        int_part = int_part.lstrip("0") or "0"

        if len(int_part) <= 3:
            grouped = int_part
        else:
            last3 = int_part[-3:]
            rest = int_part[:-3]
            groups = []

            while len(rest) > 2:
                groups.insert(0, rest[-2:])
                rest = rest[:-2]

            if rest:
                groups.insert(0, rest)

            grouped = ",".join(groups + [last3])

        if keep_dot:
            return grouped + "."
        if frac_part:
            return grouped + "." + frac_part

        return grouped

    def _on_amount_focus(self, instance, focused: bool):
        if focused:
            self._cursor_on = True
            self.hero_cursor.opacity = 1

            if self._cursor_ev is None:
                self._cursor_ev = Clock.schedule_interval(self._blink_cursor, 0.5)
        else:
            if self._cursor_ev is not None:
                self._cursor_ev.cancel()
                self._cursor_ev = None

            self.hero_cursor.opacity = 0
            self._cursor_on = False

            if not self.amount_input.text.strip():
                self.hero_amount.text = "0"
                self._fit_hero_amount()

    def _on_amount_text(self, instance, value: str):
        raw = value.replace(",", "").strip()
        raw = "".join(ch for ch in raw if (ch.isdigit() or ch == "."))

        if raw.count(".") > 1:
            first = raw.find(".")
            raw = raw[: first + 1] + raw[first + 1 :].replace(".", "")

        if raw != instance.text:
            instance.text = raw
            return

        self.hero_amount.text = self._format_inr_display(raw) if raw else "0"
        self._fit_hero_amount()

    def _fit_hero_amount(self):
        from kivy.core.window import Window

        max_row_w = min(dp(360), Window.width * 0.78)

        spacing = dp(2)
        avail_digits_w = (
            max_row_w - self.hero_rupee.width - spacing - self.hero_cursor.width
        )

        default_fs = dp(56) + self._amount_font_bias
        min_fs = dp(34) + min(0, self._amount_font_bias)

        text = self.hero_amount.text if self.hero_amount.text else "0"

        fs = default_fs
        while fs > min_fs:
            lbl = CoreLabel(text=text, font_size=fs)
            lbl.refresh()
            w = lbl.texture.size[0]

            if w <= avail_digits_w:
                break
            fs -= dp(2)

        self.hero_amount.font_size = fs

        lbl = CoreLabel(text=text, font_size=fs)
        lbl.refresh()
        digits_w = min(lbl.texture.size[0], avail_digits_w)

        self.hero_amount.size_hint = (None, None)
        self.hero_amount.width = digits_w
        self.hero_amount.height = dp(72)

        self.hero_row.size_hint = (None, None)
        self.hero_row.width = (
            self.hero_rupee.width + spacing + digits_w + self.hero_cursor.width
        )
        self.hero_row.height = dp(72)

        self.amount_input.size = (max_row_w, dp(72))

    def on_touch_down(self, touch):
        return super().on_touch_down(touch)

    def date_time_touch(self, widget, touch):
        if widget.collide_point(*touch.pos):
            self.open_date_picker()
        return False

    def open_date_picker(self):
        from datetime import date
        from itertools import zip_longest

        picker = MDDatePicker()
        primary = self._accent_rgba
        secondary = (0.08, 0.09, 0.11, 0.98)
        picker.md_bg_color = primary
        picker.background_color = secondary
        picker.primary_color = primary
        picker.accent_color = secondary
        picker.selector_color = primary
        picker.text_color = (1, 1, 1, 1)
        picker.text_weekday_color = (1, 1, 1, 0.6)
        picker.text_toolbar_color = (1, 1, 1, 1)
        picker.text_button_color = primary
        picker.line_color = primary
        picker.font_name = "Inter_24pt-Black"

        def _apply_max_date():
            today = date.today()
            dates = picker.calendar.itermonthdates(picker.year, picker.month)
            for widget, widget_date in zip_longest(picker._calendar_list, dates):
                if widget is None or widget_date is None:
                    continue
                if widget_date > today:
                    widget.disabled = True

        orig_update = picker.update_calendar

        def _update_calendar_with_limit(year, month):
            orig_update(year, month)
            _apply_max_date()

        picker.update_calendar = _update_calendar_with_limit
        try:
            picker.update_calendar(picker.year, picker.month)
        except Exception:
            pass

        picker.bind(on_save=self.on_date_selected, on_cancel=self.on_picker_cancel)
        picker.open()

    def on_date_selected(self, instance, value, date_range):
        self.selected_date = value
        self.selected_date_str = value.strftime("%Y-%m-%d")
        self.open_time_picker()

    def open_time_picker(self):
        picker = MDTimePicker()
        primary = self._accent_rgba
        secondary = (0.08, 0.09, 0.11, 0.98)
        picker.md_bg_color = secondary
        picker.background_color = primary
        picker.primary_color = secondary
        picker.accent_color = primary
        picker.selector_color = primary
        picker.text_color = (1, 1, 1, 1)
        picker.text_toolbar_color = (1, 1, 1, 1)
        picker.text_button_color = primary
        picker.line_color = primary
        picker.font_name = "Inter_24pt-Black"
        picker.bind(time=self.on_time_selected, on_cancel=self.on_time_cancel)
        picker.open()

    def on_time_selected(self, instance, time_value):
        if self.selected_date is None:
            return

        self.selected_time_str = f"{time_value.hour:02d}:{time_value.minute:02d}"
        self._refresh_date_time_display()

    def on_time_cancel(self, *args):
        self.selected_date = None
        self.selected_date_str = None
        self.selected_time_str = None
        self.date_time_input.text = ""

    def on_picker_cancel(self, instance, value):
        pass

    def _blink_cursor(self, dt):
        self._cursor_on = not self._cursor_on
        self.hero_cursor.opacity = 1 if self._cursor_on else 0
