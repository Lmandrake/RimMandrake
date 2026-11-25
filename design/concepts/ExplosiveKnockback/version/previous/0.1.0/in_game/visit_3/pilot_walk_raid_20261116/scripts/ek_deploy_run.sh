#!/usr/bin/env bash
# ek_deploy_run.sh DLL OUTNAME PAIRS SAVE : cold restart Steve's game with DLL, load SAVE, run --frames-only PAIRS
# The 2026-11-16 pilot stopped the game with taskkill /IM, which also kills a second game (game B); rw_game.sh down stops this game's pid only.
DLL=$1; OUT=$2; PAIRS=$3; SAVE=${4:-EK_WALK_SMALL_COLONY_20261116}
T=/mnt/d/SteamLibrary/steamapps/common/RimWorld/Mods/ExplosiveKnockback/Assemblies
timeout 300 ssh -o BatchMode=yes mandrake@stevedesktop-wsl "cd ~/rm/runner && infrastructure/stevedesktop/rw_game.sh down >/dev/null 2>&1"
scp -q "$DLL" mandrake@stevedesktop-wsl:$T/RimMandrakeExplosiveKnockback.dll
timeout 900 ssh -o BatchMode=yes mandrake@stevedesktop-wsl "cd ~/rm/runner && export RM_HOST_GUARD_GEN=2026; echo dll \$(md5sum $T/RimMandrakeExplosiveKnockback.dll | cut -c1-8); infrastructure/stevedesktop/rw_game.sh up --wait 2>&1 | tail -1"
RB_TIMEOUT=200 /tmp/ek_rb.sh rimworld/load_game "{\"saveName\":\"$SAVE\"}" | grep -o '"success": *[a-z]*' | head -1
for i in $(seq 1 60); do r=$(/tmp/ek_rb.sh jawa/time_clock '{}' 2>/dev/null | grep -o '"ticksGame": *[0-9]*' | grep -o '[0-9]*$'); [ -n "$r" ] && [ "$r" -gt 0 ] && break; sleep 5; done
echo "clock $r pawns $(/tmp/ek_rb.sh jawa/list_pawns '{"rect":"95,34,11,11"}' | grep -c '"def"')"
timeout 2400 ssh -o BatchMode=yes mandrake@stevedesktop-wsl "cd ~/rm/runner && export RM_HOST_GUARD_GEN=2026 && python.exe src/RimMandrake/ExplosiveKnockback/validation.py --live walk_storeroom_raid --storeroom 97,37,7,7 --cover 102,36 --gas 100,41 --frames-only --frame-pairs $PAIRS --out 'D:\\RimTest\\data\\scratch\\$OUT.json'" 2>&1 | grep "FRAME_BUDGET\|W_PRE\|REFUSED" | cut -c1-420
UD="/mnt/c/Users/sjlewis/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios"
mkdir -p /tmp/ek_$OUT; rm -f /tmp/ek_$OUT/*
timeout 60 ssh -o BatchMode=yes mandrake@stevedesktop-wsl "cd '$UD' && tar cf - \$(ls -t RM_FrameProbe_*.csv | head -$((PAIRS*2)))" | tar xf - -C /tmp/ek_$OUT
scp -q mandrake@stevedesktop-wsl:/mnt/d/RimTest/data/scratch/$OUT.json /tmp/ek_$OUT/
