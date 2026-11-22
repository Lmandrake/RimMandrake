"""selftest_rites_conduit_choir.py -- RIMMANDRAKE_FIX_CONDUIT_CHOIR_ROW_HIDDEN_PREREQ_COUNTS_TOO, offline: the
conduit_choir_gated_by_hidden_prerequisite chain reads vanilla's real answers green, and reddens when the hidden gate
does not hold. Vanilla ResearchProjectDef.PrerequisitesCompleted walks hiddenPrerequisites too, so while
RUT_Antiq_Language is unfinished it reads False (measured live, Steve filler J20261122T144744Z-003ce9: ScrapShrine
finished, unfinishedPrerequisites [], prerequisitesCompleted False)."""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


class ResearchGame(object):
    """research_finish_project marks a project finished; research_availability answers as vanilla does, or as `bad` says."""

    def __init__(self, bad=None):
        self.done, self.bad, self.tick = set(), bad or {}, 1

    def _ticks(self):
        return self.tick

    def call(self, tool, **kw):
        if tool == "jawa/research_finish_project":
            self.done.add(kw["project"])
            return {"success": True}
        if tool == "jawa/research_availability":
            lang = "RUT_Antiq_Language" in self.done
            ok = "RUT_Rites_ScrapShrine" in self.done and lang
            r = {"success": True, "canStartNow": ok, "prerequisitesCompleted": ok, "unfinishedPrerequisites": [],
                 "isHidden": False}
            r.update(self.bad.get("after" if lang else "before", {}))
            return r
        return {"success": True}


def run_chain(v, session):
    from modcheck.suite import TestContext
    t = TestContext(session)
    dict(v.suite.chains)["conduit_choir_gated_by_hidden_prerequisite"](t)
    return {c.name: (c.verdict, c.detail) for c in t.components}


def main():
    spec = importlib.util.spec_from_file_location("rites_v", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    before, after = "conduit_choir_blocked_until_language_finished", "conduit_choir_unblocked_after_language_finished"
    rows = run_chain(v, ResearchGame())
    check("vanilla answers: both rows green", rows.get(before, ("?",))[0] == "PASS" and rows.get(after, ("?",))[0] == "PASS", rows)

    def red(label, bad, row):
        got = run_chain(v, ResearchGame(bad))
        check("red: " + label, got.get(row, ("?",))[0] == "FAIL", got.get(row))

    red("the hidden gate does not block", {"before": {"canStartNow": True}}, before)
    red("prerequisites read complete with the hidden one unfinished", {"before": {"prerequisitesCompleted": True}}, before)
    red("the tool names an ordinary prerequisite", {"before": {"unfinishedPrerequisites": ["RUT_Rites_ScrapShrine"]}}, before)
    red("still blocked after Language", {"after": {"canStartNow": False}}, after)
    red("prerequisites incomplete after Language", {"after": {"prerequisitesCompleted": False}}, after)
    print("%s (%d failures)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
