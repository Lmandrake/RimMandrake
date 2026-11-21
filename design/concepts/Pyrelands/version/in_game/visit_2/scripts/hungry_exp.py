"""F9 experiment (sc_fire_sense, fire_sense_hungry_eats_first): does an urgently hungry colonist on the site eat at all?
Same placement as the row (TEN_PAD_SENSE 30,160: H at x-8,z+6, meal at x+2,z+6). Reads H's Food level and category
after the set, the meal's forbidden flag, then H's jobs over 3000 ticks with NO fire, then with the row's fire.
python.exe, bridge held, on a freshly reloaded visit-2 site. Writes evidence/hungry_exp.json."""
import sys, json, os
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
x, z = 30, 160
out = {}
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    def call(tool, **kw):
        return rb.call(tool, kw)
    def need(pid):
        r = call("jawa/pawn_need", pawn=pid, action="list")
        return [(n.get("def") or n.get("defName"), n.get("curLevel"), n.get("category") or n.get("curCategory"))
                for n in (r.get("needs") or []) if "Food" in str(n)]
    def jobs(pid, polls, step):
        seq = []
        for _ in range(polls):
            call("jawa/safe_advance", ticks=step, timeException=False)
            r = call("jawa/list_pawns", faction="player", limit=100)
            j = next((q.get("job") or q.get("curJob") for q in r.get("pawns") or [] if q.get("id") == pid), None)
            if j and (not seq or seq[-1] != j):
                seq.append(j)
        return seq
    for arm in ("no_fire", "fire"):
        r = call("jawa/spawn_pawn", kindDef="Colonist", x=x - 8, z=z + 6 + (0 if arm == "no_fire" else 4), faction="player", count=1)
        pid = ((r.get("pawns") or [{}])[0]).get("id")
        call("jawa/set_work_priority", pawnId=pid, workType="Firefighter", priority=1)
        call("jawa/paint_area", area="home", ops="%d,%d,24,24" % (x - 12, z - 12), value=True)
        sb = call("jawa/spawn_batch", ops="MealSimple:%d,%d,1" % (x + 2, z + 6 + (0 if arm == "no_fire" else 4)))
        s = call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=0.08)
        a = {"pawn": pid, "set": {k: s.get(k) for k in ("success", "before", "after", "level", "message") if k in s},
             "food_after_set": need(pid)}
        cell = call("rimworld/get_cell_info", x=x + 2, z=z + 6 + (0 if arm == "no_fire" else 4))
        a["meal_cell"] = [{k: th.get(k) for k in ("defName", "forbidden", "id", "stackCount") if k in th}
                          for th in (cell.get("things") or [])]
        if arm == "fire":
            call("jawa/map_fire", action="start", rect="%d,%d,2,2" % (x + 6, z + 9), fireSize=1.2)
        a["jobs"] = jobs(pid, 50, 60)
        a["food_end"] = need(pid)
        out[arm] = a
        print(arm, json.dumps(a)[:900])
    call("jawa/map_fire", action="extinguish", rect="0,0,250,250")
json.dump(out, open(os.path.join(r"design\concepts\Pyrelands\version\in_game\visit_2\evidence", "hungry_exp.json"), "w"), indent=1)
