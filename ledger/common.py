class LedgerException(Exception):
    pass

TX_CREDIT = 'C'
TX_DEBIT = 'D'
TX_WITHDRAW = 'W'
TX_DEPOSIT = 'A'

TX_CHOICES = (
    (TX_CREDIT, 'Credit'),
    (TX_DEBIT, 'Debit'),
    (TX_WITHDRAW, 'Withdraw'),
    (TX_DEPOSIT, 'Deposit'),
)

ACCT_DEBIT = 'D'
ACCT_CREDIT = 'C'

ACCT_CHOICES = (
    (ACCT_DEBIT, 'Debit Account'),
    (ACCT_CREDIT, 'Credit Account'),
)
