# TxTracker - A simple transaction tracker built with Kivy & KivyMD.
# Main application file. This sets up the main UI structure, handles screen management, and initializes the database connection.

import os
from kivy.config import Config
from kivy.utils import platform

# Setting a fixed window size for desktop platforms. This will not affect mobile platforms,
# which will use the full screen and it will look different in mobile.

if platform in ("win", "linux", "macosx"):
    Config.set("graphics", "width", "360")
    Config.set("graphics", "height", "800")
    Config.set("graphics", "resizable", "1")

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.text import LabelBase
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


# This function registers all TTF font files found in the "assets/fonts" directory.


def register_all_fonts():
    fonts_dir = os.path.join(os.path.dirname(__file__), "assets", "fonts")
    if not os.path.isdir(fonts_dir):
        return

    # Loop through all files in the fonts directory and register those that are TTF fonts.
    for fname in os.listdir(fonts_dir):
        if not fname.lower().endswith(".ttf"):
            continue

        # The font name will be same as the file name without the extension.
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

        # Attempt to load the background texture. If it fails, we'll just use a solid color.
        # it is a long strip (4320 x 3200) that we will shift to create a parallax effect when switching tabs.
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

        # This is where we initialize the database connection. If the app is running on a mobile platform,
        # we want to store the database in the user data directory. On desktop, we can just use the current working directory.
        from kivy.app import App

        app = App.get_running_app()
        db_dir = app.user_data_dir if app else os.getcwd()
        db_path = os.path.join(db_dir, "txtracker.sqlite3")
        self.db = DataBase(path=db_path)
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
            radius=[dp(28)],
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

    # This function builds the bottom dock with the three main buttons: Add, History, and Reports.

    def _build_dock_buttons(self):
        row = BoxLayout(orientation="horizontal", spacing=dp(18))

        self._button_add = self._make_dock_button(
            "plus-circle-outline",
            "Add",
            "add",
        )
        self._button_history = self._make_dock_button(
            "history",
            "History",
            "history",
        )
        self._button_reports = self._make_dock_button(
            "chart-box-outline",
            "Reports",
            "reports",
        )

        row.add_widget(self._button_add)
        row.add_widget(self._button_history)
        row.add_widget(self._button_reports)

        self.dock.add_widget(row)
        self.set_tab("add")

    # This function creates a button for the dock with the specified icon, label, and associated tab name.
    # It returns a BoxLayout containing the button and label, and also stores references to these widgets
    # for later use when updating their appearance based on the active tab.

    def _make_dock_button(self, icon, label, tab_name):
        box = BoxLayout(orientation="vertical", spacing=dp(2))
        box.size_hint_x = 1

        button = MDIconButton(icon=icon)
        button.pos_hint = {"center_x": 0.5}
        button.bind(on_release=lambda *a: self.set_tab(tab_name))

        text = MDLabel(
            text=label,
            halign="center",
            padding=(0, 0, 0, dp(15)),
        )
        text.font_name = "Cause-Black"
        text.theme_text_color = "Custom"

        box.add_widget(button)
        box.add_widget(text)

        box._dock_icon = button
        box._dock_label = text
        box._dock_tab = tab_name
        return box

    # This function is called when a dock button is pressed. It switches the current screen to the one associated with the button,
    # and also updates the appearance of the dock buttons to indicate which one is active. It also triggers a refresh of the screen if necessary,
    # and starts an animation to smoothly transition the background image to the new tab's segment.

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

    # This function animates the background image to smoothly transition to the segment associated with the new tab.
    # It calculates the target U coordinate based on the tab index and creates a slide transition for the screen manager.

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
        self._apply_immersive()

    def on_resume(self):
        self._apply_immersive()

    def build(self):
        register_all_fonts()
        self.root_ui = RootUI()
        return self.root_ui

    # These functions are used to trigger a refresh of the history and reports screens when they become active.

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

    # This function applies immersive mode on Android devices to hide the navigation bar and status bar for a more full-screen experience.

    def _apply_immersive(self):
        if platform != "android":
            return
        try:
            from android import mActivity
            from jnius import autoclass

            View = autoclass("android.view.View")
            decor_view = mActivity.getWindow().getDecorView()

            flags = (
                View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            )
            decor_view.setSystemUiVisibility(flags)
        except Exception:
            pass


# I thought of adding comments to other files too, but i became too lazy. sry :P


if __name__ == "__main__":
    TxTrackerApp().run()
