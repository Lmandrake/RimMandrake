#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_BUILD_ONE_LANDING_COMMAND_215_FORM_REFUSALS (rank 1 of one_page.md).

Contract: a new module src/RimMandrake/Utils/finish.py
  finish(item, paths, subject, evidence, effect=None, live=None, seat="BENCH", run=None)
      -> {"status", "sha", "line", "why"}; status is one of
         closed          landed, the outcome check holds (or the item has none), the ledger closed it
         close_unlanded  landed, closed, and the close event itself is written but not on origin (rimflow exit 4, twice)
         landed_open     landed, and the item stays open: the check fails, or rimflow refused the close (why says which)
         stopped         not landed, a hand is needed: a red check, a conflict, a hook, races without end, a bad path
         could_not_look  a step gave no reading (hung, no PUBLISHED line, the check is unmeasured); never closed
  run(argv) -> (rc, output); rc None means the command hung and was ended. Acts used: ./publish, git, list_effect.py check,
  cli.py note, cli.py close. `effect` is the item's outcome-check text, None when it has none.
Expected when built: PASS 18/18."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _harness as H  # noqa: E402

FN = H.load("finish")
SHA = "0123456789abcdef0123456789abcdef01234567"
PUB = (0, "PUBLISHED " + SHA)
RACE = (1, "REFUSED: origin kept moving: 5 non-fast-forward rejections in a row")
RED = (1, "REFUSED: 1 tree check(s) red after your commit (it stays on HEAD; fix, then publish again):\n  selftest_x.py")
CONFLICT = (1, "REFUSED: replaying abc onto origin/main stopped on a conflict in: src/a.py. Your commit is intact on HEAD")
HOOK = (1, "REFUSED: push refused by the pre-push hook (nothing pushed):\npre-push REFUSED: ledger NOT_APPEND")
PATHSPEC = (1, "REFUSED: git commit failed: error: pathspec 'src/gone.py' did not match any file(s) known to git")
NOTHING = (1, "REFUSED: nothing to publish: HEAD is already on origin/main")


class Fake:
    def __init__(self, publish, effect=(0, "holds"), close=(0, "ok")):
        self.p, self.e, self.c, self.calls = list(publish), effect, close, []

    def __call__(self, argv):
        a = " ".join(str(x) for x in argv)
        self.calls.append(a)
        if "publish" in os.path.basename(str(argv[0])) or "./publish" in a or "publish.py" in a:
            return self.p.pop(0) if len(self.p) > 1 else self.p[0]
        if "list_effect.py" in a:
            return self.e
        if "cli.py" in a and " close " in a:
            return self.c
        if a.startswith("git"):
            return 0, SHA
        return 0, "ok"

    def n(self, word):
        return sum(word in c for c in self.calls)


def go(fake, **k):
    kw = dict(item="ITEM_X", paths=["src/a.py"], subject="s", evidence="selftest 5/5", effect="cmd:x", run=fake)
    kw.update(k)
    return H.need(FN).finish(**kw)


def case(fake, status, closes, why=None, **k):
    r = go(fake, **k)
    if r["status"] != status or fake.n(" close ") != closes or (why and why not in r["why"] + r["line"]):
        raise RuntimeError("status %s, %d closes, why %r" % (r["status"], fake.n(" close "), r.get("why")))
    return r


H.check("all well: closed once, on the published sha, with the evidence", lambda: (
    lambda f: case(f, "closed", 1)["sha"] == SHA and any(SHA in c and "close" in c and "selftest 5/5" in c for c in f.calls))(
        Fake([PUB])))
H.check("the answer is one line and names the sha", lambda: (
    lambda r: "\n" not in r["line"] and SHA[:10] in r["line"])(go(Fake([PUB]))))
H.check("a race on origin is retried inside the call", lambda: case(Fake([RACE, RACE, PUB]), "closed", 1))


def endless():
    f = Fake([RACE])
    case(f, "stopped", 0)
    return 2 <= f.n("publish") <= 10


H.check("a race without end stops, with a bounded number of tries", endless)
H.check("nothing to publish: the landed commit is found, and the close uses it", lambda: case(Fake([NOTHING]), "closed", 1)["sha"] == SHA)


def once(resp, word):
    f = Fake([resp])
    case(f, "stopped", 0, word)
    return f.n("publish") == 1


H.check("a red check stops at once and names the check", lambda: once(RED, "selftest_x.py"))
H.check("a content conflict stops at once and names the path", lambda: once(CONFLICT, "src/a.py"))
H.check("a pre-push hook stops at once and keeps its words", lambda: once(HOOK, "NOT_APPEND"))
H.check("a path that is not there stops and names the path", lambda: case(Fake([PATHSPEC]), "stopped", 0, "src/gone.py"))
H.check("hung: a publish that hung is could not look, never closed", lambda: case(Fake([(None, "")]), "could_not_look", 0))
H.check("a publish that says 0 with no PUBLISHED line is could not look", lambda: case(Fake([(0, "")]), "could_not_look", 0))
H.check("the outcome check fails: landed, not closed", lambda: case(Fake([PUB], effect=(1, "fails: text not in file")),
                                                                    "landed_open", 0, "fails"))
H.check("the outcome check is unmeasured: could not look, not closed", lambda: case(
    Fake([PUB], effect=(2, "unmeasured")), "could_not_look", 0))
H.check("the outcome check hung: could not look, not closed", lambda: case(Fake([PUB], effect=(None, "")), "could_not_look", 0))
H.check("rimflow refuses the close: landed_open with rimflow's own reason", lambda: case(
    Fake([PUB], close=(1, "refused: owed: criterion c2")), "landed_open", 1, "criterion c2"))
H.check("the close is written and not landed: close_unlanded, never closed", lambda: go(
    Fake([PUB], close=(4, "written, not landed")))["status"] == "close_unlanded")


def empties():
    for k in ({"paths": []}, {"evidence": ""}, {"item": ""}):
        try:
            go(Fake([PUB]), **k)
        except ValueError:
            continue
        return False
    return True


H.check("empty: no paths, no evidence or no item is a ValueError before any act", empties)
H.check("the page names its promises and the selftest runs at ./publish", lambda: H.page(
    "design/specs/2026-11-23-one-landing-command/boundary.md", "the-outcome-check-stands-in-the-path",
    "a-red-check-stops", "could-not-look-never-closes") and H.listed("src/RimMandrake/Utils/selftest_finish.py"))
H.done(18)
