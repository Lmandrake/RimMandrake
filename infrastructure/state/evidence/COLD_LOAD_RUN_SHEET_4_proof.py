#!/usr/bin/env python3
"""Proof for COLD_LOAD_RUN_SHEET_4: the run sheet owes no reading of its own any more.

Every entry of the 2026-09-06 and 2026-09-21 sheets is either closed on its own item or carried
by a named live successor item; 2b (JawaBench init) is answered by the lazy-init trap recorded in
skills; and entry 4's owed resolved-value readback is read from the live-captured def dump
(RimDefDump writes the runtime DefDatabase after patches): edge power 36, bolt damageAmountBase 24.
Every clause is checked and printed; exit 1 if any fails.
"""
import json
import os
import sqlite3
import subprocess
import sys

CLOSED = [  # entry -> item that must be done/dropped/superseded
    "FLUID_CANAL_DEBUG_SURFACE_1", "DEV_LOG_AUTOOPEN_SUPPRESS_1", "BEHEMOTH_TEXTURE_MISSING_LIVE_1",
    "NINEFOLD_DEBUG_GAME_READY_CRASH_1", "ARMOURY_SWMODS_MODNAME_GAP_1",
    "ARMOURY_ABSORBED_KOTORCORE_DUPES_1", "PYRELANDS_DEFNAME_RENAME_1",
    "OUR_MODS_DEPLOYED_NEVER_ACTIVATED_1", "FOUNDERS_IMPORTER_OWED_1",
    "BRIDGE_SELECT_NONCOLONIST_PAWN_1", "WORLD_LABEL_SIZE_HIERARCHY_1",
    "GELATINOUSSLIME_FIRST_LOAD_ERRORS_1", "PATCH_FILES_UNDER_DEFS_INERT_1",
]
CARRIED = [  # still-owed readings that live on their own item (must exist; any state)
    "TITANOSLIME_SLIME_BIOME_1",            # 09-21 entry 3: in-game art walk
    "ARMOURY_PROJECTILE_DAMAGE_TOOL_1",     # 09-06 entry 4: live bridge tool for ranged damage
]
DONE_STATES = {"done", "dropped", "superseded"}
DUMP = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/"
        "DefDump/defs.sqlite")

fails = []
def need(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)

def state(item):
    r = subprocess.run([sys.executable, "src/RimMandrake/rimflow/cli.py", "show", item],
                       capture_output=True, text=True, timeout=120)
    first = (r.stdout.splitlines() or [""])[0].split()
    return first[1] if len(first) > 1 and first[0] == item else None

for it in CLOSED:
    s = state(it)
    need(s in DONE_STATES, f"{it} closed (state={s})")
for it in CARRIED:
    s = state(it)
    need(s is not None and os.path.exists(f"infrastructure/state/items/{it}.md"),
         f"{it} carries its reading as a live item (state={s})")

lazy = any("lazy" in open(p, encoding="utf-8").read().lower()
           and "jawabench" in open(p, encoding="utf-8").read().lower()
           for p in ("skills/rimbridge/references/traps.md", "skills/rimworld-load-round/SKILL.md"))
need(lazy, "2b answered: JawaBench init line is lazy (recorded in skills)")

try:
    c = sqlite3.connect(f"file:{DUMP}?mode=ro", uri=True)
    def fields(name):
        r = c.execute("select json from defs where def_name=?", (name,)).fetchone()
        return json.loads(r[0])["fields"] if r else {}
    edge = [t.get("power") for t in fields("guy762_vsword_echani").get("tools") or []
            if t.get("label") == "edge"]
    need(edge == [36], f"guy762_vsword_echani resolved edge power 36 (got {edge})")
    dmg = (fields("RSW_Low_Red_Blaster_Bolt").get("projectile") or {}).get("damageAmountBase")
    need(dmg == 24, f"RSW_Low_Red_Blaster_Bolt resolved damageAmountBase 24 (got {dmg})")
    cap = dict(c.execute("select key,value from provenance")).get("captured_utc")
    print(f"     dump captured {cap}")
except sqlite3.Error as e:
    need(False, f"def dump readable ({e})")

print("VERDICT", "FAIL" if fails else "PASS", f"({len(fails)} failed)")
sys.exit(1 if fails else 0)
