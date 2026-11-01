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
  env       environment names read through os.environ, or through a copy of it. Handing a copy to a child is not a
            read (the child's own are); anything else that walks a copy reads every name in it
  imports   every module name an import statement tried, found or not: a new file with one of these names changes
            what that import finds, a new file with any other name does not
  import_dirs  directories only the import system listed (`listed` keeps every listing anybody else asked for)
  clock_by  which python file called time.time and friends (diagnosis only: rm_preload.c is what detects a clock read)

It must never change what a test does: every hook swallows its own errors, and nothing here raises.
At exit it writes <dir>/<pid>.json; <pid>.start is written first so a process that died without
writing its trace is detectable (the runner then records nothing).
"""
import os
import sys

_DIR = os.environ.get("RM_SELFTEST_TRACE")

if _DIR:
    import _thread
    import atexit
    import json
    import time as _time

    _read, _wrote, _listed, _probed, _children, _taint = set(), set(), set(), set(), [], set()
    _mtimes = {}
    _spawns = [0, 0]   # os.posix_spawn events, subprocess.Popen events
    _real_stat, _real_lstat = os.stat, os.lstat
    _env, _imports, _import_dirs, _clock_by = set(), set(), set(), set()
    _IMPORT_FRAME = "<frozen importlib._bootstrap_external>"
    _CLOCK_ARM = "/rm-selftest/clock-armed"    # rm_preload.c: from here on a wall-clock read is the test's, not startup's
    _CLOCK_MUTE = "/rm-selftest/clock-muted"   # ...except this thread's next read
    _CLOCK_STAMPS = ("/logging/__init__.py",)

    class _Local(_thread._local):
        busy = False        # per thread: one shared flag dropped every event a second thread raised meanwhile
        quiet = False

    _me = _Local()

    def _abs(p):
        if isinstance(p, int):
            return None
        try:
            p = os.fsdecode(os.fspath(p))
        except TypeError:
            return None
        return os.path.normpath(os.path.join(os.getcwd(), p)) if not os.path.isabs(p) else os.path.normpath(p)

    _WANTED = frozenset(("open", "os.listdir", "os.scandir", "import", "sqlite3.connect", "ctypes.dlopen",
                         "subprocess.Popen", "os.posix_spawn", "os.system", "os.fork", "os.forkpty", "os.exec", "os.spawn",
                         "socket.connect", "socket.getaddrinfo", "socket.sendto", "socket.bind",
                         "socket.gethostbyname"))

    def _note_read(p):
        _read.add(p)
        if p not in _mtimes:
            try:
                _mtimes[p] = _real_stat(p).st_mtime_ns
            except OSError:
                _mtimes[p] = None

    def _hook(event, args):
        if event not in _WANTED or _me.busy:      # first: audit events fire on every compile and attribute write
            return
        _me.busy = True
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
                    f = sys._getframe(1)
                    (_import_dirs if f.f_code.co_filename == _IMPORT_FRAME else _listed).add(p)
            elif event == "import":
                _imports.add(str(args[0]))
            elif event == "sqlite3.connect":
                p = _abs(args[0]) if args[0] != ":memory:" else None
                if p is not None:
                    _wrote.add(p)
                    _note_read(p)
            elif event == "ctypes.dlopen":
                _taint.add("ctypes.dlopen")
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
            _me.busy = False

    def _wrap(real):
        def stat(path, *a, **k):
            if not _me.busy:
                p = _abs(path)
                if p is not None:
                    _probed.add(p)
            return real(path, *a, **k)
        stat.__wrapped__ = real
        return stat

    def _hook_env():
        cls = type(os.environ)
        get, copy = cls.__getitem__, cls.copy

        def __getitem__(self, key):
            if (self is os.environ or self is os.environb) and not _me.quiet:
                _env.add(key if isinstance(key, str) else os.fsdecode(key))
            return get(self, key)

        def _name(key):
            if not _me.busy:
                _env.add(key if isinstance(key, str) else os.fsdecode(key))

        def _walked(d):
            if not _me.busy and not sys._getframe(2).f_code.co_filename.endswith("/subprocess.py"):
                _env.update(k if isinstance(k, str) else os.fsdecode(k) for k in dict.keys(d))

        class _Copy(dict):
            """os.environ.copy(): a dict like any other, except that what is asked of it is a read of the environment."""

            def __getitem__(self, key):
                _name(key)
                return dict.__getitem__(self, key)

            def get(self, key, default=None):
                _name(key)
                return dict.get(self, key, default)

            def __contains__(self, key):
                _name(key)
                return dict.__contains__(self, key)

            def pop(self, key, *default):
                _name(key)
                return dict.pop(self, key, *default)

            def setdefault(self, key, default=None):
                _name(key)
                return dict.setdefault(self, key, default)

            def __iter__(self):
                _walked(self)
                return dict.__iter__(self)

            def keys(self):
                _walked(self)
                return dict.keys(self)

            def values(self):
                _walked(self)
                return dict.values(self)

            def items(self):
                _walked(self)
                return dict.items(self)

            def copy(self):
                return _Copy(dict.items(self))

        def copy_quiet(self):
            _me.quiet = True
            try:
                return _Copy(copy(self))
            finally:
                _me.quiet = False

        cls.__getitem__, cls.copy = __getitem__, copy_quiet

    def _hook_finder():
        """find_spec answers without an "import" event, and a new file with that name changes the answer."""
        import _frozen_importlib_external as ext
        real = ext.FileFinder.find_spec

        def find_spec(self, fullname, target=None):
            _imports.add(fullname)
            return real(self, fullname, target)
        ext.FileFinder.find_spec = find_spec

    def _hook_fork():
        """A forked child is a process of its own: it owes a trace, or analyse refuses. os._exit runs no atexit."""
        def in_child():
            try:
                with open(os.path.join(_DIR, "%d.start" % os.getpid()), "w") as f:
                    f.write(" ".join(sys.argv))
            except OSError:
                pass

        real = os._exit

        def _exit(status):
            _dump()
            real(status)
        os.register_at_fork(after_in_child=in_child)
        os._exit = _exit

    def _hook_clock():
        def wrap(name):
            real = getattr(_time, name)

            def clock(*a, **k):
                if len(a) <= (1 if name == "strftime" else 0):      # localtime(t), strftime(f, t) read no clock
                    try:
                        by = sys._getframe(1).f_code.co_filename
                    except Exception:  # noqa: BLE001
                        by = "?"
                    if by.endswith(_CLOCK_STAMPS):      # a stamp for a log line: never a branch, and in half the suite
                        try:                            # (`import logging` itself reads it)
                            _real_stat(_CLOCK_MUTE)
                        except OSError:
                            pass
                        try:
                            return real(*a, **k)
                        finally:
                            try:
                                _real_stat(_CLOCK_ARM)
                            except OSError:
                                pass
                    _clock_by.add("%s:%s" % (by, name))
                return real(*a, **k)
            clock.__wrapped__ = real
            setattr(_time, name, clock)
        for name in ("time", "time_ns", "localtime", "gmtime", "ctime", "asctime", "strftime"):
            wrap(name)

    def _dump():
        try:
            if _spawns[0] > _spawns[1]:
                _taint.add("os.posix_spawn outside subprocess.Popen")
            mods = sorted({os.path.normpath(m.__file__) for m in list(sys.modules.values())
                           if getattr(m, "__file__", None)})
            out = {"pid": os.getpid(), "argv": sys.argv, "read": sorted(_read), "wrote": sorted(_wrote),
                   "listed": sorted(_listed), "probed": sorted(_probed - _read - _listed), "children": _children,
                   "taint": sorted(_taint), "modules": mods, "mtimes": _mtimes, "executable": sys.executable,
                   "version": sys.version, "env": sorted(_env), "imports": sorted(_imports),
                   "import_dirs": sorted(_import_dirs), "clock_by": sorted(_clock_by)}
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
        _hook_env()
        _hook_finder()
        _hook_fork()
        _hook_clock()
        sys.addaudithook(_hook)
        try:
            _real_stat(_CLOCK_ARM)
        except OSError:
            pass
        atexit.register(_dump)
    except Exception:  # noqa: BLE001
        pass
