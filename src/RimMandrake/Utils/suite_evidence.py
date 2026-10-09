"""Skip-when-unchanged evidence records for run_selftests.py (owner card 2026-10-08, audit §8 #4).

A test may be SKIPPED only on evidence: its last run PASSED, that run was fully traced (suite_trace/sitecustomize.py
in every python process it spawned), and every input that run touched is byte-identical now. Anything not provably
covered means RUN. The rules, in the order they bite:

  eligible   only tests that opt in (`# selftest-skip: eligible` in the first 40 lines) or belong to a deterministic
             family: planted-defect lint selftests (import modpack_lint_harness) and fixed-seed kernel fuzz
             (`selftest_*_fuzz.py` calling winbuild.stage_build). Every other test always runs.
  traced     a record is written only from a PASS whose trace is complete (each python process that started also
             wrote its trace) and clean: no read or listing outside the repo / interpreter / temp dirs (deployed mods,
             /mnt/c, the def dump => never recorded), no network, no os.system/fork/exec, no unknown child program,
             no python child that dropped the tracer, no input modified while the test ran.
  inputs     files read (minus files the test itself wrote), every imported module file, every directory listed (its
             sorted entry names), every in-repo path whose existence was probed (present/absent), and the repo trees an
             rsync child copied (winbuild stages fuzz kernels that way; rsync's own --exclude list applies).
  version    each record carries RUNNER_VERSION (hash of run_selftests.py + this file + the tracer) and the python
             version; any change to either invalidates every record.

A non-PASS result deletes the test's record. `--full` / `--no-skip` ignores records (and re-records on PASS).
Records live in ~/.local/state/rm-selftests/records/<repo-key>/ — a program reads them, so not in the repo.
"""
import fnmatch
import hashlib
import json
import os
import shutil
import sys
import sysconfig
import tempfile
import time
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRACER_DIR = HERE / "suite_trace"
_VERSION_FILES = (HERE / "run_selftests.py", Path(__file__).resolve(), TRACER_DIR / "sitecustomize.py")
RUNNER_VERSION = hashlib.sha1(b"".join(p.read_bytes() for p in _VERSION_FILES)).hexdigest()[:16]

ELIGIBLE_TAG = "# selftest-skip: eligible"
# Programs a traced test may spawn without making its closure unknowable. rsync is handled specially (its sources
# become inputs); the rest are the Windows build toolchain operating on a staged COPY of hashed inputs, and git used
# read-only for a version string (winbuild.source_sha).
TOOLCHAIN = {"dotnet.exe", "cmd.exe", "powershell.exe", "wslpath", "git"}


def _allowed_outside(tmp_roots):
    roots = {sys.prefix, sys.base_prefix, sys.exec_prefix, "/usr/lib", "/usr/share", "/usr/local/lib", "/etc",
             "/proc", "/sys", "/dev", "/lib", "/usr/lib64", "/run/user"}
    for k in ("stdlib", "platstdlib", "purelib", "platlib"):
        v = sysconfig.get_paths().get(k)
        if v:
            roots.add(v)
    roots.add(str(Path.home() / ".local/lib"))
    roots.add(str(Path.home() / ".local/venvs"))
    # winbuild's stage holds the build OUTPUT of hashed inputs (the rsync'd trees), so reading it back is fine.
    roots.add(os.environ.get("WINBUILD_ROOT", "/mnt/d/Luke/dev/_rmbuild"))
    roots |= set(tmp_roots)
    return tuple(os.path.join(os.path.normpath(r), "") for r in roots if r)


def eligible(path: Path, head: str) -> str:
    """'' if not eligible, else the reason it is."""
    if ELIGIBLE_TAG in head:
        return "declared eligible"
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    if "import modpack_lint_harness" in text:
        return "planted-defect lint family"
    if path.name.endswith("_fuzz.py") and "winbuild.stage_build" in text:
        return "fixed-seed fuzz family"
    return ""


class Hasher:
    """Content hashes memoised for one run (lint tests share thousands of inputs)."""
    def __init__(self):
        self.files, self.dirs = {}, {}

    def file(self, p: str):
        if p not in self.files:
            try:
                with open(p, "rb") as f:
                    self.files[p] = hashlib.sha1(f.read()).hexdigest()
            except OSError:
                self.files[p] = None
        return self.files[p]

    def listing(self, p: str):
        if p not in self.dirs:
            try:
                self.dirs[p] = hashlib.sha1("\0".join(sorted(os.listdir(p))).encode("utf-8", "surrogateescape")).hexdigest()
            except OSError:
                self.dirs[p] = None
        return self.dirs[p]


class Store:
    def __init__(self, repo_root: Path, state_dir: Path):
        self.repo = Path(repo_root).resolve()
        key = hashlib.sha1(str(self.repo).encode()).hexdigest()[:12]
        self.dir = Path(state_dir) / "records" / key
        self.hasher = Hasher()

    def _p(self, rel: str) -> Path:
        return self.dir / (hashlib.sha1(rel.encode()).hexdigest()[:20] + ".json.z")

    def load(self, rel: str):
        try:
            return json.loads(zlib.decompress(self._p(rel).read_bytes()))
        except (OSError, ValueError, zlib.error):
            return None

    def forget(self, rel: str) -> None:
        try:
            self._p(rel).unlink()
        except OSError:
            pass

    def save(self, rec: dict) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        p = self._p(rec["test"])
        tmp = p.with_suffix(".tmp%d" % os.getpid())
        tmp.write_bytes(zlib.compress(json.dumps(rec, sort_keys=True).encode(), 6))
        os.replace(tmp, p)

    # ---- the skip decision ------------------------------------------------------------------
    def unchanged(self, rel: str):
        """(True, why) if the recorded PASS still holds for byte-identical inputs, else (False, why)."""
        rec = self.load(rel)
        if rec is None:
            return False, "no evidence record"
        if rec.get("version") != RUNNER_VERSION:
            return False, "runner changed since the record"
        if rec.get("python") != sys.version:
            return False, "python changed since the record"
        if rec.get("state") != "PASS":
            return False, "last result was not PASS"
        h = self.hasher
        for kind, table, fn in (("file", rec["files"], h.file), ("dir", rec["dirs"], h.listing)):
            for rp, want in table.items():
                if fn(str(self.repo / rp)) != want:
                    return False, f"{kind} changed: {rp}"
        for rp, existed in rec["probed"].items():
            if os.path.lexists(self.repo / rp) != existed:
                return False, f"path {'vanished' if existed else 'appeared'}: {rp}"
        n = len(rec["files"]) + len(rec["dirs"]) + len(rec["probed"])
        return True, (f"unchanged since its PASS at {time.strftime('%m-%d %H:%M', time.localtime(rec['at']))} "
                      f"({n} inputs byte-identical)")

    # ---- tracing one run --------------------------------------------------------------------
    def trace_env(self, trace_dir: Path) -> dict:
        trace_dir.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ)
        env["RM_SELFTEST_TRACE"] = str(trace_dir)
        env["PYTHONPATH"] = os.pathsep.join([str(TRACER_DIR)] + [p for p in env.get("PYTHONPATH", "").split(os.pathsep) if p])
        return env

    def record(self, rel: str, trace_dir: Path, secs: float):
        """Build and save the record from a PASSED traced run; (saved?, why not)."""
        rec, why = self.build(rel, trace_dir, secs)
        if rec is None:
            self.forget(rel)
            return False, why
        self.save(rec)
        return True, f"{len(rec['files'])} files, {len(rec['dirs'])} dirs, {len(rec['probed'])} probes"

    def build(self, rel: str, trace_dir: Path, secs: float):
        starts = {p.name.split(".")[0] for p in trace_dir.glob("*.start")}
        traces = []
        for p in trace_dir.glob("*.json"):
            try:
                traces.append(json.loads(p.read_text()))
            except (OSError, ValueError):
                return None, f"unreadable trace {p.name}"
        if not traces:
            return None, "no trace (the tracer did not load)"
        missing = starts - {str(t["pid"]) for t in traces}
        if missing:
            return None, f"{len(missing)} traced process(es) died without writing a trace"
        repo = os.path.join(str(self.repo), "")
        tmp_roots = {tempfile.gettempdir(), os.environ.get("TMPDIR", ""), "/tmp", "/var/tmp",
                     os.environ.get("RM_SELFTEST_CACHE_DIR", ""), str(trace_dir)}
        allowed = _allowed_outside(tmp_roots)
        read, wrote, listed, probed, mtimes = set(), set(), set(), set(), {}
        for t in traces:
            if t["taint"]:
                return None, "untraceable: " + ", ".join(t["taint"])
            read |= set(t["read"]) | set(t["modules"])
            wrote |= set(t["wrote"])
            listed |= set(t["listed"])
            probed |= set(t["probed"])
            mtimes.update({k: v for k, v in t["mtimes"].items() if v is not None})
            for ch in t["children"]:
                ok, why = self._child(ch, listed, read)
                if not ok:
                    return None, why
        tracer = os.path.join(str(TRACER_DIR), "")
        # the tracer itself is covered by RUNNER_VERSION, not by the test's own inputs
        inputs = {p for p in read - wrote if "/__pycache__/" not in p and not p.startswith(tracer)}

        def inside(p):
            return p.startswith(repo)
        for p in sorted(inputs | listed):
            if not inside(p) and not p.startswith(allowed) and os.path.normpath(p) != str(self.repo):
                return None, f"reads outside the repo: {p}"
        h = Hasher()   # fresh: the record must describe the bytes on disk NOW, after the run
        files, dirs, probes = {}, {}, {}
        for p in sorted(x for x in inputs if inside(x)):
            if os.path.isdir(p):
                continue
            if p in mtimes:
                try:
                    if os.stat(p).st_mtime_ns != mtimes[p]:
                        return None, f"input changed while the test ran: {os.path.relpath(p, self.repo)}"
                except OSError:
                    return None, f"input vanished while the test ran: {os.path.relpath(p, self.repo)}"
            d = h.file(p)
            if d is None:
                continue   # an attempted open of a missing file: covered by the probe below
            files[os.path.relpath(p, self.repo)] = d
        for p in sorted(x for x in listed if inside(x) or x == str(self.repo)):
            dirs[os.path.relpath(p, self.repo)] = h.listing(p)
        for p in sorted(x for x in (probed | (read - set(files_abs(files, self.repo)))) if inside(x)):
            rp = os.path.relpath(p, self.repo)
            if rp not in files and rp not in dirs and p not in wrote and "/__pycache__/" not in p:
                probes[rp] = os.path.lexists(p)
        return {"test": rel, "version": RUNNER_VERSION, "python": sys.version, "state": "PASS", "at": time.time(),
                "secs": round(secs, 2), "files": files, "dirs": dirs, "probed": probes}, ""

    def _child(self, ch, listed, read):
        exe = os.path.basename(ch["exe"] or (ch["argv"][0] if ch["argv"] else ""))
        if exe.startswith("python") and not exe.endswith(".exe"):
            return (True, "") if ch["traced"] else (False, f"a python child ran without the tracer: {' '.join(ch['argv'])[:120]}")
        if exe == "rsync":
            return self._rsync(ch, listed, read)
        if exe in TOOLCHAIN or exe.lower().endswith(".exe"):
            if exe.lower() == "python.exe":
                return False, "a Windows python child cannot be traced"
            return True, ""
        return False, f"unknown child program {exe!r} (its inputs cannot be traced)"

    def _rsync(self, ch, listed, read):
        args, cwd, excl, srcs = ch["argv"][1:], ch["cwd"], [], []
        i = 0
        while i < len(args):
            a = args[i]
            if a == "--exclude" and i + 1 < len(args):
                excl.append(args[i + 1])
                i += 2
                continue
            if a.startswith("--exclude="):
                excl.append(a.split("=", 1)[1])
            elif not a.startswith("-"):
                srcs.append(a)
            i += 1
        repo = os.path.join(str(self.repo), "")
        for s in srcs[:-1]:   # the last operand is the destination
            p = os.path.normpath(os.path.join(cwd, s))
            if not (p + os.sep).startswith(repo):
                return False, f"rsync copies from outside the repo: {p}"
            if os.path.isfile(p):
                read.add(p)
                continue
            for d, subdirs, names in os.walk(p):
                subdirs[:] = [x for x in subdirs if not _excluded(x, excl, True)]
                listed.add(d)
                read.update(os.path.join(d, n) for n in names if not _excluded(n, excl, False))
        return True, ""


def files_abs(files, repo):
    return [str(Path(repo) / r) for r in files]


def _excluded(name, patterns, is_dir):
    for pat in patterns:
        if pat.endswith("/"):
            if is_dir and fnmatch.fnmatch(name, pat[:-1]):
                return True
        elif fnmatch.fnmatch(name, pat):
            return True
    return False


def clear_trace(trace_dir: Path) -> None:
    shutil.rmtree(trace_dir, ignore_errors=True)
