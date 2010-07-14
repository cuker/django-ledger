from django.db import models
from django.conf import settings

from dagcategory.models import DAGCategory

from common import *

PRECISION = getattr(settings, 'LEDGER_PRECISION', {'max_digits':12, 'decimal_places':2})

class AccountManager(models.Manager):
    def create_transaction(self, credit_account, debit_account, amount):
        """
        credit_account: the account to credit
        debit_account: the account to debit
        amount: a nonnegative number
        """
        if amount < 0:
            raise LedgerException("Invalid amount")
        if credit_account.polarity == debit_account.polarity:
            raise LedgerException("Both accounts may not be of same type")
        if credit_account.unit != debit_account.unit:
            raise LedgerException("Both accounts must be of same unit")
        credit_account._credit(amount)
        debit_account._debit(amount)
        transaction_type = credit_account.credit_transactions.model
        return transaction_type(unit=self.unit,
                                credit_account=credit_account,
                                debit_account=debit_account,
                                amount=amount,
                                credit_balance=credit_acount.balance,
                                debit_balance=debit_acount.balance,)

class Account(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    unit = models.CharField(max_length=5)
    balance = models.DecimalField(default=0, **PRECISION)
    polarity = models.CharField(max_length=1, choices=ACCT_CHOICES)
    enforce_positive_balance = models.BooleanField(default=False)

    modified = models.DateTimeField(auto_now=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    objects = AccountManager()

    def _change_balance(self, amount):
        self.balance += amount
        if self.enforce_positive_balance and self.balance < 0:
            raise LedgerException("Transactions may not make the balance negative")
        self.save()
    
    def _credit(self, amount):
        if self.polarity == ACCT_DEBIT:
            amount *= -1
        self._change_balance(amount)
    
    def _debit(self, amount):
        if self.polarity == ACCT_CREDIT:
            amount *= -1
        self._change_balance(amount)
    
    #TODO consider a public method for debiting or crediting?

class Transaction(models.Model):
    credit_account = models.ForeignKey(Account, related_name='credit_transactions')
    debit_account = models.ForeignKey(Account, related_name='debit_transactions')
    
    unit = models.CharField(max_length=5)
    amount = models.DecimalField(**PRECISION)
    
    credit_balance = models.DecimalField(**PRECISION)
    debit_balance = models.DecimalField(**PRECISION)

    created = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    
    def clean_amount(self):
        if self.amount < 0:
            raise ValidationError('Amount must be non-negative')

class AccountCategory(DAGCategory):
    """
    Purely for organizing our accounts in a manner to help us analyze our accounting data
    """
    accounts = models.ManyToManyField(Account, blank=True)
    
    def all_accounts(self):
        return self._all_subitems(Account.objects.all(), 'accountcategory')

    def all_credit_transactions(self):
        return self._all_subitems(Transaction.objects.all(), 'credit_account__accountcategory')

    def all_debit_transactions(self):
        return self._all_subitems(Transaction.objects.all(), 'debit_account__accountcategory')
    
    def all_transactions(self):
        return self.all_credit_transactions() | self.all_debit_transactions()

    def get_balance(self):
        return self.all_accounts().aggregate(models.Sum('balance'))['balance']
    
