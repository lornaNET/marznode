#!/bin/bash
set -e

INSTALL_DIR="/root/marznode"
SERVICE_FILE="/etc/systemd/system/marz-node-ui.service"

echo "🧨 Uninstalling Marz Node UI ..."

# stop + disable service if exists
if systemctl list-units --full -all | grep -q "marz-node-ui.service"; then
  echo "⛔ Stopping service..."
  systemctl stop marz-node-ui.service || true
  systemctl disable marz-node-ui.service || true
fi

# remove service file
if [ -f "$SERVICE_FILE" ]; then
  echo "🗑 Removing systemd service..."
  rm -f "$SERVICE_FILE"
  systemctl daemon-reload
  systemctl reset-failed
fi

# remove install dir
if [ -d "$INSTALL_DIR" ]; then
  echo "🗑 Removing project files..."
  rm -rf "$INSTALL_DIR"
fi

echo "✅ Marz Node UI fully removed."
