from decimal import Decimal, ROUND_HALF_UP


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
