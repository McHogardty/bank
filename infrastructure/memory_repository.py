
from enum import auto, Enum
from typing import Mapping
from uuid import UUID

from account import (
    Account,
    Card,
    CardAccount,
    ExternalCounterparty,
    RegularAccount,
    Transaction,
)
from account.repository import AccountRepository

from .memory_store import MemoryStore, StorageRecord


AccountCache = Mapping[UUID, Account]


class AccountType(Enum):
    REGULAR = auto()
    EXTERNAL_COUNTERPARTY = auto()
    CARD = auto()


account_types = {
    ExternalCounterparty: AccountType.EXTERNAL_COUNTERPARTY,
    RegularAccount: AccountType.REGULAR,
    CardAccount: AccountType.CARD
}


ACCOUNT_MODEL = 'account'
TRANSACTION_MODEL = 'transaction'
CARD_MODEL = 'card'


class InMemoryRepository(AccountRepository):
    def __init__(self, memory_store: MemoryStore) -> None:
        self._store = memory_store

    def _account_to_record(self, account: Account) -> StorageRecord:
        return {
            'id': account.id,
            'owner': account.owner,
            'balance': account.balance,
            'type': account_types[type(account)],
            'parent': None if account.parent is None else account.parent.id,
        }

    def _transaction_to_record(self,
                               transaction: Transaction,
                               account: Account) -> StorageRecord:
        return {
            'id': transaction.id,
            'reference': transaction.reference,
            'amount': transaction.amount,
            'type': transaction.type,
            'account': account.id,
        }

    def _card_to_record(self, card: Card, account: Account) -> StorageRecord:
        return {
            'id': card.id,
            'number': card.number,
            'account': account.id,
        }

    def get(self, account_id: UUID) -> Account:
        try:
            record = self._store.get(ACCOUNT_MODEL, account_id)
        except Exception:
            raise AccountRepository.DoesNotExist

        account_class = None
        record_type = record.pop('type')
        for c, account_type in account_types.items():
            if record_type == account_type:
                account_class = c

        if account_class is None:
            raise ValueError('Encountered account record with unknown account'
                             ' type {}'.format(record_type))

        def find_transaction(record):
            return record['account'] == account_id

        transaction_records = self._store.find(
            TRANSACTION_MODEL,
            lambda r: r["account"] == account_id,
        )

        transactions = []
        for t in transaction_records:
            t.pop('account')
            transactions.append(Transaction(**t))

        record['transactions'] = transactions

        if account_class == CardAccount:
            result = list(self._store.find(
                CARD_MODEL,
                lambda c: c['account'] == account_id
            ))
            if len(result) != 1:
                raise ValueError('Encountered a card account {} with no '
                                 'associated card.'.format(account_id))
            card_record = result[0]
            card_record.pop('account')
            record['card'] = Card(**card_record)

        parent = record.pop('parent')
        if parent is not None:
            parent = self.get(parent)
            record['parent'] = parent

        instance = account_class(**record)
        return instance

    def add(self, account: Account) -> None:
        record = self._account_to_record(account)
        self._store.add(ACCOUNT_MODEL, account.id, record)

        for t in account.transactions:
            record = self._transaction_to_record(t, account)
            self._store.add(TRANSACTION_MODEL, t.id, record)

        if isinstance(account, CardAccount):
            record = self._card_to_record(account.card, account)
            self._store.add(CARD_MODEL, account.card.id, record)

        if account.parent is not None:
            self.add(account.parent)

    def update(self, account: Account) -> None:
        record = self._account_to_record(account)
        self._store.update(ACCOUNT_MODEL, account.id, record)

        for t in account.transactions:
            record = self._transaction_to_record(t, account)
            self._store.update(TRANSACTION_MODEL, t.id, record)

        if account.parent is not None:
            self.update(account.parent)
