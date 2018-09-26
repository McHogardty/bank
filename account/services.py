
from uuid import UUID, uuid4

from .values import AUD, CardNumber


class AccountTransferService:
    """A service for transferring money between accounts."""

    def __init__(self, repository):
        self.repository = repository

    def transfer(self, source: UUID = None, destination: UUID = None,
                 amount: AUD = None) -> None:
        """Transfer money from a source account to a destination account.

        Takes the following arguments:
        - source: The ID of the source account.
        - destination: The ID of the destination account.
        - amount: The amount to transfer.

        """

        if source is None:
            raise ValueError("Cannot transfer from a source of None.")

        if destination is None:
            raise ValueError("Cannot transfer to a destination of None.")

        if source == destination:
            raise ValueError("Cannot transfer to the same account.")

        if amount is None:
            raise ValueError("Cannot transfer an amount of None.")

        source_account = self.repository.get(source)
        destination_account = self.repository.get(destination)

        # The AccountRepository raises an exception if it does not exist.
        # This is mainly to make the type checker happy as this never occurs.
        assert source_account is not None
        assert destination_account is not None

        reference = uuid4()
        source_account.debit(amount, reference)
        destination_account.credit(amount, reference)

        source_account.settle(reference)
        destination_account.settle(reference)

        self.repository.update(source_account)
        self.repository.update(destination_account)


class CardPurchaseService:
    """A service for facilitating purchases involving cards."""

    def __init__(self, repository):
        self.repository = repository

    def make_purchase(self, card_number: CardNumber = None,
                      merchant: UUID = None,
                      amount: AUD = None,
                      reference: UUID = None) -> None:
        """Record a purchase for a card.

        Takes the following arguments:
        - card_number: The card number for the card.
        - merchant: The ID of the merchant account.
        - amount: The amount being transferred.
        - reference: The reference for the purchase.

        """

        if card_number is None:
            raise ValueError("Cannot make a purchase on a card account of "
                             "None.")

        if merchant is None:
            raise ValueError("Cannot make a payment to a merchant of None.")

        if amount is None:
            raise ValueError("Cannot make a purchase of an amount of None.")

        if reference is None:
            raise ValueError("Cannot make a purchase without a reference.")

        account = self.repository.find_by_card_number(card_number)

        merchant_account = self.repository.get(merchant)

        account.debit_card(card_number=card_number,
                           amount=amount,
                           reference=reference)
        merchant_account.credit(amount=amount,
                                reference=reference)

        self.repository.update(account)
        self.repository.update(merchant_account)


class TransactionSettlementService:
    """A service for settling transactions."""

    def __init__(self, repository):
        self.repository = repository

    def settle_transaction(self, reference: UUID = None) -> None:
        """Settle the transactions associated with a particular reference.

        Takes one argument:
        - The reference for the transactions to settle.

        """

        if reference is None:
            raise ValueError("Cannot settle a transaction with no reference.")

        accounts = self.repository.find_by_transaction_reference(reference)

        for account in accounts:
            account.settle(reference)
            self.repository.update(account)
