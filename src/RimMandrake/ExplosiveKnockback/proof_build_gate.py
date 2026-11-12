"""Refuse to run an Explosive Knockback live proof against the RELEASE DLL.

The proof types (RM_KnockbackProof, RM_PatchApplierProbe) compile only under RM_PROOFS (csproj property RmProofs=true).
The committed and default-deployed DLL is the release build, so on it every jawa/static_call into the proof type answers
"Type not found". Without this gate a script would read that as an empty journal or a failed stage and print a table of
FAILs (or worse, a pass of nothing). Every live proof script calls require_proof_build() on its first proof call.

    from proof_build_gate import require_proof_build
    require_proof_build(first_static_call_response)      # exits 3 with PROOF_BUILD_REQUIRED when it is release
"""
import sys

PROOF_TYPE = "RimMandrake.ExplosiveKnockback.RM_KnockbackProof"
EXIT = 3
MESSAGE = ("PROOF BUILD REQUIRED: the running ExplosiveKnockback DLL has no %s (it is the release build). Build and "
           "deploy the proof build, run the proof, then put the release build back:\n"
           "  python3 src/RimMandrake/Utils/winbuild.py ExplosiveKnockback -- -p:RmProofs=true\n"
           "  python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod ExplosiveKnockback   (read the plan, then --apply)\n"
           "  ... run the proof ...\n"
           "  python3 src/RimMandrake/Utils/winbuild.py ExplosiveKnockback   (release again; never commit the proof DLL)"
           % PROOF_TYPE)


def is_release_answer(resp):
    """True when a jawa/static_call answer says the proof type is not loaded."""
    text = repr(resp)
    return "Type not found" in text and "RM_KnockbackProof" in text


def require_proof_build(resp, out=None):
    """Exit EXIT with MESSAGE when resp shows the release DLL; otherwise return resp unchanged."""
    if is_release_answer(resp):
        print(MESSAGE, file=out or sys.stderr)
        raise SystemExit(EXIT)
    return resp
