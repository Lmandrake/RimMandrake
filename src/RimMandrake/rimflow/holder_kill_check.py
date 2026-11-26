#!/usr/bin/env python3
"""Did a real kill of a resumed holder run come back? The outcome check of item
RIMMANDRAKE_KILL_LIVE_HOLDER_RESUME_AFTER_FIRST_SESSION (the live half of RIMMANDRAKE_RESUME_HOLDER_SESSIONS_TO_400K_KILL_AND_RESUME).

    python3 src/RimMandrake/rimflow/holder_kill_check.py --mod ExplosiveKnockback     # exit 0 seen, 1 not yet

Reads the mod's DISPATCH shard only. It holds when a holder run whose run.start names the session it resumed
(`resume_session`, recorded by modledger.launch) ended `killed...`, and the next holder run.start after that end names
the same session and `reconcile: true`. The brief's opening lines follow from those two fields (maturation.launch_mod,
tested offline in selftest_holder_resume.py). A blind judge's run is never a holder run (it holds no lease).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def seen(events):
    """-> (True, the killed run and its relaunch) or (False, why not)."""
    runs = [e for e in events if e.get("writer") == "DISPATCH" and e.get("kind") in ("run.start", "run.end")]
    starts = [e for e in runs if e["kind"] == "run.start" and (e.get("body") or {}).get("lease")]
    killed = 0
    for i, e in enumerate(runs):
        b = e.get("body") or {}
        if e["kind"] != "run.end" or not str(b.get("status") or "").lower().startswith("killed"):
            continue
        st = [s for s in starts if (s.get("body") or {}).get("run") == b.get("run")]
        sid = st and (st[-1].get("body") or {}).get("resume_session")
        if not sid:
            continue
        killed += 1
        nxt = [s for s in runs[i + 1:] if s in starts]
        if not nxt:
            return False, "resumed run %s (session %s) was killed; no holder launch since" % (b.get("run"), sid)
        nb = nxt[0].get("body") or {}
        if nb.get("resume_session") == sid and nb.get("reconcile") is True:
            return True, "killed resumed run %s (session %s, %s); the next launch %s resumed it and reconciled" % (
                b.get("run"), sid, b.get("status"), nb.get("run"))
    return False, ("%d killed resumed holder run(s), none relaunched with the same session and reconcile" % killed
                   if killed else "no resumed holder run has been killed")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mod", required=True)
    o = ap.parse_args(argv)
    import modledger
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    ok, why = seen(modledger.read(root, o.mod))
    print(("HOLDS " if ok else "NOT YET ") + why)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
