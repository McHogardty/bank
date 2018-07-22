
from uuid import UUID, uuid4

from .account import CardAccount
from .values import AUD


class AccountTransferService:
    def __init__(self, repository):
        self.repository = repository

    def transfer(self, source: UUID = None, destination: UUID = None,
                 amount: AUD = None) -> None:
        if source is None:
            raise ValueError("Cannot transfer from a source of None.")

        if destination is None:
            raise ValueError("Cannot transfer to a destination of None.")

        if source == destination:
            raise ValueError("Cannot transfer to the same account.")

        if amount is None:
            raise ValueError("Cannot transfer an amount of None.")

        if isinstance(source, CardAccount):
            raise ValueError("Cannot debit a card account.")

        source_account = self.repository.get(source)
        destination_account = self.repository.get(destination)

        # The AccountRepository raises an exception if it does not exist.
        # This is mainly to make the type checker happy as this never occurs.
        assert source_account is not None
        assert destination_account is not None

        reference = uuid4()
        source_account.debit(amount, reference)
        destination_account.credit(amount, reference)

        self.repository.update(source_account)
        self.repository.update(destination_account)
