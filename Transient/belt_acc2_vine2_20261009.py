import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
old = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.drop_map(old, 114480)
mid = S.biome_map(114480, "RM_LeaningScrub", size=150, keeper=(5, 5))
open("Transient/belt_acc2_ls_map_id.txt", "w").write(str(mid))
S.quiet()
try:
    for form in ("strangler", "weeper", "sleeper", "lure"):
        r = S.call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_FourFormsProof", method="ProofForm", args=form)
        print(form, "on", r.get("success"), str(r.get("result") or r.get("message"))[:600], flush=True)
finally:
    pass
