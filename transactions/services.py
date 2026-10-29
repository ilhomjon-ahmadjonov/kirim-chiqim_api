from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError
from .models import Account, Currency, ExchangeRate, Expense, Income, Transfer

CENT = Decimal("0.01")


def rate_to_uzs(currency):
    if currency == Currency.UZS:
        return Decimal("1")
    try:
        return ExchangeRate.objects.get(currency=currency).rate_to_uzs
    except ExchangeRate.DoesNotExist:
        raise ValidationError({"currency": f"{currency} uchun kurs kiritilmagan"})


def convert(amount, from_cur, to_cur):
    amount = Decimal(amount)
    if from_cur == to_cur:
        return amount.quantize(CENT)
    amount_uzs = amount * rate_to_uzs(from_cur)
    return (amount_uzs / rate_to_uzs(to_cur)).quantize(CENT, rounding=ROUND_HALF_UP)


@transaction.atomic
def create_income(*, owner, account, income_type, amount, currency, date, description=""):
    account = Account.objects.select_for_update().get(pk=account.pk)
    amount_in_account = convert(amount, currency, account.currency)

    Account.objects.filter(pk=account.pk).update(balance=F("balance") + amount_in_account)

    return Income.objects.create(
        owner=owner, account=account, income_type=income_type,
        amount=amount, currency=currency,
        amount_in_account=amount_in_account,
        amount_uzs=convert(amount, currency, Currency.UZS),
        date=date, description=description,
    )


@transaction.atomic
def create_expense(*, owner, account, expense_type, amount, currency, date, description=""):
    account = Account.objects.select_for_update().get(pk=account.pk)
    amount_in_account = convert(amount, currency, account.currency)

    if account.balance < amount_in_account:
        raise ValidationError({"amount": "Hisobda mablag' yetarli emas"})

    Account.objects.filter(pk=account.pk).update(balance=F("balance") - amount_in_account)

    return Expense.objects.create(
        owner=owner, account=account, expense_type=expense_type,
        amount=amount, currency=currency,
        amount_in_account=amount_in_account,
        amount_uzs=convert(amount, currency, Currency.UZS),
        date=date, description=description,
    )


@transaction.atomic
def create_transfer(*, owner, source, target, amount):
    
    locked = {
        a.pk: a for a in
        Account.objects.select_for_update().filter(pk__in=[source.pk, target.pk]).order_by("pk")
    }
    source, target = locked[source.pk], locked[target.pk]

    if source.balance < amount:
        raise ValidationError({"amount": "Hisobda mablag' yetarli emas"})

    received = convert(amount, source.currency, target.currency)

    Account.objects.filter(pk=source.pk).update(balance=F("balance") - amount)
    Account.objects.filter(pk=target.pk).update(balance=F("balance") + received)

    return Transfer.objects.create(
        owner=owner, source=source, target=target,
        amount=amount, received_amount=received,
    )