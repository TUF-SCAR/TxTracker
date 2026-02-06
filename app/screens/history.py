# A screen for viewing transaction history, with sections for "This Week", "This Month" and "Older".
# Each transaction shows item name, note, date/time and amount. Transactions can be deleted with an undo option.

from datetime import date, timedelta
from functools import partial
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.stencilview import StencilView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from app.services.drive_sync import DriveSyncService
from app.utils import (
    paise_to_rupees,
    time_24_to_12,
    str_to_date,
    start_of_week_sun,
    start_of_month,
)


class HistoryRow(RecycleDataViewBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(24)
        self.spacing = 0
        self.padding = (0, 0, 0, 0)

        self.header = MDLabel(
            halign="left",
            valign="middle",
            font_style="H6",
            size_hint_y=None,
            height=dp(26),
            padding=(0, 0, 0, 0),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
        )
        self.header.font_name = "Nunito-ExtraBold"
        self.header.font_size = "18sp"

        self.subheader = MDLabel(
            halign="left",
            valign="middle",
            font_style="Caption",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(16),
        )
        self.subheader.font_name = "Nunito-SemiBold"
        self.subheader.font_size = "14sp"

        self.card = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            radius=[dp(18)],
            height=dp(96),
            padding=(dp(14), dp(12), dp(14), dp(12)),
            spacing=dp(12),
            md_bg_color=(0.05, 0.06, 0.07, 0.80),
            elevation=0,
        )

        self.item_field = MDLabel(
            font_style="Subtitle1",
            padding=(dp(5), 0, 0, 0),
            size_hint_y=None,
            height=dp(34),
            valign="top",
        )
        self.item_field.shorten = True
        self.item_field.shorten_from = "right"
        self.note_field = MDLabel(
            font_style="Caption",
            padding=(0, dp(2), 0, 0),
            size_hint_y=None,
            height=dp(22),
            valign="top",
        )
        self.note_field.shorten = True
        self.note_field.shorten_from = "right"
        self.date_time_field = MDLabel(
            font_style="Caption",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(14),
        )

        self.item_field.font_name = "Nunito-ExtraBold"
        self.note_field.font_name = "Nunito-ExtraBold"
        self.date_time_field.font_name = "Nunito-Black"

        self.item_field.font_size = "24sp"
        self.note_field.font_size = "14sp"
        self.date_time_field.font_size = "8sp"

        left = BoxLayout(orientation="vertical", size_hint_x=1)
        left.add_widget(self.item_field)
        left.add_widget(self.note_field)
        left.add_widget(self.date_time_field)
        self._left_box = left

        right = BoxLayout(
            orientation="horizontal", size_hint_x=None, width=dp(170), spacing=dp(6)
        )
        self.amount_field = MDLabel(halign="right", font_style="H6")
        self.amount_field.font_name = "Roboto-Bold"
        self.amount_field.font_size = "20sp"
        self.amount_field.text_size = (dp(170), None)
        self.amount_field.shorten = True
        self.amount_field.shorten_from = "right"
        right.add_widget(self.amount_field)

        self.delete_button = MDIconButton(icon="trash-can-outline")
        self.delete_button.padding = (0, 0, 0, dp(26))
        right.add_widget(self.delete_button)

        self.card.add_widget(left)
        self.card.add_widget(right)

        def _sync_text_width(*_):
            w = max(0, left.width - dp(4))
            self.item_field.text_size = (w, None)
            self.note_field.text_size = (w, self.note_field.height)
            self.date_time_field.text_size = (w, None)

        self._sync_text_width = _sync_text_width

        left.bind(width=_sync_text_width)
        _sync_text_width()

        self.add_widget(self.header)
        self.add_widget(self.subheader)
        self.add_widget(self.card)

        self._delete_cb = None
        self._note_cb = None
        self._note_text = ""
        self._item_text = ""

    def refresh_view_attrs(self, rv, index, data):
        kind = data.get("kind")
        self.size_hint_y = None
        if kind == "section":
            self.header.text = data.get("text", "")
            self.header.opacity = 1
            self.header.height = data.get("height", dp(26))
            self.subheader.opacity = 0
            self.subheader.height = 0
            self.subheader.text = ""
            self.card.opacity = 0
            self.card.height = 0
            self.height = data.get("height", dp(26))
        elif kind == "group":
            self.subheader.text = data.get("text", "")
            self.subheader.opacity = 1
            self.subheader.height = data.get("height", dp(16))
            self.header.opacity = 0
            self.header.height = 0
            self.header.text = ""
            self.card.opacity = 0
            self.card.height = 0
            self.height = data.get("height", dp(16))
        else:
            self.item_field.text = data.get("item", "")
            self._item_text = data.get("item", "")
            self.note_field.text = data.get("note", "")
            self._note_text = data.get("note", "")
            self.date_time_field.text = data.get("date_time", "")
            self.amount_field.text = data.get("amount", "")
            self.card.opacity = 1
            self.card.height = dp(96)
            self.header.opacity = 0
            self.header.height = 0
            self.header.text = ""
            self.subheader.opacity = 0
            self.subheader.height = 0
            self.subheader.text = ""
            self.note_field.height = dp(22)
            self.note_field.shorten = True
            self._sync_text_width()
            self.height = data.get("height", dp(96))

            if self._delete_cb:
                self.delete_button.unbind(on_press=self._delete_cb)
            screen = data.get("screen")
            txid = data.get("txid")
            if screen and txid is not None:
                self._delete_cb = lambda *_: screen.delete_transaction(txid)
                self.delete_button.bind(on_press=self._delete_cb)
                self._note_cb = lambda *_: screen.show_note(
                    self._item_text, self._note_text
                )

        return super().refresh_view_attrs(rv, index, data)

    def on_touch_up(self, touch):
        if self.card.opacity and self.card.collide_point(*touch.pos):
            if self.delete_button.collide_point(*touch.pos):
                return super().on_touch_up(touch)
            if self._left_box.collide_point(*touch.pos) and getattr(
                self, "_note_cb", None
            ):
                self._note_cb()
                return True
        return super().on_touch_up(touch)


class HistoryScreen(BoxLayout):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)

        self.db = db
        self.orientation = "vertical"
        self.padding = dp(12)
        self.spacing = dp(10)
        self.last_deleted_id = None
        self.drive_sync = DriveSyncService()
        self.drive_sync.set_status_callback(self._set_drive_status)
        self._note_dialog = None

        self.drive_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(36),
            spacing=dp(8),
        )
        self.drive_status = MDLabel(
            text="Drive sync: not linked",
            halign="left",
            theme_text_color="Hint",
        )
        self.drive_status.font_name = "Nunito-SemiBold"
        self.drive_status.font_size = "12sp"

        self._set_drive_status(
            "Drive linked" if self.drive_sync.uri else "Drive sync: not linked"
        )

        self.drive_link_btn = MDFlatButton(text="LINK DRIVE")
        self.drive_link_btn.font_name = "Inter_24pt-Black"
        self.drive_link_btn.font_size = "12sp"
        self.drive_link_btn.bind(on_press=lambda *_: self.drive_sync.link_drive())

        self.drive_sync_btn = MDFlatButton(text="SYNC NOW")
        self.drive_sync_btn.font_name = "Inter_24pt-Black"
        self.drive_sync_btn.font_size = "12sp"
        self.drive_sync_btn.bind(on_press=lambda *_: self.drive_sync.sync_db(self.db))

        self.drive_bar.add_widget(self.drive_status)
        self.drive_bar.add_widget(self.drive_link_btn)
        self.drive_bar.add_widget(self.drive_sync_btn)

        self.add_widget(self.drive_bar)

        rv_wrap = StencilView(size_hint=(1, 1))
        self.rv = RecycleView(size_hint=(None, None))
        rv_wrap.add_widget(self.rv)
        self.add_widget(rv_wrap)
        rv_wrap.bind(pos=self._sync_rv_clip, size=self._sync_rv_clip)
        self.rv_layout = RecycleBoxLayout(
            default_size=(None, dp(1)),
            default_size_hint=(1, None),
            size_hint=(1, None),
            orientation="vertical",
            spacing=dp(6),
        )
        self.rv_layout.size_hint_x = 1
        self.rv_layout.bind(minimum_height=self._update_rv_layout)
        self.rv.layout_manager = self.rv_layout
        self.rv.add_widget(self.rv_layout)
        self.rv.viewclass = HistoryRow

        self.undo_bar = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            padding=dp(12),
            spacing=dp(12),
        )
        self.undo_label = MDLabel(text="", valign="middle")
        self.undo_label.font_name = "Inter_24pt-Bold"
        self.undo_label.font_size = "12sp"
        self.undo_button = MDFlatButton(text="UNDO")
        self.undo_button.font_name = "Inter_24pt-Black"
        self.undo_button.font_size = "10sp"
        self.undo_button.bind(on_press=self.undo_last_delete)

        self.undo_bar.add_widget(self.undo_label)
        self.undo_bar.add_widget(self.undo_button)

        self.delete_button = MDFlatButton(text="PERMANENT DELETE")
        self.delete_button.font_name = "Inter_24pt-Black"
        self.delete_button.font_size = "10sp"
        self.delete_button.bind(on_press=self.delete_last_permanently)

        self.undo_bar.add_widget(self.delete_button)
        self.undo_bar.opacity = 0

        self.add_widget(self.undo_bar)

    def _set_drive_status(self, msg: str):
        self.drive_status.text = msg

    def _update_rv_layout(self, *args):
        self.rv_layout.height = self.rv_layout.minimum_height

    def _sync_rv_clip(self, *args):
        if self.rv:
            self.rv.pos = args[0].pos
            self.rv.size = args[0].size

    def _build_tx_data(self, t: dict):
        amount = paise_to_rupees(t["amount"])
        note = t["note"] if t["note"] else ""
        date_str = t["date"]
        time_str = t["time"]
        time_12 = time_24_to_12(time_str)
        return {
            "kind": "tx",
            "item": t["item"],
            "note": note,
            "date_time": f"{date_str} • {time_12}",
            "amount": f"₹{amount}",
            "txid": t["id"],
            "screen": self,
            "height": dp(96),
            "size_hint_y": None,
        }

    def refresh(self):
        self.rv.data = []
        transactions = self.db.list_txns()

        if not transactions:
            self.rv.data = [
                {
                    "kind": "section",
                    "text": "No Transactions Yet!!",
                    "height": dp(26),
                    "size_hint_y": None,
                }
            ]
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

        data = []
        if week_groups:
            data.append(
                {
                    "kind": "section",
                    "text": "This Week",
                    "height": dp(26),
                    "size_hint_y": None,
                }
            )

            if "Today" in week_groups:
                data.append(
                    {
                        "kind": "group",
                        "text": "Today",
                        "height": dp(16),
                        "size_hint_y": None,
                    }
                )
                for t in week_groups["Today"]:
                    data.append(self._build_tx_data(t))

            if "Yesterday" in week_groups:
                data.append(
                    {
                        "kind": "group",
                        "text": "Yesterday",
                        "height": dp(16),
                        "size_hint_y": None,
                    }
                )
                for t in week_groups["Yesterday"]:
                    data.append(self._build_tx_data(t))

            other_dates = []
            for k in week_groups.keys():
                if k not in ("Today", "Yesterday"):
                    other_dates.append(k)

            other_dates.sort(reverse=True)

            for date_str in other_dates:
                data.append(
                    {
                        "kind": "group",
                        "text": date_str,
                        "height": dp(16),
                        "size_hint_y": None,
                    }
                )
                for t in week_groups[date_str]:
                    data.append(self._build_tx_data(t))

        if month_groups:
            data.append(
                {
                    "kind": "section",
                    "text": "This Month",
                    "height": dp(26),
                    "size_hint_y": None,
                }
            )
            for d in sorted(month_groups.keys(), reverse=True):
                data.append(
                    {
                        "kind": "group",
                        "text": d.strftime("%Y-%m-%d"),
                        "height": dp(16),
                        "size_hint_y": None,
                    }
                )
                for t in month_groups[d]:
                    data.append(self._build_tx_data(t))

        if older_groups:
            data.append(
                {
                    "kind": "section",
                    "text": "Older",
                    "height": dp(26),
                    "size_hint_y": None,
                }
            )
            for d in sorted(older_groups.keys(), reverse=True):
                data.append(
                    {
                        "kind": "group",
                        "text": d.strftime("%Y-%m-%d"),
                        "height": dp(16),
                        "size_hint_y": None,
                    }
                )
                for t in older_groups[d]:
                    data.append(self._build_tx_data(t))

        self.rv.data = data
        self.rv.refresh_from_data()

    def show_note(self, item_text: str, note_text: str):
        item = (item_text or "").strip()
        note = (note_text or "").strip()
        if not item and not note:
            return
        parts = []
        if item:
            parts.append(f"Item: {item}")
        if note:
            parts.append(f"Note: {note}")
        text = "\n\n".join(parts)
        if self._note_dialog:
            self._note_dialog.dismiss()
        close_btn = MDFlatButton(
            text="CLOSE",
            font_name="Inter_24pt-Black",
            font_size="12sp",
        )
        self._note_dialog = MDDialog(
            title="Details",
            text=text,
            radius=[(dp(24)), dp(24), dp(24), dp(24)],
            md_bg_color=(0.08, 0.09, 0.11, 0.98),
            buttons=[close_btn],
        )
        close_btn.bind(on_release=lambda *_: self._note_dialog.dismiss())
        self._note_dialog.open()

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
