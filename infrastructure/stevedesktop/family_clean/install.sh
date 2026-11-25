#!/bin/bash
# install.sh - install rm-family-clean (the test lane's Screenshots cleaner) as a user timer on SteveDesktop. Rerunnable.
# Run on SteveDesktop from a checkout of this repo: bash infrastructure/stevedesktop/family_clean/install.sh
set -euo pipefail
H="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.local/state/rm-family-clean"
install -D -m 0644 "$H/rm-family-clean.service" "$HOME/.config/systemd/user/rm-family-clean.service"
install -D -m 0644 "$H/rm-family-clean.timer" "$HOME/.config/systemd/user/rm-family-clean.timer"
systemctl --user daemon-reload
systemctl --user enable --now rm-family-clean.timer
echo "installed: rm-family-clean.timer (user, every 6 h); reading ~/.local/state/rm-family-clean/check_ok.txt"
