"""The known-result ledger: run_selftests.py does not re-run a test whose MEASURED inputs have not changed.

Owner, on testing: "they would say 'yup, testing things I already knew again.'" (plan C3, requirement TE2.) Each record
says: this test, given exactly these inputs, passed, in N seconds. If every input still hashes the same the stored
answer comes back and nothing runs. To run it anyway a caller has to say what could differ (`--because`).

A false "unchanged" is far worse than a rerun, so nothing here is declared by hand and nothing unobserved is trusted:

  How dependencies are found. Every process of a traced test is measured from two sides: a libc LD_PRELOAD shim
  (suite_trace/rm_preload.c, for native programs as much as for python) and the python audit tracer
  (suite_trace/sitecustomize.py). `analyse` turns that into a manifest: files read, directories listed, paths probed,
  environment names read, tool binaries run, imports tried.

  No observation, no record. The shim writes an "@" line in every process it reaches. A successful exec with no "@"
  line (a static or Go binary, a Windows .exe, a child whose environment was cleared) or a python process with no tracer
  start file (python -I) means part of the run was unseen, and `analyse` refuses. A test that fails to record simply
  runs every time; the failure mode is a rerun.

  Never cached (`analyse` taints these, whatever the result): the network; the wall clock read by a python process or a
  `date`; the live game and the Windows drives; /proc and /sys machine state; the repository's own git state; the
  sweep-wide derived-file cache; a shared temp file the test did not write; a pre-existing file the test both reads and
  writes; a file that changed during the run.

  Only PASS comes back. A red is written down so the runner can say "KNOWN RED: last failed on these inputs" and it is
  run again every time. A red exists to make somebody look, and a stored red cannot be told from a transient one (the
  2026-10-31 nightly had 12 dotnet timeouts under contention): returning it would pin a passing test red until an input
  happened to change. CRASH and UNMEASURED reached no verdict, so they are stored as nothing at all.

  The audit. Whatever the instrument cannot see (a raw syscall; ld.so's own opens, so a project-local library an extension links; a file's mtime that a test turns into
  behaviour; a timestamp logging.LogRecord took that a test then branches on; a name absent from an environment python walked
  whole; a native program outside ENV_IMPORTERS reading `environ` directly; file identity, as in os.path.samefile; the order a directory enumerates in) is what the nightly's sample exists for: a fixed
  share of the tests with a live answer is run for real anyway (`audit_sample`), and a PASS that comes back as anything
  else is a FALSE HIT: an alarm, a red run, the test's records deleted and the test quarantined from the ledger until
  someone clears it with --because.

The instrument has a second reader. A record only says "these inputs"; it never says the test is good, and a stored PASS
is not close evidence (it reports detail "cached", which review AD2 refuses).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat as _stat
import subprocess
import sys
import time
from pathlib import Path

VERSION = "1"
HERE = Path(__file__).resolve().parent
TRACE_DIR = HERE / "suite_trace"
SHIM_SRC = TRACE_DIR / "rm_preload.c"
TRACER = TRACE_DIR / "sitecustomize.py"
ARM_ENV = "RM_SELFTEST_ARM"             # run_selftests: {"trace", "preload", "pythonpath"} for the process that runs the test
AUDIT_RATE = 0.10                       # the nightly's share of live answers that run anyway
RECORDS_PER_TEST = 6                    # two branches, or a revert, should each still hit
TIME_SLOP_S = 2                         # a file touched this close to the run's start may have changed under it

# Set per run, per test or per seat, and carrying a path the manifest already follows, never a verdict.
ENV_PER_RUN = {"TMPDIR", "TMP", "TEMP", "RM_SELFTEST_TRACE", "RM_SELFTEST_CACHE_DIR", "RM_SELFTEST_NESTED", ARM_ENV,
               "RM_SELFTEST_STATE_DIR", "RM_SELFTEST_LOCK", "LD_PRELOAD", "PWD", "OLDPWD", "SHLVL", "_", "LS_COLORS",
               "RM_SELFTEST_TRACE_COVERS", "CLAUDE_CODE_SSE_PORT"}
# In the key whether or not anything was seen reading them: a process can reach these without going through getenv.
ENV_ALWAYS = ("PATH", "HOME", "USER", "LANG", "LC_ALL", "LC_CTYPE", "LC_COLLATE", "TZ", "PYTHONHASHSEED", "PYTHONUTF8",
              "PYTHONDONTWRITEBYTECODE", "PYTHONWARNINGS", "PYTHONOPTIMIZE", "PYTHONPATH", "PYTHONHOME", "LD_LIBRARY_PATH")
PACKAGES = "/var/lib/dpkg/status"       # every shared library ld.so loads comes from a package; ld.so's opens are not visible
DEV_OK = ("/dev/null", "/dev/urandom", "/dev/random", "/dev/zero", "/dev/tty", "/dev/full", "/dev/stdin", "/dev/stdout",
          "/dev/stderr", "/dev/pts/", "/dev/fd/", "/dev/shm/", "/dev/ptmx")
PROC_OK = ("/proc/self/", "/proc/thread-self/", "/proc/filesystems", "/proc/sys/kernel/random/", "/proc/sys/crypto/fips_enabled", "/proc/sys/vm/overcommit")
EXTERNAL = ("/mnt/", "/media/", "/net/")   # the Windows drives: the live game, its logs, other machines
LOCAL_TREES = ("/mnt/d/Luke/dev",)         # ...but this is source on a local disk (Lodestar, Waypoint on sys.path): it hashes
CLOCK_TOOLS = {"date"}
# These copy the whole environment into their own tables and never call getenv: every name is a dependency, absent ones too.
ENV_IMPORTERS = {"sh", "dash", "bash", "zsh", "ksh", "busybox", "perl", "awk", "gawk", "mawk"}
ENV_WHOLE = "*"                         # the pseudo-name in a record's env for "all of it"
ENV_NOISE = ("CLAUDE", "RM_SELFTEST", "CODEX")      # which session is asking is not an input


# --- the shim -----------------------------------------------------------------------------------------------------------
def build_shim(state_dir: Path):
    """Path of the shim compiled from the current source, or None: no shim, no ledger, everything simply runs."""
    try:
        src = SHIM_SRC.read_bytes()
        out = Path(state_dir) / "known_results" / f"rm_preload_{hashlib.sha1(src).hexdigest()[:12]}.so"
        if out.is_file():
            return out
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_suffix(f".tmp{os.getpid()}")
        r = subprocess.run(["gcc", "-O1", "-w", "-shared", "-fPIC", "-o", str(tmp), str(SHIM_SRC), "-ldl"],
                           capture_output=True, text=True, timeout=60)
        if r.returncode:
            print(f"known results: shim did not compile: {r.stderr[-200:]}", file=sys.stderr)
            return None
        os.replace(tmp, out)
        return out
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"known results: no shim ({type(exc).__name__}: {exc})", file=sys.stderr)
        return None


def arm_env(trace_dir: Path, shim: Path) -> dict:
    """The environment for a measured run. The tracer and shim are NOT switched on here but by the process about to
    exec the test (`armed`): between the runner and the test stand systemd-run and the harness wrapper, and neither of
    them is the test."""
    Path(trace_dir).mkdir(parents=True, exist_ok=True)
    return dict(os.environ, **{ARM_ENV: json.dumps({"trace": str(trace_dir), "preload": str(shim),
                                                    "pythonpath": str(TRACE_DIR)})})


def armed(env=None) -> dict | None:
    """The environment to exec the test with, or None if this run is not measured."""
    src = os.environ if env is None else env
    raw = src.get(ARM_ENV)
    if not raw:
        return None
    arm = json.loads(raw)
    out = {k: v for k, v in src.items() if k != ARM_ENV}
    out["RM_SELFTEST_TRACE"] = arm["trace"]
    out["PYTHONPATH"] = os.pathsep.join([arm["pythonpath"]] + [p for p in out.get("PYTHONPATH", "").split(os.pathsep) if p])
    out["LD_PRELOAD"] = ":".join(p for p in (arm["preload"], out.get("LD_PRELOAD", "")) if p)
    return out


# --- from a trace directory to a manifest ---------------------------------------------------------------------------------
def _load_trace(trace_dir: Path) -> dict:
    t = {"py": [], "starts": set(), "native": []}
    for f in Path(trace_dir).iterdir():
        if f.name.endswith(".start"):
            t["starts"].add(f.name[:-6])
        elif f.name.endswith(".json"):
            try:
                t["py"].append(dict(json.loads(f.read_text()), pid=f.name[:-5]))
            except ValueError:
                t.setdefault("broken", []).append(f.name)
        elif f.name.endswith(".native"):
            t["native"].append(f)
    return t


def _under(p: str, roots) -> bool:
    return any(p == r or p.startswith(r.rstrip("/") + "/") for r in roots if r)


def analyse(trace_dir: Path, repo: Path, own_tmp: str, started: float) -> dict:
    """{"refused": [reasons], "files", "absent", "lists", "import_lists", "probes", "env"}. Any reason means no record."""
    repo = str(Path(repo).resolve())
    trace_dir = Path(trace_dir)
    tr = _load_trace(trace_dir)
    refused: list = []
    read, wrote, listed, probed, envs = set(), set(), set(), set(), set()
    import_dirs, imports, exes, clock_by = set(), set(), set(), set()
    if not tr["native"]:
        refused.append("unobserved: the shim wrote nothing")
    if tr.get("broken"):
        refused.append("unobserved: a tracer file is unreadable")
    linked = set()
    execs = lands = 0
    pythons = set()
    finder = {d["pid"]: set(d.get("import_dirs", [])) for d in tr["py"]}
    for f in tr["native"]:
        pid = f.name[:-7]
        try:
            lines = f.read_text(encoding="utf-8", errors="surrogateescape").splitlines()
        except OSError:
            refused.append("unobserved: a shim log is unreadable")
            continue
        for ln in lines:
            op, val = ln[:1], ln[2:]
            if op in "RSLK" and "/../" in val and os.path.realpath(val) != os.path.realpath(os.path.normpath(val)):
                refused.append(f"unobserved: .. through a symlink, the name is not the file: {val}")
            if op == "P":
                pythons.add(pid)
            elif op == "@":
                lands += 1
                exes.add(val)
                if re.fullmatch(r"python[\d.]*", os.path.basename(val)):
                    pythons.add(pid)
            elif op == "R":
                read.add(_source_of(os.path.normpath(val)))
            elif op == "K":
                linked.add(os.path.normpath(val))
            elif op == "W":
                wrote.add(os.path.normpath(val))
            elif op == "L":
                # python's import system lists every sys.path dir; its own tracer says which ones and what for
                if os.path.normpath(val) not in finder.get(pid, ()):
                    listed.add(os.path.normpath(val))
            elif op == "S":
                probed.add(os.path.normpath(val))
            elif op == "E":
                envs.add(val)
            elif op == "X":
                execs += 1
                if os.path.basename(val) in CLOCK_TOOLS:
                    refused.append(f"clock: ran {os.path.basename(val)}")
                if "/" in val:          # @ only hashes where it landed: the name is what a retargeted link changes
                    probed.add(os.path.normpath(val))
                else:                   # execvp walks PATH: a new file early on it takes the place of the one found
                    probed.update(os.path.join(d or ".", val) for d in os.environ.get("PATH", "").split(os.pathsep))
            elif op == "F":
                execs -= 1
            elif op == "N":
                refused.append(f"network: {val}")
            elif op == "U":
                refused.append(f"network: unix socket {val}")
            elif op == "C":
                refused.append("clock: a python process read the wall clock")
    if lands < execs + 1:
        refused.append(f"unobserved: {execs + 1 - lands} of {execs} exec(s) landed where the shim cannot see")
    missing = pythons - tr["starts"]
    if missing:
        refused.append(f"unobserved: {len(missing)} python process(es) ran without the tracer")
    if len(tr["py"]) < len(tr["starts"]):
        refused.append("unobserved: a python process died before its trace was written")
    for d in tr["py"]:
        read |= {_source_of(p) for p in d.get("read", [])}
        wrote |= set(d.get("wrote", []))
        listed |= set(d.get("listed", []))
        probed |= set(d.get("probed", []))
        envs |= set(d.get("env", []))
        import_dirs |= set(d.get("import_dirs", []))
        clock_by |= set(d.get("clock_by", []))
        imports |= {part for m in d.get("imports", []) for part in m.split(".")}
        for t in d.get("taint", []):
            if t not in ("os.fork", "os.forkpty", "os.exec", "os.system", "os.spawn"):
                refused.append("taint: " + t)      # exec and friends are measured now: the "@" count covers them
        for m in d.get("modules", []):
            if m.endswith((".so", ".pyd", ".py")):  # dlopen is ld.so's, and a valid .pyc leaves the source only stat'ed
                read.add(m)
    read |= {e for e in exes if e}

    tmp_root = os.path.dirname(own_tmp) if own_tmp else ""
    mine = (own_tmp, str(trace_dir))

    def keep(p: str) -> bool:
        """False for what is no input at all. Refuses for what must never be cached."""
        if not p.startswith("/"):
            return False
        if _under(p, mine) or "/__pycache__/" in p or p.endswith(".pyc") or p.startswith("/rm-selftest/"):
            return False
        if p.startswith("/dev/"):
            if not any(p == d or p.startswith(d) for d in DEV_OK if d):
                refused.append(f"machine state: {p}")
            return False
        if p in ("/proc", "/sys", "/dev") or _under(str(trace_dir), (p,)):
            return False                             # the tracer walking down to its own folder is not the test
        if p.startswith("/proc/"):
            if not any(p.startswith(o) for o in PROC_OK):
                refused.append(f"machine state: {p}")
            return False
        if p.startswith("/sys/"):
            refused.append(f"machine state: {p}")
            return False
        if p in ("/mnt", "/mnt/d", "/mnt/d/Luke") or _under(p, LOCAL_TREES):
            return p not in ("/mnt", "/mnt/d", "/mnt/d/Luke")
        if _under(p, EXTERNAL) and not _under(p, (repo,)):
            refused.append(f"external: {p}")
            return False
        if "/.git/" in p + "/" and _under(p, (repo,)) and p not in wrote:
            refused.append("git state")
            return False
        if os.environ.get("RM_SELFTEST_CACHE_DIR") and _under(p, (os.environ["RM_SELFTEST_CACHE_DIR"],)):
            refused.append("shares the sweep's derived cache")
            return False
        return True

    for p in sorted(linked):            # a link in the test's own TMPDIR is exempt, what it points at is not
        if p in wrote and not os.path.lexists(p):
            continue                    # a temp name renamed into place: the test's own, and gone
        if keep(p) and os.path.isdir(p):
            refused.append(f"unobserved: a link to the directory {p} hides what is read through it")
        else:
            read.add(p)

    files, absent = [], []
    for p in sorted(read):
        if not keep(p):
            continue
        if p in wrote:      # the order of the two is not kept, so "it made this itself" cannot be told from "it changed
            refused.append(f"reads and writes {p}")  # what it read": anything outside its own TMPDIR counts as the second
            continue
        if _under(p, ("/tmp", "/var/tmp", tmp_root)) and p != tmp_root:
            refused.append(f"shared temp: {p}")
            continue
        (files if os.path.isfile(p) else absent).append(p)
    lists = [p for p in sorted(listed) if keep(p) and p not in wrote and not _under(p, (tmp_root,))]
    for p in sorted(listed):
        if keep(p) and p not in wrote and _under(p, (tmp_root,)):
            refused.append(f"shares: listed shared temp {p}")   # what strangers leave there is what a glob of it answers
    idirs = [p for p in sorted(import_dirs - listed) if keep(p) and not _under(p, (tmp_root,))]
    probes = []
    for p in sorted(probed - read - listed):
        if not keep(p) or p in wrote or p == tmp_root:
            continue
        if _under(p, ("/tmp", "/var/tmp", tmp_root)):       # "is the switch file absent" is an input, wherever it is
            if p in ("/tmp", "/var/tmp") or _under(tmp_root, (p,)):
                continue
            if os.path.lexists(p):
                refused.append(f"shared temp: {p}")
                continue
        probes.append(p)
    candidates = [os.path.join(d, n) for d in idirs for n in _names(d) if n.split(".")[0] in imports]
    changed = moved(files + lists + candidates, started)
    if changed:
        refused.append(f"changed during the run: {changed}")
    env = {n for n in envs | set(ENV_ALWAYS) if n not in ENV_PER_RUN}
    if {os.path.basename(e) for e in exes} & ENV_IMPORTERS:
        env.add(ENV_WHOLE)
    env = sorted(env)
    return {"refused": sorted(set(refused)), "files": files, "absent": absent, "lists": lists, "import_dirs": idirs,
            "imports": sorted(imports), "probes": probes, "env": env, "clock_by": sorted(clock_by)}


def _source_of(p: str) -> str:
    """The .py a cached .pyc stands for: a valid .pyc leaves the source only stat'ed, and a stat keeps type and size."""
    m = re.fullmatch(r"(.*)/__pycache__/([^/]+?)\.[^/.]+(\.opt-\d+)?\.pyc", p)
    return f"{m.group(1)}/{m.group(2)}.py" if m else p


def _names(d: str) -> list:
    try:
        return os.listdir(d)
    except OSError:
        return []


def moved(paths, started: float) -> str:
    """The first path touched since the run began, else "". A dir counts: a file landing in a listed dir mid-run means
    the test saw one listing and the record would hold another."""
    for p in paths:
        try:
            st = os.stat(p)
        except OSError:
            continue                        # gone since: the caller hashes it next and finds that out
        if max(st.st_mtime, st.st_ctime) >= started - TIME_SLOP_S:
            return p
    return ""


# --- hashing ------------------------------------------------------------------------------------------------------------
class Hasher:
    """Content hash per file, memoised on (path, size, mtime, ctime), so a hit costs stats and not reads."""

    def __init__(self, store: Path):
        self.path = Path(store) / "statcache.json"
        try:
            self.memo = json.loads(self.path.read_text())
        except (OSError, ValueError):
            self.memo = {}
        self.dirty = False

    def file(self, p: str):
        try:                    # a stat every time: a sweep is long, and a sibling edits files while it runs
            link = self._link(p)
            st = os.stat(p)
            if not _stat.S_ISREG(st.st_mode):
                h = "not-a-file" if not _stat.S_ISDIR(st.st_mode) else "dir"
            else:
                k = f"{p}|{st.st_size}|{st.st_mtime_ns}|{st.st_ctime_ns}"
                h = self.memo.get(k)
                if h is None:
                    with open(p, "rb") as f:
                        h = hashlib.sha1(f.read()).hexdigest()
                    self.memo[k] = h
                    self.dirty = True
                h = f"{h}:{_stat.S_IMODE(st.st_mode):o}"
        except OSError:
            h = None
        return link + h if link and h else h

    @staticmethod
    def _link(p: str) -> str:
        """A symlink's own text: readlink() is an answer that two links to identical files do not share."""
        try:
            return "link:" + os.readlink(p) + ":"
        except OSError:
            return ""

    def probe(self, p: str):
        """What a stat of p tells: its type, permissions and a file's size. mtime stays out, or every checkout is a miss."""
        link = Hasher._link(p)
        try:
            st = os.stat(p)
        except OSError:
            return link or None
        mode = oct(_stat.S_IMODE(st.st_mode))
        return link + (f"d{mode}" if _stat.S_ISDIR(st.st_mode) else f"f{st.st_size}:{mode}")

    @staticmethod
    def listing(p: str, keep=None):
        try:
            with os.scandir(p) as it:
                entries = sorted(it, key=lambda e: e.name)
            if keep is not None:
                entries = [e for e in entries if e.name.split(".")[0] in keep]
            # DirEntry.is_file() answers from this listing without a stat, so the kind of each entry is part of what was read
            names = [e.name + ("@" if e.is_symlink() else "/" if e.is_dir() else "") for e in entries]
        except OSError:
            return None
        return hashlib.sha1("\0".join(names).encode("utf-8", "surrogateescape")).hexdigest()

    def save(self):
        if not self.dirty:
            return
        if len(self.memo) > 300000:
            self.memo = {}
        tmp = self.path.with_name(f"{self.path.name}.{os.getpid()}")
        try:
            tmp.write_text(json.dumps(self.memo))
            os.replace(tmp, self.path)
            self.dirty = False
        except OSError:
            pass


def _env_value(name: str):
    if name == ENV_WHOLE:
        rows = sorted(f"{n}={v}" for n, v in os.environ.items() if n not in ENV_PER_RUN and n not in ("PYTHONPATH",)
                      and not n.startswith(ENV_NOISE))
        return hashlib.sha1("\0".join(rows).encode("utf-8", "surrogateescape")).hexdigest()[:16]
    v = os.environ.get(name)
    if name == "PYTHONPATH" and v:
        v = os.pathsep.join(p for p in v.split(os.pathsep) if p != str(TRACE_DIR))
    return None if v is None else hashlib.sha1(v.encode("utf-8", "surrogateescape")).hexdigest()[:16]


def runner_version() -> str:
    h = hashlib.sha1(f"{VERSION}|{sys.version}|{sys.executable}".encode())
    for p in (HERE / "run_selftests.py", Path(__file__).resolve(), TRACER, SHIM_SRC):
        h.update(p.read_bytes())
    try:
        h.update(str(os.stat(PACKAGES).st_size).encode() + b"|" + str(os.stat(PACKAGES).st_mtime_ns).encode())
    except OSError:
        pass
    return h.hexdigest()[:16]


# --- the ledger -----------------------------------------------------------------------------------------------------------
class Ledger:
    def __init__(self, repo: Path, state_dir: Path):
        self.repo = str(Path(repo).resolve())
        self.dir = Path(state_dir) / "known_results"
        self.rec_dir = self.dir / "records"
        self.rec_dir.mkdir(parents=True, exist_ok=True)
        self.hash = Hasher(self.dir)
        self.version = runner_version()
        self.quarantine_file = self.dir / "quarantine.json"
        self.run = {"hits": 0, "misses": 0, "saved_s": 0.0, "refused": {}, "audited": 0, "false_hits": [], "drift": 0}

    # paths: a file in the repo is keyed relative to it, so two clones with the same inputs share an answer
    def _key(self, p: str) -> str:
        if p == self.repo:
            return "."
        return p[len(self.repo) + 1:] if p.startswith(self.repo + "/") else p

    def _abs(self, k: str) -> str:
        return k if k.startswith("/") else os.path.join(self.repo, k)

    def _path(self, rel: str) -> Path:
        return self.rec_dir / (rel.replace("/", "__") + ".json")

    def _load(self, rel: str) -> list:
        try:
            return json.loads(self._path(rel).read_text())
        except (OSError, ValueError):
            return []

    def _save(self, rel: str, recs: list) -> None:
        tmp = self._path(rel).with_suffix(f".tmp{os.getpid()}")
        tmp.write_text(json.dumps(recs))
        os.replace(tmp, self._path(rel))

    def manifest_inputs(self, rel: str, m: dict) -> dict:
        h = self.hash
        imports = set(m["imports"])
        return {"runner": self.version,
                "files": {self._key(p): h.file(p) for p in m["files"]},
                "absent": [self._key(p) for p in m["absent"]],
                "lists": {self._key(p): h.listing(p) for p in m["lists"]},
                "import_dirs": {self._key(p): h.listing(p, imports) for p in m["import_dirs"]},
                "imports": m["imports"],
                "probes": {self._key(p): h.probe(p) for p in m["probes"]},
                "env": {n: _env_value(n) for n in m["env"]}}

    def first_difference(self, rec: dict):
        """None if the world still matches the record, else the first input that does not."""
        h = self.hash
        if rec.get("runner") != self.version:
            return "runner, tracer or package set"
        for n, v in rec["env"].items():
            if _env_value(n) != v:
                return f"env {n}"
        for k, v in rec["files"].items():
            if h.file(self._abs(k)) != v:
                return k
        for k in rec["absent"]:
            if os.path.lexists(self._abs(k)):
                return f"{k} (appeared)"
        for k, v in rec["lists"].items():
            if h.listing(self._abs(k)) != v:
                return f"{k}/ (listing)"
        keep = set(rec["imports"])
        for k, v in rec["import_dirs"].items():
            if h.listing(self._abs(k), keep) != v:
                return f"{k}/ (a new importable name)"
        for k, v in rec["probes"].items():
            if h.probe(self._abs(k)) != v:
                return f"{k} (stat)"
        return None

    def lookup(self, rel: str):
        """(record or None, why): the newest record whose every input still matches. Reds are found but never returned
        as an answer: the caller gets ("red", record) to say so and run it."""
        recs = self._load(rel)
        why = "no record"
        for rec in recs:
            d = self.first_difference(rec)
            if d is None:
                return rec, ""
            if why == "no record":
                why = d
        return None, why

    def quarantined(self) -> dict:
        try:
            return json.loads(self.quarantine_file.read_text())
        except (OSError, ValueError):
            return {}

    def quarantine(self, rel: str, why: str) -> None:
        q = self.quarantined()
        q[rel] = why
        self.quarantine_file.write_text(json.dumps(q, indent=0))

    def clear_quarantine(self, rel: str) -> None:
        q = self.quarantined()
        if q.pop(rel, None) is not None:
            self.quarantine_file.write_text(json.dumps(q, indent=0))

    def record(self, rel: str, state: str, secs: float, trace_dir: Path, own_tmp: str, started: float, test: Path):
        """Write down a finished run. (saved?, why not). PASS and FAIL have verdicts; anything else leaves no record."""
        if state not in ("PASS", "FAIL"):
            return False, f"{state} reached no verdict"
        m = analyse(trace_dir, Path(self.repo), own_tmp, started)
        if m["refused"]:
            self.forget(rel)
            self._append("refusals.jsonl", {"test": rel, "why": m["refused"][:12], "clock_by": m["clock_by"][:12]})
            return False, m["refused"][0]
        if str(test) not in m["files"]:
            m["files"].append(str(test))           # the test's own text, even if some path above lost it
        rec = dict(self.manifest_inputs(rel, m), test=rel, state=state, secs=round(secs, 2),
                   date=time.strftime("%Y-%m-%d %H:%M"), sha=_head(Path(self.repo)))
        if any(v is None for v in rec["files"].values()) or moved(m["files"] + m["lists"], started):
            self.forget(rel)
            return False, "changed during the run: an input moved while it was being hashed"
        recs = [r for r in self._load(rel) if self._inputs(r) != self._inputs(rec)]
        self._save(rel, ([rec] + recs)[:RECORDS_PER_TEST])
        return True, ""

    @staticmethod
    def _inputs(r: dict):
        return json.dumps({k: r.get(k) for k in ("runner", "files", "absent", "lists", "import_dirs", "probes", "env")},
                          sort_keys=True)

    def forget(self, rel: str) -> None:
        self._path(rel).unlink(missing_ok=True)

    def note_forced(self, reason: str, tests: int, argv: list) -> None:
        self._append("forced.jsonl", {"ts": _stamp(), "because": reason, "tests": tests, "argv": argv})

    def note_run(self, row: dict) -> None:
        self._append("runs.jsonl", dict(row, ts=_stamp()))

    def _append(self, name: str, row: dict) -> None:
        with open(self.dir / name, "a") as f:
            f.write(json.dumps(row) + "\n")


def _stamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _head(repo: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              timeout=20).stdout.strip() or "?"
    except (OSError, subprocess.SubprocessError):
        return "?"


def audit_sample(rel: str, day: str, rate: float = AUDIT_RATE) -> bool:
    """Is this test in tonight's sample? Fixed by (test, date): reproducible, rotates over the suite, never chosen."""
    return int(hashlib.sha256(f"{rel}|{day}".encode()).hexdigest()[:8], 16) < rate * 2 ** 32


def false_hit(stored_state: str, state: str) -> bool:
    """The whole audit in one line: the ledger said PASS on these inputs and a real run said anything but."""
    return stored_state == "PASS" and state != "PASS"


if __name__ == "__main__":      # the selftest*.py glob does not match; say what this is if it is run
    print("known_results.py is a library; its test is selftest_known_results.py")
