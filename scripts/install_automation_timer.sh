#!/usr/bin/env bash
set -euo pipefail

ROOT="${REPO_ROOT}"
UNIT_DIR="$HOME/.config/systemd/user"
ENV_DIR="$HOME/.config/sandy-chaos"
STATE_DIR="$HOME/.local/state/sandy-chaos"

mkdir -p "$UNIT_DIR" "$ENV_DIR" "$STATE_DIR"

cp "$ROOT/ops/systemd/sandy-automation.service" "$UNIT_DIR/"
cp "$ROOT/ops/systemd/sandy-automation.timer" "$UNIT_DIR/"

if [[ ! -f "$ENV_DIR/automation.env" ]]; then
  cat > "$ENV_DIR/automation.env" <<'EOF'
# Required for Telegram sends by automation service
OPENCLAW_TELEGRAM_BOT_TOKEN=
EOF
  echo "Created $ENV_DIR/automation.env (fill token before first send)."
fi

systemctl --user daemon-reload
systemctl --user enable --now sandy-automation.timer
# Force timer refresh when cadence changes
systemctl --user restart sandy-automation.timer

echo "Installed and started sandy-automation.timer"
systemctl --user status sandy-automation.timer --no-pager || true

echo
echo "Next scheduled firings (probabilistic 4-6 minute window):"
systemctl --user list-timers sandy-automation.timer --no-pager || true
