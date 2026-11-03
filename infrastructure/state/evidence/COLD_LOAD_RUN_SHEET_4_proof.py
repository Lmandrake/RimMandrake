#!/usr/bin/env python3
"""Proof for COLD_LOAD_RUN_SHEET_4: the run sheet owes no reading of its own any more.

Every entry of the 2026-09-06 and 2026-09-21 sheets is either closed on its own item or carried
by a named live successor item. Three entries are read here, not trusted to an item's state:
  * entry 3 (Behemoth fPack): the engine builds the pack overlay as Graphic_Multi at
    <lifestage body/female texPath> + "Pack" (the path the 2026-09-05 error line itself named), and
    Graphic_Multi errors only when no _north/_east/_south/_west texture exists there. Every runtime
    RSW_Behemoth texPath (def dump) + "Pack" must resolve to _north/_east/_south PNGs in the
    Textures of an ACTIVE deployed mod.
  * entry 2b (does the log auto-open suppressor install in plain play): NO. Its only installer is
    JawaBenchInit.Announce, a [ModuleInitializer] that runs on the first jawa/ tool call (measured
    lazy, JAWABENCH_INIT_LINE_IS_LAZY_1), and no type in the companion runs at startup. That gap
    is carried by LOG_AUTOOPEN_FIX_WAITS_FOR_FIRST_HELLO.
  * entry 4: resolved values read from the live-captured def dump (RimDefDump writes the runtime
    DefDatabase after patches): edge power 36, bolt damageAmountBase 24.
Every clause is checked and printed; exit 1 if any fails.
"""
import glob
import json
import os
import re
import xml.etree.ElementTree as ET
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
    "LOG_AUTOOPEN_FIX_WAITS_FOR_FIRST_HELLO",  # 09-06 entry 2b: suppressor absent in plain play
]
DONE_STATES = {"done", "dropped", "superseded"}
MODS = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"
MODSCONFIG = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/"
              "Config/ModsConfig.xml")
JB = "src/RimMandrake/bridgetools/JawaBench.BridgeTools"
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
    if r.returncode:
        print(f"     rimflow show {item} exit {r.returncode}: {r.stderr.strip()[-300:]}")
    first = (r.stdout.splitlines() or [""])[0].split()
    return first[1] if len(first) > 1 and first[0] == item else None

for it in CLOSED:
    s = state(it)
    need(s in DONE_STATES, f"{it} closed (state={s})")
for it in CARRIED:
    s = state(it)
    need(s is not None and s not in DONE_STATES, f"{it} carries its reading as an open item (state={s})")

# 2b: read the companion's source for every caller of the suppressor's installer and every way
# code in the assembly could run at startup without a bridge call.
src = {p: open(p, encoding="utf-8").read() for p in glob.glob(f"{JB}/**/*.cs", recursive=True) if "/obj/" not in p and "/bin/" not in p}
callers = sorted(os.path.basename(p) for p, t in src.items()
                 if re.search(r"JawaBenchLogAutoOpenSuppress\.Install\(\)", t))
need(callers == ["JawaBenchInit.cs"], f"2b: suppressor's only installer is JawaBenchInit.cs (got {callers})")
init = src.get(f"{JB}/JawaBenchInit.cs", "")
need("[System.Runtime.CompilerServices.ModuleInitializer]" in init,
     "2b: JawaBenchInit.Announce is a module initializer (fires on the first jawa/ call)")
startup = sorted({os.path.basename(p) for p, t in src.items() for m in re.finditer(
    r"^\s*\[(?:Verse\.)?StaticConstructorOnStartup\b|\bclass\s+\w+\s*:\s*(?:Verse\.)?(?:Mod|GameComponent|"
    r"MapComponent|WorldComponent|ModSettings|\w*Def)\b", re.sub(r"//.*", "", t), re.M)})
need(not startup, f"2b: no type in the companion runs at startup (found {startup})")
print("     2b ANSWER: plain play does NOT install the log auto-open suppressor "
      "(carried: LOG_AUTOOPEN_FIX_WAITS_FOR_FIRST_HELLO)")

def active_mod_dirs():
    try:
        active = {li.text.strip().lower() for li in ET.parse(MODSCONFIG).find("activeMods")}
    except (OSError, ET.ParseError) as e:
        need(False, f"ModsConfig.xml readable ({e})")
        return []
    out = []
    for about in glob.glob(f"{MODS}/*/About/About.xml"):
        try:
            pid = (ET.parse(about).getroot().findtext("packageId") or "").strip().lower()
        except ET.ParseError:
            continue
        if pid in active:
            out.append(os.path.dirname(os.path.dirname(about)))
    return out

try:
    c = sqlite3.connect(f"file:{DUMP}?mode=ro", uri=True)
    def fields(name, typ="ThingDef"):
        r = c.execute("select json from defs where def_name=? and def_type=?", (name, typ)).fetchone()
        return json.loads(r[0])["fields"] if r else {}
    edge = [t.get("power") for t in fields("guy762_vsword_echani").get("tools") or []
            if t.get("label") == "edge"]
    need(edge == [36], f"guy762_vsword_echani resolved edge power 36 (got {edge})")
    dmg = (fields("RSW_Low_Red_Blaster_Bolt").get("projectile") or {}).get("damageAmountBase")
    need(dmg == 24, f"RSW_Low_Red_Blaster_Bolt resolved damageAmountBase 24 (got {dmg})")
    # entry 3: the pack overlay path the engine builds, for every Behemoth graphic, in an active mod
    paths = set()
    for ls in fields("RSW_Behemoth", "PawnKindDef").get("lifeStages") or []:
        for k in ("bodyGraphicData", "femaleGraphicData"):
            tp = (ls.get(k) or {}).get("texPath")
            if tp:
                paths.add(tp + "Pack")
    need(len(paths) >= 2, f"RSW_Behemoth runtime pack paths read from the dump ({sorted(paths)})")
    pack = (fields("RSW_Behemoth").get("race") or {}).get("packAnimal")
    need(pack is True, f"RSW_Behemoth race is a pack animal at runtime (packAnimal={pack})")
    dirs = active_mod_dirs()
    need(len(dirs) > 10, f"active deployed mod folders found ({len(dirs)})")
    for pp in sorted(paths):
        hits = [d for d in dirs for tex in ("Textures", "1.6/Textures")
                if all(os.path.isfile(f"{d}/{tex}/{pp}_{f}.png") for f in ("north", "east", "south"))]
        need(bool(hits), f"entry 3: {pp}_north/_east/_south in an active mod "
                         f"({[os.path.basename(h) for h in hits]})")
    cap = dict(c.execute("select key,value from provenance")).get("captured_utc")
    print(f"     dump captured {cap}")
except sqlite3.Error as e:
    need(False, f"def dump readable ({e})")

print("VERDICT", "FAIL" if fails else "PASS", f"({len(fails)} failed)")
sys.exit(1 if fails else 0)
