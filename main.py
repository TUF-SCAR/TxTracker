from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.label import MDLabel
from app.screens.add import AddScreen
from app.db import DataBase
from app.screens.history import HistoryScreen


class RootUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.db = DataBase()
        self.db.init_database()

        self.bottom_nav = MDBottomNavigation()

        self.tab_add = MDBottomNavigationItem(name="add", text="Add", icon="plus")
        self.add_screen = AddScreen(db=self.db)
        self.tab_add.add_widget(self.add_screen)

        self.tab_history = MDBottomNavigationItem(
            name="history", text="History", icon="history"
        )
        self.history_screen = HistoryScreen(db=self.db)
        self.history_screen.refresh()
        self.tab_history.add_widget(self.history_screen)

        self.tab_reports = MDBottomNavigationItem(
            name="reports", text="Reports", icon="chart-bar"
        )
        self.tab_reports.add_widget(MDLabel(text="Reports (next)", halign="center"))

        self.bottom_nav.add_widget(self.tab_add)
        self.bottom_nav.add_widget(self.tab_history)
        self.bottom_nav.add_widget(self.tab_reports)

        self.add_widget(self.bottom_nav)
        self.bottom_nav.bind(on_tab_switch=self.on_tab_switch)

    def on_tab_switch(self, nav, tab, tab_label, tab_icon):
        if tab.name == "history":
            self.history_screen.refresh()


class TxTrackerApp(MDApp):
    def on_start(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = "Red"

    def build(self):
        self.root_ui = RootUI()
        return self.root_ui

    def refresh_history(self):
        try:
            self.root_ui.history_screen.refresh()
        except Exception:
            pass


if __name__ == "__main__":
    TxTrackerApp().run()
