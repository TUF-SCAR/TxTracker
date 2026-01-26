from datetime import date, timedelta
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFlatButton
from app.utils import (
    paise_to_rupees,
    time_24_to_12,
    str_to_date,
    start_of_week_sun,
    start_of_month,
)


class HistoryScreen(BoxLayout):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)

        self.db = db
        self.orientation = "vertical"
        self.padding = 12
        self.spacing = 10
        self.last_deleted_id = None

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
        self.undo_label.font_name = "Inter_24pt-Bold"
        self.undo_button = MDFlatButton(text="UNDO")
        self.undo_button.font_name = "Inter_24pt-Black"
        self.undo_button.font_size = "16sp"
        self.undo_button.bind(on_press=self.undo_last_delete)

        self.undo_bar.add_widget(self.undo_label)
        self.undo_bar.add_widget(self.undo_button)

        self.delete_button = MDFlatButton(text="PERMANENT DELETE")
        self.delete_button.font_name = "Inter_24pt-Black"
        self.delete_button.font_size = "16sp"
        self.delete_button.bind(on_press=self.delete_last_permanently)

        self.undo_bar.add_widget(self.delete_button)
        self.undo_bar.opacity = 0

        self.add_widget(self.undo_bar)

    def _add_section_header(self, text: str):
        section_header = MDLabel(
            text=text,
            halign="left",
            font_style="Subtitle1",
            size_hint_y=None,
            height=24,
            padding=(0, dp(20), 0, 0),
        )
        section_header.font_name = "design.graffiti.comicsansmsgras"
        section_header.font_size = "18sp"
        self.list_box.add_widget(section_header)

    def _add_group_header(self, text: str):
        group_header = MDLabel(
            text=text,
            halign="left",
            font_style="Caption",
            theme_text_color="Hint",
            size_hint_y=None,
            height=26,
        )
        group_header.font_name = "design.graffiti.comicsansmsgras"
        self.list_box.add_widget(group_header)

    def _add_tx_card(self, t: dict):
        amount = paise_to_rupees(t["amount"])
        note = t["note"] if t["note"] else ""

        date_str = t["date"]
        time_str = t["time"]
        time_12 = time_24_to_12(time_str)

        card = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=96,
            padding=12,
            spacing=12,
        )

        item_field = MDLabel(
            text=t["item"], font_style="Subtitle1", padding=(dp(5), 0, 0, 0)
        )

        note_field = MDLabel(
            text=note, font_style="Caption", padding=(dp(5), dp(5), 0, 0)
        )

        date_time_field = MDLabel(
            text=f"{date_str} • {time_12}",
            font_style="Caption",
            theme_text_color="Hint",
        )

        item_field.font_name = "Nunito-ExtraBold"
        note_field.font_name = "Nunito-ExtraBold"
        date_time_field.font_name = "Nunito-Black"

        item_field.font_size = "26sp"
        note_field.font_size = "16sp"
        date_time_field.font_size = "10sp"

        left = BoxLayout(orientation="vertical")
        left.add_widget(item_field)
        left.add_widget(note_field)
        left.add_widget(date_time_field)

        right = BoxLayout(
            orientation="horizontal", size_hint_x=None, width=200, spacing=6
        )
        amount_field = MDLabel(text=f"₹{amount}", halign="right", font_style="H6")
        amount_field.font_name = "Roboto-Bold"
        amount_field.font_size = "24sp"

        right.add_widget(amount_field)

        delete_button = MDIconButton(icon="trash-can-outline")
        delete_button.padding = (0, 0, 0, dp(26))
        delete_button.bind(
            on_press=lambda button, txid=t["id"]: self.delete_transaction(txid)
        )

        right.add_widget(delete_button)

        card.add_widget(left)
        card.add_widget(right)

        self.list_box.add_widget(card)

    def refresh(self):
        self.list_box.clear_widgets()
        transactions = self.db.list_txns()

        if not transactions:
            spacer = MDCard(
                size_hint_y=None,
                height=dp(300),
                md_bg_color=(0, 0, 0, 0),
            )

            no_transaction_bg = MDCard(
                size_hint_y=None,
                height=dp(48),
                radius=[18],
                md_bg_color=(0.05, 0.06, 0.07, 0.85),
                padding=(0, 0, 0, 0),
                elevation=0,
            )

            no_transaction = MDLabel(
                text="No Transactions Yet!!",
                halign="center",
                size_hint_y=None,
                height=40,
                padding=(0, 0, 0, dp(110)),
            )
            no_transaction.font_name = "PermanentMarker-Regular"
            no_transaction.font_size = "26sp"

            self.list_box.add_widget(spacer)
            self.list_box.add_widget(no_transaction_bg)
            self.list_box.add_widget(no_transaction)
            return

        today = date.today()
        yesterday = today - timedelta(days=1)

        week_start = start_of_week_sun(today)
        week_end = week_start + timedelta(days=7)

        month_start = start_of_month(today)
        if month_start.month == 12:
            month_end = date(month_start.year + 1, 1, 1)
        else:
            month_end = date(month_start.year, month_start.month + 1, 1)

        week_groups = {}
        month_groups = {}
        older_groups = {}

        for t in transactions:
            d = str_to_date(t["date"])

            if week_start <= d < week_end:
                if d == today:
                    k = "Today"
                elif d == yesterday:
                    k = "Yesterday"
                else:
                    k = t["date"]
                week_groups.setdefault(k, []).append(t)

            elif month_start <= d < month_end:
                month_groups.setdefault(d, []).append(t)

            else:
                older_groups.setdefault(d, []).append(t)

        if week_groups:
            self._add_section_header("This Week")

            if "Today" in week_groups:
                self._add_group_header("Today")
                for t in week_groups["Today"]:
                    self._add_tx_card(t)

            if "Yesterday" in week_groups:
                self._add_group_header("Yesterday")
                for t in week_groups["Yesterday"]:
                    self._add_tx_card(t)

            other_dates = []
            for k in week_groups.keys():
                if k not in ("Today", "Yesterday"):
                    other_dates.append(k)

            other_dates.sort(reverse=True)

            for date_str in other_dates:
                self._add_group_header(date_str)
                for t in week_groups[date_str]:
                    self._add_tx_card(t)

        if month_groups:
            self._add_section_header("This Month")
            for d in sorted(month_groups.keys(), reverse=True):
                self._add_group_header(d.strftime("%Y-%m-%d"))
                for t in month_groups[d]:
                    self._add_tx_card(t)

        if older_groups:
            self._add_section_header("Older")
            for d in sorted(older_groups.keys(), reverse=True):
                self._add_group_header(d.strftime("%Y-%m-%d"))
                for t in older_groups[d]:
                    self._add_tx_card(t)

    def delete_transaction(self, txn_id):
        self.db.soft_delete(txn_id)
        self.last_deleted_id = txn_id
        self.undo_label.text = f"Deleted #{txn_id}"
        self.undo_bar.opacity = 1

        self.refresh()

        app = App.get_running_app()
        if app and hasattr(app, "refresh_reports"):
            app.refresh_reports()

    def undo_last_delete(self, instance):
        if self.last_deleted_id is None:
            return

        self.db.undo_delete(self.last_deleted_id)
        self.undo_bar.opacity = 0
        self.last_deleted_id = None

        self.refresh()

        app = App.get_running_app()
        if app and hasattr(app, "refresh_reports"):
            app.refresh_reports()

    def delete_last_permanently(self, instance):
        if self.last_deleted_id is None:
            return

        self.db.hard_delete(self.last_deleted_id)
        self.undo_bar.opacity = 0
        self.last_deleted_id = None

        self.refresh()

        app = App.get_running_app()
        if app and hasattr(app, "refresh_reports"):
            app.refresh_reports()
