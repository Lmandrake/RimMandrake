r"""Shared by the dotnet-driven selftests: make a csproj reachable by Windows dotnet.exe.

dotnet.exe cannot build from an ext4 clone (`\wsl.localhost` UNC: obj state files unwritable,
MSB3101/MSB3030; a bare /home path converts to an invalid `\home\...`). From an ext4 clone this
stages the project through winbuild.stage_build (under D:\ClaudeWork\rimmandrake\build, or $WINBUILD_ROOT when
set) plus the whole src tree (the tests walk up from their exe to read shipped defs) and returns the
staged Windows path.

One stage per (csproj, source clone): `selftest_<csproj>_<8 hex of sha1(realpath of the clone root)>`.
The clone hash is what keeps parallel agents apart - a single stage per csproj let one clone's run
rsync --delete over another's and execute THEIR source (P-series review, 2026-10-11). Run this file
bare to check that two roots never share a stage.

Stages are never auto-pruned (~209 stages, 2.2G by 2026-10-10, and the per-clone hash multiplies
them: every throwaway clone leaves its own): prune stale ones by hand under D:\ClaudeWork\rimmandrake\build when
space matters - a `selftest_*_<hash>` dir whose clone is gone is dead. On the /mnt tree it returns the
plain D:-style path, as before.
"""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def stage_name_for(csproj, root):
    """Stage dir name for csproj built from the clone at root (unique per resolved root)."""
    base = re.sub(r"[^A-Za-z0-9_.-]", "_", os.path.splitext(os.path.basename(csproj))[0])
    tag = hashlib.sha1(os.path.realpath(root).encode("utf-8")).hexdigest()[:8]
    return "selftest_%s_%s" % (base, tag)


def windows_project_path(csproj):
    p = os.path.abspath(csproj)
    if os.path.realpath(p).startswith("/mnt/") and len(p) > 6 and p[6] == "/":
        return "%s:\\%s" % (p[5].upper(), p[7:].replace("/", "\\"))
    import winbuild
    name = stage_name_for(p, winbuild.ROOT)
    rc, record = winbuild.stage_build(p, stage_name=name,
                                    extra_dirs=[os.path.join(winbuild.ROOT, "src")])
    if rc:
        sys.exit("staged build of %s failed (rc=%d) - env/build failure, not a selftest verdict" % (p, rc))
    return winbuild.staged_win(record, p)


def _selftest():
    import tempfile
    fails = []

    def check(name, ok):
        print("%s  %s" % ("PASS" if ok else "FAIL", name))
        if not ok:
            fails.append(name)

    proj = "src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj"
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        na, nb = stage_name_for(proj, a), stage_name_for(proj, b)
        check("two clone roots get different stages (%s vs %s)" % (na, nb), na != nb)
        check("same root is stable", na == stage_name_for(proj, a + "/"))
        link = os.path.join(b, "link")
        os.symlink(a, link)
        check("a symlink to a root resolves to that root's stage", stage_name_for(proj, link) == na)
        check("one stage per csproj: other csproj, same root, differs",
              stage_name_for("x/Other.csproj", a) != na)
        check("name keeps the csproj stem and is path-safe",
              na.startswith("selftest_RimMandrakeFlowWorks.SelfTest_")
              and re.fullmatch(r"[A-Za-z0-9_.-]+", na) is not None)
    import winbuild
    check("WINBUILD_ROOT override still decides the base dir",
          winbuild.BUILD_ROOT == os.environ.get("WINBUILD_ROOT", rm_str("build")))
    print("\n%s" % ("PASS: 0 failure(s)" if not fails else "FAIL: %d failure(s)" % len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(_selftest())
