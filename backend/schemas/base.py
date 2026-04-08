from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AppBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        json_encoders={Decimal: lambda value: float(value)},
    )
