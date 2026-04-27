#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UNIT_DIR="$HOME/.config/systemd/user"
ENV_DIR="$HOME/.config/sandy-chaos"
STATE_DIR="$HOME/.local/state/sandy-chaos"
SECRETS_FILE="$ROOT/.secrets.local.env"
SECRETS_TEMPLATE="$ROOT/.secrets.example.env"
ENABLE_NOW=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --enable-now)
      ENABLE_NOW=1
      shift
      ;;
    -h|--help)
      cat <<'EOF'
Usage: bash scripts/install_automation_timer.sh [--enable-now]

Install the Sandy Chaos user units and local env templates.
By default this does not enable the timer. Use --enable-now when you are
ready to start the timer after reviewing the activation stage in automation.env.
EOF
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 2
      ;;
  esac
done

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
# Activation gate for unattended automation
SANDY_AUTOMATION_STAGE=off
SANDY_AUTOMATION_AGENT=claude
SANDY_AUTOMATION_DISPATCH_LIMIT=1
SANDY_AUTOMATION_AGENT_TIMEOUT_SEC=600
SANDY_AUTOMATION_SEND_TELEGRAM=0

# Required for Telegram sends when explicitly enabled
OPENCLAW_TELEGRAM_BOT_TOKEN=
OPENCLAW_TELEGRAM_TARGET=
EOF
  chmod 600 "$ENV_DIR/automation.env"
  echo "Created $ENV_DIR/automation.env with automation stage defaulted to off."
fi

systemctl --user daemon-reload

if [[ "$ENABLE_NOW" -eq 1 ]]; then
  systemctl --user enable --now sandy-automation.timer
  # Force timer refresh when cadence changes
  systemctl --user restart sandy-automation.timer

  echo "Installed and started sandy-automation.timer"
  systemctl --user status sandy-automation.timer --no-pager || true

  echo
  echo "Next scheduled firings (probabilistic 4-6 minute window):"
  systemctl --user list-timers sandy-automation.timer --no-pager || true
else
  echo "Installed sandy-automation.service and sandy-automation.timer"
  echo "Timer is not enabled yet."
  echo
  echo "Next steps:"
  echo "1. Review $ENV_DIR/automation.env"
  echo "2. Keep SANDY_AUTOMATION_STAGE=off until preflight/design review is complete"
  echo "3. When ready, either:"
  echo "   - set SANDY_AUTOMATION_STAGE=preflight and run the service manually"
  echo "   - or rerun this script with --enable-now"
fi
