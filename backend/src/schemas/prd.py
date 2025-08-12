from pydantic import BaseModel, ConfigDict

class LoveablePRD(BaseModel):
    """Schema for the AI-generated Loveable PRD."""
    model_config = ConfigDict(from_attributes=True)
    content: str
