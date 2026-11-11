"""trunk_live.py -- HUGETHINGS_TRUNK_ZERO_BLOCKERS_1 criterion A2: a full-grown RM_Nogtyl gets its measured trunk.

  python.exe src/RimMandrake/HugeThings/northstar/trunk_live.py [--site X,Z] [--out FILE]

LIST: Huge Things (mandrake.rm.hugethings) + RimMandrake.Biomes (TheRot's RM_Nogtyl and its RotGiants_HugeFootprint patch), all
five DLC. Any Playing map; the site (default: map centre +30,-30) is cleared (destroy_batch All, 30x30) and DIRTIED: use a
throwaway quicktest map, never a canonical save.

The same check as validation.py's trunk.full_grown_giant_gets_its_measured_footprint, which failed live 2026-10-08 with 0 blockers:
stage RM_Nogtyl at growth 1 (artboard_stage sets growth before GenSpawn), step 120 ticks, count RM_HugeTrunkBlocker in the
17x17 box around it (must be one of the measured variants' contact counts, read from the patch) and in the two rows south (must
be 0). Beside the counts it ALWAYS reads MapComponent_HugeFootprints.DebugPlantState (registered, claimed/realized/pending, the
comp's signature, the pending cells' planner flags and a dry Planner.Plan accept count), so a FAIL says why.

Settings are only read: a run with giantPlantsEnabled/plantTrunkEnabled off or plantTrunkScale != 1 is UNMEASURED SITE.
Exit 0 PASS, 1 FAIL or UNMEASURED, 2 the bridge was never reached (no verdict). Rows JSON -> Transient/modcheck/.
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(MOD, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))

ITEM = "HUGETHINGS_TRUNK_ZERO_BLOCKERS_1"
GIANT = "RM_Nogtyl"
BLOCKER = "RM_HugeTrunkBlocker"
MC = "RimMandrake.HugeThings.MapComponent_HugeFootprints"
SETTINGS = "RimMandrake.HugeThings.RM_HugeThingsSettings"
NEED = {"giantPlantsEnabled": "true", "plantTrunkEnabled": "true", "plantTrunkScale": 1.0}
WAIT = 120
NO_VERDICT = 2
PATCH = os.path.join(MOD, "..", "TheRot", "Patches", "RotGiants_HugeFootprint.xml")


def allowed_counts(path=PATCH):
    """The measured contact counts of GIANT's variants, read from the patch (never a hand number)."""
    import xml.etree.ElementTree as ET
    for op in ET.parse(path).getroot():
        if 'defName="%s"' % GIANT in (op.findtext("xpath") or ""):
            li = op.find("match/value/li")
            return sorted(set(len(v.findall("contact/li")) for v in li.findall("variants/li")))
    return []


def rects(x, z):
    """(around, south) as list_things rects: the footprint plus margin incl. two rows south, and those two rows."""
    return "%d,%d,17,17" % (x - 8, z - 2), "%d,%d,17,2" % (x - 8, z - 2)


def map_centre(mi):
    """Default site (centre +30,-30) from a jawa/map_info reply ({sizeX, sizeZ, ...}, JawaBenchMapInfoTools), or None."""
    try:
        return int(mi["sizeX"]) // 2 + 30, int(mi["sizeZ"]) // 2 - 30
    except (KeyError, TypeError, ValueError):
        return None


def judge(around, south, allowed, probe):
    """(status, detail). around/south are blocker counts, allowed the measured counts, probe the DebugPlantState text."""
    d = "blockers around=%s south=%s (allowed %r) | probe: %s" % (around, south, allowed, probe)
    if around is None or south is None or not allowed:
        return "UNMEASURED", d
    if around not in allowed:
        return "FAIL", d
    if south:
        return "FAIL", d
    return "PASS", d


def settings_ok(vals):
    bad = []
    for f, want in NEED.items():
        v = vals.get(f)
        if isinstance(want, float):
            try:
                if abs(float(v) - want) > 1e-4:
                    bad.append("%s=%s" % (f, v))
            except (TypeError, ValueError):
                bad.append("%s=%r" % (f, v))
        elif str(v).lower() != want:
            bad.append("%s=%r" % (f, v))
    return bad


def open_bridge():
    from rimbridge_client import RimBridge, RimBridgeError, discover_from_log
    try:
        host, port, token = discover_from_log()
        rb = RimBridge(host, port, token, timeout=180.0)
        rb.connect()
        return rb
    except (RimBridgeError, OSError) as e:
        print("UNMEASURED: the bridge could not be reached, no verdict (exit %d): %s" % (NO_VERDICT, str(e)[:400]), flush=True)
        return None


def run(rb, site, out):
    log = []

    def call(tool, **kw):
        try:
            r = rb.call(tool, kw) or {}
        except Exception as ex:  # noqa: BLE001
            r = {"success": False, "error": "call raised: %s" % ex}
        log.append((tool, kw, str(r)[:400]))
        return r

    def count(rect):
        r = call("jawa/list_things", defName=BLOCKER, rect=rect, limit=200)
        return int(r["countMatched"]) if isinstance(r, dict) and "countMatched" in r else None

    def probe(x, z):
        r = call("jawa/static_call", type=MC, method="DebugPlantState", args="current|%d,%d" % (x, z))
        return str(r.get("result") if r.get("success") is True else (r.get("error") or r.get("message") or r))[:900]

    def finish(status, detail):
        row = dict(id="full_grown_giant_gets_its_measured_footprint", item=ITEM, criterion="A2", status=status, detail=detail)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(dict(script="trunk_live.py", when=time.strftime("%Y-%m-%dT%H:%M:%S"), rows=[row], calls=log), f, indent=1,
                      default=str)
        print("A2 %s: %s\nrows -> %s" % (status, detail, out), flush=True)
        return 0 if status == "PASS" else 1

    vals = dict((f, call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=f).get("value")) for f in NEED)
    bad = settings_ok(vals)
    if bad:
        return finish("UNMEASURED", "SITE: settings not at the shipped trunk defaults: %s" % bad)
    allowed = allowed_counts()
    if site:
        x, z = (int(v) for v in site.split(","))
    else:
        mi = call("jawa/map_info")
        xz = map_centre(mi)
        if xz is None:
            return finish("UNMEASURED", "HARNESS: map_info unreadable: %s" % str(mi)[:200])
        x, z = xz
    call("jawa/destroy_batch", rects="%d,%d,30,30" % (x - 15, z - 15), categories="All")
    around_r, south_r = rects(x, z)
    pre = count(around_r)
    if pre:
        return finish("UNMEASURED", "SITE: %d blockers remain at %d,%d after clearing | probe: %s" % (pre, x, z, probe(x, z)))
    st = call("jawa/artboard_stage", phase="subjects", pause=False, killHostiles=True,
              ops="id=g|kind=plant|x=%d|z=%d|def=%s|growth=1" % (x, z, GIANT))
    ops = st.get("ops") or [] if isinstance(st, dict) else []
    if not ops or not ops[0].get("ok"):
        return finish("UNMEASURED", "HARNESS: could not stage %s at %d,%d: %s" % (GIANT, x, z, str(st)[:300]))
    call("rimworld/step_game_ticks", ticks=WAIT)
    around, south = count(around_r), count(south_r)
    status, detail = judge(around, south, allowed, probe(x, z))
    detail = "site %d,%d readBack=%s; %s" % (x, z, ops[0].get("readBack"), detail)
    # tidy: cut the plant (its blockers go with it); recorded, not judged
    call("jawa/destroy_batch", rects="%d,%d,1,1" % (x, z), categories="Plant")
    detail += " | after cut: %s blockers" % count(around_r)
    return finish(status, detail)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="", help="X,Z of the giant (default: map centre +30,-30)")
    ap.add_argument("--out", default=os.path.join(REPO, "Transient", "modcheck", "hugethings_trunk_a2_%s.json"
                                                  % time.strftime("%Y%m%dT%H%M%S")))
    a = ap.parse_args()
    if a.site and not re.match(r"^\d+,\d+$", a.site):
        ap.error("--site wants X,Z")
    rb = open_bridge()
    if rb is None:
        return NO_VERDICT
    with rb:
        return run(rb, a.site, os.path.abspath(a.out))


if __name__ == "__main__":
    sys.exit(main())
