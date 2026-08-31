import feedparser

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


# ============================================================
# تبدیل تاریخ RSS
# ============================================================

def parse_entry_datetime(entry):
    """
    تبدیل تاریخ RSS به datetime با timezone UTC
    """

    # ---------------------------------------------
    # اولویت با published_parsed
    # ---------------------------------------------

    parsed = entry.get("published_parsed")

    if parsed:

        try:

            return datetime(
                parsed.tm_year,
                parsed.tm_mon,
                parsed.tm_mday,
                parsed.tm_hour,
                parsed.tm_min,
                parsed.tm_sec,
                tzinfo=timezone.utc
            )

        except Exception:
            pass

    # ---------------------------------------------
    # updated_parsed
    # ---------------------------------------------

    parsed = entry.get("updated_parsed")

    if parsed:

        try:

            return datetime(
                parsed.tm_year,
                parsed.tm_mon,
                parsed.tm_mday,
                parsed.tm_hour,
                parsed.tm_min,
                parsed.tm_sec,
                tzinfo=timezone.utc
            )

        except Exception:
            pass

    # ---------------------------------------------
    # published string
    # ---------------------------------------------

    published = entry.get("published")

    if published:

        try:

            dt = parsedate_to_datetime(
                published
            )

            if dt.tzinfo is None:

                dt = dt.replace(
                    tzinfo=timezone.utc
                )

            return dt.astimezone(
                timezone.utc
            )

        except Exception:
            pass

    # ---------------------------------------------
    # updated string
    # ---------------------------------------------

    updated = entry.get("updated")

    if updated:

        try:

            dt = parsedate_to_datetime(
                updated
            )

            if dt.tzinfo is None:

                dt = dt.replace(
                    tzinfo=timezone.utc
                )

            return dt.astimezone(
                timezone.utc
            )

        except Exception:
            pass

    return None


# ============================================================
# دریافت اخبار RSS
# ============================================================

def get_news(
    rss_url,
    start_time=None
):

    print(
        f"📡 دریافت RSS: {rss_url}"
    )

    try:

        feed = feedparser.parse(
            rss_url
        )

    except Exception as e:

        print(
            f"❌ خطا در دریافت RSS: {e}"
        )

        # RSS دریافت نشده؛ این چرخه ناموفق است.
        return None

    if getattr(
        feed,
        "bozo",
        False
    ):

        print(
            "⚠️ RSS با هشدار دریافت شد."
        )

        bozo_exception = getattr(
            feed,
            "bozo_exception",
            None
        )

        if bozo_exception:

            print(
                f"⚠️ {bozo_exception}"
            )

        # اگر RSS به علت مشکل شبکه/اینترنت دریافت نشده باشد،
        # feedparser معمولاً bozo=True و entries خالی برمی‌گرداند.
        # در این حالت این چرخه نباید موفق محسوب شود.
        if bozo_exception and not getattr(
            feed,
            "entries",
            None
        ):

            print(
                "❌ RSS دریافت نشد؛ احتمالاً اینترنت قطع است."
            )

            return None

    entries = feed.entries

    print(
        f"📥 تعداد آیتم‌های RSS: {len(entries)}"
    )

    results = []

    now = datetime.now(
        timezone.utc
    )

    # ---------------------------------------------
    # اگر start_time نداریم:
    # 24 ساعت گذشته
    # ---------------------------------------------

    if start_time is None:

        from datetime import timedelta

        start_time = (
            now - timedelta(hours=24)
        )

    if start_time.tzinfo is None:

        start_time = start_time.replace(
            tzinfo=timezone.utc
        )

    start_time = start_time.astimezone(
        timezone.utc
    )

    # ========================================================
    # پردازش RSS
    # ========================================================

    for entry in entries:

        try:

            title = (
                entry.get("title")
                or ""
            ).strip()

            link = (
                entry.get("link")
                or ""
            ).strip()

            summary = (
                entry.get("summary")
                or entry.get("description")
                or ""
            ).strip()

            published_dt = (
                parse_entry_datetime(
                    entry
                )
            )

            # -----------------------------------------
            # اگر تاریخ پیدا نشد
            # -----------------------------------------

            if published_dt is None:

                print(
                    f"⚠️ تاریخ خبر مشخص نیست: {title}"
                )

                continue

            # -----------------------------------------
            # خبر قدیمی
            # -----------------------------------------

            if published_dt < start_time:

                continue

            # -----------------------------------------
            # خبر آینده
            # -----------------------------------------

            if published_dt > now:

                continue

            results.append(
                {
                    "title": title,

                    "summary": summary,

                    "link": link,

                    "published": published_dt,

                    "published_time": published_dt.strftime(
                        "%Y-%m-%d %H:%M:%S UTC"
                    ),
                }
            )

        except Exception as e:

            print(
                f"⚠️ خطا در پردازش RSS item: {e}"
            )

    # ========================================================
    # جدیدترین اول
    # ========================================================

    results.sort(
        key=lambda x: x["published"],
        reverse=True
    )

    return results