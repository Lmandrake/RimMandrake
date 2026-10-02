"""saved_base -- a SAVED bland world, loaded between suites instead of cleaned.

Owner 2026-10-01: suites run back to back on one dirty world (corpses, blood, 21 colonists, 'Forced weather'
alert spam, leftover hediffs) and the colony-naming dialogs re-raise every 1000 ticks (Faction.FactionTick,
TicksGame % 1000 == 200) until named. So: build the bland world ONCE (j6_bland_base.py), name the colony,
assert_bland, save it as BLAND_NORTHSTAR_BASE, and `world_reset()` = LOAD that save.

  induce_and_finish_naming(s)  name faction+settlement directly (jawa/name_colony == what the dialogs' OK does),
                               close any naming dialog already open, prove none remains. Returns problems.
  save_base(s, saves_dir)      back up the Saves keepers, rimworld/save_game, then PROVE a NEW file appeared and
                               no existing save changed size (save_game has silently written the wrong slot).
  world_reset(s, ...)          load the save, assert_bland; falls back to cleanup() when no save is loadable.
  cleanup(s)                   fallback only: remove non-colonists, resurrect/heal colonists, unlock weather,
                               end conditions, clear the incident queue, extinguish fires, destroy corpses/filth.
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import helpers as H   # noqa: E402

SAVE_NAME = "BLAND_NORTHSTAR_BASE"
WIN_SAVES = "C:\\Users\\Mandrake\\AppData\\LocalLow\\Ludeon Studios\\RimWorld by Ludeon Studios\\Saves"
WSL_SAVES = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves"


def default_saves_dir():
    return WIN_SAVES if os.name == "nt" else WSL_SAVES


def _window_types(s):
    r = s.call("jawa/window_list_close", action="list")
    out = []
    for w in r.get("windows") or []:
        out.append(w if isinstance(w, str) else str(w.get("typeName") or w.get("type") or w))
    return out, r


def induce_and_finish_naming(s, faction_name=None, settlement_name=None):
    """Name the colony now so the dialogs never appear. Returns a list of problems (empty == done)."""
    problems = []
    r = s.call("jawa/name_colony", factionName=faction_name, settlementName=settlement_name)
    if not r.get("success"):
        problems.append("jawa/name_colony failed: %s" % r.get("message"))
    elif not r.get("settlements"):
        problems.append("name_colony named the faction but found no player settlement")
    s.call("jawa/window_list_close", action="close", typeName="Dialog_NamePlayer", closeAll=True)
    left = [t for t in _window_types(s)[0] if "NamePlayer" in t]
    if left:
        problems.append("naming dialog still open: %s" % left)
    return problems


def snapshot_saves(saves_dir):
    try:
        return {n: os.path.getsize(os.path.join(saves_dir, n)) for n in os.listdir(saves_dir) if n.endswith(".rws")}
    except OSError:
        return {}


def save_base(s, saves_dir=None, name=SAVE_NAME, overwrite=False, wait=2.0):
    """Returns {"verified": bool, "problems": [...], ...}. Never trusts the path save_game hands back."""
    saves_dir = saves_dir or default_saves_dir()
    before = snapshot_saves(saves_dir)
    problems = []
    if name + ".rws" in before and not overwrite:
        return {"verified": False, "problems": ["%s.rws already exists; pass overwrite=True" % name], "path": None}
    if before:
        bk = os.path.join(os.path.dirname(saves_dir.rstrip("/\\")), "Saves_backup_northstar_%s" % time.strftime("%Y%m%d%H%M%S"))
        os.makedirs(bk, exist_ok=True)
        for n in before:
            shutil.copy2(os.path.join(saves_dir, n), os.path.join(bk, n))
    r = s.call("rimworld/save_game", saveName=name)
    if not r.get("success"):
        problems.append("save_game failed: %s" % r.get("message"))
    time.sleep(wait)
    after = snapshot_saves(saves_dir)
    if name + ".rws" not in after:
        problems.append("no %s.rws appeared" % name)
    elif after[name + ".rws"] < 1000:
        problems.append("%s.rws is only %d bytes" % (name, after[name + ".rws"]))
    changed = [n for n in before if n != name + ".rws" and after.get(n) != before[n]]
    if changed:
        problems.append("existing saves changed or vanished: %s" % changed)
    return {"verified": not problems, "problems": problems, "path": os.path.join(saves_dir, name + ".rws"),
            "sizeBytes": after.get(name + ".rws", 0)}


def cleanup(s, keep_colonists=3):
    """Fallback cleanup. Each step is best-effort and reported; only assert_bland afterwards is a verdict."""
    steps = {}
    steps["incident_queue_clear"] = bool(s.call("jawa/incident_queue_clear").get("success"))
    steps["weather_unlock"] = bool(s.call("jawa/weather_set", unlock=True).get("success"))
    wg = s.call("jawa/weather_get")
    ended = 0
    for c in wg.get("conditions") or []:
        name = c if isinstance(c, str) else (c.get("def") or c.get("defName"))
        if name and s.call("jawa/game_condition", action="end", condition=name).get("success"):
            ended += 1
    steps["conditions_ended"] = ended
    steps["fires_extinguished"] = s.call("jawa/map_fire", action="extinguish",
                                         rect="0,0,%d,%d" % (250, 250)).get("firesExtinguished")
    steps["non_colonists_destroyed"] = s.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False).get("matchedCount")
    # UNVERIFIED live: category names for corpses/filth in destroy_batch (J3 proved only "Building,Item")
    info = s.call("jawa/map_info")
    n = int(info.get("sizeX", 250))
    steps["corpses_filth"] = bool(s.call("jawa/destroy_batch", rects="0,0,%d,%d" % (n, int(info.get("sizeZ", n))),
                                         categories="Corpse,Filth").get("success"))
    rows = H.read_pawns(s)
    revived = 0
    for r in rows:
        if H.is_colonist(r) and r["dead"]:
            s.call("jawa/pawn_resurrect", pawn=r["id"], restoreMissingParts=True, removeDiedThoughts=True)
            revived += 1
    steps["colonists_resurrected"] = revived
    healed = 0
    for r in H.read_pawns(s):
        if H.is_colonist(r) and not r["dead"]:
            for h in r["health"]["hediffs"]:
                if h["def"] in H.INJURY_DEFS:
                    s.call("jawa/pawn_health", pawn=r["id"], action="remove", hediff=h["def"])
                    healed += 1
    steps["hediffs_removed"] = healed
    cols = [r for r in H.read_pawns(s, health=False) if H.is_colonist(r) and not r["dead"]]
    steps["extra_colonists"] = max(0, len(cols) - keep_colonists)   # no verified per-pawn removal tool: reported, not hidden
    return steps


def world_reset(s, save_name=SAVE_NAME, saves_dir=None, fallback=True, keep_colonists=3, load_retries=2):
    """Between suites. Returns {"method": "load"|"cleanup", "problems": [...], "steps": {...}}; empty problems == bland."""
    out = {"method": None, "problems": [], "steps": {}}
    saves_dir = saves_dir or default_saves_dir()
    have_save = (save_name + ".rws") in snapshot_saves(saves_dir) or not os.path.isdir(saves_dir)
    loaded = False
    if have_save:
        for _ in range(load_retries):
            r = s.call("rimworld/load_game_ready", saveName=save_name)
            if r.get("success"):
                loaded = True
                break
            out["steps"]["load_error"] = r.get("message")
    if loaded:
        out["method"] = "load"
    elif fallback:
        out["method"] = "cleanup"
        out["steps"].update(cleanup(s, keep_colonists))
    else:
        out["problems"].append("save %s not loadable and fallback disabled" % save_name)
        return out
    out["problems"] += H.assert_bland(s)
    ncol = len([r for r in H.read_pawns(s, health=False) if H.is_colonist(r) and not r["dead"]])
    if ncol > keep_colonists:
        out["problems"].append("%d living colonists, expected at most %d" % (ncol, keep_colonists))
    out["problems"] += [t for t in ["naming dialog open: %s" % w for w in _window_types(s)[0] if "NamePlayer" in w]]
    return out
