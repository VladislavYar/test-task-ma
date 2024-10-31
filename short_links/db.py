import sqlite3


class DataBase:
    """База данных.

    Attributes:
         db_name (str): название базы данных.
         table_name (str): название таблицы.
    """

    db_name = "short_links.sqlite"
    table_name = "link"

    def __init__(self):
        """Инициализация базы данных."""
        connect = sqlite3.connect(self.db_name)
        cursor = connect.cursor()
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
        id INTEGER PRIMARY KEY,
        original_url TEXT NOT NULL,
        short_link TEXT NOT NULL
        )
        """)
        connect.commit()
        connect.close()

    def get_original_url(self, short_link: str) -> str | None:
        """Отдаёт оригинальную ссылку.

        Args:
            short_link (str): короткая ссылка.

        Returns:
            str | None: оригинальная ссылка.
        """
        connect = sqlite3.connect(self.db_name)
        cursor = connect.cursor()

        cursor.execute(
            f"""
            SELECT original_url FROM {self.table_name}
            WHERE short_link = ?
            """,
            (short_link,),
        )
        if original_url := cursor.fetchone():
            connect.close()
            return original_url[0]
        connect.close()

    def _get_short_link(self, original_url: str) -> str | None:
        """Отдаёт короткую ссылку.

        Args:
            original_url (str): оригинальная ссылка.

        Returns:
            str | None: короткая ссылка.
        """
        connect = sqlite3.connect(self.db_name)
        cursor = connect.cursor()

        cursor.execute(
            f"""
            SELECT short_link FROM {self.table_name}
            WHERE original_url = ?
            """,
            (original_url,),
        )
        if short_link := cursor.fetchone():
            connect.close()
            return short_link[0]
        connect.close()

    def save_short_link(
        self,
        original_url: str,
        short_link: str,
    ) -> None:
        """Сохраняет короткую ссылку.

        Args:
            original_url (str): оригинальная ссылка.
            short_link (str): короткая ссылка.
        """
        if self._get_short_link(original_url):
            return
        connect = sqlite3.connect(self.db_name)
        cursor = connect.cursor()
        cursor.execute(
            "INSERT INTO link(original_url, short_link) VALUES (?, ?)",
            (original_url, short_link),
        )
        connect.commit()
        connect.close()
