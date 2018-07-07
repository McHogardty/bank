
import uuid

from account import Account, AccountRepository, AUD

amount = AUD('1')

account = Account(owner=uuid.uuid4())
print(account.balance)
AccountRepository.add(account)

print("Account is {}".format(account))

second_account = AccountRepository.get(account.id)

print()
print("Second account is {}".format(account))
print("Second account is account ? {}".format(second_account is account))
print("Second account equals account ? {}".format(second_account == account))

third_account = Account(id=account.id, owner=uuid.uuid4())

print()
print("Third account is {}".format(account))
print("Third account is account ? {}".format(third_account is account))
print("Third account equals account ? {}".format(third_account == account))

account.credit(AUD('5'))

print()
print("Credited account with $5.")
print()

print("Account is {}".format(account))

account.debit(AUD('2.5'))

print()
print("Debited account with $2.5.")
print()

print("Account is {}".format(account))

print("Second account is {}".format(second_account))
