# Kirim-Chiqim API

Kirim, chiqim, hisoblar, valyuta konvertatsiyasi va statistika uchun Django REST Framework asosidagi API. Valyuta kurslari O'zbekiston Respublikasi Markaziy bankidan (cbu.uz) olinadi.

## Imkoniyatlar

- Token asosida autentifikatsiya, ikki rol: `admin` va `user`
- Naqd pul, karta va valyuta hisoblari (UZS, USD, EUR)
- Kirim va chiqimlarni turlari bo'yicha yuritish
- Kirim va chiqim summasini hisob valyutasiga avtomatik konvertatsiya qilish
- Hisoblar orasida o'tkazma (valyuta konvertatsiyasi bilan)
- Umumiy balansni istalgan valyutada ko'rish
- Oylik statistika: turlar bo'yicha summa va foiz
- Atomic tranzaksiyalar: balans va yozuv doim birga saqlanadi
- Swagger hujjati va Postman collection

## Texnologiyalar

- Python 3.12, Django 6.1, Django REST Framework
- PostgreSQL 16
- Docker va docker compose
- drf-yasg (Swagger), django-filter, python-dotenv, requests

## Loyiha tuzilmasi
## O'rnatish va ishga tushirish

### Talablar

- Python 3.12 yoki yuqori
- PostgreSQL 16 (lokal ishga tushirish uchun)
- Docker va docker compose (Docker variant uchun)

### 1. Paketlarni o'rnatish (lokal)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

python -m pip install -r requirements.txt
```

### 2. `.env` faylini sozlash

```bash
cp .env.example .env
```

Qiymatlarni to'ldiring (`DJANGO_SECRET_KEY`, `POSTGRES_PASSWORD` va boshqalar).

### 3. Ma'lumotlar bazasini tayyorlash

```bash
python manage.py migrate
python manage.py seed_users
python manage.py runserver
```

Server ishga tushgach: http://127.0.0.1:8000/swagger/

### Docker orqali ishga tushirish

```bash
docker compose up --build
```

Migratsiyalar va test foydalanuvchilari konteyner ishga tushganda avtomatik yaratiladi.

### Kurslarni yuklash

```bash
python manage.py update_rates
```
