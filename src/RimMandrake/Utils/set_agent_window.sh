#!/usr/bin/env bash
# set_agent_window.sh — name this seat, in all THREE namespaces, in one command.
#
# ⚠️ NORMALLY YOU DO NOT NEED THIS. The Windows Terminal seat profiles
# (`src/RimMandrake/Utils/install_wt_seat_profiles.py`) export `AGENT_SEAT=<SEAT>` and launch
# Claude Code, and `.claude/hooks/set_session_title.py` turns that into the same
# recorded role this script writes. Opening the seat's tab is the whole startup.
#
# This stays the MANUAL path, for the two cases the profile cannot cover:
#   * a window opened without a seat profile (plain Ubuntu tab, ssh, another box)
#   * a seat CHANGING role mid-session — the role file it writes beats AGENT_SEAT
#
#   ./src/RimMandrake/Utils/set_agent_window.sh OPS
#   ./src/RimMandrake/Utils/set_agent_window.sh OPS "log harvest"    # optional detail suffix
#   ./src/RimMandrake/Utils/set_agent_window.sh --preview            # show every seat's colour
#   ./src/RimMandrake/Utils/set_agent_window.sh --reset-colour       # undo colours, keep names
#
# TWO NAMESPACES THIS SETS, AND A THIRD IT CANNOT
# ===============================================
#   1. terminal window  OSC 0, set here directly. What the owner reads off the
#                       taskbar.
#   2. conversation     .claude/hooks/set_session_title.py reads the role this
#                       script records and returns it as a sessionTitle.
#   3. MESSAGING NAME   ⛔ NOT settable from here, or from any hook. It is fixed
#                       at LAUNCH by `--name`. See "ADDRESSABILITY" below.
#
# The hook ALSO injects infrastructure/agents/<SEAT>.md as this session's identity, from the
# same recorded role. So this one command names the window, names the
# conversation and tells the seat who it is — but does not make it addressable.
#
# ADDRESSABILITY — the 2026-08-12 measurement was RIGHT; the 2026-08-13
# "correction" that overwrote it was wrong, and is retracted here
# ============================================================================
# The retracted text claimed sessionTitle propagates to the name peers address
# with SendMessage. It does not, and never did.
#
# Re-measured 2026-08-13 with three seats live at once — the strongest form of
# this test, because all three had CORRECT role files and none of the three was
# addressable:
#
#   .claude/session_roles/<sid>     AGENT OPS · AGENT CREATE · AGENT PROJECT
#   ~/.claude/sessions/<pid>.json   "name": "rimworld-1b" / "-64" / "-b8",
#                                   "nameSource": "derived"   (all three)
#
# Confirmed against the 2.1.231 binary rather than inferred from behaviour: a
# hook's sessionTitle reaches `saveCustomTitle(title, "hook")`, which appends a
# `custom-title` transcript entry and sets the conversation title. The pid-file
# writer that owns `name` is reached only by `--name`/`-n`, by `/rename`, and by
# the agent-name setter. There is no path between the two.
#
# WHY THE EARLIER "CORRECTION" LOOKED TRUE: it cited one session whose name did
# read `AGENT PROJECT`. That is consistent — a name set by `/rename` or `--name`
# persists and looks identical afterwards. One session observed AFTER the fact
# cannot distinguish which mechanism named it, and no control was run.
#
# THE FIX, and it is zero-typing: the Windows Terminal seat profiles now launch
# `claude --name 'AGENT <SEAT>'` (src/RimMandrake/Utils/install_wt_seat_profiles.py). Reinstall
# with `--apply`; it takes effect at each seat's NEXT launch and cannot be
# applied mid-session by anything.
#
# So ALWAYS confirm an address with `python3 src/RimMandrake/Utils/peers.py` before initiating
# contact. It joins the role file to the live registry and prints both columns:
# send to NAME, read SEAT to know who that is.
#
# ⚠️ The conversation and messaging names land on your NEXT prompt, not this
# turn: the role is declared mid-turn and no post-tool hook event accepts a
# sessionTitle. On a RESUMED session both are immediate, because the session id
# — and so the recorded role — survives.
#
# ⚠️ The WINDOW half requires CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1 (set for this
# project in .claude/settings.json). Without it Claude Code rewrites the title
# every turn. It is read once at process start, so it applies from the next
# Claude Code launch — a CLI restart, never a game load.

set -euo pipefail

# --- the seat table: the single source of truth --------------------------
# Colour is the seat's identity in the one place the owner sees all five at
# once. Chosen to stay legible on a dark background and to be distinguishable
# from each other by hue, not just by lightness.
seat_colour() {
    case "$1" in
        BRIDGE)  printf '#4EC9E0' ;;   # cyan     — instruments, telemetry
        OPS)     printf '#E5A03C' ;;   # amber    — alarms, diagnostics
        CREATE)  printf '#7BC96F' ;;   # green    — making things
        VISION)  printf '#C08CE0' ;;   # violet   — design
        PROJECT) printf '#9CB3D0' ;;   # slate    — documents
    esac
}
SEATS="BRIDGE OPS CREATE VISION PROJECT"

usage() {
    echo "usage: $0 {BRIDGE|OPS|CREATE|VISION|PROJECT} [detail]" >&2
    echo "       $0 --preview | --reset-colour" >&2
    echo "  identities: infrastructure/agents/<SEAT>.md   shared rules: agents_def.md" >&2
}

# --- colour --------------------------------------------------------------
# OSC 10 sets the default FOREGROUND, OSC 12 the cursor. Widely supported
# (xterm, VTE/GNOME, kitty, alacritty, iTerm2, Windows Terminal); terminals that
# do not support it ignore the sequence silently.
#
# ⚠️ We cannot verify this from inside. A script's stdout reaches the owner's
# screen, but the terminal's REPLY to a query goes to Claude Code's stdin, not
# ours — so there is no readback. If a window does not change colour, its
# terminal does not support OSC 10; that is a fact about the terminal, not a bug
# here. `--reset-colour` restores the default either way.
apply_colour() {
    printf '\033]10;%s\007' "$1"      # default foreground
    printf '\033]12;%s\007' "$1"      # cursor, so the caret matches
}

case "${1:-}" in
    --preview)
        echo "Seat colours — if these five lines are not tinted, this terminal"
        echo "ignores OSC 10 and per-seat colour is unavailable here."
        for s in $SEATS; do
            c="$(seat_colour "$s")"
            printf '\033]10;%s\007  AGENT %-8s %s\n' "$c" "$s" "$c"
        done
        printf '\033]110;\007\033]112;\007'    # reset fg + cursor
        echo "(colour reset)"
        exit 0
        ;;
    --reset-colour|--reset-color)
        printf '\033]110;\007\033]112;\007'    # OSC 110/112 = reset to default
        echo "colour reset to this terminal's default"
        exit 0
        ;;
    -h|--help)
        usage; exit 0 ;;
esac

ROLE="${1:-}"
DETAIL="${2:-}"

case "$ROLE" in
    BRIDGE|OPS|CREATE|VISION|PROJECT) ;;
    WORLD)
        echo "WORLD was renamed to OPS on 2026-08-13." >&2
        echo "  The name pointed at design/Jawa/worldbuilding/, which now belongs to VISION." >&2
        echo "  What this seat does is keep the live mod stack working." >&2
        echo "  Run: $0 OPS" >&2
        exit 2
        ;;
    *)
        usage; exit 2 ;;
esac

TITLE="AGENT ${ROLE}"
[ -n "$DETAIL" ] && TITLE="${TITLE} — ${DETAIL}"

# --- 1. the terminal window ----------------------------------------------
printf '\033]0;%s\007' "$TITLE"        # OSC 0 = icon name + window title

# --- colour, unless suppressed -------------------------------------------
# ⚠️ MEASURED 2026-08-13: Windows Terminal IGNORES OSC 10. The owner ran
# `--preview` and all five lines rendered in the default colour. The escape is
# kept because it costs nothing and works on xterm/VTE/kitty/iTerm2 — but on
# this setup the working route is a per-seat Windows Terminal PROFILE, which
# also colours the tab strip and cannot be done from inside the shell at all:
#     python3 src/RimMandrake/Utils/install_wt_seat_profiles.py --apply
# So this reports what it ATTEMPTED, never that the colour changed.
if [ "${AGENT_WINDOW_NO_COLOUR:-}" = "1" ]; then
    COLOUR_NOTE="suppressed (AGENT_WINDOW_NO_COLOUR=1)"
else
    apply_colour "$(seat_colour "$ROLE")"
    COLOUR_NOTE="OSC 10 sent, $(seat_colour "$ROLE") — ignored by Windows Terminal; use install_wt_seat_profiles.py"
fi

# --- 2 and 3. the conversation, and the name peers message ---------------
# Keyed by session id, which Claude Code exports here and also puts on the hook
# payload, so both sides agree without either guessing.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROLE_DIR="${CLAUDE_PROJECT_DIR:-$REPO_ROOT}/.claude/session_roles"
SID="${CLAUDE_CODE_SESSION_ID:-}"

echo "seat        : ${TITLE}"
echo "window      : set"
echo "colour      : ${COLOUR_NOTE}"

if [ -n "$SID" ]; then
    mkdir -p "$ROLE_DIR"
    printf '%s\n' "$TITLE" > "${ROLE_DIR}/${SID}"
    echo "conversation: recorded"
    echo "identity    : infrastructure/agents/${ROLE}.md, injected by the hook"
    echo "  (both apply on your NEXT prompt — immediate on a resume)"
    echo "messaging   : UNCHANGED — this cannot set the name peers address."
    echo "  That is fixed at launch by --name; see ADDRESSABILITY in this file."
    echo "  Peers still reach you at your generated name: python3 src/RimMandrake/Utils/peers.py"
else
    echo "conversation: NOT SET — CLAUDE_CODE_SESSION_ID is unset." >&2
    echo "  The window is named, but peers cannot address you by seat and your" >&2
    echo "  identity file will not be injected. Only the window half worked." >&2
fi
