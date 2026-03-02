#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UNIT_DIR="$HOME/.config/systemd/user"
ENV_DIR="$HOME/.config/sandy-chaos"
STATE_DIR="$HOME/.local/state/sandy-chaos"
SECRETS_FILE="$ROOT/.secrets.local.env"
SECRETS_TEMPLATE="$ROOT/.secrets.example.env"

mkdir -p "$UNIT_DIR" "$ENV_DIR" "$STATE_DIR"

cp "$ROOT/ops/systemd/sandy-automation.service" "$UNIT_DIR/"
cp "$ROOT/ops/systemd/sandy-automation.timer" "$UNIT_DIR/"

if [[ ! -f "$SECRETS_FILE" ]]; then
  if [[ -f "$SECRETS_TEMPLATE" ]]; then
    cp "$SECRETS_TEMPLATE" "$SECRETS_FILE"
  else
    cat > "$SECRETS_FILE" <<'EOF'
OPENCLAW_TELEGRAM_BOT_TOKEN=
OPENCLAW_TELEGRAM_TARGET=
EOF
  fi
  chmod 600 "$SECRETS_FILE"
  echo "Created $SECRETS_FILE (fill values before first send)."
fi

if [[ ! -f "$ENV_DIR/automation.env" ]]; then
  cat > "$ENV_DIR/automation.env" <<'EOF'
# Required for Telegram sends by automation service
OPENCLAW_TELEGRAM_BOT_TOKEN=
OPENCLAW_TELEGRAM_TARGET=
EOF
  echo "Created $ENV_DIR/automation.env (legacy fallback env)."
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
