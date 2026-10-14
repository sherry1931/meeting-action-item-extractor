"""Clean a transcript and segment it by speaker and sentence."""
import re
from dataclasses import dataclass
from datetime import date

FILLER = re.compile(r"\b(?:um+|uh+|erm|you know|i mean)\b,?\s*", re.I)
LINE = re.compile(r"^\s*(?:\[?\d{1,2}:\d{2}(?::\d{2})?\]?\s*)?([A-Z][\w.'-]*(?: [A-Z][\w.'-]*)?):\s*(.+)$")
SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'])")
HEAD = re.compile(r"meeting date:\s*(\d{4}-\d{2}-\d{2})", re.I)

@dataclass
class Turn:
    speaker: str
    sentence: str

def meeting_date(text, default=None):
    m = HEAD.search(text)
    return date.fromisoformat(m.group(1)) if m else (default or date.today())

def segment(text):
    turns = []
    for line in text.splitlines():
        m = LINE.match(line)
        if not m:
            continue
        speaker, body = m.groups()
        for s in SENT.split(FILLER.sub("", body).strip()):
            if s.strip():
                turns.append(Turn(speaker, s.strip()))
    return turns
