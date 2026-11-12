#!/bin/bash
# Install, enable and start one Claude Whittle worker as a systemd user unit (survives WSL restarts; the loop itself
# waits out the account switcher's hard stop). Run on Archmagi from any clone that has infrastructure/whittle_claude.
#   install.sh <WORKER>          make the clone if missing, the gate hook, the unit, and start it
#   install.sh <WORKER> --no-start
# SteveDesktop workers (CLAUDE_STEVEDESKTOP_OFFLINE<n>) are installed over ssh: their clone is ~/rm/claude-offline<n>
# made from ~/rm/runner with origin GitHub, and the MandrakeWorkflows runner is copied to ~/.local/share/whittle-claude/mw.
set -euo pipefail
W=${1:?usage: install.sh <WORKER> [--no-start]}
START=1; [ "${2:-}" = --no-start ] && START=0
HERE=$(cd "$(dirname "$0")" && pwd)
read -r MACHINE CLONE BRIEF < <(bash "$HERE/loop.sh" "$W" --where)
case "$BRIEF" in archmagi) GATE=archmagi ;; steve) GATE=steve ;; *) GATE=offline ;; esac
HOME_WC=/mnt/d/ClaudeWork/rimmandrake/whittle_claude
STEVE=mandrake@stevedesktop-wsl
OPTS=(-o BatchMode=yes -o ConnectTimeout=10 -o LogLevel=ERROR)
SETTINGS='{"hooks":{"PreToolUse":[{"matcher":"Bash","hooks":[{"type":"command","command":"python3 \"${CLAUDE_PROJECT_DIR}/infrastructure/whittle_claude/gate.py\" '$GATE'"}]}]}}'

# the shared tools on Archmagi: Steve's wc.py forwards status, log and claims to this copy
mkdir -p "$HOME_WC/tools" "$HOME_WC/$W"
cp "$HERE/wc.py" "$HOME_WC/tools/wc.py"

unit_files() {   # unit_files <dir>: the template and this worker's drop-in under <dir>
    mkdir -p "$1/whittle-claude@$W.service.d"
    cp "$HERE/whittle-claude@.service" "$1/whittle-claude@.service"
    printf '[Service]\nEnvironment=WC_CLONE=%s\n' "$CLONE" > "$1/whittle-claude@$W.service.d/clone.conf"
}

# disk guard: no new worker while the backing drive of this machine's WSL disk is under the floor (2026-11-11: Steve C:
# filled, its WSL root went read-only and a clone lost its work)
if [ "$MACHINE" = Archmagi ]; then DF=$(python3 "$HERE/wc.py" diskfree); else DF=$(ssh "${OPTS[@]}" "$STEVE" python3 - diskfree < "$HERE/wc.py"); fi \
    || { echo "refused: disk guard: $DF" >&2; exit 4; }

if [ "$MACHINE" = Archmagi ]; then
    if [ ! -d "$CLONE/.git" ]; then
        name=$(basename "$CLONE")
        (cd /home/mandrake/rm/bench && AGENT_SEAT=BENCH python3 src/RimMandrake/Utils/scratch_clone.py clone \
            "Claude Whittle worker $W (owner order 2026-11-11)" --name "$name" --checkout --dissociate --fetch)
    fi
    [ -d "$CLONE/.git" ] || { echo "no clone at $CLONE" >&2; exit 1; }
    git -C "$CLONE" remote set-url origin git@github.com:Lmandrake/RimMandrake.git
    git -C "$CLONE" fetch -q origin main
    # never rewind an existing clone that holds unpublished commits or edits (a round may be mid-flight in it)
    if [ -n "$(git -C "$CLONE" status --porcelain 2>/dev/null)" ] || [ "$(git -C "$CLONE" rev-list --count origin/main..HEAD 2>/dev/null || echo 0)" != 0 ]; then
        echo "refused: $CLONE has unpublished commits or uncommitted edits; publish or clean them first" >&2; exit 5; fi
    git -C "$CLONE" checkout -q -B main origin/main
    git -C "$CLONE" branch -q --set-upstream-to=origin/main main
    [ -e "$CLONE/infrastructure/whittle_claude/loop.sh" ] || { echo "origin/main has no infrastructure/whittle_claude: publish it first" >&2; exit 1; }
    mkdir -p "$CLONE/.claude"; printf '%s\n' "$SETTINGS" > "$CLONE/.claude/settings.local.json"
    unit_files "$HOME/.config/systemd/user"
    systemctl --user daemon-reload
    systemctl --user enable "whittle-claude@$W.service" >/dev/null 2>&1
    [ "$START" = 1 ] && systemctl --user restart "whittle-claude@$W.service"
    systemctl --user --no-pager status "whittle-claude@$W.service" 2>&1 | sed -n 1,4p
    exit 0
fi

# --- SteveDesktop --------------------------------------------------------------------------------------------------
MW=$HOME/dev/MandrakeWorkflows
ssh "${OPTS[@]}" "$STEVE" "mkdir -p ~/.local/share/whittle-claude/mw ~/.config/systemd/user $HOME_WC/$W"
rsync -a --delete --exclude __pycache__ -e "ssh ${OPTS[*]}" "$MW/whittle" "$MW/tools" "$STEVE:.local/share/whittle-claude/mw/"
TMP=$(mktemp -d); unit_files "$TMP"
rsync -a -e "ssh ${OPTS[*]}" "$TMP/" "$STEVE:.config/systemd/user/"; rm -rf "$TMP"
ssh "${OPTS[@]}" "$STEVE" "set -e; C=$CLONE
    if [ ! -d \$C/.git ]; then git clone -q --local ~/rm/runner \$C; fi
    git -C \$C remote set-url origin git@github.com:Lmandrake/RimMandrake.git
    git -C \$C fetch -q origin main
    if [ -n \"\$(git -C \$C status --porcelain 2>/dev/null)\" ] || [ \"\$(git -C \$C rev-list --count origin/main..HEAD 2>/dev/null || echo 0)\" != 0 ]; then
        echo \"refused: \$C has unpublished commits or uncommitted edits\" >&2; exit 5; fi
    git -C \$C checkout -q -B main origin/main
    git -C \$C branch -q --set-upstream-to=origin/main main
    [ -e \$C/infrastructure/whittle_claude/loop.sh ] || { echo 'origin/main has no infrastructure/whittle_claude' >&2; exit 1; }
    mkdir -p \$C/.claude; printf '%s\n' '$SETTINGS' > \$C/.claude/settings.local.json
    ssh -o BatchMode=yes -o ConnectTimeout=10 mandrake@archmagi-wsl true || { echo 'Steve cannot reach Archmagi' >&2; exit 1; }
    systemctl --user daemon-reload
    systemctl --user enable whittle-claude@$W.service >/dev/null 2>&1
    [ $START = 1 ] && systemctl --user restart whittle-claude@$W.service
    systemctl --user --no-pager status whittle-claude@$W.service 2>&1 | sed -n 1,4p"
