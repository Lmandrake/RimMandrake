#!/usr/bin/env python3
"""Build a mod's C# from an ext4 clone by staging it on the Windows drive.

    python3 src/RimMandrake/Utils/winbuild.py <Mod | path/to/X.csproj> [-c Release] [--dry-run]

Plan: design/RimMandrake/git_workflow_plan_2026-10-01.md §2.3 ("dotnet.exe builds — rsync to a
Windows directory is the default route"). dotnet.exe is Windows-native: it cannot build from a
`\\\\wsl.localhost` path (dotnet/sdk#19169, NuGet/Home#13989, dotnet/msbuild#7001), so:

1. Resolve the csproj (a mod name finds the single shipping csproj under src/**/<Mod>/Source/).
2. Collect what it needs by RELATIVE path — its own dir, every `..\\` Include/HintPath/
   ProjectReference/OutputPath target (recursively through ProjectReferences), and
   src/Directory.Build.targets (the .srchash stamp) — and rsync them, keeping their repo-relative
   layout, into /mnt/d/ClaudeWork/rimmandrake/build/<Mod>/ (D:\\ClaudeWork\\rimmandrake\\build\\<Mod>\\). Layout matters:
   the stamp records the csproj path relative to src/, so the mirror must keep src/ as its root.
   bin/ and obj/ on the Windows side are left alone as a warm incremental cache.
3. Run C:\\Users\\Mandrake\\.dotnet\\dotnet.exe build there.
4. Copy every DLL and .srchash the build wrote under an Assemblies/ dir back to the same path in
   the clone, and record the source sha in <build root>/<Mod>/BUILD_SOURCE.json.

Run from the /mnt/d tree it builds in place (that tree is already a Windows path).
Prints `BUILT <repo-relative dll> (source <sha>[+dirty])` per DLL; exits non-zero on failure.
"""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import argparse
import datetime
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
BUILD_ROOT = os.environ.get("WINBUILD_ROOT", rm_str("build"))
DOTNET_CANDIDATES = ["/mnt/c/Users/Mandrake/.dotnet/dotnet.exe",
                     "/mnt/c/Program Files/dotnet/dotnet.exe"]
RSYNC_EXCLUDES = ["bin/", "obj/", "Textures/", "Sounds/", "*.png", "*.psd", "*.ogg", "*.wav"]
PATH_TAGS = {"Compile", "None", "Content", "EmbeddedResource", "ProjectReference", "Reference",
             "HintPath", "OutputPath", "BaseOutputPath", "Import"}


def dotnet_exe():
    for c in DOTNET_CANDIDATES:
        if os.path.exists(c):
            return c
    sys.exit("dotnet.exe not found (looked at %s)" % ", ".join(DOTNET_CANDIDATES))


def on_windows_drive(path):
    return os.path.realpath(path).startswith("/mnt/")


def find_csproj(target):
    if target.endswith(".csproj"):
        p = os.path.abspath(target if os.path.isabs(target) else os.path.join(os.getcwd(), target))
        if not os.path.exists(p):
            p = os.path.join(ROOT, target)
        if not os.path.exists(p):
            sys.exit("no such csproj: %s" % target)
        return os.path.realpath(p)
    hits = [p for p in glob.glob(os.path.join(ROOT, "src", "**", target, "Source", "**", "*.csproj"),
                                 recursive=True)
            if "selftest" not in p.lower() and "/bin/" not in p and "/obj/" not in p]
    if not hits:
        sys.exit("no csproj under src/**/%s/Source/" % target)
    top = min(len(os.path.relpath(h, ROOT).split(os.sep)) for h in hits)
    hits = [h for h in hits if len(os.path.relpath(h, ROOT).split(os.sep)) == top]
    if len(hits) > 1:
        sys.exit("%s has %d csproj files; name one:\n  %s" % (
            target, len(hits), "\n  ".join(os.path.relpath(h, ROOT) for h in sorted(hits))))
    return os.path.realpath(hits[0])


def strip_ns(tag):
    return tag.split("}", 1)[-1]


def rel_values(csproj):
    """Every path-ish value in the csproj that starts with `..` (MSBuild props stripped)."""
    vals = []
    try:
        tree = ET.parse(csproj)
    except ET.ParseError as e:
        sys.exit("cannot parse %s: %s" % (csproj, e))
    for el in tree.iter():
        tag = strip_ns(el.tag)
        cands = []
        if tag in PATH_TAGS:
            cands += [el.get("Include"), el.get("Project"), el.get("Update")]
            if el.text and tag in ("HintPath", "OutputPath", "BaseOutputPath"):
                cands.append(el.text)
        # a PropertyGroup default like <XDll>$(MSBuildThisFileDirectory)..\\..\\Other\\Assemblies\\X.dll</XDll>
        # is a path the build needs too (7 csprojs, e.g. BlueDesert's EnvironmentalHazards reference)
        if el.text and "$(MSBuildThisFileDirectory)" in el.text and ".." in el.text:
            cands.append(el.text.strip().replace("$(MSBuildThisFileDirectory)", ""))
            tag = "Reference"
        for c in cands:
            if c and ".." in c and "$(" not in c.split("..")[0]:
                vals.append((tag, el.get("Include") or "", c.strip()))
    return vals


def needed_dirs(csproj, seen=None):
    """Directories (absolute) the build needs, following ProjectReferences recursively."""
    seen = seen if seen is not None else set()
    csproj = os.path.realpath(csproj)
    if csproj in seen:
        return set()
    seen.add(csproj)
    base = os.path.dirname(csproj)
    dirs = {base}
    for tag, include, raw in rel_values(csproj):
        for piece in raw.split(";"):
            piece = piece.strip().replace("\\", "/")
            if not piece or ".." not in piece:
                continue
            piece = re.sub(r"\$\([^)]*\)", "", piece)
            full = os.path.normpath(os.path.join(base, piece))
            # the deepest real directory at or above the referenced path (globs/files trimmed)
            d = full
            while d and (any(ch in os.path.basename(d) for ch in "*?") or not os.path.isdir(d)):
                d = os.path.dirname(d)
            if not d.startswith(ROOT):
                continue
            if tag in ("OutputPath", "BaseOutputPath"):
                continue                      # an output dir is created by the build
            if tag == "ProjectReference" and full.endswith(".csproj") and os.path.exists(full):
                dirs |= needed_dirs(full, seen)
            elif os.path.isfile(full):
                dirs.add(os.path.dirname(full))
            else:
                dirs.add(d)
    return dirs


def minimal(dirs):
    keep = []
    for d in sorted(dirs, key=len):
        if not any(d == k or d.startswith(k + os.sep) for k in keep):
            keep.append(d)
    return keep


def source_sha(paths):
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    rel = [os.path.relpath(p, ROOT) for p in paths]
    dirty = subprocess.run(["git", "status", "--porcelain", "--", *rel], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip()
    return sha, bool(dirty)


def run_dotnet(csproj_win, cwd, config, extra):
    cmd = [dotnet_exe(), "build", csproj_win, "-c", config, "--nologo", "-v", "minimal", *extra]
    print("+ dotnet.exe build %s -c %s" % (csproj_win, config), flush=True)
    return subprocess.run(cmd, cwd=cwd).returncode


def built_outputs(tree, since):
    outs = []
    for dirpath, dirnames, files in os.walk(tree):
        dirnames[:] = [d for d in dirnames if d not in ("obj", ".git")]
        if "Assemblies" not in dirpath.split(os.sep):
            continue
        for f in files:
            if f.endswith(".dll") or f.endswith(".dll.srchash"):
                p = os.path.join(dirpath, f)
                if os.path.getmtime(p) >= since - 2:
                    outs.append(p)
    return sorted(outs)


def win(path):
    return subprocess.run(["wslpath", "-w", path], capture_output=True, text=True).stdout.strip()


def rsync_stage(rels, stage, cwd, excl=()):
    """rsync repo-relative rels into stage, deciding "changed" by CONTENT (--checksum), not mtime+size.

    The old --modify-window=2 skipped a same-size edit made within 2 s of the previous copy (mutate-test-restore), so the
    stage kept stale source and MSBuild ran the stale binary. No -t: staged files carry their copy time, never the clone mtime. Every file rsync rewrites also gets mtime = now so
    MSBuild sees it newer than obj even when the clone file carries an old mtime (e.g. cp -p restore).
    Returns the CompletedProcess (stdout holds the itemize lines)."""
    r = subprocess.run(["rsync", "-rR", "-c", "-i", "--delete", "--no-perms", "--no-owner", "--no-group",
                        *excl, *rels, stage + "/"], cwd=cwd, stdout=subprocess.PIPE, universal_newlines=True)
    now = time.time()
    for line in r.stdout.splitlines():
        if line.startswith(">f") and len(line) > 12:
            p = os.path.join(stage, line[12:])
            try:
                os.utime(p, (now, now))
            except OSError:
                pass
    return r


def stage_build(csproj, config="Release", extra=(), extra_dirs=(), copy_back_dirs=(),
                stage_name=None, dry_run=False):
    """Stage csproj (+ what it references, + extra_dirs) on D:, build, copy outputs back.

    Returns (rc, record). Outputs copied back: every DLL/.srchash the build wrote under an
    Assemblies/ dir, plus every file the build wrote under copy_back_dirs (repo-relative).
    Callers that need a staged Windows path for a repo dir use staged_win(record, repo_dir).
    """
    csproj = os.path.realpath(csproj)
    rel_proj = os.path.relpath(csproj, ROOT)
    parts = rel_proj.split(os.sep)                       # src/<Tier>/<Mod>/Source/...
    mod = stage_name or (parts[2] if len(parts) > 3 else os.path.splitext(parts[-1])[0])
    stage = os.path.join(BUILD_ROOT, re.sub(r"[^A-Za-z0-9_.-]", "_", mod))
    dirs = minimal(needed_dirs(csproj) | {os.path.realpath(d) for d in extra_dirs})
    print("staging %s -> %s" % (rel_proj, win(stage) if os.path.isdir(BUILD_ROOT) else stage))
    for d in dirs:
        print("  %s/" % os.path.relpath(d, ROOT))
    record = {"csproj": rel_proj, "stage": stage, "outputs": []}
    if dry_run:
        return 0, record
    os.makedirs(stage, exist_ok=True)
    started = time.time()
    rels = [os.path.relpath(d, ROOT) + "/" for d in dirs] + ["src/Directory.Build.targets", "src/Directory.Build.props"]
    excl = sum((["--exclude", e] for e in RSYNC_EXCLUDES), [])
    # close evidence (review Z F2/F7): the build reads the STAGE, so the tree it tested is the clone between these two
    # snapshots, scoped to what was staged; the DLLs copied back afterwards never make the record dirty
    record["ev_scope"] = rels
    record["ev_start"] = _ce_snapshot(rels)
    # -R keeps repo-relative layout; --delete prunes files removed from the clone (excludes kept).
    # rsync exit 24 = "some source files vanished": another agent saved/renamed a file in the clone mid-copy (the stage
    # copies whole src/). Transient, not a build verdict - the copy is idempotent, so retry before failing (2026-10-22).
    for attempt in range(4):
        r = rsync_stage(rels, stage, ROOT, excl)
        if r.returncode != 24:
            break
        print("rsync 24 (source files vanished mid-copy); retry %d/3" % (attempt + 1), file=sys.stderr)
        time.sleep(2)
    if r.returncode:
        print("rsync failed (%d)" % r.returncode, file=sys.stderr)
        record["staged"] = False                   # nothing was built: UNMEASURED, not FAIL (review Z F7)
        return r.returncode, record
    record["staged"] = True
    record["ev_end"] = _ce_snapshot(rels)
    staged_proj = os.path.join(stage, rel_proj)
    sha, dirty = source_sha(dirs + [os.path.join(ROOT, "src", "Directory.Build.targets"), os.path.join(ROOT, "src", "Directory.Build.props")])
    record.update(source_sha=sha, dirty=dirty, clone=ROOT)
    # No .git on the stage, so hand the SDK the sha it would otherwise read from git:
    # AssemblyInformationalVersion still ends "+<sha>" (bridgetools/build.py reads it back).
    rc = run_dotnet(win(staged_proj), os.path.dirname(staged_proj), config,
                    ["-p:SourceRevisionId=%s" % sha, *extra])
    if rc:
        print("BUILD FAILED (%d) in %s" % (rc, win(staged_proj)), file=sys.stderr)
        return rc, record
    outs = built_outputs(stage, started)
    for d in copy_back_dirs:
        base = os.path.join(stage, d)
        for dirpath, _, files in os.walk(base):
            for f in files:
                p = os.path.join(dirpath, f)
                if os.path.getmtime(p) >= started - 2 and p not in outs:
                    outs.append(p)
    # A no-op incremental build rewrites the stamp but not the DLL: always carry the pair together.
    for p in list(outs):
        twin = p[:-len(".srchash")] if p.endswith(".srchash") else p + ".srchash"
        if os.path.exists(twin) and twin not in outs:
            outs.append(twin)
    for p in outs:
        if p.endswith(".srchash"):
            want = next((l.split(":", 1)[1].strip() for l in open(p) if l.startswith("# dll:")), None)
            got = hashlib.sha256(open(p[:-len(".srchash")], "rb").read()).hexdigest()
            if want and want != got:
                print("STAMP MISMATCH in stage: %s records dll %s, file is %s" % (p, want, got),
                      file=sys.stderr)
                return 3, record
    for p in sorted(outs):
        rel = os.path.relpath(p, stage)
        dst = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(p, "rb") as f, open(dst + ".winbuild-tmp", "wb") as g:
            g.write(f.read())
        os.replace(dst + ".winbuild-tmp", dst)
        record["outputs"].append(rel)
    record["built_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    with open(os.path.join(stage, "BUILD_SOURCE.json"), "w") as f:
        json.dump(record, f, indent=1)
    return 0, record


def staged_win(record, repo_path):
    """The Windows path of a repo path inside this build's stage."""
    return win(os.path.join(record["stage"], os.path.relpath(os.path.realpath(repo_path), ROOT)))


def pulse_report(csproj, rc, stage=None):
    """One build attempt for RimPulse's job history (RIMPULSE_FAILURES_BUILD_ONLY_THE_STUCK): a failure followed
    by a pass is history, never an alarm. Never fails the build."""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pulse"))
        from failreport import report
        report("build:" + os.path.splitext(os.path.basename(csproj))[0], rc == 0,
               cause=None if rc == 0 else "winbuild exit %d (see the build output)" % rc,
               link=stage if rc and stage else None)
    except Exception:  # noqa: BLE001
        pass


def _ce():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import close_evidence
    return close_evidence


def _ce_snapshot(scope=None):
    """close_evidence tree snapshot of ROOT (scoped to `scope` pathspecs); None when unavailable. Never raises."""
    try:
        return _ce().tree_state(ROOT, scope)
    except Exception as exc:  # noqa: BLE001
        print("!!! CLOSE-EVIDENCE snapshot failed (%s: %s)" % (type(exc).__name__, exc), file=sys.stderr)
        return None


def evidence_report(csproj, rc, config, rec=None, start=None):
    """One close-evidence line per build (CLOSE_EVIDENCE_BUILD_GATES_CAN_DECIDE): PASS on exit 0, FAIL on a build
    failure, UNMEASURED when staging failed and nothing was built. Staged builds are keyed by the tree between the
    snapshots taken around the rsync, scoped to the staged dirs (review Z F2/F7); in-place builds by `start` and the
    tree at the end. Never fails the build."""
    try:
        ce = _ce()
    except Exception as exc:  # noqa: BLE001
        print("!!! CLOSE-EVIDENCE unavailable (%s: %s); this build is not recorded" % (type(exc).__name__, exc),
              file=sys.stderr)
        return
    rec = rec or {}
    result = "UNMEASURED" if rec.get("staged") is False else ("PASS" if rc == 0 else "FAIL")
    scope = rec.get("ev_scope")
    covers = [os.path.join(ROOT, r.rstrip("/")) for r in scope] if scope else None
    ce.record("winbuild", result, [csproj], clone=ROOT, start=rec.get("ev_start", start), end=rec.get("ev_end"),
              scope=scope, covers=([csproj] + covers) if covers else None,
              detail={"rc": rc, "configuration": config, "outputs": rec.get("outputs", []),
                      "staged_dirs_dirty": rec.get("dirty"), "source_sha": rec.get("source_sha")})


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="mod folder name (e.g. SleepingIce) or a csproj path")
    ap.add_argument("-c", "--configuration", default="Release")
    ap.add_argument("--dry-run", action="store_true", help="show what would be staged; build nothing")
    argv = list(sys.argv[1:] if argv is None else argv)
    extra = argv[argv.index("--") + 1:] if "--" in argv else []     # after --: to dotnet build
    a = ap.parse_args(argv[:argv.index("--")] if "--" in argv else argv)
    csproj = find_csproj(a.target)

    if on_windows_drive(ROOT):                                  # already a Windows path: in place
        if a.dry_run:
            print("in place: %s" % win(csproj))
            return 0
        start = _ce_snapshot()
        rc = run_dotnet(win(csproj), os.path.dirname(csproj), a.configuration, extra)
        pulse_report(csproj, rc)
        evidence_report(csproj, rc, a.configuration, start=start)
        return rc

    rc, rec = stage_build(csproj, a.configuration, extra, dry_run=a.dry_run)
    if not a.dry_run:
        pulse_report(csproj, rc, rec.get("stage"))
        evidence_report(csproj, rc, a.configuration, rec)
    if rc or a.dry_run:
        return rc
    if not rec["outputs"]:
        print("build succeeded but wrote no DLL under an Assemblies/ dir "
              "(an artifacts-only project?) — nothing copied back")
    for rel in rec["outputs"]:
        if rel.endswith(".dll"):
            print("BUILT %s (source %s%s)" % (rel, rec["source_sha"][:12],
                                              "+dirty" if rec["dirty"] else ""))
    try:  # telemetry `build` event (TELEMETRY_BUILD_EVERY_TICK_ACCOUNTED); never fails the build
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "telemetry"))
        from telemetry_emit import emit_change
        emit_change("build", os.path.basename(csproj), sha=rec["source_sha"][:12],
                    detail={"outputs": rec["outputs"], "dirty": rec["dirty"], "configuration": a.configuration})
    except Exception:  # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
