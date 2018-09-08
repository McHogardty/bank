
import copy
from enum import auto, Enum
from typing import Any, Dict
from uuid import UUID

from account import (
    Account,
    CardAccount,
    ExternalCounterparty,
    RegularAccount,
    Transaction,
)
from account.repository import AccountRepository


AccountCache = Dict[UUID, Account]
StorageRecord = Dict[str, Any]
MemoryStore = Dict[UUID, StorageRecord]


class AccountType(Enum):
    REGULAR = auto()
    EXTERNAL_COUNTERPARTY = auto()
    CARD = auto()


account_types = {
    ExternalCounterparty: AccountType.EXTERNAL_COUNTERPARTY,
    RegularAccount: AccountType.REGULAR,
    CardAccount: AccountType.CARD
}


class InMemoryRepository(AccountRepository):
    def __init__(self):
        self._account_store: MemoryStore = {}
        self._transaction_store: MemoryStore = {}

    def _account_to_record(self, account: Account) -> StorageRecord:
        return {
            'id': account.id,
            'owner': account.owner,
            'balance': account.balance,
            'type': account_types[type(account)]
        }

    def _transaction_to_record(self,
                               transaction: Transaction,
                               account: Account) -> StorageRecord:  # noqa
        return {
            'id': transaction.id,
            'reference': transaction.reference,
            'amount': transaction.amount,
            'type': transaction.type,
            'account': account.id
        }

    def get(self, account_id: UUID) -> Account:
        try:
            record = self._account_store[account_id]
        except KeyError:
            raise AccountRepository.DoesNotExist

        record = copy.deepcopy(record)

        account_class = None
        record_type = record.pop('type')
        for c, account_type in account_types.items():
            if record_type == account_type:
                account_class = c

        if account_class is None:
            raise ValueError('Encountered account record with unknown account'
                             ' type {}'.format(record_type))

        return account_class(**record)

    def add(self, account: Account) -> None:
        account = copy.deepcopy(account)
        self._account_store[account.id] = self._account_to_record(account)

        for t in account.transactions:
            self._transaction_store[t.id] = \
                self._transaction_to_record(t, account)

    def update(self, account: Account):
        account = copy.deepcopy(account)
        record = self._account_to_record(account)
        try:
            self._account_store[account.id].update(record)
        except KeyError:
            self._account_store[account.id] = record

        for t in account.transactions:
            record = self._transaction_to_record(t, account)
            try:
                self._transaction_store[t.id].update(record)
            except KeyError:
                self._transaction_store[t.id] = record
