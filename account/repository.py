
from abc import ABCMeta, abstractmethod
from uuid import UUID

from .account import Account


class AccountRepository(metaclass=ABCMeta):
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
