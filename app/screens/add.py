import time
from datetime import datetime
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFillRoundFlatButton, MDIconButton
from kivy.core.text import Label as CoreLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.metrics import dp
from app.utils import rupees_to_paise, time_24_to_12


class AddScreen(BoxLayout):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.orientation = "vertical"
        self.padding = (12, 18, 12, 12)
        self.spacing = 6

        card = MDCard(
            orientation="vertical",
            padding=(18, 20, 18, 18),
            spacing=10,
            size_hint=(0.92, None),
            radius=[24],
        )
        card.md_bg_color = (0.08, 0.09, 0.11, 0.92)
        card.elevation = 0
        card.height = 420
        card.pos_hint = {"center_x": 0.5}

        self.date_time_input = MDTextField(
            hint_text="Date & Time (tap to pick)",
            readonly=True,
        )
        self.date_time_input.bind(on_touch_down=self.date_time_touch)
        self.selected_date_str = None
        self.selected_time_str = None

        self.item_input = MDTextField(hint_text="Item (e.g. Tea)")
        # --- HERO AMOUNT (display) ---
        from kivy.uix.anchorlayout import AnchorLayout

        hero_wrap = AnchorLayout(size_hint_y=None, height=dp(72))
        self.hero_wrap = hero_wrap

        hero_row = BoxLayout(
            orientation="horizontal",
            size_hint=(None, None),
            height=dp(72),
            spacing=dp(2),
        )
        self.hero_row = hero_row
        hero_row.size_hint = (None, None)
        hero_row.width = dp(120)
        hero_row.bind(minimum_width=hero_row.setter("width"))

        self.hero_rupee = MDLabel(
            text="₹",
            halign="right",
            font_style="H3",
            size_hint=(None, None),
            size=(dp(26), dp(72)),
        )
        self.hero_rupee.theme_text_color = "Custom"
        self.hero_rupee.text_color = (1, 1, 1, 1)

        self.hero_amount = MDLabel(
            text="0",
            halign="left",
            font_style="H3",
            size_hint=(None, None),
            height=(dp(72)),
        )
        self.hero_amount.text_size = (None, None)
        self.hero_amount.theme_text_color = "Custom"
        self.hero_amount.text_color = (1, 1, 1, 0.90)

        hero_row.add_widget(self.hero_rupee)
        hero_row.add_widget(self.hero_amount)
        hero_wrap.add_widget(hero_row)

        self.add_widget(
            MDLabel(
                text="Add Transaction",
                halign="center",
                font_style="H6",
                size_hint_y=None,
                height=dp(34),
            )
        )

        self.add_widget(
            MDLabel(
                text="TOTAL AMOUNT",
                halign="center",
                font_style="Caption",
                theme_text_color="Hint",
                size_hint_y=None,
                height=dp(18),
            )
        )

        self.add_widget(hero_wrap)

        # --- REAL INPUT (hidden, used only for typing) ---
        self.amount_input = MDTextField(
            text="",
            hint_text="",
            input_filter="float",
            multiline=False,
            size_hint=(None, None),
            opacity=0,
        )
        self.amount_input.input_type = "number"
        self.amount_input.bind(focus=self._on_amount_focus)
        self.amount_input.bind(text=self._on_amount_text)
        self.amount_input.size = (dp(220), dp(72))
        self.amount_input.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.amount_input.background_color = (0, 0, 0, 0)
        self.amount_input.md_bg_color = (0, 0, 0, 0)
        self.amount_input.line_color_normal = (0, 0, 0, 0)
        self.amount_input.line_color_focus = (0, 0, 0, 0)
        self.hero_wrap.add_widget(self.amount_input)

        self.note_input = MDTextField(hint_text="Note (optional)")

        self.status_label = MDLabel(
            text="", halign="center", size_hint_y=None, height=24
        )

        self.save_button = MDFillRoundFlatButton(text="Save Transaction", size_hint_x=1)
        self.save_button.md_bg_color = (0.96, 0.40, 0.46, 1)
        self.save_button.text_color = (0, 0, 0, 1)
        self.save_button.size_hint_y = None
        self.save_button.height = 48
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

        def pill_row(
            field, left_icon: str, right_icon: str | None = None, on_right=None
        ):
            p = MDCard(
                size_hint_y=None,
                height=dp(70),
                radius=[18],
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
            from kivy.uix.anchorlayout import AnchorLayout

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
            return p

        card.add_widget(
            MDLabel(
                text="ITEM NAME",
                font_style="Caption",
                theme_text_color="Hint",
                size_hint_y=None,
                height=dp(16),
            )
        )
        card.add_widget(pill_row(self.item_input, "tag-outline"))

        card.add_widget(
            MDLabel(
                text="DETAILS",
                font_style="Caption",
                theme_text_color="Hint",
                size_hint_y=None,
                height=dp(16),
            )
        )
        card.add_widget(pill_row(self.note_input, "pencil-outline"))

        card.add_widget(
            pill_row(
                self.date_time_input,
                "calendar-month-outline",
                "chevron-down",
                self.open_date_picker,
            )
        )

        card.add_widget(self.status_label)
        card.add_widget(self.save_button)

        self.add_widget(card)
        self._fit_hero_amount()

    def on_save(self, instance):

        if self.selected_date_str is None or self.selected_time_str is None:
            self.status_label.text = "Pick date & time"
            return

        date_str = self.selected_date_str
        time_str = self.selected_time_str

        item = self.item_input.text.strip()
        amount_text = self.amount_input.text.replace(",", "").strip()
        note = self.note_input.text.strip()

        if not item:
            self.status_label.text = "Item required"
            return

        try:
            amount = rupees_to_paise(amount_text)
        except Exception:
            self.status_label.text = "Invalid amount"
            return

        self.db.add_transaction(date_str, time_str, item, amount, note)

        self.status_label.text = "Saved"

        app = App.get_running_app()
        if app and hasattr(app, "refresh_history"):
            app.refresh_history()
        if app and hasattr(app, "refresh_reports"):
            app.refresh_reports()

        print("Date: ", date_str)
        print("Time: ", time_str)
        print("ITEM: ", item)
        print("AMOUNT: ", amount)
        print("NOTE: ", note)

        self.item_input.text = ""
        self.amount_input.text = ""
        self.note_input.text = ""
        self.date_time_input.text = ""
        self.selected_date_str = None
        self.selected_time_str = None

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
        if not focused and not self.amount_input.text.strip():
            self.hero_amount.text = "0"

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
        avail_digits_w = max_row_w - self.hero_rupee.width - spacing

        default_fs = dp(56)
        min_fs = dp(34)

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
        self.hero_row.width = self.hero_rupee.width + spacing + digits_w
        self.hero_row.height = dp(72)

        self.amount_input.size = (max_row_w, dp(72))

    def on_touch_down(self, touch):
        return super().on_touch_down(touch)

    def date_time_touch(self, widget, touch):
        if widget.collide_point(*touch.pos):
            self.open_date_picker()
        return False

    def open_date_picker(self):
        picker = MDDatePicker()
        picker.bind(on_save=self.on_date_selected, on_cancel=self.on_picker_cancel)
        picker.open()

    def on_date_selected(self, instance, value, date_range):
        self.selected_date = value
        self.selected_date_str = value.strftime("%Y-%m-%d")
        self.open_time_picker()

    def open_time_picker(self):
        picker = MDTimePicker()
        picker.bind(time=self.on_time_selected)
        picker.open()

    def on_time_selected(self, instance, time_value):
        if self.selected_date is None:
            return

        date_time = datetime(
            self.selected_date.year,
            self.selected_date.month,
            self.selected_date.day,
            time_value.hour,
            time_value.minute,
        )

        self.selected_time_str = f"{time_value.hour:02d}:{time_value.minute:02d}"

        display_time = time_24_to_12(self.selected_time_str)
        self.date_time_input.text = f"{self.selected_date_str} • {display_time}"

    def on_picker_cancel(self, instance, value):
        pass
