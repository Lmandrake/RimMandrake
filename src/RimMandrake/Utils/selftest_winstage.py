"""Shared by the dotnet-driven selftests: make a csproj reachable by Windows dotnet.exe.

dotnet.exe cannot build from an ext4 clone (`\\wsl.localhost` UNC: obj state files unwritable,
MSB3101/MSB3030; a bare /home path converts to an invalid `\home\...`). From an ext4 clone this
stages the project through winbuild.stage_build (under D:\Luke\dev\_rmbuild, one stage per
csproj so parallel selftests never rsync --delete over each other) plus the whole src tree (the tests walk up from their exe to read
shipped defs) and returns the staged Windows path.
Stages are never auto-pruned (~209 stages, 2.2G by 2026-10-10): prune stale ones by hand under D:\\Luke\\dev\\_rmbuild when space matters. On the /mnt tree it returns the plain D:-style path, as before.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def windows_project_path(csproj):
    p = os.path.abspath(csproj)
    if os.path.realpath(p).startswith("/mnt/") and len(p) > 6 and p[6] == "/":
        return "%s:\\%s" % (p[5].upper(), p[7:].replace("/", "\\"))
    import winbuild
    name = "selftest_" + re.sub(r"[^A-Za-z0-9_.-]", "_", os.path.splitext(os.path.basename(p))[0])
    rc, record = winbuild.stage_build(p, stage_name=name,
                                    extra_dirs=[os.path.join(winbuild.ROOT, "src")])
    if rc:
        sys.exit("staged build of %s failed (rc=%d) - env/build failure, not a selftest verdict" % (p, rc))
    return winbuild.staged_win(record, p)
