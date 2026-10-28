#!/usr/bin/env bash
# Set up mutation testing on SteveDesktop WSL (idempotent). Run ON Steve from a checkout of this repo:
#   bash infrastructure/stevedesktop/mutation/install_mutation.sh
# Makes ~/mutation/RimMandrake (its OWN clone -- never ~/rm/runner, never a seat clone), ~/mutation/venv pinned to
# infrastructure/stevedesktop/mutation_requirements.txt (WSL python, not Windows python.exe), copies the slice,
# service and timer into ~/.config/systemd/user, and does NOT enable the timer (see mutation-nightly.timer).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
repo="$(cd "$here/../../.." && pwd)"
base="$HOME/mutation"
mkdir -p "$base/results" "$base/shards" "$HOME/.config/systemd/user"
url="$(git -C "$repo" remote get-url origin)"
if [ ! -d "$base/RimMandrake/.git" ]; then
  git clone -q --filter=blob:none --no-checkout "$url" "$base/RimMandrake"     # shards are sparse, not this
fi
git -C "$base/RimMandrake" fetch -q origin main
git -C "$base/RimMandrake" checkout -q --detach origin/main
[ -x "$base/venv/bin/python" ] || python3 -m venv "$base/venv"
"$base/venv/bin/python" -m pip install -q -r "$repo/infrastructure/stevedesktop/mutation_requirements.txt"
cp "$here/mutation.slice" "$here/mutation-nightly.service" "$here/mutation-nightly.timer" "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
echo "installed; timer state: $(systemctl --user is-enabled mutation-nightly.timer 2>/dev/null || true) (enable by hand)"
