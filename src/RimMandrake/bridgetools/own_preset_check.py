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
# the mod whose load makes each namespace's types findable (About.xml packageIds)
NS_MOD = {"RimMandrake.GimmeSomeSlack.": "mandrake.rm.gimmesomeslack", "RimMandrake.Pyrelands.": "mandrake.rm.pyrelands"}
SRC = os.path.normpath(os.path.join(HERE, "..", ".."))


def source_types(root=SRC):
    """-> {"Ns.Type"} for every class/struct declared in a file-scoped or block namespace under src/ (top-level types)."""
    out = set()
    for d, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith(".cs"):
                continue
            try:
                t = open(os.path.join(d, f), encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            ns = re.search(r"^\s*namespace\s+([\w.]+)", t, re.M)
            if ns:
                for c in re.findall(r"\b(?:class|struct)\s+(\w+)", t):
                    out.add(ns.group(1) + "." + c)
    return out


def live_keys(keys, types):
    """-> (wanted, cut). A GSS/Pyrelands key whose type no source file declares any more (cut from the mod, e.g.
    WorldObject_RM_FurnaceHerd in 84cc81013d) can be timed by no build: it is reported as cut, not demanded."""
    want = [k for k in keys if k.startswith(WANT_NS)]
    return [k for k in want if k.split(":")[0] in types], [k for k in want if k.split(":")[0] not in types]


def reload_why(refused, running, want=None):
    """-> 'reload needed: ...' when a wanted key's type is missing because its mod is not in the running load, else None.
    That is the wrong list (SITE), which no rerun on this game can change: relentless_live restages on this line."""
    if running is None:
        return None
    absent = sorted({mod for r in (refused or []) if "type not found" in str(r)
                     if want is None or str(r).split(": ")[0] in want
                     for ns, mod in NS_MOD.items() if str(r).startswith(ns) and mod not in running})
    return ("reload needed: %s not in the running load (%d mods); preset own cannot time its types there"
            % (", ".join(absent), len(running))) if absent else None


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


def judge_live(profile, keys, cut=()):
    """-> (ok, text). profile is jawa/health_profile's `profile` after start(preset=own); keys are the wanted ones."""
    if not isinstance(profile, dict):
        return False, "no profile object"
    timed = {r.get("method") for r in (profile.get("methods") or []) if isinstance(r, dict)}
    want = [k for k in keys if k.startswith(WANT_NS)]
    gss = [k for k in want if k.startswith(WANT_NS[0])]
    pyr = [k for k in want if k.startswith(WANT_NS[1])]
    missing = [k for k in want if k not in timed]
    ok = bool(gss) and bool(pyr) and not missing and profile.get("preset") == "own"
    return ok, "preset=%s timed=%d gss=%d pyrelands=%d missing=%s cut=%s refused=%s" % (
        profile.get("preset"), len(timed), len(gss), len(pyr), missing, list(cut), profile.get("refused"))


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
    gone = "RimMandrake.Pyrelands.Gone:T"
    assert live_keys(keys + [gone], {"RimMandrake.GimmeSomeSlack.B", "RimMandrake.Pyrelands.C"}) == (keys[1:], [gone])
    refused = ["RimMandrake.GimmeSomeSlack.B:T: type not found in the running game"]
    assert reload_why(refused, ["mandrake.rm.flowworks"]).startswith("reload needed: mandrake.rm.gimmesomeslack")
    assert reload_why(refused, ["mandrake.rm.gimmesomeslack"]) is None  # loaded yet unfound is the MOD's failure
    assert reload_why(refused, None) is None
    assert reload_why(refused, ["x"], want=["RimMandrake.Pyrelands.C:T"]) is None  # a cut key never asks for a load
    real = preset_keys(open(CORE, encoding="utf-8").read())
    want, cut = live_keys(real, source_types())
    assert any(k.startswith(WANT_NS[0]) for k in want) and any(k.startswith(WANT_NS[1]) for k in want), want
    assert "RimMandrake.GimmeSomeSlack.RM_MapComponent_CordGraph:MapComponentTick" in want, want  # the scan can see
    print("SELFTEST OK (%d preset keys in source; %d GSS/Pyrelands demanded live; cut: %s)" % (len(real), len(want), cut))
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
            want, cut = live_keys(keys, source_types())
            ok, text = judge_live(prof, want, cut)
            running = None
            if not ok:
                try:
                    running = (B.call("jawa/running_mods", {}) or {}).get("packageIds")
                except Exception as e:  # a failed read is no reason to restage
                    text += " running_mods unread: %s" % e
        if not ok:
            text += " start=" + json.dumps(s, default=str)[:300]
            why = reload_why((prof or {}).get("refused") if isinstance(prof, dict) else None, running, want)
            if why:
                print("FAIL " + text)
                print(why)
                return 1
    else:
        print(__doc__)
        return 2
    print(("PASS " if ok else "FAIL ") + text)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
