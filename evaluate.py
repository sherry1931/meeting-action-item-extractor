"""Score extraction against annotated gold: python -m actionitems.evaluate --mode rules"""
import argparse, json, pathlib
from .pipeline import run
from .validate import jaccard

def match(preds, gold, thr=0.5):
    pairs, used = [], set()
    for g in gold:
        score, idx = max(((jaccard(p.task, g["task"]), i) for i, p in enumerate(preds) if i not in used), default=(0, None))
        if score >= thr:
            used.add(idx); pairs.append((preds[idx], g))
    return pairs, [p for i, p in enumerate(preds) if i not in used]

def evaluate(mode="rules", data="data", verbose=False):
    root = pathlib.Path(data); gold_all = json.loads((root / "gold.json").read_text())
    tp = fp = fn = own = dl = 0
    for name, gold in gold_all.items():
        preds, _ = run((root / name).read_text(), mode)
        pairs, extra = match(preds, gold)
        tp += len(pairs); fp += len(extra); fn += len(gold) - len(pairs)
        own += sum(p.owner == g.get("owner") for p, g in pairs)
        dl += sum((p.deadline.isoformat() if p.deadline else None) == g.get("deadline") for p, g in pairs)
        if verbose:
            matched = {g["task"] for _, g in pairs}
            for g in gold:
                if g["task"] not in matched: print(f"  MISSED  {name}: {g['task']}")
            for p in extra: print(f"  EXTRA   {name}: {p.task}")
    P, R = tp / max(tp + fp, 1), tp / max(tp + fn, 1)
    return {"precision": round(P, 3), "recall": round(R, 3), "f1": round(2 * P * R / max(P + R, 1e-9), 3),
            "owner_acc": round(own / max(tp, 1), 3), "deadline_acc": round(dl / max(tp, 1), 3), "matched": tp, "gold": tp + fn}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", default="rules"); ap.add_argument("--data", default="data")
    a = ap.parse_args(); print(evaluate(a.mode, a.data, verbose=True))
