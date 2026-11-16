#!/usr/bin/env python3
"""Write the visit's env_<tag>.json: activeMods parsed from the live ModsConfig.xml, in order, and the game build from
Player.log's first lines. WSL python3:  python3 .../visit_3/scripts/env.py <tag> <source sha> <dll note>"""
import json, os, re, sys, xml.etree.ElementTree as ET
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7, "src", "RimMandrake", "Utils"))
from game_paths import MODS_CONFIG, PLAYER_LOG  # noqa: E402
mods = [li.text.strip().lower() for li in ET.parse(MODS_CONFIG).find("activeMods")]
head = open(PLAYER_LOG, encoding="utf-8", errors="replace").read(20000)
m = re.search(r"RimWorld (\d+\.\d+\.\d+ rev\d+)", head)
out = {"tag": sys.argv[1], "game": "archmagi", "game_build": m.group(1) if m else "UNMEASURED", "active_mods_count": len(mods),
       "activeMods": mods, "source_sha": sys.argv[2], "dll_build": sys.argv[3]}
p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "env_%s.json" % sys.argv[1])
json.dump(out, open(p, "w"), indent=1)
print(p, out["game_build"], len(mods))
