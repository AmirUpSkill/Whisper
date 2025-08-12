from typing import List
from pydantic import BaseModel, Field, ConfigDict, conint

class MQCItem(BaseModel):
    """A single, validated MQC item."""
    question: str
    options: List[str] = Field(..., min_length=4, max_length=4)
    correct_answer_index: conint(ge=0, le=3) # Ensures index is 0, 1, 2, or 3

class MQC(BaseModel):
    """The full MQC payload containing a list of questions."""
    model_config = ConfigDict(from_attributes=True)
    questions: List[MQCItem]
