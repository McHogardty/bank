
from enum import auto, Enum
from typing import Optional
from uuid import UUID

from .account import Account, ExternalCounterparty, RegularAccount


class AccountType(Enum):
    REGULAR = auto()
    EXTERNAL_COUNTERPARTY = auto()


account_types = {
    ExternalCounterparty: AccountType.EXTERNAL_COUNTERPARTY,
    RegularAccount: AccountType.REGULAR
}

ACCOUNT_MODEL = 'account'
TRANSACTION_MODEL = 'transaction'


class AccountRepository:
    class DoesNotExist(Exception):
        pass

    def __init__(self, database) -> None:
        self.database = database

    def add(self, account: Account) -> None:
        if account.id is None:
            raise ValueError('Cannot add an account without an ID.')

        account_record = {
            'id': account.id,
            'owner': account.owner,
            'balance': account.balance,
            'type': account_types[type(account)]
        }

        self.database.insert(ACCOUNT_MODEL, account_record)

    def get(self, account_id: UUID) -> Optional[Account]:
        try:
            account_record = self.database.get(ACCOUNT_MODEL, account_id)
        except Exception:
            raise AccountRepository.DoesNotExist('Account with ID {} does not '
                                                 'exist.'.format(account_id))

        account_class = None
        for c, t in account_types.items():
            if t == account_record['type']:
                account_class = c

        if account_class is None:
            raise ValueError('Type {} does not match a valid account type.'
                             .format(account_record['type']))

        return account_class(id=account_record['id'],
                             owner=account_record['owner'],
                             balance=account_record['balance'])

    def update(self, account: Account) -> None:
        account_record = {'id': account.id,
                          'owner': account.owner,
                          'balance': account.balance,
                          'type': account_types[type(account)]}

        self.database.update(ACCOUNT_MODEL, account_record)
