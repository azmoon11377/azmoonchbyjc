# ============================================================
# YJC Monitor - اپ موبایل (Kivy)
# ============================================================

import queue

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.checkbox import CheckBox
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, BooleanProperty

import yjcsettings
from engine import MonitorEngine


KV = """
#:import Window kivy.core.window.Window

ScreenManager:
    MainScreen:
    SettingsScreen:


<MainScreen>:
    name: "main"

    BoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(8)

        BoxLayout:
            size_hint_y: None
            height: dp(48)
            spacing: dp(8)

            Label:
                text: "YJC Monitor"
                font_size: "20sp"
                bold: True
                halign: "right"
                text_size: self.size

            Button:
                text: "تنظیمات"
                size_hint_x: None
                width: dp(110)
                on_release: app.go_settings()

        Label:
            text: root.status_text
            size_hint_y: None
            height: dp(30)
            color: (0.2, 0.7, 0.2, 1) if root.is_running else (0.8, 0.2, 0.2, 1)

        Button:
            text: "توقف" if root.is_running else "شروع پایش"
            size_hint_y: None
            height: dp(56)
            font_size: "18sp"
            background_color: (0.8, 0.2, 0.2, 1) if root.is_running else (0.2, 0.6, 0.3, 1)
            on_release: app.toggle_engine()

        ScrollView:
            id: scroll
            do_scroll_x: False

            Label:
                id: log_label
                text: root.log_text
                size_hint_y: None
                height: self.texture_size[1]
                text_size: (self.width, None)
                halign: "right"
                valign: "top"
                padding: (dp(6), dp(6))


<SettingsScreen>:
    name: "settings"

    BoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(10)

        BoxLayout:
            size_hint_y: None
            height: dp(48)

            Button:
                text: "بازگشت"
                size_hint_x: None
                width: dp(110)
                on_release: app.go_main()

            Label:
                text: "تنظیمات"
                font_size: "20sp"
                bold: True

        ScrollView:

            BoxLayout:
                id: feeds_box
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(6)

                Label:
                    text: "فیدهای فعال:"
                    size_hint_y: None
                    height: dp(30)
                    halign: "right"
                    text_size: self.size

                Label:
                    text: "بازه بررسی (دقیقه):"
                    size_hint_y: None
                    height: dp(30)
                    halign: "right"
                    text_size: self.size

                TextInput:
                    id: interval_input
                    text: root.interval_text
                    multiline: False
                    input_filter: "int"
                    size_hint_y: None
                    height: dp(44)

                Label:
                    text: "توکن ربات بله (BALE_BOT_TOKEN):"
                    size_hint_y: None
                    height: dp(30)
                    halign: "right"
                    text_size: self.size

                TextInput:
                    id: token_input
                    text: root.token_text
                    multiline: False
                    password: True
                    size_hint_y: None
                    height: dp(44)

                Label:
                    text: "شناسه چت بله (chat_id):"
                    size_hint_y: None
                    height: dp(30)
                    halign: "right"
                    text_size: self.size

                TextInput:
                    id: chat_id_input
                    text: root.chat_id_text
                    multiline: False
                    size_hint_y: None
                    height: dp(44)

        Button:
            text: "ذخیره تنظیمات"
            size_hint_y: None
            height: dp(54)
            font_size: "16sp"
            background_color: (0.2, 0.5, 0.8, 1)
            on_release: app.save_settings_screen()

        Label:
            text: root.saved_text
            size_hint_y: None
            height: dp(24)
            color: (0.2, 0.7, 0.2, 1)
"""


class MainScreen(Screen):

    status_text = StringProperty("متوقف")
    log_text = StringProperty("")
    is_running = BooleanProperty(False)


class SettingsScreen(Screen):

    interval_text = StringProperty("30")
    token_text = StringProperty("")
    chat_id_text = StringProperty("")
    saved_text = StringProperty("")


class YjcMonitorApp(App):

    def build(self):

        self.title = "YJC Monitor"

        self.log_queue = queue.Queue()
        self.log_lines = []

        self.engine = MonitorEngine(
            on_log=self._on_engine_log,
            on_news_sent=self._on_news_sent,
        )

        self.root_widget = Builder.load_string(KV)

        Clock.schedule_interval(self._drain_log_queue, 0.5)

        return self.root_widget

    def on_start(self):

        self._build_feed_checkboxes()
        self._load_settings_into_form()

    # --------------------------------------------------
    # ناوبری
    # --------------------------------------------------

    def go_settings(self):

        self._load_settings_into_form()

        self.root_widget.current = "settings"

    def go_main(self):

        self.root_widget.current = "main"

    # --------------------------------------------------
    # صفحه تنظیمات
    # --------------------------------------------------

    def _build_feed_checkboxes(self):

        settings_screen = self.root_widget.get_screen("settings")

        feeds_box = settings_screen.ids.feeds_box

        # حذف چک‌باکس‌های قبلی (در صورت بازسازی)
        for widget in list(self._feed_checkbox_widgets_get(feeds_box)):

            feeds_box.remove_widget(widget)

        self._feed_checkboxes = {}

        settings = yjcsettings.load_settings()

        # چک‌باکس‌ها را درست بعد از لیبل "فیدهای فعال:" اضافه می‌کنیم
        # (که اولین ویجت در feeds_box است)
        insert_index = len(feeds_box.children) - 1

        for feed in settings["feeds"]:

            row = BoxLayout(
                size_hint_y=None,
                height=40,
            )

            checkbox = CheckBox(
                active=feed.get("enabled", True),
                size_hint_x=None,
                width=40,
            )

            label = Label(
                text=f"{feed['emoji']} {feed['name']}",
                halign="right",
            )

            row.add_widget(label)
            row.add_widget(checkbox)

            feeds_box.add_widget(row, index=insert_index)

            self._feed_checkboxes[feed["id"]] = checkbox

    def _feed_checkbox_widgets_get(self, feeds_box):

        # ردیف‌هایی که قبلاً برای فیدها اضافه شده‌اند (BoxLayout با دو فرزند)
        return [
            child for child in feeds_box.children
            if isinstance(child, BoxLayout)
        ]

    def _load_settings_into_form(self):

        settings = yjcsettings.load_settings()

        settings_screen = self.root_widget.get_screen("settings")

        settings_screen.interval_text = str(
            settings.get("check_interval_minutes", 30)
        )

        settings_screen.token_text = settings.get("bale_bot_token", "")
        settings_screen.chat_id_text = settings.get("bale_chat_id", "")

        if hasattr(self, "_feed_checkboxes"):

            for feed in settings["feeds"]:

                checkbox = self._feed_checkboxes.get(feed["id"])

                if checkbox:

                    checkbox.active = feed.get("enabled", True)

    def save_settings_screen(self):

        settings_screen = self.root_widget.get_screen("settings")

        settings = yjcsettings.load_settings()

        for feed in settings["feeds"]:

            checkbox = self._feed_checkboxes.get(feed["id"])

            if checkbox:

                feed["enabled"] = checkbox.active

        try:

            interval = int(settings_screen.ids.interval_input.text or "30")

        except ValueError:

            interval = 30

        settings["check_interval_minutes"] = max(1, interval)
        settings["bale_bot_token"] = settings_screen.ids.token_input.text.strip()
        settings["bale_chat_id"] = settings_screen.ids.chat_id_input.text.strip()

        yjcsettings.save_settings(settings)

        settings_screen.saved_text = "✅ ذخیره شد."

        Clock.schedule_once(
            lambda dt: setattr(settings_screen, "saved_text", ""),
            2
        )

    # --------------------------------------------------
    # شروع / توقف پایش
    # --------------------------------------------------

    def toggle_engine(self):

        main_screen = self.root_widget.get_screen("main")

        if self.engine.running:

            self.engine.stop()

            main_screen.is_running = False
            main_screen.status_text = "در حال توقف..."

        else:

            self.log_lines = []

            main_screen.log_text = ""

            self.engine.start()

            main_screen.is_running = True
            main_screen.status_text = "در حال اجرا"

    # --------------------------------------------------
    # کال‌بک‌های engine (از ترد پس‌زمینه صدا زده می‌شوند)
    # --------------------------------------------------

    def _on_engine_log(self, text):

        self.log_queue.put(("log", text))

    def _on_news_sent(self, title):

        self.log_queue.put(("news", title))

    def _drain_log_queue(self, dt):

        main_screen = self.root_widget.get_screen("main")

        updated = False

        while True:

            try:

                kind, payload = self.log_queue.get_nowait()

            except queue.Empty:

                break

            if kind == "log":

                self.log_lines.append(payload)

                if len(self.log_lines) > 500:

                    self.log_lines = self.log_lines[-500:]

                updated = True

            elif kind == "news":

                self._show_notification(payload)

        if updated:

            main_screen.log_text = "\n".join(self.log_lines)

            scroll = main_screen.ids.get("scroll")

            if scroll:

                scroll.scroll_y = 0

        if not self.engine.running and main_screen.status_text == "در حال اجرا":

            main_screen.is_running = False
            main_screen.status_text = "متوقف"

        elif not self.engine.running and main_screen.status_text == "در حال توقف...":

            main_screen.status_text = "متوقف"

    def _show_notification(self, title):

        try:

            from plyer import notification

            notification.notify(
                title="خبر جدید ارسال شد",
                message=title[:150],
                app_name="YJC Monitor",
                timeout=6,
            )

        except Exception:
            pass


if __name__ == "__main__":

    YjcMonitorApp().run()
