#!/usr/bin/env python3
"""The release DLL carries no proof code; the proof build does (owner: "Agreed for Explosive Knockback", 2026-11-12).

RM_KnockbackProof, RM_PatchApplierProbe and the proof-only hooks compile only under RM_PROOFS (csproj RmProofs=true).
  R1  the committed Assemblies/RimMandrakeExplosiveKnockback.dll (the one deploy_custom_mods.py ships) has none of the
      proof names in its metadata #Strings heap. Sanity first: it must have RM_MapComponent_Knockback and
      RM_ThingFlyer_Knockback, so a blind read (wrong file, wrong heap) is UNMEASURED, never a pass.
  P1  a proof build (winbuild.py ... -- -p:RmProofs=true, output to a scratch folder so Assemblies/ stays release)
      has every proof name.
  D1  every name in RM_KnockbackProof.SceneNames reaches a case of its Build switch (a name with no case stages "unknown
      scene"), none listed twice.
  G1  proof_build_gate.is_release_answer reads the bridge's "Type not found" answer as release, and a real answer
      as not release: neither another type's "Type not found" nor a proof-type error is release; require_proof_build
      exits EXIT (3) on the release answer and hands a real answer back unchanged (blind cycle 3: an `or` for the `and`
      and a gate that never exits both stayed green).
Names are matched exactly (NUL on both sides): the #Strings heap is NUL-separated UTF-8, so a doc comment or a longer
name never matches.

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_proofgate.py [--no-build]
"""
import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(HERE, "..", "Utils")
sys.path.insert(0, HERE)
sys.path.insert(0, UTILS)
import io  # noqa: E402
from proof_build_gate import EXIT, is_release_answer, require_proof_build  # noqa: E402

RELEASE = os.path.join(HERE, "Assemblies", "RimMandrakeExplosiveKnockback.dll")
PROOF_NAMES = ["RM_KnockbackProof", "RM_PatchApplierProbe", "ProofSchedule", "FillToSurface", "RM_FrameProbe", "RM_KnockbackVerdicts",
               "RM_KnockbackScenes", "RMTestAttribute"]   # the jawa/run_scenes suite and its attribute (RIMMANDRAKE_BUILD_SHARED_SCENE_RUNNER_FIRST_SLICE)
SANITY = ["RM_MapComponent_Knockback", "RM_ThingFlyer_Knockback"]
PROOF_ERROR = "RimMandrake.ExplosiveKnockback.RM_KnockbackProof.Stage threw: NullReferenceException"


def strings_heap(path):
    """The #Strings heap of a .NET assembly (ECMA-335 II.24.2.2), or None when the file is not one."""
    data = open(path, "rb").read()
    i = data.find(b"BSJB")
    if i < 0:
        return None
    vlen = struct.unpack_from("<I", data, i + 12)[0]
    p = i + 16 + vlen
    nstreams = struct.unpack_from("<H", data, p + 2)[0]
    p += 4
    for _ in range(nstreams):
        off, size = struct.unpack_from("<II", data, p)
        p += 8
        end = data.index(b"\0", p)
        name = data[p:end].decode("ascii")
        p = (end + 4) & ~3
        if name == "#Strings":
            return data[i + off:i + off + size]
    return None


def has(heap, name):
    return (b"\0" + name.encode() + b"\0") in heap


def build_proof_dll():
    """Proof build into scratch (own OutputPath and obj dir): the clone's Assemblies/ is never touched."""
    root = os.environ.get("WINBUILD_ROOT", "/mnt/d/ClaudeWork/rimmandrake/build")
    out = os.path.join(root, "ExplosiveKnockbackProofGate")
    win = lambda p: "%s:\\%s" % (p[5].upper(), p[7:].replace("/", "\\"))
    dll = os.path.join(out, "RimMandrakeExplosiveKnockback.dll")
    if os.path.exists(dll):
        os.remove(dll)
    proj = os.path.join(HERE, "Source", "RimMandrake_ExplosiveKnockback.csproj")
    r = subprocess.run([sys.executable, os.path.join(UTILS, "winbuild.py"), proj, "--", "-p:RmProofs=true",
                        "-p:OutputPath=%s\\" % win(out), "-p:IntermediateOutputPath=obj\\RmProofs\\"],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=400)
    if r.returncode or not os.path.exists(dll):
        tail = "\n".join(((r.stdout or "") + (r.stderr or "")).splitlines()[-8:])
        return None, "proof build failed (%d): %s" % (r.returncode, tail)
    return dll, ""


def dispatch_faults(proof):
    """D1: every name in RM_KnockbackProof.SceneNames (what Names() hands the runner) reaches a `case` of Build, the stage
    switch; a name with no case stages "unknown scene <name>" and its bar's scene cannot run (blind challenge 0.2.0
    cycle 1: a renamed case stayed green in every decider of inv_proof_scenes). A name listed twice is a fault too.
    Returns (faults, number of names); an unreadable list or switch is a fault, never a pass."""
    m = re.search(r"SceneNames\s*=\s*\{(.*?)\};", proof, re.S)
    names = re.findall(r'"(\w+)"', re.sub(r"//[^\n]*", "", m.group(1))) if m else []
    b = re.search(r"private static string Build\(Scene s\)(.*?)return \"unknown scene \"", proof, re.S)
    if len(names) < 20 or not b:
        return ["cannot read SceneNames (%d names) or the Build switch (%s)" % (len(names), "found" if b else "missing")], len(names)
    cases = set(re.findall(r'case "(\w+)":', b.group(1)))
    faults = ["no Build case for %s" % n for n in names if n not in cases]
    faults += ["%s listed twice" % n for n in sorted({n for n in names if names.count(n) > 1})]
    return faults, len(names)


def main():
    fails, unmeasured = [], []
    heap = strings_heap(RELEASE) if os.path.exists(RELEASE) else None
    if heap is None or not all(has(heap, n) for n in SANITY):
        unmeasured.append("R1 cannot read type names in %s" % RELEASE)
    else:
        bad = [n for n in PROOF_NAMES if has(heap, n)]
        print("R1 %s release DLL proof names present: %s" % ("FAIL" if bad else "PASS", bad or "none"))
        if bad:
            fails.append("R1 committed DLL is a proof build (has %s): rebuild without -p:RmProofs=true" % bad)
    if "--no-build" in sys.argv:
        unmeasured.append("P1 skipped (--no-build)")
    else:
        dll, why = build_proof_dll()
        ph = strings_heap(dll) if dll else None
        if ph is None or not all(has(ph, n) for n in SANITY):
            unmeasured.append("P1 " + (why or "cannot read type names in the proof DLL"))
        else:
            miss = [n for n in PROOF_NAMES if not has(ph, n)]
            print("P1 %s proof DLL proof names missing: %s" % ("FAIL" if miss else "PASS", miss or "none"))
            if miss:
                fails.append("P1 proof build lacks %s" % miss)
    d_bad, d_n = dispatch_faults(open(os.path.join(HERE, "Source", "RM_KnockbackProof.cs"), encoding="utf-8").read())
    print("D1 %s proof build stages every named scene (%d names): %s" % ("FAIL" if d_bad else "PASS", d_n, d_bad or "each reaches a Build case"))
    if d_bad:
        fails.append("D1 " + "; ".join(d_bad))
    fake_release = {"success": False, "error": "Type not found: RimMandrake.ExplosiveKnockback.RM_KnockbackProof"}
    g = [is_release_answer(fake_release), not is_release_answer({"success": True, "result": "items,caps ..."}),
         not is_release_answer({"success": False, "error": "No public static Stage with 1 params."}),
         not is_release_answer({"success": False, "error": "Type not found: RimMandrake.Other.SomeProof"}),
         not is_release_answer({"success": False, "error": PROOF_ERROR})]
    try:
        require_proof_build(fake_release, out=io.StringIO())
        exited = None
    except SystemExit as e:
        exited = e.code
    real = {"success": True, "result": "items,caps ..."}
    g += [exited == EXIT == 3, require_proof_build(real) is real]
    print("G1 %s gate reads release/proof answers: %s" % ("PASS" if all(g) else "FAIL", g))
    if not all(g):
        fails.append("G1 gate misreads %s" % g)
    for f in fails:
        print("FAIL", f)
    for u in unmeasured:
        print("UNMEASURED, not a pass or a fail:", u)  # run_selftests' UNMEASURED_PHRASE
    if fails:
        return 1
    if unmeasured:
        return 2
    print("PASS proofgate (R1 P1 D1 G1)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
