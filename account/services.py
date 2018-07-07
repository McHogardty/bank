
from uuid import UUID

from .repository import AccountRepository
from .values import AUD


class AccountTransferService:
    @classmethod
    def transfer(cls, source: UUID = None, destination: UUID = None,
                 amount: AUD = None) -> None:
        if source is None:
            raise ValueError("Cannot transfer from a source of None.")

        if destination is None:
            raise ValueError("Cannot transfer to a destination of None.")

        if source == destination:
            raise ValueError("Cannot transfer to the same account.")

        if amount is None:
            raise ValueError("Cannot transfer an amount of None.")

        source_account = AccountRepository.get(source)
        destination_account = AccountRepository.get(destination)

        # The AccountRepository raises an exception if it does not exist.
        # This is mainly to make the type checker happy as this never occurs.
        assert source_account is not None
        assert destination_account is not None

        source_account.debit(amount)
        destination_account.credit(amount)
