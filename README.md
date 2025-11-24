
کامل کپی کن بذار تو README.md گیت‌هاب 👇


---

# 🚀 Marz Node UI  
🛡️ Soft Delete Nodes + Hosts Safe + Xray SSH Manager

یک UI سبک و کاربردی برای مدیریت Nodeهای مرزنشین/مرزنود بدون اینکه با حذف Node، هاست‌ها پاک بشن.  
همچنین امکان مدیریت Xray از طریق SSH و دکمه ON/OFF برای docker compose.

---

## ✨ Features
✅ **Soft Delete واقعی برای Node‌ها**  
- وقتی Node رو حذف می‌کنی، حذف نمی‌شه  
- فقط **Disable** می‌شه  
- Hostها دست‌نخورده باقی می‌مونن ✅

✅ **تغییر IP / جابجایی Node بدون خراب شدن سرویس‌ها**  
فقط Node رو Edit کن، همه Hosts سالم می‌مونن 💙

✅ **Xray SSH Manager**
- اتصال SSH
- خواندن/ویرایش `xray/config.json`
- ذخیره داخل UI
- اجرای خودکار docker compose ✅

✅ **Docker ON/OFF**
- ON = `docker compose up -d`
- OFF = `docker compose down`
دیگه لازم نیست بری داخل سرور، nano بزنی و دستی Up/Down کنی 😄

✅ **Setup Wizard**
اولین بار UI رو باز کنی، یه صفحه نصب میاد و اطلاعات زیر رو می‌گیره:
- یوزرنیم/پسورد UI
- آدرس پنل مرزنشین
- یوزرنیم/پسورد ادمین پنل  
اطلاعات توی همین سرور داخل فایل ذخیره می‌شن:
`data/config.json`

---

## 📌 پیش‌نیازها
روی Ubuntu/Debian:

```bash
apt update
apt install -y python3 python3-venv python3-pip sshpass git


---

🔥 نصب و اجرا (بدون systemd)

1) دانلود پروژه

git clone https://github.com/lornaNET/marznode.git
cd marznode

2) ساخت venv و نصب پکیج‌ها

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

3) اجرای UI

source venv/bin/activate
python3 app.py

4) باز کردن در مرورگر

http://YOUR-SERVER-IP:9000

بعد از باز شدن، Setup Wizard میاد و اطلاعات پنل رو می‌گیری ✅


---

⚙️ نصب به صورت سرویس systemd (پیشنهادی)

1) فایل سرویس بساز

sudo nano /etc/systemd/system/marz-node-ui.service

2) اینو کامل داخلش کپی کن

[Unit]
Description=Marz Node UI (FastAPI + Uvicorn)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/marznode
Environment="PYTHONUNBUFFERED=1"

ExecStart=/root/marznode/venv/bin/uvicorn app:app --host 0.0.0.0 --port 9000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target

3) فعال و اجرا کن

sudo systemctl daemon-reload
sudo systemctl enable marz-node-ui.service
sudo systemctl restart marz-node-ui.service

✅ حالا UI همیشه روی سرور روشن می‌مونه.


---

🔄 آپدیت گرفتن از گیت‌هاب

cd /root/marznode
git pull
sudo systemctl restart marz-node-ui.service

اگر خطای overwrite فایل دادی، اینو بزن:

cd /root/marznode
git reset --hard origin/main
git pull
sudo systemctl restart marz-node-ui.service


---

🗂️ محل ذخیره تنظیمات

کل اطلاعات نصب داخل این فایل ذخیره می‌شه:

data/config.json

نمونه:

{
  "ui_username": "admin",
  "ui_password": "admin",
  "panel_url": "https://YOUR-PANEL-DOMAIN",
  "panel_admin_user": "PANEL-ADMIN-USER",
  "panel_admin_pass": "PANEL-ADMIN-PASS"
}


---

🧩 نصب پنل مرزنشین (Marzneshin)

📌 اول مرزنشین رو نصب کنید، بعد وارد UI بشید و اطلاعاتش رو داخل Setup Wizard وارد کنید ✅
(این UI خودش توکن ادمین رو از پنل می‌گیره و Node/Host ها رو می‌خونه.)


---

🧰 بکاپ گرفتن از سورس

برای بکاپ فولدر پروژه:

cd /opt
tar -czvf marz-node-ui-backup.tar.gz marznode


---

🆘 رفع ارورهای رایج

❌ TemplateNotFound: setup.html / login.html

یعنی سرویس از مسیر اشتباه اجرا شده.
systemd رو دقیقاً طبق README بالا بسازید (WorkingDirectory مهمه ✅)

❌ ModuleNotFoundError مثل requests یا itsdangerous

یعنی requirements نصب نشده:

cd marznode
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart marz-node-ui.service

❌ صفحه سفید / ERR_EMPTY_RESPONSE

سرویس بالا نیست. وضعیت رو چک کن:

sudo systemctl status marz-node-ui.service --no-pager
journalctl -u marz-node-ui.service -n 100 --no-pager


---

❤️ Support

اگر این ابزار بهت کمک کرد یه ⭐ به ریپو بده
برای توسعه هم Issue یا PR بذار 😄


---

Marz Node UI — Soft Delete Nodes, Keep Hosts Alive 💙

-
