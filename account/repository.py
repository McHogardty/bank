
from abc import abstractmethod
from typing import Iterable
from uuid import UUID

from .account import Account
from .base import Repository
from .values import CardNumber


class AccountRepository(Repository[Account]):
    """A repository for the Account aggregate root."""

    class DoesNotExist(Exception):
        """Raised when searching for an account which does not exist."""
        pass

    @abstractmethod
    def get(self, id: UUID) -> Account:
        pass

    @abstractmethod
    def add(self, account: Account) -> None:
        pass

    @abstractmethod
    def update(self, account: Account) -> None:
        pass

    @abstractmethod
    def find_by_card_number(self, card_number: CardNumber) -> Account:
        """Find an account by an associated card.

        Takes one argument:
        - card_number: The card number for the card.

        Returns an Account instance.

        """

        pass

    @abstractmethod
    def find_by_transaction_reference(self,
                                      reference: UUID) -> Iterable[Account]:
        """Find the accounts containing transactions with a particular
        reference.

        Takes one argument:
        - reference: The reference to search for.

        Returns an iterable of Account instances.

        """
        pass
