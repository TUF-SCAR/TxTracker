from kivy.app import App
from kivy.uix.label import Label


class TxTrackerApp(App):
    def build(self):
        return Label(text="TxTracker App Running")


if __name__ == "__main__":
    TxTrackerApp().run()
