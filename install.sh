#!/bin/bash
set -e

REPO_URL="https://github.com/lornaNET/marznode.git"
INSTALL_DIR="/root/marznode"
SERVICE_FILE="/etc/systemd/system/marz-node-ui.service"
PORT="9000"

echo "🚀 Installing Marz Node UI ..."

# 1) prerequisites
echo "📦 Installing prerequisites..."
apt update -y
apt install -y python3 python3-venv python3-pip sshpass git curl

# 2) clone or update
if [ -d "$INSTALL_DIR/.git" ]; then
  echo "🔄 Repo exists, updating..."
  cd "$INSTALL_DIR"
  git pull
else
  echo "📥 Cloning repo..."
  git clone "$REPO_URL" "$INSTALL_DIR"
  cd "$INSTALL_DIR"
fi

# 3) venv + requirements
echo "🐍 Setting up virtualenv..."
python3 -m venv venv
source venv/bin/activate

echo "📚 Installing python packages..."
if [ -f requirements.txt ]; then
  pip install -r requirements.txt || true
fi

# hard dependencies to avoid your past errors
pip install fastapi uvicorn jinja2 python-dotenv requests pydantic python-multipart itsdangerous

deactivate

# 4) systemd service
echo "🛠 Creating systemd service..."
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Marz Node UI (FastAPI + Uvicorn)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port $PORT
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 5) enable + start
echo "✅ Enabling and starting service..."
systemctl daemon-reload
systemctl enable marz-node-ui.service
systemctl restart marz-node-ui.service

echo ""
echo "🎉 Done!"
echo "🌍 Open: http://YOUR-SERVER-IP:$PORT/setup"
echo ""
echo "📌 Logs: journalctl -u marz-node-ui.service -n 200 --no-pager"
