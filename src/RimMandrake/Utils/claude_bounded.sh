#!/usr/bin/env bash
# claude_bounded.sh — launch a Claude Code seat inside its own memory cgroup, so a
# runaway seat dies ALONE instead of taking the WSL VM and every other seat with it.
#
# ── Why this exists ───────────────────────────────────────────────────────────
# On 2026-08-14 WSL died twice (01:37 and 11:26). Both were the same event, and it
# was neither the GPU nor host RAM:
#
#   Aug 14 11:26:41 kernel: Out of memory: Killed process 25380 (2.1.232)
#                           total-vm:38083000kB, anon-rss:27445504kB
#   oom-kill:constraint=CONSTRAINT_NONE, ..., global_oom
#
# `2.1.232` is ~/.local/share/claude/versions/2.1.232 — the Claude Code binary
# itself, named by version. ONE seat reached 27.4 GB of the VM's 31.7 GB while the
# other five sat at ~600 MB each. `constraint=CONSTRAINT_NONE` + `global_oom` is
# the kernel saying the whole VM ran out, so init went down and every seat with it.
#
# The cause is not the ceiling. Raising the VM's memory would only move the same
# kill later — a process that reaches 27 GB will reach 40 GB. What was missing is
# that all five seats shared ONE unbounded cgroup (`/init.scope`, `memory.max=max`),
# because `wsl.exe -- bash -lc` never opens a per-session scope. Nothing separated
# them, so one seat's balloon was indistinguishable from the VM being full.
#
# ── What this changes ─────────────────────────────────────────────────────────
# Running under a scope with MemoryMax turns the global kill into a scoped one.
# Measured on 2026-08-14, same machine, deliberately overrunning a 200M scope:
#
#   oom-kill:constraint=CONSTRAINT_MEMCG, oom_memcg=/user.slice/.../run-p10162.scope
#   Memory cgroup out of memory: Killed process 10482 (python3)
#
# CONSTRAINT_MEMCG instead of CONSTRAINT_NONE. That one word is the whole fix:
# the offending seat is killed, the VM and the other four keep running.
#
# ⚠️ MemorySwapMax matters as much as MemoryMax. With swap unbounded the same test
# was NOT killed at all — it silently spilled into swap (8 GB then, 16 GB now) and kept going,
# which is how you get the machine crawling for seven minutes before it dies. The
# journal shows exactly that: page-allocation failures from 11:19:48, the kill at
# 11:26:41.
#
# ── Usage ─────────────────────────────────────────────────────────────────────
#   ./claude_bounded.sh --dangerously-skip-permissions --name 'AGENT DECIDE'
#   MEM_MAX=16G ./claude_bounded.sh ...        # override for a known-heavy seat
#   CLAUDE_CODE_TOOL_MEMORY_LIMIT=none ...    # opt out of the tool cap for one seat
#
# All arguments are passed through to `claude` untouched.
#
# ── 2026-10-08 additions (SEAT_MEMORY_CLONES_DRIVES_1, design
#    design/RimMandrake/memory_clones_drives_2026-10-08.md §3 A1/A7, §7 phase 0/1) ──
# 1. Tool cgroup. Claude Code (2.1.286+) caps its own tool commands when
#    CLAUDE_CODE_TOOL_MEMORY_LIMIT is set: it writes each tool's pid into a cgroup
#    named `claude-code-bash`, created as a SIBLING of its own cgroup (dirname of
#    /proc/self/cgroup) — read from the binary, not guessed. Run bare in the seat
#    scope, that sibling is `claude-seats.slice/claude-code-bash`: ONE cgroup shared
#    by every seat, outside each seat's 10G, last writer's limit wins. So the scope
#    is DELEGATED and Claude runs in a leaf `<scope>/seat`; its sibling then is
#    `<scope>/claude-code-bash`, inside this seat's cap.
#    🔴 MEASURED: Claude writes memory.max only, never memory.swap.max. With swap
#    unbounded a 1.5G bomb under a 1G tool cap did NOT die — it swapped 524 MB and
#    printed success. So this script pre-creates the cgroup with memory.swap.max=0
#    (Claude reuses an existing dir). Proof it engaged: `tool cgroup: <dir> limit=`
#    in `claude --debug-file`, or `cat <scope>/claude-code-bash/memory.max`.
# 2. Seat temp on ext4. TMPDIR and CLAUDE_CODE_TMPDIR = ~/.seat-tmp/<SEAT> (0700).
#    /tmp is tmpfs: its pages are charged to the seat as shmem and outlive the
#    writer, which is how six seats died between 10-01 and 10-08. ext4 page cache is
#    reclaimable. Aged out after 3 days by claude-seat-tmp.conf (systemd-tmpfiles,
#    installed below); each launcher holds a shared flock on its seat dir, which
#    tmpfiles honours, so a LIVE seat's files are never aged out.
# 3. Terminal reset. No `exec`: when Claude exits for ANY reason (kill -9 and OOM
#    included) this script turns mouse tracking, bracketed paste and the alt screen
#    off and runs `stty sane`, then exits with Claude's status. A killed Claude used
#    to leave the tab printing `0;34;37M` on every mouse move.

set -uo pipefail

# 10G, raised from 6G on 2026-08-14 after measuring what a scope actually has to
# hold. The bound covers the whole PROCESS TREE, not just the tab: a seat spawns
# `claude daemon run`, which spawns `bg-pty-host` processes, which spawn the
# versioned binary per background session - and children inherit the parent's
# cgroup. Measured on one idle seat with three background jobs:
#
#   tab 0.65G + daemon 0.33G + 3x pty-host 0.59G + 3x session 1.24G = 2.81 GB
#
# That was already 47% of a 6 GB bound while doing nothing, which would have made
# spurious kills likely. 10G is ~3.5x that idle tree and still far below the
# ~27 GB a real runaway reached, so it catches the failure with room to spare.
# If a seat legitimately needs more, raise MEM_MAX for THAT seat; never remove it.
MEM_MAX="${MEM_MAX:-10G}"
SWAP_MAX="${SWAP_MAX:-2G}"
SEAT="${AGENT_SEAT:-unknown}"
# 6G of the seat's 10G: tools die first, Claude keeps ~4G. `none`/`0` opts out.
TOOL_MEM="${CLAUDE_CODE_TOOL_MEMORY_LIMIT:-6G}"
SEAT_TMP_ROOT="${SEAT_TMP_ROOT:-$HOME/.seat-tmp}"

red() { printf '\033[1;31m%s\033[0m\n' "$*" >&2; }

# Restore the terminal Claude leaves behind: mouse tracking (1000/1002/1003, SGR
# 1006, urxvt 1015), focus reporting (1004), bracketed paste (2004), alternate
# screen (1049), cursor (25h). (CLAUDE_CODE_DISABLE_MOUSE=1 exists; not set — UX.)
# Written to /dev/tty, never stdout, so `claude -p ... | tool` output stays clean.
reset_terminal() {
  { printf '\033[?1000l\033[?1002l\033[?1003l\033[?1006l\033[?1015l\033[?1004l\033[?2004l\033[?1049l\033[?25h' >/dev/tty
    stty sane </dev/tty; } 2>/dev/null
}

CLAUDE_BIN="$(command -v claude || true)"
if [ -z "$CLAUDE_BIN" ]; then
  echo "claude_bounded: 'claude' not on PATH; launching unbounded is not the fallback." >&2
  exit 127
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
# Seat temp dir on ext4 (header §2), set up before the scope probe so even an
# unbounded seat keeps its temp off tmpfs. Failure is loud, never fatal. fd 9
# holds the shared flock that keeps tmpfiles away from a live seat's files.
TMPFILES_SRC="$HERE/claude-seat-tmp.conf"
TMPFILES_DST="${XDG_CONFIG_HOME:-$HOME/.config}/user-tmpfiles.d/claude-seat-tmp.conf"
if [ -f "$TMPFILES_SRC" ] && ! cmp -s "$TMPFILES_SRC" "$TMPFILES_DST" 2>/dev/null; then
  mkdir -p "$(dirname "$TMPFILES_DST")" && cp "$TMPFILES_SRC" "$TMPFILES_DST"
fi
# The user clean timer ships disabled on this distro; without it nothing ages out.
systemctl --user is-enabled -q systemd-tmpfiles-clean.timer 2>/dev/null ||
  systemctl --user enable --now -q systemd-tmpfiles-clean.timer 2>/dev/null ||
  red "!!! claude_bounded: could not enable systemd-tmpfiles-clean.timer — ~/.seat-tmp will not age out."
SEAT_TMP="$SEAT_TMP_ROOT/$SEAT"
if mkdir -p -m 0700 "$SEAT_TMP_ROOT" "$SEAT_TMP" && chmod 0700 "$SEAT_TMP_ROOT" "$SEAT_TMP" &&
   exec 9<"$SEAT_TMP" && flock -s -n 9; then
  export TMPDIR="$SEAT_TMP" CLAUDE_CODE_TMPDIR="$SEAT_TMP"
else
  red "!!! claude_bounded: cannot prepare $SEAT_TMP — this seat's temp stays on tmpfs (/tmp)."
fi

# 🔴 Probe the CAPABILITY, not a proxy for it. The first version of this guard
# used `systemctl --user is-system-running`, which on this machine reports
# `degraded` and exits 1 — a perfectly normal state — while scope creation works
# fine. That silently downgraded every seat to UNBOUNDED, which is the exact
# failure this script exists to prevent, and it would have done so invisibly.
# Ask the question you actually need answered: can I make a scope?
if ! systemd-run --user --scope --quiet -- true >/dev/null 2>&1; then
  # Unbounded is still better than a seat that will not start, but this must be
  # impossible to miss: it scrolls past in a fresh tab otherwise. Red, and it
  # costs three seconds so the reader has time to see it.
  red "!!! claude_bounded: cannot create a systemd scope — starting UNBOUNDED."
  red "!!! This seat has NO OOM protection. A runaway here kills the whole VM."
  sleep 3
  # No delegated scope means no safe place for the tool cgroup (see header §1):
  # 'none' stops Claude creating a shared sibling wherever it happens to run.
  CLAUDE_CODE_TOOL_MEMORY_LIMIT=none "$CLAUDE_BIN" "$@" 9<&-
  rc=$?; reset_terminal; exit "$rc"
fi

# Install the slice unit if it is missing. It lives in the repo so a fresh clone
# or a rebuilt WSL distro is not silently downgraded to per-seat-only protection —
# systemd would happily create an UNBOUNDED slice on demand for an unknown name,
# which fails open in exactly the way this whole script exists to prevent.
SLICE_SRC="$HERE/claude-seats.slice"
SLICE_DST="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user/claude-seats.slice"
if [ -f "$SLICE_SRC" ] && ! cmp -s "$SLICE_SRC" "$SLICE_DST" 2>/dev/null; then
  mkdir -p "$(dirname "$SLICE_DST")"
  cp "$SLICE_SRC" "$SLICE_DST" && systemctl --user daemon-reload 2>/dev/null
fi

# Runs INSIDE the scope, before Claude (header §1). Moves itself to the leaf
# <scope>/seat (cgroup v2 forbids processes in a cgroup that delegates memory to
# children), enables memory for children, pre-creates claude-code-bash with
# swap 0, then execs Claude. Any failure: red warning, Claude starts uncapped.
# shellcheck disable=SC2016
SEAT_INNER='
red() { printf "\033[1;31m%s\033[0m\n" "$*" >&2; }
lim=$(printf %s "${CLAUDE_CODE_TOOL_MEMORY_LIMIT:-}" | tr "[:upper:]" "[:lower:]")
case "$lim" in ""|none|0|false|off|no) export CLAUDE_CODE_TOOL_MEMORY_LIMIT=none ;; *)
  cg=/sys/fs/cgroup$(sed -n "s/^0:://p" /proc/self/cgroup)
  if { mkdir -p "$cg/seat" && echo 0 >"$cg/seat/cgroup.procs" &&
       echo +memory >"$cg/cgroup.subtree_control" &&
       mkdir -p "$cg/claude-code-bash" && echo 0 >"$cg/claude-code-bash/memory.swap.max"; } 2>/dev/null
  then :; else
    red "!!! claude_bounded: tool memory cgroup could NOT be set up in $cg"
    red "!!! Tool commands are UNCAPPED: a runaway tool can kill Claude itself."
    export CLAUDE_CODE_TOOL_MEMORY_LIMIT=none; sleep 3
  fi ;;
esac
exec "$@"'

# --slice puts every seat under ONE parent with its own ceiling, so there are two
# limits, not one: MemoryMax below stops a single runaway at 10G, and the slice's
# 24G stops all five together. Without the slice the per-seat bound proves only
# that one seat cannot kill the VM - four at once still could.
# Defined in ~/.config/systemd/user/claude-seats.slice.
#
# Foreground, not exec (header §3). The traps are handlers, not ignores, so the
# child still gets default signal dispositions; they only keep this shell alive
# long enough to reset the terminal. The seat lock fd is closed for the child.
trap ':' INT TERM HUP QUIT
CLAUDE_CODE_TOOL_MEMORY_LIMIT="$TOOL_MEM" systemd-run --user --scope --quiet \
  --slice=claude-seats.slice \
  --unit="claude-seat-${SEAT}-$$" \
  -p MemoryMax="$MEM_MAX" \
  -p MemorySwapMax="$SWAP_MAX" \
  -p MemoryAccounting=yes \
  -p OOMPolicy=continue \
  -p Delegate=yes \
  -- bash -c "$SEAT_INNER" claude-seat "$CLAUDE_BIN" "$@" 9<&-
rc=$?
reset_terminal
exit "$rc"
# OOMPolicy=continue (2026-09-05): without it, systemd's default (stop) killed the
# WHOLE seat when the kernel OOM-killed one runaway python child inside the scope —
# both live seats died mid-stream that day. With continue, the child dies alone and
# the seat keeps running; if claude itself is the balloon the outcome is unchanged.
