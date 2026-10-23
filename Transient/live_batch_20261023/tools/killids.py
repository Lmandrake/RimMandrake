"""killids.py ID[,ID...] | --faction DEF -- vanish exact pawns on the current map (raiders a proof spawned), read back."""
import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
import validation_core as V
B = V.Bridge(); H = V._helpers()
arg = sys.argv[1]
if arg == "--faction":
    fac = sys.argv[2]
    pick = lambda x: not x.get("dead") and x.get("spawned", True) and str(x.get("faction") or x.get("factionName") or "") == fac
else:
    want = set(arg.split(","))
    pick = lambda x: not x.get("dead") and x.get("spawned", True) and x.get("id") in want
ids = set(x["id"] for x in H.read_pawns(B, health=False) if pick(x))
print("targets", sorted(ids))
if ids:
    res = H._kill_ids(B, ids, "kill_raiders", pick, action="vanish")
    print("removed", res.evidence.get("targeted"), "left", list(res.residue))
