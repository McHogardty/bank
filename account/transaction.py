
from __future__ import annotations

from copy import deepcopy

from enum import auto, Enum
from uuid import UUID

from .base import Entity
from .values import AUD


class TransactionType(Enum):
    CREDIT = auto()
    DEBIT = auto()


class Transaction(Entity):
    def __init__(self, id: UUID = None, reference: UUID = None,
                 amount: AUD = None, type: TransactionType = None) -> None:
        super(Transaction, self).__init__(id=id)

        if reference is None:
            raise ValueError('Cannot create a transaction without a '
                             'reference.')

        self.reference = reference

        if type is None:
            raise ValueError('Transaction type must be specified.')

        self.amount = amount if amount is not None else AUD('0')
        self.type = type

    def __copy__(self) -> Transaction:  # noqa
        return type(self)(id=self.id, amount=self.amount, type=self.type)

    def __deepcopy__(self, memo) -> Transaction: # noqa
        self_id = id(self)
        if self_id in memo:
            return memo[self_id]

        new_id = deepcopy(self.id)
        new_amount = deepcopy(self.amount)
        new_type = deepcopy(self.type)
        new_reference = deepcopy(self.reference)
        new_transaction = type(self)(id=new_id, amount=new_amount,
                                     type=new_type, reference=new_reference)

        return new_transaction
