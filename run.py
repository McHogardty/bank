
import random
import uuid

from account import (
    AccountTransferService,
    AUD,
    Card,
    CardAccount,
    CardNumber,
    CardPurchaseService,
    ExternalCounterparty,
    RegularAccount,
)
from infrastructure import InMemoryRepository, MemoryStore, WorkManager


def generate_card_number():
    card_digits = [random.randint(1, 9)] + [random.randint(0, 9)
                                            for _ in range(15)]
    return CardNumber(''.join(map(str, card_digits)))


store = MemoryStore()
work_manager = WorkManager(store)
master_repository = InMemoryRepository(store)

first_owner = uuid.uuid4()
second_owner = uuid.uuid4()

first_owner_wallet = ExternalCounterparty(owner=first_owner)
first_account = RegularAccount(owner=first_owner)
first_card_account = CardAccount(owner=first_owner,
                                 card=Card(number=generate_card_number()))

second_owner_wallet = ExternalCounterparty(owner=second_owner)
second_account = RegularAccount(owner=second_owner)

master_repository.add(first_owner_wallet)
master_repository.add(first_account)
master_repository.add(second_owner_wallet)
master_repository.add(second_account)
master_repository.add(first_card_account)

# Start with some fake balances.
with work_manager.scope() as SCOPE:
    transfer_service = AccountTransferService(SCOPE.get(InMemoryRepository))
    transfer_service.transfer(source=first_owner_wallet.id,
                              destination=first_account.id,
                              amount=AUD('10'))
    transfer_service.transfer(source=second_owner_wallet.id,
                              destination=second_account.id,
                              amount=AUD('20'))

print("First owner wallet is {}"
      .format(master_repository.get(first_owner_wallet.id)))
print("Second owner wallet is {}"
      .format(master_repository.get(second_owner_wallet.id)))
print()
print("First account is {}".format(master_repository.get(first_account.id)))
print("Second account is {}".format(master_repository.get(second_account.id)))
print()
print("First card account is {}"
      .format(master_repository.get(first_card_account.id)))

amount = AUD('5')
print()
print("Transferring {!s} from first account to second account.".format(amount))
print()

SCOPE = work_manager.unit()
SCOPE.begin()
transfer_service = AccountTransferService(SCOPE.get(InMemoryRepository))
transfer_service.transfer(source=first_account.id,
                          destination=second_account.id,
                          amount=amount)
SCOPE.commit()

print("First account is {}".format(master_repository.get(first_account.id)))
print("Second account is {}".format(master_repository.get(second_account.id)))

amount = AUD('10.5')
print()
print("Transferring {!s} from second account to first account.".format(amount))
print()

try:
    with work_manager.scope() as SCOPE:
        transfer_service = AccountTransferService(
            SCOPE.get(InMemoryRepository)
        )

        transfer_service.transfer(source=second_account.id,
                                  destination=first_account.id,
                                  amount=amount)

        raise ValueError('Something bad happened.')
except ValueError:
    pass

print("First account is {}".format(master_repository.get(first_account.id)))
print("Second account is {}".format(master_repository.get(second_account.id)))

amount = AUD('5')
print()
print("Transferring {!s} from first account to first card account."
      .format(amount))
print()

with work_manager.scope() as SCOPE:
    transfer_service = AccountTransferService(SCOPE.get(InMemoryRepository))

    transfer_service.transfer(source=first_account.id,
                              destination=first_card_account.id,
                              amount=amount)

print("First account is {}".format(master_repository.get(first_account.id)))
print("First card account is {}"
      .format(master_repository.get(first_card_account.id)))

merchant = ExternalCounterparty(owner=uuid.uuid4())
master_repository.add(merchant)

amount = AUD('2.5')
print()
print("Making a purchase if {!s} from the merchant to the first card account."
      .format(amount))
print()

with work_manager.scope() as SCOPE:
    purchase_service = CardPurchaseService(SCOPE.get(InMemoryRepository))
    purchase_service.make_purchase(card_account=first_card_account.id,
                                   merchant=merchant.id,
                                   amount=amount)

print("First card account is {}"
      .format(master_repository.get(first_card_account.id)))
print("Merchant is {}".format(master_repository.get(merchant.id)))
