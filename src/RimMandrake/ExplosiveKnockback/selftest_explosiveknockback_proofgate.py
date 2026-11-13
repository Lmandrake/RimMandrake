#!/usr/bin/env python3
"""The release DLL carries no proof code; the proof build does (owner: "Agreed for Explosive Knockback", 2026-11-12).

RM_KnockbackProof, RM_PatchApplierProbe and the proof-only hooks compile only under RM_PROOFS (csproj RmProofs=true).
  R1  the committed Assemblies/RimMandrakeExplosiveKnockback.dll (the one deploy_custom_mods.py ships) has none of the
      proof names in its metadata #Strings heap. Sanity first: it must have RM_MapComponent_Knockback and
      RM_ThingFlyer_Knockback, so a blind read (wrong file, wrong heap) is UNMEASURED, never a pass.
  P1  a proof build (winbuild.py ... -- -p:RmProofs=true, output to a scratch folder so Assemblies/ stays release)
      has every proof name.
  G1  proof_build_gate.is_release_answer reads the bridge's "Type not found" answer as release, and a real answer
      as not release.
Names are matched exactly (NUL on both sides): the #Strings heap is NUL-separated UTF-8, so a doc comment or a longer
name never matches.

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_proofgate.py [--no-build]
"""
# selftest-timeout: 420
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(HERE, "..", "Utils")
sys.path.insert(0, HERE)
sys.path.insert(0, UTILS)
from proof_build_gate import is_release_answer  # noqa: E402

RELEASE = os.path.join(HERE, "Assemblies", "RimMandrakeExplosiveKnockback.dll")
PROOF_NAMES = ["RM_KnockbackProof", "RM_PatchApplierProbe", "ProofSchedule", "FillToSurface"]
SANITY = ["RM_MapComponent_Knockback", "RM_ThingFlyer_Knockback"]


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
    fake_release = {"success": False, "error": "Type not found: RimMandrake.ExplosiveKnockback.RM_KnockbackProof"}
    g = [is_release_answer(fake_release), not is_release_answer({"success": True, "result": "items,caps ..."}),
         not is_release_answer({"success": False, "error": "No public static Stage with 1 params."})]
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
    print("PASS proofgate (R1 P1 G1)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
