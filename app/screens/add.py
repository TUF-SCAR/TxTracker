import time
from datetime import datetime
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from app.utils import rupees_to_paise


class AddScreen(BoxLayout):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.orientation = "vertical"
        self.padding = 12
        self.spacing = 10
        self.add_widget(BoxLayout())

        self.add_widget(
            MDLabel(
                text="Add Expense",
                halign="center",
                font_style="H5",
                size_hint_y=None,
                height=50,
            )
        )
        card = MDCard(
            orientation="vertical",
            padding=(18, 26, 18, 18),
            spacing=14,
            size_hint=(1, None),
            radius=[24],
        )
        card.height = 400

        self.date_time_input = MDTextField(
            hint_text="Date & Time (tap to pick)", readonly=True
        )
        self.date_time_input.bind(on_touch_down=self.date_time_touch)
        self.selected_date = None
        self.selected_date_time = None

        self.item_input = MDTextField(hint_text="Item (e.g. Tea)")
        self.amount_input = MDTextField(
            hint_text="Amount (e.g. 120.50)", input_filter="float"
        )
        self.note_input = MDTextField(hint_text="Note (optional)")

        self.status_label = MDLabel(
            text="", halign="center", size_hint_y=None, height=24
        )

        self.save_button = MDRaisedButton(text="SAVE", size_hint_x=1, height=48)
        self.save_button.bind(on_press=self.on_save)

        self.date_time_input.mode = "rectangle"
        self.item_input.mode = "rectangle"
        self.amount_input.mode = "rectangle"
        self.note_input.mode = "rectangle"

        card.add_widget(self.date_time_input)
        card.add_widget(self.item_input)
        card.add_widget(self.amount_input)
        card.add_widget(self.note_input)
        card.add_widget(self.status_label)
        card.add_widget(self.save_button)

        self.add_widget(card)
        self.add_widget(BoxLayout())

    def on_save(self, instance):

        if self.selected_date_time is None:
            self.status_label.text = "Pick date & time"
            return

        date_time = int(self.selected_date_time.timestamp() * 1000)
        item = self.item_input.text.strip()
        amount_text = self.amount_input.text.strip()
        note = self.note_input.text.strip()

        if not item:
            self.status_label.text = "Item required"
            return

        amount = rupees_to_paise(amount_text)
        self.db.add_transaction(date_time, item, amount, note)

        self.status_label.text = "Saved ✅🤯🔥🔥"
        app = App.get_running_app()
        if app and hasattr(app, "refresh_history"):
            app.refresh_history()

        print("Date: ", date_time)
        print("ITEM: ", item)
        print("AMOUNT: ", amount)
        print("NOTE: ", note)

        self.item_input.text = ""
        self.amount_input.text = ""
        self.note_input.text = ""
        self.date_time_input.text = ""
        self.selected_date = None
        self.selected_date_time = None

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

        self.selected_date_time = date_time
        self.date_time_input.text = date_time.strftime("%Y-%m-%d • %H:%M")

    def on_picker_cancel(self, instance, value):
        pass
