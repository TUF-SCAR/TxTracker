import time
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

        self.add_widget(Label(text="Add Expence", size_hint_y=None, height=40))

        self.date_time_input = TextInput(
            hint_text="Date & Time (you type)", multiline=False
        )
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
        date_time = int(time.time() * 1000)
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
