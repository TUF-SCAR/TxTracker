import time
from datetime import datetime
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.app import App
from app.utils import rupees_to_paise


class AddScreen(BoxLayout):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.orientation = "vertical"
        self.padding = 12
        self.spacing = 10
        self.selected_date = None
        self.selected_date_time = None

        self.add_widget(Label(text="Add Expence", size_hint_y=None, height=40))

        self.date_time_input = TextInput(
            hint_text="Date & Time (you type)", multiline=False
        )
        self.date_time_input.readonly = True
        self.date_time_input.bind(on_touch_down=self.date_time_touch)
        self.add_widget(self.date_time_input)

        self.item_input = TextInput(hint_text="Item (e.g. Tea)", multiline=False)
        self.add_widget(self.item_input)

        self.amount_input = TextInput(hint_text="Amount (e.g. 120.50)", multiline=False)
        self.add_widget(self.amount_input)

        self.note_input = TextInput(hint_text="Note (optional)", multiline=False)
        self.add_widget(self.note_input)

        self.status_label = Label(text="", size_hint_y=None, height=30)
        self.add_widget(self.status_label)

        self.save_button = Button(text="SAVE", size_hint_y=None, height=50)
        self.save_button.bind(on_press=self.on_save)
        self.add_widget(self.save_button)

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
        self.date_time_input.text = date_time.strftime("%Y-%m-%d %H:%M")

    def on_picker_cancel(self, instance, value):
        pass
