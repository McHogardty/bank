
from __future__ import annotations

from copy import deepcopy
from functools import reduce
from typing import Iterable, List
from uuid import UUID

from .base import Entity
from .card import Card
from .transaction import Transaction, TransactionStatus, TransactionType
from .values import AUD, Balance, CardNumber


class SubAccount(Entity):
    can_overdraw = False

    def __init__(self,
                 id: UUID = None,
                 transactions: Iterable[Transaction] = None) -> None:
        super(SubAccount, self).__init__(id=id)

        self.transactions: List[Transaction] = []

        if transactions is not None:
            self.transactions = list(transactions)

    def __copy__(self) -> SubAccount:  # noqa
        new_copy = type(self)(id=self.id)
        new_copy.transactions = self.transactions

        return new_copy

    def __deepcopy__(self, memo) -> SubAccount:
        self_id = id(self)
        if self_id in memo:
            return memo[self_id]

        new_id = deepcopy(self.id)
        new_account = type(self)(id=new_id)
        new_account.transactions = deepcopy(self.transactions)

        return new_account

    @property
    def balance(self):
        # Balance() is the same as Balance(available=AUD(0), pending=AUD(0)).
        return reduce(lambda s, t: t.adjust(s), self.transactions, Balance())

    def settle(self,
               reference: UUID) -> None:
        for t in self.transactions:
            if t.reference == reference:
                t.settle()


class RegularSubAccount(SubAccount):
    pass


class CardSubAccount(SubAccount):
    can_overdraw = True

    def __init__(self,
                 id: UUID = None,
                 transactions: Iterable[Transaction] = None,
                 card: Card = None) -> None:
        super(CardSubAccount, self).__init__(id, transactions)

        if card is None:
            raise ValueError("Cannot create a card account without a card.")

        self.card = card


class Account(Entity):
    class InsufficientBalance(Exception):
        pass

    can_overdraw = False

    def __init__(self, id: UUID = None, owner: UUID = None,
                 subaccounts: Iterable[SubAccount] = None) -> None:
        super(Account, self).__init__(id=id)

        self.owner = owner

        if subaccounts is None:
            raise ValueError('Cannot create an account without any '
                             'subaccounts.')

        self.subaccounts = list(subaccounts)
        self.check_subaccounts()

    @property
    def balance(self):
        return sum(s.balance for s in self.subaccounts)

    @property
    def default_subaccount(self):
        for s in self.subaccounts:
            if isinstance(s, RegularSubAccount):
                return s

    def check_subaccounts(self):
        have_regular = False
        for s in self.subaccounts:
            is_regular = isinstance(s, RegularSubAccount)

            if have_regular and is_regular:
                raise ValueError('Cannot have more than one regular '
                                 'subaccount for this account.')

            have_regular = have_regular or is_regular

        if not have_regular:
            raise ValueError('Subaccounts must include a RegularSubAccount')

    def _add_transaction(self, subaccount, transaction):
        subaccount.transactions.append(transaction)

    def debit(self,
              amount: AUD = None,
              reference: UUID = None) -> None:
        if not self.can_overdraw and amount > self.balance.available:
            raise Account.InsufficientBalance("Account may not be in arrears.")

        self._add_transaction(self.default_subaccount,
                              Transaction(amount=amount,
                                          type=TransactionType.DEBIT,
                                          reference=reference))

    def debit_card(self,
                   card_number: CardNumber = None,
                   amount: AUD = None,
                   reference: UUID = None) -> None:
        card_account = None
        for s in self.subaccounts:
            if isinstance(s, CardSubAccount) and s.card.number == card_number:
                card_account = s

        if s is None:
            raise ValueError('No subaccount matching card number {}.'
                             .format(card_number))

        if not self.can_overdraw and amount > self.balance.available:
            raise Account.InsufficientBalance("Account may not be in arrears.")

        self._add_transaction(card_account,
                              Transaction(amount=amount,
                                          type=TransactionType.DEBIT,
                                          reference=reference))

    def credit(self,
               amount: AUD = None,
               reference: UUID = None) -> None:
        self._add_transaction(self.default_subaccount,
                              Transaction(amount=amount,
                                          type=TransactionType.CREDIT,
                                          reference=reference))

    def settle(self, reference: UUID) -> None:
        for s in self.subaccounts:
            s.settle(reference)


class RegularAccount(Account):
    can_overdraw = False

    def __init__(self, id: UUID = None, owner: UUID = None,
                 subaccounts: Iterable[SubAccount] = None,
                 cards: Iterable[Card] = None) -> None:
        if cards is not None and subaccounts is not None:
            raise ValueError('Cannot create a regular account with both cards '
                             'and subaccounts.')

        if subaccounts is None:
            subaccounts = [RegularSubAccount()]

            if cards is not None:
                for card in cards:
                    subaccounts.append(CardSubAccount(card=card))

        super(RegularAccount, self).__init__(id=id,
                                             owner=owner,
                                             subaccounts=subaccounts)


class ExternalCounterparty(Account):
    can_overdraw = True

    def __init__(self, id: UUID = None, owner: UUID = None,
                 subaccounts: Iterable[SubAccount] = None) -> None:
        if subaccounts is None:
            subaccounts = [RegularSubAccount()]

        super(ExternalCounterparty, self).__init__(id=id,
                                                   owner=owner,
                                                   subaccounts=subaccounts)

    def check_subaccounts(self):
        if (len(self.subaccounts) != 1 or
                not isinstance(self.subaccounts[0], RegularSubAccount)):
            raise ValueError('An external counterparty must have only one '
                             'regular account.')
