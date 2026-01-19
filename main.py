from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivy.clock import Clock
from app.screens.add import AddScreen
from app.db import DataBase
from app.screens.history import HistoryScreen
from app.screens.reports import ReportScreen


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
        self.reports_screen = ReportScreen(db=self.db)
        self.reports_screen.refresh()
        self.tab_reports.add_widget(self.reports_screen)

        self.bottom_nav.add_widget(self.tab_add)
        self.bottom_nav.add_widget(self.tab_history)
        self.bottom_nav.add_widget(self.tab_reports)

        self.add_widget(self.bottom_nav)


class TxTrackerApp(MDApp):
    def on_start(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = "Red"

    def build(self):
        self.root_ui = RootUI()
        self.root_ui.bottom_nav.bind(on_tab_switch=self.on_tab_switch)
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

    def on_tab_switch(self, nav, tab, tab_label, tab_icon):
        if tab.name == "history":
            Clock.schedule_once(lambda dt: self.root_ui.history_screen.refresh(), 0)
        elif tab.name == "reports":
            Clock.schedule_once(lambda dt: self.root_ui.reports_screen.refresh(), 0)


if __name__ == "__main__":
    TxTrackerApp().run()
