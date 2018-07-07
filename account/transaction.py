
from decimal import Decimal
from enum import auto, Enum
from uuid import UUID

from .base import Entity

class TransactionType(Enum):
	CREDIT = auto()
	DEBIT = auto()


class Transaction(Entity):
    def __init__(self, id: UUID = None, amount: Decimal = None,
    			 type: TransactionType = None) -> None:
        super(Transaction, self).__init__(id=id)

        if type is None:
        	raise ValueError('Transaction type must be specified.')

        self.amount = amount if amount is not None else Decimal('0')
        self.type = type