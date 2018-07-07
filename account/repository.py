
from typing import Dict, Optional
from uuid import UUID

from .account import Account

_accounts: Dict[UUID, Account] = {}


class AccountRepository:
    class DoesNotExist(Exception):
        pass

    @classmethod
    def add(cls, account: Account) -> None:
        if account.id is None:
            raise ValueError('Cannot add an account without an ID.')

        _accounts[account.id] = account

    @classmethod
    def get(cls, account_id: UUID) -> Optional[Account]:
        try:
            return _accounts.get(account_id)
        except KeyError:
            raise cls.DoesNotExist('Account with ID {} does not exist.'.format(account_id))