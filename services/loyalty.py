"""Чистые функции программы лояльности (кешбэк-бонусы)."""


def earned_for(total_paid: int, threshold: int, bonus: int) -> int:
    """Сколько всего бонусов заслужено при суммарной оплате total_paid."""
    if threshold <= 0:
        return 0
    return (total_paid // threshold) * bonus


def progress_to_next(total_paid: int, threshold: int) -> int:
    """Сколько сум осталось оплатить до следующего начисления."""
    if threshold <= 0:
        return 0
    return threshold - (total_paid % threshold)


def format_money(n: int) -> str:
    """12345678 -> '12 345 678'."""
    return f"{n:,}".replace(",", " ")


def parse_money(text: str) -> int | None:
    """'20 000 000' / '20000000' -> 20000000; мусор -> None."""
    cleaned = text.strip().replace(" ", "").replace("'", "").replace(" ", "")
    if not cleaned.isdigit():
        return None
    return int(cleaned)
