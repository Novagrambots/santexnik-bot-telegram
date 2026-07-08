from calendar import monthrange
from datetime import date, timedelta

DATE_FMT = "%d.%m.%Y"


def add_months(base: date, months: int) -> date:
    """Прибавляет месяцы к дате, корректно обрабатывая конец месяца."""
    month_index = base.month - 1 + months
    year = base.year + month_index // 12
    month = month_index % 12 + 1
    day = min(base.day, monthrange(year, month)[1])
    return date(year, month, day)


def calc_next_service_date(base_date: date, period_months: int) -> date:
    """Дата следующей профилактики от опорной даты (установка или последнее ТО)."""
    return add_months(base_date, period_months)


def parse_date(text: str) -> date | None:
    text = text.strip().replace("/", ".").replace("-", ".")
    parts = text.split(".")
    if len(parts) != 3:
        return None
    try:
        d, m, y = (int(p) for p in parts)
        if y < 100:
            y += 2000
        return date(y, m, d)
    except (ValueError, TypeError):
        return None


def fmt_date(d: date) -> str:
    return d.strftime(DATE_FMT)


def stage_name(days: int) -> str:
    return f"{days}d"


def parse_stages(raw: str) -> list[int]:
    """"14,3,0" -> [14, 3, 0] (уникальные, по убыванию, только >= 0)."""
    result: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            v = int(part)
        except ValueError:
            continue
        if v >= 0:
            result.add(v)
    return sorted(result, reverse=True)


def due_stages(next_date: date, today: date, stages: list[int]) -> list[int]:
    """Возвращает этапы (в днях), которые наступили на сегодня и раньше.

    Для просроченного оборудования срабатывает этап 0 (в день/после)."""
    days_left = (next_date - today).days
    fired: list[int] = []
    for stage in stages:
        if stage == 0:
            if days_left <= 0:
                fired.append(0)
        elif days_left == stage:
            fired.append(stage)
    return fired


__all__ = [
    "add_months",
    "calc_next_service_date",
    "parse_date",
    "fmt_date",
    "stage_name",
    "parse_stages",
    "due_stages",
    "timedelta",
]
