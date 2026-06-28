"""In-memory resume storage service (swap with DB in production)"""

from typing import Dict, Optional, List
from src.models.resume import ResumeData


class ResumeService:
    """Simple in-memory store. Replace with DynamoDB/RDS in production."""

    _store: Dict[str, ResumeData] = {}

    def save(self, resume_id: str, data: ResumeData) -> ResumeData:
        self._store[resume_id] = data
        return data

    def get(self, resume_id: str) -> Optional[ResumeData]:
        return self._store.get(resume_id)

    def list_all(self) -> List[dict]:
        return [
            {"id": rid, "name": r.contact.full_name, "template": r.template}
            for rid, r in self._store.items()
        ]

    def delete(self, resume_id: str) -> bool:
        if resume_id in self._store:
            del self._store[resume_id]
            return True
        return False
