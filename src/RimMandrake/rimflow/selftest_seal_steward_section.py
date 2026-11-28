#!/usr/bin/env python3
"""selftest_seal_steward_section.py - the blind judge's sealed "Steward's decisions" stay out of its brief file.

Item RIMMANDRAKE_SEAL_STEWARD_SECTION_BLIND_JUDGE_READ_IT_FIRST; page design/specs/2026-11-28-seal-steward-section/
boundary.md (each promise has a test of its name here). The real launch_mod runs on selftest_maturation's blind fixture
with a fake detached helper. Written before the fix and watched failing on it (all four promises red at f7a9e1c71a:
the handed brief held the steward's decision), then passing. No network, no game.
  python3 selftest_seal_steward_section.py      -> one PASS/FAIL line per check; exit 1 on any FAIL
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_maturation as SM    # noqa: E402  (its fixture; importing it runs nothing)

M = SM.M
FAILS = []
MOD = "GimmeSomeSlack"
DECISION = "selftest steward decision: judge the hose bar first"
PREAMBLE = "These are the Conductor's decisions as steward"
SEALED_HEADING = "## Steward's decisions (SEALED: read only after lane 1 is committed)"   # the marker, as text
W = {}      # the world one setup() builds: root, log


def check(cond, name, detail=""):
    print("%s %s%s" % ("PASS" if cond else "FAIL", name, (": %s" % detail) if detail else ""))
    if not cond:
        FAILS.append(name)


def calls():
    with open(W["log"]) as f:
        return [json.loads(x) for x in f if x.strip()]


def setup():
    root = tempfile.mkdtemp(prefix="seal_steward_")
    SM.copy_blind(root)
    fake, log = os.path.join(root, "fake_dh.py"), os.path.join(root, "fake_dh.log")
    with open(fake, "w") as f:
        f.write(SM.FAKE_DH)
    open(log, "w").close()
    os.environ.update(MATURATION_DETACHED_HELPER=fake, FAKE_DH_LOG=log, MATURATION_CLOCK=str(SM.BLIND_CLOCK),
                      MATURATION_BRIEF_DIR=os.path.join(root, "briefs"))
    jp = os.path.join(root, "design", "concepts", MOD, "journal.md")
    with open(jp) as f:
        j = f.read()
    with open(jp, "w") as f:
        f.write(M.add_intervention(j, "- CONDUCTOR INTERVENED (stage 4+5, 2026-11-15 12:40 AM PST, kind decision): "
                                      "%s. Source: selftest." % DECISION))
    W.update(root=root, log=log)
    full, _ = M.brief_text(root, MOD)
    check(DECISION in full and PREAMBLE in full and SEALED_HEADING in full, "fixture: the steward's preview of the "
          "brief holds the sealed section and its decision")


def launched():
    """One real launch at the blind challenge -> (brief path, handed text); the first call launches, later ones reuse."""
    if "bf" not in W:
        rc, out, unit = M.launch_mod(W["root"], MOD, 20, SM.ITEM)
        c = calls()
        bf = c[0][c[0].index("--brief-file") + 1] if rc == 0 and len(c) == 1 else None
        W.update(bf=bf, rc=rc, out=out, handed=open(bf).read() if bf else "")
    return W["bf"], W["handed"]


def t_handed_holds_no_sealed_line():
    bf, handed = launched()
    check(bool(handed) and "# Blind challenge" in handed and DECISION not in handed and PREAMBLE not in handed
          and SEALED_HEADING not in handed, "handed-holds-no-sealed-line",
          "rc %s, decision in the handed brief: %s" % (W["rc"], DECISION in handed))


def t_sealed_file_named_with_its_time():
    bf, handed = launched()
    sp = (bf + ".sealed.md") if bf else ""
    sealed = open(sp).read() if sp and os.path.isfile(sp) else ""
    check(DECISION in sealed and PREAMBLE in sealed and SEALED_HEADING in sealed and sp in handed
          and "only after lane 1 is committed" in handed, "sealed-file-named-with-its-time",
          "sealed file read: %s; named in the brief: %s" % (bool(sealed), bool(sp) and sp in handed))


def t_no_section_launches_as_today():
    plain = "# Offline build (Stage 3): X 0.1.0\n\nbody\n"
    bp = os.path.join(W["root"], "briefs", "plain.md")
    try:
        got = M.seal_steward(plain, bp, expect=False)
    except AttributeError as e:
        got = "no seal_steward: %s" % e
    check(got == (plain, None) and not os.path.exists(bp + ".sealed.md"), "no-section-launches-as-today",
          repr(got)[:100])


def t_missing_marker_refuses_by_name():
    real, n0 = M.blind_brief_text, len(calls())

    def lost(root_, mod_, cap_usd=None):
        t, f = real(root_, mod_, cap_usd)
        return t.replace(SEALED_HEADING, "## Steward decisions"), f
    M.blind_brief_text = lost
    try:
        rc, out, _ = M.launch_mod(W["root"], MOD, 20, SM.ITEM + "_TWO")
    finally:
        M.blind_brief_text = real
    check(rc == 2 and len(calls()) == n0 and SEALED_HEADING in out, "missing-marker-refuses-by-name",
          "rc %s, launches %d -> %d: %s" % (rc, n0, len(calls()), out[:120]))


def main():
    keys = ("MATURATION_DETACHED_HELPER", "FAKE_DH_LOG", "MATURATION_BRIEF_DIR", "MATURATION_CLOCK")
    was = {k: os.environ.get(k) for k in keys}
    W.clear()
    try:
        was.update(SM.isolate(tempfile.mkdtemp(prefix="seal_steward_iso_")))
        setup()
        t_handed_holds_no_sealed_line()
        t_sealed_file_named_with_its_time()
        t_no_section_launches_as_today()
        t_missing_marker_refuses_by_name()
    finally:
        SM.restore(was)
        if W.get("root"):
            shutil.rmtree(W["root"], ignore_errors=True)
    print("RESULT: %s (%d check(s) failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
