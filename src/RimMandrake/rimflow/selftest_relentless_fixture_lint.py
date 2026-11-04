#!/usr/bin/env python3
"""selftest_relentless_fixture_lint.py -- an instrument repair's fixtures must be able to print the verdict line
(REPAIR_FIXTURES_ENFORCE_VERDICT_AT_FILING).

An incident releases its parents only when the repair's good/bad fixtures print `FIXTURE_VERDICT: PASS|FAIL`
(relentless_incident.check). A pair that never prints it keeps every parent waiting for good, so it is caught:
  - at attribution: a pair that names no script and has no verdict text is REFUSED; one whose script lacks the line
    (or does not exist yet) is linked and FLAGGED: alarm kind instrument_fixture_no_verdict (Operations' told ledger)
    and a note on the repair item;
  - at the repair's `finish`: refused while its open incident's fixtures still lack the line in the worker's tree;
  - at the repair's close (the release run): a run with no verdict alarms the same kind and notes the repair item.
Plus the alarm path itself: an alarm journalled with no kind no longer raises out of Effects.alarm_signal.
Driven through the REAL supervisor (relentless_attrib.answer, R.finish, R.tick); only the world is faked.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                      # noqa: E402
import relentless_attrib as A               # noqa: E402
import relentless_incident as I             # noqa: E402
import selftest_relentless as S             # noqa: E402
import selftest_relentless_attrib as SA     # noqa: E402

ok = S.ok
STEVE, BOX_FIX = SA.STEVE, SA.BOX_FIX


def alarms(x, kind):
    with open(x.s.p("journal.jsonl"), encoding="utf-8") as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    return [r for r in rows if r.get("do") == "alarm" and r.get("kind") == kind]


def t_lint(root):
    with open(os.path.join(root, "speaks.py"), "w") as f:
        f.write("print('FIXTURE_VERDICT: PASS')\n")
    with open(os.path.join(root, "mute.py"), "w") as f:
        f.write("print('ok')\n")
    os.makedirs(os.path.join(root, "t"), exist_ok=True)
    with open(os.path.join(root, "t", "deep.sh"), "w") as f:
        f.write("echo FIXTURE_VERDICT: FAIL; exit 3\n")
    cases = [
        ("python3 -c \"print('FIXTURE_VERDICT: PASS')\"", I.LINT_OK),
        ("python3 speaks.py --x", I.LINT_OK),
        ("bash t/deep.sh", I.LINT_OK),
        ("python3 tool --script=speaks.py", I.LINT_OK),
        ("python3 mute.py", I.LINT_PENDING),
        ("python3 probe.py --mounted D:", I.LINT_PENDING),
        ("true", I.LINT_NEVER),
        ("exit 1", I.LINT_NEVER),
        ("df -h D:", I.LINT_NEVER),
        ("curl -s https://example.org/x", I.LINT_NEVER),
    ]
    for cmd, want in cases:
        got, why = I.lint(cmd, root)
        ok(got == want, "lint %r -> %s (wants %s): %s" % (cmd, got, want, why))
    ok(I.lint(os.path.join(root, "speaks.py"), "/nonexistent")[0] == I.LINT_OK, "an absolute path is read as itself")
    ok(I.lint_pair({"good": "python3 speaks.py", "bad": "true"}, root)[0] == I.LINT_NEVER, "the worst of a pair wins")
    ok(I.lint_pair({"good": "python3 speaks.py", "bad": "python3 mute.py"}, root)[0] == I.LINT_PENDING,
       "pending beats ok")


def held(root):
    """STEVE held for attribution with its candidate (the attrib replay's own opening)."""
    x = SA.rig([STEVE, BOX_FIX])
    SA.checked(x, STEVE, "FAIL", "df shows 40G left on C: but the item measures D:, which this box does not mount")
    ok(x.st(STEVE)["status"] == "held", "STEVE is held for attribution: %s" % x.st(STEVE)["status"])
    return x


def answer(x, root, notes, **a):
    a.setdefault("evidence", "the deciding log line")
    return A.answer(x.s, STEVE, None, ["SITE", "CHECKER"], dict(a, repair=BOX_FIX), x.r, x.now, R,
                    known=lambda i: i in x.w.items, root=root, note=lambda i, t: notes.append((i, t)))


def t_attribution(root):
    x = held(root)
    notes = []
    try:
        answer(x, root, notes, fixture_good="true", fixture_bad="exit 1")
        ok(False, "a fixture pair that can never print the verdict is refused at attribution")
    except ValueError as e:
        ok("FIXTURE_VERDICT" in str(e) and "can never" in str(e),
           "a fixture pair that can never print the verdict is refused at attribution: %s" % str(e)[:160])
    ok(I.get(x.s, BOX_FIX) is None and x.st(STEVE)["status"] == "held" and not notes,
       "the refusal opens no incident and leaves the item held for a better attribution")
    route = answer(x, root, notes, fixture_good="python3 probe.py --mounted D:", fixture_bad="python3 probe.py --mounted Q:")
    ok(route == "wait:" + BOX_FIX, "a fixture whose script does not exist yet is linked (the repair writes it): %s" % route)
    got = alarms(x, I.NO_VERDICT)
    ok(len(got) == 1 and got[0].get("item") == BOX_FIX and got[0].get("parent") == STEVE,
       "and flagged once: an alarm of kind %s on the repair, for Operations: %s" % (I.NO_VERDICT, got))
    ok(len(notes) == 1 and notes[0][0] == BOX_FIX and "FIXTURE_VERDICT" in notes[0][1] and STEVE in notes[0][1],
       "and a note on the REPAIR item says its close owes the line: %s" % notes)
    return x


def t_repair_finish(x, root):
    """BOX_FIX, carried by Relentless, may not finish while its incident's fixtures print no verdict in its tree."""
    x.run_one(BOX_FIX)
    st = x.st(BOX_FIX)
    R.contract(x.s, BOX_FIX, st["gen"], "python3 selftest_x.py")
    try:
        R.finish(x.s, BOX_FIX, st["gen"], SA.SHA, "fixed the mount", root=root)
        ok(False, "the repair's finish is refused while its fixtures cannot give a verdict")
    except ValueError as e:
        ok("cannot give a verdict" in str(e) and STEVE in str(e) and "probe.py absent" in str(e),
           "the repair's finish is refused while its fixtures cannot give a verdict: %s" % str(e)[:200])
    ok(x.st(BOX_FIX)["status"] != "candidate", "no receipt was taken")
    with open(os.path.join(root, "probe.py"), "w") as f:
        f.write("import sys\nok = sys.argv[-1] == 'D:'\nprint('FIXTURE_VERDICT: %s' % ('PASS' if ok else 'FAIL'))\n"
                "sys.exit(0 if ok else 1)\n")
    R.finish(x.s, BOX_FIX, st["gen"], SA.SHA, "fixed the mount, probe prints its verdict", root=root)
    ok(x.st(BOX_FIX)["status"] == "candidate", "once the script prints the verdict, the finish lands")
    os.remove(os.path.join(root, "probe.py"))
    other = SA.rig(["LONE_ITEM_FINISH_FREELY"])
    other.run_one("LONE_ITEM_FINISH_FREELY")
    R.contract(other.s, "LONE_ITEM_FINISH_FREELY", 1, "python3 selftest_x.py")
    R.finish(other.s, "LONE_ITEM_FINISH_FREELY", 1, SA.SHA, "e", root=root)
    ok(other.st("LONE_ITEM_FINISH_FREELY")["status"] == "candidate", "an item that repairs no incident is never asked")


def t_release_no_verdict(root):
    """The repair closed by anyone (rimflow close): the release run prints no verdict -> alarm + a note on the repair."""
    x = held(root)
    answer(x, root, [], fixture_good=SA.GOOD, fixture_bad=SA.BAD)
    for _ in range(2):
        x.tick(3600)
    x.w.fixture_exits = {SA.GOOD: (0, "mounted"), SA.BAD: (1, "not mounted")}     # right exits, no verdict word
    x.w.close_repair(BOX_FIX, "fix1")
    x.tick()
    x.tick()
    ok(x.st(STEVE)["status"] == "blocked", "a release run with no verdict releases nothing")
    ok(len(alarms(x, I.NO_VERDICT)) == 2, "it alarms kind %s (filing + close): %d" % (I.NO_VERDICT,
                                                                                     len(alarms(x, I.NO_VERDICT))))
    ok(sum("printed no FIXTURE_VERDICT line" in n for n in x.w.notes) == 1, "and says so once on the repair item")
    x.w.fixture_exits = {SA.GOOD: (0, "FIXTURE_VERDICT: PASS"), SA.BAD: (1, "FIXTURE_VERDICT: FAIL")}
    x.w.reopen(BOX_FIX)
    x.w.close_repair(BOX_FIX, "fix2")
    x.tick()
    x.tick()
    ok(x.st(STEVE)["status"] != "blocked", "the verdict lines release it: %s" % x.st(STEVE)["status"])
    ok(len(alarms(x, "instrument_fixture_refused")) == 0, "a no-verdict refusal is not also counted as a plain one")


def t_effective_pair(root):
    """A second diagnosis on an open incident does not replace its fixtures (link keeps the first), so the lint judges
    the pair that will run, not the pair this answer typed."""
    x = held(root)
    with x.s.lock():
        I.link(x.s, BOX_FIX, "EARLIER_PARENT_ON_THE_BOX", SA.SHA, x.now, None, "e",
               {"good": "python3 speaks.py", "bad": "python3 speaks.py --bad"}, ["SITE"])
    notes = []
    route = answer(x, root, notes, fixture_good="true", fixture_bad="exit 1")
    ok(route == "wait:" + BOX_FIX and not alarms(x, I.NO_VERDICT) and not notes,
       "an open incident's speaking fixtures stand: the ignored pair is neither refused nor flagged: %s %s" % (route, notes))


def t_kindless_alarm(root):
    d = tempfile.mkdtemp(dir=root)
    old = os.environ.get("RM_OPS_WATCH_DIR")
    os.environ["RM_OPS_WATCH_DIR"] = d
    try:
        x = SA.rig([STEVE])
        fx = R.Effects(dict(x.r, ops_watch_dir=d), x.s)
        x.s.on_alarm = fx.alarm_signal
        try:
            x.s.journal({"at": "t", "do": "alarm", "item": STEVE, "why": "an alarm written before kinds"})
            fx.alarm_signal({"do": "alarm", "kind": I.NO_VERDICT, "why": "fixtures print no verdict"})
            ok(True, "an alarm with no kind no longer raises out of journal()")
        except KeyError as e:
            ok(False, "an alarm with no kind no longer raises out of journal(): KeyError %s" % e)
        p = os.path.join(d, "told.jsonl")
        rows = [json.loads(ln) for ln in open(p)] if os.path.exists(p) else []
        ok(any(r.get("kind") == I.NO_VERDICT for r in rows), "the no-verdict alarm reaches Operations' told ledger: %s"
           % [r.get("kind") for r in rows])
    finally:
        if old is None:
            os.environ.pop("RM_OPS_WATCH_DIR", None)
        else:
            os.environ["RM_OPS_WATCH_DIR"] = old


def t_attribute_cli(root):
    """The `attribute` command itself (R.main), not a hand-wired store: its flag must reach Operations' told ledger.
    Only the world is faked: the ledger lookup and the rimflow note (no books clone here); the store, the rules file and
    RM_OPS_WATCH_DIR are real paths the command reads."""
    x = held(root)
    d = tempfile.mkdtemp(dir=root)
    rules_p = os.path.join(d, "rules.json")
    with open(rules_p, "w", encoding="utf-8") as f:
        json.dump(dict(x.r, ops_watch_dir=d), f)
    saved_env = {k: os.environ.get(k) for k in ("RM_OPS_WATCH_DIR", "RELENTLESS_ROOT", "RELENTLESS_RULES")}
    saved = (R.ledger_has, R.Effects.ledger_note, os.getcwd())
    notes = []
    os.environ.update(RM_OPS_WATCH_DIR=d, RELENTLESS_ROOT=x.s.root, RELENTLESS_RULES=rules_p)
    R.ledger_has = lambda i: True
    R.Effects.ledger_note = lambda self, i, t: notes.append((i, t))
    os.chdir(d)
    try:
        R.main(["attribute", "--item", STEVE, "--seat", "--target", "SITE", "--target", "CHECKER",
                "--evidence", "the deciding log line", "--repair", BOX_FIX,
                "--fixture-good", "python3 probe.py --mounted D:", "--fixture-bad", "python3 probe.py --mounted Q:"])
    finally:
        R.ledger_has, R.Effects.ledger_note = saved[0], saved[1]
        os.chdir(saved[2])
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    ok(I.get(x.s, BOX_FIX) is not None and len(alarms(x, I.NO_VERDICT)) == 1,
       "the attribute command links the pending pair and journals one %s alarm" % I.NO_VERDICT)
    p = os.path.join(d, "told.jsonl")
    rows = [json.loads(ln) for ln in open(p)] if os.path.exists(p) else []
    ok(any(r.get("kind") == I.NO_VERDICT for r in rows),
       "the attribute command routes the no-verdict flag to Operations' told ledger: %s" % [r.get("kind") for r in rows])
    ok(any(i == BOX_FIX and "FIXTURE_VERDICT" in t for i, t in notes),
       "and its ledger note goes to the repair item: %s" % notes)


def main():
    root = tempfile.mkdtemp(prefix="fixture_lint_")
    t_lint(root)
    x = t_attribution(root)
    t_repair_finish(x, root)
    t_release_no_verdict(root)
    t_effective_pair(root)
    t_kindless_alarm(root)
    t_attribute_cli(root)
    if S.FAILS:
        print("FAIL: %d" % len(S.FAILS))
        for f in S.FAILS:
            print("FAIL " + f)
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()
