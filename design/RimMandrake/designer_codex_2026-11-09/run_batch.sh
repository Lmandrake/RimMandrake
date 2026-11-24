#!/bin/bash
# Codex Designer dry runs (stages 0-1), 3 at a time, with a quota stop at 85% used.
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
U="$ROOT/src/RimMandrake/Utils"
DOOR="${RM_DISPATCH_ROOT:-$HOME/dev/Dispatch}/providers/chatgpt/bin/gpt_door.py"
B=${RM_DESIGNER_DIR:-/mnt/d/ClaudeWork/rimmandrake/designer_codex}
MODS=${RM_DESIGNER_MODS:-"Abyss BlueDesert Cauldron Contagion CrackedLands FeverWood GelatinousSlime Greentide LanternDeeps LeaningScrub LongShade Miasma NightsideIce RustCathedral Stillsand TheForge TheRot TheSump Wasteland Webwork WeepingStones Scarlands AtmosphericBase"}
quota() { cd "$U" && python3 -c "
import sys,time,json;sys.path.insert(0,'.');import ops_watch as O
r=O.c_codex(time.time(), json.load(open('ops_watch_rules.json')), {})
v=r['codex.week_used_pct'];print(v['v'] if v.get('m') in ('MEASURED','ESTIMATE') else 999)" 2>/dev/null || echo 999; }
for m in $MODS; do
  [ -f $B/$m/QUESTIONS.md ] && { echo "$m skip (done)"; continue; }
  q=$(quota); if python3 -c "import sys; sys.exit(0 if float('$q')<85 else 1)"; then :; else echo "STOP quota $q before $m"; break; fi
  while [ $(jobs -rp | wc -l) -ge 3 ]; do sleep 20; done
  mkdir -p $B/$m; sed "s/__MOD__/$m/g" $B/brief_template.md > $B/$m/designer_brief.md
  ( cd $B/$m && python3 "$DOOR" agent --sandbox danger-full-access --cwd "$B/$m" --model inherit --effort "${CODEX_EFFORT:-high}" --result "$B/$m/designer_final.md" --task-file designer_brief.md > designer.log 2>&1; echo "$(date +%H:%M) $m exit $? quota_before $q" >> $B/batch.log ) &
  echo "$(date +%H:%M) launched $m (quota $q)" >> $B/batch.log
done
wait; echo "$(date +%H:%M) BATCH DONE" >> $B/batch.log; tail -30 $B/batch.log
