
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
    """A subaccount of an account. Contains a group of transactions and
    potentially some additional behaviour which is provided by subclasses.

    """

    def __init__(self,
                 id: UUID = None,
                 transactions: Iterable[Transaction] = None) -> None:
        super(SubAccount, self).__init__(id=id)

        self.transactions: List[Transaction]
        if transactions is None:
            self.transactions = []
        else:
            self.transactions = list(transactions)

    def __copy__(self) -> SubAccount:
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
        """Calculate the balance of this subaccount. The balance is the sum of
        the transactions.

        Returns a Balance value object.
        """
        # Balance() is the same as Balance(available=AUD(0), pending=AUD(0)).
        return reduce(lambda s, t: t.adjust(s), self.transactions, Balance())

    def settle(self,
               reference: UUID) -> None:
        """Settle a transaction. Fail silently if there is no transaction with
        the provided reference.

        Takes one argument:
        - reference: The reference of the transaction to settle.

        """

        for t in self.transactions:
            if t.reference == reference:
                t.settle()


class RegularSubAccount(SubAccount):
    """No special behaviour. Simply used to distinguish it from the
    alternatives.

    """
    pass


class CardSubAccount(SubAccount):
    """A subaccount representing a magnetic stripe card. All of the
    transactions involving the card are added to this subaccount.

    """

    def __init__(self,
                 id: UUID = None,
                 transactions: Iterable[Transaction] = None,
                 card: Card = None) -> None:
        super(CardSubAccount, self).__init__(id, transactions)

        if card is None:
            raise ValueError("Cannot create a card account without a card.")

        self.card = card


class Account(Entity):
    """An Aggregate root representing multiple annotated collections of
    transactions."""

    class InsufficientBalance(Exception):
        """Used in situations where the account would otherwise be in arrears
        if an operation were to be performed.

        """
        pass

    # Determines whether or not an account may be put into a negative
    # available balance.
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
    def balance(self) -> Balance:
        """Calculate the balance as the sum of the balances of the
        subaccounts.

        Returns a Balance value object.

        """

        return sum(s.balance for s in self.subaccounts)

    @property
    def default_subaccount(self) -> SubAccount:
        """Find the default subaccount for any transactions. The usual
        behaviour is to return the RegularSubAccount.

        This property would ideally be overridden by subclasses if necessary.

        Returns a SubAccount instance.

        """

        for s in self.subaccounts:
            if isinstance(s, RegularSubAccount):
                return s

    def check_subaccounts(self) -> None:
        """Make sure that the account has been initialised with the correct
        types of subaccounts. The default behaviour is to ensure that there is
        one (and only one) regular subaccount.

        """

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
        """Add a transaction to a particular subaccount."""

        subaccount.transactions.append(transaction)

    def debit(self,
              amount: AUD = None,
              reference: UUID = None) -> None:
        """Debit this account by a particular amount.

        Takes two arguments:
        - amount: The amount by which to debit the account.
        - reference: The reference for the transaction.

        """

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
        """Debit a CardSubAccount by a particular amount.

        Takes three arguments:
        - card_number: The number of the card to be debited.
        - amount: The amount by which to debit the card.
        - reference: The reference for the transaction.

        """

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
        """Credit this account by a particular amount.

        Takes two arguments:
        - amount: The amount by which to credit the account.
        - reference: A reference for the transaction.

        """

        self._add_transaction(self.default_subaccount,
                              Transaction(amount=amount,
                                          type=TransactionType.CREDIT,
                                          reference=reference))

    def settle(self, reference: UUID) -> None:
        """Settle a transaction associated with this account.

        Takes one argument:
        - reference: The reference for the transaction to be settled.

        Failed silently if a transaction with that reference is not found.

        """

        for s in self.subaccounts:
            s.settle(reference)


class RegularAccount(Account):
    """A 'typical' account. It can have one regular subaccount and one or more
    card subaccounts."""

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
    """A tool for representing a transaction involving an account which is not
    part of our system. E.g. if a user deposits money into an account. It has
    only a single regular subaccount, no others.

    """

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
