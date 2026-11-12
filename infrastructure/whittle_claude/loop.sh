#!/bin/bash
# One Claude Whittle worker: forever, one ticket at a time (owner order 2026-11-11 ~19:10 PST, and ~19:40 "Yes maximize
# stevedesktop too"). Run by the systemd user unit whittle-claude@<WORKER>.service (install.sh); never by hand twice.
#
#   loop.sh <WORKER>
#
# A round is three phases (owner order 2026-11-11 ~20:40 PST: "check the tickets deterministically first"):
#   SETUP   wc.py setup, no model: the eligibility gate (wc.py gate prints every pick and skip with its reason), both
#           claims (shared table + ledger), whittle/<dir>/ STATEMENT, NOTES, MODE, PROMPT; commit and publish.
#           Last line PICKED <ID> <dir> <mode> | NONE <why>.
#   WHITTLE MandrakeWorkflows whittle/run.py --runner claude with WHITTLE=1 WHITTLE_DIR=whittle/<dir>: builds until its
#           Stop hook (DONE + BROADEN + a fresh judge) lets it stop. rc 1 (incomplete) runs again, at most 3 runs.
#   WRAPUP  wc.py wrapup, no model, for every mechanical ending (ghost, closed upstream, failed, parked). Only a Whittle
#           exit 0 needs a model to read DONE.md and the judge and close: claude -p (wrapup.md) on sonnet with a slim
#           context (no CLAUDE.md layers, no MCP, Bash+Read, turn and dollar caps). Last line RESULT <ID> <ending> sha=.
# Each round's spend (setup / whittle / wrapup, raw, weighted with cache reads at 0.1, and cost_usd; a killed Whittle
# run read from its session transcripts) goes to rounds/<N>/spend.json and onto the round's end line.
# At each round boundary the loop re-runs itself when the clone's loop.sh changed (its private copy is replaced first).
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
export WC_LOOP=2   # wc.py: this loop runs setup itself (an older loop gets its pick through the shortlist instead)
RUNPY="$MW/whittle/run.py"
unset WHITTLE WHITTLE_DIR CLAUDECODE

# run from a private copy, so a pull that rewrites loop.sh never changes the script under a running bash
if [ "${WC_RUNCOPY:-}" != 1 ]; then
    mkdir -p "$WC_DIR"
    cp "$0" "$WC_DIR/loop.run.sh.tmp" && mv -f "$WC_DIR/loop.run.sh.tmp" "$WC_DIR/loop.run.sh" \
        && WC_RUNCOPY=1 exec /bin/bash "$WC_DIR/loop.run.sh" "$W"
    echo "could not make the private run copy $WC_DIR/loop.run.sh: not running the clone's mutable loop.sh" >&2; exit 1
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
hard_stop() {   # exit 0 and the reason while nothing new may start: a hard stop, or a notice that cannot be read (fail safe;
    # on SteveDesktop wc.py asks Archmagi's copy over ssh, where the switcher writes notice.json)
    local r rc; r=$($WC hardstop 2>&1); rc=$?
    case $rc in
        0) echo "$r" ;;
        1) return 1 ;;
        *) echo "the account switcher's notice cannot be read (wc.py hardstop exit $rc: $(tr '\n' ' ' <<<"$r" | cut -c1-200)); waiting, fail safe" ;;
    esac
}
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
claude_slim() {   # claude_slim <log> <prompt>: one headless sonnet with only what the brief needs, 40 min at most.
    # No settings files (so no CLAUDE.md layers and no claude.ai connectors), no MCP, no skills; the lane's PreToolUse
    # gate passed inline because the clone's settings.local.json is not read; turns and dollars capped.
    local hook
    hook=$(printf '{"hooks":{"PreToolUse":[{"matcher":"Bash","hooks":[{"type":"command","command":"python3 %s %s"}]}]}}' \
        "$HERE/gate.py" "$BRIEF")
    timeout -k 120 2400 claude -p "$2" --model sonnet --output-format json --setting-sources "" --strict-mcp-config \
        --mcp-config '{"mcpServers":{}}' --disable-slash-commands --tools "Bash,Read" --settings "$hook" \
        --max-turns "${WC_MAX_TURNS:-40}" --max-budget-usd "${WC_MAX_USD:-2}" --dangerously-skip-permissions \
        >"$1" 2>"$1.err"
}
spend_line() {   # the round's spend: rounds/<N>/spend.json, one readable log line, and the key=value tail for the end line
    local out; out=$($WC spend "$RD" --clone "$CLONE" 2>/dev/null) || { echo "tokens=unknown"; return; }
    lg "round $ROUND spend: $(head -n 1 <<<"$out")" >/dev/null
    tail -n 1 <<<"$out"
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
release_bridge() {   # only the live lanes ever take the bridge; a failed release is logged, not hidden
    local out rc=0
    case "$BRIEF" in
        archmagi) out=$(python3 "$CLONE/src/RimMandrake/rimflow/cli.py" bridge release --mine 2>&1) || rc=$? ;;
        steve) out=$(python3 "$CLONE/src/RimMandrake/rimflow/cli.py" bridge release --host stevedesktop --mine 2>&1) || rc=$? ;;
        *) return 0 ;;
    esac
    [ "$rc" = 0 ] || lg "note: bridge release failed (rc=$rc): $(tail -n 2 <<<"$out" | tr '\n' ' ' | cut -c1-200)" >/dev/null
    true
}
unclaim_logged() {   # unclaim_logged <ID>: a failed unclaim (ssh from SteveDesktop) is said, not swallowed
    local out; out=$($WC unclaim "$W" "$1" 2>&1) || lg "note: unclaim $1 failed: $(tr '\n' ' ' <<<"$out" | cut -c1-200)" >/dev/null
}
housekeeping() {   # at a round start: sync.log rotated at 5 MB, round folders older than 14 days removed
    local f="$WC_DIR/sync.log"
    [ -f "$f" ] && [ "$(stat -c %s "$f" 2>/dev/null || echo 0)" -gt 5242880 ] && mv -f "$f" "$f.1"
    find "$WC_DIR/rounds" -mindepth 1 -maxdepth 1 -type d -mtime +14 -exec rm -rf {} + 2>/dev/null
    true
}
disk_guard() {   # the drive this round fills: the SteveDesktop live lane builds on SteveDesktop, so ask SteveDesktop
    if [ "$BRIEF" = steve ]; then
        ssh -o BatchMode=yes -o ConnectTimeout=10 -o LogLevel=ERROR mandrake@stevedesktop-wsl python3 - diskfree \
            < "$HERE/wc.py" 2>&1
    else
        $WC diskfree 2>&1
    fi
}

trap 'release_bridge' EXIT
trap 'exit 143' TERM INT
st --state idle --note "loop started on $MACHINE (pid $$)"
lg "loop start: $W on $MACHINE, clone $CLONE, unit $UNIT"
FAILS=0
while :; do
    stopped_by_file && { st --state stopped --item - --note "STOP file: loop ended cleanly"; lg "loop end: STOP file"; exit 0; }
    wait_hard_stop
    PHASE=$(cur phase)
    if [ -z "$PHASE" ]; then   # ---------------------------------------------------- a new round: SETUP
        level_clone
        if ! cmp -s "$HERE/loop.sh" "$0"; then   # the clone's loop.sh changed: run the new one from here
            cp "$HERE/loop.sh" "$WC_DIR/loop.run.sh.tmp" && mv -f "$WC_DIR/loop.run.sh.tmp" "$WC_DIR/loop.run.sh" && {
                lg "loop.sh changed in the clone: re-running the new copy at this round boundary"
                WC_RUNCOPY=1 exec /bin/bash "$WC_DIR/loop.run.sh" "$W"; }
        fi
        ROUND=$(( $(cat "$WC_DIR/round.txt" 2>/dev/null || echo 0) + 1 ))   # written once an item is picked
        housekeeping
        rm -f "$CUR"; setcur round="$ROUND" phase=setup tries=0 || { lg "note: cannot write $CUR; next look in 5 min"; sleep 300; }
        continue
    fi
    ROUND=$(cur round); RD="$WC_DIR/rounds/$ROUND"; mkdir -p "$RD"; TRIES=$(cur tries); TRIES=${TRIES:-0}
    case "$PHASE" in
    setup)
        if ! DF=$(disk_guard); then   # the backing drive is under the floor: no new round (SteveDesktop C:, 2026-11-11)
            lg "idle: disk guard: $DF; next look in 30 min"; st --state idle --item - --note "disk guard: $DF"
            stopped_by_file && { lg "loop end: STOP file"; exit 0; }; sleep 1800; continue
        fi
        OPEN=$($WC lane-open "$LANE" 2>/dev/null || echo "?")
        st --state working --round "$ROUND" --item - --note "round $ROUND: picking from $OPEN open $LANE items"
        # every open item's pick or skip with its reason, for a person to read (the setup below re-runs the same gate)
        $WC shortlist "$W" "$LANE" --no-pick --why --n 15 >"$RD/gate.txt" 2>&1
        $WC setup "$W" "$LANE" --round "$ROUND" >"$RD/setup.out" 2>>"$RD/setup.log"
        rc=$?; LAST=$(tail -n 1 "$RD/setup.out"); mirror
        case "$LAST" in
            PICKED\ *)
                read -r _ ID DIR MODE <<<"$LAST"
                if ! [[ "$ID" =~ ^[A-Z][A-Z0-9_]+$ ]] || [ "$DIR" != "${ID,,}" ] || [ ! -e "infrastructure/state/items/$ID.md" ] \
                    || ! $WC mine "$W" 2>/dev/null | grep -qx "$ID"; then
                    lg "round $ROUND setup said '$LAST' but it does not check (id, dir, live file, our claim): not started"
                    unclaim_logged "$ID"; rm -f "$CUR"; FAILS=$((FAILS + 1)); sleep 120; continue
                fi
                setcur phase=whittle item="$ID" dir="whittle/$DIR" mode="${MODE:-whittle}" tries=0 open="$OPEN" \
                    || { lg "note: cannot write $CUR; next look in 5 min"; unclaim_logged "$ID"; sleep 300; continue; }
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
                if hard_stop >/dev/null; then wait_hard_stop; continue; fi   # stopped by the switcher: not a try
                TRIES=$((TRIES + 1)); setcur tries="$TRIES"
                lg "round $ROUND setup did not finish (rc=$rc, try $TRIES): $(tail -c 300 "$RD/setup.log" | tr '\n' ' ')"
                if [ "$TRIES" -ge 3 ]; then
                    # a half-done pick: whatever it claimed goes back, so no other loop waits on it
                    for id in $($WC mine "$W" 2>/dev/null); do unclaim_logged "$id"; done
                    lg "setup failed 3 times without a pick (round $ROUND not started)"; rm -f "$CUR"; FAILS=$((FAILS + 1))
                fi
                st --state blocked --note "round $ROUND setup failed (rc=$rc), retrying"; sleep $((120 * (FAILS + 1))) ;;
        esac ;;
    whittle)
        ID=$(cur item); DIR=$(cur dir)
        if [ ! -e "infrastructure/state/items/$ID.md" ]; then   # a ledger ghost: no live item file, nothing to build
            lg "round $ROUND $ID has no live item file (ghost): to wrap-up to release it"
            setcur phase=wrapup whittle_rc=ghost tries=0; continue
        fi
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
        date +%s > "$RD/whittle.$N.t0"   # the window wc.py spend reads the session transcripts in, if this run is killed
        WHITTLE=1 WHITTLE_DIR="$DIR" WHITTLE_LOOP_LIMIT=3 WC_ITEM="$ID" \
            timeout -k 120 23000 python3 "$RUNPY" --runner claude --cwd "$CLONE" --log "$RD/whittle.$N.log" --model opus \
            >"$RD/whittle.$N.out" 2>&1
        rc=$?; date +%s > "$RD/whittle.$N.t1"; mirror
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
        $WC wrapup "$W" "$ID" --dir "$DIR" --rc "$WRC" --round "$ROUND" >"$RD/wrapup.out" 2>>"$RD/wrapup.log"
        rc=$?; LAST=$(tail -n 1 "$RD/wrapup.out")
        if [ "$rc" = 5 ]; then   # a Whittle exit 0: a model reads DONE.md and the judge, and closes
            claude_slim "$RD/wrapup.json" "$(brief wrapup.md "## This round" "Item: $ID" "Whittle directory: $DIR" \
                "Whittle exit code: $WRC" "Whittle runner output tail:" "$(tail -n 20 "$RD"/whittle.*.out 2>/dev/null | tail -n 20)")"
            rc=$?; LAST=$(last_line "$RD/wrapup.json")
        fi
        mirror
        case "$LAST" in
            RESULT\ "$ID"\ closed\ *|RESULT\ "$ID"\ parked\ *|RESULT\ "$ID"\ dropped\ *|RESULT\ "$ID"\ failed\ *|RESULT\ "$ID"\ released\ *)
                read -r _ RID END SHA <<<"$LAST"
                release_bridge; unclaim_logged "$ID"; publish_leftovers
                lg "round $ROUND end: $ID $END $SHA $(spend_line)"
                st --state idle --item - --note "round $ROUND: $ID $END ($SHA)"
                rm -f "$CUR"; FAILS=0 ;;
            *)
                if hard_stop >/dev/null; then wait_hard_stop; continue; fi   # stopped by the switcher: not a try
                TRIES=$((TRIES + 1)); setcur tries="$TRIES"
                lg "round $ROUND wrapup did not finish (rc=$rc, try $TRIES): last line '$(cut -c1-160 <<<"$LAST")'"
                if [ "$TRIES" -ge 3 ]; then
                    release_bridge; unclaim_logged "$ID"; publish_leftovers
                    python3 src/RimMandrake/rimflow/cli.py note "$ID" --text "Claude Whittle $W round $ROUND: the wrap-up failed 3 times; the work so far is in $DIR and $RD" \
                        --why "loop.sh: wrap-up never returned a RESULT line" >/dev/null 2>&1; publish_leftovers
                    lg "round $ROUND end: $ID failed sha=none $(spend_line)"
                    st --state idle --item - --note "round $ROUND: $ID wrap-up failed 3 times"
                    rm -f "$CUR"; FAILS=$((FAILS + 1))
                fi
                sleep 120 ;;
        esac ;;
    *) lg "round $ROUND: unknown phase $PHASE, starting a new round"; rm -f "$CUR" ;;
    esac
    [ "$FAILS" -ge 3 ] && { st --state blocked --item - --note "3 failed rounds in a row; pausing 1 h"; lg "pause: 3 failed rounds in a row"; sleep 3600; FAILS=0; }
done
