"""Resolve deadline phrases against the meeting date."""
import re
from datetime import date, timedelta

MON = r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
MONTHS = {m: i + 1 for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split())}
DAYS = "monday tuesday wednesday thursday friday saturday sunday".split()
PATTERNS = [
    ("iso", re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")),
    ("md", re.compile(r"\b" + MON + r"\.?\s+(\d{1,2})(?:st|nd|rd|th)?\b", re.I)),
    ("dm", re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?" + MON + r"\b", re.I)),
    ("rel", re.compile(r"\b(today|tomorrow|end of (?:the )?week|eow|end of (?:the )?month|eom|next week)\b", re.I)),
    ("day", re.compile(r"\b(next\s+)?(" + "|".join(DAYS) + r")\b", re.I)),
]

def _resolve(kind, g, ref):
    if kind == "iso": return date(int(g[0]), int(g[1]), int(g[2]))
    if kind == "md": return date(ref.year, MONTHS[g[0][:3].lower()], int(g[1]))
    if kind == "dm": return date(ref.year, MONTHS[g[1][:3].lower()], int(g[0]))
    if kind == "rel":
        w = g[0].lower()
        if w == "today": return ref
        if w == "tomorrow": return ref + timedelta(1)
        if w == "next week": return ref + timedelta(7)
        if w == "eow" or ("week" in w and w.startswith("end")):
            return ref + timedelta((4 - ref.weekday()) % 7)
        return date(ref.year + (ref.month == 12), ref.month % 12 + 1, 1) - timedelta(1)
    d = ref + timedelta((DAYS.index(g[1].lower()) - ref.weekday() - 1) % 7 + 1)
    return d + timedelta(7) if g[0] and d < ref + timedelta(7 - ref.weekday()) else d

def parse_deadline(text, ref):
    """Return (date | None, matched text | None, is_invalid)."""
    for kind, rx in PATTERNS:
        m = rx.search(text)
        if m:
            try:
                return _resolve(kind, m.groups(), ref), m.group(0), False
            except ValueError:               # e.g. "Feb 30"
                return None, m.group(0), True
    return None, None, False
