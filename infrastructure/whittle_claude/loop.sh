#!/bin/bash
# One Claude Whittle worker: forever, one ticket at a time (owner order 2026-11-11 ~19:10 PST, and ~19:40 "Yes maximize
# stevedesktop too"). Run by the systemd user unit whittle-claude@<WORKER>.service (install.sh); never by hand twice.
#
#   loop.sh <WORKER>
#
# A round is three phases, each a fresh Claude so no context outlives its ticket:
#   SETUP   claude -p (setup.md): pick one item from wc.py's shortlist, claim it (shared claims table + ledger), write
#           whittle/<dir>/ STATEMENT, NOTES, MODE, PROMPT; commit and publish. Last line PICKED <ID> <dir> <mode> | NONE.
#   WHITTLE MandrakeWorkflows whittle/run.py --runner claude with WHITTLE=1 WHITTLE_DIR=whittle/<dir>: builds until its
#           Stop hook (DONE + BROADEN + a fresh judge) lets it stop. rc 1 (incomplete) runs again, at most 3 runs.
#   WRAPUP  claude -p (wrapup.md): close | park (OWNER_QUESTIONS.md) | drop | failed; release the bridge; commit, publish,
#           unclaim. Last line RESULT <ID> <ending> sha=<sha>.
# The round's phase is in $WC_DIR/current.json, so a restart (WSL restart, unit restart, the account switcher's hard
# stop) resumes the same phase on the same item. While the switcher's notice says hard stop the loop waits, state
# "stopped". $WC_DIR/STOP (or the clone's infrastructure/whittle_claude/STOP.<WORKER>) ends the loop cleanly at a round
# boundary. Status for the WHITTLE_NOW page: worker.json and loop.log through wc.py, every stamp with its full date.
set -uo pipefail
W=${1:?usage: loop.sh <WORKER>}

# --- the worker table -------------------------------------------------------------------------------------------------
case "$W" in
    CLAUDE_ARCHMAGI_FWLIVE)       MACHINE=Archmagi;     LANE=fwlive;  BRIEF=archmagi; GAME=Archmagi
                                  CLONE=/home/mandrake/rm/scratch/BENCH/claude-archmagi-fwlive ;;
    CLAUDE_STEVEDESKTOP_FWLIVE)   MACHINE=Archmagi;     LANE=fwlive;  BRIEF=steve;    GAME=SteveDesktop
                                  CLONE=/home/mandrake/rm/scratch/BENCH/claude-steve-fwlive ;;
    CLAUDE_ARCHMAGI_OFFLINE[0-9]) MACHINE=Archmagi;     LANE=offline; BRIEF=offline;  GAME=none
                                  CLONE=/home/mandrake/rm/scratch/BENCH/claude-archmagi-offline${W##*OFFLINE} ;;
    CLAUDE_STEVEDESKTOP_OFFLINE[0-9]) MACHINE=SteveDesktop; LANE=offline; BRIEF=offline; GAME=none
                                  CLONE=/home/mandrake/rm/claude-offline${W##*OFFLINE} ;;
    *) echo "unknown worker $W" >&2; exit 64 ;;
esac
[ "${2:-}" = --where ] && { echo "$MACHINE $CLONE $BRIEF"; exit 0; }   # install.sh reads the table here
HERE="$CLONE/infrastructure/whittle_claude"   # the briefs come from the clone, not from the private run copy
UNIT="whittle-claude@$W.service"
WC_HOME=${WC_HOME:-/mnt/d/ClaudeWork/rimmandrake/whittle_claude}
export WC_DIR="$WC_HOME/$W" WC_HOME
# On SteveDesktop the status, log and claims live on Archmagi (one claims table; the WHITTLE_NOW page reads Archmagi's
# folder): wc.py forwards to Archmagi's copy over ssh, and progress.md / OWNER_QUESTIONS.md are mirrored after each phase.
[ "$MACHINE" = SteveDesktop ] && export WC_REMOTE=${WC_REMOTE:-mandrake@archmagi-wsl}
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
export RIMFLOW_SEAT=$W AGENT_SEAT=$W RIMFLOW_BRIDGE_SEAT=$W
export WSLENV="${WSLENV:+$WSLENV:}RIMFLOW_SEAT:AGENT_SEAT:RIMFLOW_BRIDGE_SEAT"
# the Whittle runner: MandrakeWorkflows whittle/ and tools/ (install.sh copies them to SteveDesktop, whose checkout is old)
MW=${WC_MW:-$HOME/dev/MandrakeWorkflows}
[ -e "$MW/whittle/run.py" ] || MW="$HOME/.local/share/whittle-claude/mw"
export WC_LANE=$BRIEF WC_TEMPLATE="$MW/whittle/template"
RUNPY="$MW/whittle/run.py"
unset WHITTLE WHITTLE_DIR CLAUDECODE

# run from a private copy, so a pull that rewrites loop.sh never changes the script under a running bash
if [ "${WC_RUNCOPY:-}" != 1 ]; then
    mkdir -p "$WC_DIR"
    cp "$0" "$WC_DIR/loop.run.sh" && WC_RUNCOPY=1 exec /bin/bash "$WC_DIR/loop.run.sh" "$W"
fi
mkdir -p "$WC_DIR/rounds"
touch "$WC_DIR/progress.md" "$WC_DIR/OWNER_QUESTIONS.md"
cd "$CLONE" || { echo "no clone $CLONE" >&2; exit 1; }
WC="python3 $CLONE/infrastructure/whittle_claude/wc.py"
CUR="$WC_DIR/current.json"

st()  { $WC status "$W" --unit "$UNIT" --machine "$MACHINE" --lane "$LANE" --game "$GAME" "$@" >/dev/null 2>&1 || true; }
lg()  { $WC log "$W" "$@" >/dev/null 2>&1 || true; echo "$(date '+%F %T %z') $*"; }
cur() { python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get(sys.argv[2]) or "")' "$CUR" "$1" 2>/dev/null; }
setcur() {   # setcur key=value ...
    python3 - "$CUR" "$@" <<'EOF'
import json, os, sys
p = sys.argv[1]
try: d = json.load(open(p))
except Exception: d = {}
for kv in sys.argv[2:]:
    k, v = kv.split("=", 1); d[k] = v
json.dump(d, open(p + ".tmp", "w"), indent=1); os.replace(p + ".tmp", p)
EOF
}
mirror() { [ -n "${WC_REMOTE:-}" ] && rsync -a -e "ssh -o BatchMode=yes -o ConnectTimeout=10" "$WC_DIR/progress.md" "$WC_DIR/OWNER_QUESTIONS.md" "$WC_REMOTE:$WC_DIR/" >/dev/null 2>&1; true; }
stopped_by_file() { [ -e "$WC_DIR/STOP" ] || [ -e "$CLONE/infrastructure/whittle_claude/STOP.$W" ]; }
hard_stop() { python3 -c 'import sys; sys.path.insert(0, "src/RimMandrake/Utils"); import account_stop_notice as a; r = a.hard_stop_reason(); print(r or ""); sys.exit(0 if r else 1)' 2>/dev/null; }
wait_hard_stop() {   # the account switcher stopped the fleet: wait for its notice to clear, then go on where we were
    local r; r=$(hard_stop) || return 0
    lg "round $(cur round) paused: account hard stop: $r"
    while r=$(hard_stop); do st --state stopped --note "account hard stop: $r"; stopped_by_file && exit 0; sleep 60; done
    lg "round $(cur round) resumed after the account hard stop"
    st --state working --note "resumed after the account hard stop"
}
last_line() {   # the final result text of a `claude -p --output-format json` log
    python3 - "$1" <<'EOF'
import json, sys
txt = ""
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    try: d = json.loads(line)
    except ValueError: continue
    if isinstance(d, dict) and d.get("type") == "result": txt = d.get("result") or ""
lines = [l.strip() for l in txt.strip().splitlines() if l.strip()]
print(lines[-1] if lines else "")
EOF
}
brief() {   # the prompt for a claude -p phase: common + lane + phase brief, with this worker's values filled in
    { cat "$HERE/common.md" "$HERE/lane_$BRIEF.md" "$HERE/$1"; shift; printf '\n%s\n' "$@"; } \
        | sed -e "s#\$RIMFLOW_SEAT#$W#g" -e "s#\$WC_DIR#$WC_DIR#g" -e "s#\$WC_TEMPLATE#$WC_TEMPLATE#g" -e "s#\$WC_LANE#$BRIEF#g"
}
claude_phase() {   # claude_phase <log> <prompt>: one headless Claude, 2 h at most
    timeout 7200 claude -p "$2" --model opus --output-format json --dangerously-skip-permissions >"$1" 2>"$1.err"
}
level_clone() {   # only between tickets: bring the clone to origin/main
    ./sync >>"$WC_DIR/sync.log" 2>&1 || lg "note: ./sync failed before round $(( $(cat "$WC_DIR/round.txt" 2>/dev/null || echo 0) + 1 )); see $WC_DIR/sync.log"
}
publish_leftovers() {   # a round may end with its shard or OWNER.jsonl unpublished: land them, nothing else
    local p=() f
    for f in "infrastructure/state/ledger/events/$W.jsonl" infrastructure/state/ledger/events/OWNER.jsonl; do
        [ -e "$f" ] || continue
        if ! git ls-files --error-unmatch -- "$f" >/dev/null 2>&1 || ! git diff --quiet HEAD -- "$f" 2>/dev/null; then p+=("$f"); fi
    done
    [ ${#p[@]} -eq 0 ] && return 0
    git add -- "${p[@]}" && git commit -q "${p[@]}" -F - <<EOF >/dev/null 2>&1
ledger: $W round $(cur round) leftovers

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
    ./publish >/dev/null 2>&1 || lg "round $(cur round) note: ./publish of the ledger leftovers failed"
}
release_bridge() {
    case "$BRIEF" in
        archmagi) python3 src/RimMandrake/rimflow/cli.py bridge release --mine >/dev/null 2>&1 ;;
        steve) python3 src/RimMandrake/rimflow/cli.py bridge release --host stevedesktop --mine >/dev/null 2>&1 ;;
    esac
    true
}

st --state idle --note "loop started on $MACHINE (pid $$)"
lg "loop start: $W on $MACHINE, clone $CLONE, unit $UNIT"
FAILS=0
while :; do
    stopped_by_file && { st --state stopped --item - --note "STOP file: loop ended cleanly"; lg "loop end: STOP file"; exit 0; }
    wait_hard_stop
    PHASE=$(cur phase)
    if [ -z "$PHASE" ]; then   # ---------------------------------------------------- a new round: SETUP
        level_clone
        ROUND=$(( $(cat "$WC_DIR/round.txt" 2>/dev/null || echo 0) + 1 ))   # written once an item is picked
        rm -f "$CUR"; setcur round="$ROUND" phase=setup tries=0
        continue
    fi
    ROUND=$(cur round); RD="$WC_DIR/rounds/$ROUND"; mkdir -p "$RD"; TRIES=$(cur tries); TRIES=${TRIES:-0}
    case "$PHASE" in
    setup)
        OPEN=$($WC lane-open "$LANE" 2>/dev/null || echo "?")
        st --state working --round "$ROUND" --item - --note "round $ROUND: picking from $OPEN open $LANE items"
        SL=$($WC shortlist "$W" "$LANE" --n 15 2>&1 | tail -n 16)
        claude_phase "$RD/setup.json" "$(brief setup.md "## Your shortlist (wc.py shortlist $W $LANE, ranked)" "$SL")"
        rc=$?; LAST=$(last_line "$RD/setup.json"); mirror
        case "$LAST" in
            PICKED\ *)
                read -r _ ID DIR MODE <<<"$LAST"
                setcur phase=whittle item="$ID" dir="whittle/$DIR" mode="${MODE:-whittle}" tries=0 open="$OPEN"
                echo "$ROUND" > "$WC_DIR/round.txt"
                lg "round $ROUND start, open=$OPEN item=$ID"
                lg "round $ROUND $ID claimed, mode ${MODE:-whittle}, whittle/$DIR"
                st --state working --item "$ID" --note "round $ROUND: $ID claimed, mode ${MODE:-whittle}; Whittle starting"
                FAILS=0 ;;
            NONE*)
                lg "idle: nothing to take from $OPEN open $LANE items: ${LAST#NONE }; next look in 30 min"
                st --state idle --item - --note "nothing to take (${LAST#NONE }); next look in 30 min"
                rm -f "$CUR"; publish_leftovers; sleep 1800 ;;
            *)
                wait_hard_stop
                TRIES=$((TRIES + 1)); setcur tries="$TRIES"
                lg "round $ROUND setup did not finish (rc=$rc, try $TRIES): $(tail -c 300 "$RD/setup.json.err" | tr '\n' ' ')"
                if [ "$TRIES" -ge 3 ]; then
                    # a half-done pick: whatever it claimed goes back, so no other loop waits on it
                    for id in $($WC mine "$W" 2>/dev/null); do $WC unclaim "$W" "$id" >/dev/null 2>&1; done
                    lg "setup failed 3 times without a pick (round $ROUND not started)"; rm -f "$CUR"; FAILS=$((FAILS + 1))
                fi
                st --state blocked --note "round $ROUND setup failed (rc=$rc), retrying"; sleep $((120 * (FAILS + 1))) ;;
        esac ;;
    whittle)
        ID=$(cur item); DIR=$(cur dir)
        mkdir -p "$DIR/evidence"
        # the Whittle machinery: the templates with their paths pointed at this item's directory
        for f in DONE.md JUDGE_PROMPT.md; do [ -e "$DIR/$f" ] || sed "s#whittle/#$DIR/#g" "$WC_TEMPLATE/$f" > "$DIR/$f"; done
        grep -q "This loop's round" "$DIR/PROMPT.md" 2>/dev/null || {
            [ -s "$DIR/PROMPT.md" ] || sed "s#whittle/#$DIR/#g" "$WC_TEMPLATE/PROMPT.md" > "$DIR/PROMPT.md"
            sed -e "s#\$WC_LANE#$BRIEF#g" -e "s#\$WC_ITEM#$ID#g" -e "s#\$WHITTLE_DIR#$DIR#g" -e "s#\$RIMFLOW_SEAT#$W#g" \
                "$HERE/builder.md" >> "$DIR/PROMPT.md"; }
        N=$((TRIES + 1))
        st --state working --item "$ID" --note "round $ROUND: $ID Whittle run $N of 3"
        lg "round $ROUND $ID whittle run $N"
        WHITTLE=1 WHITTLE_DIR="$DIR" WHITTLE_LOOP_LIMIT=3 WC_ITEM="$ID" \
            timeout 23000 python3 "$RUNPY" --runner claude --cwd "$CLONE" --log "$RD/whittle.$N.log" --model opus \
            >"$RD/whittle.$N.out" 2>&1
        rc=$?; mirror
        if [ "$rc" = 0 ] || [ "$rc" = 2 ]; then
            setcur phase=wrapup whittle_rc="$rc" tries=0
        else
            if hard_stop >/dev/null; then wait_hard_stop; continue; fi   # killed by the switcher: same run again
            TRIES=$N; setcur tries="$TRIES" whittle_rc="$rc"
            [ "$TRIES" -ge 3 ] && setcur phase=wrapup tries=0
        fi
        lg "round $ROUND $ID whittle run $N exit $rc" ;;
    wrapup)
        ID=$(cur item); DIR=$(cur dir); WRC=$(cur whittle_rc)
        st --state working --item "$ID" --note "round $ROUND: $ID wrapping up (Whittle exit $WRC)"
        claude_phase "$RD/wrapup.json" "$(brief wrapup.md "## This round" "Item: $ID" "Whittle directory: $DIR" \
            "Whittle exit code: $WRC" "Whittle runner output tail:" "$(tail -n 20 "$RD"/whittle.*.out 2>/dev/null | tail -n 20)")"
        rc=$?; LAST=$(last_line "$RD/wrapup.json"); mirror
        case "$LAST" in
            RESULT\ *)
                read -r _ RID END SHA <<<"$LAST"
                TOK=$($WC tokens "$RD"/setup.json "$RD"/wrapup.json "$RD"/whittle.*.log 2>/dev/null || echo "")
                release_bridge; $WC unclaim "$W" "$ID" >/dev/null 2>&1; publish_leftovers
                lg "round $ROUND end: $ID $END $SHA tokens=${TOK:-unknown}"
                st --state idle --item - --note "round $ROUND: $ID $END ($SHA)"
                rm -f "$CUR"; FAILS=0 ;;
            *)
                wait_hard_stop
                TRIES=$((TRIES + 1)); setcur tries="$TRIES"
                lg "round $ROUND wrapup did not finish (rc=$rc, try $TRIES)"
                if [ "$TRIES" -ge 3 ]; then
                    release_bridge; $WC unclaim "$W" "$ID" >/dev/null 2>&1; publish_leftovers
                    python3 src/RimMandrake/rimflow/cli.py note "$ID" --text "Claude Whittle $W round $ROUND: the wrap-up failed 3 times; the work so far is in $DIR and $RD" \
                        --why "loop.sh: wrap-up never returned a RESULT line" >/dev/null 2>&1; publish_leftovers
                    lg "round $ROUND end: $ID failed sha=none tokens=unknown"
                    st --state idle --item - --note "round $ROUND: $ID wrap-up failed 3 times"
                    rm -f "$CUR"; FAILS=$((FAILS + 1))
                fi
                sleep 120 ;;
        esac ;;
    *) lg "round $ROUND: unknown phase $PHASE, starting a new round"; rm -f "$CUR" ;;
    esac
    [ "$FAILS" -ge 3 ] && { st --state blocked --item - --note "3 failed rounds in a row; pausing 1 h"; lg "pause: 3 failed rounds in a row"; sleep 3600; FAILS=0; }
done
