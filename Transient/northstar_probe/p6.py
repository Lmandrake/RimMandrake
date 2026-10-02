import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils"); sys.path.insert(0, "src/RimMandrake/Utils/modcheck")
from rimdrive.session import Session
import helpers as H
with Session(strict=False, quiet=True, focus=False) as s:
    pre = H.read_settings(s)
    print("before: hostiles", len([r for r in H.read_pawns(s,False) if H.is_hostile(r)]), "wild", len([r for r in H.read_pawns(s,False) if H.is_wildlife(r)]), "strangers", len([r for r in H.read_pawns(s,False) if H.is_stranger(r)]))
    t=time.time()
    with H.SettingsTransaction(s) as tx:
        rep = H.prepare_bland_map(s, tx)
        print("prepare took %.1fs bland=%s problems=%s" % (time.time()-t, rep.bland, rep.problems))
        for st in rep.steps: print("  ", st)
        print("  baseline:", {k:sorted(v) for k,v in rep.baseline.items()})
        print("  during: storyteller", H.read_settings(s)["enableStoryteller"])
    post = H.read_settings(s)
    print("settings restored exactly:", all(pre[k]==post[k] for k in pre))
    print("after: ", H.assert_bland(s))
