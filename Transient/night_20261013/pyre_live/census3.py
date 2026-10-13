"""Night 2026-10-13 PYRE_ANIMALS_DIAGNOSE_TEN_IS_NOT_TWELVE: N fresh Pyrelands site maps via northstar_site.build_site,
wild animal census (validation.py animal_census predicate: faction None, intelligence Animal, not dead) at tick 0
(before save) and again after the fixture reload.  python.exe census3.py <out.json> [N] [tagprefix]"""
import json, os, sys, time
ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Pyrelands"))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
import northstar_site as NS
import preflight_pyrelands as P
from northstar_driver.session import FastSession
from game_paths import SAVES

FP = "a32c5db7c6f1"

def census(s):
    r = P._call(s, "jawa/list_pawns", limit=1000)
    wild = [p for p in (r.get("pawns") or []) if p.get("faction") is None and p.get("intelligence") == "Animal" and not p.get("dead")]
    counts = {}
    for p in wild:
        counts[p.get("kindDef")] = counts.get(p.get("kindDef"), 0) + 1
    return {"total": len(wild), "distinct": len(counts), "counts": counts, "truncated": bool(r.get("truncated")),
            "mapId": r.get("mapId"), "listCount": len(r.get("pawns") or [])}

out = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 3; pref = sys.argv[3] if len(sys.argv) > 3 else "nightcA"
res = {"started": time.strftime("%Y-%m-%dT%H:%M:%S"), "sites": []}
def save():
    with open(out + ".tmp", "w") as f: json.dump(res, f, indent=1, default=str)
    os.replace(out + ".tmp", out)
for i in range(n):
    tag = "%s%d" % (pref, i + 1)
    s = FastSession(strict=False)
    row = {"tag": tag}
    res["sites"].append(row)
    try:
        with s:
            rec = NS.build_site(s, int(os.environ.get("SITEK", "1")) + i, FP, SAVES, os.path.join(ROOT, "Transient", "night_pyre_sites"), tag=tag,
                                census=lambda s_, r_: census(s_))
            row["gen"] = rec.get("census")
            row["tile"] = rec["pick"]["centre"]
            row["reload"] = rec.get("reload")
            row["after_reload"] = census(s)
            row["saveName"] = rec.get("saveName")
    except Exception as ex:
        row["error"] = "%s: %s" % (type(ex).__name__, str(ex)[:400])
    print(json.dumps(row, default=str)[:900], flush=True)
    save()
