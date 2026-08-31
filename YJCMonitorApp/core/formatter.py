# ============================================================
# YJC Monitor Formatter
# ============================================================

import re


CHANNEL_NAME = "باشگاه خبرنگاران جوان چهارمحال و بختیاری"
CHANNEL_ID = "@ChbYjcNews"


def clean_link_for_display(link):
    """
    حذف https:// و www. از ابتدای لینک، فقط برای نمایش در متن خبر.
    مثال: https://www.yjc.ir/00cHfy  ->  yjc.ir/00cHfy
    """

    link = (
        link or ""
    ).strip()

    link = re.sub(
        r"^https?://(www\.)?",
        "",
        link
    )

    return link


TITLE_EMOJI = "💢"
VIDEO_TITLE_EMOJI = "🎥"


def build_news_message(
    title,
    summary,
    short_link,
    category="",
    channel=None,
    has_video=False
):

    title = (
        title or ""
    ).strip()

    summary = (
        summary or ""
    ).strip()

    display_link = clean_link_for_display(
        short_link
    )

    title_emoji = (
        VIDEO_TITLE_EMOJI
        if has_video
        else TITLE_EMOJI
    )

    message = f"""
{title_emoji} {title}

🔸 {summary}

🔻 جزئیات بیشتر در لینک زیر:

👉 {display_link}

🔷 کانال «{CHANNEL_NAME}»:

🆔 {CHANNEL_ID}
""".strip()

    return message