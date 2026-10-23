#!/bin/sh
# Install the RimPulse units to run from a dedicated origin/main checkout (RIMPULSE_DEPLOY_FIX_RUNS_THE_BENCH_CLONE).
#   sh src/RimMandrake/Utils/pulse/systemd/install.sh
# The checkout lives under the machine's agent storage root (Lodestar agent_storage.py; never ~/dev, never a
# seat clone): <root>/rimmandrake/pulse-deploy, a sparse blobless clone of origin holding only what pulse runs.
# Units read its path from RM_PULSE_DEPLOY, set in one drop-in per unit; a missing variable fails by name.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(python3 "$HOME/dev/Lodestar/bin/lib/agent_storage.py" rimmandrake)
[ -n "$ROOT" ] || { echo "install.sh: agent storage root unset (agent_storage.py)" >&2; exit 1; }
DEPLOY="$ROOT/pulse-deploy"
ORIGIN=$(git -C "$HERE" remote get-url origin)
if [ ! -d "$DEPLOY/.git" ]; then
  git clone -q --filter=blob:none --no-checkout --sparse "$ORIGIN" "$DEPLOY"
  git -C "$DEPLOY" sparse-checkout set src/RimMandrake/Utils/pulse src/RimMandrake/rimflow
  git -C "$DEPLOY" checkout -q main
else
  git -C "$DEPLOY" pull -q --ff-only origin main
fi
UNITS=~/.config/systemd/user
for u in rm-pulse.service rm-pulse-digest.service rm-pulse-digest.timer rm-pulse-health.service rm-pulse-health.timer \
         rm-pulse-update.service rm-pulse-update.timer; do
  cp "$HERE/$u" "$UNITS/$u"
done
for u in rm-pulse.service rm-pulse-digest.service rm-pulse-health.service rm-pulse-update.service; do
  mkdir -p "$UNITS/$u.d"
  printf '[Service]\nEnvironment=RM_PULSE_DEPLOY=%s\n' "$DEPLOY" > "$UNITS/$u.d/pulse-deploy.conf"
done
systemctl --user daemon-reload
systemctl --user enable -q rm-pulse.service rm-pulse-health.timer rm-pulse-digest.timer rm-pulse-update.timer
systemctl --user restart rm-pulse.service
systemctl --user start rm-pulse-update.timer
echo "install.sh: rm-pulse runs $DEPLOY @ $(git -C "$DEPLOY" log -1 --format=%h)"
