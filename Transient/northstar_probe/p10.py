import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils"); sys.path.insert(0, "src/RimMandrake/Utils/modcheck")
from rimdrive.session import Session
import helpers as H, snapshot as S, detectors as D
with Session(strict=False, quiet=True, focus=False) as s:
    with H.SettingsTransaction(s) as tx:
        rep = H.prepare_bland_map(s, tx); print("bland", rep.bland, rep.problems)
        for st in rep.steps: print("  ", st)
        base = S.Baseline(S.take_snapshot(s, "full"))
        for i in range(3):
            s.call("rimworld/step_game_ticks", ticks=120, pauseFirst=True)
            h = D.sweep(S.take_snapshot(s, "full"), base)
            f = s.call("jawa/list_things", defName="Fire")
            print("+%d: hits=%s direct_fires=%s" % (120*(i+1), [x.detector for x in h], f["countMatched"]))
