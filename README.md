

🚀 Marz Node UI

پنل مدیریت نودهای Marzneshin با قابلیت Soft Delete واقعی و کنترل مستقیم Xray روی نودها از طریق SSH.

✅ حذف نود بدون حذف Hosts
✅ غیرفعال‌سازی نود با تغییر اسم + IP رندوم (بدون ارور تکراری)
✅ ویرایش و مدیریت Hosts
✅ ادیت و نمایش config.json نود از راه دور
✅ دکمه‌های ON / OFF برای docker compose نود
✅ پنل نصب اولیه داخل وب (Setup Wizard)
✅ بدون نیاز به ورود دستی به سرور و nano و docker up/down 😄


---

✨ Features

Soft Delete Safe

نود حذف نمی‌شود، فقط:

اسمش [DISABLED] می‌گیرد

IP رندوم 127.0.0.x می‌گیرد

port = 0 و usage_coefficient = 0 می‌شود


هیچ هاستی پاک نمی‌شود و ساختار پنل بهم نمی‌ریزد.


SSH Xray Manager

خواندن و ذخیره xray/config.json

نمایش مرتب JSON داخل UI

اجرای خودکار docker compose بعد از ذخیره

دکمه‌های:

ON: docker compose up -d

OFF: docker compose down



Setup Wizard

اولین بار که UI بالا میاد، صفحه نصب می‌بینی و اطلاعات رو وارد می‌کنی:

آدرس پنل مرزنشین

یوزرنیم/پسورد ادمین پنل

یوزرنیم/پسورد ورود به UI


اطلاعات داخل فایل ذخیره میشه:

data/config.json





---

🧩 پیش‌نیازها

روی سروری که UI رو اجرا می‌کنی:

1) Python 3.10+

python3 --version

2) نصب پکیج‌ها (اگه Docker نمی‌خوای)

apt update
apt install -y python3-venv python3-pip sshpass git

> sshpass لازمه برای SSH و SCP بدون سوال پسورد.




---

🛠️ نصب (روش سریع بدون Docker)

1) کلون پروژه

cd /opt
git clone https://github.com/YOUR-USER/marz-node-ui.git
cd marz-node-ui

2) ساخت venv و نصب نیازمندی‌ها

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

3) اجرای برنامه

uvicorn app:app --host 0.0.0.0 --port 9000

حالا تو مرورگر بزن:

http://YOUR-SERVER-IP:9000

✅ اولین بار صفحه نصب (Setup) میاد.
اطلاعات رو وارد کن و Save بزن.
بعدش UI اصلی بالا میاد.


---

🐳 نصب با Docker (پیشنهادی)

1) کلون

cd /opt
git clone https://github.com/YOUR-USER/marz-node-ui.git
cd marz-node-ui

2) اجرا

docker compose up -d --build

✅ برو تو مرورگر:

http://YOUR-SERVER-IP:9000


---

⚙️ فایل کانفیگ

بعد از Setup، اطلاعات اینجا ذخیره میشه:

data/config.json

{
  "ui_username": "admin",
  "ui_password": "admin",
  "panel_url": "https://your-panel.com",
  "panel_admin_user": "admin_user",
  "panel_admin_pass": "admin_pass"
}

> این فایل رو تو گیت نذار. داخل .gitignore هست.




---

🔐 نکات امنیتی

این پروژه برای استفاده شخصی ساخته شده؛ بهتره:

پشت Cloudflare Access / Basic Auth / VPN بذاری

یا حداقل IP محدود کنی


پسورد پنل و UI داخل data/config.json ذخیره میشه.
پس فقط خودت به سرور دسترسی داشته باشی.



---

🧯 بکاپ گرفتن

برای بکاپ کامل از سورس:

cd /opt
tar -czvf marz-node-ui-backup-$(date +%F).tar.gz marz-node-ui


---

❓ سوال رایج: “توکن داک می‌خواد؟”

نه.
این UI مستقیم با ادمین پنل مرزنشین لاگین می‌کنه و از API خودش توکن می‌گیره.
پس هر کاربری که نصب کنه فقط کافیه اطلاعات پنل خودش رو تو Setup وارد کنه ✅


---

📌 مسیرهای مهم

UI Project:
/opt/marz-node-ui

Node Base Dir:
/opt/marznode/<label>/xray/config.json

Docker restart node:
docker compose -f docker-compose.yml down && up -d



---

🤝 Contribute

اگه باگ دیدی یا فیچر خواستی:

Issue بزن

یا Pull Request بده
خوشحال میشم پروژه بهتر بشه 💙



---

🌟 Credits

Built with FastAPI + Jinja2 + ❤️
For Marzneshin Node management without host deletion disasters 😄


---
اگه خواستی همین README رو یه نسخه انگلیسی
