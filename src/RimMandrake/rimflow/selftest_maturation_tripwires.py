#!/usr/bin/env python3
"""selftest_maturation_tripwires: the promises of design/specs/2026-11-19-maturation-tripwires/boundary.md, one test per
promise, each named as the promise is. T1 (RIMMANDRAKE_FLAG_NUMBER_ONLY_DIFFS_IN_MATURATION_NEXT): `next` notes a
builder diff that changes only numbers, with the item's count; T2 (RIMMANDRAKE_LIST_THINNEST_MARGINS_IN_CERTIFICATE_RUN):
`certificate --run` lists the thinnest margins first. Neither refuses. Watched failing on 09fffd6665. No game, no
network; RM_DISPATCHER_STATE points at a temp folder."""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="mat_trip_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "_dispatcher")
import maturation as M  # noqa: E402

FAILS = []
CS = "src/RimMandrake/TMod/Source/Climb.cs"


def check(ok, name, got=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def diff(path, minus, plus, ctx=("public static class Climb {",)):
    body = ["diff --git a/%s b/%s" % (path, path), "--- a/%s" % path, "+++ b/%s" % path,
            "@@ -10,%d +10,%d @@" % (len(ctx) + len(minus), len(ctx) + len(plus))]
    body += [" " + c for c in ctx] + ["-" + m for m in minus] + ["+" + p for p in plus]
    return "\n".join(body) + "\n"


NUM_A = diff(CS, ["    public const float SlopeLimit = 0.35f;"], ["    public const float SlopeLimit = 0.40f;"])
NUM_A2 = diff(CS, ["    public const float SlopeLimit = 0.40f;"], ["    public const float SlopeLimit = 0.42f;"])
NUM_OTHER = diff(CS, ["    public const int Reach = 3;"], ["    public const int Reach = 4;"])
LOGIC = diff(CS, ["        if (x > SlopeLimit) return;"], ["        if (x >= SlopeLimit) return;"])
ADDED = diff(CS, [], ["    public const float Extra = 1f;"])
XML = diff("src/RimMandrake/TMod/Defs/Things.xml", ["    <MaxSpeed>3.5</MaxSpeed>"], ["    <MaxSpeed>4</MaxSpeed>"],
           ctx=("<ThingDef>",))


def t_number_only_diff_is_named():
    f = M.number_only_constants
    check(f(NUM_A) == [CS + ":SlopeLimit"], "a diff that changes only a constant's number names it", f(NUM_A))
    check(f(LOGIC) is None, "a diff that changes an operator is not number-only", f(LOGIC))
    check(f(ADDED) is None, "a line added alone is not number-only", f(ADDED))
    check(f(XML) == ["src/RimMandrake/TMod/Defs/Things.xml:MaxSpeed"], "an XML value names its tag", f(XML))
    check(f("") == [], "an empty diff is [] (looked, nothing changed), not None", f(""))
    both = NUM_A + NUM_OTHER.split("\n", 3)[3]      # a second hunk in the same file
    check(f(both) == [CS + ":Reach", CS + ":SlopeLimit"], "two number-only hunks name both, sorted", f(both))
    check(f(NUM_A + LOGIC) is None, "one logic hunk among number hunks is not number-only", f(NUM_A + LOGIC))


def t_tripwire_counts_the_item_history():
    hist = os.path.join(TMP, "hist", "ITEM_X.jsonl")
    one = M.tripwire(NUM_A, "ITEM_X", hist)
    check(one and one["count"] == 1 and one["constants"] == [CS + ":SlopeLimit"]
          and "changes only numbers in 1 constants" in one["note"] and "has had 1 such diffs" in one["note"]
          and "Map where each bar holds before the next one." in one["note"], "a first number-only diff counts 1", one)
    again = M.tripwire(NUM_A, "ITEM_X", hist)
    check(again and again["count"] == 1, "the same diff read twice is counted once", again)
    two = M.tripwire(NUM_A2, "ITEM_X", hist)
    check(two and two["count"] == 2 and "has had 2 such diffs on the same check" in two["note"],
          "with one earlier number-only diff on the same check, the count reads 2", two)
    other = M.tripwire(NUM_OTHER, "ITEM_X", hist)
    check(other and other["count"] == 1, "a number-only diff on another constant starts its own count", other)
    n = len(open(hist).read().splitlines())
    check(M.tripwire(LOGIC, "ITEM_X", hist) is None and len(open(hist).read().splitlines()) == n,
          "a logic diff gives no note and records nothing")
    check(M.tripwire(NUM_A, "ITEM_Y", os.path.join(TMP, "hist", "ITEM_Y.jsonl"))["count"] == 1,
          "another item's history is its own")


def _next(argv, nx):
    real = M.next_step
    M.next_step = lambda root, mod: dict(nx)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            rc = M.main(argv)
    except SystemExit as e:     # argparse refusing an option is a failed check, not a dead test run
        rc = "SystemExit %s" % e.code
    finally:
        M.next_step = real
    return rc, buf.getvalue()


def t_next_prints_the_tripwire_and_never_refuses():
    nx = {"mod": "TMod", "version": "0.1.0", "stage": "offline_build", "stage_label": "Offline build", "to":
          "blind_challenge", "passed": [], "refusals": [], "hand_steps": [], "cycles": {}, "spend": {},
          "launch": "none", "next": "NEXT (hand): nothing", "may_run": {"result": "hand", "why": "fixture"},
          "tick": {"line": "dispatch tick: fixture"}}
    files = {}
    for name, d in (("num", NUM_A), ("num2", NUM_A2), ("logic", LOGIC)):
        files[name] = os.path.join(TMP, name + ".diff")
        with open(files[name], "w") as f:
            f.write(d)
    root = os.path.join(TMP, "root")
    os.makedirs(root, exist_ok=True)
    rc0, out0 = _next(["--root", root, "next", "TMod"], nx)
    rc1, out1 = _next(["--root", root, "next", "TMod", "--diff-file", files["num"], "--item", "ITEM_N"], nx)
    rc2, out2 = _next(["--root", root, "next", "TMod", "--diff-file", files["num2"], "--item", "ITEM_N"], nx)
    rc3, out3 = _next(["--root", root, "next", "TMod", "--diff-file", files["logic"], "--item", "ITEM_N"], nx)
    rc4, out4 = _next(["--root", root, "next", "TMod", "--diff-file", os.path.join(TMP, "gone.diff"), "--item",
                       "ITEM_N"], nx)
    check("this diff changes only numbers in 1 constants; this item has had 1 such diffs" in out1,
          "next prints the note for a number-only diff", out1[-300:])
    check("this item has had 2 such diffs on the same check" in out2, "the second one on the same check reads 2",
          out2[-300:])
    check("only numbers" not in out3 and "tuning tripwire" not in out3, "a logic diff prints nothing about it",
          out3[-300:])
    check("tuning tripwire: diff UNMEASURED" in out4, "an unreadable diff prints UNMEASURED, never no note", out4[-300:])
    check(rc0 == rc1 == rc2 == rc3 == rc4, "the exit code is next's own in every case", (rc0, rc1, rc2, rc3, rc4))


def t_margin_line_round_trips():
    import check_margin as CM
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        CM.line(0.101, 0.10, 36, name="slack sag")
    got = CM.parse(buf.getvalue())
    check(len(got) == 1 and got[0]["worst"] == 0.101 and got[0]["limit"] == 0.10 and got[0]["cases"] == 36
          and got[0].get("name") == "slack sag", "line then parse gives the same worst, limit and cases", got)
    check(CM.parse("MARGIN worst=abc limit=0.1 cases=3\nMARGIN worst=0.2 cases=3\nnoise") == [],
          "a non-number or a missing field is not a margin", CM.parse("MARGIN worst=abc limit=0.1 cases=3"))


def _cert_root(with_margins):
    root = os.path.join(TMP, "cert_%s" % with_margins)
    vd = os.path.join(root, "design", "concepts", "TMod", "version")
    os.makedirs(vd, exist_ok=True)
    pr = "import sys; sys.path.insert(0, %r); import check_margin as C; " % HERE

    def cmd(w, l, n):
        return "python3 -c \"%sC.line(%s, %s, %s)\"" % (pr, w, l, n) if with_margins else "python3 -c \"print('ok')\""
    tests = {"t_thin": {"id": "t_thin", "kind": "offline", "command": cmd(0.101, 0.10, 36), "file": "x.py", "reads": []},
             "t_wide": {"id": "t_wide", "kind": "offline", "command": cmd(0.48, 0.10, 4411), "file": "y.py", "reads": []},
             "t_none": {"id": "t_none", "kind": "offline", "command": "python3 -c \"print('PASS')\"", "file": "z.py",
                        "reads": []}}
    bars = [{"id": "b%d" % i, "decides": [t], "offline_decides": [t], "proves_at": "2",
             "every_decider_runnable_today": True} for i, t in enumerate(tests)]
    with open(os.path.join(vd, "test_table.json"), "w") as f:
        json.dump({"version": "0.1.0", "tests": tests, "bars": bars}, f)
    M.write_text(root, "TMod", M.RECORD, M.dump({"schema": 1, "mod": "TMod", "version": "0.1.0", "stage":
                                                    "offline_build", "cycles": {}, "moves": [], "spend": []}))
    return root


def t_certificate_run_lists_thinnest_margins_first():
    outs = {}
    for wm in (True, False):
        root = _cert_root(wm)
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                rc = M.main(["--root", root, "certificate", "TMod", "--run"])
        except SystemExit as e:
            rc = "SystemExit %s" % e.code
        tt = json.load(open(os.path.join(root, "design", "concepts", "TMod", "version", "test_table.json")))
        outs[wm] = (rc, buf.getvalue(), tt, M.certificate(root, "TMod"))
    rc, out, tt, cv = outs[True]
    lines = out.splitlines()
    thin = [i for i, x in enumerate(lines) if "t_thin" in x and "36 cases" in x]
    wide = [i for i, x in enumerate(lines) if "t_wide" in x and "4411 cases" in x]
    none = [x for x in lines if "t_none" in x and "margin not printed" in x]
    check(thin and wide and thin[0] < wide[0], "the 0.101-against-0.10 check is listed first, with '36 cases'",
          out[-600:])
    check(none, "the check that prints no margin is listed as 'margin not printed'", out[-600:])
    st = {k: (v.get("runs_today") or {}).get("margins") for k, v in tt["tests"].items()}
    check(isinstance(st["t_thin"], list) and len(st["t_thin"]) == 1 and st["t_none"] == [],
          "run_offline keeps each test's margin lines on its stamp, [] when it printed none", st)
    rc2, _, _, cv2 = outs[False]

    def verdicts(v):        # a row's `observed` quotes the test's last line, which is the margin line itself
        return [{k: x for k, x in r.items() if k != "observed"} for r in v.get("rows") or []]
    check(rc == rc2 and cv.get("ok") == cv2.get("ok") and verdicts(cv) == verdicts(cv2) and verdicts(cv),
          "the certificate's verdict and exit code are unchanged by the margin lines", (rc, rc2, cv.get("ok"),
                                                                                         cv2.get("ok")))


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    try:
        for t in (t_number_only_diff_is_named, t_tripwire_counts_the_item_history,
                  t_next_prints_the_tripwire_and_never_refuses, t_margin_line_round_trips,
                  t_certificate_run_lists_thinnest_margins_first):
            if only is not None and t.__name__ not in only:
                continue
            print("== %s" % t.__name__)
            try:
                t()
            except Exception as e:      # noqa: BLE001
                check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    if FAILS:
        print("FAILED %d: %s" % (len(FAILS), "; ".join(FAILS[:8])))
        return 1
    print("PASS selftest_maturation_tripwires")
    return 0


if __name__ == "__main__":
    sys.exit(main())
