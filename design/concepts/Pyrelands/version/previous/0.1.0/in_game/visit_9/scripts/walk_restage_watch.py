"""The restaged walk save freshly loaded: run it as he would and read, every 500 ticks, the weather, the storyteller's hostiles,
each wild animal's job, and the plants of station 2. Writes evidence/walk_restage_watch.json; saves no game. argv: ticks."""
import collections, json, os, sys, time
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
N = int(sys.argv[1]); h, p, tk = resolve_endpoint(); rows = []; t0 = time.time()
with RimBridge(h, p, tk) as rb:
    c = lambda t, **k: rb.call(t, k, check=False) or {}
    plants0 = c("jawa/export_things", rect="74,20,20,16", includePawns=False, includeItems=False, limit=5000).get("things") or []
    start = c("rimworld/get_game_info")["ticksGame"]
    tick = start
    while tick < start + N and time.time() - t0 < 2400:      # the hang guard of one shell call, about 10 times a plain run
        c("jawa/safe_advance", ticks=500)
        tick = c("rimworld/get_game_info").get("ticksGame")
        pawns = c("jawa/list_pawns", limit=300).get("pawns") or []
        ids = [q["id"] for q in pawns if not q.get("isPlayer")]
        rr = c("jawa/thing_read", thingIds=",".join(str(i) for i in ids), members="CurJobDef").get("rows") or []
        job = {r["id"]: str((r.get("values") or {}).get("CurJobDef")) for r in rr}
        w = c("jawa/weather_get")
        rows.append({"tick": tick, "weather": (w.get("weather") or {}).get("current") or str(w)[:200], "hostile": sum(bool(q.get("hostile")) for q in pawns),
                     "jobs": collections.Counter("%s:%s" % (q.get("kindDef"), job.get(q["id"], "unread")) for q in pawns if not q.get("isPlayer")),
                     "n": collections.Counter(q.get("kindDef") for q in pawns), "st2": [(q.get("kindDef"), q["x"], q["z"]) for q in pawns if 70 <= q["x"] <= 97 and 16 <= q["z"] <= 40]})
    plants1 = c("jawa/export_things", rect="74,20,20,16", includePawns=False, includeItems=False, limit=5000).get("things") or []
    out = {"ticks": tick - start, "wall_s": time.time() - t0, "st2_plants_before": len(plants0), "st2_plants_after": len(plants1), "rows": rows}
json.dump(out, open(os.path.join(ROOT, "design/concepts/Pyrelands/version/in_game/visit_9/evidence/walk_restage_watch.json"), "w"), indent=0)
print(out["ticks"], out["wall_s"], out["st2_plants_before"], out["st2_plants_after"], rows[0] if rows else None)
wx = [(r["tick"], r["weather"]) for i, r in enumerate(rows) if not i or r["weather"] != rows[i - 1]["weather"]]
print("WEATHER", wx); print("HOSTILE max", max([r["hostile"] for r in rows] or [0]))
tot = collections.Counter()
for r in rows: tot.update(r["jobs"])
print("JOBS", sorted(tot.items(), key=lambda a: -a[1])[:40])
