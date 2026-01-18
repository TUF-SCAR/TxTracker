from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta


def rupees_to_paise(text):
    x = (text or "").strip().replace("₹", "")
    if not x:
        raise ValueError("Amount is empty")

    decimal = Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    paise = int(decimal * 100)
    if paise > 0:
        paise = -paise
    return paise


def paise_to_rupees(paise):
    decimal = Decimal(paise) / Decimal(100)
    return f"{decimal:.2f}"


def start_of_day(date_time):
    return date_time.replace(hour=0, minute=0, second=0, microsecond=0)


def start_of_week(date_time):
    day = start_of_day(date_time)
    return day - timedelta(days=day.weekday())


def start_of_month(date_time):
    day = start_of_day(date_time)
    return day.replace(day=1)


def start_of_year(date_time):
    day = start_of_day(date_time)
    return day.replace(month=1, day=1)


def date_time_to_ms(date_time):
    return int(date_time.timestamp() * 1000)
