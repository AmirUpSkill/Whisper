from pydantic import BaseModel, ConfigDict

class Summary(BaseModel):
    """Schema for the AI-generated summary."""
    model_config = ConfigDict(from_attributes=True)
    content: str
