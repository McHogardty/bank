
from __future__ import annotations

from copy import deepcopy
from typing import Iterable, List
from uuid import UUID

from .base import Entity
from .card import Card
from .transaction import Transaction, TransactionType
from .values import AUD


class Account(Entity):
    class InsufficientBalance(Exception):
        pass

    def __init__(self, id: UUID = None, owner: UUID = None,
                 balance: AUD = None,
                 transactions: Iterable[Transaction] = None) -> None:
        super(Account, self).__init__(id=id)

        if owner is None:
            raise ValueError("An account must have an owner.")

        self.transactions: List[Transaction] = []
        self.owner = owner
        self.can_overdraw = False

        if transactions is not None:
            self.balance = AUD('0')
            for t in transactions:
                self._add_transaction(t)

            if balance is not None and self.balance != balance:
                raise ValueError('Provided balance does not match sum of '
                                 'transactions.')
        else:
            self.balance = AUD('0') if balance is None else balance

    def __copy__(self) -> Account:  # noqa
        new_copy = type(self)(id=self.id, owner=self.owner)
        new_copy.balance = self.balance
        new_copy.transactions = self.transactions

        return new_copy

    def __deepcopy__(self, memo) -> Account:  # noqa
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

    def debit(self, amount: AUD, reference: UUID) -> None:
        if not self.can_overdraw and amount > self.balance:
            raise Account.InsufficientBalance("Account may not be in arrears.")

        self._add_transaction(Transaction(amount=amount,
                                          type=TransactionType.DEBIT,
                                          reference=reference))

    def credit(self, amount: AUD, reference: UUID) -> None:
        self._add_transaction(Transaction(amount=amount,
                                          type=TransactionType.CREDIT,
                                          reference=reference))


class RegularAccount(Account):
    pass


class CardAccount(Account):
    def __init__(self, id: UUID = None, owner: UUID = None,
                 balance: AUD = None,
                 transactions: Iterable[Transaction] = None,
                 card: Card = None) -> None:
        super(CardAccount, self).__init__(id, owner, balance,
                                          transactions)

        self.card = card


class ExternalCounterparty(Account):
    def __init__(self, id: UUID = None, owner: UUID = None,
                 balance: AUD = None,
                 transactions: Iterable[Transaction] = None) -> None:
        super(ExternalCounterparty, self).__init__(id, owner, balance,
                                                   transactions)

        self.can_overdraw = True
