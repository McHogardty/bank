# Domain rules and definitions for the account and transaction entities

## Money
 * Money is represented using the AUD value object.

## Transactions
 * A transaction is a unit of exchange of money, representing the movement of money from one owner to another.
 * A transaction may be recorded against as either a debit or a credit. A debit represents a reduction in the owner's money, and a credit represents an increase.
 * A transaction has an associated amount, which is assumed to be in Australian dollars (AUD).
 * A transaction amount is represented as a decimal to two significant figures.
 * Transactions are recording using a system known as 'double-entry bookkeeping'. Every transfer of money is recorded as a debit against one account and a credit against another.
 * The credit and debit of a transaction are linked by a transaction reference, which is a unique identifier. External stakeholders will identify a transaction based on
 this reference.

## Accounts
 * An account is a record of exchanges of money, called transactions.
 * An account has a balance, which is the sum of all of the transactions recorded against this account. Simply, balance = sum(credit transactions) - sum(debit transactions)
 * The balance is assumed to be in Australian dollars (AUD).
 * The balance is represented as a decimal to two significant figures.
 * An account has an owner, representing the entity to whom the money contained in the account belongs.
 * There are two types of accounts: regular and external counterparty accounts.
   * Regular accounts exist within the bank for representing a customer's money.
   * External counterparty accounts represent external accounts which are debited or credited as a result of a corresponding debit or credit to an account within the bank. These external counterparty accounts exist for the purpose of double-entry bookkeeping.
 * A regular account may not be in arrears (i.e. it may not ever have a negative balance).
 * As a tool for record keeping, external counterparty account balances are not restricted.

## Account transfers
 * Money may be transferred between accounts.
 * An account may not have money transferred to itself (as this ends up being a null operation).
