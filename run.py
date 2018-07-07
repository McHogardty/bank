
import uuid

from account import (AccountRepository, AccountTransferService, AUD,
                     ExternalCounterparty, RegularAccount)
first_owner = uuid.uuid4()
second_owner = uuid.uuid4()

first_owner_wallet = ExternalCounterparty(owner=first_owner)
first_account = RegularAccount(owner=first_owner)

second_owner_wallet = ExternalCounterparty(owner=second_owner)
second_account = RegularAccount(owner=second_owner)

AccountRepository.add(first_owner_wallet)
AccountRepository.add(first_account)
AccountRepository.add(second_owner_wallet)
AccountRepository.add(second_account)

# Start with some fake balances.
AccountTransferService.transfer(source=first_owner_wallet.id,
                                destination=first_account.id,
                                amount=AUD('10'))
AccountTransferService.transfer(source=second_owner_wallet.id,
                                destination=second_account.id,
                                amount=AUD('20'))

print("First owner wallet is {}".format(first_owner_wallet))
print("Second owner wallet is {}".format(second_owner_wallet))
print()
print("First account is {}".format(first_account))
print("Second account is {}".format(second_account))

amount = AUD('5')
print()
print("Transferring {!s} from first account to second account.".format(amount))
print()

AccountTransferService.transfer(source=first_account.id,
                                destination=second_account.id,
                                amount=amount)

print("First account is {}".format(first_account))
print("Second account is {}".format(second_account))

amount = AUD('10.5')
print()
print("Transferring {!s} from second account to first account.".format(amount))
print()

AccountTransferService.transfer(source=second_account.id,
                                destination=first_account.id,
                                amount=amount)

print("First account is {}".format(first_account))
print("Second account is {}".format(second_account))
