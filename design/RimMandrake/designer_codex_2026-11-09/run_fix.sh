#!/bin/bash
B=/mnt/d/ClaudeWork/rimmandrake/designer_codex
C=/mnt/c/Users/Mandrake/AppData/Local/OpenAI/Codex/bin/22cfb1d302613eae/codex.exe
for d in /home/mandrake/rm/bench/design/RimMandrake/designer_codex_2026-11-09/*/; do m=$(basename $d)
  [ -f $B/$m/QUESTIONS_OWNER.md ] && continue
  while [ $(jobs -rp | wc -l) -ge 4 ]; do sleep 15; done
  sed "s/__MOD__/$m/g" $B/fix_template.md > $B/$m/fix_brief.md
  ( cd $B/$m && "$C" exec --sandbox danger-full-access --skip-git-repo-check -C "D:\\ClaudeWork\\rimmandrake\\designer_codex\\$m" -c 'model_reasoning_effort="medium"' -o "D:\\ClaudeWork\\rimmandrake\\designer_codex\\$m\\fix_final.md" - < fix_brief.md > fix.log 2>&1; echo "$(date +%H:%M) $m fix exit $?" >> $B/fix.log ) &
done; wait; echo "$(date +%H:%M) FIX DONE" >> $B/fix.log; ls $B/*/QUESTIONS_OWNER.md | wc -l
