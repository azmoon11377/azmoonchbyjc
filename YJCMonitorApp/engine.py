# ============================================================
# YJC Monitor - موتور پایش (نسخه موبایل)
#
# همان منطق app.py نسخه دسکتاپ است، با این تفاوت‌ها:
# - به‌جای print از یک log_callback استفاده می‌شود تا متن‌ها
#   در رابط کاربری (Kivy) نمایش داده شوند.
# - به‌جای یک حلقه بی‌نهایت با time.sleep، از threading.Event
#   استفاده می‌شود تا با زدن دکمه «توقف» بلافاصله متوقف شود.
# - فیدهای فعال، بازه بررسی، توکن و chat_id بله از settings.json
#   خوانده می‌شوند (نه از config.py ثابت).
# ============================================================

import re
import time
import threading

from datetime import datetime, timedelta, timezone
from pathlib import Path

from core.monitor import get_news
from core.parser import (
    get_short_link,
    get_video_url,
    get_image_url,
    download_video,
    download_image,
)
from core.formatter import build_news_message
from core.database import NewsDatabase
from core.notifier import send_to_bale

import yjcsettings


OVERLAP_MINUTES = 5


def clean_summary(summary, title=""):

    if not summary:

        return ""

    summary = re.sub(
        r"<[^>]+>",
        " ",
        summary
    )

    summary = re.sub(
        r"\s+",
        " ",
        summary
    ).strip()

    if (
        title
        and summary.strip() == title.strip()
    ):

        return ""

    max_length = 400

    if len(summary) > max_length:

        summary = (
            summary[:max_length].rsplit(" ", 1)[0] + "..."
        )

    return summary


class MonitorEngine:
    """
    اجرای پایش RSS در یک ترد جداگانه.
    UI (main.py) این کلاس را می‌سازد، on_log/on_news_sent را
    وصل می‌کند و start()/stop() را صدا می‌زند.
    """

    def __init__(self, on_log=None, on_news_sent=None):

        self.on_log = on_log or (lambda text: None)
        self.on_news_sent = on_news_sent or (lambda title: None)

        self._stop_event = threading.Event()
        self._thread = None
        self.running = False

    # --------------------------------------------------
    # لاگ
    # --------------------------------------------------

    def log(self, text):

        try:

            self.on_log(str(text))

        except Exception:
            pass

    # --------------------------------------------------
    # شروع / توقف
    # --------------------------------------------------

    def start(self):

        if self.running:

            return

        self._stop_event.clear()
        self.running = True

        self._thread = threading.Thread(
            target=self._run,
            daemon=True
        )

        self._thread.start()

    def stop(self):

        self._stop_event.set()
        self.running = False

    # --------------------------------------------------
    # انتظار قابل‌قطع (به‌جای time.sleep یک‌جا)
    # --------------------------------------------------

    def _interruptible_sleep(self, seconds):

        remaining = seconds

        while remaining > 0 and not self._stop_event.is_set():

            step = min(1, remaining)

            time.sleep(step)

            remaining -= step

    # --------------------------------------------------
    # پردازش یک فید
    # --------------------------------------------------

    def _process_feed(self, feed, db, start_time, bot_token, chat_id):

        self.log(f"\n{feed['emoji']} {feed['name']}")
        self.log("-" * 40)

        news_list = get_news(
            feed["rss"],
            start_time=start_time
        )

        if news_list is None:

            self.log("❌ RSS دریافت نشد.")

            return False

        if not news_list:

            self.log("ℹ️ خبر جدیدی پیدا نشد.")

            return True

        self.log(f"📥 تعداد خبر جدید: {len(news_list)}")

        all_success = True

        images_dir = yjcsettings.get_media_dir("images")
        videos_dir = yjcsettings.get_media_dir("videos")

        for news in news_list:

            if self._stop_event.is_set():

                break

            try:

                self.log(f"\n📰 {news['title']}")

                short_link = get_short_link(
                    news["link"]
                )

                self.log(f"🔗 لینک: {short_link}")

                if not short_link:

                    self.log(
                        "⏭ لینک معتبر yjc.ir پیدا نشد؛ رد شد."
                    )

                    continue

                if db.exists(short_link):

                    self.log("⏭ قبلاً ارسال شده.")

                    continue

                video_path = ""
                image_path = ""

                video_url = get_video_url(news["link"])

                if video_url:

                    video_name = (
                        short_link.rstrip("/").split("/")[-1] + ".mp4"
                    )

                    video_path = str(Path(videos_dir) / video_name)

                    if not download_video(video_url, video_path):

                        video_path = ""

                if not video_path:

                    image_url = get_image_url(news["link"])

                    if image_url:

                        image_name = (
                            short_link.rstrip("/").split("/")[-1] + ".jpg"
                        )

                        image_path = str(Path(images_dir) / image_name)

                        if not download_image(image_url, image_path):

                            image_path = ""

                if not video_path and not image_path:

                    self.log("⏭ رسانه‌ای پیدا نشد؛ در دفعه بعد دوباره بررسی می‌شود.")

                    all_success = False

                    continue

                summary = clean_summary(
                    news.get("summary", ""),
                    news.get("title", "")
                )

                if not summary:

                    summary = "برای مشاهده جزئیات بیشتر به لینک خبر مراجعه کنید."

                message = build_news_message(
                    title=news["title"],
                    summary=summary,
                    short_link=short_link,
                    category=f"{feed['emoji']} {feed['name']}",
                    has_video=bool(video_path)
                )

                sent = send_to_bale(
                    message=message,
                    bot_token=bot_token,
                    chat_id=chat_id,
                    video_path=video_path,
                    image_path=image_path
                )

                if not sent:

                    self.log("❌ ارسال ناموفق بود.")

                    all_success = False

                    continue

                db.save(
                    category=feed["name"],
                    title=news["title"],
                    summary=summary,
                    original_link=news["link"],
                    short_link=short_link,
                    image_path=(video_path if video_path else image_path),
                    published=news["published"]
                )

                self.log("✅ خبر با موفقیت ارسال شد.")

                self.on_news_sent(news["title"])

            except Exception as e:

                self.log(f"❌ خطا در پردازش خبر: {e}")

                all_success = False

        return all_success

    # --------------------------------------------------
    # حلقه اصلی
    # --------------------------------------------------

    def _run(self):

        settings = yjcsettings.load_settings()

        feeds = [
            f for f in settings["feeds"] if f.get("enabled", True)
        ]

        interval_seconds = max(
            60,
            int(settings.get("check_interval_minutes", 30)) * 60
        )

        bot_token = settings.get("bale_bot_token", "")
        chat_id = settings.get("bale_chat_id", "")

        if not feeds:

            self.log("❌ هیچ فیدی فعال نیست. از تنظیمات یک فید را فعال کنید.")

            self.running = False

            return

        if not bot_token:

            self.log("⚠️ توکن ربات بله در تنظیمات خالی است.")

        self.log("▶️ پایش شروع شد.")

        db = NewsDatabase(
            db_path=yjcsettings.get_db_path()
        )

        try:

            last_run = db.get_last_run()
            now = datetime.now(timezone.utc)

            if last_run is None:

                start_time = now - timedelta(hours=24)

                self.log("🆕 اولین اجرا؛ ۲۴ ساعت گذشته بررسی می‌شود.")

            else:

                if last_run.tzinfo is None:

                    last_run = last_run.replace(tzinfo=timezone.utc)

                start_time = last_run - timedelta(minutes=OVERLAP_MINUTES)

                maximum_start = now - timedelta(hours=24)

                if start_time < maximum_start:

                    start_time = maximum_start

            while not self._stop_event.is_set():

                # هر دور دوباره تنظیمات را می‌خوانیم تا اگر
                # کاربر حین اجرا تنظیمات را عوض کرد، اعمال شود
                settings = yjcsettings.load_settings()

                feeds = [
                    f for f in settings["feeds"] if f.get("enabled", True)
                ]

                interval_seconds = max(
                    60,
                    int(settings.get("check_interval_minutes", 30)) * 60
                )

                bot_token = settings.get("bale_bot_token", "")
                chat_id = settings.get("bale_chat_id", "")

                self.log("\n🔎 در حال بررسی RSS ها...")

                cycle_start = datetime.now(timezone.utc)

                all_feeds_success = True

                for feed in feeds:

                    if self._stop_event.is_set():

                        break

                    try:

                        result = self._process_feed(
                            feed, db, start_time, bot_token, chat_id
                        )

                        if not result:

                            all_feeds_success = False

                    except Exception as e:

                        self.log(f"❌ خطا در بخش {feed['name']}: {e}")

                        all_feeds_success = False

                if all_feeds_success:

                    db.set_last_run(cycle_start)

                    start_time = cycle_start - timedelta(
                        minutes=OVERLAP_MINUTES
                    )

                self.log(
                    f"⏱ {interval_seconds // 60} دقیقه تا بررسی بعدی..."
                )

                self._interruptible_sleep(interval_seconds)

        finally:

            db.close()

            self.running = False

            self.log("🛑 پایش متوقف شد.")
