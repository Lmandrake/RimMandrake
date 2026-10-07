"""Chill creature on a warm map must leave with a readable message. python.exe, cwd = repo root."""
import sys, os, json, time
REPO = os.getcwd()
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack"))
import validation_aerial as VA  # noqa: E402
B = VA.A()
kinds = sys.argv[1].split(",")
x, z = int(sys.argv[2]), int(sys.argv[3])
out = {"spawn": {}}
for k in kinds:
    r = B.call("jawa/spawn_pawn", kindDef=k, x=x, z=z, faction="none", count=2)
    out["spawn"][k] = {kk: r.get(kk) for kk in ("success", "spawned", "count", "message") if kk in r}
def census():
    r = B.call("jawa/list_pawns", limit=500)
    ps = r.get("pawns") or []
    return {k: sum(1 for p in ps if (p.get("kindDef") or p.get("kind") or p.get("def") or "").startswith(k)) for k in kinds}, (ps[0].keys() if ps else [])
c, keys = census(); out["keys"] = list(keys); out["t0"] = c
seen = []
for step in range(120):  # messages expire in real time, so poll them every 250 ticks
    B.call("rimworld/step_game_ticks", ticks=250, pauseFirst=True, timeoutMs=300000)
    m = B.call("rimworld/list_messages", limit=40)
    for x in (m.get("messages") or []):
        s = (x.get("text") or x.get("label") or str(x))[:200]
        if s not in seen:
            seen.append(s)
    if step % 10 == 9:
        c, _ = census(); out["t%d" % (step + 1)] = c
        if all(v == 0 for v in c.values()):
            break
out["messages"] = seen
out["dead"] = [p for p in (B.call("jawa/list_pawns", includeCorpses=True, limit=500).get("pawns") or []) if p.get("dead") and any((p.get("kindDef") or "").startswith(k) for k in kinds)]
l = B.call("rimworld/list_letters", limit=20)
out["letters"] = [ (x.get("label") or str(x))[:120] for x in (l.get("letters") or [])]
p = os.path.join(REPO, "Transient", "kinetic_gss_live_2026-10-07", "chill_leave_%s.json" % time.strftime("%H%M%S"))
open(p, "w").write(json.dumps(out, indent=1, default=str))
print(json.dumps(out, default=str)[:3000]); print("->", p)
