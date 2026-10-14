"""Offline rule-based extractor (also the baseline to compare the LLM against)."""
import re
from .dates import parse_deadline
from .schema import ActionItem

STOP = set("okay ok thanks thank great sure yes no so well also we they it this that there then the a i you please let and but maybe if hello hi morning good alright understood next last".split())
ADDR = re.compile(r"^([A-Z][a-z]+),\s+(.*)$")
CUE_ADDR = re.compile(r"^(?:you(?:'ll| will| should| need to| must| have to)|should|need to|must|have to|please|(?:can|could|would|will) you)\s+", re.I)
COMMIT = re.compile(r"\b(?:I'll|I will|I can take|I'm going to|I am going to|let me)\s+", re.I)
NAMEWILL = re.compile(r"\b([A-Z][a-z]+)\s+(will|is going to|to)\s+")
GENERIC = re.compile(r"\b(?:need to|needs to|have to|has to|should|must|please|action item:?|make sure(?: to)?)\s+", re.I)

def extract(turns, ref):
    speakers = {t.speaker for t in turns}
    items = []
    for t in turns:
        s, owner, task, conf = t.sentence, None, None, 0.0
        m = ADDR.match(s)
        if m and m.group(1).lower() not in STOP and (c := CUE_ADDR.match(m.group(2))):
            owner, task, conf = m.group(1), m.group(2)[c.end():], 0.85      # "Sam, can you ..."
        elif (c := COMMIT.search(s)):
            owner, task, conf = t.speaker, s[c.end():], 0.85                 # "I'll ..."
        else:
            for n in NAMEWILL.finditer(s):                                    # "Lena will ..."
                if n.group(1).lower() in STOP or (n.group(2) == "to" and n.group(1) not in speakers):
                    continue
                owner, task, conf = n.group(1), s[n.end():], 0.8
                break
            if not task and (c := GENERIC.search(s)):                         # "we need to ..." (no owner)
                task, conf = s[c.end():], 0.55
        if not task:
            continue
        deadline, span, bad = parse_deadline(s, ref)
        if span:
            task = re.sub(r"\s*\b(?:by|on|before|until|due|for)?\s*" + re.escape(span), "", task, flags=re.I)
        task = task.strip(" .?!,;")
        if len(task.split()) < 2:
            continue
        task = task[0].upper() + task[1:]
        items.append(ActionItem(task, owner, deadline, confidence=min(conf + (0.1 if deadline else 0), 0.95),
                                evidence=f"{t.speaker}: {s}", flags=["invalid_date"] if bad else []))
    return items
