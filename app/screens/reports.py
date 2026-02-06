# A screen for viewing transaction reports, with sections for "This Week", "This Month" and "This Year".
# Each section shows the total amount spent and a line chart of daily/monthly totals.
# Tapping a section expands/collapses the chart with animation.

import calendar
from datetime import date, timedelta
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from app.widgets.line_chart import LineChart
from app.utils import (
    date_to_str,
    start_of_week_sun,
    start_of_month,
    start_of_year,
    paise_to_rupees,
)


class ReportCard(MDCard):
    _orig_bg = ListProperty([0.08, 0.09, 0.11, 0.92])
    _sel_bg = ListProperty([0.914, 0.094, 0.153, 1.0])
    _press_bg = ListProperty([0.95, 0.18, 0.22, 1.0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = self._orig_bg[:]
        self._is_open = False
        self._orig_elev = float(self.elevation or 0)
        self._sel_elev = max(6, self._orig_elev + 6)
        self.shadow_softness = dp(16)
        self.shadow_offset = (0, -dp(2))
        try:
            self.shadow_color = (0, 0, 0, 1)
        except Exception:
            pass

    def set_opened(self, is_open: bool):
        self._is_open = is_open
        target = self._sel_bg if is_open else self._orig_bg
        Animation.cancel_all(self)
        Animation(
            md_bg_color=target,
            elevation=self._sel_elev if is_open else self._orig_elev,
            d=0.12,
            t="out_quad",
        ).start(self)

    def on_touch_down(self, touch):
        if self.disabled:
            return super().on_touch_down(touch)
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self._touch_down = True
            Animation.cancel_all(self)
            Animation(md_bg_color=self._press_bg, d=0.08, t="out_quad").start(self)
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            target = self._sel_bg if self._is_open else self._orig_bg
            Animation.cancel_all(self)
            Animation(md_bg_color=target, d=0.12, t="out_quad").start(self)
            if self.collide_point(*touch.pos) and getattr(self, "_touch_down", False):
                self._touch_down = False
                self.dispatch("on_release")
                return True
        return super().on_touch_up(touch)


class ReportScreen(BoxLayout):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)

        self.db = db
        self.orientation = "vertical"
        self.padding = (dp(16), dp(12), dp(16), dp(12))
        self.spacing = dp(8)

        self._week_vals = []
        self._month_vals = []
        self._year_vals = []
        self._week_labels = []
        self._month_labels = []
        self._year_labels = []

        from kivy.uix.scrollview import ScrollView

        scroll = ScrollView(do_scroll_x=False)

        cards_col = BoxLayout(
            orientation="vertical", size_hint=(1, None), spacing=dp(12)
        )
        cards_col.bind(minimum_height=cards_col.setter("height"))
        scroll.bind(width=lambda *a: setattr(cards_col, "width", scroll.width))

        self.card_week = self.make_card("This Week", "₹0", "week")
        self.card_month = self.make_card("This Month", "₹0", "month")
        self.card_year = self.make_card("This Year", "₹0", "year")

        self.week_chart = LineChart(size_hint=(1, None), height=0)
        self.month_chart = LineChart(size_hint=(1, None), height=0)
        self.year_chart = LineChart(size_hint=(1, None), height=0)

        for c in (self.week_chart, self.month_chart, self.year_chart):
            c.opacity = 0
            c.disabled = True
            c.size_hint_y = None
            c.set_colors(self.card_week._sel_bg, self.card_week._sel_bg)

        cards_col.add_widget(self.card_week)
        cards_col.add_widget(self.week_chart)
        cards_col.add_widget(self.card_month)
        cards_col.add_widget(self.month_chart)
        cards_col.add_widget(self.card_year)
        cards_col.add_widget(self.year_chart)

        scroll.add_widget(cards_col)
        self.add_widget(scroll)

        self._selected = None
        self.cards_col = cards_col

        def _sync(*args):
            self.cards_col.height = self.cards_col.minimum_height
            self.cards_col.do_layout()

        for chart in (self.week_chart, self.month_chart, self.year_chart):
            chart.bind(height=_sync, opacity=_sync)

    def make_card(self, title, value, key):
        card = ReportCard(
            orientation="vertical",
            padding=(dp(36), dp(18), dp(18), dp(16)),
            spacing=dp(6),
            size_hint_y=None,
            height=dp(100),
            radius=[dp(22)],
            elevation=0,
        )
        card.register_event_type("on_release")

        title_lbl = MDLabel(text=title, font_style="Subtitle1")
        value_lbl = MDLabel(text=value, font_style="H4")

        title_lbl.font_name = "Nunito-ExtraBold"
        title_lbl.font_size = "28sp"
        value_lbl.font_name = "Roboto-Bold"

        for lbl in (title_lbl, value_lbl):
            lbl.halign = "left"
            lbl.text_size = (0, None)

        def _sync_labels(*args):
            w = max(0, card.width - card.padding[0] - card.padding[2])
            title_lbl.text_size = (w, None)
            value_lbl.text_size = (w, None)

        card.bind(size=_sync_labels)
        _sync_labels()

        card.add_widget(title_lbl)
        card.add_widget(value_lbl)

        card._value_lbl = value_lbl
        card._key = key
        card.bind(on_release=lambda *a: self.select_chart(key))
        return card

    def select_chart(self, key):
        if not (self._week_vals or self._month_vals or self._year_vals):
            try:
                self.refresh()
            except Exception:
                pass

        if self._selected == key:
            self._selected = None
        else:
            self._selected = key

        mapping = {
            "week": (self.week_chart, self._week_vals, self._week_labels),
            "month": (self.month_chart, self._month_vals, self._month_labels),
            "year": (self.year_chart, self._year_vals, self._year_labels),
        }

        for k, (chart, vals, labels) in mapping.items():
            if k == self._selected:
                chart.disabled = False
                chart.opacity = 1
                chart.height = dp(210)
                Animation.cancel_all(chart)
                Animation(height=dp(210), d=1, t="out_expo").start(chart)
                if not labels:
                    if k == "week":
                        labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
                    elif k == "month":
                        today = date.today()
                        days_in_month = calendar.monthrange(today.year, today.month)[1]
                        labels = [str(i) for i in range(1, days_in_month + 1)]
                    else:
                        labels = [
                            "Jan",
                            "Feb",
                            "Mar",
                            "Apr",
                            "May",
                            "Jun",
                            "Jul",
                            "Aug",
                            "Sep",
                            "Oct",
                            "Nov",
                            "Dec",
                        ]
                values = vals if vals else [0] * len(labels)
                chart.set_data(values, labels)
            else:
                Animation.cancel_all(chart)
                fade = Animation(opacity=0, d=0.1, t="out_cubic")
                collapse = Animation(height=0, d=0.5, t="out_cubic")
                (fade & collapse).start(chart)
                chart.disabled = True

        for c in (self.card_week, self.card_month, self.card_year):
            c.set_opened(c._key == self._selected)

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

        week_vals_paise = self.db.week_daily_totals(week_start)
        self._week_vals = [v / 100 for v in week_vals_paise]
        self._week_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        month_vals_paise = self.db.month_daily_totals(month_start)
        self._month_vals = [v / 100 for v in month_vals_paise]
        self._month_labels = [str(i) for i in range(1, len(self._month_vals) + 1)]

        year_vals_paise = self.db.year_monthly_totals(year_start)
        self._year_vals = [v / 100 for v in year_vals_paise]
        self._year_labels = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]

        if self._selected == "week":
            self.week_chart.set_data(self._week_vals, self._week_labels)
        elif self._selected == "month":
            self.month_chart.set_data(self._month_vals, self._month_labels)
        elif self._selected == "year":
            self.year_chart.set_data(self._year_vals, self._year_labels)
