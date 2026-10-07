#!/bin/bash
# build, selftest, kill game, deploy, relaunch, rebuild visuals, screenshot stone+dirt D3 as $1
cd /home/mandrake/rm/bench; D=Transient/scorch_concept_2026-10-06; S="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Screenshots"
python3 src/RimMandrake/Utils/winbuild.py FlowWorks 2>&1 | tail -1
timeout 500 python3 src/RimMandrake/Utils/selftest_flowworks_stock.py 2>&1 | tail -1
taskkill.exe /IM RimWorldWin64.exe /F 2>&1 | tr -d '\r'; sleep 5
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks --apply 2>&1 | tail -1
powershell.exe -NoProfile -Command "Start-Process 'steam://rungameid/294100'"; sleep 15
for i in $(seq 1 55); do python.exe src/RimMandrake/Utils/rimbridge_client.py --call rimworld/get_ui_state 2>&1 | tr -d '\r' | grep -q '"programState": "Entry"' && break; sleep 10; done
timeout 400 python.exe src/RimMandrake/FlowWorks/review_map.py --build --fresh-map --only visuals 2>&1 | tr -d '\r' | tail -1
python.exe $D/shoot.py ${1}_stone_D3 29 57 5 ${1}_dirt_D3 29 50 5 ${1}_overview 25 53 11 2>&1 | tr -d '\r' | tail -1
python3 - "$1" <<'PY'
import sys
from PIL import Image
n=sys.argv[1]; D='Transient/scorch_concept_2026-10-06/'; S='/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Screenshots/'
for k in ('stone','dirt'):
    im=Image.open(S+f'{n}_{k}_D3.png').convert('RGB'); W,H=im.size; cx,cy=W//2,H//2
    im.crop((cx-512,cy-400,cx+512,cy+400)).save(D+f'{n}_{k}_D3_crop.png')
Image.open(S+f'{n}_overview.png').convert('RGB').save(D+f'{n}_overview.png')
PY
