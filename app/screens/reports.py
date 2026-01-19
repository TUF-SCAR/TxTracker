from datetime import date, timedelta
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from app.utils import (
    date_to_str,
    start_of_week_sun,
    start_of_month,
    start_of_year,
    paise_to_rupees,
)


class ReportScreen(BoxLayout):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.orientation = "vertical"
        self.padding = 16
        self.spacing = 12
        self.add_widget(BoxLayout())

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
        today = date.today()

        week_start = start_of_week_sun(today)
        month_start = start_of_month(today)
        year_start = start_of_year(today)

        end_exclusive = date_to_str(today + timedelta(days=1))

        week_total = self.db.sum_between_dates(date_to_str(week_start), end_exclusive)
        month_total = self.db.sum_between_dates(date_to_str(month_start), end_exclusive)
        year_total = self.db.sum_between_dates(date_to_str(year_start), end_exclusive)

        self.card_week._value_lbl.text = f"₹{paise_to_rupees(week_total)}"
        self.card_month._value_lbl.text = f"₹{paise_to_rupees(month_total)}"
        self.card_year._value_lbl.text = f"₹{paise_to_rupees(year_total)}"
