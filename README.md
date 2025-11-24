

# 🚀 Marz Node UI

پنل سبک و سریع برای مدیریت **Node** و **Host** های مرزنشین، با قابلیت  
**Soft Delete واقعی بدون حذف Hosts** + مدیریت Xray از طریق SSH ✅

---

## ✨ Features

✅ **Soft Delete Safe**
- نود حذف واقعی نمی‌شود  
- فقط اسمش `[DISABLED]` می‌خورد و IP/Port عوض می‌شود  
- هیچ Host یا Inbound پاک نمی‌شود 💙

✅ **Node Edit بدون خراب شدن Hosts**
- IP عوض شد؟ سرور جدید گرفتی؟  
- فقط Edit کن و همه چیز سالم می‌ماند

✅ **SSH Xray Manager**
- ادیت مستقیم `config.json` داخل UI  
- اجرای خودکار `docker compose down/up`  
- دکمه‌های ON / OFF برای خاموش/روشن کردن نود

✅ **Setup Wizard**
- بار اول UI یک صفحه نصب می‌آورد  
- اطلاعات پنل مرزنشین و ورود UI را می‌گیریم  
- در فایل `data/config.json` ذخیره می‌شود

---
### 1) دانلود پروژه
```bash
git clone https://github.com/lornaNET/marznode.git
cd marznode

2) نصب پیش‌نیازها

apt update
apt install -y python3 python3-venv python3-pip sshpass git

3) ساخت محیط و نصب پکیج‌ها

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

4) اجرای UI

python3 app.py

## 📥 نصب Marz Node UI

### 1) دانلود پروژه
```bash
git clone https://github.com/lornaNET/marznode.git
cd marznode

2) نصب پیش‌نیازها

apt update
apt install -y python3 python3-venv python3-pip sshpass git

3) ساخت محیط و نصب پکیج‌ها

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

4) اجرای UI

python3 app.py

5) باز کردن در مرورگر

http://YOUR-SERVER-IP:9000


---

🧩 نصب پنل مرزنشین (Marzneshin)

بعد از نصب، اطلاعات پنل رو داخل Setup Wizard همین UI وارد کن ✅


---

🗂️ محل ذخیره تنظیمات

اطلاعات نصب و لاگین داخل این فایل ذخیره می‌شود:

marz-node-ui/data/config.json

نمونه:

{
  "ui_username": "admin",
  "ui_password": "admin",
  "panel_url": "https://YOUR-PANEL-DOMAIN",
  "panel_admin_user": "PANEL-ADMIN-USER",
  "panel_admin_pass": "PANEL-ADMIN-PASS"
}


---

🔄 بکاپ گرفتن از سورس

برای بکاپ فولدر پروژه:

cd /opt
tar -czvf marz-node-ui-backup.tar.gz marznode


---

❤️ Donate / Support

اگر این ابزار بهت کمک کرد خوشحال میشم ستاره بدی ⭐
و اگه خواستی توسعه‌ش بدیم، Issue بزار یا PR بده 😄


---

---

