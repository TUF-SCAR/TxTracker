from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
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
        self.last_deleted_id = None

        self.add_widget(Label(text="History", size_hint_y=None, height=40))

        self.scroll = ScrollView()
        self.list_box = GridLayout(cols=1, spacing=8, size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        self.scroll.add_widget(self.list_box)
        self.add_widget(self.scroll)

        self.undo_bar = BoxLayout(size_hint_y=None, height=50, spacing=8)
        self.undo_label = Label(text="")
        self.undo_button = Button(text="UNDO", size_hint_x=None, width=100)
        self.undo_button.bind(on_press=self.undo_last_delete)
        self.undo_bar.add_widget(self.undo_label)
        self.undo_bar.add_widget(self.undo_button)
        self.undo_bar.opacity = 0
        self.add_widget(self.undo_bar)

    def refresh(self):
        self.list_box.clear_widgets()
        txns = self.db.list_txns()

        if not txns:
            self.list_box.add_widget(
                Label(text="(no transactions yet)", size_hint_y=None, height=30)
            )
            return

        for t in txns:
            row = BoxLayout(size_hint_y=None, height=40, spacing=8)
            amount = paise_to_rupees(t["amount"])
            note = t["note"] if t["note"] else ""
            text = f'#{t["id"]} {t["item"]} - ₹{amount}/- note : "{note}"'
            row.add_widget(Label(text=text))
            delete_button = Button(text="Delete", size_hint_x=None, width=90)
            delete_button.bind(
                on_press=lambda button, txid=t["id"]: self.delete_txn(txid)
            )
            row.add_widget(delete_button)
            self.list_box.add_widget(row)

    def delete_txn(self, txn_id):
        self.db.soft_delete(txn_id)
        self.last_deleted_id = txn_id
        self.undo_label.text = f"Deleted #{txn_id}"
        self.undo_bar.opacity = 1
        self.refresh()

    def undo_last_delete(self, instance):
        if self.last_deleted_id is None:
            return
        self.db.undo_delete(self.last_deleted_id)
        self.undo_bar.opacity = 0
        self.last_deleted_id = None
        self.refresh()
