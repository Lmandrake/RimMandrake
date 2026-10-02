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
   layout, into /mnt/d/Luke/dev/_rmbuild/<Mod>/ (D:\\Luke\\dev\\_rmbuild\\<Mod>\\). Layout matters:
   the stamp records the csproj path relative to src/, so the mirror must keep src/ as its root.
   bin/ and obj/ on the Windows side are left alone as a warm incremental cache.
3. Run C:\\Users\\Mandrake\\.dotnet\\dotnet.exe build there.
4. Copy every DLL and .srchash the build wrote under an Assemblies/ dir back to the same path in
   the clone, and record the source sha in _rmbuild/<Mod>/BUILD_SOURCE.json.

Run from the /mnt/d tree it builds in place (that tree is already a Windows path).
Prints `BUILT <repo-relative dll> (source <sha>[+dirty])` per DLL; exits non-zero on failure.
"""
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
BUILD_ROOT = os.environ.get("WINBUILD_ROOT", "/mnt/d/Luke/dev/_rmbuild")
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
                dirs.add(os.path.dirname(full) if tag == "Compile" else os.path.dirname(full))
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
    rels = [os.path.relpath(d, ROOT) + "/" for d in dirs] + ["src/Directory.Build.targets"]
    excl = sum((["--exclude", e] for e in RSYNC_EXCLUDES), [])
    # -R keeps repo-relative layout; --delete prunes files removed from the clone (excludes kept).
    r = subprocess.run(["rsync", "-rtR", "--delete", "--no-perms", "--no-owner", "--no-group",
                        "--modify-window=2", *excl, *rels, stage + "/"], cwd=ROOT)
    if r.returncode:
        print("rsync failed (%d)" % r.returncode, file=sys.stderr)
        return r.returncode, record
    staged_proj = os.path.join(stage, rel_proj)
    sha, dirty = source_sha(dirs + [os.path.join(ROOT, "src", "Directory.Build.targets")])
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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="mod folder name (e.g. NightsideIce) or a csproj path")
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
        return run_dotnet(win(csproj), os.path.dirname(csproj), a.configuration, extra)

    rc, rec = stage_build(csproj, a.configuration, extra, dry_run=a.dry_run)
    if rc or a.dry_run:
        return rc
    if not rec["outputs"]:
        print("build succeeded but wrote no DLL under an Assemblies/ dir "
              "(an artifacts-only project?) — nothing copied back")
    for rel in rec["outputs"]:
        if rel.endswith(".dll"):
            print("BUILT %s (source %s%s)" % (rel, rec["source_sha"][:12],
                                              "+dirty" if rec["dirty"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
