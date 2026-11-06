#!/usr/bin/env python3
"""selftest_close_gate.py - DONE IS EARNED (CLOSE_GATE_ENFORCE_DONE_IS_EARNED, RO3, ruling D1(b) of 2026-11-01).

Every case plants its fault on the real path: the real `cli.py` as a subprocess, a throwaway ledger, real commits of this
repo. S1-S4 of the item's verify section; S6 holds every way to done to the same gate. `--au4` is S5: it re-reads AU4 from the live ledger (close_audit.py).

    python3 src/RimMandrake/rimflow/selftest_close_gate.py [--au4]
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "cli.py")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from rimflow import model                                       # noqa: E402

FAILS = []
TMP = tempfile.mkdtemp(prefix="rimflow_close_gate_")
LEDGER = os.path.join(TMP, "events.jsonl")
ITEMS = os.path.join(TMP, "items")
os.makedirs(os.path.join(ITEMS, "closed"))


def check(cond, what):
    print(("ok    " if cond else "FAIL  ") + what)
    if not cond:
        FAILS.append(what)


def git(*a):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True, timeout=60).stdout.strip()


def paths_of(sha):
    return git("diff-tree", "--no-commit-id", "--name-only", "-r", "--root", sha).split()


def commits(n=2):
    """Real code commits on origin/main that promise nothing live, newest first: `a` is an ancestor of `b`."""
    import live_line
    good = [sha for sha in git("log", "origin/main", "--format=%H", "-n", "300", "--", "src/RimMandrake/Utils/").split()
            if paths_of(sha) and not live_line.needs_line(paths_of(sha))]
    if len(good) < n:
        raise SystemExit("UNMEASURED: %d code commits with no live path in the last 300" % len(good))
    return good[:n]


def ledger_only():
    for sha in git("log", "origin/main", "--format=%H", "-n", "200", "--",
                   "infrastructure/state/ledger/events/RUNNER.jsonl").split():
        names = paths_of(sha)
        if names and all(n.startswith("infrastructure/state/ledger/") for n in names):
            return sha
    raise SystemExit("UNMEASURED: no ledger-only commit in the last 200 RUNNER commits")


def cli(*args, seat="BENCH"):
    env = {k: v for k, v in os.environ.items()
           if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RIMFLOW_GITINDEX")}
    env.update(RIMFLOW_LEDGER=LEDGER, RIMFLOW_ITEMS=ITEMS, RIMFLOW_SEAT=seat, AGENT_SEAT=seat)
    r = subprocess.run([sys.executable, CLI, *args], cwd=REPO, env=env, capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr


def ok(*args, **kw):
    rc, out = cli(*args, **kw)
    if rc:
        raise AssertionError("%s -> %d: %s" % (" ".join(args), rc, out[-400:]))
    return out


def refused(what, kind, *args, **kw):
    rc, out = cli(*args, **kw)
    check(rc != 0 and kind in out, "%s: refused (%s)" % (what, kind))
    if rc == 0 or kind not in out:
        print("      rc=%d: %s" % (rc, out[-300:]))
    check(item(args[1]).state != "done", "%s: and the item did not change" % what)


def events():
    model.EVENTS = LEDGER
    return model.read()


def world():
    return model.replay(events())


def item(iid):
    return world().items[iid]


N = [0]


def new(name, prose=""):
    N[0] += 1
    iid = "%s_%d_PROBE_FIXTURE" % (name, N[0])
    if prose:
        with open(os.path.join(ITEMS, iid + ".md"), "w", encoding="utf-8") as f:
            f.write(prose)
    ok("file", iid, "--for", "BENCH", "--title", "fixture %s" % iid)
    ok("claim", iid)
    return iid


def manifest(iid, *crit):
    path = os.path.join(TMP, iid + ".json")
    with open(path, "w", encoding="utf-8") as f:
        f.write("".join("- %s %s: fixture\n" % c for c in crit))
    return path


def built(name, sha, *crit):
    """An item implemented at `sha` owing `crit`, [(id, level)]."""
    iid = new(name)
    ok("implemented", iid, "--sha", sha, "--criteria-file", manifest(iid, *crit))
    return iid


def passed(iid, sha, level="L0", **kw):
    return ok("verify", iid, "--sha", sha, "--level", level, "--result", "pass", "--config", "fixture",
              "--evidence", "ran it", **kw)


def s1(a, b, led):
    print("-- S1 each of the four missing is refused")
    i = new("NO_SHA")
    refused("no sha, no --no-code (implicit HEAD)", "--no-code", "close", i)
    refused("--no-code with no words", "needs the words", "close", i, "--no-code", " ")
    refused("--sha and --no-code at once", "Pick one", "close", i, "--sha", a, "--no-code", "x")
    passed(i, led)
    refused("a sha touching only the ledger", "nothing but the ledger", "close", i, "--sha", led)
    refused("a sha no commit answers to", "does not resolve", "close", i, "--sha", "0badc0de0badc0de")
    ok("close", i, "--no-code", "a decision, no commit shows it")
    last = [e for e in events() if e.get("event") == "close"][-1]
    check(item(i).state == "done" and last.get("noCode"), "--no-code closes and says so on the event")

    i = built("OWED", a, ("C1", "L1"), ("C2", "L2"))
    refused("owed criteria (no longer a warning)", "owed", "close", i, "--sha", a)
    refused("owed criteria with --no-code", "owed", "close", i, "--no-code", "skip it")
    refused("owed criteria with the owner's word", "owed", "close", i, "--sha", a, "--per-ruling", i)

    i = new("UNCHECKED")
    refused("no check run on that sha", "unchecked", "close", i, "--sha", a)
    passed(i, b)
    refused("a check on ANOTHER sha", "unchecked", "close", i, "--sha", a)

    i = new("MASKED_FAIL")
    passed(i, a)
    ok("verify", i, "--sha", a, "--level", "L0", "--result", "fail", "--config", "fixture", "--evidence", "broke")
    passed(i, b)
    refused("a pass on ANOTHER sha cannot hide a fail", "fail ", "close", i, "--sha", a)

    i = built("L0_ONLY", a, ("C1", "L0"))
    check(item(i).state == "built" and item(i).held, "the setup: an L0 manifest stops at built, no run on the sha")
    refused("a manifest is no check on the sha", "unchecked", "close", i, "--sha", a)

    i = new("NEWER_FAIL")
    passed(i, a)
    ok("verify", i, "--sha", a, "--level", "L0", "--result", "fail", "--config", "fixture", "--evidence", "broke")
    refused("a fail newer than the pass", "fail ", "close", i, "--sha", a)

    i = new("CLEAN", prose="Cites `%s` and nothing else.\n" % paths_of(a)[0])
    passed(i, a)
    ok("close", i, "--sha", a)
    check(item(i).state == "done", "a clean close: named sha, a check on it, nothing failing -> done")


def s2(a, b):
    print("-- S2 a fail after a pass demotes")
    i = built("DEMOTE", a, ("C1", "L1"), ("C2", "L2"))
    ok("verify", i, "--criterion", "C1", "--sha", a, "--result", "pass", "--config", "fixture", "--evidence", "e")
    it = item(i)
    check(it.state == "validated" and it.outstanding == ["C2"], "the setup: C1 passed, validated, C2 owed")
    out = ok("verify", i, "--criterion", "C1", "--sha", a, "--result", "fail", "--config", "fixture", "--evidence", "e")
    it = item(i)
    check(it.state == "built" and sorted(it.outstanding) == ["C1", "C2"] and not it.passed and it.level_reached == "L0",
          "a fail on the built sha: validated -> built, C1 owed again (%s %s)" % (it.state, it.outstanding))
    check("demoted" in out, "and the seat is told")
    i = built("UNSCOPED", a, ("C1", "L1"), ("C2", "L2"))
    ok("verify", i, "--criterion", "C1", "--sha", a, "--result", "pass", "--config", "fixture", "--evidence", "e")
    ok("verify", i, "--sha", a, "--result", "fail", "--config", "fixture", "--evidence", "e")
    check(sorted(item(i).outstanding) == ["C1", "C2"], "an unscoped fail re-owes everything it contradicts")
    i = built("STALE_FAIL", a, ("C1", "L1"), ("C2", "L2"))
    ok("verify", i, "--criterion", "C1", "--sha", a, "--result", "pass", "--config", "fixture", "--evidence", "e")
    ok("verify", i, "--criterion", "C1", "--sha", b, "--result", "fail", "--config", "fixture", "--evidence", "e")
    check(item(i).state == "validated", "a fail on a stale sha demotes nothing")
    i = built("STALE_PASS", a, ("C1", "L1"))
    out = ok("verify", i, "--criterion", "C1", "--sha", b, "--result", "pass", "--config", "fixture", "--evidence", "e")
    it = item(i)
    check(it.state == "built" and it.outstanding == ["C1"] and "does NOT count" in out,
          "a pass on a stale built_sha does not count: the item stays built, C1 owed")


def s3(a, b):
    print("-- S3 a seeded behavioural regression caught later reopens the item")
    # the seeded regression passes the item's check: C1 is green, the item goes done with no close
    i = built("REGRESSION", a, ("C1", "L1"))
    with open(os.path.join(ITEMS, "closed", i + ".md"), "w", encoding="utf-8") as f:
        f.write("prose\n")
    ok("verify", i, "--criterion", "C1", "--sha", a, "--result", "pass", "--config", "the check as written",
       "--evidence", "green")
    check(item(i).state == "done", "the seed: every current check passes, the item is done")
    # the later catch: a check nobody had at close, on a later commit that contains the closed one
    out = ok("verify", i, "--criterion", "C1", "--sha", b, "--result", "fail", "--config", "the sharper check",
             "--evidence", "caught it", seat="FOUNDRY")
    it = item(i)
    check(it.state == "ready" and it.closed_sha is None and it.outstanding == ["C1"] and "REOPENED" in out,
          "a later catch, by another seat, reopens the same id and owes C1 (%s)" % it.state)
    check(os.path.exists(os.path.join(ITEMS, i + ".md")), "and its prose is back in the live glob")
    i = new("CLOSED_HAND")
    passed(i, b)
    ok("close", i, "--sha", b)
    ok("verify", i, "--sha", b, "--level", "L1", "--result", "fail", "--config", "x", "--evidence", "e")
    check(item(i).state == "ready", "a hand close reopens the same way, on the closed sha")
    i = new("CLOSED_LATE")
    passed(i, b)
    ok("close", i, "--sha", b)
    ok("verify", i, "--sha", a, "--level", "L1", "--result", "fail", "--config", "x", "--evidence", "e")
    check(item(i).state == "done", "a fail on a sha OLDER than the close is stale: it reopens nothing")


def s4(a, b):
    print("-- S4 the D1(b) rules")
    fail = lambda i, s: ok("verify", i, "--sha", s, "--level", "L0", "--result", "fail",     # noqa: E731
                           "--config", "fixture", "--evidence", "e")
    i = new("NO_VERDICT")
    ruling = N[0]
    passed(i, a)
    ok("close", i, "--sha", a)
    check(item(i).state == "done", "no verdict at all blocks nothing (not option c)")

    for flag in (("--owner-said", "Close it."), ("--by-card", "close -> yes"),
                 ("--per-ruling", "NO_VERDICT_%d_PROBE_FIXTURE" % ruling)):
        i = new("OVERRIDE")
        passed(i, a)
        fail(i, a)
        refused("--why is not his word", "fail ", "close", i, "--sha", a, "--why", "I am sure")
        ok("close", i, "--sha", a, *flag)
        check(item(i).state == "done", "the owner overrides with %s" % flag[0])

    i = new("WHY", prose="Cites `design/RimMandrake/standing_rulings.md` only.\n")
    passed(i, a)
    refused("a sha touching none of the cited paths", "none of the", "close", i, "--sha", a)
    ok("close", i, "--sha", a, "--why", "the fix landed elsewhere, the item cites the ruling")
    check(item(i).state == "done", "--why lets that one through")


def s4_relentless(a):
    print("-- the supervisor's path: the blind PASS is the check, and the gate holds it too")
    import relentless as RE

    class Books(RE.Effects):
        def __init__(self):
            self.marked = set()
            self.books = REPO

        def rimflow(self, *args, timeout=60, seat=None):
            rc, out = cli(*args, seat=seat or "BENCH")
            return subprocess.CompletedProcess(args, rc, out, out)

        def sync(self):
            pass

        def item_state(self, iid):
            return {"state": item(iid).state}

    fx = Books()
    i = new("MARKER")
    check(fx.ledger_close(i, a, "relentless: blind PASS") is None and item(i).state == "done",
          "a blind PASS closes: the Marker's run is on the sha")
    check([r.config for r in item(i).runs] == ["marker:blind-check"], "and the run says who judged it")


def s7_marker_fail(a, b):
    print("-- a Marker FAIL is on the ledger, seen by the Close gate, locking once MARKER_FAIL_LOCKS is on")
    import relentless as RE

    class Books(RE.Effects):
        def __init__(self):
            self.marked = set()
            self.books = REPO

        def rimflow(self, *args, timeout=60, seat=None):
            rc, out = cli(*args, seat=seat or "BENCH")
            return subprocess.CompletedProcess(args, rc, out, out)

    fx = Books()

    def locked(iid, sha, owner=False):
        keep = model.MARKER_FAIL_LOCKS
        model.MARKER_FAIL_LOCKS = True      # in-process only: the replay and the gate as they will read once it is on
        try:
            it = world().items[iid]
            return [k for k, _ in model.close_refusals(it, sha, owner=owner)], it.state
        finally:
            model.MARKER_FAIL_LOCKS = keep

    check(model.MARKER_FAIL_LOCKS is False, "the lock ships off (operations_design_2026-11-01 §9 step 2: not yet locking)")
    i = new("MARKERFAIL")
    passed(i, a)
    check(fx.ledger_marker_fail(i, a, "the proof read red") is None, "the supervisor's FAIL write is accepted from RUNNER")
    runs = item(i).runs
    check([(r.config, r.result, r.sha[:12]) for r in runs][-1:] == [("marker:blind-check", "fail", a[:12])],
          "the ledger holds the Marker's FAIL on the candidate sha")
    check(item(i).state == "doing", "off, it moves no state")
    why = model.marker_lock(item(i), a)
    check(bool(why) and "Marker" in why and "proof read red" in why, "the Close gate sees it: %s" % why)
    check(model.close_refusals(item(i), a) == [], "off, it refuses nothing")
    kinds, _ = locked(i, a)
    check(kinds == ["fail"], "on, it is the fail the lock holds: %s" % kinds)
    check(locked(i, a, owner=True)[0] == [], "on, his word on the close lifts it")
    out = ok("close", i, "--sha", a)
    check(item(i).state == "done" and "marker" in out and "Marker" in out,
          "off, a hand close goes through and prints the Marker's FAIL")
    # A wrong FAIL (§9 step 2: 1 of 9 good controls failed) must not reopen closed work before the lock is on: a fail
    # on an open item moves nothing anyway, so this is the one probe that sees the _earned_run guard.
    before = (item(i).state, item(i).closed_sha, list(item(i).passed), list(item(i).outstanding))
    check(before[0] == "done", "the probe starts from a closed item: %s" % before[0])
    fx.ledger_marker_fail(i, a, "a wrong FAIL after the close")
    after = item(i)
    check((after.state, after.closed_sha, list(after.passed), list(after.outstanding)) == before,
          "off, a Marker FAIL on a closed item's sha leaves it done, its passes and owed criteria unchanged: %s"
          % ((after.state, after.closed_sha),))

    j = new("MARKERAPPEAL")
    passed(j, a)
    fx.ledger_marker_fail(j, a, "a false fail")
    ok("verify", j, "--sha", a, "--level", "L0", "--result", "pass", "--config", "marker:blind-check",
        "--evidence", "the appeal's blind PASS", seat="RUNNER")
    check(model.marker_lock(item(j), a) is None and locked(j, a)[0] == [], "a pass on that sha after it (the appeal) lifts it")

    k = new("MARKERNEWBUILD")
    passed(k, a)
    fx.ledger_marker_fail(k, a, "broken build")
    check(sorted(locked(k, b)[0]) == ["fail", "unchecked"], "on, it holds a new build with no pass: %s" % locked(k, b)[0])
    passed(k, b)
    check(model.marker_lock(item(k), b) is None and locked(k, b)[0] == [], "a new build that passes lifts it")


def s5_replay():
    print("-- history replays unchanged: nothing before EARNED_FROM moves")
    old = "2026-10-01T00:00:%02dZ"
    evs = [{"seat": "BENCH", "event": "file", "ts": old % 0, "id": "OLD_PROBE_FIXTURE", "for": "BENCH", "title": "t", "kind": "task"},
           {"seat": "BENCH", "event": "claim", "ts": old % 1, "id": "OLD_PROBE_FIXTURE"},
           {"seat": "BENCH", "event": "close", "ts": old % 2, "id": "OLD_PROBE_FIXTURE", "sha": "abcdef1"},
           {"seat": "BENCH", "event": "verify", "ts": old % 3, "id": "OLD_PROBE_FIXTURE", "sha": "abcdef1", "result": "fail",
            "config": "c"}]
    check(model.replay(evs).items["OLD_PROBE_FIXTURE"].state == "done", "an old fail on an old close changes nothing")


def s6_every_way_to_done(a, b, led):
    print("-- S6 the gate is one gate: `implemented` and `verify` reach done only as `close` does")
    held = lambda i: item(i).state == "built" and item(i).held and not item(i).closed_sha

    i = new("NONE_OWED_NO_CHECK")
    out = ok("implemented", i, "--sha", b, "--none-owed")
    check(held(i) and "unchecked" in out, "--none-owed with no pass on the sha stops at built and says why")
    ok("verify", i, "--sha", b, "--level", "L0", "--result", "pass", "--config", "fixture", "--evidence", "e")
    check(item(i).state == "done" and model.same_sha(item(i).closed_sha, b), "then a level-tagged pass on that sha finishes it")

    i = new("PASS_THEN_IMPLEMENTED")
    passed(i, b)
    ok("implemented", i, "--sha", b, "--none-owed")
    check(item(i).state == "done", "the other order: a pass already on the sha, `implemented` -> done")

    i = new("PASS_ON_ANOTHER_SHA")
    passed(i, a)
    ok("implemented", i, "--sha", b, "--none-owed")
    check(held(i), "a pass on another sha earns nothing at `implemented`")
    ok("verify", i, "--sha", a, "--level", "L0", "--result", "pass", "--config", "fixture", "--evidence", "e")
    check(held(i), "nor does one recorded after it")

    i = new("UNTAGGED_PASS")
    ok("implemented", i, "--sha", b, "--none-owed")
    ok("verify", i, "--sha", b, "--result", "pass", "--config", "fixture", "--evidence", "e")
    check(held(i), "a pass with no level finishes nothing")

    i = new("NEWER_FAIL_IMPLEMENTED")
    passed(i, b)
    ok("verify", i, "--sha", b, "--level", "L0", "--result", "fail", "--config", "fixture", "--evidence", "broke")
    ok("implemented", i, "--sha", b, "--none-owed")
    check(held(i), "a fail newer than the pass holds `implemented` too")

    i = new("REFUSED_CLOSE_SIDESTEP")
    refused("the setup: an unchecked close", "unchecked", "close", i, "--sha", b)
    ok("implemented", i, "--sha", b, "--none-owed")
    check(held(i), "a refused close is not sidestepped by `implemented --none-owed`")
    refused("nor closed from built while it holds", "unchecked", "close", i, "--sha", b)
    ok("close", i, "--no-code", "nothing to check, said out loud")
    check(item(i).state == "done" and not item(i).held, "--no-code remains the one door, and it lifts the hold")

    i = new("LEDGER_ONLY_NONE_OWED")
    refused("`implemented` at a ledger-only sha, none owed", "nothing but the ledger", "implemented", i, "--sha", led, "--none-owed")
    check(item(i).built_sha is None, "and no build is recorded")
    i = new("LEDGER_ONLY_MANIFEST")
    refused("`implemented` at a ledger-only sha, L1 owed", "nothing but the ledger", "implemented", i, "--sha", led,
            "--criteria-file", manifest(i, ("C1", "L1")))
    check(item(i).state not in ("built", "validated"), "so verify-to-done never starts from a ledger-only build")

    i = new("UNCITED", prose="Cites `design/RimMandrake/no_such_thing.md` and nothing else.\n")
    refused("`implemented` at a sha touching no cited path", "touches none", "implemented", i, "--sha", b, "--none-owed")
    ok("implemented", i, "--sha", b, "--none-owed", "--why", "the cited doc moved")
    check(held(i), "--why answers the cited paths, and only those: still unchecked")

    i = built("STALE_LAST_PASS", a, ("C1", "L1"))
    ok("implemented", i, "--sha", b, "--criteria-file", manifest(i, ("C1", "L1")))
    rc, _ = cli("verify", i, "--criterion", "C1", "--sha", a, "--result", "pass", "--config", "fixture", "--evidence", "e")
    check(item(i).state == "built" and item(i).outstanding == ["C1"], "the last criterion passing on a stale sha is no done")

    print("-- a clone's old cli: a `close` written past the cli gate is refused by the fold")
    t = "2026-11-01T19:20:%02dZ"
    x, bare = "STALE_CLI_FIXTURE", {"seat": "BENCH", "event": "close", "id": "STALE_CLI_FIXTURE", "sha": "abcdef1"}
    base = [{"seat": "BENCH", "event": "file", "ts": t % 0, "id": x, "for": "BENCH", "title": "t", "kind": "task"}]
    w = model.replay(base + [dict(bare, ts=t % 1)])
    check(w.items[x].state != "done" and w.errors, "a close with no pass on its sha reaches no done, and is reported")
    w = model.replay(base + [dict(bare, ts=t % 1, perRuling="X")])
    check(w.items[x].state != "done", "the owner's word lifts no missing check")
    w = model.replay(base + [dict(bare, ts=t % 1, noCode="a decision")])
    check(w.items[x].state == "done", "--no-code has no check to want")
    w = model.replay(base + [dict(bare, ts=model.CLOSE_FOLD_FROM.replace("19:15:00", "19:14:59"))])
    check(w.items[x].state == "done", "an event before CLOSE_FOLD_FROM replays as written")

    print("-- AU4 counts every way to done, and a thin sample is no reading")
    import close_audit
    rows = close_audit.dones(events())
    by = {r["id"]: r for r in rows}
    check({r["via"] for r in rows} == {"close", "verify", "implemented"}, "AU4 sees all three verbs (%s)"
          % sorted({r["via"] for r in rows}))
    good_row = next(r for r in rows if "PASS_THEN_IMPLEMENTED" in r["id"])
    check(good_row["via"] == "implemented" and good_row["earned"], "an earned `implemented` done counts as earned")
    t = "2026-11-01T19:00:%02dZ"
    x = "PLANTED_PROBE_FIXTURE"
    planted = [{"seat": "BENCH", "event": "file", "ts": t % 0, "id": x, "for": "BENCH", "title": "t", "kind": "task"},
               {"seat": "BENCH", "event": "close", "ts": t % 1, "id": x, "sha": "abcdef1"}]
    w, bad, code = close_audit.audit(close_audit.dones(planted), "2026-11-01T18:35:00Z")
    check(len(w) == 1 and [d["id"] for d in bad] == [x], "a done with no pass on its sha reads as unearned")
    old = "2026-10-01T00:00:%02dZ"
    legacy = [dict(e, ts=old % n) for n, e in enumerate(planted)] + \
             [{"seat": "BENCH", "event": "implemented", "ts": old % 5, "id": x + "2", "sha": "abcdef2", "criteria": []}]
    legacy.insert(2, {"seat": "BENCH", "event": "file", "ts": old % 2, "id": x + "2", "for": "BENCH", "title": "t", "kind": "task"})
    legacy.insert(3, {"seat": "BENCH", "event": "claim", "ts": old % 3, "id": x + "2"})
    rows = close_audit.dones(legacy)
    check({r["via"] for r in rows} == {"close", "implemented"} and not any(r["earned"] for r in rows),
          "the old way, `implemented` straight to done, is seen and read unearned (%d)" % len(rows))
    check(model.replay(legacy).items[x + "2"].state == "done", "and it replays as it was written")
    rules = json.load(open(close_audit.RULES, encoding="utf-8"))
    check(rules["min_sample"] >= 5 and rules["since"] == model.DONE_GATE_FROM, "AU4's window starts when this gate did, min_sample holds")
    keep = model.read
    try:
        few = events()[:6]
        model.read = lambda *a, **k: few
        tmp = os.path.join(TMP, "rules.json")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(dict(rules, since="2020-01-01", min_sample=99), f)
        close_audit.RULES, was = tmp, close_audit.RULES
        check(close_audit.main() == 2, "a window under min_sample is UNMEASURED, never IN RANGE")
        close_audit.RULES = was
    finally:
        model.read = keep


def main():
    if "--au4" in sys.argv:
        return subprocess.call([sys.executable, os.path.join(HERE, "close_audit.py")])
    try:
        new_c, old_c = commits()
        led = ledger_only()
        s1(old_c, new_c, led)
        s2(old_c, new_c)
        s3(old_c, new_c)
        s4(old_c, new_c)
        s4_relentless(old_c)
        s5_replay()
        s7_marker_fail(old_c, new_c)
        s6_every_way_to_done(old_c, new_c, led)
        before = len(events())
        check(before > 40, "the instrument saw the fixture ledger (%d events)" % before)
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("%s, %d failed" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
