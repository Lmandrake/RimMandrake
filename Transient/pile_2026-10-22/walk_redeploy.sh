#!/bin/bash
# Walk driver redeploy: copy the COMMITTED FlowWorks DLL pair (+ any committed FlowWorks file the plan lists as drifting) from
# origin/main into the game, relaunch, reload save b. Usage: walk_redeploy.sh "<why>"
cd /home/mandrake/rm/bench || exit 1
REF=origin/main
G="/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/FlowWorks"
P=$(tasklist.exe /FI "IMAGENAME eq RimWorldWin64.exe" | awk '/RimWorld/{print $2}')
[ -n "$P" ] && taskkill.exe /PID $P >/dev/null 2>&1
for i in $(seq 1 30); do tasklist.exe /FI "IMAGENAME eq RimWorldWin64.exe" | grep -q RimWorldWin64 || break; timeout 2 tail -f /dev/null; done
./game --why "$1" down 2>&1 | tail -1
FILES="Assemblies/RimMandrakeFlowWorks.dll Assemblies/RimMandrakeFlowWorks.dll.srchash"
for p in $(git diff --name-only HEAD $REF -- src/RimMandrake/FlowWorks | grep -v '\.py$\|\.md$\|/northstar/\|/Source/' | sed 's#src/RimMandrake/FlowWorks/##'); do
  case " $FILES " in *" $p "*) ;; *) FILES="$FILES $p";; esac
done
for p in $FILES; do
  if git cat-file -e $REF:src/RimMandrake/FlowWorks/$p 2>/dev/null; then mkdir -p "$(dirname "$G/$p")"; git show $REF:src/RimMandrake/FlowWorks/$p > "$G/$p" && echo "deployed $p"; fi
done
echo "md5 repo(origin) $(git show $REF:src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll | md5sum | cut -c1-12) game $(md5sum "$G/Assemblies/RimMandrakeFlowWorks.dll" | cut -c1-12)"
timeout 8 tail -f /dev/null
for t in 1 2 3; do powershell.exe Start-Process 'steam://rungameid/294100'; for i in $(seq 1 15); do tasklist.exe /FI "IMAGENAME eq RimWorldWin64.exe" | grep -q RimWorld && break 2; timeout 3 tail -f /dev/null; done; done
./game --why "relaunch: $1" loading 2>&1 | tail -1
for i in $(seq 1 40); do ./game 2>&1 | head -1 | grep -q 'bridge answers' && break; timeout 6 tail -f /dev/null; done
./game --why "main menu: $1" up 2>&1 | tail -1
f=Transient/pile_2026-10-22/walk_c7_probe.py
timeout 120 python.exe $f 'call:rimworld/load_game:{"saveName":"RM_fw_walkthrough_20261022b"}' 2>&1 | tr -d '\r' | cut -c1-60
for i in $(seq 1 30); do timeout 6 tail -f /dev/null; r=$(timeout 60 python.exe $f 'call:jawa/time_clock:{}' 2>&1 | tr -d '\r'); echo "$r" | grep -q '"programState": "Playing"' && break; done
echo "$r" | grep -o '"ticksGame": [0-9]*\|"programState": "[A-Za-z]*"'
python3 -c "
L=open('/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log',errors='replace').read().splitlines()
bad=[l for l in L if 'Exception' in l or 'rror' in l]
print('Player.log', len(L), 'lines; error/exception lines:', len(bad)); [print('  ', b[:200]) for b in bad[:8]]"
# re-check stop 6 (ponds unpoked) and overflow OFF, frame stop 1, re-save b in place (raw save: b IS the loaded slot)
timeout 200 python.exe $f water "call:jawa/mod_settings_field:{\"typeName\":\"RimMandrake.FlowWorks.Sheet.RM_SheetSettings\",\"action\":\"get\",\"field\":\"sheetOverflowEnabled\"}" 2>&1 | tr -d '\r' | grep -o '^HIGH.*\|^LOW.*\|"value": "[^"]*"'
timeout 120 python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --goto C3 2>&1 | tr -d '\r' | tail -1
timeout 100 python.exe $f 'call:rimworld/pause_game:{"pause":true}' 'call:jawa/clear_ui:{"all":true}' 'call:rimworld/save_game:{"saveName":"RM_fw_walkthrough_20261022b"}' 2>&1 | tr -d '\r' | cut -c1-60 | tail -1
timeout 15 tail -f /dev/null
SV="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves"
ls -la --time-style=+%H:%M:%S "$SV" | grep walkthrough
echo "original md5 $(md5sum "$SV/RM_fw_walkthrough_20261022.rws" | cut -c1-12) (want ea795bfb21c2)"
