#!/usr/bin/env python3
"""Does T_NO_HOSE's scan catch the three planted faults it missed in blind cycle 3?
    python3 check_nohose_catches.py --rev <git sha>      the decider as committed at that sha
    python3 check_nohose_catches.py --rev WORKTREE       the decider in the working tree
Loads scan() from selftest_gss_no_hose.py at that revision and runs it on throwaway copies of today's mod (Defs, Patches,
Textures, Source): the clean copy must read green, and each planted copy must read red. Planted (lane2/planted_faults.json):
  NH_CALLER_HOSE_TEXTURE_LITERAL  GSS code drawing a hose texture by a path literal, no hose-named type or def
  NH_CALLER_PIPEMATS_OWN_ART      the pipe span drawn from GSS-owned art built by string concatenation
  NH_DEF_LABEL_HOSE_REEL          a ThingDef labelled "garden hose reel" under an innocent defName and texPath
Exit 0 = every planted fault caught (the fix holds); 1 = at least one missed; 2 = instrument broke."""
import argparse, importlib.util, json, os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
DEC = "src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py"
MOD = os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack")
IDS = ["NH_CALLER_HOSE_TEXTURE_LITERAL", "NH_CALLER_PIPEMATS_OWN_ART", "NH_DEF_LABEL_HOSE_REEL"]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--rev", required=True); a = ap.parse_args()
    tmpd = tempfile.mkdtemp(prefix="gss_nohose_chk_")
    try:
        src = os.path.join(tmpd, "decider.py")
        if a.rev == "WORKTREE":
            shutil.copy(os.path.join(REPO, DEC), src)
        else:
            p = subprocess.run(["git", "show", "%s:%s" % (a.rev, DEC)], cwd=REPO, capture_output=True)
            if p.returncode: print("UNMEASURED: git show failed:", p.stderr.decode()[:200]); return 2
            open(src, "wb").write(p.stdout)
        spec = importlib.util.spec_from_file_location("decider_at_rev", src); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        faults = {f["id"]: f for f in json.load(open(os.path.join(HERE, "planted_faults.json")))["faults"]}
        missed = []
        for fid in [None] + IDS:
            cp = os.path.join(tmpd, "mod_%s" % (fid or "clean"))
            for top in ("Defs", "Patches", "Textures", "Source"):
                shutil.copytree(os.path.join(MOD, top), os.path.join(cp, top), ignore=shutil.ignore_patterns("bin", "obj"))
            if fid:
                f = faults[fid]; rel = os.path.relpath(os.path.join(REPO, f["file"]), MOD); path = os.path.join(cp, rel)
                txt = open(path, encoding="utf-8").read()
                if txt.count(f["old"]) != 1: print("UNMEASURED: %s old text not unique in the copy" % fid); return 2
                open(path, "w", encoding="utf-8").write(txt.replace(f["old"], f["new"]))
            hits = mod.scan(cp)
            if fid is None:
                if hits: print("UNMEASURED: the clean copy reads red at %s: %s" % (a.rev, hits[:3])); return 2
                print("clean copy green at", a.rev)
                continue
            print("%s  %s  %s" % ("CAUGHT" if hits else "MISSED", fid, hits[:2]))
            if not hits: missed.append(fid)
        print("RESULT rev %s: %d of %d planted faults caught%s" % (a.rev, len(IDS) - len(missed), len(IDS), (", missed " + ",".join(missed)) if missed else ""))
        return 1 if missed else 0
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

if __name__ == "__main__":
    sys.exit(main())
