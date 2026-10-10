# After-fix correctness spot-check + clean Normal-speed window. python.exe ... (repo root)
import sys, json, time, glob, os, pathlib, datetime
sys.path.insert(0, str(pathlib.Path("src/RimMandrake/Utils").resolve()))
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=200); S.connect()
def c(n, **k):
    r = S.call(n, k) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
out = {}
out["blockerDef"] = c("jawa/get_defs", defs="ThingDef/RM_HugeTrunkBlocker", fields="defName,passability,blockWind,fillPercent", limit=1)
spot = []
for gd in ("AB_GiantAgarilux", "AB_WitchesOyster", "RM_PaleTree"):
    g = c("jawa/list_things", defName=gd, limit=2).get("things") or []
    for th in g:
        x, z = th["x"], th["z"]
        b = c("jawa/list_things", defName="RM_HugeTrunkBlocker", rect="%d,%d,9,9" % (x - 4, z - 4), limit=100)
        spot.append({"giant": gd, "id": th.get("id"), "pos": [x, z], "blockersIn9x9": b.get("countMatched"),
                     "blockerCells": [ [bb.get("x"), bb.get("z")] for bb in (b.get("things") or [])][:20]})
out["spot"] = spot
D = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\JawaBench\tps"
c("jawa/set_game_speed", speed="Normal"); time.sleep(8)
t0 = time.time(); time.sleep(60); t1 = time.time(); time.sleep(6)
c("jawa/set_game_speed", speed="Paused")
f = max(glob.glob(os.path.join(D, "tps_*.jsonl")), key=os.path.getmtime); rows = []
for line in open(f, encoding="utf-8"):
    r = json.loads(line)
    if r.get("kind") != "sample": continue
    u = datetime.datetime.strptime(r["utc"][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp()
    if t0 <= u - r["dReal"] and u <= t1 + 0.5: rows.append(r)
tk = sum(r["dTicks"] for r in rows); rl = sum(r["dReal"] for r in rows)
out["normal60"] = {"rows": len(rows), "ticks": tk, "realS": round(rl, 1), "tps": round(tk / rl, 1), "ratio": round(tk / rl / 60, 3),
                   "gc": rows[-1]["gc"] - rows[0]["gc"], "gapMaxMs": max(r["gapMaxMs"] for r in rows), "tops": [r["top"] for r in rows],
                   "fps": round(sum(r["fps"] for r in rows) / len(rows), 1)}
out["counts"] = c("jawa/static_call", type="RimMandrake.HugeThings.MapComponent_HugeFootprints", method="DebugCounts", args="current").get("result")
json.dump(out, open("Transient/foundry_hugefix_check_20261010.json", "w"), indent=1)
print(json.dumps(out["blockerDef"])[:400]); print(json.dumps(out["spot"])[:1500]); print(json.dumps(out["normal60"])); print(out["counts"])
