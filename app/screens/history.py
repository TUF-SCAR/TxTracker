from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from app.utils import paise_to_rupees


class HistoryScreen(BoxLayout):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.orientation = "vertical"
        self.padding = 12
        self.spacing = 10

        self.add_widget(Label(text="History", size_hint_y=None, height=40))

        self.scroll = ScrollView()
        self.list_box = GridLayout(cols=1, spacing=8, size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        self.scroll.add_widget(self.list_box)
        self.add_widget(self.scroll)

    def refresh(self):
        self.list_box.clear_widgets()
        txns = self.db.list_txns()

        if not txns:
            self.list_box.add_widget(
                Label(text="(no transactions yet)", size_hint_y=None, height=30)
            )
            return

        for t in txns:
            amount = paise_to_rupees(t["amount"])
            text = f'#{t["id"]} {t["item"]} ₹{amount} note="{t["note"]}"'
            self.list_box.add_widget(Label(text=text, size_hint_y=None, height=30))
