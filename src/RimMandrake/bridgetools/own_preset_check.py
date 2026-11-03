#!/usr/bin/env python3
"""own_preset_check.py - is jawa/health_profile's preset "own" (GSS + Pyrelands, 53595b2d45) really in the game?

OWN_PRESET_WIDEN_PYRELANDS_JOINS_IN. The preset is the OwnPreset constant in
JawaBench.BridgeTools/JawaBenchHealthCore.cs; the exc window's `repTop` is in JawaBenchTpsTierCore.cs.

  python3 own_preset_check.py --self-test   # the pure judge, on fixtures
  python3 own_preset_check.py --dll [PATH]  # offline: the DEPLOYED companion holds every preset key + repTop
  python.exe own_preset_check.py --live     # live (bridge held by caller): start preset=own for 1 minute,
                                            # read status, stop; every GSS and Pyrelands key must be TIMED
                                            # (in `methods`, not `refused`), so GimmeSomeSlack + Pyrelands must be loaded

Exit 0 iff the claim holds, 1 if not. A .NET string literal is UTF-16LE in the #US heap: an ASCII grep of the DLL
sees nothing (the trap that makes a byte grep read 0).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORE = os.path.join(HERE, "JawaBench.BridgeTools", "JawaBenchHealthCore.cs")
GAME_DLL = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/BridgeTools/JawaBench/JawaBench.BridgeTools.dll"
WANT_NS = ("RimMandrake.GimmeSomeSlack.", "RimMandrake.Pyrelands.")


def preset_keys(src):
    """The OwnPreset constant's 'Ns.Type:Method' keys, in order, from the C# source text."""
    m = re.search(r'OwnPreset\s*=\s*((?:\s*"[^"]*"\s*\+?)+);', src)
    if not m:
        raise SystemExit("OwnPreset constant not found in %s" % CORE)
    joined = "".join(re.findall(r'"([^"]*)"', m.group(1)))
    return [k for k in joined.split(";") if k]


def judge_dll(blob, keys):
    """-> (ok, text). The preset is ONE literal (C# folds the + chain), so the whole joined string must be present."""
    whole = ";".join(keys).encode("utf-16-le")
    missing = [k for k in keys if k.encode("utf-16-le") not in blob]
    rep = "repTop".encode("utf-16-le") in blob
    ok = not missing and whole in blob and rep
    return ok, "keys=%d missing=%s wholePreset=%s repTop=%s" % (len(keys), missing, whole in blob, rep)


def judge_live(profile, keys):
    """-> (ok, text). profile is jawa/health_profile's `profile` after start(preset=own)."""
    if not isinstance(profile, dict):
        return False, "no profile object"
    timed = {r.get("method") for r in (profile.get("methods") or []) if isinstance(r, dict)}
    want = [k for k in keys if k.startswith(WANT_NS)]
    gss = [k for k in want if k.startswith(WANT_NS[0])]
    pyr = [k for k in want if k.startswith(WANT_NS[1])]
    missing = [k for k in want if k not in timed]
    ok = bool(gss) and bool(pyr) and not missing and profile.get("preset") == "own"
    return ok, "preset=%s timed=%d gss=%d pyrelands=%d missing=%s refused=%s" % (
        profile.get("preset"), len(timed), len(gss), len(pyr), missing, profile.get("refused"))


def self_test():
    keys = ["RimMandrake.FlowWorks.A:T", "RimMandrake.GimmeSomeSlack.B:T", "RimMandrake.Pyrelands.C:T"]
    good = {"preset": "own", "methods": [{"method": k} for k in keys], "refused": []}
    assert judge_live(good, keys)[0]
    assert not judge_live(dict(good, methods=good["methods"][:2], refused=[keys[2]]), keys)[0]
    assert not judge_live(dict(good, preset=None), keys)[0]
    assert not judge_live(None, keys)[0]
    blob = b"x" + ";".join(keys).encode("utf-16-le") + "repTop".encode("utf-16-le")
    assert judge_dll(blob, keys)[0]
    assert not judge_dll(blob.replace("repTop".encode("utf-16-le"), b""), keys)[0]
    assert not judge_dll(";".join(keys).encode(), keys)[0]  # ASCII is not what a .NET literal looks like
    real = preset_keys(open(CORE, encoding="utf-8").read())
    assert any(k.startswith(WANT_NS[0]) for k in real) and any(k.startswith(WANT_NS[1]) for k in real), real
    print("SELFTEST OK (%d preset keys in source)" % len(real))
    return 0


def main(argv):
    keys = preset_keys(open(CORE, encoding="utf-8").read())
    if not argv or argv[0] == "--self-test":
        return self_test()
    if argv[0] == "--dll":
        path = argv[1] if len(argv) > 1 else GAME_DLL
        ok, text = judge_dll(open(path, "rb").read(), keys)
    elif argv[0] == "--live":
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
        from rimbridge_client import RimBridge, resolve_endpoint
        h, p, t = resolve_endpoint()
        with RimBridge(h, p, t, timeout=120.0) as B:
            B.call("jawa/health_profile", {"action": "stop"})
            s = B.call("jawa/health_profile", {"action": "start", "preset": "own", "minutes": 1}) or {}
            r = B.call("jawa/health_profile", {"action": "status"}) or {}
            B.call("jawa/health_profile", {"action": "stop"})
        prof = r.get("profile") or s.get("profile")
        ok, text = judge_live(prof, keys)
        if not ok:
            text += " start=" + json.dumps(s, default=str)[:300]
    else:
        print(__doc__)
        return 2
    print(("PASS " if ok else "FAIL ") + text)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
