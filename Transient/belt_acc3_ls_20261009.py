import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
old = int(open("Transient/belt_acc3_still_map_id.txt").read())
S.drop_map(old, 114480)
mid = S.biome_map(114480, "RM_LeaningScrub", size=150, keeper=(5, 5))
open("Transient/belt_acc3_ls_map_id.txt", "w").write(str(mid))
S.quiet()
for form, mode in (("weeper","on"),("weeper","off"),("strangler","on"),("strangler","off"),("lure","on"),("lure","off"),("sleeper","on"),("sleeper","off")):
    r = S.call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_FourFormsProof", method="ProofForm", args="%s|%s" % (form, mode))
    print(form, mode, r.get("success"), str(r.get("result") or r.get("message"))[:300], flush=True)
