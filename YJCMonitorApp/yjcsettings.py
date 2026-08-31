# ============================================================
# YJC Monitor - تنظیمات و مسیر ذخیره‌سازی (نسخه موبایل)
# ============================================================

import json
import os


# ============================================================
# فیدهای پیش‌فرض (همان چهار فید نسخه دسکتاپ)
# هر فید یک کلید enabled دارد که از صفحه تنظیمات کنترل می‌شود.
# ============================================================

DEFAULT_FEEDS = [
    {
        "id": "25",
        "name": "چهارمحال و بختیاری",
        "emoji": "🟢",
        "rss": "https://www.yjc.ir/fa/rss/25",
        "enabled": True,
    },
    {
        "id": "5",
        "name": "اجتماعی",
        "emoji": "🔵",
        "rss": "https://www.yjc.ir/fa/rss/5",
        "enabled": True,
    },
    {
        "id": "6",
        "name": "اقتصادی",
        "emoji": "🟠",
        "rss": "https://www.yjc.ir/fa/rss/6",
        "enabled": True,
    },
    {
        "id": "7",
        "name": "علمی و پزشکی",
        "emoji": "🟣",
        "rss": "https://www.yjc.ir/fa/rss/7",
        "enabled": True,
    },
]


DEFAULT_SETTINGS = {
    "feeds": DEFAULT_FEEDS,
    "check_interval_minutes": 30,
    "bale_bot_token": "",
    "bale_chat_id": "1546510289",
}


# ============================================================
# مسیر ذخیره‌سازی
#
# روی اندروید از مسیر اختصاصی برنامه (که با نصف/حذف برنامه
# پاک می‌شود ولی بین اجراها می‌ماند) استفاده می‌شود.
# روی دسکتاپ (برای تست قبل از build گرفتن) یک پوشه کنار
# پروژه استفاده می‌شود.
# ============================================================

def get_storage_dir():

    try:

        from android.storage import app_storage_path

        base = app_storage_path()

    except Exception:

        base = os.path.join(
            os.path.expanduser("~"),
            ".yjcmonitor"
        )

    os.makedirs(
        base,
        exist_ok=True
    )

    return base


def get_settings_path():

    return os.path.join(
        get_storage_dir(),
        "settings.json"
    )


def get_db_path():

    return os.path.join(
        get_storage_dir(),
        "history.db"
    )


def get_media_dir(sub):

    path = os.path.join(
        get_storage_dir(),
        "media",
        sub
    )

    os.makedirs(
        path,
        exist_ok=True
    )

    return path


# ============================================================
# بارگذاری تنظیمات
# ============================================================

def load_settings():

    path = get_settings_path()

    if not os.path.exists(path):

        save_settings(
            DEFAULT_SETTINGS
        )

        return json.loads(
            json.dumps(
                DEFAULT_SETTINGS
            )
        )

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(
                file
            )

        # ----------------------------------------------
        # اگر کلیدی جا افتاده بود (نسخه‌های قدیمی‌تر تنظیمات)
        # با مقدار پیش‌فرض پر شود
        # ----------------------------------------------

        for key, value in DEFAULT_SETTINGS.items():

            if key not in data:

                data[key] = value

        return data

    except Exception:

        return json.loads(
            json.dumps(
                DEFAULT_SETTINGS
            )
        )


# ============================================================
# ذخیره تنظیمات
# ============================================================

def save_settings(data):

    path = get_settings_path()

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )
