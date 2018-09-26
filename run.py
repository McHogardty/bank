
import random
import uuid

from account import (
    AccountTransferService,
    AUD,
    Card,
    CardNumber,
    CardPurchaseService,
    ExternalCounterparty,
    RegularAccount,
    TransactionSettlementService,
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
first_card = Card(number=generate_card_number())
second_card = Card(number=generate_card_number())
first_account = RegularAccount(owner=first_owner,
                               cards=[first_card, second_card])

second_owner_wallet = ExternalCounterparty(owner=second_owner)
second_account = RegularAccount(owner=second_owner)

with work_manager.scope() as SCOPE:
    account_repository = SCOPE.get(InMemoryRepository)
    account_repository.add(first_owner_wallet)
    account_repository.add(first_account)
    account_repository.add(second_owner_wallet)
    account_repository.add(second_account)

# Start with some fake balances.
with work_manager.scope() as SCOPE:
    transfer_service = AccountTransferService(SCOPE.get(InMemoryRepository))
    transfer_service.transfer(source=first_owner_wallet.id,
                              destination=first_account.id,
                              amount=AUD('10'))
    transfer_service.transfer(source=second_owner_wallet.id,
                              destination=second_account.id,
                              amount=AUD('20'))

account_repository = InMemoryRepository(store)
first_owner_wallet_copy = account_repository.get(first_owner_wallet.id)
print("First owner wallet balance is {!s}"
      .format(account_repository.get(first_owner_wallet.id).balance))
print("Second owner wallet balance is {!s}"
      .format(account_repository.get(second_owner_wallet.id).balance))
print()
print("First account balance is {!s}"
      .format(account_repository.get(first_account.id).balance))
print("Second account balance is {!s}"
      .format(account_repository.get(second_account.id).balance))
print()

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

account_repository = InMemoryRepository(store)
print("First account balance is {!s}"
      .format(account_repository.get(first_account.id).balance))
print("Second account balance is {!s}"
      .format(account_repository.get(second_account.id).balance))

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
    print("Something bad happened.")
    print()

account_repository = InMemoryRepository(store)
print("First account balance is {!s}"
      .format(account_repository.get(first_account.id).balance))
print("Second account balance is {!s}"
      .format(account_repository.get(second_account.id).balance))

merchant = ExternalCounterparty(owner=uuid.uuid4())
with work_manager.scope() as SCOPE:
    account_repository = SCOPE.get(InMemoryRepository)
    account_repository.add(merchant)

amount = AUD('2.5')
print()
print("Making a purchase if {!s} from the merchant to the first account."
      .format(amount))
print()

with work_manager.scope() as SCOPE:
    purchase_service = CardPurchaseService(SCOPE.get(InMemoryRepository))
    reference = uuid.uuid4()
    purchase_service.make_purchase(card_number=first_card.number,
                                   merchant=merchant.id,
                                   amount=amount,
                                   reference=reference)

account_repository = InMemoryRepository(store)
print("First account balance is {!s}"
      .format(account_repository.get(first_account.id).balance))
print("Merchant balance is {!s}"
      .format(account_repository.get(merchant.id).balance))

print()
print("Settling the transaction with reference {}.".format(reference))
print()

with work_manager.scope() as SCOPE:
    repo = SCOPE.get(InMemoryRepository)
    settlement_service = TransactionSettlementService(repo)
    settlement_service.settle_transaction(reference)

account_repository = InMemoryRepository(store)
print("First account balance is {!s}"
      .format(account_repository.get(first_account.id).balance))
print("Merchant balance is {!s}"
      .format(account_repository.get(merchant.id).balance))


amount = AUD('5.5')
print()
print("Making a purchase of {!s} from the merchant to the second card account."
      .format(amount))
print()

try:
    with work_manager.scope() as SCOPE:
        purchase_service = CardPurchaseService(SCOPE.get(InMemoryRepository))
        reference = uuid.uuid4()
        purchase_service.make_purchase(card_number=second_card.number,
                                       merchant=merchant.id,
                                       amount=amount,
                                       reference=reference)
except Exception as e:
    print("Got error: {}".format(e))
    print()

account_repository = InMemoryRepository(store)
print("First account balance is {!s}"
      .format(account_repository.get(first_account.id).balance))
print("First account is {}".format(account_repository.get(first_account.id)))
print("Merchant balance is {!s}"
      .format(account_repository.get(merchant.id).balance))
