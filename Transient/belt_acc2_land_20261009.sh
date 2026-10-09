#!/bin/bash
# usage: belt_acc2_land_20261009.sh "msg" ; lands the FOUNDRY shard, sitting notes, closed/moved item prose and acc2 evidence
cd /home/mandrake/rm/foundry
git fetch origin main -q
paths=(infrastructure/state/ledger/events/FOUNDRY.jsonl Transient/belt_acc_sitting2_20261009.md)
for f in Transient/belt_acc2_* Transient/belt_sitting2_* Transient/Player_sitting2*; do paths+=("$f"); done
for i in $(git status --short infrastructure/state/items | awk '{print $2}'); do
  case "$i" in *SHIPVERMIN_FREE_TIER_BEASTS_1*) continue;; esac
  if [ -e "$i" ]; then
    if git cat-file -e "origin/main:$i" 2>/dev/null; then
      cur=$(git hash-object "$i"); org=$(git rev-parse "origin/main:$i")
      [ "$cur" = "$org" ] && continue
    fi
    paths+=("$i")
  else
    git cat-file -e "origin/main:$i" 2>/dev/null && paths+=("$i")
  fi
done
/home/mandrake/.seat-tmp/land.sh -m "$1" "${paths[@]}" 2>&1 | tail -3
