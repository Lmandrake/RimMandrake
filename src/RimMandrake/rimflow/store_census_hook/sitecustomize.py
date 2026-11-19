"""The run-time hook of store_write_census.py (item RIMMANDRAKE_NARROW_CUTOVER_WRITER_CHECK_EIGHT_OF_THIRTEEN_READ).

Loaded by every Python process a census test starts, because the census puts this folder first on PYTHONPATH; inert
unless RM_STORE_CENSUS_DIR is set. It records two things under that folder:
  - every open-for-writing of an old mod store (stage.json, journal.md, version/stage_record.json) and every rename onto
    one, with the src/RimMandrake modules on the stack, innermost first: appended at the moment it happens, so a process
    that dies afterwards still leaves it;
  - which code objects of src/RimMandrake files started (sys.monitoring PY_START, each disabled after its first start),
    written at exit: a process that dies without exiting leaves none, which reads as "never ran", never as "ran clean".
Then it hands over to the next sitecustomize on sys.path, if any.
"""
import atexit
import json
import os
import sys

_OUT = os.environ.get("RM_STORE_CENSUS_DIR")
_MARK = "src/RimMandrake/"
_WFLAGS = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC


def _key(fn):
    fn = str(fn).replace("\\", "/")
    i = fn.rfind(_MARK)
    return fn[i:] if i >= 0 else None


def _is_store(p):
    """A store by name; nothing under a .git folder is one (seat_sync parks dirty copies there)."""
    p = os.fsdecode(p).replace("\\", "/")
    if "/.git/" in p or p.startswith(".git/"):
        return False
    b = p.rsplit("/", 1)[-1]
    return b in ("stage.json", "journal.md") or p.endswith("version/stage_record.json")


if _OUT:
    _BUSY = [False]
    _RAN = {}
    _TEST = os.environ.get("RM_STORE_CENSUS_TEST", "")

    def _record(event, path):
        f, chain = sys._getframe(2), []
        while f is not None:
            k = _key(f.f_code.co_filename)
            if k and k not in chain:
                chain.append(k)
            f = f.f_back
        line = json.dumps({"event": event, "path": os.path.abspath(os.fsdecode(path)), "chain": chain, "test": _TEST})
        _BUSY[0] = True
        try:
            with open(os.path.join(_OUT, "%d.writes.jsonl" % os.getpid()), "a", encoding="utf-8") as w:
                w.write(line + "\n")
        finally:
            _BUSY[0] = False

    def _audit(event, args):
        if _BUSY[0]:
            return
        if event == "open":
            path, mode, flags = (tuple(args) + (None, None, None))[:3]
            if not isinstance(path, (str, bytes, os.PathLike)) or not _is_store(path):
                return
            if isinstance(flags, int):
                w = bool(flags & _WFLAGS)
            else:
                w = isinstance(mode, str) and any(c in mode for c in "wax+")
            if w:
                _record("open", path)
        elif event == "os.rename" and len(args) >= 2 and isinstance(args[1], (str, bytes, os.PathLike)) \
                and _is_store(args[1]):
            _record("rename", args[1])

    sys.addaudithook(_audit)

    _M = sys.monitoring
    _TOOL = next((t for t in (4, 3) if _M.get_tool(t) is None), None)
    if _TOOL is not None:
        _M.use_tool_id(_TOOL, "rm_store_census")

        def _start(code, _off):
            k = _key(code.co_filename)
            if k:
                _RAN.setdefault(k, set()).add(code.co_firstlineno)
            return _M.DISABLE

        _M.register_callback(_TOOL, _M.events.PY_START, _start)
        _M.set_events(_TOOL, _M.events.PY_START)

    def _dump():
        if _TOOL is not None:
            _M.set_events(_TOOL, 0)
        _BUSY[0] = True
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
    _here = os.path.dirname(os.path.abspath(__file__))
    _spec = importlib.machinery.PathFinder.find_spec(
        "sitecustomize", [p for p in sys.path if os.path.abspath(p or ".") != _here])
    if _spec is not None and _spec.loader is not None:
        _spec.loader.exec_module(importlib.util.module_from_spec(_spec))
except Exception:
    pass
