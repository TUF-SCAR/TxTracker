from datetime import datetime
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from app.utils import *


class ReportScreen(BoxLayout):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.orientation = "vertical"
        self.padding = 16
        self.spacing = 12
        self.add_widget(BoxLayout())

        self.add_widget(
            MDLabel(
                text="Reports",
                halign="center",
                font_style="H5",
                size_hint_y=None,
                height=50,
            )
        )

        self.card_week = self.make_card("This Week", "₹0")
        self.card_month = self.make_card("This Month", "₹0")
        self.card_year = self.make_card("This Year", "₹0")

        self.add_widget(self.card_week)
        self.add_widget(self.card_month)
        self.add_widget(self.card_year)
        self.add_widget(BoxLayout())

    def make_card(self, title, value):
        card = MDCard(
            orientation="vertical",
            padding=(18, 18, 18, 18),
            spacing=6,
            size_hint=(1, None),
            height=110,
            radius=[24],
        )
        title_lbl = MDLabel(text=title, font_style="Subtitle1")
        value_lbl = MDLabel(text=value, font_style="H4")

        card.add_widget(title_lbl)
        card.add_widget(value_lbl)

        card._value_lbl = value_lbl
        return card

    def refresh(self):
        now = datetime.now()
        now_ms = date_time_to_ms(now)

        week_start = date_time_to_ms(start_of_week(now))
        month_start = date_time_to_ms(start_of_month(now))
        year_start = date_time_to_ms(start_of_year(now))

        week_total = self.db.sum_between(week_start, now_ms)
        month_total = self.db.sum_between(month_start, now_ms)
        year_total = self.db.sum_between(year_start, now_ms)

        self.card_week._value_lbl.text = f"₹{paise_to_rupees(-week_total)}"
        self.card_month._value_lbl.text = f"₹{paise_to_rupees(-month_total)}"
        self.card_year._value_lbl.text = f"₹{paise_to_rupees(-year_total)}"
