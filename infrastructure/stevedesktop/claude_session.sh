#!/usr/bin/env bash
# Open an oriented Claude Code session on SteveDesktop's WSL. Used by the desktop shortcuts
# ("Claude - SteveDesktop test centre", "Claude - Lodestar") and by Archmagi's
# "Claude on SteveDesktop" (inside tmux). No credentials are touched here: whichever
# account `claude-account` last selected is the one that runs.
#   claude_session.sh centre|lodestar
set -uo pipefail
case "${1:-centre}" in
  centre)
    DIR="$HOME/rm/runner"; NAME="SteveDesktop test centre"; SEAT=STEVECENTRE; RC=SteveDesktop-Owner
    PROMPT="You are on SteveDesktop, the unattended RimWorld test centre (WSL, cwd ~/rm/runner, a clone of RimMandrake). The owner just opened you from a desktop shortcut to talk about this machine. Before anything else read infrastructure/stevedesktop/RUNBOOK.md and design/RimMandrake/test_orchestration_two_machines_2026-10-25.md (if the latter is missing run git pull --ff-only first). Account switching is the claude-account command (claude-remote-control skill); do not log in or touch credentials. Archmagi (the owner's main box) is reachable as mandrake@archmagi-wsl; checks from there: infrastructure/stevedesktop/verify_from_archmagi.sh. Then summarise in five lines what this machine is for and its current state, and ask what the owner wants." ;;
  lodestar)
    DIR="$HOME/dev/Lodestar"; NAME="SteveDesktop Lodestar"; SEAT=STEVELODESTAR; RC=SteveDesktop-Lodestar
    PROMPT="You are on SteveDesktop (WSL), in ~/dev/Lodestar, opened by the owner from a desktop shortcut for machine-maintenance work. Read README.md, AGENTS.md and BOARD.md here first. The RimWorld test centre on this machine is documented in ~/rm/runner/infrastructure/stevedesktop/RUNBOOK.md (read it if the work touches the machine itself). Account switching is the claude-account command; do not log in or touch credentials. Then say in three lines where things stand and ask what the owner wants." ;;
  *) echo "usage: $0 centre|lodestar" >&2; exit 2 ;;
esac
cd "$DIR" || { echo "missing $DIR" >&2; read -r -p "press enter"; exit 1; }
export AGENT_SEAT="$SEAT"
W="$HOME/rm/runner/src/RimMandrake/Utils/claude_bounded.sh"
[ -x "$W" ] || W=claude
"$W" --dangerously-skip-permissions --name "$NAME" --remote-control "$RC" "$PROMPT"
exec bash -l
