#!/bin/bash
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
U="$ROOT/src/RimMandrake/Utils"
B=${RM_DESIGNER_DIR:-/mnt/d/ClaudeWork/rimmandrake/designer_codex}
MODS=${RM_DESIGNER_MODS:-$(for d in "$ROOT/design/RimMandrake/designer_codex_2026-11-09/"*/; do basename "$d"; done)}
for m in $MODS; do
  [ -f $B/$m/QUESTIONS_OWNER.md ] && continue
  while [ $(jobs -rp | wc -l) -ge 4 ]; do sleep 15; done
  sed "s/__MOD__/$m/g" $B/fix_template.md > $B/$m/fix_brief.md
  ( cd $B/$m && python3 "$U/codex_side.py" exec --sandbox danger-full-access --skip-git-repo-check -C "$B/$m" -c "model_reasoning_effort=\"${CODEX_EFFORT:-medium}\"" -o "$B/$m/fix_final.md" - < fix_brief.md > fix.log 2>&1; echo "$(date +%H:%M) $m fix exit $?" >> $B/fix.log ) &
done; wait; echo "$(date +%H:%M) FIX DONE" >> $B/fix.log; ls $B/*/QUESTIONS_OWNER.md | wc -l
