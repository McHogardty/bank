
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

    can_overdraw = False

    def __init__(self, id: UUID = None, owner: UUID = None,
                 balance: AUD = None, parent: Account = None,
                 transactions: Iterable[Transaction] = None) -> None:
        super(Account, self).__init__(id=id)

        if owner is None:
            raise ValueError("An account must have an owner.")

        self.transactions: List[Transaction] = []
        self.owner = owner
        self.parent = parent

        if transactions is not None:
            self.balance = AUD('0')
            for t in transactions:
                self._add_transaction(t)
        else:
            self.balance = AUD('0') if balance is None else balance

    def __copy__(self) -> Account:  # noqa
        new_copy = type(self)(id=self.id, owner=self.owner)
        new_copy.balance = self.balance
        new_copy.transactions = self.transactions
        new_copy.parent = self.parent

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
        new_account.parent = deepcopy(self.parent)

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

        if self.parent is not None:
            self.parent.debit(amount, reference)

    def credit(self, amount: AUD, reference: UUID) -> None:
        self._add_transaction(Transaction(amount=amount,
                                          type=TransactionType.CREDIT,
                                          reference=reference))

        if self.parent is not None:
            self.parent.credit(amount, reference)


class RegularAccount(Account):
    pass


class CardAccount(Account):
    can_overdraw = True

    def __init__(self, id: UUID = None, owner: UUID = None,
                 balance: AUD = None, parent: Account = None,
                 transactions: Iterable[Transaction] = None,
                 card: Card = None) -> None:
        super(CardAccount, self).__init__(id, owner, balance, parent,
                                          transactions)

        if card is None:
            raise ValueError("Cannot create a card account without a card.")
        self.card = card


class ExternalCounterparty(Account):
    can_overdraw = True

    def __init__(self, id: UUID = None, owner: UUID = None,
                 balance: AUD = None, parent: Account = None,
                 transactions: Iterable[Transaction] = None) -> None:
        super(ExternalCounterparty, self).__init__(id, owner, balance, parent,
                                                   transactions)
