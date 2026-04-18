import os
from kivy.config import Config
from kivy.utils import platform

if platform in ("win", "linux", "macosx"):
    Config.set("graphics", "width", "360")
    Config.set("graphics", "height", "800")
    Config.set("graphics", "resizable", "0")

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.image import Image as CoreImage
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, SlideTransition
from kivy.storage.jsonstore import JsonStore
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton

from app.db import DataBase
from app.screens.add import AddScreen
from app.screens.history import HistoryScreen
from app.screens.reports import ReportScreen
from app.screens.settings import SettingsScreen
from app.services.drive_sync import DriveSyncService


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
        except Exception:
            pass


class RootUI(BoxLayout):
    bg_u = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._bg_rect = None
        self._bg_dim_rect = None
        self._bg_tex = None
        self.orientation = "vertical"
        self._last_main_screen = "add"
        self._current_main_screen = "add"
        self._status_bar_top_pad = dp(6)
        self._android_bottom_safe = dp(38) if platform == "android" else dp(16)
        self._accent_rgba = (0.914, 0.094, 0.153, 1.0)

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
                    texture=self._bg_tex,
                    pos=self.pos,
                    size=self.size,
                )

            self._bg_dim_color = Color(0, 0, 0, 0)
            self._bg_dim_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_bg, size=self._update_bg, bg_u=self._update_bg)
        self._update_bg()

        app = MDApp.get_running_app()
        db_dir = app.user_data_dir if app else os.getcwd()
        db_path = os.path.join(db_dir, "txtracker.sqlite3")

        self.db = DataBase(path=db_path)
        self.db.init_database()

        self.drive_sync = DriveSyncService()

        Window.bind(size=lambda *_: self._update_dock_width())
        Window.bind(on_keyboard=self._on_window_keyboard)

        # ---------- Top Bar ----------
        self.top_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            padding=(dp(16), self._status_bar_top_pad, dp(16), 0),
            spacing=dp(8),
        )

        self.left_slot = BoxLayout(size_hint=(None, 1), width=dp(48))
        self.right_slot = BoxLayout(size_hint=(None, 1), width=dp(48))

        self.left_action = MDIconButton(
            icon="arrow-left",
            pos_hint={"center_y": 0.5},
        )
        self.left_action.bind(on_release=lambda *_: self.close_settings())

        self.top_title = MDLabel(
            text="TxTracker",
            halign="center",
            valign="middle",
        )
        self.top_title.font_name = "Cause-Black"
        self.top_title.font_size = "22sp"

        self.right_action = MDIconButton(
            icon="cog-outline",
            pos_hint={"center_y": 0.5},
        )
        self.right_action.bind(on_release=lambda *_: self.open_settings())

        self.left_slot.add_widget(self.left_action)
        self.right_slot.add_widget(self.right_action)

        self.top_bar.add_widget(self.left_slot)
        self.top_bar.add_widget(self.top_title)
        self.top_bar.add_widget(self.right_slot)
        self.add_widget(self.top_bar)

        # ---------- Screens ----------
        self.screen_manager = ScreenManager(transition=NoTransition())

        self.add_screen = AddScreen(db=self.db)
        self.history_screen = HistoryScreen(db=self.db)
        self.reports_screen = ReportScreen(db=self.db)
        self.settings_screen = SettingsScreen(db=self.db, drive_sync=self.drive_sync)

        self.history_screen.refresh()
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

        settings_screen = Screen(name="settings")
        settings_screen.add_widget(self.settings_screen)
        self.screen_manager.add_widget(settings_screen)

        self.content_wrap = BoxLayout(
            padding=(dp(18), dp(8), dp(18), dp(18)),
        )
        self.content_wrap.add_widget(self.screen_manager)
        self.add_widget(self.content_wrap)

        # ---------- Dock ----------
        self.dock_area = AnchorLayout(
            size_hint_y=None,
            height=dp(136),
            padding=(0, 0, 0, self._android_bottom_safe),
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

        self.dock_area.add_widget(self.dock)
        self.add_widget(self.dock_area)

        self._build_dock_buttons()
        self._update_dock_width()

        self.screen_manager.current = "add"
        self._set_bg_segment(0)
        self.apply_visual_prefs()
        self._update_top_bar("add")
        Clock.schedule_once(lambda *_: self.add_screen.on_open(), 0.05)

    def _settings_store(self):
        app = MDApp.get_running_app()
        base = app.user_data_dir if app else "."
        return JsonStore(f"{base}/settings.json")

    def _get_pref(self, key, default):
        try:
            store = self._settings_store()
            if store.exists("prefs"):
                data = store.get("prefs")
                if key in data:
                    return data.get(key, default)
        except Exception:
            pass
        return default

    def _accent_from_pref(self):
        accent = self._get_pref("accent_color", "red")
        palette = {
            "red": (0.914, 0.094, 0.153, 1.0),
            "blue": (0.18, 0.52, 0.98, 1.0),
            "purple": (0.62, 0.33, 0.95, 1.0),
            "green": (0.18, 0.72, 0.38, 1.0),
        }
        return palette.get(accent, palette["red"])

    def _dim_alpha_from_pref(self):
        mode = self._get_pref("bg_dim_strength", "off")
        return {
            "off": 0.00,
            "low": 0.08,
            "medium": 0.18,
            "high": 0.28,
        }.get(mode, 0.00)

    def _card_alpha_from_pref(self):
        mode = self._get_pref("card_transparency", "normal")
        return {
            "glass": 0.74,
            "normal": 0.95,
            "dark": 0.98,
        }.get(mode, 0.95)

    def _corner_radius_from_pref(self):
        mode = self._get_pref("corner_style", "rounded")
        return {
            "soft": dp(18),
            "rounded": dp(28),
            "extra": dp(36),
        }.get(mode, dp(28))

    def _transition_duration(self):
        mode = self._get_pref("animation_speed", "normal")
        return {
            "normal": 0.35,
            "fast": 0.18,
            "off": 0.01,
        }.get(mode, 0.35)

    def apply_visual_prefs(self):
        self._accent_rgba = self._accent_from_pref()

        dim_alpha = self._dim_alpha_from_pref()
        self._bg_dim_color.rgba = (0, 0, 0, dim_alpha)

        large_ui = self._get_pref("large_ui_text", "off") == "on"
        compact = self._get_pref("compact_mode", "normal") == "compact"

        dock_height_mode = self._get_pref("dock_height_mode", "normal")
        dock_lift_mode = self._get_pref("dock_lift_mode", "high")
        show_nav_labels = self._get_pref("show_nav_labels", "on") == "on"

        dock_alpha = self._card_alpha_from_pref()
        corner_radius = self._corner_radius_from_pref()

        self.top_bar.height = dp(56) if compact else dp(60)
        self.top_bar.padding = (
            (dp(14), self._status_bar_top_pad, dp(14), 0)
            if compact
            else (dp(16), self._status_bar_top_pad, dp(16), 0)
        )
        self.top_title.font_size = "24sp" if large_ui else "22sp"

        self.content_wrap.padding = (
            (dp(14), dp(6), dp(14), dp(14))
            if compact
            else (dp(18), dp(8), dp(18), dp(18))
        )

        self._android_bottom_safe = (
            dp(54)
            if (platform == "android" and dock_lift_mode == "high")
            else dp(38) if platform == "android" else dp(16)
        )

        self.dock.height = dp(86) if dock_height_mode == "tall" else dp(76)
        self.dock.radius = [corner_radius]
        self.dock.md_bg_color = (0.06, 0.06, 0.06, dock_alpha)

        self.dock_area.height = self.dock.height + self._android_bottom_safe + dp(28)
        self.dock_area.padding = (0, 0, 0, self._android_bottom_safe)

        for box in (self._button_add, self._button_history, self._button_reports):
            box.spacing = dp(2) if show_nav_labels else 0
            box._dock_label.opacity = 1 if show_nav_labels else 0
            box._dock_label.height = dp(18) if show_nav_labels else 0
            box._dock_label.font_size = "14sp" if large_ui else "12sp"

        self._update_dock_state(
            self._current_main_screen
            if self.screen_manager.current != "settings"
            else self._last_main_screen
        )

        try:
            self.add_screen.apply_prefs()
        except Exception:
            pass

        try:
            self.settings_screen.apply_prefs()
        except Exception:
            pass

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

        if self._bg_dim_rect:
            self._bg_dim_rect.pos = self.pos
            self._bg_dim_rect.size = self.size

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
        self._update_dock_state("add")

    def _make_dock_button(self, icon, label, tab_name):
        box = BoxLayout(orientation="vertical", spacing=dp(2))
        box.size_hint_x = 1

        button = MDIconButton(icon=icon)
        button.pos_hint = {"center_x": 0.5}
        button.bind(on_release=lambda *_: self.set_tab(tab_name))

        text = MDLabel(
            text=label,
            halign="center",
            size_hint_y=None,
            height=dp(18),
            padding=(0, 0, 0, dp(4)),
        )
        text.font_name = "Cause-Black"
        text.theme_text_color = "Custom"
        text.font_size = "12sp"

        box.add_widget(button)
        box.add_widget(text)

        box._dock_icon = button
        box._dock_label = text
        box._dock_tab = tab_name
        return box

    def _update_dock_state(self, active_tab):
        inactive = (1, 1, 1, 0.60)

        for box in (self._button_add, self._button_history, self._button_reports):
            is_active = box._dock_tab == active_tab
            color = self._accent_rgba if is_active else inactive
            box._dock_icon.theme_text_color = "Custom"
            box._dock_icon.text_color = color
            box._dock_label.text_color = color

    def _show_dock(self):
        self.dock_area.opacity = 1
        self.dock_area.disabled = False
        self.dock_area.height = self.dock.height + self._android_bottom_safe + dp(28)

    def _hide_dock(self):
        self.dock_area.opacity = 0
        self.dock_area.disabled = True
        self.dock_area.height = 0

    def set_tab(self, tab_name: str):
        if tab_name not in ("add", "history", "reports"):
            return

        self._last_main_screen = tab_name

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

        def do_switch(*args):
            self.screen_manager.current = tab_name
            self._current_main_screen = tab_name
            self._update_top_bar(tab_name)
            if tab_name == "add":
                try:
                    self.add_screen.on_open()
                except Exception:
                    pass

        Clock.schedule_once(do_switch, 0.01)
        self._animate_tab_switch(tab_name)
        self._update_dock_state(tab_name)

    def open_settings(self):
        current = self.screen_manager.current
        if current in ("add", "history", "reports"):
            self._last_main_screen = current

        try:
            self.settings_screen.refresh_status()
        except Exception:
            pass

        duration = self._transition_duration()
        self.screen_manager.transition = SlideTransition(
            direction="down",
            duration=duration,
        )
        self.screen_manager.current = "settings"
        self._update_top_bar("settings")
        self._hide_dock()

    def close_settings(self):
        if self.screen_manager.current != "settings":
            return

        target = (
            self._last_main_screen
            if self._last_main_screen in ("add", "history", "reports")
            else "add"
        )

        duration = self._transition_duration()
        self.screen_manager.transition = SlideTransition(
            direction="up",
            duration=duration,
        )
        self.screen_manager.current = target
        self._current_main_screen = target
        self._update_top_bar(target)
        self._show_dock()
        self._update_dock_state(target)

        if target == "history":
            try:
                self.history_screen.refresh()
            except Exception:
                pass
        elif target == "reports":
            try:
                self.reports_screen.refresh()
            except Exception:
                pass
        elif target == "add":
            try:
                self.add_screen.on_open()
            except Exception:
                pass

    def _on_window_keyboard(self, window, key, scancode, codepoint, modifiers):
        if key == 27:
            if self.screen_manager.current == "settings":
                self.close_settings()
                return True
        return False

    def _update_top_bar(self, screen_name: str):
        if screen_name == "settings":
            self.left_action.opacity = 1
            self.left_action.disabled = False
            self.right_action.opacity = 0
            self.right_action.disabled = True
            self.top_title.text = "Settings"
        else:
            self.left_action.opacity = 0
            self.left_action.disabled = True
            self.right_action.opacity = 1
            self.right_action.disabled = False
            self.top_title.text = "TxTracker"

    def _set_bg_segment(self, index: int):
        self.bg_u = max(0.0, min(2.0 / 3.0, index / 3.0))

    def _animate_tab_switch(self, tab_name: str):
        from kivy.animation import Animation

        tab_order = {"add": 0, "history": 1, "reports": 2}
        current = tab_order.get(self._current_main_screen, 0)
        target = tab_order.get(tab_name, 0)

        if tab_name == "add":
            target_u = 0.0
        elif tab_name == "history":
            target_u = 1.0 / 3.0
        else:
            target_u = 2.0 / 3.0

        direction = "left" if target > current else "right"
        duration = self._transition_duration()

        self.screen_manager.transition = SlideTransition(
            duration=duration,
            direction=direction,
        )
        Animation.cancel_all(self, "bg_u")
        Animation(bg_u=target_u, duration=duration, t="out_quad").start(self)

    def refresh_reports(self):
        try:
            self.reports_screen.refresh()
        except Exception:
            pass

    def refresh_history(self):
        try:
            self.history_screen.refresh()
        except Exception:
            pass


class TxTrackerApp(MDApp):
    def on_start(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.primary_hue = "200"
        self.theme_cls.accent_palette = "Red"
        self.theme_cls.material_style = "M3"

        Clock.schedule_interval(self._auto_sync_tick, 60)
        self._apply_android_window_mode()

    def on_resume(self):
        self._apply_android_window_mode()

    def build(self):
        register_all_fonts()
        self.root_ui = RootUI()
        return self.root_ui

    def refresh_reports(self):
        try:
            self.root_ui.refresh_reports()
        except Exception:
            pass

    def refresh_history(self):
        try:
            self.root_ui.refresh_history()
        except Exception:
            pass

    def _auto_sync_tick(self, *_):
        try:
            self.root_ui.drive_sync.auto_sync_if_due(self.root_ui.db)
        except Exception:
            pass

    def _apply_android_window_mode(self):
        if platform != "android":
            return

        try:
            from android import mActivity
            from jnius import autoclass

            View = autoclass("android.view.View")
            Color = autoclass("android.graphics.Color")
            WindowManagerLayoutParams = autoclass(
                "android.view.WindowManager$LayoutParams"
            )
            BuildVersion = autoclass("android.os.Build$VERSION")
            BuildVersionCodes = autoclass("android.os.Build$VERSION_CODES")

            window = mActivity.getWindow()
            decor_view = window.getDecorView()

            flags = (
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
            )
            decor_view.setSystemUiVisibility(flags)

            window.clearFlags(WindowManagerLayoutParams.FLAG_TRANSLUCENT_STATUS)
            window.addFlags(WindowManagerLayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS)
            window.setStatusBarColor(Color.parseColor("#00000000"))
            window.setNavigationBarColor(Color.parseColor("#CC0A0A0A"))

            if BuildVersion.SDK_INT >= BuildVersionCodes.P:
                attrs = window.getAttributes()
                attrs.layoutInDisplayCutoutMode = (
                    WindowManagerLayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
                )
                window.setAttributes(attrs)

        except Exception:
            pass


if __name__ == "__main__":
    TxTrackerApp().run()
