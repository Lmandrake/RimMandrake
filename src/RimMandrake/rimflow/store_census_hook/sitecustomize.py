"""The run-time hook of store_write_census.py (item RIMMANDRAKE_NARROW_CUTOVER_WRITER_CHECK_EIGHT_OF_THIRTEEN_READ).

Loaded by every Python process a census test starts, because the census puts this folder first on PYTHONPATH; inert
unless RM_STORE_CENSUS_DIR is set. It records, under that folder:
  - every open-for-writing of an old mod store (stage.json, journal.md, version/stage_record.json) and every rename onto
    one, with the src/RimMandrake files on the stack, innermost first: appended the moment it happens, so a process that
    dies afterwards still leaves it;
  - every Python child it starts that will carry no hook (-I, -S or -E, or an env without this folder on PYTHONPATH or
    without RM_STORE_CENSUS_DIR): the census cannot see into it, so it says so;
  - which code objects of src/RimMandrake files started (sys.monitoring PY_START, each disabled after its first start),
    written at exit: a process that dies without exiting leaves none, which reads as "never ran", never as "ran clean".
A file is named "<path from src/RimMandrake/>#<sha256 of its content, 16 hex>", so a fixture copy that differs from the
real module never stands in for it. Then it hands over to the next sitecustomize on sys.path, if any.
"""
import atexit
import hashlib
import json
import os
import sys
import threading

_OUT = os.environ.get("RM_STORE_CENSUS_DIR")
_HERE = os.path.dirname(os.path.abspath(__file__))
_MARK = "src/RimMandrake/"
_WFLAGS = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC
_KEYS = {}


def _key(fn):
    """-> "src/RimMandrake/...#sha16" for a file under src/RimMandrake, else None (cached per file name)."""
    if fn in _KEYS:
        return _KEYS[fn]
    s = str(fn).replace("\\", "/")
    i = s.rfind(_MARK)
    k = None
    if i >= 0:
        try:
            with open(fn, "rb") as f:
                k = s[i:] + "#" + hashlib.sha256(f.read()).hexdigest()[:16]
        except OSError:
            k = s[i:] + "#unreadable"
    _KEYS[fn] = k
    return k


def _norm(p, dir_fd=None):
    """-> the absolute, normalised path (a dir_fd resolved through /proc/self/fd), or None when it cannot be told."""
    p = os.fsdecode(p)
    if not os.path.isabs(p):
        if isinstance(dir_fd, int):
            try:
                base = os.readlink("/proc/self/fd/%d" % dir_fd)
            except OSError:
                return None
        else:
            base = os.getcwd()
        p = os.path.join(base, p)
    return os.path.normpath(p).replace("\\", "/")


def _is_store(p):
    """A store by name and place: stage.json or journal.md, or stage_record.json in a folder named version; nothing
    under a .git folder is one (seat_sync parks dirty copies there). None (cannot tell) counts as a store."""
    if p is None:
        return True
    parts = p.split("/")
    if ".git" in parts[:-1]:
        return False
    return parts[-1] in ("stage.json", "journal.md") or (parts[-1] == "stage_record.json" and len(parts) > 1
                                                           and parts[-2] == "version")


def _pathlike(x):
    return isinstance(x, (str, bytes, os.PathLike))


if _OUT:
    _BUSY = threading.local()          # per thread: another thread's store write is never skipped while one records
    _RAN = {}
    _TEST = os.environ.get("RM_STORE_CENSUS_TEST", "")

    def _chain():
        f, chain = sys._getframe(3), []
        while f is not None:
            k = _key(f.f_code.co_filename)
            if k and k not in chain:
                chain.append(k)
            f = f.f_back
        return chain

    def _record(event, path):
        _BUSY.on = True
        try:
            line = json.dumps({"event": event, "path": path, "chain": _chain(), "test": _TEST})
            with open(os.path.join(_OUT, "%d.writes.jsonl" % os.getpid()), "a", encoding="utf-8") as w:
                w.write(line + "\n")
        finally:
            _BUSY.on = False

    def _python(prog):
        p = os.fsdecode(prog or "")
        return os.path.basename(p).startswith("python") or p == sys.executable

    def _unhooked(args, env):
        """A Python child that will not load this hook -> its reason, else None."""
        if isinstance(args, (str, bytes)):
            argv = os.fsdecode(args).split()
        else:
            try:
                argv = [os.fsdecode(a) for a in args]
            except TypeError:
                return None
        if not argv or not _python(argv[0]):
            return None
        for a in argv[1:]:
            if not a.startswith("-") or a in ("-c", "-m"):
                break
            if not a.startswith("--") and any(c in a[1:] for c in "ISE"):
                return "started with %s" % a
        if env is not None:
            try:
                pp = os.fsdecode(env.get("PYTHONPATH") or env.get(b"PYTHONPATH") or "")
                has_dir = bool(env.get("RM_STORE_CENSUS_DIR") or env.get(b"RM_STORE_CENSUS_DIR"))
            except (AttributeError, TypeError):
                return None
            if _HERE not in pp.split(os.pathsep) or not has_dir:
                return "started with an env that drops the hook"
        return None

    def _audit(event, args):
        if getattr(_BUSY, "on", False):
            return
        if event == "open":
            path, mode, flags = (tuple(args) + (None, None, None))[:3]
            if not _pathlike(path):
                return
            if isinstance(flags, int):
                w = bool(flags & _WFLAGS)
            else:
                w = isinstance(mode, str) and any(c in mode for c in "wax+")
            if w:
                p = _norm(path)
                if _is_store(p):
                    _record("open", p)
        elif event == "os.rename" and len(args) >= 2 and _pathlike(args[1]):
            p = _norm(args[1], args[3] if len(args) > 3 else None)
            if _is_store(p):
                _record("rename", p)
        elif event == "subprocess.Popen" and len(args) >= 4:
            why = _unhooked(args[1], args[3])
            if why:
                _record("unhooked_child", why)

    sys.addaudithook(_audit)

    _M = sys.monitoring
    _TOOL = next((t for t in (4, 3) if _M.get_tool(t) is None), None)
    if _TOOL is not None:
        _M.use_tool_id(_TOOL, "rm_store_census")

        def _start(code, _off):
            k = _key(code.co_filename)
            if k:
                _RAN.setdefault(k, set()).add("%d:%s" % (code.co_firstlineno, code.co_name))
            return _M.DISABLE

        _M.register_callback(_TOOL, _M.events.PY_START, _start)
        _M.set_events(_TOOL, _M.events.PY_START)

    def _dump():
        if _TOOL is not None:
            _M.set_events(_TOOL, 0)
        _BUSY.on = True
        try:
            with open(os.path.join(_OUT, "%d.cov.json" % os.getpid()), "w", encoding="utf-8") as w:
                json.dump({"test": _TEST, "monitoring": _TOOL is not None,
                           "ran": {k: sorted(v) for k, v in _RAN.items()}}, w)
        except OSError:
            pass

    atexit.register(_dump)

# hand over to the sitecustomize this one shadows (Ubuntu's installs apport's crash handler)
try:
    import importlib.machinery
    import importlib.util
    _spec = importlib.machinery.PathFinder.find_spec(
        "sitecustomize", [p for p in sys.path if os.path.abspath(p or ".") != _HERE])
    if _spec is not None and _spec.loader is not None:
        _spec.loader.exec_module(importlib.util.module_from_spec(_spec))
except Exception:
    pass
