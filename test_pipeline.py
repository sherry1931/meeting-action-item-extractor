from datetime import date
from actionitems.evaluate import evaluate
from actionitems.extract_rules import extract
from actionitems.preprocess import Turn
from actionitems.schema import ActionItem
from actionitems.validate import validate

REF = date(2026, 10, 12)

def test_baseline_quality():
    r = evaluate("rules", "data")
    assert r["f1"] >= 0.9 and r["owner_acc"] >= 0.9 and r["deadline_acc"] >= 0.9

def test_missing_owner_flagged():
    it = validate([ActionItem("Update the roadmap deck", None, None, confidence=0.55)], REF)[0]
    assert "missing_owner" in it.flags and it.confidence < 0.55

def test_duplicates_merged():
    a = ActionItem("Send the revised copy to legal", "Sam", None, confidence=0.7)
    b = ActionItem("Send revised copy to legal", "Sam", date(2026, 10, 13), confidence=0.85)
    out = validate([a, b], REF)
    assert len(out) == 1 and out[0].deadline == date(2026, 10, 13)

def test_past_and_invalid_dates():
    assert "deadline_in_past" in validate([ActionItem("Pay the invoice now", "Ann", date(2026, 9, 1))], REF)[0].flags
    bad = extract([Turn("Ann", "I'll file the report by Feb 30.")], REF)[0]
    assert "invalid_date" in bad.flags and bad.deadline is None
