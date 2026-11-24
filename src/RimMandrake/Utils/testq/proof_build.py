#!/usr/bin/env python3
"""testq/proof_build.py - put a mod's PROOF build into this machine's game for one test job (the worker's deploy phase, the
game down). RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE; page design/specs/2026-11-24-stage-six-checks-to-steve/.

  proof_build.py --mod ExplosiveKnockback --mods-dir <game>/Mods

Builds the mod's csproj with -p:RmProofs=true in its own Windows stage (winbuild, stage <Mod>_proof), copies nothing back
into the clone, and copies the DLL and its .srchash over the deployed release in <game>/Mods/<Mod>/Assemblies. A proof DLL
is never committed. The next job's deploy plan sees the drift and puts the release back. Exit 0 done; 2 build failed or
wrote no DLL; 3 the mod is not deployed there; 4 the csproj has no RmProofs switch; 5 the clone's Assemblies changed."""
import argparse
import glob
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
SWITCH = "-p:RmProofs=true"


def tree_hash(folder):
    out = {}
    for p in sorted(glob.glob(os.path.join(folder, "**", "*"), recursive=True)):
        if os.path.isfile(p):
            with open(p, "rb") as f:
                out[os.path.relpath(p, folder)] = hashlib.sha256(f.read()).hexdigest()
    return out


def build(mod, root, WB=None):
    """-> ([built DLL path in the stage], None) or ([], why). WB: a winbuild stand-in (the selftest's)."""
    if WB is None:
        sys.path.insert(0, UTILS)
        import winbuild as WB
    csproj = WB.find_csproj(mod)
    with open(csproj, encoding="utf-8-sig") as f:
        if "RmProofs" not in f.read():
            return [], "no RmProofs switch in %s" % csproj
    WB._copy_back = lambda outs, stage, record, staged_in=None: record["outputs"].extend(
        os.path.relpath(p, stage) for p in sorted(outs))        # the stage keeps the proof DLL; the clone never sees it
    rc, rec = WB.stage_build(csproj, "Release", [SWITCH], stage_name=mod + "_proof")
    if rc != 0:
        return [], "the build failed (exit %s)" % rc
    want = "src/RimMandrake/%s/Assemblies/" % mod
    dlls = [os.path.join(rec["stage"], o) for o in rec["outputs"]
            if o.endswith(".dll") and o.replace(os.sep, "/").startswith(want)]
    return (dlls, None) if dlls else ([], "the build wrote no DLL under %s" % want)


def place(dlls, mod, mods_dir):
    """-> [deployed path], or raises FileNotFoundError when the release is not deployed there."""
    out = []
    for d in dlls:
        dst = os.path.join(mods_dir, mod, "Assemblies", os.path.basename(d))
        if not os.path.isfile(dst):
            raise FileNotFoundError(dst)
        for a, b in ((d, dst), (d + ".srchash", dst + ".srchash")):
            if os.path.isfile(a):
                shutil.copyfile(a, b)
                out.append(b)
    return out


def main(argv=None, WB=None, root=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mod", required=True)
    ap.add_argument("--mods-dir", required=True)
    a = ap.parse_args(argv)
    root = root or os.path.abspath(os.path.join(UTILS, "..", "..", ".."))
    asm = os.path.join(root, "src", "RimMandrake", a.mod, "Assemblies")
    before = tree_hash(asm)
    dlls, why = build(a.mod, root, WB)
    if tree_hash(asm) != before:
        print("REFUSED: the proof build changed the clone's %s" % asm)
        return 5
    if why:
        print("NOT BUILT: %s" % why)
        return 4 if "RmProofs" in why else 2
    try:
        done = place(dlls, a.mod, a.mods_dir)
    except OSError as e:
        print("NOT PLACED: %s: %s (the release must be deployed first)" % (type(e).__name__, e))
        return 3
    print("PROOF BUILD of %s in the game: %s" % (a.mod, ", ".join(done)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
