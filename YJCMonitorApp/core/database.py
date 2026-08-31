import sqlite3

from pathlib import Path
from datetime import datetime, timezone


# ============================================================
# مسیر دیتابیس
# ============================================================

DB_PATH = Path(
    "data/history.db"
)


# ============================================================
# Database
# ============================================================

class NewsDatabase:

    def __init__(
        self,
        db_path=DB_PATH
    ):

        self.db_path = Path(
            db_path
        )

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.connection = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False
        )

        self.connection.row_factory = (
            sqlite3.Row
        )

        self.create_tables()

    # ========================================================
    # ایجاد جدول
    # ========================================================

    def create_tables(self):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                title TEXT,
                summary TEXT,
                original_link TEXT,
                short_link TEXT UNIQUE,
                image_path TEXT,
                published TEXT,
                created_at TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS app_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )

        self.connection.commit()

    # ========================================================
    # بررسی خبر تکراری
    # ========================================================

    def exists(
        self,
        short_link
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM news
            WHERE short_link = ?
            LIMIT 1
            """,
            (
                short_link,
            )
        )

        result = cursor.fetchone()

        return result is not None

    # ========================================================
    # ذخیره خبر
    # ========================================================

    def save(
        self,
        category,
        title,
        summary,
        original_link,
        short_link,
        image_path,
        published
    ):

        now = datetime.now(
            timezone.utc
        ).isoformat()

        if isinstance(
            published,
            datetime
        ):

            published = published.isoformat()

        try:

            cursor = self.connection.cursor()

            cursor.execute(
                """
                INSERT INTO news (
                    category,
                    title,
                    summary,
                    original_link,
                    short_link,
                    image_path,
                    published,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    category,
                    title,
                    summary,
                    original_link,
                    short_link,
                    image_path,
                    published,
                    now
                )
            )

            self.connection.commit()

            return True

        except sqlite3.IntegrityError:

            print(
                "⚠️ این خبر قبلاً در دیتابیس ثبت شده است."
            )

            return False

        except Exception as e:

            print(
                f"❌ خطا در ذخیره خبر: {e}"
            )

            return False

    # ========================================================
    # آخرین اجرای موفق
    # ========================================================

    def get_last_run(self):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT value
            FROM app_state
            WHERE key = 'last_run'
            """
        )

        row = cursor.fetchone()

        if not row:

            return None

        value = row["value"]

        try:

            dt = datetime.fromisoformat(
                value
            )

            if dt.tzinfo is None:

                dt = dt.replace(
                    tzinfo=timezone.utc
                )

            return dt.astimezone(
                timezone.utc
            )

        except Exception:

            return None

    # ========================================================
    # ثبت آخرین اجرای موفق
    # ========================================================

    def set_last_run(
        self,
        value
    ):

        if isinstance(
            value,
            datetime
        ):

            value = value.isoformat()

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO app_state (
                key,
                value
            )
            VALUES ('last_run', ?)

            ON CONFLICT(key)
            DO UPDATE SET
                value = excluded.value
            """,
            (
                value,
            )
        )

        self.connection.commit()

    # ========================================================
    # بستن دیتابیس
    # ========================================================

    def close(self):

        try:

            self.connection.close()

        except Exception:
            pass