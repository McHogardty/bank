# Domain rules and definitions for the account and transaction entities

## Money
 * Money is represented using the AUD value object.

## Accounts
 * An account is a record of exchanges of money, called transactions.
 * An account has a balance, which is the sum of all of the transactions recorded against this account. Simply, balance = sum(credit transactions) - sum(debit transactions)
 * The balance is assumed to be in Australian dollars (AUD).
 * The balance is represented as a decimal to two significant figures.
 * An account has an owner, representing the entity to whom the money contained in the account belongs.

## Transactions
 * A transaction is a unit of exchange of money, representing the movement of money from one owner to another.
 * A transaction may be recorded against an account as either a debit or a credit. A debit represents a reduction in the owner's money in that account, and a credit represents an increase in the amount of money in the owner's account.
 * A transaction has an associated amount, which is assumed to be in Australian dollars (AUD).
 * A transaction amount is represented as a decimal to two significant figures.
