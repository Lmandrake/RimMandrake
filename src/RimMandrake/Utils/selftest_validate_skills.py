#!/usr/bin/env python3
"""Selftest for skills/validate_skills.py (SKILL_VALIDATOR_FIX_CRIES_WOLF_AT_PHANTOMS).

1. A bare run over the real skills/ tree names no phantom jawa/ tool (it used to cry
   wolf on six mentions that said "this tool does not exist"; the docs were reworded).
2. The instrument can still see: a planted phantom jawa/ name in a throwaway tree is
   flagged as an ERROR and the run exits 1, while a real tool name is not flagged.
"""
import os, shutil, subprocess, sys, tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
VALIDATOR = os.path.join(REPO, "skills", "validate_skills.py")
FAILS = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def run(script, *args):
    return subprocess.run([sys.executable, script, *args], capture_output=True,
                          text=True, timeout=120)


def test_bare_run_names_no_phantom():
    r = run(VALIDATOR)
    out = r.stdout + r.stderr
    phantoms = [l for l in out.splitlines() if "NOT a real tool" in l]
    check(not phantoms, "bare run names no phantom jawa/ tool %s" % phantoms[:6])
    check("companion source declares" in out, "bare run actually read the companion source")
    check(r.returncode == 0, "bare run exits 0 (got %d)" % r.returncode)


def test_planted_phantom_is_flagged():
    tmp = tempfile.mkdtemp(prefix="selftest_validate_skills_")
    try:
        sk = os.path.join(tmp, "skills")
        os.makedirs(os.path.join(sk, "fake-skill"))
        shutil.copy(VALIDATOR, os.path.join(sk, "validate_skills.py"))
        src = os.path.join(tmp, "src", "RimMandrake", "bridgetools", "JawaBench.BridgeTools")
        os.makedirs(src)
        with open(os.path.join(src, "Tools.cs"), "w") as f:
            f.write('[Tool("jawa/real_tool")] public static void X() {}\n')
        with open(os.path.join(sk, "fake-skill", "SKILL.md"), "w") as f:
            f.write("---\nname: fake-skill\ndescription: Use when testing the validator "
                    "flags phantom tool names in a skill body.\n---\n\n"
                    "Call jawa/real_tool, then jawa/made_up_tool.\n")
        r = run(os.path.join(sk, "validate_skills.py"))
        out = r.stdout + r.stderr
        check("'jawa/made_up_tool' which is NOT a real tool" in out, "planted phantom is flagged")
        check("'jawa/real_tool' which is NOT" not in out, "real tool is not flagged")
        check(r.returncode == 1, "planted phantom makes the run exit 1 (got %d)" % r.returncode)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    test_bare_run_names_no_phantom()
    test_planted_phantom_is_flagged()
    print("FAILED %d" % len(FAILS) if FAILS else "ALL PASS")
    sys.exit(1 if FAILS else 0)
