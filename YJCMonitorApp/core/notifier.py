# ============================================================
# YJC Monitor - Notifier (نسخه موبایل)
#
# تفاوت با نسخه دسکتاپ:
# - وابستگی به pyperclip حذف شده (کلیپ‌بورد دسکتاپ روی اندروید
#   کاربرد ندارد و اصلاً استفاده نمی‌شد).
# - وابستگی به python-dotenv حذف شده؛ توکن ربات بله و chat_id
#   دیگر از فایل .env خوانده نمی‌شوند، بلکه از تنظیمات برنامه
#   (ذخیره‌شده در settings.json) به هر تابع پاس داده می‌شوند.
# ============================================================

import os

import requests


# ============================================================
# ارسال متن
# ============================================================

def send_message(
    text,
    bot_token,
    chat_id
):

    if not bot_token:

        print(
            "❌ توکن ربات بله تنظیم نشده است."
        )

        return False

    try:

        url = (
            f"https://tapi.bale.ai/bot{bot_token}/sendMessage"
        )

        data = {
            "chat_id": chat_id,
            "text": text
        }

        response = requests.post(
            url,
            data=data,
            timeout=30
        )

        print(
            f"📤 ارسال متن به بله: "
            f"HTTP {response.status_code}"
        )

        if response.ok:

            result = response.json()

            if result.get("ok"):

                print(
                    "✅ متن با موفقیت به بله ارسال شد."
                )

                return True

            print(
                f"❌ بله خطا داد: {result}"
            )

            return False

        print(
            f"❌ خطای HTTP بله: "
            f"{response.text}"
        )

        return False

    except Exception as e:

        print(
            f"❌ خطا در ارسال متن: {e}"
        )

        return False


# ============================================================
# ارسال عکس + کپشن
# ============================================================

def send_photo(
    image_path,
    caption,
    bot_token,
    chat_id
):

    if not bot_token:

        print(
            "❌ توکن ربات بله تنظیم نشده است."
        )

        return False

    if not image_path:

        print(
            "❌ مسیر تصویر خالی است."
        )

        return False

    if not os.path.exists(
        image_path
    ):

        print(
            f"❌ فایل تصویر پیدا نشد: "
            f"{image_path}"
        )

        return False

    try:

        url = (
            f"https://tapi.bale.ai/bot{bot_token}/sendPhoto"
        )

        with open(
            image_path,
            "rb"
        ) as image_file:

            files = {
                "photo": image_file
            }

            data = {
                "chat_id": chat_id,
                "caption": caption
            }

            response = requests.post(
                url,
                data=data,
                files=files,
                timeout=90
            )

        print(
            f"📤 ارسال عکس به بله: "
            f"HTTP {response.status_code}"
        )

        if response.ok:

            result = response.json()

            if result.get("ok"):

                print(
                    "✅ عکس و کپشن با موفقیت "
                    "به بله ارسال شد."
                )

                return True

            print(
                f"❌ بله خطا داد: {result}"
            )

            return False

        print(
            f"❌ خطای HTTP بله: "
            f"{response.text}"
        )

        return False

    except Exception as e:

        print(
            f"❌ خطا در ارسال عکس: {e}"
        )

        return False


# ============================================================
# ارسال ویدئو + کپشن
# ============================================================

def send_video(
    video_path,
    caption,
    bot_token,
    chat_id
):

    if not bot_token:

        print(
            "❌ توکن ربات بله تنظیم نشده است."
        )

        return False

    if not video_path:

        print(
            "❌ مسیر ویدئو خالی است."
        )

        return False

    if not os.path.exists(
        video_path
    ):

        print(
            f"❌ فایل ویدئو پیدا نشد: "
            f"{video_path}"
        )

        return False

    try:

        url = (
            f"https://tapi.bale.ai/bot{bot_token}/sendVideo"
        )

        print(
            "🎥 در حال ارسال ویدئو به بله..."
        )

        with open(
            video_path,
            "rb"
        ) as video_file:

            files = {
                "video": video_file
            }

            data = {
                "chat_id": chat_id,
                "caption": caption
            }

            response = requests.post(
                url,
                data=data,
                files=files,
                timeout=300
            )

        print(
            f"📤 ارسال ویدئو به بله: "
            f"HTTP {response.status_code}"
        )

        if response.ok:

            result = response.json()

            if result.get("ok"):

                print(
                    "✅ ویدئو و کپشن با موفقیت "
                    "به بله ارسال شد."
                )

                return True

            print(
                f"❌ بله خطا داد: {result}"
            )

            return False

        print(
            f"❌ خطای HTTP بله: "
            f"{response.text}"
        )

        return False

    except Exception as e:

        print(
            f"❌ خطا در ارسال ویدئو: {e}"
        )

        return False


# ============================================================
# ارسال خبر
#
# اولویت:
# 1- ویدئو
# 2- عکس
# ============================================================

def send_news(
    bot_token,
    chat_id,
    video_path="",
    image_path="",
    message=""
):

    # ========================================================
    # اولویت اول: ویدئو
    # ========================================================

    if (
        video_path
        and os.path.exists(video_path)
    ):

        print(
            "🎥 ویدئو موجود است؛ "
            "اولویت ارسال با ویدئو است."
        )

        sent = send_video(
            video_path=video_path,
            caption=message,
            bot_token=bot_token,
            chat_id=chat_id
        )

        if sent:

            return True

        print(
            "⚠️ ارسال ویدئو ناموفق بود."
        )

        print(
            "🔄 در صورت وجود تصویر، "
            "ارسال تصویر انجام می‌شود."
        )

    # ========================================================
    # اولویت دوم: عکس
    # ========================================================

    if (
        image_path
        and os.path.exists(image_path)
    ):

        print(
            "🖼 ارسال عکس انجام می‌شود."
        )

        return send_photo(
            image_path=image_path,
            caption=message,
            bot_token=bot_token,
            chat_id=chat_id
        )

    # ========================================================
    # هیچ رسانه‌ای
    # ========================================================

    print(
        "❌ نه ویدئو و نه تصویر خبر موجود نیست."
    )

    return False


# ============================================================
# تابع اصلی ارسال به بله
# ============================================================

def send_to_bale(
    message,
    bot_token,
    chat_id,
    video_path="",
    image_path=""
):

    print()

    print(
        "📤 در حال ارسال خبر به بله..."
    )

    return send_news(
        bot_token=bot_token,
        chat_id=chat_id,
        video_path=video_path,
        image_path=image_path,
        message=message
    )
