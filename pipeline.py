from . import preprocess
from .validate import validate

def run(text, mode="rules"):
    """transcript text -> (validated ActionItems, meeting date)"""
    ref, turns = preprocess.meeting_date(text), preprocess.segment(text)
    if mode == "llm":
        from .extract_llm import extract
    else:
        from .extract_rules import extract
    return validate(extract(turns, ref), ref, {t.speaker for t in turns}), ref
