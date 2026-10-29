from decimal import Decimal
import requests
from django.db import transaction
from .models import ExchangeRate

CBU_URL = "https://cbu.uz/ru/arkhiv-kursov-valyut/json/"
SUPPORTED = ("USD", "EUR")


def update_rates_from_cbu():
    response = requests.get(CBU_URL, timeout=10)
    response.raise_for_status()

    updated = {}
    with transaction.atomic():
        for item in response.json():
            code = item.get("Ccy")
            if code not in SUPPORTED:
                continue
            # Ba'zi valyutalar 100 birlik bo'yicha beriladi, shuning uchun Nominal bilan bo'lamiz
            rate = (Decimal(item["Rate"]) / Decimal(item["Nominal"])).quantize(Decimal("0.0001"))
            ExchangeRate.objects.update_or_create(currency=code, defaults={"rate_to_uzs": rate})
            updated[code] = str(rate)
    return updated