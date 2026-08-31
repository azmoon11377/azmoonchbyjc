import os
import re
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin


# ============================================================
# Headers
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    )
}


# ============================================================
# دریافت HTML خبر
# ============================================================

def get_page_html(news_url):

    response = requests.get(
        news_url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    response.encoding = "utf-8"

    return response.text


# ============================================================
# استخراج لینک کوتاه YJC
# ============================================================

def is_yjc_link(url):
    """
    بررسی می‌کند که آدرس داده‌شده از دامنه yjc.ir شروع شده باشد.
    """

    if not url:

        return False

    return bool(
        re.match(
            r"^https?://(www\.)?yjc\.ir(/|$)",
            url.strip()
        )
    )


def get_short_link(news_url):

    try:

        html = get_page_html(
            news_url
        )

        patterns = [

            r"https://www\.yjc\.ir/00[A-Za-z0-9]+",

            r"https://yjc\.ir/00[A-Za-z0-9]+",

        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                html
            )

            if match:

                return match.group(0)

    except Exception as e:

        print(
            f"❌ خطا در استخراج لینک کوتاه: {e}"
        )

    # ========================================================
    # اگر لینک کوتاه پیدا نشد:
    # فقط در صورتی از news_url استفاده کن که خودش از yjc.ir
    # شروع شده باشد. در غیر این صورت رشته خالی برگردان تا هیچ
    # آدرس غیر yjc در متن خبر نوشته نشود.
    # ========================================================

    if is_yjc_link(news_url):

        return news_url

    print(
        "⚠️ لینک معتبر yjc.ir پیدا نشد؛ "
        "لینک در پیام درج نمی‌شود."
    )

    return ""


# ============================================================
# استخراج ویدئوی اصلی خبر
# ============================================================

def get_video_url(news_url):

    try:

        html = get_page_html(
            news_url
        )

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        # ====================================================
        # 1 - تگ video
        # ====================================================

        video = soup.find(
            "video"
        )

        if video:

            src = video.get(
                "src"
            )

            if src:

                return urljoin(
                    news_url,
                    src
                )

            source = video.find(
                "source"
            )

            if source:

                src = (
                    source.get("src")
                    or source.get("data-src")
                )

                if src:

                    return urljoin(
                        news_url,
                        src
                    )

        # ====================================================
        # 2 - source
        # ====================================================

        for source in soup.find_all(
            "source"
        ):

            src = (
                source.get("src")
                or source.get("data-src")
                or source.get("data-video")
                or source.get("data-video-url")
            )

            if not src:
                continue

            if any(
                ext in src.lower()
                for ext in [
                    ".mp4",
                    ".webm",
                    ".mov",
                    ".m4v"
                ]
            ):

                return urljoin(
                    news_url,
                    src
                )

        # ====================================================
        # 3 - URL مستقیم MP4 داخل HTML
        # ====================================================

        video_pattern = re.compile(
            r'https?://[^"\']+\.(?:mp4|webm|mov|m4v)(?:\?[^"\']*)?',
            re.IGNORECASE
        )

        match = video_pattern.search(
            html
        )

        if match:

            return match.group(0)

        # ====================================================
        # 4 - URL نسبی
        # ====================================================

        for tag in soup.find_all(
            [
                "a",
                "video",
                "source",
                "div"
            ]
        ):

            for attribute in [
                "href",
                "src",
                "data-src",
                "data-video",
                "data-video-url",
                "data-file",
                "data-media"
            ]:

                value = tag.get(
                    attribute
                )

                if not value:
                    continue

                if any(
                    ext in value.lower()
                    for ext in [
                        ".mp4",
                        ".webm",
                        ".mov",
                        ".m4v"
                    ]
                ):

                    return urljoin(
                        news_url,
                        value
                    )

        # ====================================================
        # 5 - JSON / JavaScript
        # ====================================================

        patterns = [

            r'"videoUrl"\s*:\s*"([^"]+)"',

            r'"video_url"\s*:\s*"([^"]+)"',

            r'"video"\s*:\s*"([^"]+\.mp4[^"]*)"',

            r'"file"\s*:\s*"([^"]+\.mp4[^"]*)"',

            r"'videoUrl'\s*:\s*'([^']+)'",

            r"'video_url'\s*:\s*'([^']+)'",

        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                html,
                re.IGNORECASE
            )

            if match:

                value = (
                    match.group(1)
                    .replace("\\/", "/")
                    .replace("\\u0026", "&")
                )

                if value:

                    return urljoin(
                        news_url,
                        value
                    )

    except Exception as e:

        print(
            f"❌ خطا در استخراج ویدئو: {e}"
        )

    return None


# ============================================================
# استخراج تصویر اصلی خبر
# ============================================================

def get_image_url(news_url):

    try:

        html = get_page_html(
            news_url
        )

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        # ====================================================
        # 1 - og:image
        # ====================================================

        og_image = soup.find(
            "meta",
            property="og:image"
        )

        if (
            og_image
            and og_image.get("content")
        ):

            return urljoin(
                news_url,
                og_image["content"]
            )

        # ====================================================
        # 2 - twitter:image
        # ====================================================

        twitter_image = soup.find(
            "meta",
            attrs={
                "name": "twitter:image"
            }
        )

        if (
            twitter_image
            and twitter_image.get("content")
        ):

            return urljoin(
                news_url,
                twitter_image["content"]
            )

        # ====================================================
        # 3 - تصاویر صفحه
        # ====================================================

        for img in soup.find_all(
            "img"
        ):

            src = (
                img.get("src")
                or img.get("data-src")
                or img.get("data-original")
                or img.get("data-lazy-src")
            )

            if not src:
                continue

            src_lower = src.lower()

            if any(
                word in src_lower
                for word in [
                    "logo",
                    "icon",
                    "avatar",
                    "banner",
                    "loading"
                ]
            ):

                continue

            return urljoin(
                news_url,
                src
            )

    except Exception as e:

        print(
            f"❌ خطا در استخراج تصویر: {e}"
        )

    return None


# ============================================================
# دانلود ویدئو
# ============================================================

def download_video(
    video_url,
    output_path
):

    if not video_url:

        return False

    try:

        print(
            "🎥 در حال دانلود ویدئو..."
        )

        response = requests.get(
            video_url,
            headers=HEADERS,
            timeout=180,
            stream=True
        )

        response.raise_for_status()

        with open(
            output_path,
            "wb"
        ) as file:

            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):

                if chunk:

                    file.write(
                        chunk
                    )

        if (
            not os.path.exists(
                output_path
            )
            or os.path.getsize(
                output_path
            ) == 0
        ):

            print(
                "❌ فایل ویدئو خالی است."
            )

            return False

        print(
            f"✅ ویدئو ذخیره شد: {output_path}"
        )

        return True

    except Exception as e:

        print(
            f"❌ خطا در دانلود ویدئو: {e}"
        )

        try:

            if os.path.exists(
                output_path
            ):

                os.remove(
                    output_path
                )

        except Exception:
            pass

        return False


# ============================================================
# دانلود تصویر
# ============================================================

def download_image(
    image_url,
    output_path
):

    if not image_url:

        return False

    try:

        print(
            "🖼 در حال دانلود تصویر..."
        )

        response = requests.get(
            image_url,
            headers=HEADERS,
            timeout=60
        )

        response.raise_for_status()

        if not response.content:

            print(
                "❌ تصویر خالی دریافت شد."
            )

            return False

        with open(
            output_path,
            "wb"
        ) as file:

            file.write(
                response.content
            )

        if (
            not os.path.exists(
                output_path
            )
            or os.path.getsize(
                output_path
            ) == 0
        ):

            return False

        print(
            f"✅ تصویر ذخیره شد: {output_path}"
        )

        return True

    except Exception as e:

        print(
            f"❌ خطا در دانلود تصویر: {e}"
        )

        return False