
from __future__ import annotations

from copy import deepcopy

from enum import auto, Enum
from uuid import UUID

from .base import Entity
from .values import AUD, Balance


class TransactionStatus(Enum):
    """An enum representing the status of a transaction."""

    # The transfer of money has been requested but is not final.
    PENDING = auto()
    # The transfer of money has been finalised.
    SETTLED = auto()


class TransactionType(Enum):
    """An enum representing the type of a transaction."""

    # Money is being transferred into an account.
    CREDIT = auto()
    # Money is being transferred out of an account.
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
        """Adjust a balance object by the amount of this transaction.

        Takes one argument:
        - The balance to be adjusted.

        Returns a new balance object.

        """

        if self.status == TransactionStatus.PENDING:
            adjustment = Balance(pending=self.amount)
        else:
            adjustment = Balance(available=self.amount)

        if self.type == TransactionType.DEBIT:
            adjustment = -adjustment

        return balance + adjustment

    def settle(self) -> None:
        if self.status != TransactionStatus.PENDING:
            raise RuntimeError('Cannot settle a transaction which is not '
                               'pending.')

        self.status = TransactionStatus.SETTLED
