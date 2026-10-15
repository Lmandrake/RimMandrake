#!/usr/bin/env python3
"""modcheck.test_site_saves -- clean saved test maps (TESTSITE_SAVES_BUILD_ONE_CALM_MAP; owner by card 2026-10-15:
"Clean saved maps" -- one cleared, calm map per suite, saved once; every run loads it instead of generating a fresh map).

Why: live rounds 5-8 spent ~6 h and met ~9 test-environment hazards (heat, fogged mechs and shrine pawns, storm fires,
spiders/hives, stray drones, a river ending at the sea, ferry banks) and ~0 mod defects. Every one came with the fresh
map. A save is cleaned ONCE, read back, and then the same clean map comes back on every load.

    python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py list
    python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py build calm            # fresh quicktest -> clean -> save
    python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py build river           # + river_site.py, home map dropped
    python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py build pyrelands --fingerprint 417df172fdb5 --from-tag r6
    python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py load calm             # load + read-back check
    python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py check calm            # read-back on the current map

The suites call load_site() themselves by default (proof_all.py, validation_v2.py, extension_proof.py --site river);
each keeps a --fresh-map flag for the old path. Pyrelands keeps its own fixture loader (northstar_site.py
--reload-only --tag calm), which this module's `build pyrelands` feeds.

Two clean profiles:
  calm    every map-gen danger AND every unowned artificial building (ruins), for suites whose subject is not the
          map's own content (GSS, FlowWorks).
  danger  only the dangers (ancient-danger containers with their contents, triggers, hostiles, hives, explosives), for
          a biome suite whose subject IS the map (Pyrelands reads its ruins and its wildlife census).
Both: every fog/proximity trigger + signal action disarmed, the whole map unfogged with the re-sweep
(testenv_guards.clear_map_fog), the map-only quiet profile, Clear weather, no fire, queue cleared.
The ancient-danger CONTAINERS go by Vanish (Building_Casket.Destroy(Vanish) -> innerContainer.ClearAndDestroyContents:
the sleepers in a casket are destroyed with it, never dropped) BEFORE the unfog (owner 2026-10-15: "The pawns that emerge
from an ancient danger (hidden site on the map) may not be there before you open it, not sure.").

`call` is anything shaped call(tool, **params) -> dict (a bridge client's .call, rimdrive Session.call, a fake).
"""
import json
import os
import re
import shutil
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
for _p in (_HERE, _UTILS):
    if _p not in sys.path:
        sys.path.append(_p)

import testenv_guards as TG  # noqa: E402

REGISTRY = os.path.join(_HERE, "test_site_saves.json")

SITES = {
    "calm": {"save": "RM_TestSite_calm_v1", "profile": "calm", "size": 250, "temp": (5.0, 30.0), "minColonists": 3,
             "suites": ["GimmeSomeSlack/northstar/proof_all.py --live", "FlowWorks/northstar/validation_v2.py --live"]},
    "river": {"save": "RM_TestSite_river_v1", "profile": "calm", "size": 250, "temp": (5.0, 30.0), "minColonists": 3,
              "minRiverEdges": 2, "suites": ["FlowWorks/northstar/extension_proof.py --live --site river"]},
    "pyrelands": {"save": None, "profile": "danger", "size": 250, "temp": None, "minColonists": 3, "tag": "calm",
                  "suites": ["Pyrelands/northstar_site.py --reload-only --tag calm, then northstar_driver run"]},
}

# Ancient-danger containers and map-gen threats (r8 spawner probe, 4 maps: every released group sat in a shrine with
# AncientCryptosleepCasket + AncientHermeticCrate + Sarcophagus within 3 cells; hives/egg sacs/glow pods on r5-r8 maps).
DANGER_RE = re.compile(r"(Cryptosleep|Casket|HermeticCrate|Sarcophag|^Hive$|^BI_Hive|EggSac|GlowPod|"
                       r"Turret|MechDrop|MechCluster|Spawner|Warhead|Mortar|Shell_|Pulser|Monolith$)", re.I)
# Explosive and pulser ITEMS that a fire or a curious colonist sets off (r8: Shell_AntigrainWarhead in two shrines).
DANGER_ITEM_DEFS = ("Shell_AntigrainWarhead", "Shell_HighExplosive", "Shell_Incendiary", "Shell_EMP", "Shell_Firefoam",
                    "Shell_Smoke", "Shell_ChemFuel", "Shell_Toxic", "PsychicAnimalPulser", "ShardAnimalPulser",
                    "PsychicSoothePulser", "PsychicInsanityLance", "PsychicShockLance")
# Kept on purpose (L1 2026-10-15, 3 of 6 quicktest rolls): Anomaly's Fallen monolith (VoidMonolith) is placed on every
# new colony map, has hitPoints -1 (destroy_batch cannot remove it) and stays inert until a colonist is ordered to study
# or activate it. It matched `Monolith$` and failed every clean, so it is exempt from the danger and ruin passes.
INERT_FIXTURES = ("VoidMonolith",)
LIST_LIMIT = 5000
POLL_S = 1.0


def _ok(r):
    return isinstance(r, dict) and r.get("success") is not False


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def is_danger_def(d):
    return bool(d) and (bool(DANGER_RE.search(d)) or d in DANGER_ITEM_DEFS)


def _things(call, **kw):
    """-> (rows, error). A truncated listing is an error: it must never read as 'all gone'."""
    r = call("jawa/list_things", limit=LIST_LIMIT, **kw)
    if not _ok(r) or not isinstance(r.get("things"), list):
        return [], "list_things %s failed: %s" % (kw, str(r)[:200])
    if r.get("isCompleteList") is False or (r.get("countMatched") or 0) > len(r["things"]):
        return [], "list_things %s truncated (%s matched)" % (kw, r.get("countMatched"))
    return [t for t in r["things"] if t.get("x") is not None and t.get("z") is not None], None


def _unowned(t):
    return (t.get("factionName") or t.get("faction")) in (None, "", "None")


def _player(t):
    """list_things: `faction` is the FactionDef defName (PlayerColony/PlayerTribe...), `factionName` the colony's own
    name ("New Arrivals"), so only `faction` can say player."""
    return str(t.get("faction") or "").startswith("Player") or t.get("isPlayer") is True


def danger_things(call):
    """Map-gen danger things on the current map: buildings by DANGER_RE (never the player's), items by DANGER_ITEM_DEFS.
    -> (rows, error)."""
    b, e1 = _things(call, group="BuildingArtificial")
    i, e2 = _things(call, defName=",".join(DANGER_ITEM_DEFS))
    rows = [t for t in b if is_danger_def(t.get("def")) and not _player(t) and t.get("def") not in INERT_FIXTURES] + i
    return rows, e1 or e2


def ruin_things(call, natural=("SteamGeyser", "VHGE_GasGeyser") + INERT_FIXTURES):
    """Unowned artificial buildings (ruins, walls, columns, shrine decor), natural scenery excluded. -> (rows, error)."""
    b, err = _things(call, group="BuildingArtificial")
    return [t for t in b if _unowned(t) and t.get("def") not in natural], err


def _vanish_cells(call, rows, categories, passes, relist):
    total, left = 0, rows
    for _ in range(passes):
        if not left:
            break
        rects = ";".join("%d,%d,1,1" % (t["x"], t["z"]) for t in left)
        r = call("jawa/destroy_batch", rects=rects, categories=categories)
        if _ok(r):
            total += len(left)
        left, err = relist()
        if err:
            return left, total, err
    return left, total, None


class call_session(object):
    """Adapter: a bare call(tool, **kw) as an object with .call (what testenv_guards / quiet_site take)."""

    def __init__(self, call):
        self.call = call


def clean_map(call, profile, quiet=True):
    """The one cleaning pass. Order matters: triggers first (nothing may fire), then the danger containers by Vanish
    (contents destroyed, never dropped), then every non-colonist pawn, then (calm) the ruins, then the WHOLE-map unfog
    with its re-sweep (no fogged pocket survives into the save, so no later wall removal can flood, letter or wake),
    then a second danger/trigger pass and the map-only quiet profile, then the sky. -> receipt dict; receipt['problems']
    is empty only when every step read back clean."""
    if profile not in ("calm", "danger"):
        raise ValueError("profile must be calm or danger")
    S = call_session(call)
    rec = {"profile": profile, "utc": _now(), "problems": []}
    rec["triggers"] = TG.disarm_fog_triggers(S)
    if rec["triggers"].get("verified") is not True:
        rec["problems"].append("fog triggers not disarmed: %s" % (rec["triggers"].get("error") or rec["triggers"].get("left")))
    d0, err = danger_things(call)
    rec["dangerFound"] = sorted({t.get("def") for t in d0})
    left, n, err2 = _vanish_cells(call, d0, "Building,Item", 4, lambda: danger_things(call))
    rec["dangerVanished"], rec["dangerLeft"] = n, [(t.get("def"), t.get("x"), t.get("z")) for t in left]
    if err or err2 or left:
        rec["problems"].append("danger things: %s" % (err or err2 or rec["dangerLeft"][:6]))
    db = call("jawa/destroy_bulk", filter="nonColonists", dryRun=False) or {}
    rec["nonColonistsVanished"] = db.get("matchedCount")
    if profile == "calm":
        r0, err = ruin_things(call)
        left, n, err2 = _vanish_cells(call, r0, "Building,Item", 5, lambda: ruin_things(call))
        rec["ruinsVanished"], rec["ruinsLeft"] = n, len(left)
        if err or err2 or left:
            rec["problems"].append("ruins: %s" % (err or err2 or "%d left" % len(left)))
    # L1 2026-10-15 (HARNESS): vanishing shrine walls/caskets above opens their fog pocket and releases the sleepers
    # (4 mechs listed hostile at the unfog guard, after the first sweep), so sweep non-colonists again before the unfog.
    db2 = call("jawa/destroy_bulk", filter="nonColonists", dryRun=False) or {}
    rec["nonColonistsVanishedBeforeUnfog"] = db2.get("matchedCount")
    rec["fog"] = TG.clear_map_fog(S)
    if rec["fog"].get("verified") is not True:
        rec["problems"].append("fog: %s" % rec["fog"].get("error"))
    # after the unfog: anything the fog hid is now listable; one more trigger + danger pass, then read back
    rec["triggersAfter"] = TG.disarm_fog_triggers(S)
    if rec["triggersAfter"].get("verified") is not True:
        rec["problems"].append("fog triggers after the unfog: %s" % (rec["triggersAfter"].get("error") or rec["triggersAfter"].get("left")))
    d1, err = danger_things(call)
    left, n, err2 = _vanish_cells(call, d1, "Building,Item", 3, lambda: danger_things(call))
    rec["dangerAfterUnfog"] = sorted({t.get("def") for t in d1})
    if err or err2 or left:
        rec["problems"].append("danger things after the unfog: %s" % (err or err2 or [(t.get("def")) for t in left][:6]))
    if quiet:
        import quiet_site as QS
        rec["quietMap"] = QS.site_profile_receipt(S, "test_site_saves_clean", controls=QS.MAP_ONLY + ("modal_broker",))
        if rec["quietMap"].get("error") or rec["quietMap"].get("problems"):
            rec["problems"].append("quiet map profile: %s" % (rec["quietMap"].get("error") or rec["quietMap"].get("problems")))
    mi = call("jawa/map_info") or {}
    rec["sky"] = TG.calm_sky(S, (int(mi.get("sizeX", 250)), int(mi.get("sizeZ", 250))))
    if rec["sky"].get("verified") is not True:
        rec["problems"].append("sky: %s" % rec["sky"].get("error"))
    call("jawa/incident_queue_clear")
    return rec


def _colonists(call):
    r = call("jawa/list_pawns", limit=500) or {}
    rows = r.get("pawns") or []
    return [p for p in rows if p.get("isPlayer") and p.get("intelligence", "Humanlike") == "Humanlike" and not p.get("dead")]


def check_map(call, site):
    """Read-back that the CURRENT map is still a clean `site` (after a build, and after every load). Touches nothing
    except a 1x1 unfog probe (the fog count has no read-only tool; on a clean map it changes nothing).
    -> {"verified": bool, "problems": [...], ...readings}."""
    spec = SITES[site]
    out = {"site": site, "utc": _now(), "problems": []}
    P = out["problems"]
    S = call_session(call)
    mi = call("jawa/map_info") or {}
    out["map"] = {k: mi.get(k) for k in ("tile", "mapId", "sizeX", "sizeZ", "mapBiome", "outdoorTempNow")}
    if spec.get("size") and (mi.get("sizeX"), mi.get("sizeZ")) != (spec["size"], spec["size"]):
        P.append("map is %sx%s, want %d" % (mi.get("sizeX"), mi.get("sizeZ"), spec["size"]))
    fg = call("jawa/set_fog", action="unfog", rect="0,0,1,1") or {}
    out["foggedCells"] = fg.get("foggedCellsNow")
    if fg.get("foggedCellsNow") != 0:
        P.append("fogged cells: %s" % fg.get("foggedCellsNow"))
    tr, err = TG._list_triggers(S)
    out["triggers"] = len(tr) if not err else None
    if err or tr:
        P.append("triggers: %s" % (err or [(t["def"], t["x"], t["z"]) for t in tr][:6]))
    dg, err = danger_things(call)
    out["danger"] = sorted({t.get("def") for t in dg}) if not err else None
    if err or dg:
        P.append("danger things: %s" % (err or out["danger"]))
    if spec["profile"] == "calm":
        rn, err = ruin_things(call)
        out["ruins"] = len(rn) if not err else None
        if err or rn:
            P.append("ruins: %s" % (err or "%d (%s)" % (len(rn), sorted({t.get('def') for t in rn})[:6])))
    ids, err = TG._hostile_pawns(S)
    out["hostiles"] = ids
    if err or ids:
        P.append("hostile pawns: %s" % (err or ids[:6]))
    qs = call("jawa/quiet_site", action="status") or {}
    thr = [t for t in qs.get("threats") or [] if not t.get("kept")]
    out["threatStructures"] = [(t.get("def"), t.get("id")) for t in thr] if _ok(qs) else None
    if not _ok(qs) or thr:
        P.append("threat structures: %s" % (out["threatStructures"] if _ok(qs) else str(qs)[:160]))
    fires, err = _things(call, defName="Fire")
    out["fires"] = len(fires) if not err else None
    if err or fires:
        P.append("fires: %s" % (err or len(fires)))
    w = call("jawa/weather_get") or {}
    wx = w.get("weather") or {}
    out["weather"] = {"current": wx.get("current"), "rainRate": wx.get("rainRate")}
    if (wx.get("rainRate") or 0) > 0.01:
        P.append("raining: %s" % out["weather"])
    band = spec.get("temp")
    t = mi.get("outdoorTempNow")
    if band and (not isinstance(t, (int, float)) or not band[0] <= t <= band[1]):
        P.append("outdoor %s C outside the safe band %s" % (t, band))
    cols = _colonists(call)
    out["colonists"] = [(p.get("id"), bool(p.get("downed"))) for p in cols]
    up = [p for p in cols if not p.get("downed")]
    if len(up) < spec.get("minColonists", 1):
        P.append("%d standing colonist(s), want %d" % (len(up), spec.get("minColonists", 1)))
    out["verified"] = not P
    return out


# ------------------------------------------------------------------ save / load
def saves_stat(saves_dir):
    out = {}
    for f in os.listdir(saves_dir):
        if f.endswith(".rws"):
            st = os.stat(os.path.join(saves_dir, f))
            out[f] = (st.st_size, int(st.st_mtime))
    return out


def backup_saves(saves_dir, backup_dir):
    """Project rule: back up the Saves folder before writing a save. -> number of files copied."""
    os.makedirs(backup_dir, exist_ok=True)
    n = 0
    for f in os.listdir(saves_dir):
        src = os.path.join(saves_dir, f)
        if os.path.isfile(src):
            dst = os.path.join(backup_dir, f)
            if os.path.exists(dst):
                os.chmod(dst, 0o666)
                os.remove(dst)
            shutil.copy2(src, dst)
            n += 1
    return n


def save_site(call, name, saves_dir, wait_s=180, sleep=time.sleep):
    """save_game under `name`, then STAT: a new <name>.rws appeared and no existing file changed (save_game has
    written the CURRENT slot instead of saveName before). Never overwrites: a rebuilt site takes the next _vN."""
    before = saves_stat(saves_dir)
    if name + ".rws" in before:
        raise RuntimeError("%s.rws already exists -- a site save is never overwritten; build the next version" % name)
    call("rimworld/save_game", saveName=name)
    t0 = time.time()
    while name + ".rws" not in saves_stat(saves_dir):
        if time.time() - t0 > wait_s:
            raise RuntimeError("no %s.rws appeared in %s within %ds" % (name, saves_dir, wait_s))
        sleep(POLL_S)
    sleep(3.0)                                  # the writer finishes the file after it appears
    after = saves_stat(saves_dir)
    touched = [f for f in before if after.get(f) != before[f]]
    if touched:
        raise RuntimeError("save touched existing file(s) %s" % touched)
    return {"path": os.path.join(saves_dir, name + ".rws"), "bytes": after[name + ".rws"][0]}


def _state(call):
    try:
        return (call("rimworld/get_ui_state") or {}).get("programState")
    except Exception:                            # noqa: BLE001 - the bridge drops calls during a load
        return None


def _wait(pred, budget_s, sleep):
    t0 = time.time()
    while time.time() - t0 < budget_s:
        try:
            if pred():
                return round(time.time() - t0, 1)
        except Exception:                        # noqa: BLE001
            pass
        sleep(POLL_S)
    return None


def load_site(call, site, budget_s=420, sleep=time.sleep, check=True, name=None):
    """Load the site save from the MAIN MENU (loading over a live game NREs in the teardown: northstar_site.py), wait for
    Playing + a current map, make the site map current, re-apply the map-only quiet profile and the calm sky (a load
    resets the storyteller static and the weather lock), and READ BACK check_map. -> receipt; receipt['verified']."""
    spec = SITES[site]
    name = name or spec.get("save")
    if not name:
        raise ValueError("site %s has no save of its own (Pyrelands loads through northstar_site.py --reload-only)" % site)
    rec = {"site": site, "save": name, "utc": _now(), "problems": []}
    t0 = time.time()
    if _state(call) == "Playing":
        call("rimworld/go_to_main_menu")
        if _wait(lambda: _state(call) == "Entry", 180, sleep) is None:
            rec["problems"].append("main menu not reached within 180 s")
            rec["verified"] = False
            return rec
    try:
        call("rimworld/load_game", saveName=name)
    except Exception as ex:                      # noqa: BLE001 - polled below, never resent
        rec["loadCallRaised"] = type(ex).__name__
    got = _wait(lambda: _state(call) == "Playing" and (call("jawa/map_info") or {}).get("tile") is not None, budget_s, sleep)
    rec["load_s"] = round(time.time() - t0, 1)
    if got is None:
        rec["problems"].append("no Playing map within %ds of load_game %s" % (budget_s, name))
        rec["verified"] = False
        return rec
    reg = read_registry().get(site) or {}
    if reg.get("tile") is not None:
        mid = reg.get("mapId")
        cur = call("jawa/map_info") or {}
        if cur.get("tile") != reg["tile"] and mid is not None:
            call("jawa/set_current_map", mapId=mid)
        cur = call("jawa/map_info") or {}
        if cur.get("tile") != reg["tile"]:
            rec["problems"].append("current map is tile %s, the save's site is %s" % (cur.get("tile"), reg["tile"]))
    S = call_session(call)
    import quiet_site as QS
    rec["quietMap"] = QS.site_profile_receipt(S, "test_site_saves_load_%s" % site, controls=QS.MAP_ONLY + ("modal_broker",))
    mi = call("jawa/map_info") or {}
    rec["sky"] = TG.calm_sky(S, (int(mi.get("sizeX", 250)), int(mi.get("sizeZ", 250))))
    call("jawa/incident_queue_clear")
    if check:
        rec["check"] = check_map(call, site)
        rec["problems"].extend(rec["check"]["problems"])
    rec["ready_s"] = round(time.time() - t0, 1)
    rec["verified"] = not rec["problems"]
    return rec


# ------------------------------------------------------------------ registry (what was built, where, at which HEAD)
def read_registry(path=REGISTRY):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def write_registry(site, entry, path=REGISTRY):
    reg = read_registry(path)
    reg[site] = entry
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(reg, f, indent=1, sort_keys=True)
        f.write("\n")


def _head():
    try:
        import subprocess
        return subprocess.check_output(["git", "rev-parse", "--short=10", "HEAD"], cwd=_UTILS, text=True).strip()
    except Exception:                            # noqa: BLE001
        # a git-archive export (the live runs' copy) has no .git: read the HEAD the exporter wrote beside it
        try:
            root = os.path.dirname(os.path.dirname(os.path.dirname(_UTILS)))
            return open(os.path.join(root, "EXPORT_HEAD"), encoding="utf-8").read().strip() or None
        except OSError:
            return None


# ------------------------------------------------------------------ builds
def fresh_quicktest(call, sleep=time.sleep, budget_s=420):
    call("rimworld/go_to_main_menu")
    _wait(lambda: _state(call) == "Entry", 180, sleep)
    r = call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000) or {}
    w = _wait(lambda: _state(call) == "Playing" and (call("jawa/map_info") or {}).get("success") is not False
              and (call("jawa/map_info") or {}).get("tile") is not None, budget_s, sleep)
    mi = call("jawa/map_info") or {}
    return {"start": r.get("success"), "wait_s": w, "tile": mi.get("tile"), "biome": mi.get("mapBiome"),
            "size": (mi.get("sizeX"), mi.get("sizeZ")), "outdoor": mi.get("outdoorTempNow")}


FROZEN_OR_HOT = ("IceSheet", "SeaIce", "Tundra", "ExtremeDesert", "Desert", "TemperateSwamp", "TropicalSwamp", "ColdBog")


def roll_ok(call, site):
    """Is the current fresh quicktest map an acceptable base for `site`? -> None or why not."""
    spec = SITES[site]
    mi = call("jawa/map_info") or {}
    if (mi.get("sizeX"), mi.get("sizeZ")) != (spec["size"], spec["size"]):
        return "size %sx%s" % (mi.get("sizeX"), mi.get("sizeZ"))
    if mi.get("mapBiome") in FROZEN_OR_HOT:
        return "biome %s" % mi.get("mapBiome")
    t = mi.get("outdoorTempNow")
    lo, hi = spec["temp"]
    if not isinstance(t, (int, float)) or not lo + 3 <= t <= hi - 3:      # margin: the band must hold through the day
        return "outdoor %s C" % t
    w = (call("jawa/weather_get") or {}).get("weather") or {}
    if (w.get("rainRate") or 0) > 0.01:
        return "raining"
    if site == "calm":
        e = call("jawa/flowworks_engine_state") or {}
        if _ok(e) and (e.get("bodyCount") or e.get("excavatedCellCount") or e.get("superdeepCellCount")):
            return "FlowWorks engine not pristine (bodies %s)" % e.get("bodyCount")
    return None


def build(call, site, saves_dir, work_dir, max_rolls=6, sleep=time.sleep, name=None):
    """calm / river: fresh quicktest (re-rolled until roll_ok) -> [river: river_site.py, home map dropped] -> clean_map
    -> check_map -> back up Saves -> save -> registry. Raises on any unclean read-back (nothing is saved then)."""
    spec = SITES[site]
    name = name or spec["save"]
    if name + ".rws" in saves_stat(saves_dir):
        raise RuntimeError("%s.rws exists -- bump the version in SITES (a save is never overwritten)" % name)
    rec = {"site": site, "save": name, "rolls": [], "utc": _now(), "head": _head()}
    for _ in range(max_rolls):
        q = fresh_quicktest(call, sleep=sleep)
        why = roll_ok(call, site) if site == "calm" else None
        if why is None and site == "calm":
            # L1 2026-10-15 (SITE): a map whose clean cannot finish (an indestructible Fallen monolith, VoidMonolith,
            # hitPoints -1, survives destroy_batch) is a bad roll, not a failed build: roll again.
            rec["clean"] = clean_map(call, spec["profile"])
            if rec["clean"]["problems"]:
                why = "clean: %s" % rec["clean"]["problems"]
        q["rejected"] = why
        rec["rolls"].append(q)
        if why is None:
            break
    else:
        raise RuntimeError("no acceptable quicktest map in %d rolls: %s" % (max_rolls, rec["rolls"]))
    if site == "river":
        rec["river"] = make_river_site(call, rec["rolls"][-1].get("tile"))
        rec["clean"] = clean_map(call, spec["profile"])
    if rec["clean"]["problems"]:
        raise RuntimeError("clean_map not clean: %s" % rec["clean"]["problems"])
    rec["check"] = check_map(call, site)
    if not rec["check"]["verified"]:
        raise RuntimeError("check_map after the clean: %s" % rec["check"]["problems"])
    stamp = time.strftime("%Y%m%dT%H%M%S")
    rec["backup"] = {"dir": os.path.join(work_dir, "saves_backup_%s" % stamp)}
    rec["backup"]["files"] = backup_saves(saves_dir, rec["backup"]["dir"])
    rec["saved"] = save_site(call, name, saves_dir, sleep=sleep)
    mi = call("jawa/map_info") or {}
    write_registry(site, {"save": name, "tile": mi.get("tile"), "mapId": mi.get("mapId"), "biome": mi.get("mapBiome"),
                          "builtUtc": rec["utc"], "head": rec["head"], "profile": spec["profile"],
                          "outdoorAtSave": mi.get("outdoorTempNow"), "bytes": rec["saved"]["bytes"]})
    return rec


def make_river_site(call, home_tile):
    """Run FlowWorks' river_site.py in-process (it founds a mild river colony with moving water on >= 2 edges, read back,
    and drops every rejected candidate), then remove the quicktest HOME map so the save holds the river site only."""
    import subprocess
    root = os.path.dirname(os.path.dirname(os.path.dirname(_UTILS)))
    rs = os.path.join(root, "src", "RimMandrake", "FlowWorks", "northstar", "river_site.py")
    env = dict(os.environ, RM_ALLOW_CONCURRENT_BRIDGE="1")   # this module's own connection stays open and idle meanwhile
    p = subprocess.run([sys.executable, rs], cwd=root, capture_output=True, text=True, timeout=900, env=env)
    out = (p.stdout or "").replace("\r", "")
    rec = {"rc": p.returncode, "tail": out.strip().splitlines()[-4:]}
    if p.returncode != 0:
        raise RuntimeError("river_site.py rc %s: %s" % (p.returncode, rec["tail"]))
    mi = call("jawa/map_info") or {}
    rec["site"] = {"tile": mi.get("tile"), "mapId": mi.get("mapId"), "biome": mi.get("mapBiome")}
    if home_tile is not None and home_tile != mi.get("tile"):
        r = call("jawa/settlement_remove", mode="map", tile=home_tile, force=True) or {}
        rec["homeDropped"] = {"tile": home_tile, "ok": _ok(r)}
        call("jawa/set_current_map", mapId=mi.get("mapId"))
    return rec


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("verb", choices=("list", "build", "load", "check"))
    ap.add_argument("site", nargs="?", choices=sorted(SITES))
    ap.add_argument("--work", default=None, help="evidence dir (default Transient/test_site_saves)")
    ap.add_argument("--out", default=None, help="receipt JSON")
    ap.add_argument("--fingerprint", help="build pyrelands: the Pyrelands def fingerprint of the source fixture")
    ap.add_argument("--from-tag", default=None, help="build pyrelands: the source fixture's tag (e.g. r6)")
    ap.add_argument("--tile", type=int, default=5, help="build pyrelands: the fixture's centre tile")
    a = ap.parse_args(argv)
    if a.verb == "list":
        reg = read_registry()
        for k, v in sorted(SITES.items()):
            print("%-10s %-24s profile=%-6s built=%s" % (k, v.get("save") or "(northstar_site tag %s)" % v.get("tag"),
                                                         v["profile"], json.dumps(reg.get(k)) if reg.get(k) else "-"))
        return 0
    if not a.site:
        ap.error("%s needs a site" % a.verb)
    root = os.path.dirname(os.path.dirname(os.path.dirname(_UTILS)))
    work = a.work or os.path.join(root, "Transient", "test_site_saves")
    os.makedirs(work, exist_ok=True)
    from rimbridge_client import RimBridge, resolve_endpoint
    h, p, t = resolve_endpoint()
    with RimBridge(h, p, t, timeout=300.0) as rb:
        call = lambda tool, **kw: rb.call(tool, kw)   # noqa: E731
        if a.verb == "check":
            res = check_map(call, a.site)
        elif a.verb == "load":
            res = load_site(call, a.site)
        elif a.site == "pyrelands":
            res = build_pyrelands(call, a.fingerprint, a.from_tag, a.tile, work)
        else:
            from game_paths import SAVES
            res = build(call, a.site, SAVES, work)
    out = a.out or os.path.join(work, "%s_%s_%s.json" % (a.verb, a.site, time.strftime("%Y%m%dT%H%M%S")))
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, sort_keys=True, default=str)
    ok = res.get("verified", not res.get("problems"))
    print("%s %s: %s -> %s %s" % (a.verb, a.site, "CLEAN" if ok else "NOT CLEAN", out,
                                 "" if ok else (res.get("problems") or (res.get("check") or {}).get("problems"))))
    return 0 if ok else 3


def build_pyrelands(call, fingerprint, from_tag, tile, work_dir):
    """Reload the existing Pyrelands fixture (northstar_site.py's own loader + settle), clean it with the DANGER profile
    (its ruins and wildlife are the suite's subject and stay), read back, save as the tag-`calm` fixture."""
    if not fingerprint:
        raise SystemExit("build pyrelands needs --fingerprint (the source fixture's)")
    root = os.path.dirname(os.path.dirname(os.path.dirname(_UTILS)))
    pdir = os.path.join(root, "src", "RimMandrake", "Pyrelands")
    if pdir not in sys.path:
        sys.path.insert(0, pdir)
    import northstar_site as NS
    from game_paths import SAVES
    from northstar_driver.session import FastSession
    src = NS.fixture_name(1, fingerprint, NS.TARGET_TEMP, from_tag)
    dst = NS.fixture_name(1, fingerprint, NS.TARGET_TEMP, SITES["pyrelands"]["tag"])
    rec = {"site": "pyrelands", "from": src, "save": dst, "utc": _now(), "head": _head()}
    s = FastSession(strict=False)
    with s:
        rec["reload"] = {k: v for k, v in NS.reload_fixture(s, src, tile).items() if k != "quietSite"}
        rec["clean"] = clean_map(s.call, "danger")
        if rec["clean"]["problems"]:
            raise RuntimeError("clean_map not clean: %s" % rec["clean"]["problems"])
        rec["check"] = check_map(s.call, "pyrelands")
        if not rec["check"]["verified"]:
            raise RuntimeError("check_map after the clean: %s" % rec["check"]["problems"])
        rec["backup"] = {"dir": os.path.join(work_dir, "saves_backup_%s" % time.strftime("%Y%m%dT%H%M%S"))}
        rec["backup"]["files"] = backup_saves(SAVES, rec["backup"]["dir"])
        rec["saved"] = save_site(s.call, dst, SAVES)
        mi = s.call("jawa/map_info") or {}
    write_registry("pyrelands", {"save": dst, "tile": mi.get("tile"), "mapId": mi.get("mapId"), "biome": mi.get("mapBiome"),
                                 "builtUtc": rec["utc"], "head": rec["head"], "profile": "danger", "from": src,
                                 "outdoorAtSave": mi.get("outdoorTempNow"), "bytes": rec["saved"]["bytes"],
                                 "load": "northstar_site.py --site 1 --fingerprint %s --tag calm --reload-only --tile %s"
                                         % (fingerprint, tile)})
    rec["verified"] = True
    return rec


if __name__ == "__main__":
    sys.exit(main())
