"""The read record of one door test (door_reads.py; page design/specs/2026-11-26-door-reads/boundary.md).

publish.py puts this folder first on PYTHONPATH and names a record file in RM_DOOR_READS; then every Python process of
the test (children too: they inherit both) appends, once per path, what it reads under RM_DOOR_READS_ROOT:
    R <path>    a file it opened or imported (any mode; a missing file too)
    D <path>    a folder it listed (os.listdir, os.scandir, glob)
    C <json>    a non-Python child aimed at the tree: {"cwd": its folder relative to the tree, or null, "argv": [...]}
                (door_reads.py reads what a git child reads; any other is a read the record cannot see)
    X <why>     a read the hook cannot see: a Python child that drops the hook
Without RM_DOOR_READS this file does nothing. It never raises into the test.
"""
import _thread
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _install():
    out, root = os.environ.get("RM_DOOR_READS"), os.environ.get("RM_DOOR_READS_ROOT")
    if not out or not root:
        return
    root = os.path.realpath(root)
    pre = root.rstrip(os.sep) + os.sep
    try:
        fd = os.open(out, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    except OSError:
        return
    seen = set()
    busy = set()        # the threads inside the hook now: a read the hook itself makes is not recorded, and a read in
    #                     another thread at the same moment is (one flag for the process lost 361 of 400 reads in
    #                     8 threads, 2026-11-26)

    def put(kind, text):
        key = (kind, text)
        if key in seen:
            return
        seen.add(key)
        try:
            os.write(fd, ("%s %s\n" % (kind, text.replace("\n", " "))).encode("utf-8", "replace"))
        except OSError:
            pass

    memo = {}
    UNRESOLVED = "\0unresolved"     # never a real relative path; inside() said "could not look"

    def inside(p):
        """-> p relative to the tree, "." for the tree, or None outside it. Cached per (cwd, p): the hook runs on every
        open, and realpath costs several system calls."""
        try:
            p = os.fsdecode(p) if isinstance(p, (bytes, os.PathLike)) else p
            if not isinstance(p, str):
                return None
            k = p if p.startswith("/") else (os.getcwd(), p)
            if k in memo:
                return memo[k]
            a = os.path.realpath(p if os.path.isabs(p) else os.path.join(os.getcwd(), p))
        except (OSError, ValueError, TypeError) as e:       # could not look: the record says so, never "outside"
            put("X", "a path it could not resolve (%s: %r)" % (type(e).__name__, p))
            return UNRESOLVED
        r = "." if a == root else (a[len(pre):] if a.startswith(pre) else None)
        if len(memo) < 100000:
            memo[k] = r
        return r

    def is_py(exe):
        b = os.path.basename(os.fsdecode(exe)) if isinstance(exe, (str, bytes, os.PathLike)) else ""
        return b.startswith("python") or os.path.realpath(os.fsdecode(exe)) == os.path.realpath(sys.executable)

    def child(exe, argv, cwd, env):
        argv = [os.fsdecode(a) if isinstance(a, (bytes, os.PathLike)) else str(a) for a in (argv or [])]
        exe = exe if exe is not None else (argv[0] if argv else "")
        if is_py(exe):
            e = env if env is not None else os.environ
            try:
                hooked = e.get("RM_DOOR_READS") == out and HERE in (e.get("PYTHONPATH") or "").split(os.pathsep)
            except AttributeError:
                hooked = False
            if not hooked:
                put("X", "a Python child without the hook: %s" % " ".join(argv)[:200])   # cut-ok: names the child, decides nothing
            elif any(a in ("-I", "-E", "-S") or (a.startswith("-") and not a.startswith("--") and set(a[1:]) & set("IES")
                                                and len(a) <= 4) for a in argv[1:3]):
                put("X", "a Python child that skips the hook: %s" % " ".join(argv)[:200])   # cut-ok: names the child, decides nothing
            return
        aim = os.fsdecode(cwd) if cwd is not None else os.getcwd()
        if os.path.basename(argv[0] if argv else "") == "git":     # git -C moves it: the folder it reads is the last -C
            for i, a in enumerate(argv[1:-1], 1):
                if a == "-C":
                    aim = os.path.join(aim, argv[i + 1])
        if inside(aim) is not None or any(inside(a) is not None for a in argv[1:] if os.path.isabs(a)):
            put("C", json.dumps({"cwd": inside(aim), "argv": [exe if not argv else argv[0]] + argv[1:]}))

    WATCH = frozenset(("open", "os.listdir", "os.scandir", "glob.glob", "subprocess.Popen", "os.posix_spawn",
                       "os.exec", "os.spawn", "os.system"))

    def hook(event, args):
        if event not in WATCH:
            return
        me = _thread.get_ident()
        if me in busy:
            return
        busy.add(me)
        try:
            if event == "open":
                r = inside(args[0])
                if r is not None and r != UNRESOLVED:
                    put("R", r)
            elif event in ("os.listdir", "os.scandir"):
                # the import system lists each sys.path folder to cache its names: not a read of the folder by the
                # test (a new module there matters only to an import that missed; the page names that gap)
                f = sys._getframe(1)
                if f.f_code.co_name == "_fill_cache":
                    return
                r = inside(args[0] if args and args[0] is not None else ".")
                if r is not None and r != UNRESOLVED:
                    put("D", r)
            elif event == "glob.glob":
                r = inside(os.path.dirname(args[0]) or ".") if args and isinstance(args[0], str) else None
                if r is not None and r != UNRESOLVED:
                    put("D", r)
            elif event == "subprocess.Popen":
                exe, argv, cwd, env = args
                child(exe, argv if not isinstance(argv, (str, bytes)) else [argv], cwd, env)
            elif event == "os.posix_spawn":
                path, argv, env = args
                child(path, argv, None, env)
            elif event == "os.exec":
                child(args[0], args[1], None, args[2] if len(args) > 2 else None)
            elif event == "os.spawn":
                child(args[1], args[2], None, args[3] if len(args) > 3 else None)
            elif event == "os.system":
                put("X", "os.system: %s" % str(args[0])[:200])   # cut-ok: names the command, decides nothing
        except Exception:  # noqa: BLE001  the hook never breaks the test it watches
            pass
        finally:
            busy.discard(me)

    sys.addaudithook(hook)


def _chain():
    """Run the sitecustomize this one shadows (Ubuntu's installs apport's hook), so a test sees its usual start."""
    for d in sys.path:
        p = os.path.join(d, "sitecustomize.py")
        if d and os.path.realpath(d) != os.path.realpath(HERE) and os.path.isfile(p):
            try:
                with open(p, encoding="utf-8") as f:
                    exec(compile(f.read(), p, "exec"), {"__name__": "sitecustomize", "__file__": p})
            except Exception:  # noqa: BLE001  as Python itself: a broken sitecustomize never stops the start
                pass
            return


_install()
_chain()
