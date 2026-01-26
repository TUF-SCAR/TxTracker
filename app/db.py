import time
import sqlite3


class DataBase:
    def __init__(self, path="txtracker.sqlite3"):
        self.path = path

    def connect(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def init_database(self):
        with self.connect() as connect:
            connect.execute(
                """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                item TEXT NOT NULL,
                amount INTEGER NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                created_at_ms INTEGER NOT NULL,
                deleted INTEGER NOT NULL DEFAULT 0
            );
            """
            )

            connect.execute(
                "CREATE INDEX IF NOT EXISTS idx_tx_date_time ON transactions(date, time);"
            )
            connect.commit()

    def add_transaction(self, date_str, time_str, item, amount, note):
        created_at_ms = int(time.time() * 1000)
        with self.connect() as connect:
            current = connect.execute(
                "INSERT INTO transactions (date, time, item, amount, note, created_at_ms, deleted) VALUES (?, ?, ?, ?, ?, ?, 0)",
                (date_str, time_str, item, amount, note, created_at_ms),
            )
            connect.commit()
        return current.lastrowid

    def list_txns(self):
        with self.connect() as connect:
            rows = connect.execute(
                "SELECT id, date, time, item, amount, note FROM transactions WHERE deleted = 0 ORDER BY date DESC, time DESC, id DESC"
            ).fetchall()
            return [dict(r) for r in rows]

    def soft_delete(self, txn_id):
        with self.connect() as connect:
            connect.execute(
                "UPDATE transactions SET deleted = 1 WHERE id = ?", (txn_id,)
            )
            connect.commit()

    def hard_delete(self, txn_id: int):
        with self.connect() as connect:
            connect.execute("DELETE FROM transactions WHERE id = ?", (txn_id,))
            connect.commit()

    def undo_delete(self, txn_id):
        with self.connect() as connect:
            connect.execute(
                "UPDATE transactions SET deleted = 0 WHERE id = ?", (txn_id,)
            )
            connect.commit()

    def sum_between_dates(self, start_date, end_date):
        with self.connect() as connect:
            row = connect.execute(
                """
                SELECT COALESCE(SUM(amount), 0)
                FROM transactions
                WHERE deleted = 0
                AND date >= ?
                AND date < ?
                """,
                (start_date, end_date),
            ).fetchone()
            return int(row[0])
