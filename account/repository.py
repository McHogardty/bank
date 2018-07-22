
from enum import auto, Enum
from typing import Optional
from uuid import UUID

from .account import Account, CardAccount, ExternalCounterparty, RegularAccount
from .transaction import Transaction


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


class AccountRepository:
    class DoesNotExist(Exception):
        pass

    def __init__(self, database, manager) -> None:
        self.database = database
        self.work_manager = manager

    def add(self, account: Account) -> None:
        if account.id is None:
            raise ValueError('Cannot add an account without an ID.')

        account_record = {
            'id': account.id,
            'owner': account.owner,
            'balance': account.balance,
            'type': account_types[type(account)]
        }

        self.work_manager.add(ACCOUNT_MODEL, account_record)

        for t in account.transactions:
            transaction_record = {'id': t.id,
                                  'reference': t.reference,
                                  'amount': t.amount,
                                  'type': t.type,
                                  'account': account.id}

            self.work_manager.add(TRANSACTION_MODEL, transaction_record)

        if isinstance(account, CardAccount):
            card_record = {'id': account.card.id,
                           'number': account.card.number,
                           'account': account.id}

            self.work_manager.add(CARD_MODEL, card_record)

    def get(self, account_id: UUID) -> Optional[Account]:
        try:
            account_record = self.database.get(ACCOUNT_MODEL, account_id)
        except Exception:
            raise AccountRepository.DoesNotExist('Account with ID {} does not '
                                                 'exist.'.format(account_id))

        account_class = None
        for c, account_type in account_types.items():
            if account_type == account_record['type']:
                account_class = c

        if account_class is None:
            raise ValueError('Type {} does not match a valid account type.'
                             .format(account_record['type']))

        transaction_records = self.database.find(
            TRANSACTION_MODEL,
            lambda t: t['account'] == account_id
        )
        transactions = []
        for t in transaction_records:
            t.pop('account', None)
            transactions.append(Transaction(**t))

        account_kwargs = {'id': account_record['id'],
                          'owner': account_record['owner'],
                          'balance': account_record['balance'],
                          'transactions': transactions}
        if account_class == CardAccount:
            card = self.database.find(CARD_MODEL,
                                      lambda c: c['account'] == account_id)
            account_kwargs['card'] = card

        return account_class(**account_kwargs)

    def update(self, account: Account) -> None:
        account_record = {'id': account.id,
                          'owner': account.owner,
                          'balance': account.balance,
                          'type': account_types[type(account)]}

        self.work_manager.mark_dirty(ACCOUNT_MODEL, account_record)

        for t in account.transactions:
            self.work_manager.delete(TRANSACTION_MODEL, t.id)
            transaction_record = {'id': t.id,
                                  'reference': t.reference,
                                  'amount': t.amount,
                                  'type': t.type,
                                  'account': account.id}

            self.work_manager.add(TRANSACTION_MODEL, transaction_record)
