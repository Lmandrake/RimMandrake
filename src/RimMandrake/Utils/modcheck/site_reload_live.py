#!/usr/bin/env python3
"""Live proof of RIMMANDRAKE_RELOAD_SITE_AFTER_A_CHAIN_KILLS_ITS_COLONIST (Windows python; the bridge holder or the lane).

  python.exe site_reload_live.py fresh       on a fresh debug map (no registered save made it)
  python.exe site_reload_live.py pyrelands   on the registered Pyrelands site (tier pyrelands)

Kind A. Claim: run_suite's next chain runs on a reloaded site after a chain killed a colonist. Entry point: run_suite with
hold_site=True, as a lane job calls it. Opportunity: chain one kills one colonist (jawa/pawn_force_incapacitate kill) and
reads it dead. Success: chain two records a reload, its body runs, and it reads that colonist alive (pyrelands) or every
colonist alive (fresh). Control: a run whose colonist is dead at its first hold reloads nothing and runs no body.
Exit 0 = PASS, 1 = FAIL, 2 = could not look."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main(mode):
    # the lane runs its proofs one after another: the proof that ended seconds ago is no second driver
    # (bridge_concurrency_guard refused A2 so, J20261124T210552Z-ef32be)
    os.environ.setdefault("RM_ALLOW_CONCURRENT_BRIDGE", "1")
    import helpers as H
    import runner
    import test_site_saves as T
    from rimdrive import Session
    from suite import Suite
    runner.ensure_playing_map()
    with Session(lock=None) as s:
        print("start map:", runner._load_site_again(s) if mode == "fresh" else T.reload_registered(s, "pyrelands"), flush=True)
        seen = {}

        def colonists():
            return dict((p["id"], bool(p["dead"])) for p in H.read_pawns(s, health=False) if H.is_colonist(p))

        def kill(t):
            with t.component("kill_one", beyond_toggle=True):
                pid = sorted(i for i, d in colonists().items() if not d)[0]
                s.call("jawa/pawn_force_incapacitate", pawn=pid, action="kill")
                seen["killed"], seen["dead_read"] = pid, colonists().get(pid)

        def after(t):
            with t.component("after", beyond_toggle=True):
                seen["after"] = colonists()

        def suite(*chains):
            su = Suite("site_reload_live")
            su.chains.extend(chains)
            return su
        r = runner.run_suite(suite(("kill", kill), ("after", after)), s, hold_site=True)
        again = dict(r["chains"][1].get("site_reload") or {})
        print("killed:", seen.get("killed"), "read dead:", seen.get("dead_read"), "| reload:", again, "| colonists after:",
              seen.get("after"), "| rows:", [(c["name"], c["verdict"]) for ch in r["chains"] for c in ch["components"]], flush=True)
        if seen.get("dead_read") is not True:
            print("COULD NOT LOOK: no colonist was killed, so nothing was spoiled")
            return 2
        live = seen.get("after") or {}
        ok = bool(again.get("loaded")) and bool(live) and not any(live.values())
        if mode == "pyrelands":
            ok = ok and live.get(seen["killed"]) is False and again["loaded"].startswith("save ")
        # control: dead at the first hold of a run = no reload
        runner.run_suite(suite(("kill", kill)), s, hold_site=True)
        seen.pop("after", None)
        c = runner.run_suite(suite(("first", after), ("second", after)), s, hold_site=True)
        none = [ch.get("site_reload") for ch in c["chains"]]
        held = [[x["detail"][:90] for x in ch["components"]] for ch in c["chains"]]
        print("control, dead at the first hold: reloads", none, "bodies ran:", "after" in seen, held, flush=True)
        ok = ok and none == [None, None] and "after" not in seen
        runner._load_site_again(s)      # leave no dead colonist to the next job
    print("SITE RELOAD %s: %s" % (mode, "PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1]))
    except Exception as e:      # noqa: BLE001 - a run that could not be made is never a FAIL of the claim
        print("COULD NOT LOOK: %s: %s" % (type(e).__name__, e))
        sys.exit(2)
