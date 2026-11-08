#!/bin/bash
# g8_fetch.sh <run|latest|latest-depth|latest-kit|latest-site> <local dir>   (run on Archmagi, from anywhere)
# Tar one g8 run folder on Steve (Transient/ralph_fw/g8/<run>: log.txt, results.jsonl, shots/) and fetch it in ONE copy,
# unpacked under <local dir>/<run>/. Prints the run name and how many shots came back.
set -e
WHICH="$1"; D="$2"
[ -n "$WHICH" ] && [ -n "$D" ] || { sed -n 2,3p "$0"; exit 64; }
cd "$(dirname "$0")/../.."
case "$WHICH" in
    latest) PAT='*' ;;
    latest-*) PAT="${WHICH#latest-}_*" ;;
    *) PAT="" ;;
esac
if [ -n "$PAT" ]; then
    WHICH=$(ralph/steve.sh run "ls -1td Transient/ralph_fw/g8/$PAT 2>/dev/null | head -n 1 | xargs -r basename")
    [ -n "$WHICH" ] || { echo "no g8 run matching $PAT on Steve" >&2; exit 1; }
fi
ralph/steve.sh run "cd Transient/ralph_fw/g8 && tar cf ../g8_fetch_$WHICH.tar $WHICH && echo packed" >/dev/null
mkdir -p "$D"
ralph/steve.sh fetch "Transient/ralph_fw/g8_fetch_$WHICH.tar" "$D" >/dev/null
tar xf "$D/g8_fetch_$WHICH.tar" -C "$D" && rm "$D/g8_fetch_$WHICH.tar"
ralph/steve.sh run "rm -f Transient/ralph_fw/g8_fetch_$WHICH.tar" >/dev/null
echo "$WHICH: $(ls "$D/$WHICH/shots" 2>/dev/null | wc -l) shots in $D/$WHICH"
