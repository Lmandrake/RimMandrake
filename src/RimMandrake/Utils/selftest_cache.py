"""Declared-input PASS cache for run_selftests.py (friction census 2026-10-26: selftest_flowworks_stock alone
cost 18.6 h over 563 runs, a third of them repeats of an unchanged tree).

A test is cached ONLY if it is declared in DECLS - an
unknown test never caches. The key is a sha256 over: CACHE_VERSION, the python version, the test script, run_selftests.py,
this file, and every declared input (relative path + content hash of each file, so an add, delete, rename or edit of any
file under a declared tree changes the key). A dotnet-built test names its csproj: every directory winbuild.needed_dirs
reports for it, plus src/Directory.Build.*, plus the Windows dotnet.exe's size and mtime (the toolchain), join the key.
Only PASS is stored; a non-PASS deletes the test's entries. Entries live in <agent_storage>/cache/selftests/ (a program
reads them, so not in the repo), keyed by content, so two clones with identical inputs share a hit.

Declare conservatively: a tree you forget is a stale PASS. Prefer a whole directory over a file list.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

CACHE_VERSION = "1"
HERE = Path(__file__).resolve().parent
SKIP_DIRS = {"__pycache__", "bin", "obj", ".git", "node_modules"}
CODE = (".py", ".cs", ".csproj", ".props", ".targets", ".xml", ".json")
DOTNET = ("/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe")

# trees: (repo-relative dir, extensions or None for every file, recursive). names_only: sibling mod folders a dotnet
# SelfTest names in a string literal without reading them (selftest_selftest_cache checks every other one is a tree)
_GSS_PY = dict(trees=[
    ("src/RimMandrake/GimmeSomeSlack", CODE, True),
    ("src/RimMandrake/FlowWorks", CODE, True),                 # review_map.py, northstar/playtest_runner.py
    ("src/RimMandrake/bridgetools", (".cs", ".csproj"), True),  # JawaBenchGssPlaytest.cs
    ("src/RimMandrake/Utils", (".py",), True),                  # validation_core, modcheck, winbuild: shared libs
])
DECLS: dict[str, dict] = {
    "src/RimMandrake/Utils/selftest_flowworks_stock.py": dict(
        csproj="src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj",
        # the SelfTest reads these at RUN time from the stage (extra_dirs=[src]), not only what it compiles:
        # FlowWorks Defs/Patches/Languages/art_source json, GSS Source + Defs + Textures, HugeThings/MovingDunes/
        # Pyrelands Source, GelatinousSlime, _Shared, BlueDesert Defs, RimUtinni UtinniPatches (selftest_selftest_cache guards this)
        trees=[("src/RimMandrake/FlowWorks", CODE, True),
               ("src/RimMandrake/FlowWorks/Source", None, True),
               ("src/RimMandrake/GimmeSomeSlack", CODE + (".png",), True),
               ("src/RimMandrake/HugeThings/Source", CODE, True),
               ("src/RimMandrake/MovingDunes/Source", CODE, True),
               ("src/RimMandrake/Pyrelands/Source", CODE, True),
               ("src/RimMandrake/GelatinousSlime", CODE, True),
               ("src/RimMandrake/_Shared", CODE, True),
               ("src/RimMandrake/BlueDesert/Defs", (".xml",), True),
               ("src/RimUtinni/UtinniPatches", (".xml",), True)],
        files=["src/RimMandrake/Utils/selftest_winstage.py", "src/RimMandrake/Utils/winbuild.py"], dotnet=True),
    "src/RimMandrake/Utils/selftest_gimmesomeslack.py": dict(
        csproj="src/RimMandrake/GimmeSomeSlack/Source/SelfTest/RimMandrakeGimmeSomeSlack.SelfTest.csproj",
        trees=[("src/RimMandrake/GimmeSomeSlack/Source", None, True),
               ("src/RimMandrake/Utils/mockups/messy_conduit", None, True)],
        files=["src/RimMandrake/Utils/winbuild.py", "src/RimMandrake/Utils/selftest_winstage.py"], dotnet=True,
        names_only={"MessyConduit"}),       # the legacy-name migration text, not a folder the test reads
    "src/RimMandrake/ColdStorage/selftest_coldstorage.py": dict(
        csproj="src/RimMandrake/ColdStorage/Source/SelfTest/RimMandrakeColdStorage.SelfTest.csproj",
        trees=[("src/RimMandrake/ColdStorage", None, True),
               ("src/RimMandrake/TheSump", (".xml", ".cs", ".csproj"), True),
               ("src/RimMandrake/WreckedMachines", (".xml", ".cs", ".csproj"), True),
               ("src/RimStarWars/Cuisine", (".xml", ".cs", ".csproj"), True),
               ("src/RimUtinni/StructureInjectionsRUT/Defs/VaultDungeons", (".xml",), True)],
        files=["src/RimMandrake/Utils/winbuild.py", "src/RimMandrake/Utils/selftest_winstage.py"], dotnet=True),
    "src/RimMandrake/GimmeSomeSlack/selftest_gss_proof_drivers.py": _GSS_PY,
    "src/RimMandrake/GimmeSomeSlack/selftest_human_review.py": _GSS_PY,
    "src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_playtest_runner.py": _GSS_PY,
}


def cache_dir() -> Path:
    base = os.environ.get("RM_SELFTEST_CACHE_STORE")
    if not base:
        out = subprocess.run([sys.executable, str(Path.home() / "dev/Lodestar/bin/lib/agent_storage.py")],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        if not out:
            raise RuntimeError("agent_storage.py printed nothing")
        base = os.path.join(out, "cache", "selftests")
    p = Path(base)
    p.mkdir(parents=True, exist_ok=True)
    return p


class _Hasher:
    """Content hash per file, memoised on (path, size, mtime_ns) so a hit costs stats, not reads."""

    def __init__(self, store: Path):
        self.f = store / "_statcache.json"
        try:
            self.m = json.loads(self.f.read_text())
        except (OSError, ValueError):
            self.m = {}
        self.dirty = False

    def file(self, p: Path) -> str:
        st = p.stat()
        k = f"{p}|{st.st_size}|{st.st_mtime_ns}|{st.st_ctime_ns}"   # ctime cannot be set back by utime
        h = self.m.get(k)
        if h is None:
            h = hashlib.sha1(p.read_bytes()).hexdigest()
            self.m[k] = h
            self.dirty = True
        return h

    def save(self):
        if self.dirty:
            if len(self.m) > 200000:
                self.m = {}
            tmp = self.f.with_name(f"{self.f.name}.{os.getpid()}")
            try:
                tmp.write_text(json.dumps(self.m))
                os.replace(tmp, self.f)
            except OSError:
                pass


def _walk(root: Path, exts, recursive):
    if not root.is_dir():
        return
    for dp, dn, fs in os.walk(root):
        dn[:] = sorted(d for d in dn if d not in SKIP_DIRS) if recursive else []
        for n in sorted(fs):
            if n.endswith(".pyc") or (exts and not n.endswith(tuple(exts))):
                continue
            yield Path(dp) / n


def compute_key(rel: str, repo: Path, decl: dict | None = None):
    """(key, n_files) for a declared test, or None (unknown test: never cached). Raises nothing on a missing input - a
    missing declared tree/file is part of the key (its absence is hashed), so appearing/vanishing invalidates."""
    decl = decl or DECLS.get(rel)
    if decl is None:
        return None
    store = cache_dir()
    H = _Hasher(store)
    h = hashlib.sha256()
    n = 0

    def feed(label, path: Path):
        nonlocal n
        n += 1
        h.update(f"{label}\0{H.file(path) if path.is_file() else 'ABSENT'}\n".encode())

    h.update(f"v{CACHE_VERSION}|py{sys.version_info[:3]}\n".encode())
    for p in (repo / rel, HERE / "run_selftests.py", HERE / "selftest_cache.py"):
        feed(f"core:{p.name}", p)
    for f in decl.get("files", []):
        feed("file:" + f, repo / f)
    for d, exts, rec in decl.get("trees", []):
        root = repo / d
        h.update(f"tree:{d}:{root.is_dir()}\n".encode())
        for p in _walk(root, exts, rec):
            feed("t:" + p.relative_to(repo).as_posix(), p)
    if decl.get("csproj"):
        sys.path.insert(0, str(HERE))
        import winbuild
        cs = repo / decl["csproj"]
        feed("csproj:" + decl["csproj"], cs)
        for d in sorted(winbuild.minimal(winbuild.needed_dirs(str(cs)))):
            h.update(f"needed:{os.path.relpath(d, winbuild.ROOT)}\n".encode())
            for p in _walk(Path(d), None, True):
                feed("n:" + os.path.relpath(p, winbuild.ROOT), p)
        for p in sorted((repo / "src").glob("Directory.Build.*")):
            feed("dbp:" + p.name, p)
    if decl.get("dotnet"):
        for c in DOTNET:
            try:
                st = os.stat(c)
                h.update(f"dotnet:{c}:{st.st_size}:{st.st_mtime_ns}\n".encode())
            except OSError:
                h.update(f"dotnet:{c}:absent\n".encode())
    H.save()
    return h.hexdigest()[:20], n


def _entry(store: Path, rel: str, key: str) -> Path:
    return store / f"{Path(rel).stem}__{key}.json"


def lookup(rel: str, key: str):
    p = _entry(cache_dir(), rel, key)
    try:
        d = json.loads(p.read_text())
    except (OSError, ValueError):
        return None
    return d if d.get("key") == key and d.get("test") == rel else None


def _head_sha(repo: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True, timeout=20).stdout.strip() or "?"
    except Exception:
        return "?"


def store_pass(rel: str, key: str, secs: float, repo: Path) -> None:
    store = cache_dir()
    for old in store.glob(f"{Path(rel).stem}__*.json"):      # one live entry per test
        old.unlink(missing_ok=True)
    rec = {"test": rel, "key": key, "date": time.strftime("%Y-%m-%d"), "sha": _head_sha(repo), "secs": round(secs, 1)}
    tmp = _entry(store, rel, key).with_suffix(f".tmp{os.getpid()}")
    tmp.write_text(json.dumps(rec))
    os.replace(tmp, _entry(store, rel, key))


def forget(rel: str) -> None:
    for old in cache_dir().glob(f"{Path(rel).stem}__*.json"):
        old.unlink(missing_ok=True)


def hit_line(rel: str, key: str, rec: dict) -> str:
    return f"CACHED PASS {rel} key={key} from {rec.get('date')} {rec.get('sha')}"


if __name__ == "__main__":      # the selftest*.py glob picks this library up; say so instead of a silent pass
    print("selftest_cache.py is a library; its test is selftest_selftest_cache.py")
