#!/usr/bin/env python3
"""selftest_seal_steward_section.py - the blind judge's sealed "Steward's decisions" stay out of its brief file.

Item RIMMANDRAKE_SEAL_STEWARD_SECTION_BLIND_JUDGE_READ_IT_FIRST; page design/specs/2026-11-28-seal-steward-section/
boundary.md. The real launch_mod runs on selftest_maturation's blind fixture with a fake detached helper. Written before
the fix and watched failing on it (case handed_holds_no_sealed_line), then passing. No network, no game.
  python3 selftest_seal_steward_section.py      -> one PASS/FAIL line per case; exit 1 on any FAIL
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


def check(cond, name, detail=""):
    print("%s %s%s" % ("PASS" if cond else "FAIL", name, (": %s" % detail) if detail else ""))
    if not cond:
        FAILS.append(name)


def main():
    root = tempfile.mkdtemp(prefix="seal_steward_")
    keys = ("MATURATION_DETACHED_HELPER", "FAKE_DH_LOG", "MATURATION_BRIEF_DIR", "MATURATION_CLOCK")
    was = {k: os.environ.get(k) for k in keys}
    was.update(SM.isolate(root))
    try:
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

        def calls():
            with open(log) as f:
                return [json.loads(x) for x in f if x.strip()]

        full, _ = M.brief_text(root, MOD)
        check(DECISION in full and PREAMBLE in full, "fixture_carries_a_decision",
              "the steward's preview of the brief holds the sealed section")

        # handed_holds_no_sealed_line + sealed_file_named_with_its_time: one real launch at the blind challenge
        rc, out, unit = M.launch_mod(root, MOD, 20, SM.ITEM)
        c = calls()
        bf = c[0][c[0].index("--brief-file") + 1] if rc == 0 and len(c) == 1 else None
        handed = open(bf).read() if bf else ""
        check(bool(handed) and "# Blind challenge" in handed and DECISION not in handed and PREAMBLE not in handed
              and "(SEALED: read only after lane 1 is committed)" not in handed,
              "handed_holds_no_sealed_line", "rc %s, %d call(s), decision in handed %s" % (
                  rc, len(c), DECISION in handed))
        sp = (bf + ".sealed.md") if bf else ""
        sealed = open(sp).read() if sp and os.path.isfile(sp) else ""
        check(DECISION in sealed and PREAMBLE in sealed and sp in handed and "after lane 1 is committed" in handed,
              "sealed_file_named_with_its_time", "sealed file %s, named in the brief %s" % (
                  bool(sealed), bool(sp) and sp in handed))

        # no_section_launches_as_today: a text with no sealed section, none expected, passes unchanged
        seal = getattr(M, "seal_steward", None)
        plain = "# Offline build (Stage 3): X 0.1.0\n\nbody\n"
        got = seal(plain, os.path.join(root, "briefs", "plain.md"), expect=False) if seal else None
        check(got == (plain, None) and not os.path.exists(os.path.join(root, "briefs", "plain.md.sealed.md")),
              "no_section_launches_as_today", "seal_steward %s" % ("missing" if not seal else repr(got)[:80]))

        # missing_marker_refuses_by_name: at the blind challenge, a brief that lost its marker never launches whole
        real = M.blind_brief_text
        n0 = len(calls())
        try:
            def lost(root_, mod_, cap_usd=None):
                t, f = real(root_, mod_, cap_usd)
                return t.replace(M.SEAL_MARK if hasattr(M, "SEAL_MARK") else "## Steward's decisions (SEALED",
                                 "## Steward decisions"), f
            M.blind_brief_text = lost
            rc2, out2, _ = M.launch_mod(root, MOD, 20, SM.ITEM + "_TWO")
        finally:
            M.blind_brief_text = real
        check(rc2 == 2 and len(calls()) == n0 and hasattr(M, "SEAL_MARK") and M.SEAL_MARK in out2,
              "missing_marker_refuses_by_name", "rc %s, calls %d -> %d, %s" % (rc2, n0, len(calls()), out2[:120]))
    finally:
        SM.restore(was)
        shutil.rmtree(root, ignore_errors=True)
    print("RESULT: %s (%d case(s) failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
