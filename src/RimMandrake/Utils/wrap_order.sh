#!/usr/bin/env bash
# wrap_order.sh — compose the WRAP ORDER broadcast before a full seat reboot.
#
#   ./src/RimMandrake/Utils/wrap_order.sh
#   ./src/RimMandrake/Utils/wrap_order.sh "game going down"
#   ./src/RimMandrake/Utils/wrap_order.sh --degraded "reboot in 2 min, lock will not clear"
#
# WRAP is PROJECT's to issue, and only on the owner's instruction. The protocol
# itself is `skills/agent-messaging/SKILL.md` §9 — this only composes it.
#
# THIS SCRIPT DOES NOT SEND
# =========================
# Sending is a SendMessage tool call, not a shell command. So this prints the
# exact text to paste, once per live peer, and stops there.
#
# WHY IT CHECKS THE TREE FIRST
# ============================
# Step 2 of the checklist is "commit and push". Two conditions make that step
# fail for EVERY seat simultaneously, and neither is visible from a seat that
# was merely told to wrap:
#
#   * a git lock   — every `git commit` dies with "Unable to create index.lock"
#   * a dirty tree — one shared working tree, so a seat racing a reboot with
#                    `git add` will sweep a peer's half-finished file into its
#                    own commit
#
# Surface both BEFORE the order goes out. A seat cannot work around a lock it
# does not know about, and a broadcast that arrives into a broken tree turns one
# problem into five.
#
# WHY A LOCK IS NOT A HOLD
# ========================
# A WRAP is issued BECAUSE something is going down, so "hold until the lock
# clears" refuses to answer the question. A locked tree delays the COMMIT, not
# the WORK: the repo is on `D:\Luke\dev\Rimworld` and uncommitted files survive
# a reboot, while `/tmp` is tmpfs and does not. So this prints the BRANCH — which
# of four cases holds, and the exact next command — and `--degraded` emits the
# fallback order for the one case with no time left. Reasoning: SKILL.md §9a/§9b.

# No `set -e`: check_git_locks.py exits non-zero BY DESIGN (1 = stale lock found,
# 2 = live lock, wait). Those are findings to print, not failures to abort on.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT" || exit 2

DEGRADED=0
REASON=""
while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            echo "usage: $0 [--degraded] [\"one-line reason\"]" >&2
            echo "  prints the WRAP ORDER text to paste; does not send" >&2
            echo "  --degraded  emit the DEGRADED order: lock will not clear and" >&2
            echo "              the machine is going down now. Scratchpad to disk," >&2
            echo "              no commit, state file anyway (SKILL.md §9b)" >&2
            echo "  protocol: skills/agent-messaging/SKILL.md §9" >&2
            exit 0 ;;
        --degraded) DEGRADED=1 ;;
        *)          REASON="$1" ;;
    esac
    shift
done

rule() { printf '%s\n' "------------------------------------------------------------"; }

# --- 1. can the tree take a wrap order at all? ----------------------------
rule
echo "GIT LOCKS"
LOCK_OUT="$(python3 src/RimMandrake/Utils/check_git_locks.py 2>&1)"
LOCK_RC=$?
printf '%s\n' "$LOCK_OUT"

# The exact `rm` lines the checker printed for locks it judged STALE, and whether
# any LIVE lock is merely young. Both come from its output rather than being
# re-derived here — one tool owns the evidence.
STALE_RM="$(printf '%s\n' "$LOCK_OUT" | grep -F 'clear it rm -f' | sed 's/^ *clear it //')"
YOUNG_LIVE="$(printf '%s\n' "$LOCK_OUT" | grep -c 'younger than')"

echo
echo "TREE (git status --short)"
DIRTY="$(git status --short)"
if [ -n "$DIRTY" ]; then
    printf '%s\n' "$DIRTY"
else
    echo "  clean"
fi

# --- 2. who is live, and therefore needs the order ------------------------
echo
rule
echo "LIVE SEATS — send to each of these, by the NAME shown"
python3 src/RimMandrake/Utils/peers.py

# --- 3. the verdict, before the text ---------------------------------------
echo
rule
if [ "$DEGRADED" -eq 1 ]; then
    echo "⚠️  DEGRADED. You have declared the lock unclearable and the reboot"
    echo "    imminent. The order below drops step 2 — no commit — and makes the"
    echo "    scratchpad the whole job. Uncommitted survives the reboot; /tmp"
    echo "    does not. Record which seats reply DEGRADED: landing their files"
    echo "    is the first act of the next session (infrastructure/state/queue/PROJECT.md, top)."
elif [ "$LOCK_RC" -eq 1 ]; then
    echo "➜  STALE lock — clearable, and this is the common case. Run:"
    printf '%s\n' "$STALE_RM" | while IFS= read -r cmd; do
        [ -n "$cmd" ] && echo "      $cmd"
    done
    echo "    then re-run this script. Left alone a stale lock fails every"
    echo "    seat's commit silently — it has already cost five seats 19 min."
elif [ "$LOCK_RC" -eq 2 ] && [ "$YOUNG_LIVE" -gt 0 ]; then
    echo "➜  LIVE and young — a peer is mid-commit, and a commit takes seconds."
    echo "    Do not issue the order into it. Next: wait 60s, re-run this script."
elif [ "$LOCK_RC" -eq 2 ]; then
    echo "➜  LIVE but not young — the ambiguous case. Next: wait, re-run at the"
    echo "    2-minute mark. Aged past the threshold with nothing holding it"
    echo "    open, it IS stale and the checker will print the rm."
    echo "    If the machine is going down before then, do not wait:"
    echo "      $0 --degraded \"${REASON:-reboot now, lock will not clear}\""
elif [ -n "$DIRTY" ]; then
    echo "⚠️  The tree is dirty. That is normal with five seats — but each path"
    echo "    above belongs to somebody, and they are about to commit under"
    echo "    time pressure. Remind them: explicit pathspec, never \`git add -A\`."
else
    echo "✅  Tree clean, no locks. The order below is safe to send."
fi

# --- 4. the message ---------------------------------------------------------
# Ten-line ceiling (§2), so the checklist is in its short form and the long form
# stays in the skill. The § reference is what makes the short form safe.
echo
rule
echo "PASTE THIS — one send per live seat above, addressed by name"
rule
{
    if [ "$DEGRADED" -eq 1 ]; then
        if [ -n "$REASON" ]; then
            echo "WRAP ORDER (DEGRADED) — ${REASON}. Git is locked. Stop now."
        else
            echo "WRAP ORDER (DEGRADED) — reboot now, git locked. Stop now."
        fi
        cat <<'EOF'
1 release the live bridge if you hold it — say what you left on the map
2 NO COMMIT. Do not delete a lock you have not proven stale
3 /tmp is tmpfs and dies. Move everything unreproducible into the repo tree
4 uncommitted is fine — D:\Luke\dev\Rimworld survives the reboot, /tmp does not
5 write AGENT_<SEAT>_state.md anyway; it is a file write and needs no git
6 reply WRAP DONE (DEGRADED): on disk, uncommitted, and WHICH PATHS
Protocol: skills/agent-messaging/SKILL.md §9b. Name the paths — PROJECT records
the degraded seats, and landing that work is the first act after the reboot.
EOF
    else
        if [ -n "$REASON" ]; then
            echo "WRAP ORDER — full seat reboot: ${REASON}. Stop; start nothing new."
        else
            echo "WRAP ORDER — full seat reboot. Stop; start nothing new."
        fi
        cat <<'EOF'
1 release the live bridge if you hold it — say what you left on the map
2 commit AND push: git status clean, main == origin/main
3 triage /tmp scratchpad — it is tmpfs. Bank only what cannot be regenerated
4 file the half-done in infrastructure/state/queue/<SEAT>.md, with what you already checked
5 update AGENT_<SEAT>_state.md — live state, what is owed, what is blocked
6 reply WRAP DONE, one line per item, say which did not apply
Protocol: skills/agent-messaging/SKILL.md §9. The reply is required — a silent
seat is indistinguishable from one that crashed mid-write.
EOF
    fi
}
rule
echo "Then wait for a WRAP DONE from every seat listed above. A missing reply"
echo "is a finding, not an omission — chase it before the machine goes down."
if [ "$DEGRADED" -eq 1 ]; then
    echo
    echo "Log every WRAP DONE (DEGRADED) and its paths at the TOP of"
    echo "infrastructure/state/queue/PROJECT.md before you go down. Landing those files is the first"
    echo "act of the next session; a dirty tree nobody can explain is the failure."
fi
