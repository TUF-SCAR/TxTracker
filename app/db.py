import sqlite3
import time


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
            date_time_ms INTEGER NOT NULL,
            item TEXT NOT NULL,
            amount INTEGER NOT NULL,
            note TEXT NOT NULL DEFAULT ' ',
            created_at_ms INTEGER NOT NULL,
            deleted INTEGER NOT NULL DEFAULT 0
            );
            """
            )

            connect.execute(
                "CREATE INDEX IF NOT EXISTS idx_tx_dt ON transactions(date_time_ms);"
            )
            connect.commit()

    def add_transaction(self, date_time_ms, item, amount, note):
        if amount > 0:
            amount = -amount

        created_at_ms = int(time.time() * 1000)

        with self.connect() as connect:
            current = connect.execute(
                "INSERT INTO transactions (date_time_ms, item, amount, note, created_at_ms, deleted) VALUES (?, ?, ?, ?, ?, 0)",
                (date_time_ms, item, amount, note, created_at_ms),
            )
            connect.commit()

        return current.lastrowid

    def list_txns(self):
        with self.connect() as connect:
            rows = connect.execute(
                "SELECT id, date_time_ms, item, amount, note FROM transactions WHERE deleted = 0 ORDER BY date_time_ms DESC, id DESC"
            ).fetchall()
            return [dict(r) for r in rows]

    def soft_delete(self, txn_id):
        with self.connect() as connect:
            connect.execute(
                "UPDATE transactions SET deleted = 1 WHERE id = ?", (txn_id,)
            )
            connect.commit()

    def undo_delete(self, txn_id):
        with self.connect() as connect:
            connect.execute(
                "UPDATE transactions SET deleted = 0 WHERE id = ?", (txn_id,)
            )
            connect.commit()

    def sum_between(self, start, end):
        with self.connect() as connect:
            row = connect.execute(
                """
                SELECT COALESCE(SUM(amount), 0)
                FROM transactions
                WHERE date_time_ms BETWEEN ? AND ?
                AND deleted = 0
                """,
                (start, end),
            ).fetchone()
            return int(row[0])
