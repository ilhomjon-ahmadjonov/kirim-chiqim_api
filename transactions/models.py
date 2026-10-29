from decimal import Decimal
from accounts.models import CustomUser
from django.core.validators import MinValueValidator
from django.db import models

MIN_AMOUNT = [MinValueValidator(Decimal("0.01"))]


class Currency(models.TextChoices):
    UZS = "UZS", "So'm"
    USD = "USD", "Dollar"
    EUR = "EUR", "Yevro"


class ExchangeRate(models.Model):
    currency = models.CharField(max_length=3, choices=Currency.choices, unique=True)
    rate_to_uzs = models.DecimalField(max_digits=18, decimal_places=4)
    updated_at = models.DateTimeField(auto_now=True)


class Account(models.Model):
    class Kind(models.TextChoices):
        CASH = "cash", "Naqd pul"
        CARD = "card", "Karta"
        CURRENCY = "currency", "Valyuta hisobi"

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="accounts")
    name = models.CharField(max_length=100)
    kind = models.CharField(max_length=10, choices=Kind.choices)
    currency = models.CharField(max_length=3, choices=Currency.choices)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))

    def __str__(self):
        return f"{self.name} ({self.currency})"


class IncomeType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class ExpenseType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Income(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="incomes")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="incomes")
    income_type = models.ForeignKey(IncomeType, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=MIN_AMOUNT)
    currency = models.CharField(max_length=3, choices=Currency.choices)
    amount_in_account = models.DecimalField(max_digits=14, decimal_places=2)
    amount_uzs = models.DecimalField(max_digits=18, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-date", "-id"]


class Expense(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="expenses")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="expenses")
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=MIN_AMOUNT)
    currency = models.CharField(max_length=3, choices=Currency.choices)
    amount_in_account = models.DecimalField(max_digits=14, decimal_places=2)
    amount_uzs = models.DecimalField(max_digits=18, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-date", "-id"]


class Transfer(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="transfers")
    source = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="outgoing_transfers")
    target = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="incoming_transfers")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    received_amount = models.DecimalField(max_digits=14, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)