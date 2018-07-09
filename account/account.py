
from __future__ import annotations

from copy import deepcopy
from typing import List
from uuid import UUID

from .base import Entity
from .transaction import Transaction, TransactionType
from .values import AUD


class Account(Entity):
    class InsufficientBalance(Exception):
        pass

    def __init__(self, id: UUID = None, owner: UUID = None,
                 balance: AUD = None) -> None:
        super(Account, self).__init__(id=id)

        if owner is None:
            raise ValueError("An account must have an owner.")

        self.transactions: List[Transaction] = []
        self.balance = AUD('0') if balance is None else balance
        self.owner = owner
        self.can_overdraw = False

    def __copy__(self) -> Account:
        new_copy = type(self)(id=self.id, owner=self.owner)
        new_copy.balance = self.balance
        new_copy.transactions = self.transactions

        return new_copy

    def __deepcopy__(self, memo) -> Account:
        self_id = id(self)
        if self_id in memo:
            return memo[self_id]

        new_id = deepcopy(self.id)
        new_owner = deepcopy(self.owner)
        new_account = type(self)(id=new_id, owner=new_owner)
        new_account.balance = deepcopy(self.balance)
        new_account.transactions = deepcopy(self.transactions)

        return new_account

    def _add_transaction(self, transaction: Transaction) -> None:
        self.transactions.append(transaction)

        if transaction.type == TransactionType.CREDIT:
            self.balance += transaction.amount
        else:
            self.balance -= transaction.amount

    def _can_debit(self, amount: AUD) -> bool:
        raise NotImplementedError

    def debit(self, amount: AUD) -> None:
        if not self.can_overdraw and amount > self.balance:
            raise Account.InsufficientBalance("Account may not be in arrears.")

        self._add_transaction(Transaction(amount=amount,
                                          type=TransactionType.DEBIT))

    def credit(self, amount: AUD) -> None:
        self._add_transaction(Transaction(amount=amount,
                                          type=TransactionType.CREDIT))


class RegularAccount(Account):
    pass


class ExternalCounterparty(Account):
    def __init__(self, id: UUID = None, owner: UUID = None,
                 balance: AUD = None) -> None:
        super(ExternalCounterparty, self).__init__(id, owner, balance)

        self.can_overdraw = True
