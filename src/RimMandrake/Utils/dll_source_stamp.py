#!/usr/bin/env python3
"""dll_source_stamp.py — verify a committed mod DLL against its committed C# sources.

WHY (DLL_SOURCE_STAMP_GUARD_1): 80 built DLLs are committed under
src/**/Assemblies/. A binary DLL can't merge, so a conflict on one is usually
resolved by keeping one branch's DLL — silently dropping the other branch's
C# from the build (measured 2026-09-25: five merges that day each carried a
stale/rebuilt RimMandrake.CreatureBehaviors.dll).

src/Directory.Build.targets now writes a `<dll>.srchash` sidecar next to every
DLL it builds (SHA256 of every @(Compile) item, one line each, sorted, plus a
"# project: <csproj path relative to src/>" header). This script recomputes
those hashes from COMMITTED git blobs (never the worktree — a worktree file
can be edited without being committed, which would hide exactly the defect
this guards against) and reports where a committed DLL's stamp disagrees with
the committed source it claims to summarize.

Uses a single long-lived `git cat-file --batch` process for all blob reads
(never one `git show`/`git cat-file` per file — this repo is on slow WSL
drvfs; see the git-efficiency skill).

USAGE
    python3 dll_source_stamp.py check                 # verify every tracked
                                                        # *.dll.srchash against
                                                        # committed source at HEAD
    python3 dll_source_stamp.py check --range A..B     # verify only what
                                                        # A..B introduces —
                                                        # used by
                                                        # block_dll_source_mismatch.py

Exit code 1 if anything is reported, 0 otherwise (0 output lines => exit 0).

Output lines, one assembly per group:
    MATCH <dll-path>
    MISMATCH <dll-path>
        <compile-item-path>: <reason>
    STAMP_MISSING <dll-path>   (--range only: the DLL changed in the range,
                                 its .srchash did not)
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys

SRC = "src"


# --------------------------------------------------------------------------
# git plumbing — one process for every blob we need to read.
# --------------------------------------------------------------------------

def _repo_root():
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                        capture_output=True, text=True, check=True)
    return r.stdout.strip()


class BatchCat:
    """One `git cat-file --batch` process serving many `<rev>:<path>` reads.

    Avoids spawning a git process per file — the documented drvfs-slowness
    trap (see the git-efficiency skill).
    """

    def __init__(self, repo):
        self._p = subprocess.Popen(
            ["git", "cat-file", "--batch"], cwd=repo,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self._cache = {}

    def get(self, spec):
        """Bytes of the object at `spec` ("<rev>:<path>"), or None if absent."""
        if spec in self._cache:
            return self._cache[spec]
        self._p.stdin.write((spec + "\n").encode())
        self._p.stdin.flush()
        header = self._p.stdout.readline().decode("utf-8", "replace").strip()
        parts = header.split()
        if len(parts) < 2 or parts[-1] == "missing":
            self._cache[spec] = None
            return None
        size = int(parts[2])
        data = self._p.stdout.read(size)
        self._p.stdout.read(1)  # the trailing newline cat-file --batch emits
        self._cache[spec] = data
        return data

    def close(self):
        try:
            self._p.stdin.close()
        except Exception:
            pass
        self._p.wait(timeout=10)


def ls_tree(rev, path, repo):
    """Tracked file paths under `path` at `rev`, relative to the repo root."""
    r = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", rev, "--", path],
        cwd=repo, capture_output=True, text=True)
    if r.returncode != 0:
        return []
    return [ln for ln in r.stdout.splitlines() if ln]


def diff_paths(a, b, repo):
    """Every path touched anywhere across a..b (added, modified or deleted)."""
    r = subprocess.run(["git", "diff", "--name-only", "%s..%s" % (a, b)],
                        cwd=repo, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("git diff %s..%s failed: %s" % (a, b, r.stderr.strip()))
    return set(ln for ln in r.stdout.splitlines() if ln)


# --------------------------------------------------------------------------
# csproj interpretation — what @(Compile) would resolve to at a given rev.
# --------------------------------------------------------------------------

_ENABLE_DEFAULT_RE = re.compile(
    r"<EnableDefaultCompileItems>\s*(true|false)\s*</EnableDefaultCompileItems>",
    re.IGNORECASE)
_COMPILE_INCLUDE_RE = re.compile(r'<Compile\s+Include\s*=\s*"([^"]+)"', re.IGNORECASE)


def _norm(p):
    return p.replace("\\", "/")


def expected_compile_set(cat, rev, csproj_repo_path, repo):
    """(paths, project_dir_repo_relative) the csproj would compile at `rev`.

    Paths are relative to the project's own directory (matching how @(Compile)
    Identity — and therefore the .srchash sidecar — records them), forward
    slashes. Returns (None, None) if the csproj itself is not present at rev.
    """
    raw = cat.get("%s:%s" % (rev, csproj_repo_path))
    if raw is None:
        return None, None
    text = raw.decode("utf-8", "replace")
    project_dir = os.path.dirname(csproj_repo_path)

    m = _ENABLE_DEFAULT_RE.search(text)
    enable_default = True if m is None else (m.group(1).lower() == "true")

    if not enable_default:
        # EnableDefaultCompileItems=false — the explicit <Compile Include>
        # list below it IS the whole compile set (RM_CreatureBehaviors.csproj
        # is the pattern this was modeled on).
        includes = sorted(set(_norm(p) for p in _COMPILE_INCLUDE_RE.findall(text)))
        return includes, project_dir

    # Default SDK glob: every *.cs under the project dir, except:
    #   - anything under an obj/ or bin/ path segment (MSBuild's own
    #     default excludes for the glob itself; a *generated* file like
    #     CoreGenerateAssemblyInfo's AssemblyAttributes.cs is added to
    #     @(Compile) separately, AFTER those excludes run, so it can still
    #     show up live — measured 2026-09-25 on Oracle.csproj. It is not
    #     committed, so it must not be expected here either.)
    #   - anything under a subdirectory that itself holds another .csproj
    #     (a nested SelfTest project — Visibility.csproj hits exactly this
    #     and excludes it with an explicit <Compile Remove>; parsing that
    #     Remove is unnecessary because the nested-csproj rule alone
    #     produces the same result).
    listing = ls_tree(rev, project_dir, repo)
    rel_listing = []
    for p in listing:
        if not p.startswith(project_dir + "/"):
            continue
        rel_listing.append(p[len(project_dir) + 1:])

    nested_dirs = set()
    for p in rel_listing:
        if p.endswith(".csproj"):
            d = os.path.dirname(p)
            if d:
                nested_dirs.add(d)

    def under_nested(p):
        return any(p == d or p.startswith(d + "/") for d in nested_dirs)

    expected = []
    for p in rel_listing:
        if not p.endswith(".cs"):
            continue
        segs = p.split("/")[:-1]
        if any(s.lower() in ("obj", "bin") for s in segs):
            continue
        if under_nested(p):
            continue
        expected.append(p)
    return sorted(set(expected)), project_dir


# --------------------------------------------------------------------------
# stamp recomputation
# --------------------------------------------------------------------------

class Result:
    def __init__(self, status, detail=None):
        self.status = status      # MATCH | MISMATCH | ABSENT | MALFORMED | CSPROJ_MISSING
        self.detail = detail or []


def recompute_stamp(cat, rev, stamp_repo_path, repo):
    raw = cat.get("%s:%s" % (rev, stamp_repo_path))
    if raw is None:
        return Result("ABSENT")
    text = raw.decode("utf-8", "replace")
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# project:"):
        return Result("MALFORMED", ["stamp has no '# project:' header line"])
    project_rel = lines[0][len("# project:"):].strip()
    csproj_repo_path = SRC + "/" + project_rel

    recorded = {}
    for ln in lines[1:]:
        ln = ln.strip()
        if not ln:
            continue
        h, _, p = ln.partition(" ")
        recorded[_norm(p)] = h.lower()

    expected_paths, project_dir = expected_compile_set(cat, rev, csproj_repo_path, repo)
    if expected_paths is None:
        return Result("CSPROJ_MISSING",
                       ["%s not present at %s" % (csproj_repo_path, rev)])

    union = sorted(set(recorded) | set(expected_paths))
    detail = []
    for p in union:
        file_repo_path = project_dir + "/" + p
        actual = cat.get("%s:%s" % (rev, file_repo_path))
        in_recorded = p in recorded
        in_expected = p in expected_paths
        if actual is None:
            detail.append("%s: source file missing at %s" % (p, rev))
            continue
        actual_hash = hashlib.sha256(actual).hexdigest()
        if not in_recorded:
            detail.append("%s: compiled by the project but absent from the "
                           "stamp (added since the last rebuild)" % p)
        elif recorded[p] != actual_hash:
            detail.append("%s: hash in stamp does not match committed source"
                           % p)
        if in_recorded and not in_expected:
            detail.append("%s: stamp lists it but the project would not "
                           "compile it now (stale/removed/renamed)" % p)

    if detail:
        return Result("MISMATCH", detail)
    return Result("MATCH")


def find_stamps(rev, repo):
    return [p for p in ls_tree(rev, SRC, repo) if p.endswith(".dll.srchash")]


# --------------------------------------------------------------------------
# top-level check modes
# --------------------------------------------------------------------------

def _print_result(dll, result):
    print("%s %s" % (result.status, dll))
    for d in result.detail:
        print("    %s" % d)


def check_head(cat, repo):
    bad = False
    for stamp in sorted(find_stamps("HEAD", repo)):
        dll = stamp[: -len(".srchash")]
        result = recompute_stamp(cat, "HEAD", stamp, repo)
        if result.status != "MATCH":
            bad = True
        _print_result(dll, result)
    return 1 if bad else 0


def _exists_at(rev, path, repo):
    r = subprocess.run(["git", "cat-file", "-e", "%s:%s" % (rev, path)],
                        cwd=repo, capture_output=True)
    return r.returncode == 0


def check_range(cat, a, b, repo):
    changed = diff_paths(a, b, repo)
    # A DELETED dll (present at `a`, gone at `b`) can never disagree with its
    # source -- nothing ships. Flagging it as STAMP_MISSING is a false
    # positive that blocks a legitimate mod rename/removal (measured
    # 2026-09-25/26: a RimUtinni -> RimMandrake tier rename deleted
    # RimMandrake.Utinni.LanternDeeps.dll, which never had a .srchash sidecar
    # in the first place -- there was nothing to keep "in sync"). Only a dll
    # that still EXISTS at `b` needs a paired stamp change.
    changed_dlls = {p for p in changed
                    if p.endswith(".dll") and "/Assemblies/" in p
                    and _exists_at(b, p, repo)}
    changed_stamps = {p for p in changed if p.endswith(".dll.srchash")}

    bad = False
    reported_dlls = set()

    for dll in sorted(changed_dlls):
        stamp = dll + ".srchash"
        if stamp in changed_stamps:
            continue
        # LANTERNDEEPS_RM_MOD_BUILD_1 (2026-09-25): a cross-directory mod
        # rename (git mv the whole mod folder, rebuild under the new
        # namespace) makes git see the OLD path's DLL as a plain delete, not
        # a rename — its bytes changed too much (different namespace/
        # assembly name baked into the IL) to pass git's own similarity
        # heuristic at the default threshold. That case is already excluded
        # above: `changed_dlls` only contains paths that still exist at `b`,
        # so a DLL retired by such a rename (gone at `b`) never reaches this
        # loop at all — its retirement drops no provenance claim, since there
        # was never a stamp asserting it matched its source.
        print("STAMP_MISSING %s" % dll)
        print("    DLL changed in %s..%s but %s did not — rebuild and "
              "commit them together" % (a, b, os.path.basename(stamp)))
        reported_dlls.add(dll)
        bad = True

    for stamp in sorted(find_stamps(b, repo)):
        dll = stamp[: -len(".srchash")]
        if dll in reported_dlls:
            continue
        result_b = recompute_stamp(cat, b, stamp, repo)
        if result_b.status == "MATCH":
            continue
        result_a = recompute_stamp(cat, a, stamp, repo)
        if result_a.status == result_b.status == "MISMATCH":
            continue  # pre-existing — not introduced by this range, allow it
        bad = True
        _print_result(dll, result_b)

    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_check = sub.add_parser("check")
    p_check.add_argument("--range", help="A..B — only report what this range introduces")
    args = ap.parse_args()

    repo = _repo_root()
    cat = BatchCat(repo)
    try:
        if args.cmd == "check":
            if args.range:
                if ".." not in args.range:
                    sys.exit("--range must look like A..B")
                a, b = args.range.split("..", 1)
                return check_range(cat, a, b, repo)
            return check_head(cat, repo)
    finally:
        cat.close()


if __name__ == "__main__":
    sys.exit(main())
