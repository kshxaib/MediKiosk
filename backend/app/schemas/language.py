"""Language Pydantic schemas."""
from pydantic import BaseModel, ConfigDict


class LanguageRead(BaseModel):
    code: str
    name: str
    native_name: str
    is_default: bool = False
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)
