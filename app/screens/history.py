from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFlatButton
from app.utils import paise_to_rupees


class HistoryScreen(BoxLayout):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.orientation = "vertical"
        self.padding = 12
        self.spacing = 10
        self.last_deleted_id = None

        self.add_widget(
            MDLabel(
                text="History",
                halign="center",
                font_style="H5",
                size_hint_y=None,
                height=50,
            )
        )

        self.scroll = ScrollView()
        self.list_box = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        self.scroll.add_widget(self.list_box)
        self.add_widget(self.scroll)

        self.undo_bar = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=56,
            padding=12,
            spacing=12,
        )
        self.undo_label = MDLabel(text="", valign="middle")
        self.undo_button = MDFlatButton(text="UNDO")
        self.undo_button.bind(on_press=self.undo_last_delete)
        self.undo_bar.add_widget(self.undo_label)
        self.undo_bar.add_widget(self.undo_button)
        self.undo_bar.opacity = 0
        self.add_widget(self.undo_bar)

    def refresh(self):
        self.list_box.clear_widgets()
        transactions = self.db.list_txns()

        if not transactions:
            self.list_box.add_widget(
                MDLabel(
                    text="(no transactions yet)",
                    halign="center",
                    size_hint_y=None,
                    height=40,
                )
            )
            return

        for t in transactions:
            amount = paise_to_rupees(t["amount"])
            note = t["note"] if t["note"] else ""

            card = MDCard(
                orientation="horizontal",
                size_hint_y=None,
                height=76,
                padding=12,
                spacing=12,
            )

            left = BoxLayout(orientation="vertical")

            left.add_widget(MDLabel(text=t["item"], font_style="Subtitle1"))
            left.add_widget(MDLabel(text=note, font_style="Caption"))

            right = BoxLayout(
                orientation="horizontal", size_hint_x=None, width=150, spacing=6
            )
            right.add_widget(
                MDLabel(text=f"₹{amount}", halign="right", font_style="H6")
            )

            delete_button = MDIconButton(icon="trash-can-outline")
            delete_button.bind(
                on_press=lambda button, txid=t["id"]: self.delete_transaction(txid)
            )
            right.add_widget(delete_button)

            card.add_widget(left)
            card.add_widget(right)

            self.list_box.add_widget(card)

    def delete_transaction(self, txn_id):
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
