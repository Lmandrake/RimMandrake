"""Where a supervisor tick spends its wall clock: every child process it waits on, tallied by command.

RELENTLESS_TICK_MEASURE_OUTLASTS_ITS_NAP: a tick ran 5-10 minutes and its journal row named only its phases, so nobody
could say which command ate them. A ps sample of one live tick (2026-11-06) found clone creation, the live round, a
compose deploy and publishing, all run inline. This tally makes every tick's journal row carry that answer itself.

A child is counted from Popen() to the wait() that reaps it (subprocess.run and check_output end in one), so time spent
waiting on it is what is measured; a detached worker nobody waits on is never counted. Children run in parallel threads
add up, so the total may exceed the tick's wall time.
"""
import os
import subprocess
import sys
import threading
import time

TOP = 8
_BASE = (subprocess.Popen.__init__, subprocess.Popen.wait)     # a patch an exception leaked is replaced, never stacked


def label(argv):
    """A short, stable name for a command: `git fetch`, `scratch_clone.py clone`, `powershell.exe`."""
    if isinstance(argv, (str, bytes)):
        argv = str(argv).split()
    argv = [str(a) for a in (argv or [])]
    if not argv:
        return "?"
    head = os.path.basename(argv[0])
    rest = argv[1:]
    if head.startswith("python") and rest:
        while rest and rest[0].startswith("-") and rest[0] not in ("-m",):
            rest = rest[1:]
        if rest[:1] == ["-m"] and len(rest) > 1:
            return "%s %s" % (rest[1], _word(rest[2:]))
        if rest:
            return ("%s %s" % (os.path.basename(rest[0]), _word(rest[1:]))).strip()
    if head == "git":
        while rest and (rest[0].startswith("-") or rest[0] in ("-C", "--git-dir")):
            rest = rest[2:] if rest[0] in ("-C", "--git-dir", "-c") else rest[1:]
        return ("git " + _word(rest)).strip()
    return head


def _word(rest):
    for a in rest:
        if not a.startswith("-"):
            return a if len(a) <= 24 and "/" not in a else ""
        return ""
    return ""


class Tally:
    """Install with `with Tally() as t:`; read `t.top()` and `t.total()` after (or during) the tick."""

    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.rows = {}
        self.lock = threading.Lock()

    def add(self, name, s):
        with self.lock:
            n, tot = self.rows.get(name, (0, 0.0))
            self.rows[name] = (n + 1, tot + s)

    def total(self):
        return round(sum(t for _, t in self.rows.values()), 1)

    def top(self, k=TOP):
        rows = sorted(self.rows.items(), key=lambda x: -x[1][1])[:k]
        return [{"cmd": name, "n": n, "s": round(t, 1)} for name, (n, t) in rows]

    def __enter__(self):
        P = subprocess.Popen
        init, wait, me = _BASE[0], _BASE[1], self

        def __init__(pop, args, *a, **kw):
            pop._tickprof = (me.clock(), label(args))
            return init(pop, args, *a, **kw)

        def _wait(pop, *a, **kw):
            rc = wait(pop, *a, **kw)
            tp = getattr(pop, "_tickprof", None)
            if tp is not None and pop.returncode is not None:
                pop._tickprof = None
                me.add(tp[1], max(me.clock() - tp[0], 0.0))
            return rc

        P.__init__, P.wait = __init__, _wait
        return self

    def __exit__(self, *exc):
        subprocess.Popen.__init__, subprocess.Popen.wait = _BASE
        return False


class Sampler:
    """Where the tick's own Python spends its wall clock: a thread looks at the ticking thread's stack every `every` s.

    The child-process tally saw 101 of a 288 s tick (2026-11-06 08:04Z); the rest is in-process and only a stack can
    name it (py-spy cannot attach: ptrace is closed to the unit's user). Two tallies, in seconds:
      `calls`: the frame just below `root` (the tick function): which call of the tick costs what;
      `leaves`: the innermost frame in a rimflow/Utils file (and its caller), with `[child]` appended while it waits on a process.
    """

    def __init__(self, root="_tick", every=0.25, clock=time.monotonic):
        self.root, self.every, self.clock = root, every, clock
        self.calls, self.leaves = {}, {}
        self.n = 0
        self._stop = threading.Event()
        self._ident = None
        self._t = None

    def _sample(self):
        f = sys._current_frames().get(self._ident)
        if f is None:
            return
        stack = []
        while f is not None:
            stack.append(f)
            f = f.f_back
        stack.reverse()                 # outermost first
        names = [fr.f_code.co_name for fr in stack]
        if self.root not in names:
            return
        i = names.index(self.root)
        mine = [fr for fr in stack[i:] if _ours(fr.f_code.co_filename)]
        call = _where(stack[i + 1]) if i + 1 < len(stack) else _where(stack[i])
        leaf = " < ".join(_where(fr) for fr in reversed(mine[-2:])) if mine else call     # with its caller
        if any(os.path.basename(fr.f_code.co_filename) == "subprocess.py" for fr in stack[i:]):
            leaf += " [child]"
        self.n += 1
        self.calls[call] = self.calls.get(call, 0) + 1
        self.leaves[leaf] = self.leaves.get(leaf, 0) + 1

    def _run(self):
        while not self._stop.wait(self.every):
            try:
                self._sample()
            except Exception:  # noqa: BLE001  a profiler never costs the tick
                pass

    def top(self, which, k=TOP):
        rows = sorted(getattr(self, which).items(), key=lambda x: -x[1])[:k]
        return [{"at": a, "s": round(c * self.every, 1)} for a, c in rows]

    def __enter__(self):
        self._ident = threading.get_ident()
        self._t = threading.Thread(target=self._run, name="tickprof-sampler", daemon=True)
        self._t.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        if self._t is not None:
            self._t.join(timeout=2)
        return False


def _ours(path):
    return "/rimflow/" in path or "/Utils/" in path


def _where(fr):
    return "%s:%s" % (os.path.basename(fr.f_code.co_filename).replace(".py", ""), fr.f_code.co_name)
