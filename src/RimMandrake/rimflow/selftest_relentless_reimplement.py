#!/usr/bin/env python3
"""selftest_relentless_reimplement.py -- RELENTLESS_GAME_PROVE_REIMPLEMENT_AFTER_FAIL.

After a game_fail the item is ledger `built` while a new offline worker runs; its next blind PASS makes the supervisor
call `rimflow implemented` again, on a new sha. selftest_relentless_game.py proves that walk against a FAKE ledger
(GW.game_implement simply overwrites a dict). This one proves it against the REAL one: GameFx.game_implement runs the
real cli.py as a subprocess and GameFx.game_ledger replays the real model, both on a throwaway ledger
(RIMFLOW_LEDGER / RIMFLOW_ITEMS, a RIMFLOW_GITINDEX fixture publishing the shas), so nothing reads or writes this repo's.

  1. cli: implemented from `built` (after a live FAIL) and from `validated` (a live pass on record) on a NEW sha is
     accepted; the manifest is replaced, earlier passes are forgotten, and every game clause is owed again at its
     live level; a pass on the OLD sha counts for nothing; passes on the new sha take it to done.
  2. supervisor: relentless_game.step through a whole fail-then-reimplement cycle with only the ledger made real.

    python3 src/RimMandrake/rimflow/selftest_relentless_reimplement.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CLI = os.path.join(HERE, "cli.py")
sys.path.insert(0, HERE)
import model                          # noqa: E402  (the module relentless_game.game_ledger imports)
import relentless as R                # noqa: E402
import relentless_game as G           # noqa: E402
import selftest_relentless as S       # noqa: E402
import selftest_relentless_game as SG  # noqa: E402

FAILS = S.FAILS
ok = S.ok
SHA1 = "a1" * 20
SHA2 = "b2" * 20
CRITERIA = "A1 L0: the defs parse offline\nA2 L1: the comp loads on the minimal list\nA3 L2: it behaves on a quicktest map\n"


class Ledger(object):
    """A throwaway ledger the real cli and the real model both see."""

    def __init__(self):
        self.d = tempfile.mkdtemp(prefix="rl-reimpl-")
        self.events = os.path.join(self.d, "events.jsonl")
        os.makedirs(os.path.join(self.d, "items"))
        with open(os.path.join(self.d, "gitfixture.json"), "w") as fh:
            json.dump({"ref": "origin/main", "head": "f" * 40, "commits": [
                {"sha": s, "ts": "2099-01-01T00:00:0%dZ" % n, "subject": "build %d" % n, "body": "",
                 "files": ["src/RimMandrake/Mod/X.xml"]} for n, s in ((1, SHA1), (2, SHA2))]}, fh)
        self._saved = (model.EVENTS, model.ITEMS, model.CLOSED)
        model.EVENTS, model.ITEMS = self.events, os.path.join(self.d, "items")
        model.CLOSED = os.path.join(model.ITEMS, "closed")

    def env(self):
        e = {k: v for k, v in os.environ.items()
             if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RIMFLOW_GITINDEX", "CLAUDE_PROJECT_DIR")}
        e.update(RIMFLOW_LEDGER=self.events, RIMFLOW_ITEMS=model.ITEMS, RIMFLOW_PROBE="no-reading",
                 RIMFLOW_SEAT="BENCH", AGENT_SEAT="BENCH", RIMFLOW_SHARED_BRIDGE="",
                 RIMFLOW_GITINDEX=os.path.join(self.d, "gitfixture.json"))
        return e

    def cli(self, *args):
        return subprocess.run([sys.executable, CLI] + list(args), cwd=REPO, env=self.env(), capture_output=True,
                              text=True, timeout=180, stdin=subprocess.DEVNULL)

    def must(self, *args):
        r = self.cli(*args)
        ok(r.returncode == 0, "`rimflow %s` exits 0 (got %d: %s)" % (" ".join(args[:3]), r.returncode,
                                                                   (r.stderr or r.stdout).strip()[-400:]))
        return r

    def file(self, item):
        """The item, filed and claimed (`doing`, as the supervisor's `start` leaves it). Written raw: a fixture id like I0 is no
        queue name `file` would take, and the replay that judges every later event is the real one."""
        with open(self.events, "a", encoding="utf-8") as fh:
            for verb, extra in (("file", {"for": "BENCH", "title": "a mod thing", "kind": "feature"}), ("claim", {})):
                fh.write(json.dumps(dict({"seat": "BENCH", "event": verb, "id": item, "ts": "2026-11-01T00:00:00Z"},
                                         **extra)) + "\n")

    def verify(self, item, sha, crit, level, result):
        return self.must("verify", item, "--sha", sha, "--criterion", crit, "--level", level, "--result", result,
                         "--config", "relentless_live_round", "--evidence", "/l/%s.log" % crit,
                         "--why", "selftest: the live round's verdict")

    def done(self):
        model.EVENTS, model.ITEMS, model.CLOSED = self._saved
        shutil.rmtree(self.d, ignore_errors=True)


class RealFx(G.GameFx):
    """GameFx's own game_implement and game_ledger, with only the cli call pointed at the throwaway ledger."""

    def __init__(self, led):
        self.led_ = led
        self.base = led.d

    def rimflow(self, *args, timeout=60, seat=None):
        return self.led_.cli(*args)


def t_cli_reimplement_from_built_and_validated():
    L = Ledger()
    try:
        fx = RealFx(L)
        L.file("I0")
        ok(fx.game_implement("I0", SHA1, CRITERIA) is None, "first implemented on sha1 accepted")
        g = fx.game_ledger("I0")
        ok(g["state"] == "built" and g["owed"] == {"A2": "L1", "A3": "L2"}, "sha1: built, owes A2 L1 + A3 L2: %s" % g)

        L.verify("I0", SHA1, "A2", "L1", "pass")
        g = fx.game_ledger("I0")
        ok(g["state"] == "validated" and g["owed"] == {"A3": "L2"}, "a live pass on sha1: validated, owes A3: %s" % g)
        L.verify("I0", SHA1, "A3", "L2", "fail")                      # the game_fail
        g = fx.game_ledger("I0")
        ok(g["state"] == "built" and g["owed"] == {"A3": "L2"}, "the live FAIL: back to built, still owes A3: %s" % g)

        # a new offline worker fixed it; its blind PASS is on sha2: the supervisor calls implemented again
        why = fx.game_implement("I0", SHA2, CRITERIA)
        ok(why is None, "implemented from BUILT on a new sha is accepted: %s" % why)
        g = fx.game_ledger("I0")
        ok(g["state"] == "built" and G.same_sha(g["built_sha"], SHA2), "built on sha2: %s" % g)
        ok(g["owed"] == {"A2": "L1", "A3": "L2"}, "every game clause owed again, the sha1 pass forgotten: %s" % g)
        ok(all(v in G.LIVE_LEVELS() for v in g["owed"].values()), "owed at live levels: %s" % g["owed"])

        r = L.cli("verify", "I0", "--sha", SHA1, "--criterion", "A2", "--level", "L1", "--result", "pass",
                  "--config", "relentless_live_round", "--evidence", "/l/old.log", "--why", "selftest: stale")
        g = fx.game_ledger("I0")
        ok("A2" in g["owed"], "a pass on the OLD sha counts for nothing (rc %d): %s" % (r.returncode, g["owed"]))

        L.verify("I0", SHA2, "A2", "L1", "pass")
        g = fx.game_ledger("I0")
        ok(g["state"] == "validated" and g["owed"] == {"A3": "L2"}, "sha2 A2 pass: validated: %s" % g)
        # and from VALIDATED, a third build is accepted the same way (no FAIL in between)
        ok(fx.game_implement("I0", SHA1, CRITERIA) is None, "implemented from VALIDATED on another sha is accepted")
        g = fx.game_ledger("I0")
        ok(g["state"] == "built" and G.same_sha(g["built_sha"], SHA1) and g["owed"] == {"A2": "L1", "A3": "L2"},
           "from validated: built, both clauses owed again: %s" % g)
        L.verify("I0", SHA1, "A2", "L1", "pass")
        L.verify("I0", SHA1, "A3", "L2", "pass")
        ok(fx.game_ledger("I0")["state"] == "done", "the last live pass on the current sha is done")
    finally:
        L.done()


def to_game(x, i, sha):
    """selftest_relentless_game.to_game, on a sha the real cli can resolve."""
    x.run_one(i)
    st = x.st(i)
    if not st.get("contract"):
        R.contract(x.s, i, st["gen"], "python3 selftest_x.py", game={"clauses": ["A2", "A3"], "why": "defs load"})
    if st.get("diagnose_owed"):     # a live ending is classified before a finish (LIVE_WORKERS_DIAGNOSE_BEFORE_THEY_REBUILD)
        R.learn(x.s, i, st["gen"], "CLASSIFY: MOD - the proof asked and A3 read 0 where 1 is wanted")
    R.finish(x.s, i, st["gen"], sha, "evidence")
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    x.tick()
    st = x.st(i)
    ok(st["status"] == "checking", "%s: finish on %s reaches the checker" % (i, sha[:6]))
    R.verdict(x.s, i, st["check"]["nonce"], "PASS", "ran it")
    x.w.up[st["check"]["run"]["unit"]] = False
    x.tick()


def t_supervisor_cycle_on_the_real_ledger():
    L = Ledger()
    x = SG.rig(1)
    try:
        real = RealFx(L)
        x.w.game_ledger = real.game_ledger                  # the fake ledger is gone; implement and read are real
        x.w.game_implement = lambda item, sha, crit, live=None: G.GameFx.game_implement(real, item, sha, crit, live)
        x.w.proofs[("I0", ".txt")] = ("live-proof A2: python3 src/RimMandrake/Utils/live_def_check.py --has ThingDef/RM_X=C\n"
                                      "live-proof A3: python3 src/RimMandrake/Utils/live_def_check.py --has ThingDef/RM_Y=C\n")
        x.w.proofs[("I0", ".criteria")] = CRITERIA
        L.file("I0")

        to_game(x, "I0", SHA1)
        x.tick()
        st, g = x.st("I0"), real.game_ledger("I0")
        ok(st["status"] == "game" and st["game"]["phase"] == "prove", "sha1: implemented, prove phase: %s" % st.get("game"))
        ok(g["state"] == "built" and G.same_sha(g["built_sha"], SHA1), "ledger built on sha1: %s" % g)
        x.tick()                                             # the blind round launches
        ok(x.st("I0")["game"]["phase"] == "proving", "sha1: the blind round runs")

        # what the live round records on a FAIL: its row carries the LEDGER's short built_sha (relentless_live_round
        # stamps item["built_sha"]), never the store's full one; a full-sha row matches nothing and the FAIL is unseen
        L.verify("I0", SHA1, "A3", "L2", "fail")
        x.w.rows = [{"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A3", "sha": SHA1[:12], "outcome": "FAIL",
                     "log": "/l/A3.log"}]
        x.w.running = False                                  # no game left up: the next worker is offline
        x.tick()
        st = x.st("I0")
        ok(st["status"] != "game" and (st.get("last_fail") or {}).get("class") == "game_fail",
           "the FAIL goes back to a worker: %s" % st.get("last_fail"))
        ok(real.game_ledger("I0")["state"] == "built", "the ledger stays built while the new worker runs")

        x.w.rows = []
        x.w.running = True
        to_game(x, "I0", SHA2)
        st = x.st("I0")
        ok(st["status"] == "game" and st["game"]["sha"] == SHA2 and st["game"]["phase"] == "implement",
           "the next blind PASS on sha2 re-enters the game phase at implement: %s" % st.get("game"))
        x.tick()
        st, g = x.st("I0"), real.game_ledger("I0")
        ok(st["status"] == "game" and st["game"]["phase"] == "prove",
           "implemented from built on sha2 is accepted, not sent back: %s / %s" % (st.get("game"), st.get("last_fail")))
        ok(G.same_sha(g["built_sha"], SHA2) and g["owed"] == {"A2": "L1", "A3": "L2"},
           "the real ledger owes the game clauses again on sha2: %s" % g)

        L.verify("I0", SHA2, "A2", "L1", "pass")
        L.verify("I0", SHA2, "A3", "L2", "pass")
        x.tick()
        ok(x.st("I0")["status"] == "done" and not x.w.closes, "the ledger's own done finishes it, no second close")
    finally:
        x.done()
        L.done()


def main():
    for t in (t_cli_reimplement_from_built_and_validated, t_supervisor_cycle_on_the_real_ledger):
        print("--", t.__name__)
        try:
            t()
        except Exception as e:                       # noqa: BLE001
            FAILS.append("%s: %s: %s" % (t.__name__, type(e).__name__, e))
            print("FAIL  %s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("selftest_relentless_reimplement: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
