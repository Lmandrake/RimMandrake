import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils"); sys.path.insert(0, "src/RimMandrake/Utils/modcheck")
from rimdrive.session import Session
import helpers as H, snapshot as S, detectors as D
def show(tag, hits):
    print("%-22s %d hit(s): %s" % (tag, len(hits), "; ".join("%s[%s]" % (h.detector, h.severity) for h in hits)))
with Session(strict=False, quiet=True, focus=False) as s:
    with H.SettingsTransaction(s) as tx:
        rep = H.prepare_bland_map(s, tx)
        print("bland:", rep.bland, rep.problems)
        base = S.Baseline(S.take_snapshot(s, "full"))
        t=time.time(); snap = S.take_snapshot(s, "full"); print("full snapshot %.0f ms" % ((time.time()-t)*1000))
        show("immediately (control)", D.sweep(snap, base))
        s.call("rimworld/step_game_ticks", ticks=120, pauseFirst=True)
        h = D.sweep(S.take_snapshot(s, "full"), base); show("quiet 120 ticks", h)
        for x in h: print("    ", x.summary)
        cols = [r for r in H.read_pawns(s) if H.is_colonist(r) and not r["dead"]]
        a,b,c = cols[0], cols[1], cols[2]
        steps = []
        def ev(tag, fn, step=0):
            fn()
            if step: s.call("rimworld/step_game_ticks", ticks=step, pauseFirst=True)
            hh = D.sweep(S.take_snapshot(s, "full"), base); show(tag, hh)
            for x in hh[:6]: print("      -", x.severity, x.detector, "|", x.summary[:110])
            return hh
        ev("fire near colonist", lambda: s.call("jawa/map_fire", action="start", rect="%d,%d,3,3"%(a["x"]+3,a["z"]+3), fireSize=1.0))
        H.extinguish(s)
        ev("cut on colonist", lambda: s.call("jawa/damage", thingId=b["id"], damageDef="Cut", amount=8, allowColonists=True))
        ev("wolf near colonist", lambda: s.call("jawa/spawn_pawn", kindDef="Wolf_Timber", x=a["x"]+5, z=a["z"]+5, faction="none"))
        ev("raid", lambda: s.call("jawa/fire_raid", points=200.0, dryRun=False))
        ev("mental break", lambda: s.call("jawa/pawn_force_mental_break", pawn=a["id"], intensity="minor"))
        ev("colonist killed", lambda: s.call("jawa/pawn_force_incapacitate", pawn=c["id"], action="kill"))
