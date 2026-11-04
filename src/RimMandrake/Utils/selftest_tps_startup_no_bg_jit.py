#!/usr/bin/env python3
"""Guard for JAWABENCH_TPSSTARTUP_HARDEN_REMAINING_BG_JIT (offline, no dotnet, no game).

The 2026-10-26 SteveDesktop crash: background code JIT-compiling while the main thread was still
Harmony-patching at bridge-registration crashed mono natively. ff9170433f deferred the Player-prev
archive (guarded by selftest_tps_archive_startup.py); cc8c8991f4 closed the other startup paths.
This test pins their shape in the SOURCE TEXT (comments stripped):

  1. Install opens the writer with deferThread: true and calls W.Go() only in its finally block,
     after every Harmony patch, the session row and the start marker.
  2. Writer.Start starts no thread when deferThread is set; Go runs a synchronous RunOnce pass on
     the calling thread BEFORE StartThreadLocked.
  3. WriteSessionStart only PARKS the manifest (Interlocked into _pendingManifest); the manifest's
     File.WriteAllText lives inside that lambda; no threadpool/Thread/Task there or in Install.
  4. The sampler's only ThreadPool.QueueUserWorkItem is in PumpArchive, after the busy reset and
     the ArchiveIdleSeconds gate, and it runs the manifest taken from _pendingManifest.
  5. OnQuit writes a still-pending manifest inline (quit before startup went idle).
  6. Watchdog.Start runs WarmOnCaller() before creating its thread.

    python3 src/RimMandrake/Utils/selftest_tps_startup_no_bg_jit.py            checks
    python3 src/RimMandrake/Utils/selftest_tps_startup_no_bg_jit.py --mutants  + each mutant must go red

Exit 0 = PASS, 1 = FAIL.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src/RimMandrake/bridgetools/JawaBench.BridgeTools"
FILES = {"sampler": SRC / "JawaBenchTpsSampler.cs",
         "writer": SRC / "JawaBenchTpsWriter.cs",
         "watchdog": SRC / "JawaBenchTpsWatchdog.cs"}

SPAWN = re.compile(r"ThreadPool\.QueueUserWorkItem|new\s+Thread\s*\(|Task\.(Run|Factory)|\.BeginInvoke\s*\(")


def strip_comments(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"//[^\n]*", "", s)


def body(text, signature_regex):
    """Brace-matched body of the first method whose signature matches, or None."""
    m = re.search(signature_regex, text)
    if not m:
        return None
    i = text.find("{", m.end())
    if i < 0:
        return None
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
    return None


def run(src):
    """src: dict name -> comment-stripped text. Returns the list of failures."""
    fails = []

    def check(cond, msg):
        if not cond:
            fails.append(msg)

    s, w, d = src["sampler"], src["writer"], src["watchdog"]

    # 1. Install: deferred writer, Go only in the finally
    inst = body(s, r"internal\s+static\s+void\s+Install\s*\(\s*string")
    check(inst is not None, "1: Install(string) not found in the sampler")
    if inst:
        check(re.search(r"W\.Start\s*\([^;]*deferThread\s*:\s*true", inst) is not None,
              "1: Install must open the writer with W.Start(..., deferThread: true)")
        fin = inst.rfind("finally")
        check(fin >= 0, "1: Install has no finally block")
        if fin >= 0:
            check("W.Go()" in inst[fin:], "1: W.Go() must be called in Install's finally block")
            check("W.Go()" not in inst[:fin], "1: W.Go() called before the finally (writer thread starts mid-patching)")
            for marker in ("h.Patch(", "WriteSessionStart(", "WD.Start("):
                p = inst.find(marker)
                check(p < 0 or p < fin, "1: %s must come before W.Go()" % marker)
        check(SPAWN.search(inst) is None, "3: Install itself must start no thread/threadpool/task work")

    # 2. Writer.Start honours deferThread; Go writes synchronously first
    ws = body(w, r"internal\s+static\s+void\s+Start\s*\(\s*string\s+dir")
    check(ws is not None, "2: Writer.Start(string dir, ...) not found")
    if ws:
        check(re.search(r"if\s*\(\s*!\s*deferThread\s*\)\s*StartThreadLocked\s*\(\s*\)", ws) is not None,
              "2: Writer.Start must start its thread only `if (!deferThread)`")
        check(SPAWN.search(ws) is None, "2: Writer.Start must not spawn a thread directly")
    go = body(w, r"internal\s+static\s+void\s+Go\s*\(\s*\)")
    check(go is not None, "2: Writer.Go() not found")
    if go:
        r1, st = go.find("RunOnce("), go.find("StartThreadLocked(")
        check(r1 >= 0, "2: Go must run a synchronous RunOnce pass on the calling thread")
        check(st >= 0, "2: Go must start the deferred thread (StartThreadLocked)")
        if r1 >= 0 and st >= 0:
            check(r1 < st, "2: Go must write (RunOnce) BEFORE starting the writer thread")
        m = re.search(r"RunOnce\s*\([^;]*,\s*(\w+)\s*\)\s*;", go)
        check(m is not None and m.group(1) == "false", "2: Go's RunOnce must not wait (wait=false)")

    # 3. WriteSessionStart parks the manifest
    wss = body(s, r"private\s+static\s+void\s+WriteSessionStart\s*\(")
    check(wss is not None, "3: WriteSessionStart not found")
    if wss:
        park = wss.find("Interlocked.Exchange(ref _pendingManifest")
        wr = wss.find("File.WriteAllText(")
        check(park >= 0, "3: WriteSessionStart must park the manifest in _pendingManifest")
        check(wr >= 0, "3: manifest File.WriteAllText not found in WriteSessionStart")
        if park >= 0 and wr >= 0:
            check(park < wr, "3: the manifest write must be inside the parked lambda, not run at install")
            check(wss.count("File.WriteAllText(") == 1, "3: only one manifest write, inside the lambda")
        check(SPAWN.search(wss) is None, "3: WriteSessionStart must start no background work")

    # 4. the only threadpool job is the idle pump's
    spawns = [m.start() for m in re.finditer(r"ThreadPool\.QueueUserWorkItem", s)]
    pa = body(s, r"private\s+static\s+void\s+PumpArchive\s*\(")
    check(pa is not None, "4: PumpArchive not found")
    if pa:
        start = s.find(pa)
        outside = [p for p in spawns if not (start <= p < start + len(pa))]
        check(not outside, "4: ThreadPool.QueueUserWorkItem outside PumpArchive (%d site(s))" % len(outside))
        check(len(spawns) >= 1, "4: PumpArchive must queue the manifest on the threadpool once idle")
        q = pa.find("ThreadPool.QueueUserWorkItem")
        gate = pa.find("ArchiveIdleSeconds")
        busy = re.search(r"if\s*\(\s*busy\s*\)\s*\{[^}]*return", pa)
        check(busy is not None, "4: PumpArchive must reset and return on a busy frame")
        check(gate >= 0 and q > gate, "4: the manifest job must be queued only after the ArchiveIdleSeconds gate")
        check(busy is not None and q > busy.start(), "4: the manifest job must come after the busy reset")
        check(re.search(r"Interlocked\.Exchange\s*\(\s*ref\s+_pendingManifest\s*,\s*null\s*\)", pa) is not None,
              "4: PumpArchive must TAKE the parked manifest (Interlocked.Exchange(ref _pendingManifest, null))")
    m = re.search(r"internal\s+const\s+double\s+ArchiveIdleSeconds\s*=\s*([0-9.]+)", s)
    check(m is not None and float(m.group(1)) >= 10, "4: ArchiveIdleSeconds must be >= 10")
    other = [m.group(0) for m in re.finditer(r"new\s+Thread\s*\(|Task\.(Run|Factory)", s)]
    check(not other, "4: the sampler must not start threads/tasks: %r" % other)

    # 5. OnQuit writes a pending manifest
    oq = body(s, r"private\s+static\s+void\s+OnQuit\s*\(")
    check(oq is not None, "5: OnQuit not found")
    if oq:
        check(re.search(r"Interlocked\.Exchange\s*\(\s*ref\s+_pendingManifest\s*,\s*null\s*\)", oq) is not None
              and re.search(r"if\s*\(\s*m\s*!=\s*null\s*\)\s*m\s*\(\s*\)", oq) is not None,
              "5: OnQuit must take and run a still-pending manifest inline")

    # 6. watchdog warms before its thread
    dst = body(d, r"internal\s+static\s+void\s+Start\s*\(\s*string\s+dir")
    check(dst is not None, "6: Watchdog.Start(string dir) not found")
    if dst:
        wo, nt = dst.find("WarmOnCaller()"), dst.find("new Thread(")
        check(wo >= 0 and nt >= 0 and wo < nt, "6: Watchdog.Start must call WarmOnCaller() before creating its thread")
    return fails


# Each mutant: (file, old, new, why). Applied to the comment-stripped text; must make run() fail.
MUTANTS = [
    ("sampler", "deferThread: true", "deferThread: false", "writer thread started mid-patching"),
    ("sampler", "try { W.Go(); } catch { }", "", "W.Go removed"),
    ("sampler", "Interlocked.Exchange(ref _pendingManifest, () =>", "ThreadPool.QueueUserWorkItem(_ =>",
     "manifest back on the threadpool at install"),
    ("sampler", "if (busy) { _idleSince = -1; return; }", "", "pump ignores long events"),
    ("sampler", "internal const double ArchiveIdleSeconds = 10;", "internal const double ArchiveIdleSeconds = 1;",
     "idle gate shortened"),
    ("sampler", "if (m != null) m();", "", "OnQuit drops a pending manifest"),
    ("writer", "if (!deferThread) StartThreadLocked();", "StartThreadLocked();", "Start ignores deferThread"),
    ("writer", "try { RunOnce(new List<string>(), new List<Action>(), false); } catch { }", "",
     "Go starts the thread with no synchronous pass"),
    ("watchdog", "            WarmOnCaller();\n", "", "watchdog not warmed"),
]


def load():
    return {k: strip_comments(p.read_text(encoding="utf-8")) for k, p in FILES.items()}


def main():
    src = load()
    fails = run(src)
    for f in fails:
        print("FAIL", f)
    if "--mutants" in sys.argv[1:]:
        for name, old, new, why in MUTANTS:
            if old not in src[name]:
                fails.append("mutant %r: anchor not found in %s (reworded? update the mutant)" % (why, name))
                print("FAIL", fails[-1])
                continue
            m = dict(src)
            m[name] = src[name].replace(old, new, 1)
            if run(m):
                print("ok   mutant red:", why)
            else:
                fails.append("mutant %r stayed green" % why)
                print("FAIL", fails[-1])
    print("PASS" if not fails else "FAIL (%d)" % len(fails))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
