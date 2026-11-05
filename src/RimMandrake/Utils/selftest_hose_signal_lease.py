#!/usr/bin/env python3
# selftest-timeout: 60
"""HOSE_SIGNAL_TAME_WITH_EXPIRY_TICK: HoseFlow.Signal reads expiry ticks, it does not walk the relay chain.

Advisory design/RimMandrake/hose_wire_algorithms_advisory_2026-10-28.md section 4 #6 (SETUP: one Signal phase 17.2 ms):
"Store 'flowing until tick T' and compare it, instead of walking the provider chain or relay chain each tick. A transfer
across the hose renews T; a cut, retract or despawn clears it in the same tick."

Runs without dotnet (the C# twin of part C is HoseNetCacheChecks' "debug lease" block in the FlowWorks SelfTest):
  A. source pins: the Signal path (HoseFlow.cs) holds no FedByDebug / RelayIndex / GetComponent / Feeders walk and
     compares hose.flowUntil and hose.debugFedTick; NetFlow compares the transfer-renewed flowUntil lease.
  B. lifecycle pins: CreditFlow renews flowUntil; EndLease clears both leases and bumps LeaseVersion; SetCarry calls
     EndLease off Laid (cut / retract / drop), despawn calls EndLease, ApplyLay ends the lease on a new end and bumps
     LeaseVersion, HoseChanged bumps it; DebugLeased restamps the SAME tick when RelayVersion or LeaseVersion moved and
     the stamp clears every reel before marking; with no flag on the map the stamp never calls RelayIndex().
  C. a Python port of HoseRelayIndex.DebugReach (forward stamp) equals the old upstream FedByDebug walk on 3000 random
     functional relay graphs (loops, free ends, unwalkable feeders, varied flags); two mutants of the port must go red.
Every pin is shown able to fail: each regex is run against a mutated copy and must miss.

    python3 src/RimMandrake/Utils/selftest_hose_signal_lease.py
"""
from __future__ import annotations

import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOSE = os.path.normpath(os.path.join(HERE, "..", "FlowWorks", "Source", "Hose"))
FAILS: list[str] = []
N = 0


def check(ok: bool, msg: str) -> None:
    global N
    N += 1
    if not ok:
        FAILS.append(msg)
        print("FAIL " + msg)


def read(name: str) -> str:
    with open(os.path.join(HOSE, name), encoding="utf-8") as f:
        return f.read()


def body(src: str, signature: str) -> str:
    """The brace-balanced body of the first member whose header matches `signature` (a regex)."""
    m = re.search(signature, src)
    if not m:
        return ""
    i = src.index("{", m.end() - 1) if src[m.end() - 1] != "{" else m.end() - 1
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return src[i:j + 1]
    return ""


def strip_comments(s: str) -> str:
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"//[^\n]*", "", s)


def pin(text: str, pattern: str, msg: str, mutate: tuple[str, str] | None = None, absent: bool = False) -> None:
    hit = re.search(pattern, text, flags=re.S) is not None
    check(hit != absent, msg)
    if mutate is not None:  # can-fail: the pin must flip on a copy with the clause broken
        bad = text.replace(mutate[0], mutate[1])
        check(bad != text and (re.search(pattern, bad, flags=re.S) is not None) == absent,
              "can-fail: " + msg + " (mutant " + repr(mutate[0][:40]) + ")")


# ------------------------------------------------------------------------------------------------- A. the Signal path
flow = strip_comments(read("HoseFlow.cs"))
debug_body = body(flow, r"class DebugHoseFlow\b[^{]*\{")
net_body = body(flow, r"class NetFlow\b[^{]*\{")
signal_body = body(flow, r"static bool Signal\(")
check(bool(debug_body and net_body and signal_body), "HoseFlow.cs: NetFlow, DebugHoseFlow and Signal found")
signal_path = debug_body + net_body + signal_body
for walker in ("FedByDebug", "RelayIndex", "GetComponent", "Feeders", "FeedersOf", "while", "Stack<", "HashSet<"):
    pin(signal_path, re.escape(walker), "Signal path calls no " + walker, absent=True)
check(re.search("FedByDebug", signal_path + "comp.FedByDebug(hose)") is not None,
      "can-fail: the walker pin sees a FedByDebug call")
pin(net_body, r"Flowing\(\s*hose\.flowUntil\s*,\s*now\s*\)", "NetFlow compares the hose's flowUntil lease with now",
    mutate=("hose.flowUntil", "hose.pendingUntil"))
pin(debug_body, r"hose\.hoseComp", "DebugHoseFlow reads the reel's registered map (no GetComponent)",
    mutate=("hose.hoseComp", "hose.parent.Map"))
pin(debug_body, r"DebugLeased\(\s*hose\s*,\s*now\s*\)", "DebugHoseFlow asks the map's per-tick lease",
    mutate=("DebugLeased(hose, now)", "FedByDebug(hose)"))

# --------------------------------------------------------------------------------------------- B. lifecycle of a lease
reel = strip_comments(read("CompHoseReel.cs"))
comp = strip_comments(read("RM_MapComponent_Hoses.cs"))
relay = strip_comments(read("HoseRelay.cs"))

credit = body(reel, r"void CreditFlow\(")
pin(credit, r"flowUntil\s*=\s*[\w.]*Lease\(\s*flowUntil\s*,\s*now\s*,\s*cadence\s*\)", "a transfer (CreditFlow) renews flowUntil",
    mutate=("flowUntil = ", "flowUntilX = "))
end = body(reel, r"void EndLease\(\)")
pin(end, r"flowUntil\s*=\s*[\w.]*NoLease", "EndLease clears the net lease", mutate=("NoLease", "Lease0"))
pin(end, r"debugFedTick\s*=\s*int\.MinValue", "EndLease clears the debug lease", mutate=("debugFedTick", "debugFedTock"))
pin(end, r"LeaseVersion\+\+", "EndLease marks the debug stamp stale (same-tick restamp)", mutate=("LeaseVersion++", "LeaseVersion--"))
setc = body(reel, r"void SetCarry\(")
pin(setc, r"if\s*\(\s*s\s*!=\s*HoseCarryState\.Laid\s*\)\s*EndLease\(\)", "leaving Laid (cut, retract, drop) ends the lease",
    mutate=("EndLease()", "EndLeaseLater()"))
pin(setc, r"RelayVersion\+\+", "a carry change bumps RelayVersion")
pin(reel, r"lay\s*=\s*null;\s*port\s*=\s*null;\s*sm\.ResetFlat\(\);\s*EndLease\(\);", "despawn ends the lease")
changed = body(reel, r"void HoseChanged\(\)")
pin(changed, r"lay\s*=\s*null;\s*RM_MapComponent_Hoses\.LeaseVersion\+\+", "a reset lay (HoseChanged) marks the stamp stale")
apply = body(comp, r"void ApplyLay\(")
pin(apply, r"r\.layEnd\s*!=\s*endCell\)\s*r\.EndLease\(\)", "a lay to a new end (or a refused lay) ends the lease")
pin(apply, r"r\.lay\s*=[^;]*;\s*LeaseVersion\+\+", "ApplyLay marks the stamp stale after it sets the lay")
reg = body(comp, r"void Register\(")
pin(reg + comp, r"r\.hoseComp\s*=\s*this", "Register gives the reel its map")
dereg = body(comp, r"void Deregister\(")
pin(dereg, r"r\.hoseComp\s*=\s*null", "Deregister takes the map back")
pin(dereg, r"r\.debugFedTick\s*=\s*int\.MinValue", "Deregister ends the debug lease")

leased = body(comp, r"bool DebugLeased\(")
pin(leased, r"debugStampTick\s*!=\s*now\s*\|\|\s*debugStampRelay\s*!=\s*RelayVersion\s*\|\|\s*debugStampLease\s*!=\s*LeaseVersion",
    "DebugLeased restamps on a new tick OR the same tick when RelayVersion / LeaseVersion moved",
    mutate=(" || debugStampLease != LeaseVersion", ""))
pin(leased, r"r\.debugFedTick\s*==\s*now", "DebugLeased compares the reel's expiry tick with now", mutate=("== now", "<= now"))
stamp = body(comp, r"void StampDebugLeases\(")
check(bool(stamp), "StampDebugLeases found")
m_clear = re.search(r"debugFedTick\s*=\s*int\.MinValue", stamp)
m_noflag = re.search(r"if\s*\(\s*!any\s*\)\s*return;", stamp)
m_index = re.search(r"RelayIndex\(\)", stamp)
check(bool(m_clear and m_noflag and m_index) and m_clear.start() < m_noflag.start() < m_index.start(),
      "the stamp clears every reel, then returns before RelayIndex() when no reel carries a flag")
pin(stamp, r"\.DebugReach\(\s*i\s*=>\s*relayOrder\[i\]\.laid\s*&&\s*relayOrder\[i\]\.lay\s*!=\s*null",
    "the stamp passes the flag on through the same walkable rule FedByDebug used (laid with a lay)")
reach_body = body(relay, r"void DebugReach\(")
check(bool(reach_body), "HoseRelayIndex.DebugReach found")
for walker in ("Feeders(", "FedByDebug", "HashSet<", "Stack<"):
    pin(reach_body, re.escape(walker), "DebugReach walks forward only (no " + walker + ")", absent=True)


# ------------------------------------------------------------------------- C. the forward stamp == the old upstream walk
def build(nxt: list[int]):
    """onCycle and feeders of a functional graph, as HoseRelayIndex.Rebuild computes them."""
    n = len(nxt)
    on, state = [False] * n, [0] * n
    for s in range(n):
        if state[s]:
            continue
        path, i = [], s
        while i >= 0 and state[i] == 0:
            state[i] = 1
            path.append(i)
            i = nxt[i]
        if i >= 0 and state[i] == 1:
            for k in path[path.index(i):]:
                on[k] = True
        for p in path:
            state[p] = 2
    feeders = [[] for _ in range(n)]
    for j in range(n):
        if nxt[j] >= 0 and not on[j]:
            feeders[nxt[j]].append(j)
    return on, feeders


def fed_by_debug(r, debug, feeders, walk):  # HoseRelayIndex.FedByDebug, line for line
    if not any(debug):
        return False
    seen, stack = {r}, [r]
    while stack:
        for f in feeders[stack.pop()]:
            if f in seen or not walk[f]:
                seen.add(f)
                continue
            seen.add(f)
            if debug[f]:
                return True
            stack.append(f)
    return False


def debug_reach(nxt, on, debug, walk, mutant=0):  # HoseRelayIndex.DebugReach, line for line
    n = len(nxt)
    reach = [False] * n
    if not any(debug):
        return reach
    for d in range(n):
        if not debug[d] or not walk[d]:
            continue
        x = d
        while mutant == 1 or not on[x]:
            y = nxt[x]
            if y < 0:
                break
            if reach[y]:
                break
            reach[y] = True
            if mutant != 2 and not walk[y]:
                break
            x = y
    return reach


rng = random.Random(20261105)
same = [True, True, True]
saw = {"fed": 0, "loop": 0, "unwalked": 0, "notfed": 0}
for case in range(3000):
    n = rng.randint(1, 40)
    nxt = [rng.randrange(-1, n) if rng.random() < 0.85 else -1 for _ in range(n)]
    nxt = [-1 if v == i else v for i, v in enumerate(nxt)]  # a reel never relays into itself
    on, feeders = build(nxt)
    debug = [rng.random() < 0.15 for _ in range(n)]
    walk = [rng.random() < 0.8 for _ in range(n)]
    old = [fed_by_debug(r, debug, feeders, walk) for r in range(n)]
    for mut in (0, 1, 2):
        if debug_reach(nxt, on, debug, walk, mut) != old:
            same[mut] = False
    saw["fed"] += sum(old)
    saw["notfed"] += n - sum(old)
    saw["loop"] += sum(on)
    saw["unwalked"] += sum(1 for r in range(n) if old[r] and not walk[r])
check(same[0], "DebugReach == FedByDebug on every reel of 3000 random relay graphs")
check(all(v > 100 for v in saw.values()), "the sweep exercised fed, unfed, loop and unwalkable reels " + repr(saw))
check(not same[1], "can-fail: a stamp that walks round a loop differs from FedByDebug")
check(not same[2], "can-fail: a stamp that passes the flag through an unwalkable reel differs from FedByDebug")

print(f"selftest_hose_signal_lease: {N - len(FAILS)}/{N} checks passed")
sys.exit(1 if FAILS else 0)
