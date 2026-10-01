from bx import call
r=call("jawa/list_things",{"defName":"Corpse_Hare","limit":50}); print([(t.get("id"),t.get("x"),t.get("z")) for t in r.get("things",[])])
for h in ("Hare112703","Hare112704","Hare112705"):
    print(h, str(call("jawa/pawn_get",{"pawn":h}))[:200])
