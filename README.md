
🚀 Marz Node UI

پنل سبک و سریع برای مدیریت نودهای Marzneshin با Soft Delete واقعی
بدون اینکه Hosts یا Inbounds حذف بشن 💙


---

✨ چی کار می‌کنه؟

✅ Soft Delete Safe

وقتی توی مرزنشین نود رو Delete می‌کنی، هاست‌ها هم پاک می‌شن و همه‌چی می‌ریزه بهم 😑
اینجا فقط نود غیرفعال (Disable) می‌شه:

نود حذف واقعی نمی‌شه

اسم نود [DISABLED] می‌گیره

IP رندوم از رنج 127.0.0.X می‌خوره

port = 0

usage_coefficient = 0

هیچ Host/Inbound ای حذف یا خراب نمی‌شه



---

✅ Node Edit بدون دردسر

IP عوض شد یا سرور جدید گرفتی؟
فقط نودو Edit کن، سرویس‌ها سالم می‌مونن ✅


---

✅ SSH Xray Manager

داخل خود UI می‌تونی:

config.json رو از نود بخونی

همونجا ادیتش کنی

Save بزنی تا خودش اتومات:

فایل رو بفرسته روی سرور

docker compose down/up بزنه



👑 یعنی دیگه لازم نیست:

بری سرور

nano بزنی

docker دستی بالا پایین کنی



---

✅ Setup Wizard (اولین اجرا)

وقتی اولین بار UI رو باز می‌کنی، یه صفحه نصب میاد و اطلاعات رو می‌گیره:

یوزر/پس ورود به UI

آدرس پنل مرزنشین

یوزر/پس ادمین پنل مرزنشین


همه چی توی این فایل ذخیره می‌شه:

data/config.json


---

📦 نصب (بدون Docker)

1) کلون پروژه

cd /opt
git clone https://github.com/lornaNET/marznode.git
cd marznode

2) نصب پیش‌نیازها

apt update
apt install -y python3 python3-venv python3-pip sshpass git

3) ساخت venv و نصب پکیج‌ها

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

4) اجرای UI

python3 app.py

حالا برو تو مرورگر:

http://YOUR-SERVER-IP:9000


---

⚙️ اجرا به صورت سرویس (Systemd)

فایل سرویس بساز:

nano /etc/systemd/system/marz-node-ui.service

محتوا:

[Unit]
Description=Marz Node UI
After=network.target

[Service]
WorkingDirectory=/opt/marznode
ExecStart=/opt/marznode/venv/bin/python app.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target

فعال‌سازی:

systemctl daemon-reload
systemctl enable marz-node-ui
systemctl start marz-node-ui
systemctl status marz-node-ui


---

🧪 بکاپ گرفتن از سورس

برای بکاپ کامل پوشه پروژه:

cd /opt
tar -czvf marznode-backup.tar.gz marznode

برای ریستور:

cd /opt
tar -xzvf marznode-backup.tar.gz


---

🛡️ امنیت

اطلاعات ورود فقط داخل data/config.json ذخیره می‌شن

هیچ چیزی داخل سورس هاردکد نیست

مناسب برای انتشار عمومی ✅



---

🇬🇧 English (Short)

Marz Node UI

A lightweight web UI for Marzneshin nodes with real Soft Delete.

Soft Delete:

Node is not removed

Renamed to [DISABLED]

IP randomizes to 127.0.0.X

port=0, usage_coefficient=0

Hosts/Inbounds stay safe


SSH Xray Manager: Edit xray/config.json directly in UI and auto restart docker compose.

Setup Wizard: On first run, asks for:

UI login

panel URL

panel admin credentials
Saved in data/config.json.
