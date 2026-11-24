#!/usr/bin/env python3
"""live_tools_units.py - build and run bridgetools/LiveToolsSelfTest (the PRODUCTION Core files of the loaded-build receipt,
the calm map and the first-exception tap; net8.0, no game) and give the unit results to the three page selftests:
selftest_loaded_receipt.py, selftest_calm_core.py, selftest_first_exception_core.py.

`units(plant)` -> {"group.name": True|False}. Raises Unmeasured when the harness could not be built or did not run whole:
an empty result is never a pass."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE) if HERE not in sys.path else None
_DLL = [None]
MIN_UNITS = 70                  # a harness that printed fewer did not run whole


class Unmeasured(Exception):
    pass


def dll():
    if _DLL[0] is None:
        import winbuild
        proj = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "LiveToolsSelfTest")
        try:
            rc, rec = winbuild.stage_build(os.path.join(proj, "LiveToolsSelfTest.csproj"), stage_name="LiveToolsSelfTest")
        except (OSError, SystemExit) as e:
            raise Unmeasured("the harness could not be built: %s" % e)
        if rc:
            raise Unmeasured("the harness build failed (rc %s)" % rc)
        _DLL[0] = winbuild.staged_win(rec, proj) + "\\bin\\Release\\net8.0\\LiveToolsSelfTest.dll"
    return _DLL[0]


def run(*args, plant=""):
    import winbuild
    env = dict(os.environ, RM_PLANT=plant)
    env["WSLENV"] = (env.get("WSLENV", "") + ":RM_PLANT").strip(":")
    return winbuild.run_interop_captured([winbuild.dotnet_exe(), dll()] + list(args), capture_output=True, text=True,
                                         cwd="/mnt/d/Luke/dev", env=env)


def units(plant=""):
    p = run(plant=plant)
    out = {}
    for ln in p.stdout.splitlines():
        if ln.startswith("U "):
            name, _, rest = ln[2:].strip().partition(" ")
            out[name] = rest.startswith("ok")
    count = [ln for ln in p.stdout.splitlines() if ln.startswith("U-count ")]
    want = int(count[0].split()[1]) if count else -1
    if want != len(out) or want < MIN_UNITS:
        raise Unmeasured("printed %d units, declared %s (expected at least %d): %s" % (len(out), want, MIN_UNITS, p.stderr[-400:]))  # cut-ok: exception message
    return out


def group(g, plants, say=print):
    """-> True when every unit of group g passes clean, and each planted fault turns at least one of them red."""
    clean = dict((n, ok) for n, ok in units().items() if n.startswith(g + "."))
    bad = sorted(n for n, ok in clean.items() if not ok)
    say("%s  %s: %d units%s" % ("ok  " if clean and not bad else "FAIL", g, len(clean), "" if not bad else ", red: %s" % bad))
    good = bool(clean) and not bad
    for pl in plants:
        red = sorted(n for n, ok in units(pl).items() if not ok)
        hit = [n for n in red if n.startswith(g + ".")]
        say("%s  %s: planted fault %r turns red: %s" % ("ok  " if hit else "FAIL", g, pl, hit))
        good = good and bool(hit)
    return good
