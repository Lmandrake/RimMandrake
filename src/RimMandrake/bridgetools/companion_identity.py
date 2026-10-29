#!/usr/bin/env python3
"""companion_identity.py - is a JawaBench companion DLL built from the sources a job runs at? (stdlib only)

STEVE_COMPANION_FIX_DLL_STALE_NO_PRIORITIES (2026-10-29): testq job J20261029T211737Z-3af227 ran FlowWorks droid_dig on
SteveDesktop with a companion older than 1b5adb3c5a (jawa/set_work_priority's manualPrioritiesOn); both rows read
UNMEASURED/HARNESS and nothing said why. Nothing on the lane compared the companion with the job's source:
  * the DLL is not committed (bridgetools/artifacts/ is gitignored) and carries no .srchash sidecar (that target only
    stamps Assemblies/ outputs);
  * its build stamp (AssemblyInformationalVersion "+<sha>") is the HEAD of whatever clone built it - often a scratch
    or seat commit that no other clone has (both copies on Archmagi on 2026-10-29 named commits absent from every
    clone), so "is it an ancestor of the job's sha" cannot be answered;
  * sync_test_mods.py called a target "same" on file count + byte total, and a PE file is 512-byte aligned, so a
    rebuild from different source routinely has the identical size.

So build.py now embeds a SOURCE hash in the DLL itself: [assembly: AssemblyMetadata("JawaBenchSrcHash", "<hex>")]
(MSBuild property JawaSrcHash). The hash covers every .cs/.csproj/.props/.targets file under the companion's project
folder (bin/ and obj/ excluded): sha256 over sorted lines "<path>\\0<sha256 of the bytes, CRLF folded to LF>\\n".
The worker recomputes it from the git tree at the job's source_sha, so FRESH means "compiled from exactly the
companion sources this job runs at", whoever built it and in whatever clone. A DLL built before this stamp existed
reads UNSTAMPED: unproven, which a lane treats as stale (fail closed).

    python3 companion_identity.py DLL [--repo R] [--rev REV]    # one line: STATE dll embedded want; exit 0 iff FRESH
"""
import hashlib
import json
import os
import re
import subprocess
import sys

DLL_NAME = "JawaBench.BridgeTools.dll"
SRC_REL = "src/RimMandrake/bridgetools/JawaBench.BridgeTools"
META_KEY = "JawaBenchSrcHash"
SUFFIXES = (".cs", ".csproj", ".props", ".targets")
# the AssemblyMetadataAttribute blob: two SerStrings, each a 1-byte length prefix (16, 64) then UTF-8
_MARK = re.compile(re.escape(bytes([len(META_KEY)]) + META_KEY.encode()) + b"\x40([0-9a-f]{64})")
_STAMP = re.compile(r"\d+\.\d+\.\d+\+([0-9a-f]{40})")


def wanted(rel):
    """`rel` (relative to the project folder, '/'-separated) is a compile input the hash covers."""
    parts = rel.split("/")
    return rel.endswith(SUFFIXES) and not any(p.lower() in ("bin", "obj") for p in parts[:-1])


def digest(files):
    """{rel: bytes} -> the source hash (hex)."""
    h = hashlib.sha256()
    for rel in sorted(files):
        h.update(("%s\0%s\n" % (rel, hashlib.sha256(files[rel].replace(b"\r\n", b"\n")).hexdigest())).encode())
    return h.hexdigest()


def srchash_worktree(repo_root):
    """The hash of the companion sources ON DISK (what a build compiles), or None when the folder is absent."""
    base = os.path.join(repo_root, *SRC_REL.split("/"))
    if not os.path.isdir(base):
        return None
    files = {}
    for root, dirs, names in os.walk(base):
        dirs[:] = [d for d in dirs if d.lower() not in ("bin", "obj")]
        for n in names:
            full = os.path.join(root, n)
            rel = os.path.relpath(full, base).replace(os.sep, "/")
            if wanted(rel):
                with open(full, "rb") as f:
                    files[rel] = f.read()
    return digest(files)


def srchash_at(repo_root, rev):
    """The hash of the companion sources in the git tree at `rev`, or None when git cannot read it."""
    r = subprocess.run(["git", "-C", repo_root, "ls-tree", "-r", "-z", rev, "--", SRC_REL],
                       capture_output=True, timeout=120)
    if r.returncode:
        return None
    entries = []
    for rec in r.stdout.split(b"\0"):
        if not rec:
            continue
        meta, path = rec.split(b"\t", 1)
        mode, typ, oid = meta.split()
        rel = path.decode("utf-8", "surrogateescape")[len(SRC_REL) + 1:]
        if typ == b"blob" and wanted(rel):
            entries.append((rel, oid.decode()))
    if not entries:
        return None
    p = subprocess.Popen(["git", "-C", repo_root, "cat-file", "--batch"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    files = {}
    try:
        for rel, oid in entries:
            p.stdin.write(oid.encode() + b"\n")
            p.stdin.flush()
            head = p.stdout.readline().split()
            if len(head) != 3 or head[1] != b"blob":
                return None
            size = int(head[2])
            files[rel] = p.stdout.read(size)
            p.stdout.read(1)
    finally:
        p.stdin.close()
        p.wait(timeout=60)
    return digest(files)


def embedded(blob):
    """The source hash build.py embedded in the DLL bytes, or None (built before the stamp, or not ours)."""
    m = _MARK.search(blob)
    return m.group(1).decode() if m else None


def build_commit(blob):
    """The clone HEAD the SDK stamped into AssemblyInformationalVersion (informational only), or None."""
    for enc in ("utf-16-le", "utf-8"):
        m = _STAMP.search(blob.decode(enc, "ignore"))
        if m:
            return m.group(1)
    return None


def write_fixture(dll, src_hash):
    """Selftests: write a stand-in DLL carrying `src_hash` the way the compiler lays out the AssemblyMetadata blob."""
    os.makedirs(os.path.dirname(dll) or ".", exist_ok=True)
    blob = b"MZ\x90\x00" + b"\x00" * 60
    if src_hash:
        blob += b"\x01\x00" + bytes([len(META_KEY)]) + META_KEY.encode() + bytes([len(src_hash)]) + src_hash.encode()
    with open(dll, "wb") as f:
        f.write(blob + b"\x00\x00")
    return dll


def verdict(dll, repo_root, rev, want=None):
    """-> {"state", "dll", "dll_sha256", "embedded", "want", "build_commit"}.

    state: FRESH (embedded == want) | STALE (embedded, different) | UNSTAMPED (no embedded hash: built before
    the stamp, unprovable) | MISSING (no file) | UNMEASURED (the job's tree could not be hashed)."""
    out = {"dll": dll, "dll_sha256": None, "embedded": None, "want": want, "build_commit": None}
    if out["want"] is None:
        out["want"] = srchash_at(repo_root, rev)
    if not os.path.isfile(dll):
        return dict(out, state="MISSING")
    with open(dll, "rb") as f:
        blob = f.read()
    out.update(dll_sha256=hashlib.sha256(blob).hexdigest(), embedded=embedded(blob), build_commit=build_commit(blob))
    if out["want"] is None:
        return dict(out, state="UNMEASURED")
    if out["embedded"] is None:
        return dict(out, state="UNSTAMPED")
    return dict(out, state="FRESH" if out["embedded"] == out["want"] else "STALE")


def describe(v):
    """One line for a result note."""
    return "%s %s (embedded source hash %s, build commit %s; the job's companion sources hash %s)" % (
        v["state"], v["dll"], (v["embedded"] or "none")[:12], (v["build_commit"] or "none")[:12],
        (v["want"] or "unreadable")[:12])


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dll")
    ap.add_argument("--repo", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
    ap.add_argument("--rev", default="HEAD")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    v = verdict(a.dll, a.repo, a.rev)
    print(json.dumps(v, sort_keys=True) if a.json else describe(v))
    return 0 if v["state"] == "FRESH" else 1


if __name__ == "__main__":
    sys.exit(main())
