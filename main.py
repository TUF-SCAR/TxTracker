from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from app.screens.add import AddScreen
from app.db import DataBase
from app.screens.history import HistoryScreen
from app.screens.reports import ReportScreen


class RootUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        with self.canvas.before:
            Color(0.03, 0.03, 0.04, 1)
            self._bg = Rectangle(pos=self.pos, size=self.size)

            Color(0.22, 0.40, 0.75, 0.18)
            self._glow_top = Ellipse(pos=(0, 0), size=(0, 0))

            Color(0.10, 0.20, 0.45, 0.12)
            self._glow_mid = Ellipse(pos=(0, 0), size=(0, 0))

            Color(0.50, 0.20, 0.60, 0.08)
            self._glow_side = Ellipse(pos=(0, 0), size=(0, 0))

            Color(0.96, 0.40, 0.46, 0.07)
            self._glow_bottom = Ellipse(pos=(0, 0), size=(0, 0))

        self.bind(pos=self._update_bg, size=self._update_bg)
        self._update_bg()
        self.db = DataBase()
        self.db.init_database()

        self.screen_manager = ScreenManager(transition=NoTransition())

        self.add_screen = AddScreen(db=self.db)

        self.history_screen = HistoryScreen(db=self.db)
        self.history_screen.refresh()

        self.reports_screen = ReportScreen(db=self.db)
        self.reports_screen.refresh()

        add_screen = Screen(name="add")
        add_screen.add_widget(self.add_screen)
        self.screen_manager.add_widget(add_screen)

        history_screen = Screen(name="history")
        history_screen.add_widget(self.history_screen)
        self.screen_manager.add_widget(history_screen)

        report_screen = Screen(name="reports")
        report_screen.add_widget(self.reports_screen)
        self.screen_manager.add_widget(report_screen)

        content_wrap = BoxLayout(padding=(dp(18), dp(12), dp(18), dp(12)))
        content_wrap.add_widget(self.screen_manager)
        self.add_widget(content_wrap)

        dock_area = AnchorLayout(
            size_hint_y=None, height=dp(104), padding=(0, 0, 0, dp(16))
        )
        self.dock = MDCard(
            size_hint=(None, None),
            height=dp(76),
            radius=[28],
            md_bg_color=(0.06, 0.06, 0.06, 0.95),
            padding=(dp(18), dp(10), dp(18), dp(10)),
            spacing=dp(22),
            elevation=0,
        )
        dock_area.add_widget(self.dock)
        self.add_widget(dock_area)

        self._build_dock_buttons()
        self._update_dock_width()
        from kivy.core.window import Window

        Window.bind(size=lambda *x: self._update_dock_width())

        self.screen_manager.current = "add"

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

        w, h = self.size
        self._glow_top.size = (w * 1.2, h * 0.55)
        self._glow_top.pos = (self.x - w * 0.1, self.y + h * 0.60)

        self._glow_mid.size = (w * 1.4, h * 0.55)
        self._glow_mid.pos = (self.x - w * 0.2, self.y + h * 0.25)

        self._glow_side.size = (w * 0.9, h * 0.6)
        self._glow_side.pos = (self.x + w * 0.25, self.y + h * 0.35)

        self._glow_bottom.size = (w * 1.2, h * 0.45)
        self._glow_bottom.pos = (self.x - w * 0.1, self.y - h * 0.10)

    def _update_dock_width(self, *args):
        from kivy.core.window import Window

        w = Window.width
        self.dock.width = min(dp(360), w * 0.92)

    def _build_dock_buttons(self):
        row = BoxLayout(orientation="horizontal", spacing=dp(18))

        self._button_add = self._make_dock_button("plus-circle-outline", "Add", "add")
        self._button_history = self._make_dock_button("history", "History", "history")
        self._button_reports = self._make_dock_button(
            "chart-box-outline", "Reports", "reports"
        )

        row.add_widget(self._button_add)
        row.add_widget(self._button_history)
        row.add_widget(self._button_reports)

        self.dock.add_widget(row)
        self.set_tab("add")

    def _make_dock_button(self, icon, label, tab_name):
        box = BoxLayout(orientation="vertical", spacing=dp(2))
        box.size_hint_x = 1

        button = MDIconButton(icon=icon)
        button.pos_hint = {"center_x": 0.5}
        button.bind(on_release=lambda *a: self.set_tab(tab_name))

        text = MDLabel(text=label, halign="center", font_style="Caption")
        text.theme_text_color = "Custom"

        box.add_widget(button)
        box.add_widget(text)

        box._dock_icon = button
        box._dock_label = text
        box._dock_tab = tab_name
        return box

    def set_tab(self, tab_name: str):
        self.screen_manager.current = tab_name

        active = (0.96, 0.40, 0.46, 1)
        inactive = (1, 1, 1, 0.60)

        for box in (self._button_add, self._button_history, self._button_reports):
            is_active = box._dock_tab == tab_name
            color = active if is_active else inactive
            box._dock_icon.theme_text_color = "Custom"
            box._dock_icon.text_color = color
            box._dock_label.text_color = color

        app = App.get_running_app()
        if tab_name == "history":
            Clock.schedule_once(lambda dt: self.history_screen.refresh(), 0)
        elif tab_name == "reports":
            Clock.schedule_once(lambda dt: self.reports_screen.refresh(), 0)


class TxTrackerApp(MDApp):
    def on_start(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.primary_hue = "200"
        self.theme_cls.accent_palette = "Red"
        self.theme_cls.material_style = "M3"

    def build(self):
        self.root_ui = RootUI()
        return self.root_ui

    def refresh_reports(self):
        try:
            self.root_ui.reports_screen.refresh()
        except Exception:
            pass

    def refresh_history(self):
        try:
            self.root_ui.history_screen.refresh()
        except Exception:
            pass


if __name__ == "__main__":
    TxTrackerApp().run()
