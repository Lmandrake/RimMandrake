#!/usr/bin/env python3
"""Guard for JAWABENCH_TPS_ARCHIVE_DIAGNOSE_STARTUP_CRASH (offline, no dotnet, no game).

SteveDesktop 2026-10-26: a threadpool ArchiveLogNow -> SHA256Managed.HashFinal, queued at
bridge-registration while the main thread was still Harmony-patching, crashed mono natively in a
JIT trampoline (no managed catch can stop it). The fix (ff9170433f) must keep this shape:

  1. ArchivePrevLog JIT-warms SHA-256 on the installing thread (W.WarmHash) BEFORE parking the work,
     and only parks it (Interlocked into _pendingArchive): it never calls W.ArchiveLog/ArchiveLogNow
     or the threadpool directly.
  2. W.ArchiveLog runs on a dedicated Thread, never ThreadPool.QueueUserWorkItem.
  3. WarmHash exercises TransformBlock, TransformFinalBlock and .Hash.
  4. PumpArchive resets on a busy (long-event) frame and fires only after ArchiveIdleSeconds (>= 10)
     of continuous idle frames; the pump is called from the per-frame finalizer.
  5. A Python port of PumpArchive, swept over busy/idle frame sequences, never fires the archive
     during or within 10 s after a long event.

Exit 0 = PASS, 1 = FAIL.
"""
import itertools
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src/RimMandrake/bridgetools/JawaBench.BridgeTools"
SAMPLER = SRC / "JawaBenchTpsSampler.cs"
WRITER = SRC / "JawaBenchTpsWriter.cs"

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def body(text, signature_regex):
    """Return the brace-matched body of the first method whose signature matches."""
    m = re.search(signature_regex, text)
    if not m:
        return None
    i = text.index("{", m.end())
    depth = 0
    for j in range(i, len(text)):
        c = text[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
    return None


def strip_comments(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"//[^\n]*", "", s)


def main():
    for p in (SAMPLER, WRITER):
        if not p.is_file():
            print("FAIL: missing %s" % p)
            return 1
    st = strip_comments(SAMPLER.read_text(encoding="utf-8"))
    wt = strip_comments(WRITER.read_text(encoding="utf-8"))

    # 1. ArchivePrevLog: warm, then park; never start the archive itself
    apl = body(st, r"void\s+ArchivePrevLog\s*\(\s*\)")
    check(apl is not None, "ArchivePrevLog() not found in %s" % SAMPLER.name)
    if apl:
        w = apl.find("W.WarmHash()")
        park = re.search(r"Interlocked\.Exchange\s*\(\s*ref\s+_pendingArchive\s*,", apl)
        check(w >= 0, "ArchivePrevLog must call W.WarmHash() on the installing thread")
        check(park is not None, "ArchivePrevLog must park the archive in _pendingArchive")
        if w >= 0 and park:
            check(w < park.start(), "W.WarmHash() must run BEFORE the archive is parked")
        check("QueueUserWorkItem" not in apl, "ArchivePrevLog must not queue threadpool work")
        # ArchiveLog may appear only inside the parked lambda
        outside = apl[:park.start()] + apl[park.end():] if park else apl
        outside = re.sub(r"\(\s*\)\s*=>\s*W\.ArchiveLog\s*\([^;]*\)", "", outside)
        check(not re.search(r"\bW\.ArchiveLog(Now)?\s*\(", outside),
              "ArchivePrevLog must not call W.ArchiveLog/ArchiveLogNow directly (only inside the parked lambda)")

    # 2. ArchiveLog on a dedicated Thread
    al = body(wt, r"static\s+void\s+ArchiveLog\s*\(")
    check(al is not None, "W.ArchiveLog not found in %s" % WRITER.name)
    if al:
        check("new Thread(" in al, "W.ArchiveLog must start a dedicated Thread")
        check("QueueUserWorkItem" not in al and "Task.Run" not in al,
              "W.ArchiveLog must not use the threadpool")

    # 3. WarmHash exercises the hash path
    wh = body(wt, r"static\s+void\s+WarmHash\s*\(\s*\)")
    check(wh is not None, "W.WarmHash not found")
    if wh:
        for call in ("TransformBlock(", "TransformFinalBlock(", ".Hash"):
            check(call in wh, "WarmHash must exercise %s" % call)

    # 4. PumpArchive gating and wiring
    m = re.search(r"ArchiveIdleSeconds\s*=\s*([0-9.]+)", st)
    idle = float(m.group(1)) if m else -1
    check(idle >= 10, "ArchiveIdleSeconds must be >= 10 (found %r)" % idle)
    pa = body(st, r"void\s+PumpArchive\s*\(\s*double\s+now\s*,\s*bool\s+busy\s*\)")
    check(pa is not None, "PumpArchive(double now, bool busy) not found")
    if pa:
        lines = [l.strip() for l in pa.splitlines() if l.strip() not in ("{", "}", "")]
        expect = [
            r"if \(busy\) \{ _idleSince = -1; return; \}",
            r"if \(_idleSince < 0\) \{ _idleSince = now; return; \}",
            r"if \(now - _idleSince < ArchiveIdleSeconds\) return;",
        ]
        for k, rx in enumerate(expect):
            check(k < len(lines) and re.fullmatch(rx, lines[k]),
                  "PumpArchive gate line %d changed (port below no longer matches): %r"
                  % (k + 1, lines[k] if k < len(lines) else None))
        ai = pa.find("_pendingArchive")
        check(ai > pa.find("ArchiveIdleSeconds"), "the archive must be taken only after the idle gate")
    ps = body(st, r"void\s+PumpIdleSafe\s*\(\s*\)")
    check(ps is not None and "LongEventHandler" in ps and "PumpArchive(" in ps,
          "PumpIdleSafe must derive busy from LongEventHandler and call PumpArchive")
    check(len(re.findall(r"\bPumpIdleSafe\s*\(\s*\)\s*;", st)) >= 1,
          "PumpIdleSafe() must be called (per-frame finalizer)")
    # JAWABENCH_TPSARCHIVE_FIX_SKIPPED_AFTER_FAULT: the pump sits at RootFinalizer's TOP level, after its try/catch,
    # so the __exception / RuntimeError / !__state.Valid early returns inside the try cannot skip the archive.
    rf = body(st, r"void\s+RootFinalizer\s*\([^)]*\)")
    check(rf is not None, "RootFinalizer(...) not found")
    if rf:
        top = []   # (depth, offset) of each PumpIdleSafe(); call; depth 1 = the method's own block
        depth = 0
        for j, c in enumerate(rf):
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            elif rf.startswith("PumpIdleSafe", j) and re.match(r"PumpIdleSafe\s*\(\s*\)\s*;", rf[j:]):
                top.append(depth)
        check(1 in top, "RootFinalizer must call PumpIdleSafe() at its top level, outside the try (found depths %r): "
                        "an early return on a fault would skip the Player-prev archive" % top)
        last_try = max([m.start() for m in re.finditer(r"\btry\b", rf)] or [-1])
        last_pump = rf.rfind("PumpIdleSafe")
        check(last_pump > rf.rfind("catch"), "PumpIdleSafe() must follow RootFinalizer's catch, not precede it")
        check(last_try < last_pump, "no try may open after the PumpIdleSafe() call in RootFinalizer")
        # Every path must REACH the pump. A `return` inside a plain try/catch leaves the METHOD, not just the try, so
        # "after the catch" is not enough: the pump must sit in a `finally` whose try opens before every return/throw,
        # or no return/throw may precede it at all (blind-check mutant B, gen 3).
        exits = [m.start() for m in re.finditer(r"\b(return|throw)\b", rf) if m.start() < last_pump]
        fin = None   # the finally block holding the last pump, if any
        for m in re.finditer(r"\bfinally\s*\{", rf):
            blk = body(rf[m.start():], r"finally")
            if blk and m.start() < last_pump < m.start() + len(blk) + (m.end() - m.start()):
                fin = m.start()
        if fin is not None:
            dep = [0] * (len(rf) + 1)   # brace depth at each offset, so the finally pairs with ITS try, not an inner one
            for j, c in enumerate(rf):
                dep[j + 1] = dep[j] + (c == "{") - (c == "}")
            guard_try = max([t.start() for t in re.finditer(r"\btry\b", rf)
                             if t.start() < fin and dep[t.start()] == dep[fin]] or [-1])
            bad = [e for e in exits if e < guard_try or e > fin]
        else:
            bad = exits
        check(not bad, "RootFinalizer has %d return/throw on a path that skips PumpIdleSafe() (offsets %r): a sampler "
                       "fault, Root.Update exception or invalid scope would lose the Player-prev archive; move the try "
                       "into a helper and call PumpIdleSafe() after it" % (len(bad), bad))

    # 5. Port of PumpArchive, swept: the archive never fires during or < idle s after a long event
    def simulate(frames, dt, idle_s):
        idle_since, fired_at, last_busy = -1.0, None, None
        t = 0.0
        for busy in frames:
            t += dt
            if busy:
                last_busy = t
            if fired_at is not None:
                continue
            if busy:
                idle_since = -1.0
                continue
            if idle_since < 0:
                idle_since = t
                continue
            if t - idle_since < idle_s:
                continue
            fired_at = t
        return fired_at, last_busy

    bad = 0
    runs = 0
    dt = 0.5
    for pattern in itertools.product((True, False), repeat=14):
        frames = []
        for b in pattern:
            frames.extend([b] * 3)          # 1.5 s blocks
        frames.extend([False] * 40)          # then 20 s idle
        runs += 1
        fired, _ = simulate(frames, dt, idle)
        if fired is None:
            bad += 1
            continue
        # every frame in the idle-window before firing must be idle
        k = int(round(fired / dt)) - 1
        window = frames[max(0, k - int(idle / dt)):k + 1]
        if any(window):
            bad += 1
    check(bad == 0, "PumpArchive port fired inside a long event's 10 s shadow (or never) in %d/%d runs" % (bad, runs))
    check(runs == 2 ** 14, "sanity: sweep ran %d patterns" % runs)
    # sanity probe: the port fires at all (gate 0 fires on the second idle frame after busy, t=1.5 s)
    f0, _ = simulate([True, False, False], dt, 0.0)
    check(f0 is not None and f0 == 1.5, "sanity: zero gate should fire at 1.5 s, got %r" % f0)

    if fails:
        for f in fails:
            print("FAIL:", f)
        return 1
    print("PASS: startup archive deferred past patching (idle gate %.0f s, %d frame patterns swept)" % (idle, runs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
