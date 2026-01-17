from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from app.screens.add import AddScreen
from app.db import DataBase
from app.screens.history import HistoryScreen


class AddTab(Screen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(AddScreen(db=db))


class HistoryTab(Screen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.screen = HistoryScreen(db=db)
        self.add_widget(self.screen)


class ReportsTab(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="Reports (next)"))


class RootUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.db = DataBase()
        self.db.init_database()

        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(AddTab(self.db, name="add"))
        self.screen_manager.add_widget(HistoryTab(self.db, name="history"))
        self.screen_manager.add_widget(ReportsTab(name="reports"))

        nav = BoxLayout(size_hint_y=None, height=56, padding=6, spacing=6)
        button_add = Button(text="Add")
        button_history = Button(text="History")
        button_reports = Button(text="Reports")

        button_add.bind(
            on_press=lambda *_: setattr(self.screen_manager, "current", "add")
        )
        button_history.bind(
            on_press=lambda *_: setattr(self.screen_manager, "current", "history")
        )
        button_reports.bind(
            on_press=lambda *_: setattr(self.screen_manager, "current", "reports")
        )

        nav.add_widget(button_add)
        nav.add_widget(button_history)
        nav.add_widget(button_reports)

        self.add_widget(self.screen_manager)
        self.add_widget(nav)


class TxTrackerApp(MDApp):
    def build(self):
        self.root_ui = RootUI()
        return self.root_ui

    def refresh_history(self):
        try:
            history_tab = self.root_ui.screen_manager.get_screen("history")
            history_tab.screen.refresh()
        except Exception:
            pass


if __name__ == "__main__":
    TxTrackerApp().run()
