#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_PREVIEW_THREE_GATES_READ_ONLY_FOR_LAUNCH_CHECKS (DESIGN DECISION 2026-11-18 on
RIMMANDRAKE_ADD_LAUNCH_CHECKS_EXAM_CERTIFY_JUDGE_THREE_UNCAUGHT): a launch check reads the gate's OWN decision function
through a read-only flag, never a second copy of its rules. Exit 0 = the gate would open, 1 = it would refuse (the
gate's own words printed), 126 = could not look (launch_checks.py reads 126 as "did not run", never a refusal).
  designer_stage.py open <dir> --run <any> --preview        open_run(..., commit=False)
  coverage_judge.py status <dir> --would-judge              plan(d)[0] == "judge"
  concept_tree.py certify <dir> --owner-event OWNER:<tsn> --check    certify's checks; no stamp, no ledger note
  launch_checks.block_for("designer_open"|"coverage_judge", mod=...), block_for("certify", mod=..., owner_event=...)
Red on 0117263cc (watched)."""
import contextlib
import hashlib
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import concept_tree as CT  # noqa: E402
import coverage_judge as CJ  # noqa: E402
import designer_stage as DS  # noqa: E402
import launch_checks as LC  # noqa: E402

FAILS = []
REAL = os.path.join(ROOT, "design", "concepts", "ExplosiveKnockback")       # a real concept: the mod owns its lock state


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


def tree_sha(d):
    h = hashlib.sha256()
    for base, dirs, files in sorted(os.walk(d)):
        dirs.sort()
        for f in sorted(files):
            p = os.path.join(base, f)
            h.update(p.encode())
            with open(p, "rb") as fh:
                h.update(fh.read())
    return h.hexdigest()


def call(mod, argv):
    """-> (exit code, output); argparse's own exit (an unknown flag is 2) comes back as "ARGPARSE <code>"."""
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = mod.main(argv)
    except SystemExit as e:
        return "ARGPARSE %s" % e.code, out.getvalue()
    except Exception as e:
        return "CRASH %s: %s" % (type(e).__name__, e), out.getvalue()
    return rc, out.getvalue()


def patched(mod, name, fn):
    @contextlib.contextmanager
    def cm():
        old = getattr(mod, name)
        setattr(mod, name, fn)
        try:
            yield
        finally:
            setattr(mod, name, old)
    return cm()


def main():
    if not os.path.isfile(os.path.join(REAL, "stage.json")):
        print("UNMEASURED: %s has no stage.json in this clone" % REAL)
        return 2
    before = tree_sha(REAL)
    ledger = os.path.join(ROOT, "infrastructure", "state", "ledger", "events")
    ledger_before = tree_sha(ledger)

    # ---- the Designer's open gate
    seen = {}

    def opens(d, run, run_cap=None, *a, **k):
        seen.update(k, n=seen.get("n", 0) + 1)
        return "packet text", 1000

    def refuses(d, run, run_cap=None, *a, **k):
        raise DS.Refused("the concept is locked")

    def blind(d, run, run_cap=None, *a, **k):
        raise OSError("stage.json unreadable")
    with patched(DS, "open_run", opens):
        rc, out = call(DS, ["open", REAL, "--run", "launch-check", "--preview"])
    check("designer open --preview: exit 0 when open_run would open", rc == 0, (rc, out[-200:]))
    check("designer open --preview: asks open_run with commit=False", seen.get("commit") is False, seen)
    check("designer open --preview: prints no packet", "packet text" not in out, out[-200:])
    with patched(DS, "open_run", refuses):
        rc, out = call(DS, ["open", REAL, "--run", "launch-check", "--preview"])
    check("designer open --preview: exit 1 with the gate's words when it refuses",
          rc == 1 and "the concept is locked" in out, (rc, out[-200:]))
    with patched(DS, "open_run", blind):
        rc, out = call(DS, ["open", REAL, "--run", "launch-check", "--preview"])
    check("designer open --preview: exit 126 when it could not look", rc == 126, (rc, out[-200:]))
    # the real concept, with no patch: the preview gives the answer of the open gate itself. Whether that concept is
    # locked is the state of the mod, which changes (it opened on 2026-11-24 and this row, which assumed "locked", went
    # red on every publish)
    try:
        DS.open_run(REAL, "launch-check", None, commit=False)
        want = 0
    except DS.Refused:
        want = 1
    rc, out = call(DS, ["open", REAL, "--run", "launch-check", "--preview"])
    check("designer open --preview: the real concept gets the answer of the open gate itself (exit %d now)" % want,
          rc == want, (rc, out[-200:]))
    rc, out = call(DS, ["open", os.path.join(ROOT, "design", "concepts", "NoSuchConceptHere"), "--run", "x", "--preview"])
    check("designer open --preview: a concept folder that does not exist is exit 1 or 126, never 0",
          rc in (1, 126), (rc, out[-200:]))

    # ---- the coverage judge
    for what, want in (("judge", 0), ("skip", 1), ("stopped", 1), ("parked", 1), ("ceiling", 1), ("error", 126)):
        with patched(CJ, "plan", lambda d, repo=None, what=what: (what, "why-%s" % what)):
            rc, out = call(CJ, ["status", REAL, "--would-judge"])
        check("coverage_judge status --would-judge: plan %r is exit %d, its reason printed" % (what, want),
              rc == want and "why-%s" % what in out, (rc, out[-200:]))
    rc, out = call(CJ, ["status", REAL, "--would-judge"])
    check("coverage_judge status --would-judge: the real locked concept is exit 1", rc == 1, (rc, out[-200:]))
    rc, out = call(CJ, ["status", REAL])
    check("coverage_judge status without the flag still exits 0 on a readable concept", rc == 0, (rc, out[-200:]))

    # ---- certify
    notes = []
    with patched(CT, "rimflow_note", lambda *a, **k: notes.append(a) or None):
        rc, out = call(CT, ["certify", REAL, "--owner-event", "OWNER:999999", "--check"])
    check("concept_tree certify --check: an event that is not his refuses (exit 1)", rc == 1, (rc, out[-300:]))
    check("concept_tree certify --check: writes no ledger note", notes == [], notes)
    with patched(CT, "certify", lambda d, owner_event, repo=CT.REPO, emit=None, **k: [] if k.get("check") else ["STAMPED"]):
        rc, out = call(CT, ["certify", REAL, "--owner-event", "OWNER:1", "--check"])
    check("concept_tree certify --check: exit 0 when certify(check=True) finds nothing", rc == 0, (rc, out[-200:]))

    # ---- nothing above wrote anything
    check("the concept folder is byte-identical after every preview", tree_sha(REAL) == before)
    check("the ledger shards are byte-identical after every preview", tree_sha(ledger) == ledger_before)

    # ---- the blocks a filer writes
    def block(kind, **k):
        try:
            return LC.block_for(kind, **k)
        except Exception as e:
            return "CRASH %s: %s" % (type(e).__name__, e)
    b = block("designer_open", mod="Foo")
    check("block_for designer_open", b == "%s\nmust-pass: python3 src/RimMandrake/rimflow/designer_stage.py open "
          "design/concepts/Foo --run launch-check --preview\n" % LC.HEAD, b)
    b = block("coverage_judge", mod="Foo")
    check("block_for coverage_judge", b == "%s\nmust-pass: python3 src/RimMandrake/rimflow/coverage_judge.py status "
          "design/concepts/Foo --would-judge\n" % LC.HEAD, b)
    b = block("certify", mod="Foo", owner_event="OWNER:123")
    check("block_for certify", b == "%s\nmust-pass: python3 src/RimMandrake/rimflow/concept_tree.py certify "
          "design/concepts/Foo --owner-event OWNER:123 --check\n" % LC.HEAD, b)
    for kind, kw in (("designer_open", {}), ("coverage_judge", {"mod": ""}), ("certify", {"mod": "Foo"}),
                     ("certify", {"mod": "Foo", "owner_event": "123"}), ("designer_open", {"mod": "../x"})):
        b = block(kind, **kw)
        check("block_for %s %r raises ValueError, writes no half block" % (kind, kw),
              isinstance(b, str) and b.startswith("CRASH ValueError"), b)
    for b in (block("designer_open", mod="Foo"), block("coverage_judge", mod="Foo")):
        ok = not b.startswith("CRASH") and [c["kind"] for c in LC.parse(b)] == ["must-pass"]
        check("launch_checks.parse reads the block as one must-pass", ok, b)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
