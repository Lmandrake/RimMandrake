#!/bin/bash
# lane E game cycle: kill game by PID, rebuild+deploy MessyConduit, tier swap, launch via Steam, poll bridge
cd /home/mandrake/rm/foundry
TIER=${1:-messyconduit}
PID=$(tasklist.exe 2>/dev/null | tr -d '\r' | awk '/RimWorldWin64.exe/{print $2}' | head -1)
if [ -n "$PID" ]; then echo "killing PID $PID"; taskkill.exe /PID $PID /F | tr -d '\r'; fi
for i in $(seq 1 30); do tasklist.exe 2>/dev/null | grep -q RimWorldWin64 || break; sleep 2; done
if [ "$TIER" = "messyconduit" ]; then
  timeout 900 flock /tmp/claude-1000/mc_build.lock -c 'python3 src/RimMandrake/Utils/winbuild.py MessyConduit 2>&1 | tail -3; python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod MessyConduit --apply 2>&1 | tail -4'
fi
for i in $(seq 1 40); do
  out=$(python3 src/RimMandrake/Utils/modset_builder.py --tier $TIER --apply 2>&1); echo "$out" | tail -2
  echo "$out" | grep -q 'REFUSING TO WRITE' || break; sleep 20
done
powershell.exe -NoProfile -Command "Start-Process -FilePath 'C:\Program Files (x86)\Steam\steam.exe' -ArgumentList '-applaunch','294100'" 
t0=$(date +%s)
while [ $(( $(date +%s) - t0 )) -lt 1500 ]; do
  r=$(timeout 40 python.exe Transient/mc_lane_e_uiprobe.py 2>/dev/null | tr -d '\r')
  case "$r" in UP*) echo "bridge up after $(( $(date +%s) - t0 ))s: $r"; exit 0;; esac
  sleep 15
done
echo "TIMEOUT waiting for bridge"; exit 1
