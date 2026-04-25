# 📚 Online Kutibxona (Raqamli Kutubxona)

Zamonaviy maktablar uchun mo'ljallangan, QR-kod tizimi orqali ishlaydigan aqlli kutubxona boshqaruv tizimi.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Django](https://img.shields.io/badge/django-5.0%2B-green.svg)

## ✨ Asosiy imkoniyatlar

*   🛡️ **Xavfsiz dinamik QR-kodlar:** Har 2 daqiqada yangilanadigan xavfsiz identifikatsiya tizimi.
*   👨‍💼 **Ko'p darajali boshqaruv:**
    *   **Super Admin:** Barcha maktablarni va muassasalarni nazorat qilish.
    *   **Maktab Admini (Kutubxonachi):** Kitoblar fondini boshqarish, o'quvchilarni ro'yxatga olish va kitob berish/qabul qilish.
    *   **O'quvchi/O'qituvchi:** Kitoblarni qidirish, bron qilish va shaxsiy kabinet orqali o'z kitoblarini kuzatish.
*   🎨 **Premium Dizayn:** Zamonaviy "Glassmorphism" uslubidagi va "Library Amber" mavzusidagi qulay interfeys.
*   📸 **Kamera bilan ishlash:** Mobil qurilmalar orqali kitob muqovalarini suratga olish va yuklash.
*   📊 **Real-vaqt statistikasi:** Kitoblar aylanishi va o'quvchilar faolligini tahlil qilish.
*   🌍 **Ko'p tilli qo'llab-quvvatlash:** O'zbek, Rus va Ingliz tillari.

## 🏗️ Loyiha strukturasi (Architecture)

Loyiha modulli arxitekturaga asoslangan bo'lib, har bir rol uchun alohida frontend ilovalari mavjud:

```text
elektronKUTIBXAN/
├── backend/                  # Django asosiy loyiha papkasi
│   ├── core/                 # Sozlamalar va global marshrutlash
│   ├── accounts/             # Foydalanuvchilar, rollar va xavfsizlik (HMAC Tokens)
│   ├── schools/              # Maktablar va muassasalar bazasi
│   ├── books/                # Kitoblar katalogi, inventar va ijara tizimi
│   ├── stats/                # Tizim loglari va tahliliy ma'lumotlar
│   ├── frontend_admin/       # Super Admin interfeysi (Django Templates)
│   ├── frontend_school/      # Maktab Admini/Kutubxonachi interfeysi
│   ├── frontend_user/        # O'quvchi va O'qituvchi interfeysi
│   ├── static/               # Global CSS/JS va dizayn aktivlari
│   └── templates/            # Umumiy va asosiy shablonlar (Base layouts)
├── scripts/                  # Avtomatlashtirish skriptlari
│   ├── seed_demo.py          # Demo ma'lumotlarni yaratish
│   ├── make_translations.py  # Tarjimalarni avtomatlashtirish
│   └── fix_roles.py          # Rollarni tekshirish va tuzatish
├── media/                    # Yuklangan rasmlar va QR-kodlar (Git-da saqlanmaydi)
├── Dockerfile                # Docker sozlamalari
└── README.md                 # Loyiha hujjatlari
```

## 🛠️ Texnologiyalar

*   **Backend:** Python 3.12, Django 5.0, PostgreSQL
*   **Frontend:** Vanilla JS, HTML5, CSS3 (Glassmorphism design)
*   **QR System:** qrcode (python) + html5-qrcode (JS)
*   **UI Framework:** Jazzmin (Admin panel uchun)

## 🚀 O'rnatish

1.  **Loyiha nusxasini olish:**
    ```bash
    git clone https://github.com/username/elektron-kutibxona.git
    cd elektron-kutibxona
    ```

2.  **Virtual muhitni sozlash:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows uchun: venv\Scripts\activate
    ```

3.  **Kutubxonalarni o'rnatish:**
    ```bash
    pip install -r backend/requirements.txt
    ```

4.  **Bazani tayyorlash:**
    ```bash
    cd backend
    python manage.py migrate
    ```

5.  **Admin foydalanuvchi yaratish:**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Loyihani ishga tushirish:**
    ```bash
    python manage.py runserver
    ```

## 📜 Foydali buyruqlar (Scripts)

Loyiha ildiz papkasidagi `scripts/` papkasida foydali skriptlar mavjud:

*   **Demo ma'lumotlar yuklash:** `python scripts/seed_demo.py`
*   **Tarjimalarni yangilash:** `python scripts/make_translations.py`
*   **Rollar xatosini tuzatish:** `python scripts/fix_roles.py`

## 📄 Litsenziya

Ushbu loyiha MIT litsenziyasi ostida tarqatiladi.

---
Developed with ❤️ for Modern Schools.
