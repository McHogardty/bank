
import random
import uuid

from account import (AccountRepository, AccountTransferService, AUD,
                     ExternalCounterparty, RegularAccount)
from account.account import CardAccount
from account.card import Card
from account.values import CardNumber
from account.services import CardPurchaseService
from infrastructure import Database, WorkManager


def generate_card_number():
    card_digits = [random.randint(1, 9)] + [random.randint(0, 9)
                                            for _ in range(15)]
    return CardNumber(''.join(map(str, card_digits)))


work_manager = WorkManager()
account_repository = AccountRepository(Database, work_manager)
transfer_service = AccountTransferService(account_repository)
purchase_service = CardPurchaseService(account_repository)

first_owner = uuid.uuid4()
second_owner = uuid.uuid4()

first_owner_wallet = ExternalCounterparty(owner=first_owner)
first_account = RegularAccount(owner=first_owner)
first_card_account = CardAccount(owner=first_owner,
                                 card=Card(number=generate_card_number()))

second_owner_wallet = ExternalCounterparty(owner=second_owner)
second_account = RegularAccount(owner=second_owner)

with work_manager.scope():
    account_repository.add(first_owner_wallet)
    account_repository.add(first_account)
    account_repository.add(second_owner_wallet)
    account_repository.add(second_account)
    account_repository.add(first_card_account)

# Start with some fake balances.
with work_manager.scope():
    transfer_service.transfer(source=first_owner_wallet.id,
                              destination=first_account.id,
                              amount=AUD('10'))
    transfer_service.transfer(source=second_owner_wallet.id,
                              destination=second_account.id,
                              amount=AUD('20'))

print("First owner wallet is {}"
      .format(first_owner_wallet))
print("Second owner wallet is {}"
      .format(second_owner_wallet))
print()
print("First account is {}".format(first_account))
print("Second account is {}".format(second_account))
print()
print("First card account is {}".format(first_card_account))

amount = AUD('5')
print()
print("Transferring {!s} from first account to second account.".format(amount))
print()

with work_manager.scope():
    transfer_service.transfer(source=first_account.id,
                              destination=second_account.id,
                              amount=amount)

print("First account is {}".format(account_repository.get(first_account.id)))
print("Second account is {}".format(account_repository.get(second_account.id)))

amount = AUD('10.5')
print()
print("Transferring {!s} from second account to first account.".format(amount))
print()

try:
    with work_manager.scope():
        transfer_service.transfer(source=second_account.id,
                                  destination=first_account.id,
                                  amount=amount)

        raise ValueError('Something bad happened.')
except ValueError:
    pass

print("First account is {}".format(account_repository.get(first_account.id)))
print("Second account is {}".format(account_repository.get(second_account.id)))

amount = AUD('5')
print()
print("Transferring {!s} from first account to first card account."
      .format(amount))
print()

with work_manager.scope():
    transfer_service.transfer(source=first_account.id,
                              destination=first_card_account.id,
                              amount=amount)

print("First account is {}".format(account_repository.get(first_account.id)))
print("First card account is {}"
      .format(account_repository.get(first_card_account.id)))

merchant = ExternalCounterparty(owner=uuid.uuid4())
with work_manager.scope():
    account_repository.add(merchant)

amount = AUD('2.5')
print()
print("Making a purchase if {!s} from the merchant to the first card account."
      .format(amount))
print()

with work_manager.scope():
    purchase_service.make_purchase(card_account=first_card_account.id,
                                   merchant=merchant.id,
                                   amount=amount)

print("First card account is {}"
      .format(account_repository.get(first_card_account.id)))
print("Merchant is {}".format(account_repository.get(merchant.id)))
