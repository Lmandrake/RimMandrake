#!/usr/bin/env python3
"""selftest_steve_worker_proof_site.py - an exact-tier proofs job runs each clause's site before its proof.

Page: design/specs/2026-11-26-lane-proofs-site/boundary.md (each promise has a test of its name here). The fault:
J20261126T185703Z-949b32 (PLAYER_START_SITE_1 A1, 2026-11-26) loaded the tier, the game stayed on the main menu, and
the proof, which reads a map, recorded FAIL. The retired live stage ran each clause's site first (rimflow/proof_lines.site_for);
the lane's worker did not.

  python3 infrastructure/stevedesktop/selftest_steve_worker_proof_site.py      exit 1 on any failure
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.pop("TESTQ_CMD_SITE", None)
import worker as W  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def t_default_site_lifts_the_colony_guard():
    got = W.proof_site("live-proof A1: python.exe x.py A1", "A1")
    check(got == "python.exe src/RimMandrake/Utils/live_site.py --game --max-ticks %d" % W.SITE_ANY_AGE
          and W.SITE_ANY_AGE >= 10 ** 8,
          "a clause with no site line gets live_site --game, its colony guard lifted (every lane game is a test "
          "game): %r" % got)


def t_own_site_line_wins():
    text = "live-site A1: python.exe src/RimMandrake/Utils/live_site.py --biome RM_Stillsand\nlive-proof A1: x\n"
    got = W.proof_site(text, "A1")
    check(got == "python.exe src/RimMandrake/Utils/live_site.py --biome RM_Stillsand",
          "the clause's own live-site line is its site: %r" % got)


def t_menu_file_takes_no_site():
    got = W.proof_site("live-menu: python.exe m.py\nlive-proof A1: x\n", "A1")
    check(got is None, "a file whose proofs want the main menu gets no site: %r" % got)


def t_site_runs_before_its_proof_and_a_failed_site_runs_no_proof():
    r = subprocess.run([sys.executable, os.path.join(HERE, "selftest_steve_worker_tier.py")], capture_output=True,
                       text=True, timeout=900)   # budget: danger=a hung worker harness; evidence=a hang guard only; longest=4s (one measured run, 2026-11-26)
    out = r.stdout
    check(r.returncode == 0 and "ok    each clause's site runs before its proof" in out
          and "ok    a site that did not stand runs no proof" in out,
          "on the worker's harness each site runs before its proof, and a site that did not stand runs no proof "
          "(selftest_steve_worker_tier.py): %s" % out[-400:])


def main():
    t_default_site_lifts_the_colony_guard()
    t_own_site_line_wins()
    t_menu_file_takes_no_site()
    t_site_runs_before_its_proof_and_a_failed_site_runs_no_proof()
    print("selftest_steve_worker_proof_site: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
