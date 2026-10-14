from fastapi import FastAPI
from pydantic import BaseModel
from .pipeline import run

app = FastAPI(title="Meeting Action-Item Extractor")

class Req(BaseModel):
    transcript: str
    mode: str = "rules"

@app.post("/extract")
def extract(r: Req):
    items, ref = run(r.transcript, r.mode)
    return {"meeting_date": ref.isoformat(), "items": [i.to_dict() for i in items]}
