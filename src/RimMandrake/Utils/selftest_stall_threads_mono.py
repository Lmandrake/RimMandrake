#!/usr/bin/env python3
"""Offline guard for the stall dump's thread list under the GAME's runtime (BRIDGE_STALL_DIAGNOSTIC_1).

    python3 src/RimMandrake/Utils/selftest_stall_threads_mono.py           text guard + instrument sanity probes
    python3 src/RimMandrake/Utils/selftest_stall_threads_mono.py --remeasure  also re-read the game's System.dll (Windows)

Why it exists. Live clause A1 FAILED on the running game (2026-11-04, build d62e3e51c6, log
/home/mandrake/rm/relentless/live/BRIDGE_STALL_DIAGNOSTIC_1-A1-20261104T063433Z.log): the watchdog wrote
stall_da77b5d5be334584995bd7bbe19de118_01.json at silentS 60.5 with phaseStack, probe and mainStack, but
"threadCount": 0, "threads": [] - so no thread was flagged main and mainCpuDeltaS (spinning vs waiting) was null.
The TPS harness (TpsMathSelfTest, net8 CoreCLR) stays green because CoreCLR's Process.Threads is real.

MEASURED 2026-11-04 with ilspycmd on the game's own
C:\\Program Files (x86)\\Steam\\steamapps\\common\\RimWorld\\RimWorldWin64_Data\\Managed\\System.dll (Unity Mono):

    threads = new ProcessThreadCollection(new ProcessThread[GetProcessData(processId, 0, out var _)]);

i.e. Process.Threads is an array of NULL entries: under the game it can never yield a thread id or CPU time. So the
dump's thread list must not come from Process.Threads at all (e.g. kernel32 CreateToolhelp32Snapshot + Thread32First/
Next filtered by GetCurrentProcessId, OpenThread + GetThreadTimes for CPU). This guard is RED while ThreadsFields in
JawaBenchStallDump.cs reads Process.Threads / ProcessThread, and green once it does not AND names a thread source.

Sanity probes (the instrument must see): the guard is red on a synthetic body that iterates Process.Threads, and
green on one that walks a Toolhelp32 snapshot; a missing ThreadsFields is a FAIL, never a pass.
"""
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DUMP = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "JawaBench.BridgeTools", "JawaBenchStallDump.cs")
GAME_SYSTEM_DLL = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\System.dll"
ILSPY = "/mnt/c/Users/Mandrake/.dotnet/tools/ilspycmd.exe"
MONO_NULL_ARRAY = "new ProcessThreadCollection(new ProcessThread[GetProcessData(processId, 0,"

# what reads the thread list through the BCL Process API (empty/null under Unity Mono)
BCL_THREADS = [re.compile(p) for p in (r"\.Threads\b", r"\bProcessThread\b", r"\bProcessThreadCollection\b")]
# a native thread source the game's runtime can actually answer
NATIVE_SOURCE = re.compile(r"\bCreateToolhelp32Snapshot\b|\bThread32(First|Next)\b|\bNtQuerySystemInformation\b")


def method_body(text, name):
    """The brace-balanced body of method `name` (first definition), comments stripped; None if absent."""
    m = re.search(r"\b" + re.escape(name) + r"\s*\([^)]*\)\s*\{", text)
    if not m:
        return None
    i, depth = m.end() - 1, 0
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                body = text[i:j + 1]
                body = re.sub(r"//[^\n]*", "", body)
                return re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    return None


def callees(text, body):
    """Bodies of same-file methods ThreadsFields calls (one level), so a helper cannot hide the BCL read."""
    out = []
    for name in sorted(set(re.findall(r"\b([A-Z][A-Za-z0-9_]*)\s*\(", body))):
        if name in ("ThreadsFields",):
            continue
        b = method_body(text, name)
        if b:
            out.append(b)
    return out


def guard(text):
    """[] when the thread list cannot come from Process.Threads and names a native source; else the reasons."""
    body = method_body(text, "ThreadsFields")
    if body is None:
        return ["ThreadsFields not found in JawaBenchStallDump.cs (the guard cannot see; not a pass)"]
    reach = [body] + callees(text, body)
    fails = []
    for rx in BCL_THREADS:
        if any(rx.search(b) for b in reach):
            fails.append("ThreadsFields reads the thread list via `%s`; under the game's Unity Mono Process.Threads "
                         "is an array of null ProcessThread entries (threadCount 0 live)" % rx.pattern)
    if not any(NATIVE_SOURCE.search(b) for b in reach) and not NATIVE_SOURCE.search(text):
        fails.append("ThreadsFields names no native thread source (CreateToolhelp32Snapshot/Thread32Next/...)")
    return fails


SYN_BAD = """class X { internal static string ThreadsFields() {
    foreach (ProcessThread pt in Process.GetCurrentProcess().Threads) { var c = pt.TotalProcessorTime; }
    return ""; } }"""
SYN_GOOD = """class X { internal static string ThreadsFields() {
    IntPtr snap = CreateToolhelp32Snapshot(4, 0); var e = new THREADENTRY32();
    for (bool ok = Thread32First(snap, ref e); ok; ok = Thread32Next(snap, ref e)) { if (e.th32OwnerProcessID == Pid()) {} }
    return ""; } static uint Pid() { return 0; } }"""


def remeasure():
    """Re-read the game's System.dll: does Process.Threads still build an array of nulls? None = could not measure."""
    if not os.path.exists(ILSPY) or not shutil.which("wslpath") and not os.path.exists("/mnt/c"):
        return None
    try:
        p = subprocess.run([ILSPY, "-t", "System.Diagnostics.Process", GAME_SYSTEM_DLL], capture_output=True,
                           text=True, timeout=300)
    except Exception:  # noqa: BLE001 - no Windows program reachable: unmeasured, said so
        return None
    if p.returncode != 0 or "class Process" not in p.stdout:
        return None
    return MONO_NULL_ARRAY in p.stdout


def main(argv):
    fails = []
    # instrument sanity: it must see both ways
    if not guard(SYN_BAD):
        fails.append("SANITY: guard passed a body iterating Process.Threads (instrument blind)")
    if guard(SYN_GOOD):
        fails.append("SANITY: guard failed a Toolhelp32 body: %s" % guard(SYN_GOOD))
    if guard("class X {}") == []:
        fails.append("SANITY: guard passed a file with no ThreadsFields")
    with open(DUMP, encoding="utf-8") as f:
        text = f.read()
    for r in guard(text):
        fails.append("JawaBenchStallDump.cs: " + r)
    if "--remeasure" in argv:
        m = remeasure()
        if m is None:
            print("remeasure: UNMEASURED (no ilspycmd.exe / game System.dll reachable)")
        elif m:
            print("remeasure: game System.dll Process.Threads still builds an array of null ProcessThread entries")
        else:
            print("remeasure: game System.dll Process.Threads NO LONGER matches the null-array form - re-read it")
    for x in fails:
        print("FAIL", x)
    print("selftest_stall_threads_mono: %s" % ("PASS" if not fails else "FAIL (%d)" % len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
