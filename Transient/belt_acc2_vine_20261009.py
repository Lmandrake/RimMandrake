import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
mid = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.call("jawa/set_current_map", mapId=mid)
S.quiet()
for form in ("strangler", "weeper", "sleeper", "lure"):
    for mode in ("on",):
        r = S.call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_FourFormsProof", method="ProofForm", args=form)
        print(form, mode, r.get("success"), str(r.get("result") or r.get("message"))[:420], flush=True)
