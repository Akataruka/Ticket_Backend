from pydantic import BaseModel, Field
from typing import Optional

# Ticket Model
class Ticket(BaseModel):
    code: str = Field(..., example="TICKET123")
    validated_status: bool = Field(False, example=False)
    