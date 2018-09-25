
from __future__ import annotations

from copy import deepcopy

from enum import auto, Enum
from uuid import UUID

from .base import Entity
from .values import AUD, Balance


class TransactionStatus(Enum):
    PENDING = auto()
    SETTLED = auto()


class TransactionType(Enum):
    CREDIT = auto()
    DEBIT = auto()


class Transaction(Entity):
    def __init__(self,
                 id: UUID = None,
                 reference: UUID = None,
                 amount: AUD = None,
                 type: TransactionType = None,
                 status: TransactionStatus = TransactionStatus.PENDING) -> None:  # noqa
        super(Transaction, self).__init__(id=id)

        if reference is None:
            raise ValueError('Cannot create a transaction without a '
                             'reference.')

        self.reference = reference

        if type is None:
            raise ValueError('Transaction type must be specified.')

        self.amount = amount if amount is not None else AUD('0')
        self.type = type
        self.status = status

    def __copy__(self) -> Transaction:  # noqa
        return type(self)(id=self.id, amount=self.amount, type=self.type,
                          status=self.status)

    def __deepcopy__(self, memo) -> Transaction: # noqa
        self_id = id(self)
        if self_id in memo:
            return memo[self_id]

        new_id = deepcopy(self.id)
        new_amount = deepcopy(self.amount)
        new_type = deepcopy(self.type)
        new_reference = deepcopy(self.reference)
        new_status = deepcopy(self.status)
        new_transaction = type(self)(id=new_id, amount=new_amount,
                                     type=new_type, reference=new_reference,
                                     status=new_status)

        return new_transaction

    def adjust(self, balance) -> Balance:
        """Adjust a balance object by the amount of this transaction."""

        if self.status == TransactionStatus.PENDING:
            adjustment = Balance(available=AUD('0'), pending=self.amount)
        else:
            adjustment = Balance(available=self.amount, pending=AUD('0'))

        if self.type == TransactionType.DEBIT:
            adjustment = -adjustment

        return balance + adjustment
