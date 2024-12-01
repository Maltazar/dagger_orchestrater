from pydantic import BaseModel


class SecretModel(BaseModel):
    name: str
    location: str
