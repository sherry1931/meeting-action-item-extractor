"""Validation rules: missing owners, bad/past dates, duplicate tasks."""
import re
from datetime import timedelta

NOISE = {"the", "a", "an", "to", "of", "for", "with", "it", "and"}

def _toks(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in NOISE}

def jaccard(a, b):
    A, B = _toks(a), _toks(b)
    return len(A & B) / len(A | B) if A | B else 0.0

def validate(items, ref, speakers=()):
    out = []
    for it in items:
        if not it.owner:
            it.flags.append("missing_owner"); it.confidence -= 0.15
        elif speakers and it.owner not in speakers:
            it.flags.append("owner_not_in_meeting")
        if it.deadline is None:
            it.flags.append("missing_deadline")
        elif it.deadline < ref:
            it.flags.append("deadline_in_past"); it.confidence -= 0.2
        elif it.deadline > ref + timedelta(365):
            it.flags.append("deadline_over_1_year")
        dup = next((i for i, o in enumerate(out) if jaccard(o.task, it.task) >= 0.7
                    and (o.owner == it.owner or not o.owner or not it.owner)), None)
        if dup is not None:                      # merge duplicates, keep the more confident one
            a, b = out[dup], it
            best, other = (b, a) if b.confidence > a.confidence else (a, b)
            best.owner, best.deadline = best.owner or other.owner, best.deadline or other.deadline
            best.flags = sorted(set(best.flags + ["merged_duplicate"]) - ({"missing_owner"} if best.owner else set()))
            out[dup] = best
        else:
            out.append(it)
    for it in out:
        it.confidence = round(max(0.05, min(0.99, it.confidence)), 2)
    return out
