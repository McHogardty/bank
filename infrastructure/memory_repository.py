
from enum import auto, Enum
from typing import Dict, List, Type
from uuid import UUID

from account import (
    Account,
    Card,
    CardNumber,
    CardSubAccount,
    ExternalCounterparty,
    RegularAccount,
    RegularSubAccount,
    SubAccount,
    Transaction,
)
from account.repository import AccountRepository

from .memory_store import MemoryStore, StorageRecord


AccountCache = Dict[UUID, Account]


class AccountType(Enum):
    REGULAR = auto()
    EXTERNAL_COUNTERPARTY = auto()
    CARD = auto()


class SubAccountType(Enum):
    REGULAR = auto()
    CARD = auto()


account_types: Dict[Type[Account], AccountType] = {
    ExternalCounterparty: AccountType.EXTERNAL_COUNTERPARTY,
    RegularAccount: AccountType.REGULAR,
}


subaccount_types: Dict[Type[SubAccount], SubAccountType] = {
    CardSubAccount: SubAccountType.CARD,
    RegularSubAccount: SubAccountType.REGULAR,
}


ACCOUNT_MODEL = 'account'
SUBACCOUNT_MODEL = 'subaccount'
TRANSACTION_MODEL = 'transaction'
CARD_MODEL = 'card'


class InMemoryRepository(AccountRepository):
    def __init__(self, memory_store: MemoryStore) -> None:
        self._store = memory_store
        self._cache: AccountCache = {}

    def _account_to_record(self, account: Account) -> StorageRecord:
        return {
            'id': account.id,
            'owner': account.owner,
            'type': account_types[type(account)],
        }

    def _subaccount_to_record(self,
                              subaccount: SubAccount,
                              account: Account) -> StorageRecord:
        return {
            'id': subaccount.id,
            'account': account.id,
            'type': subaccount_types[type(subaccount)]
        }

    def _transaction_to_record(self,
                               transaction: Transaction,
                               account: SubAccount) -> StorageRecord:
        return {
            'id': transaction.id,
            'reference': transaction.reference,
            'amount': transaction.amount,
            'type': transaction.type,
            'account': account.id,
            'status': transaction.status,
        }

    def _card_to_record(self,
                        card: Card,
                        account: SubAccount) -> StorageRecord:
        return {
            'id': card.id,
            'number': card.number,
            'account': account.id,
        }

    def get(self, account_id: UUID) -> Account:
        try:
            return self._cache[account_id]
        except KeyError:
            pass

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

        subaccounts: List[SubAccount] = []
        subaccount_records = list(self._store.find(
            SUBACCOUNT_MODEL,
            lambda r: r['account'] == account_id,
        ))
        # print(subaccount_records)
        for subaccount_record in subaccount_records:
            # print("Got subaccount.")
            subaccount_class = None
            record_type = subaccount_record.pop('type')
            subaccount_record.pop('account')
            subaccount_id = subaccount_record['id']

            for class_, subaccount_type in subaccount_types.items():
                if record_type == subaccount_type:
                    subaccount_class = class_

            if subaccount_class is None:
                raise ValueError('Encountered unknown account type for '
                                 'account {}. Type was {}.'
                                 .format(account_id, record_type))

            transaction_records = self._store.find(
                TRANSACTION_MODEL,
                lambda r: r['account'] == subaccount_id,
            )

            transactions: List[Transaction] = []
            for t in transaction_records:
                t.pop('account')
                transactions.append(Transaction(**t))

            subaccount_record['transactions'] = transactions

            if subaccount_class == CardSubAccount:
                card_records = list(self._store.find(
                    CARD_MODEL,
                    lambda c: c['account'] == subaccount_id,
                ))
                if len(card_records) != 1:
                    raise ValueError('Encountered a card sub account {}'
                                     'with no associated card.'
                                     .format(subaccount_id))
                card_record = card_records[0]
                card_record.pop('account')
                subaccount_record['card'] = Card(**card_record)

            subaccounts.append(subaccount_class(**subaccount_record))

        record['subaccounts'] = subaccounts
        self._cache[account_id] = instance = account_class(**record)
        return instance

    def add(self, account: Account) -> None:
        record = self._account_to_record(account)
        self._store.add(ACCOUNT_MODEL, account.id, record)

        for s in account.subaccounts:
            record = self._subaccount_to_record(s, account)
            self._store.add(SUBACCOUNT_MODEL, s.id, record)

            if isinstance(s, CardSubAccount):
                record = self._card_to_record(s.card, s)
                self._store.add(CARD_MODEL, s.card.id, record)

            for t in s.transactions:
                record = self._transaction_to_record(t, s)
                self._store.add(TRANSACTION_MODEL, t.id, record)

        self._cache[account.id] = account

    def update(self, account: Account) -> None:
        record = self._account_to_record(account)
        self._store.update(ACCOUNT_MODEL, account.id, record)

        for s in account.subaccounts:
            record = self._subaccount_to_record(s, account)
            self._store.update(SUBACCOUNT_MODEL, s.id, record)

            if isinstance(s, CardSubAccount):
                record = self._card_to_record(s.card, s)
                self._store.update(CARD_MODEL, s.card.id, record)

            for t in s.transactions:
                record = self._transaction_to_record(t, s)
                self._store.update(TRANSACTION_MODEL, t.id, record)

        self._cache[account.id] = account

    def find_by_card_number(self, card_number: CardNumber) -> Account:
        card_records = list(self._store.find(
            CARD_MODEL,
            lambda c: c['number'] == card_number,
        ))

        if len(card_records) != 1:
            raise ValueError('Could not find a card record for card number {}'
                             .format(card_number))

        subaccount_id = card_records[0]['account']

        try:
            subaccount = self._store.get(SUBACCOUNT_MODEL, subaccount_id)
        except Exception:
            raise AccountRepository.DoesNotExist('Could not find a subaccount '
                                                 'with ID {}.'
                                                 .format(subaccount_id))

        return self.get(subaccount['account'])
