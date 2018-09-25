# Domain rules and definitions for the account and transaction entities

## Money
 * Money is represented using the AUD value object.

## Transactions
 * A transaction is a unit of exchange of money, representing the movement of money from one owner to another.
 * A transaction may be recorded against as either a debit or a credit. A debit represents a reduction in the owner's money, and a credit represents an increase.
 * A transaction has an associated amount, which is assumed to be in Australian dollars (AUD).
 * A transaction amount is represented as a decimal to two significant figures.
 * Transactions are recording using a system known as 'double-entry bookkeeping'. Every transfer of money is recorded as a debit against one account and a credit against another.
 * The credit and debit of a transaction are linked by a transaction reference, which is a unique identifier. External stakeholders will identify a transaction based on this reference.

## Accounts
 * An account is a collection of transactions.
 * An account has a balance, which is the sum of all of the transactions recorded against this account. Simply, balance = sum(credit transactions) - sum(debit transactions)
 * The balance is assumed to be in Australian dollars (AUD).
 * The balance is represented as a decimal.
 * An account has an owner, representing the entity to whom the money contained in the account belongs.
 * There are two types of accounts: regular, card and external counterparty accounts.
   * Regular accounts exist within the bank for representing a customer's money.
   * External counterparty accounts represent external accounts which are debited or credited as a result of a corresponding debit or credit to an account within the bank. These external counterparty accounts exist for the purpose of double-entry bookkeeping.
 * A regular account may not be in arrears (i.e. it may not ever have a negative balance).
 * As a tool for record keeping, external counterparty account balances are not restricted.


   * Card accounts have a linked magnetic stripe card which can be used to make purchases. A card account has an associated Card entity.

## Subaccounts
 * An account actually consists of one or more subaccounts, which provide logical groupings for the transactions contained within an account.
 * Subaccounts are not discretely visible to the user - they only form part of an account.
 * The account which contains a specific subaccount is known as the parent account of that subaccount.
 * The parent account does not contain any transactions.
 * Subaccounts have a balance which contributes to the balance of the parent account.
 * Subaccounts may have a negative balance.
 * Transactions which contribute to the balance of the subaccount also contribute to the balance of the parent account.
 * If a parent account may not be overdrawn, this rule applies to any transaction in a subaccount.
 * Example subaccounts include:
    - RegularSubAccount: No special attributes. Simply a group of transactions.
    - CardSubAccount: these have a linked magnetic stripe card which can be used to make purchases. A card account has an associated Card entity
 * An account has a default subaccount, which is the default subaccount that is debited or credited during a transaction, unless otherwise specified.

## Account transfers
 * Money may be transferred between accounts.
 * An account may not have money transferred to itself (as this ends up being a null operation).

## Card purchases
 * Cards may be used at EFTPOS terminals to make a purchase.
 * When this occurs, the associated subaccount is debited by the purchase amount.
