
from abc import abstractmethod
from uuid import UUID

from .account import Account
from .base import Repository
from .values import CardNumber


class AccountRepository(Repository[Account]):
    class DoesNotExist(Exception):
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
        pass
