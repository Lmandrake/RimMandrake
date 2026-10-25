#!/usr/bin/env bash
# claude-account: switch SteveDesktop's Claude Code login between subscription accounts, remotely.
# Owner need (2026-10-25): "switch SteveDesktop's Claude login between his Google accounts REMOTELY,
# as he exhausts one or another".
#
# Each account is its own Claude config dir, ~/.claude-accounts/<name>/ (holds .claude.json and
# .credentials.json). ~/.claude-active is a symlink to the one in use, and CLAUDE_CONFIG_DIR points
# at the symlink (exported from /etc/profile.d and the top of ~/.bashrc). Switching repoints the
# symlink, so each account keeps its own refreshed tokens; nothing is copied between accounts.
#
#   claude-account list                     every account: name, email, logged in?, * = active
#   claude-account current                  the active name
#   claude-account use <name>               switch (refuses an account that is not logged in)
#   claude-account login <name> [email]     start a login in tmux and print the URL to open
#   claude-account code <name> <code>       paste the code the browser showed back into that login
#   claude-account import <name> <dir> [json]   adopt an existing config dir (e.g. another user's
#                                           ~/.claude plus its ~/.claude.json); root or that user
#
# From Archmagi:  ssh stevedesktop-wsl claude-account list
set -euo pipefail
ROOT=$HOME/.claude-accounts
ACTIVE=$HOME/.claude-active
CLAUDE=$HOME/.local/bin/claude
die() { echo "claude-account: $*" >&2; exit 1; }
valid() { [[ $1 =~ ^[a-z0-9][a-z0-9_-]*$ ]] || die "account name must be lowercase letters, digits, - or _"; }

status_json() { CLAUDE_CONFIG_DIR=$1 "$CLAUDE" auth status 2>/dev/null || true; }
field() { python3 -c 'import json,sys
try: d=json.loads(sys.stdin.read() or "{}")
except Exception: d={}
print(d.get(sys.argv[1]) or "")' "$1"; }

active_name() { [ -L "$ACTIVE" ] && basename "$(readlink "$ACTIVE")" || true; }

cmd=${1:-list}; shift || true
case "$cmd" in
  list)
    cur=$(active_name)
    [ -d "$ROOT" ] || { echo "no accounts yet (claude-account login <name>)"; exit 0; }
    for d in "$ROOT"/*/; do
      [ -d "$d" ] || continue; n=$(basename "$d"); s=$(status_json "$d")
      printf '%s %-12s %-32s loggedIn=%s\n' "$([ "$n" = "$cur" ] && echo '*' || echo ' ')" "$n" \
        "$(field email <<<"$s")" "$(field loggedIn <<<"$s")"
    done ;;
  current) n=$(active_name); [ -n "$n" ] || die "no active account"; echo "$n" ;;
  use)
    n=${1:?name}; valid "$n"; d=$ROOT/$n
    [ -d "$d" ] || die "no account '$n' (claude-account list)"
    [ "$(status_json "$d" | field loggedIn)" = "True" ] || die "'$n' is not logged in; run: claude-account login $n"
    ln -sfn "$d" "$ACTIVE"; echo "active: $n ($(status_json "$d" | field email))" ;;
  login)
    n=${1:?name}; valid "$n"; email=${2:-}; d=$ROOT/$n; s=claude-login-$n
    mkdir -p "$d"; chmod 700 "$ROOT" "$d"
    tmux kill-session -t "$s" 2>/dev/null || true
    tmux new-session -d -s "$s" -x 400 -y 50 \
      "CLAUDE_CONFIG_DIR='$d' '$CLAUDE' auth login --claudeai ${email:+--email '$email'}; echo LOGIN_EXITED; sleep 600"
    url=""
    for _ in $(seq 1 30); do
      url=$(tmux capture-pane -p -J -t "$s" | grep -o 'https://[^ ]*' | head -1 || true)
      [ -n "$url" ] && break; sleep 1
    done
    [ -n "$url" ] || { tmux capture-pane -p -t "$s" | tail -15; die "no login URL appeared"; }
    echo "Open this in a browser signed in to the account for '$n':"; echo "$url"
    echo "Then: claude-account code $n <code the page shows>" ;;
  code)
    n=${1:?name}; c=${2:?code}; valid "$n"; s=claude-login-$n
    tmux has-session -t "$s" 2>/dev/null || die "no login in progress for '$n'"
    tmux send-keys -t "$s" -l "$c"; tmux send-keys -t "$s" Enter
    for _ in $(seq 1 30); do
      [ "$(status_json "$ROOT/$n" | field loggedIn)" = "True" ] && break; sleep 1
    done
    st=$(status_json "$ROOT/$n")
    if [ "$(field loggedIn <<<"$st")" = "True" ]; then
      tmux kill-session -t "$s" 2>/dev/null || true
      echo "logged in: $n ($(field email <<<"$st"))"
      [ -n "$(active_name)" ] || { ln -sfn "$ROOT/$n" "$ACTIVE"; echo "active: $n"; }
    else
      tmux capture-pane -p -t "$s" | tail -10; die "not logged in yet"
    fi ;;
  import)
    n=${1:?name}; src=${2:?config dir}; js=${3:-$(dirname "$src")/.claude.json}; valid "$n"; d=$ROOT/$n
    [ -f "$src/.credentials.json" ] || die "$src has no .credentials.json"
    mkdir -p "$d"; chmod 700 "$ROOT" "$d"
    cp "$src/.credentials.json" "$d/.credentials.json"
    [ -f "$js" ] && cp "$js" "$d/.claude.json"
    chmod 600 "$d"/.credentials.json "$d"/.claude.json 2>/dev/null || true
    [ "$(status_json "$d" | field loggedIn)" = "True" ] || die "imported '$n' but it does not read as logged in"
    echo "imported: $n ($(status_json "$d" | field email))"
    [ -n "$(active_name)" ] || { ln -sfn "$d" "$ACTIVE"; echo "active: $n"; } ;;
  *) sed -n '2,20p' "$0"; exit 2 ;;
esac
