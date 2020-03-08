###########
# Schemas #
###########

from pydantic import BaseModel
from typing import List

# Schema for API
class Records(BaseModel):
    records: List[str] = []
    uids: List[str] = []
    retina_name: str

class RetinaSpec(BaseModel):
    retina_name: str

class SimilarTerms(BaseModel):
    retina_name: str
    num_terms: int
    fingerprint: List[int] = []