
from decimal import Decimal
from typing import List
from uuid import UUID

from .base import Entity
from .transaction import Transaction, TransactionType

class Account(Entity):
    def __init__(self, id: UUID = None, owner: UUID = None) -> None:
        super(Account, self).__init__(id=id)

        self.transactions: List[Transaction] = []
        self.balance: Decimal = Decimal('0')
        self.owner = owner

    def _add_transaction(self, transaction: Transaction) -> None:
    	self.transactions.append(transaction)

    	if transaction.type == TransactionType.CREDIT:
    		self.balance += transaction.amount
    	else:
	    	self.balance -= transaction.amount

    def debit(self, amount: Decimal) -> None:
    	self._add_transaction(Transaction(amount=amount, type=TransactionType.DEBIT))

    def credit(self, amount: Decimal) -> None:
    	self._add_transaction(Transaction(amount=amount, type=TransactionType.CREDIT))