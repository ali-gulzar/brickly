from enum import Enum


class SaleStatus(str, Enum):
    pending = "pending"
    completed = "completed"
