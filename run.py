
import sys
import uuid

from account import (AccountRepository, AccountTransferService, AUD,
                     ExternalCounterparty, RegularAccount)
from infrastructure import Database

account_repository = AccountRepository(Database)
transfer_service = AccountTransferService(account_repository)

first_owner = uuid.uuid4()
second_owner = uuid.uuid4()

first_owner_wallet = ExternalCounterparty(owner=first_owner)
first_account = RegularAccount(owner=first_owner)

second_owner_wallet = ExternalCounterparty(owner=second_owner)
second_account = RegularAccount(owner=second_owner)

account_repository.add(first_owner_wallet)
account_repository.add(first_account)
account_repository.add(second_owner_wallet)
account_repository.add(second_account)

# Start with some fake balances.
transfer_service.transfer(source=first_owner_wallet.id,
                          destination=first_account.id,
                          amount=AUD('10'))
transfer_service.transfer(source=second_owner_wallet.id,
                          destination=second_account.id,
                          amount=AUD('20'))

print("First owner wallet is {}"
      .format(account_repository.get(first_owner_wallet.id)))
print("Second owner wallet is {}"
      .format(account_repository.get(second_owner_wallet.id)))
print()
print("First account is {}".format(account_repository.get(first_account.id)))
print("Second account is {}".format(account_repository.get(second_account.id)))

amount = AUD('5')
print()
print("Transferring {!s} from first account to second account.".format(amount))
print()

transfer_service.transfer(source=first_account.id,
                          destination=second_account.id,
                          amount=amount)

print("First account is {}".format(account_repository.get(first_account.id)))
print("Second account is {}".format(account_repository.get(second_account.id)))

amount = AUD('10.5')
print()
print("Transferring {!s} from second account to first account.".format(amount))
print()

transfer_service.transfer(source=second_account.id,
                          destination=first_account.id,
                          amount=amount)

print("First account is {}".format(account_repository.get(first_account.id)))
print("Second account is {}".format(account_repository.get(second_account.id)))
