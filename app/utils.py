# Utility functions for the TxTracker app, including currency conversion, date formatting and parsing, and time formatting.

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date, timedelta


def rupees_to_paise(text):
    x = (text or "").strip().replace("₹", "")
    if not x:
        raise ValueError("Amount is empty")

    decimal = Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    paise = int(decimal * 100)

    if paise <= 0:
        raise ValueError("Amount must be more than 0")

    return paise


def paise_to_rupees(paise):
    decimal = Decimal(paise) / Decimal(100)
    return f"{decimal:.2f}"


def today_date_str():
    return date.today().strftime("%Y-%m-%d")


def date_to_str(d: date) -> str:
    return d.strftime("%Y-%m-%d")


def str_to_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def start_of_week_sun(d: date) -> date:
    days_since_sun = (d.weekday() + 1) % 7
    return d - timedelta(days=days_since_sun)


def start_of_month(d: date) -> date:
    return d.replace(day=1)


def start_of_year(d: date) -> date:
    return d.replace(month=1, day=1)


def time_24_to_12(time_str: str) -> str:
    hh, mm = time_str.split(":")
    h = int(hh)
    m = int(mm)

    suffix = "AM"
    if h >= 12:
        suffix = "PM"

    h12 = h % 12
    if h12 == 0:
        h12 = 12

    return f"{h12}:{m:02d} {suffix}"
