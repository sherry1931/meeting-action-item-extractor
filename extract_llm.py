"""LLM extractor (OpenAI). Output is parsed defensively and re-validated downstream."""
import json, os
from datetime import date
from .schema import ActionItem

SYSTEM = """Extract action items from the meeting transcript. Return JSON only:
{"items":[{"task":"imperative phrase","owner":"name or null","deadline":"YYYY-MM-DD or null","confidence":0.0-1.0,"evidence":"short quote"}]}
Include only commitments or assignments, not discussion. Resolve relative dates against the meeting date.
Use null when the owner or deadline is not stated. Never guess."""

def extract(turns, ref, model=None):
    from openai import OpenAI
    transcript = "\n".join(f"{t.speaker}: {t.sentence}" for t in turns)
    r = OpenAI().chat.completions.create(
        model=model or os.getenv("CHAT_MODEL", "gpt-4o-mini"), temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": f"Meeting date: {ref} ({ref:%A})\n\n{transcript}"}])
    items = []
    for d in json.loads(r.choices[0].message.content).get("items", []):
        flags = []
        try:
            dl = date.fromisoformat(d["deadline"]) if d.get("deadline") else None
        except ValueError:
            dl, flags = None, ["invalid_date"]
        if str(d.get("task", "")).strip():
            items.append(ActionItem(d["task"].strip(), d.get("owner") or None, dl,
                                    confidence=float(d.get("confidence", 0.6)), evidence=d.get("evidence", ""), flags=flags))
    return items
