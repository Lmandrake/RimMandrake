"""selftest_world_icon_in_flight.py -- the verdict of chain world_icon_in_flight (UTINNI_WORLDMAP_FLIGHT_ICON_1),
driven offline on hand-made jawa/world_objects_get replies: our textures PASS; vanilla's dome (the 2026-09-24
sighting) FAILS by name; every reply that cannot answer is UNMEASURED, never PASS and never FAIL."""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "RimMandrake", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def reply(*tex):
    return {"success": True, "count": len(tex),
            "objects": [{"row": {"def": "Gravship", "tile": 7}, "textures": x} for x in tex]}


def main():
    spec = importlib.util.spec_from_file_location("up_v", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    f = v.world_icon_findings
    ours = {"expandingIcon": "RUT_Utinni", "materialTexture": "RUT_UtinniCaravan"}
    vanilla = {"expandingIcon": "Gravship", "materialTexture": "Caravan"}
    for field in ("expandingIcon", "materialTexture"):
        check("ours passes: " + field, f(reply(ours), field)[0] == "PASS", f(reply(ours), field))
        got = f(reply(vanilla), field)
        check("vanilla fails by name: " + field, got[0] == "FAIL" and "vanilla" in got[1], got)
        mixed = f(reply(ours, vanilla), field)
        check("one vanilla ship of two fails: " + field, mixed[0] == "FAIL", mixed)
        for name, r in (("no reply", None), ("refusal", {"success": False, "message": "No world"}),
                        ("no ship", {"success": True, "count": 0, "objects": []}),
                        ("old companion, no textures", {"success": True, "count": 1,
                                                        "objects": [{"def": "Gravship", "tile": 7}]}),
                        ("read threw", reply(dict(ours, **{field: "ERROR: NullReferenceException: x"}))),
                        ("no texture", reply(dict(ours, **{field: "(none)"}))),
                        ("missing key", reply({}))):
            got = f(r, field)
            check("%s is UNMEASURED: %s" % (name, field), got[0] == "UNMEASURED", got)
    print("RESULT: %s" % ("PASS" if not FAILS else "FAIL %d" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
