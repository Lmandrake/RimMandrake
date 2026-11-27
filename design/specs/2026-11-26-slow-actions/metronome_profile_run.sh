#!/bin/bash
# Profiles of what the two metronome units run, for metronome_profile.md. Run on Archmagi:
#   ssh mandrake@archmagi-wsl bash -s < design/specs/2026-11-26-slow-actions/metronome_profile_run.sh
# Sense: the same argv as rm-metronome-sense's child, without --file-alarms and --metronome-gen, against a scratch
# copy of the live ops_watch store on the same drive (/mnt/d), so nothing is filed and the live store is not written.
# Beat: metronome's own start (no child), the dispatcher's dry tick (no --apply) and remember, raise and ring
# read-only. Writes only under $S.
set -u
S=/mnt/d/ClaudeWork/rimmandrake/scratch/metprof
R=/home/mandrake/rm/dispatch
mkdir -p "$S"
rm -rf "$S/ops_watch"; cp -r /mnt/d/ClaudeWork/rimmandrake/ops_watch "$S/ops_watch"
cd "$R"
uptime
t() {  # name, then the command: wall, user, sys, max RSS
  local n=$1; shift
  # </dev/null: a child that reads stdin (the steve family's ssh) would eat the rest of this script under `bash -s`
  /usr/bin/time -f "$n wall=%e user=%U sys=%S rss_kb=%M" "$@" > "$S/$n.out" 2> "$S/$n.time" < /dev/null; tail -1 "$S/$n.time"
}
export RM_OPS_WATCH_DIR=$S/ops_watch
P="$(command -v python3)"
OW=src/RimMandrake/Utils/ops_watch.py
t py_bare "$P" -c pass
t ow_import "$P" -c "import sys; sys.path.insert(0,'src/RimMandrake/Utils'); import ops_watch"
t met_load "$P" -c "import sys; sys.path.insert(0,'src/RimMandrake/Utils'); import metronome; metronome.load_table()"
for pair in "steve testing" "disk timers" "queues wrapup" "flow process" "tps production" "maturation pager" \
            "evidence roles" "process tokentalk" "steve codex"; do
  set -- $pair
  n="sense_$1_$2"
  t "$n" "$P" -m cProfile -o "$S/$n.prof" $OW run --compose --family "$1" --family "$2"
  t "${n}_plain" "$P" $OW run --compose --family "$1" --family "$2"
done
unset RM_OPS_WATCH_DIR
t dispatch_dry "$P" -m cProfile -o "$S/dispatch_dry.prof" src/RimMandrake/rimflow/dispatcher.py tick --json
t dispatch_dry_plain "$P" src/RimMandrake/rimflow/dispatcher.py tick --json
uptime
# the three small beat phases, read-only: remember into a scratch page, raise with --no-file, ring as it runs
mkdir -p "$S/memout"
t remember "$P" -m cProfile -o "$S/remember.prof" src/RimMandrake/Utils/ops_memory.py build --out "$S/memout"
t raise "$P" -m cProfile -o "$S/raise.prof" src/RimMandrake/Utils/restart_reconcile.py run --no-file
t ring "$P" -m cProfile -o "$S/ring.prof" src/RimMandrake/rimflow/dispatcher.py status
