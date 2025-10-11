from pydantic import BaseModel

class PSGMatchInfo(BaseModel):
    date: str
    venue: str
    opponent: str
    competition: str

    def to_string(self) -> str:
        return f"  • {self.date} — {self.venue} vs {self.opponent} ({self.competition})"
