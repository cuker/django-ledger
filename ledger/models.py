from django.db import models

from dagcategory.models import DAGCategory

from common import *

PRECISION = {'max_digits':12, 'decimal_places':2} #TODO configurable precision

class Account(DAGCategory):
    unit = models.CharField(max_length=5)
    balance = models.DecimalField(default=0, **PRECISION)
    type = models.CharField(max_length=1, choices=ACCT_CHOICES)

    modified = models.DateTimeField(auto_now=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    def _change_balance(self, amount):
        self.balance += amount
        if self.balance < 0:
            raise LedgerException("Transactions may not make the balance negative")
        self.parents().filter(type=self.type).update(balance=models.F('balance')+amount)
        self.save()

    def create_transaction(self, tx_type, other, amount):
        if amount < 0:
            raise LedgerException("Invalid amount")
        if other.type == self.type:
            raise LedgerException("Target acccount must be of different type")
        if self.unit != other.unit:
            raise LedgerException("Target acccount must be of same unit")
        if tx_type not in dict(TX_CHOICES):
            raise LedgerException("Unrecognized transaction type")
        if self.type == ACCT_CREDIT:
            credit_account = self
            debit_account = other
        elif self.type == ACCT_DEBIT:
            credit_account = other
            debit_account = self
        if tx_type == TX_DEPOSIT:
            credit_account._change_balance(amount)
            debit_account._change_balance(amount)
        elif tx_type == TX_WIDTHDRAW:
            credit_account._change_balance(-amount)
            debit_account._change_balance(-amount)
        elif tx_type == TX_CREDIT:
            credit_account._change_balance(amount)
            debit_account._change_balance(-amount)
        elif tx_type == TX_DEBIT:
            credit_account._change_balance(-amount)
            debit_account._change_balance(amount)
        return self.transactions.create(unit=self.unit,
                                        type=tx_type,
                                        credit_account=credit_account,
                                        debit_account=debit_account,
                                        amount=amount,
                                        credit_balance=credit_balance,
                                        debit_balance=debit_balance,)

class Transaction(models.Model):
    credit_account = models.ForeignKey(Account, related_name='credit_transactions')
    debit_account = models.ForeignKey(Account, related_name='debit_transactions')
    type = models.CharField(max_length=1, choices=TX_CHOICES)
    
    unit = models.CharField(max_length=5)
    amount = models.DecimalField(**PRECISION)
    
    credit_balance = models.DecimalField(**PRECISION)
    debit_balance = models.DecimalField(**PRECISION)

    created = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    
    def clean_amount(self):
        if self.amount < 0:
            raise ValidationError('Amount must be non-negative')

