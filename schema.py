from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Optional

@dataclass
class ActionItem:
    task: str
    owner: Optional[str] = None
    deadline: Optional[date] = None
    status: str = "open"
    confidence: float = 0.5
    evidence: str = ""
    flags: list = field(default_factory=list)

    def to_dict(self):
        d = asdict(self)
        d["deadline"] = self.deadline.isoformat() if self.deadline else None
        d["confidence"] = round(self.confidence, 2)
        return d
