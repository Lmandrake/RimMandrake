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
# was NOT killed at all — it silently spilled into the 8 GB swap and kept going,
# which is how you get the machine crawling for seven minutes before it dies. The
# journal shows exactly that: page-allocation failures from 11:19:48, the kill at
# 11:26:41.
#
# ── Usage ─────────────────────────────────────────────────────────────────────
#   ./claude_bounded.sh --dangerously-skip-permissions --name 'AGENT DECIDE'
#   MEM_MAX=16G ./claude_bounded.sh ...        # override for a known-heavy seat
#
# All arguments are passed through to `claude` untouched.

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

CLAUDE_BIN="$(command -v claude || true)"
if [ -z "$CLAUDE_BIN" ]; then
  echo "claude_bounded: 'claude' not on PATH; launching unbounded is not the fallback." >&2
  exit 127
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
  printf '\033[1;31m%s\033[0m\n' \
    "!!! claude_bounded: cannot create a systemd scope — starting UNBOUNDED." >&2
  printf '\033[1;31m%s\033[0m\n' \
    "!!! This seat has NO OOM protection. A runaway here kills the whole VM." >&2
  sleep 3
  exec "$CLAUDE_BIN" "$@"
fi

# Install the slice unit if it is missing. It lives in the repo so a fresh clone
# or a rebuilt WSL distro is not silently downgraded to per-seat-only protection —
# systemd would happily create an UNBOUNDED slice on demand for an unknown name,
# which fails open in exactly the way this whole script exists to prevent.
SLICE_SRC=/mnt/d/Luke/dev/Rimworld/src/RimMandrake/Utils/claude-seats.slice
SLICE_DST="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user/claude-seats.slice"
if [ -f "$SLICE_SRC" ] && ! cmp -s "$SLICE_SRC" "$SLICE_DST" 2>/dev/null; then
  mkdir -p "$(dirname "$SLICE_DST")"
  cp "$SLICE_SRC" "$SLICE_DST" && systemctl --user daemon-reload 2>/dev/null
fi

# --slice puts every seat under ONE parent with its own ceiling, so there are two
# limits, not one: MemoryMax below stops a single runaway at 10G, and the slice's
# 24G stops all five together. Without the slice the per-seat bound proves only
# that one seat cannot kill the VM - four at once still could.
# Defined in ~/.config/systemd/user/claude-seats.slice.
exec systemd-run --user --scope --quiet \
  --slice=claude-seats.slice \
  --unit="claude-seat-${AGENT_SEAT:-unknown}-$$" \
  -p MemoryMax="$MEM_MAX" \
  -p MemorySwapMax="$SWAP_MAX" \
  -p MemoryAccounting=yes \
  -p OOMPolicy=continue \
  -- "$CLAUDE_BIN" "$@"
# OOMPolicy=continue (2026-09-05): without it, systemd's default (stop) killed the
# WHOLE seat when the kernel OOM-killed one runaway python child inside the scope —
# both live seats died mid-stream that day. With continue, the child dies alone and
# the seat keeps running; if claude itself is the balloon the outcome is unchanged.
