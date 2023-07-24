from typing import List, Optional
from pydantic import BaseModel, validator
from datetime import datetime
from .transactions import transaction_processor


class Transaction(BaseModel):
    date: str
    package_size: str
    carrier: str

    @validator('date')
    def validate_date(cls, value):
        # Convert the date string to a datetime object for comparison
        date_obj = datetime.strptime(value, "%Y-%m-%d")

        # Check if the date is earlier than 2010
        if date_obj.year < 2010:
            raise ValueError("Transactions older than 2010 are not supported")
        return value

    @validator('carrier')
    def validate_carrier(cls, value):
        # check if the carrier is enabled
        if not transaction_processor.is_carrier_enabled(value):
            raise ValueError(f"Carrier with code '{value}' is disabled")
        return value


# {
#   "reduced_price": "string",
#   "applied_discount": "string or null"
# }
class ProcessedTransaction(BaseModel):
    reduced_price: str
    applied_discount: Optional[str] = None


class Carrier(BaseModel):
    code: str
    enabled: bool

    @validator('code')
    def validate_carrier(cls, value):
        # check if the carrier exists
        if not transaction_processor.get_carrier(value):
            raise ValueError(f"Carrier with code {value} not found")
        return value


class CarriersList(BaseModel):
    carriers: List[Carrier]
