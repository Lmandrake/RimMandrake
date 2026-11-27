"""sitecustomize.py: records what one Python process of an outcome check reads (check_once.py; page
design/specs/2026-11-27-check-once/boundary.md). It is on PYTHONPATH only for a check that check_once.py runs, and acts
only when RM_CHECK_READS names a folder. It never changes what the check does: each hook only notes, and a fault in a
hook is a note ("why"), never an exception in the check.

Per process it writes <RM_CHECK_READS>/<pid>.start at once, and <pid>.json at exit: every path the process opened,
listed or stat'ed (with its stat as first seen; an open that only writes is not a read), the python children it started, and each reason that its reads cannot
be named (a program that is not python, a socket, a folder by descriptor, /proc). A process that ends without its
.json (os._exit, a signal) leaves only the .start, and check_once.py then names nothing for the whole check.
"""
import os
import sys


def _install():
    out = os.environ.get("RM_CHECK_READS")
    if not out:
        return
    import atexit
    import json
    import re
    here = os.path.dirname(os.path.abspath(__file__))
    tmp = os.environ.get("TMPDIR") or ""
    pid = os.getpid()
    ppid = os.getppid()
    reads, why, state = {}, [], {"kids": 0}
    stat0, lstat0, access0 = os.stat, os.lstat, os.access
    pyname = re.compile(r"^python(\d+(\.\d+)*)?$")
    quiet = ("/dev/null", "/dev/urandom", "/dev/random", "/dev/tty", "/dev/stdin", "/dev/stdout", "/dev/stderr")

    import hashlib
    import stat as statmod
    listdir0 = os.listdir

    def sig(p):     # the same as check_once.sig
        try:
            s = stat0(p)
            if statmod.S_ISDIR(s.st_mode):
                names = "\0".join(sorted(listdir0(p)))
                return ["dir", hashlib.sha1(names.encode("utf-8", "surrogateescape")).hexdigest()]
            return [s.st_mtime_ns, s.st_size, s.st_ino, s.st_mode]
        except FileNotFoundError:
            return ["missing"]
        except NotADirectoryError:
            return ["missing"]
        except OSError as e:
            return ["error", e.errno]

    def note(p, dir_fd=None):
        if isinstance(p, int):
            return
        if dir_fd is not None:
            why.append("a path read relative to a folder descriptor")
            return
        try:
            p = os.fsdecode(p)
        except Exception:  # noqa: BLE001 - a path that is not a path is never a silent miss
            why.append("a path of type %s" % type(p).__name__)
            return
        if not os.path.isabs(p):
            p = os.path.join(os.getcwd(), p)
        p = os.path.normpath(p)
        if p in reads or p.startswith(out) or (tmp and p.startswith(tmp)):
            return
        if p in quiet:
            return
        if p.startswith(("/proc/", "/sys/", "/dev/")) or p in ("/proc", "/sys", "/dev"):
            why.append("reads %s" % p)
            return
        reads[p] = ["pending"]      # first: sig lists a folder, and that listing comes back here
        reads[p] = sig(p)

    def wrap(fn):
        def inner(path, *a, **k):
            try:
                note(path, k.get("dir_fd"))
            except Exception as e:  # noqa: BLE001
                why.append("hook fault %s" % type(e).__name__)
            return fn(path, *a, **k)
        inner.__name__ = fn.__name__
        inner.__doc__ = fn.__doc__
        return inner

    os.stat, os.lstat, os.access = wrap(stat0), wrap(lstat0), wrap(access0)

    def hook(ev, args):
        try:
            if ev == "open":
                mode, flags = (list(args) + [None, None])[1:3]
                if isinstance(mode, str):
                    write_only = "r" not in mode and "+" not in mode and "x" not in mode
                else:
                    write_only = (isinstance(flags, int) and (flags & os.O_ACCMODE) == os.O_WRONLY
                                  and not flags & os.O_EXCL)
                if not write_only:      # a write that reads nothing (w, a): what it wrote is read by a later open
                    note(args[0])
            elif ev in ("os.listdir", "os.scandir"):
                p = args[0]
                if isinstance(p, int):
                    why.append("lists a folder by descriptor")
                else:
                    note("." if p is None else p)
            elif ev == "subprocess.Popen":
                exe, argv, _cwd, env = args
                first = exe if exe else (argv[0] if isinstance(argv, (list, tuple)) and argv else argv)
                name = os.path.basename(os.fsdecode(first or ""))
                if not pyname.match(name):
                    why.append("runs %s" % name)
                elif env is not None and (env.get("RM_CHECK_READS") != out
                                          or here not in str(env.get("PYTHONPATH") or "").split(os.pathsep)):
                    why.append("runs python with an environment that does not record")
                else:
                    state["kids"] += 1
            elif ev in ("os.system", "os.exec", "os.posix_spawn", "os.spawn"):
                first = args[0]
                name = os.path.basename(os.fsdecode(first if isinstance(first, (str, bytes)) else ""))
                if ev == "os.system" or not pyname.match(name):
                    why.append("%s %s" % (ev, name))
            elif ev == "ctypes.dlopen":     # a library by path is a read; a bare name is a system library
                if isinstance(args[0], (str, bytes)) and "/" in os.fsdecode(args[0]):
                    note(args[0])
            elif ev.startswith(("socket.", "sqlite3.connect", "urllib.", "http.", "ftplib.", "smtplib.",
                                "winreg.", "mmap.")):
                if ev not in ("socket.gethostname",):
                    why.append(ev)
        except Exception as e:  # noqa: BLE001 - a hook never raises into the check
            why.append("hook fault %s" % type(e).__name__)

    def done():
        rec = {"pid": pid, "ppid": ppid, "clause": os.environ.get("RM_CHECK_CLAUSE"), "argv": sys.argv[:8],
               "kids": state["kids"], "why": why[:20], "reads": reads}
        try:
            p = os.path.join(out, "%d.json" % pid)
            with open(p + ".tmp", "w", encoding="utf-8") as f:
                json.dump(rec, f)
            os.replace(p + ".tmp", p)
        except Exception:  # noqa: BLE001 - no record: check_once names nothing for this check
            pass

    try:
        with open(os.path.join(out, "%d.start" % pid), "w", encoding="utf-8") as f:
            f.write("%d %d\n" % (pid, ppid))
    except OSError:
        return
    sys.addaudithook(hook)
    atexit.register(done)


def _chain():
    """Load the sitecustomize that this file shadows, if one exists further along sys.path."""
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path[:] = [p for p in sys.path if os.path.abspath(p or ".") != here]
    import importlib.util
    try:
        spec = importlib.util.find_spec("sitecustomize")
    except (ImportError, ValueError):
        spec = None
    if spec and spec.origin and os.path.dirname(os.path.abspath(spec.origin)) != here:
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception:  # noqa: BLE001 - the shadowed file's own fault, as python would have shown it
            import traceback
            traceback.print_exc()


try:
    _install()
finally:
    _chain()
