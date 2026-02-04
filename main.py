import os
from kivy.config import Config
from kivy.core.text import LabelBase

Config.set("graphics", "width", "412")
Config.set("graphics", "height", "815")
Config.set("graphics", "resizable", "0")

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.image import Image as CoreImage
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from app.db import DataBase
from app.screens.add import AddScreen
from app.screens.history import HistoryScreen
from app.screens.reports import ReportScreen


def register_all_fonts():
    fonts_dir = os.path.join(os.path.dirname(__file__), "assets", "fonts")
    if not os.path.isdir(fonts_dir):
        return

    for fname in os.listdir(fonts_dir):
        if not fname.lower().endswith(".ttf"):
            continue

        path = os.path.join(fonts_dir, fname)
        font_name = os.path.splitext(fname)[0]

        try:
            LabelBase.register(name=font_name, fn_regular=path)
        except Exception as e:
            pass


class RootUI(BoxLayout):
    bg_u = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._bg_rect = None
        self._bg_tex = None

        bg_path = os.path.join(os.path.dirname(__file__), "assets", "background.png")
        if os.path.exists(bg_path):
            try:
                self._bg_tex = CoreImage(bg_path).texture
            except Exception:
                self._bg_tex = None

        with self.canvas.before:
            if self._bg_tex is None:
                Color(0.05, 0.07, 0.12, 1)
                self._bg_rect = Rectangle(pos=self.pos, size=self.size)

            else:
                Color(1, 1, 1, 1)
                self._bg_tex.wrap = "clamp_to_edge"
                self._bg_rect = Rectangle(
                    texture=self._bg_tex, pos=self.pos, size=self.size
                )

        self.bind(pos=self._update_bg, size=self._update_bg)
        self.bind(bg_u=self._update_bg)

        self.orientation = "vertical"

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

        Window.bind(size=lambda *x: self._update_dock_width())

        self.screen_manager.current = "add"
        self._set_bg_segment(0)

    def _update_bg(self, *args):
        if self._bg_rect:
            self._bg_rect.pos = self.pos
            self._bg_rect.size = self.size
            if self._bg_tex is not None:
                u0 = self.bg_u
                u1 = self.bg_u + (1.0 / 3.0)
                self._bg_rect.tex_coords = (
                    u0,
                    1,
                    u1,
                    1,
                    u1,
                    0,
                    u0,
                    0,
                )

    def _update_dock_width(self, *args):
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

        text = MDLabel(
            text=label,
            halign="center",
            padding=(0, 0, 0, 15),
        )
        text.font_name = "Cause-Black"
        text.theme_text_color = "Custom"

        box.add_widget(button)
        box.add_widget(text)

        box._dock_icon = button
        box._dock_label = text
        box._dock_tab = tab_name
        return box

    def set_tab(self, tab_name: str):
        def do_switch(*args):
            self.screen_manager.current = tab_name

        if tab_name == "history":
            try:
                self.history_screen.refresh()
            except Exception:
                pass
        elif tab_name == "reports":
            try:
                self.reports_screen.refresh()
            except Exception:
                pass

        Clock.schedule_once(do_switch, 0.01)
        self._animate_tab_switch(tab_name)

        active = (0.52, 0.10, 0.14, 1.0)
        inactive = (1, 1, 1, 0.60)

        for box in (self._button_add, self._button_history, self._button_reports):
            is_active = box._dock_tab == tab_name
            color = active if is_active else inactive
            box._dock_icon.theme_text_color = "Custom"
            box._dock_icon.text_color = color
            box._dock_label.text_color = color

    def _set_bg_segment(self, index: int):
        self.bg_u = max(0.0, min(2.0 / 3.0, index / 3.0))

    def _animate_tab_switch(self, tab_name: str):
        from kivy.animation import Animation
        from kivy.uix.screenmanager import SlideTransition

        tab_order = {"add": 0, "history": 1, "reports": 2}
        current = tab_order.get(self.screen_manager.current, 0)
        target = tab_order.get(tab_name, 0)

        if tab_name == "add":
            target_u = 0.0
        elif tab_name == "history":
            target_u = 1.0 / 3.0
        else:
            target_u = 2.0 / 3.0

        direction = "left" if target > current else "right"

        self.screen_manager.transition = SlideTransition(
            duration=0.35, direction=direction
        )
        Animation.cancel_all(self, "bg_u")
        Animation(bg_u=target_u, duration=0.35, t="out_quad").start(self)


class TxTrackerApp(MDApp):
    def on_start(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.primary_hue = "200"
        self.theme_cls.accent_palette = "Red"
        self.theme_cls.material_style = "M3"
        Clock.schedule_interval(self._auto_sync_tick, 60)

    def build(self):
        register_all_fonts()
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

    def _auto_sync_tick(self, *_):
        try:
            self.root_ui.history_screen.drive_sync.auto_sync_if_due(self.root_ui.db)
        except Exception:
            pass


if __name__ == "__main__":
    TxTrackerApp().run()
