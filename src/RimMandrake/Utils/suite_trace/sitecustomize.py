"""Input tracer for run_selftests.py's skip-when-unchanged evidence records (suite_evidence.py).

Active ONLY when RM_SELFTEST_TRACE names a directory; the runner puts this folder first on PYTHONPATH for an
eligible test, so the test and every python process it spawns load it. It records, per process, what the test
actually touched — never a guess:

  read      files opened for reading (builtins.open, io.open_code for imports, os.open)
  wrote     files opened for writing (an input the test wrote itself is an output, not an input)
  listed    directories listed (os.listdir / os.scandir — glob, os.walk and shutil all go through these)
  probed    paths whose EXISTENCE was asked (os.stat / os.lstat) — a texpath check reads no file at all
  children  every subprocess (executable, argv, cwd, whether a python child kept the tracer)
  taint     anything that makes the closure unknowable: os.system, fork, exec, spawn, a socket

It must never change what a test does: every hook swallows its own errors, and nothing here raises.
At exit it writes <dir>/<pid>.json; <pid>.start is written first so a process that died without
writing its trace is detectable (the runner then records nothing).
"""
import os
import sys

_DIR = os.environ.get("RM_SELFTEST_TRACE")

if _DIR:
    import atexit
    import json

    _read, _wrote, _listed, _probed, _children, _taint = set(), set(), set(), set(), [], set()
    _mtimes = {}
    _spawns = [0, 0]   # os.posix_spawn events, subprocess.Popen events
    _real_stat, _real_lstat = os.stat, os.lstat
    _busy = [False]

    def _abs(p):
        if isinstance(p, int):
            return None
        try:
            p = os.fsdecode(os.fspath(p))
        except TypeError:
            return None
        return os.path.normpath(os.path.join(os.getcwd(), p)) if not os.path.isabs(p) else os.path.normpath(p)

    def _note_read(p):
        _read.add(p)
        if p not in _mtimes:
            try:
                _mtimes[p] = _real_stat(p).st_mtime_ns
            except OSError:
                _mtimes[p] = None

    def _hook(event, args):
        if _busy[0]:
            return
        _busy[0] = True
        try:
            if event == "open":
                p = _abs(args[0])
                if p is None:
                    return
                mode, flags = args[1], args[2] if len(args) > 2 else 0
                if isinstance(mode, str):
                    writes = any(c in mode for c in "wax+")
                    reads = "r" in mode or "+" in mode
                else:
                    acc = (flags or 0) & os.O_ACCMODE
                    writes = acc in (os.O_WRONLY, os.O_RDWR) or bool((flags or 0) & os.O_CREAT)
                    reads = acc in (os.O_RDONLY, os.O_RDWR)
                if writes:
                    _wrote.add(p)
                if reads:
                    _note_read(p)
            elif event in ("os.listdir", "os.scandir"):
                p = _abs(args[0] if args and args[0] is not None else ".")
                if p is not None:
                    _listed.add(p)
            elif event == "subprocess.Popen":
                exe, argv, cwd, env = args
                argv = [os.fsdecode(a) if isinstance(a, (bytes, str, os.PathLike)) else str(a)
                        for a in (argv if isinstance(argv, (list, tuple)) else [argv])]
                e = env if env is not None else os.environ
                traced = (e.get("RM_SELFTEST_TRACE") == _DIR and
                          os.path.dirname(os.path.abspath(__file__)) in (e.get("PYTHONPATH") or "").split(os.pathsep))
                _spawns[1] += 1
                _children.append({"exe": os.fsdecode(exe) if exe else (argv[0] if argv else ""), "argv": argv,
                                  "cwd": _abs(cwd) if cwd else os.getcwd(), "traced": traced})
            elif event == "os.posix_spawn":
                _spawns[0] += 1   # subprocess.Popen may spawn this way; only a spawn WITHOUT a Popen is opaque
            elif event in ("os.system", "os.fork", "os.forkpty", "os.exec", "os.spawn"):
                _taint.add(event)
            elif event.startswith("socket.") and event in ("socket.connect", "socket.getaddrinfo", "socket.sendto",
                                                          "socket.bind", "socket.gethostbyname"):
                _taint.add("network (%s)" % event)
        except Exception:  # noqa: BLE001 — a tracer bug must never change the test
            _taint.add("tracer error in %s" % event)
        finally:
            _busy[0] = False

    def _wrap(real):
        def stat(path, *a, **k):
            if not _busy[0]:
                p = _abs(path)
                if p is not None:
                    _probed.add(p)
            return real(path, *a, **k)
        stat.__wrapped__ = real
        return stat

    def _dump():
        try:
            if _spawns[0] > _spawns[1]:
                _taint.add("os.posix_spawn outside subprocess.Popen")
            mods = sorted({os.path.normpath(m.__file__) for m in list(sys.modules.values())
                           if getattr(m, "__file__", None)})
            out = {"pid": os.getpid(), "argv": sys.argv, "read": sorted(_read), "wrote": sorted(_wrote),
                   "listed": sorted(_listed), "probed": sorted(_probed - _read - _listed), "children": _children,
                   "taint": sorted(_taint), "modules": mods, "mtimes": _mtimes, "executable": sys.executable,
                   "version": sys.version}
            tmp = os.path.join(_DIR, "%d.json.tmp" % os.getpid())
            with open(tmp, "w") as f:
                json.dump(out, f)
            os.replace(tmp, os.path.join(_DIR, "%d.json" % os.getpid()))
        except Exception:  # noqa: BLE001
            pass

    try:
        os.makedirs(_DIR, exist_ok=True)
        with open(os.path.join(_DIR, "%d.start" % os.getpid()), "w") as _f:
            _f.write(" ".join(sys.argv))
        os.stat, os.lstat = _wrap(_real_stat), _wrap(_real_lstat)
        sys.addaudithook(_hook)
        atexit.register(_dump)
    except Exception:  # noqa: BLE001
        pass
