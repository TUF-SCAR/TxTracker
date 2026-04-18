import sqlite3
import time
from datetime import date, datetime, timedelta


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
        item = self._normalize_text(item)
        note = self._normalize_text(note)

        with self.connect() as connect:
            current = connect.execute(
                """
                INSERT INTO transactions
                (date, time, item, amount, note, created_at_ms, deleted)
                VALUES (?, ?, ?, ?, ?, ?, 0)
                """,
                (date_str, time_str, item, amount, note, created_at_ms),
            )
            connect.commit()
        return current.lastrowid

    def list_txns(self):
        with self.connect() as connect:
            rows = connect.execute(
                """
                SELECT id, date, time, item, amount, note
                FROM transactions
                WHERE deleted = 0
                ORDER BY date DESC, time DESC, id DESC
                """
            ).fetchall()
            return [dict(r) for r in rows]

    def soft_delete(self, txn_id):
        with self.connect() as connect:
            connect.execute(
                "UPDATE transactions SET deleted = 1 WHERE id = ?",
                (txn_id,),
            )
            connect.commit()

    def hard_delete(self, txn_id: int):
        with self.connect() as connect:
            connect.execute("DELETE FROM transactions WHERE id = ?", (txn_id,))
            connect.commit()

    def undo_delete(self, txn_id):
        with self.connect() as connect:
            connect.execute(
                "UPDATE transactions SET deleted = 0 WHERE id = ?",
                (txn_id,),
            )
            connect.commit()

    def transaction_exists(self, date_str, time_str, item, amount, note):
        item = self._normalize_text(item)
        note = self._normalize_text(note)

        with self.connect() as connect:
            row = connect.execute(
                """
                SELECT 1
                FROM transactions
                WHERE date = ?
                  AND time = ?
                  AND item = ?
                  AND amount = ?
                  AND note = ?
                LIMIT 1
                """,
                (date_str, time_str, item, amount, note),
            ).fetchone()
            return row is not None

    def _normalize_text(self, value) -> str:
        return str(value or "").strip()

    def _is_valid_date(self, value: str) -> bool:
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except Exception:
            return False

    def _is_valid_time(self, value: str) -> bool:
        try:
            datetime.strptime(value, "%H:%M")
            return True
        except Exception:
            return False

    def _is_valid_import_row(self, tx: dict):
        if not isinstance(tx, dict):
            return False, None

        date_str = self._normalize_text(tx.get("date", ""))
        time_str = self._normalize_text(tx.get("time", ""))
        item = self._normalize_text(tx.get("item", ""))
        note = self._normalize_text(tx.get("note", ""))

        try:
            raw_amount = tx.get("amount", 0)
            amount = abs(int(raw_amount))
        except Exception:
            return False, None

        if not date_str or not time_str or not item or amount <= 0:
            return False, None

        if not self._is_valid_date(date_str):
            return False, None

        if not self._is_valid_time(time_str):
            return False, None

        return True, {
            "date": date_str,
            "time": time_str,
            "item": item,
            "amount": amount,
            "note": note,
        }

    def import_transactions(self, transactions, skip_duplicates=True):
        imported_count = 0
        skipped_count = 0

        with self.connect() as connect:
            existing_keys = set()

            if skip_duplicates:
                existing_rows = connect.execute(
                    """
                    SELECT date, time, item, amount, note
                    FROM transactions
                    """
                ).fetchall()

                for row in existing_rows:
                    existing_keys.add(
                        (
                            row["date"],
                            row["time"],
                            row["item"],
                            row["amount"],
                            row["note"],
                        )
                    )

            for tx in transactions:
                valid, cleaned = self._is_valid_import_row(tx)
                if not valid:
                    skipped_count += 1
                    continue

                tx_key = (
                    cleaned["date"],
                    cleaned["time"],
                    cleaned["item"],
                    cleaned["amount"],
                    cleaned["note"],
                )

                if skip_duplicates and tx_key in existing_keys:
                    skipped_count += 1
                    continue

                try:
                    created_at_ms = int(time.time() * 1000)

                    connect.execute(
                        """
                        INSERT INTO transactions
                        (date, time, item, amount, note, created_at_ms, deleted)
                        VALUES (?, ?, ?, ?, ?, ?, 0)
                        """,
                        (
                            cleaned["date"],
                            cleaned["time"],
                            cleaned["item"],
                            cleaned["amount"],
                            cleaned["note"],
                            created_at_ms,
                        ),
                    )

                    if skip_duplicates:
                        existing_keys.add(tx_key)

                    imported_count += 1

                except Exception:
                    skipped_count += 1

            connect.commit()

        return imported_count, skipped_count

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

    def week_daily_totals(self, week_start: date):
        start_str = week_start.strftime("%Y-%m-%d")
        end_str = (week_start + timedelta(days=7)).strftime("%Y-%m-%d")

        with self.connect() as connect:
            rows = connect.execute(
                """
                SELECT date, COALESCE(SUM(amount), 0) AS total
                FROM transactions
                WHERE deleted = 0
                  AND date >= ?
                  AND date < ?
                GROUP BY date
                """,
                (start_str, end_str),
            ).fetchall()

        totals_by_date = {r["date"]: int(r["total"]) for r in rows}
        out = []
        for i in range(7):
            d = (week_start + timedelta(days=i)).strftime("%Y-%m-%d")
            out.append(totals_by_date.get(d, 0))
        return out

    def month_daily_totals(self, month_start: date):
        year = month_start.year
        month = month_start.month

        if month == 12:
            next_month_start = date(year + 1, 1, 1)
        else:
            next_month_start = date(year, month + 1, 1)

        start_str = month_start.strftime("%Y-%m-%d")
        end_str = next_month_start.strftime("%Y-%m-%d")

        with self.connect() as connect:
            rows = connect.execute(
                """
                SELECT date, COALESCE(SUM(amount), 0) AS total
                FROM transactions
                WHERE deleted = 0
                  AND date >= ?
                  AND date < ?
                GROUP BY date
                """,
                (start_str, end_str),
            ).fetchall()

        totals_by_date = {r["date"]: int(r["total"]) for r in rows}
        out = []
        current_date = month_start
        while current_date < next_month_start:
            d_str = current_date.strftime("%Y-%m-%d")
            out.append(totals_by_date.get(d_str, 0))
            current_date += timedelta(days=1)
        return out

    def year_monthly_totals(self, year_start: date):
        year = year_start.year
        next_year_start = date(year + 1, 1, 1)

        start_str = year_start.strftime("%Y-%m-%d")
        end_str = next_year_start.strftime("%Y-%m-%d")

        with self.connect() as connect:
            rows = connect.execute(
                """
                SELECT SUBSTR(date, 1, 7) AS month, COALESCE(SUM(amount), 0) AS total
                FROM transactions
                WHERE deleted = 0
                  AND date >= ?
                  AND date < ?
                GROUP BY month
                """,
                (start_str, end_str),
            ).fetchall()

        totals_by_month = {r["month"]: int(r["total"]) for r in rows}
        out = []
        for month in range(1, 13):
            month_str = f"{year}-{month:02d}"
            out.append(totals_by_month.get(month_str, 0))
        return out
