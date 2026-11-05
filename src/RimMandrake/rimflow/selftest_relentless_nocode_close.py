#!/usr/bin/env python3
"""selftest_relentless_nocode_close.py - a blind PASS on a ledger-only sha still closes (RELENTLESS_CLOSE_FIX_EMPTY_DIFF_SAYS_NOTHING).

The instance: DEPLOY_GUARD_FIX_EXCLUDE_DIR_MISMATCH passed its blind check at 061c3bb998, a commit that only appends to
BENCH.jsonl; its work was f160d57cf8. Relentless handed 061c3bb998 to `rimflow close --sha`, which refuses a ledger-only
sha for ever ("touches nothing but the ledger"). The repair, `Effects.ledger_close` through `Effects.work_sha`: close at
the newest commit under the candidate that names the item and changes more than bookkeeping; with none, `close --no-code`.

Real path: the real `cli.py` as a subprocess on a throwaway ledger, real commits of this repo, the real `Effects` methods.

    python3 src/RimMandrake/rimflow/selftest_relentless_nocode_close.py [--case NAME]

Cases (each prints `FIXTURE_VERDICT: PASS|FAIL`; exit 0 on PASS, 1 on FAIL):
    empty-diff-blind-pass   the instance: closes at f160d57cf8, its marker run on that sha
    no-work                 an item no commit names, blind PASS on a ledger-only sha: closes --no-code
    code-candidate          a candidate that did the work closes at itself, unchanged
    review-mark             a candidate that is only a code-review mark closes at the work under it
    constants               relentless.LEDGER_ONLY is cli._LEDGER_ONLY
    ledger-only-sha         the OLD road (close --sha <ledger-only>): FAILS by design, the instrument's bad fixture
No --case: every case but ledger-only-sha.
"""
import ast, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "cli.py")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from rimflow import model                                       # noqa: E402
import relentless as R                                          # noqa: E402

ITEM = "DEPLOY_GUARD_FIX_EXCLUDE_DIR_MISMATCH"
LEDGER_SHA = "061c3bb998"     # appends to BENCH.jsonl only; subject names ITEM
WORK_SHA = "f160d57cf8"       # deploy_def_guard.py, deploy_custom_mods.py, the selftest
MARK_SHA = "bae4f19b57"       # LIVE_RESTORE_RM_PULSE_BRIEF: a code_review mark only
MARK_WORK = "5f32790634"      # LIVE_RESTORE_RM_PULSE_BRIEF's work, under it
MARK_ITEM = "LIVE_RESTORE_RM_PULSE_BRIEF"

FAILS = []
TMP = tempfile.mkdtemp(prefix="relentless_nocode_close_")
LEDGER = os.path.join(TMP, "events.jsonl")
ITEMS = os.path.join(TMP, "items")
os.makedirs(os.path.join(ITEMS, "closed"))


def check(cond, what):
    print(("ok    " if cond else "FAIL  ") + what)
    if not cond:
        FAILS.append(what)


def git(*a):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True, timeout=60).stdout.strip()


def full(sha):
    return git("rev-parse", "--verify", "--quiet", sha + "^{commit}")


def cli(*args, seat="BENCH"):
    env = {k: v for k, v in os.environ.items()
           if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RIMFLOW_GITINDEX")}
    env.update(RIMFLOW_LEDGER=LEDGER, RIMFLOW_ITEMS=ITEMS, RIMFLOW_SEAT=seat, AGENT_SEAT=seat)
    r = subprocess.run([sys.executable, CLI, *args], cwd=REPO, env=env, capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout + r.stderr


def ok(*args, **kw):
    rc, out = cli(*args, **kw)
    if rc:
        raise AssertionError("%s -> %d: %s" % (" ".join(args), rc, out[-400:]))
    return out


def world():
    model.EVENTS = LEDGER
    return model.replay(model.read())


def closes(iid):
    model.EVENTS = LEDGER
    return [e for e in model.read() if e.get("event") == "close" and e.get("id") == iid]


class Books(R.Effects):
    """The real ledger_close / work_sha / touched, on this repo and a throwaway ledger."""

    def __init__(self):
        self.marked = set()
        self.books = REPO

    def rimflow(self, *args, timeout=60, seat=None):
        rc, out = cli(*args, seat=seat or "BENCH")
        return subprocess.CompletedProcess(args, rc, out, out)

    def sync(self):
        pass

    def item_state(self, iid):
        it = world().items.get(iid)
        return {"state": it.state} if it else None


def new(iid):
    ok("file", iid, "--for", "BENCH", "--title", "fixture %s" % iid)
    ok("claim", iid)
    return iid


def need(*shas):
    missing = [s for s in shas if not full(s)]
    if missing:
        raise SystemExit("UNMEASURED: %s not in this clone (git fetch origin)" % ", ".join(missing))


def case_empty_diff_blind_pass():
    print("-- the instance: blind PASS on a ledger-only candidate closes at the work")
    need(LEDGER_SHA, WORK_SHA)
    fx = Books()
    check(fx.touched(full(LEDGER_SHA)) == ["infrastructure/state/ledger/events/BENCH.jsonl"],
          "the instrument sees the candidate as ledger-only: %s" % fx.touched(full(LEDGER_SHA)))
    check(fx.work_sha(ITEM, full(LEDGER_SHA)) == full(WORK_SHA), "work_sha finds %s under %s" % (WORK_SHA, LEDGER_SHA))
    new(ITEM)
    why = fx.ledger_close(ITEM, full(LEDGER_SHA), "relentless: blind PASS at %s" % LEDGER_SHA)
    check(why is None, "ledger_close is not refused: %s" % (why or "")[-300:])
    check(world().items[ITEM].state == "done", "the item is done")
    c = closes(ITEM)
    check(len(c) == 1 and c[0]["sha"] == full(WORK_SHA) and not c[0].get("noCode"),
          "one close, at the work commit: %s" % [(e["sha"][:12], e.get("noCode")) for e in c])
    runs = world().items[ITEM].runs
    check([(r.config, r.sha) for r in runs] == [("marker:blind-check", full(WORK_SHA))], "the marker run is on the work sha")
    check(WORK_SHA in (c[0].get("reason") or "") if c else False, "the reason says where the work is")


def case_no_work():
    print("-- nothing names the item: a ledger-only candidate closes --no-code")
    need(LEDGER_SHA)
    iid = new("NOBODY_COMMITTED_THIS_PROBE_FIXTURE")
    fx = Books()
    check(fx.work_sha(iid, full(LEDGER_SHA)) is None, "work_sha finds no work")
    why = fx.ledger_close(iid, full(LEDGER_SHA), "relentless: blind PASS")
    check(why is None and world().items[iid].state == "done", "closed: %s" % (why or "")[-300:])
    c = closes(iid)
    check(len(c) == 1 and c[0].get("noCode"), "with noCode, saying so: %s" % c)


def case_code_candidate():
    print("-- a candidate that did the work closes at itself")
    need(WORK_SHA)
    iid = new("CODE_CANDIDATE_PROBE_FIXTURE")
    fx = Books()
    check(fx.work_sha(iid, full(WORK_SHA)) == full(WORK_SHA), "work_sha keeps the candidate")
    why = fx.ledger_close(iid, full(WORK_SHA), "relentless: blind PASS")
    c = closes(iid)
    check(why is None and len(c) == 1 and c[0]["sha"] == full(WORK_SHA) and "work at" not in c[0].get("reason", ""),
          "closed at the candidate, reason untouched: %s %s" % ((why or "")[-200:], c))


def case_review_mark():
    print("-- a review mark is bookkeeping: the work under it is the close sha")
    need(MARK_SHA, MARK_WORK)
    fx = Books()
    check(fx.touched(full(MARK_SHA)) == ["infrastructure/state/code_review/BENCH.jsonl"], "the mark only touches review state")
    check(fx.work_sha(MARK_ITEM, full(MARK_SHA)) == full(MARK_WORK), "work_sha walks past it to %s" % MARK_WORK)
    check(fx.work_sha("NOBODY_COMMITTED_THIS_PROBE_FIXTURE", full(MARK_SHA)) == full(MARK_SHA),
          "with no work under it the mark stays the sha (the gate accepts it)")


def case_constants():
    print("-- relentless and cli agree on what is ledger-only")
    tree = ast.parse(open(CLI, encoding="utf-8").read())
    got = [ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
           and any(getattr(t, "id", None) == "_LEDGER_ONLY" for t in n.targets)]
    check(got == [R.LEDGER_ONLY], "cli._LEDGER_ONLY == relentless.LEDGER_ONLY: %s" % got)
    check(set(R.LEDGER_ONLY) < set(R.BOOKKEEPING), "and bookkeeping is wider")


def case_ledger_only_sha():
    print("-- the old road: close --sha <ledger-only> after a blind PASS (expected to FAIL)")
    need(LEDGER_SHA)
    iid = new("OLD_ROAD_PROBE_FIXTURE")
    ok("verify", iid, "--sha", full(LEDGER_SHA), "--result", "pass", "--level", "L0", "--config", "marker:blind-check",
       "--evidence", "e", seat="RUNNER")
    rc, out = cli("close", iid, "--sha", full(LEDGER_SHA), "--why", "relentless: blind check passed")
    check(rc == 0 and world().items[iid].state == "done", "closed at the ledger-only sha: rc=%d %s" % (rc, out[-200:]))


CASES = {"empty-diff-blind-pass": case_empty_diff_blind_pass, "no-work": case_no_work,
         "code-candidate": case_code_candidate, "review-mark": case_review_mark, "constants": case_constants,
         "ledger-only-sha": case_ledger_only_sha}


def main():
    names = sys.argv[sys.argv.index("--case") + 1:][:1] if "--case" in sys.argv else \
        [n for n in CASES if n != "ledger-only-sha"]
    if not names or names[0] not in CASES:
        print("--case one of: %s" % ", ".join(CASES))
        return 2
    try:
        for n in names:
            CASES[n]()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("%s, %d failed" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    print("FIXTURE_VERDICT: %s" % ("PASS" if not FAILS else "FAIL"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
