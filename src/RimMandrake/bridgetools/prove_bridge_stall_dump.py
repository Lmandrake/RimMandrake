"""Live proof of BRIDGE_STALL_DIAGNOSTIC_1 clause A1. Run under WINDOWS python.exe (the bridge is reachable only there).

Freezes the game's main thread for 75 s with jawa/tps_test_block (GM build; changes no game state), so the call
blocks past JawaBenchStallDump.DumpSeconds, then checks, read-only:
  * the companion's watchdog wrote a NEW stall_<session>_NN.json in the game's JawaBench\\tps record dir during the
    block, with silentS >= 60, a phaseStack, a probe object, a mainStack text-or-error, and the main thread flagged
    among the listed native threads;
  * this client's evidence `end` row for that call names the same file in stall_dumps.
Exit 0 when both hold, 1 when either does not, 2 when the proof could not run (no bridge, tool absent).

SITE first (gen13, 2026-11-04): the game's BridgeTools\\JawaBench\\JawaBench.BridgeTools.dll must be built from THIS
checkout's companion sources (companion_identity FRESH) and be older than the running game's Player.log, else the run
proves an old DLL: the e26a661423 fix read FAIL twice on the d62e3e51 DLL because nothing deployed the companion.
Such a run exits 1 with a `SITE:` line before any block, never a mod verdict.
"""
import json
import os
import sys
import time

_RM_ROOT = __import__("pathlib").Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_RM_ROOT / "src" / "RimMandrake" / "Utils"))
import rimbridge_client as rb  # noqa: E402

BLOCK_S = 75.0
_BT = _RM_ROOT / "src" / "RimMandrake" / "bridgetools"
DLL = os.environ.get("RM_COMPANION_DLL") or (
    r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll")


def site_check(dll=DLL, repo_root=str(_RM_ROOT), log=None):
    """-> None when the game can be running this checkout's companion, else the SITE reason (one line)."""
    sys.path.insert(0, str(_BT))
    import companion_identity as ci
    v = ci.verdict(dll, repo_root, None, want=ci.srchash_worktree(repo_root))
    if v["state"] != "FRESH":
        return "deployed companion is not this checkout's build: " + ci.describe(v)
    log = log or rb.DEFAULT_PLAYER_LOG
    if os.path.isfile(log) and os.path.getmtime(dll) > os.stat(log).st_ctime:
        return "deployed companion %s was written after the running game opened %s: not loaded until a restart" % (
            dll, log)
    return None


def main():
    why = site_check()
    if why:
        print("SITE: " + why)
        print("prove_bridge_stall_dump: FAIL (site, not the mod)")
        return 1
    d = rb._stall_dir()
    if not d or not os.path.isdir(d):
        print("UNMEASURED: no stall record dir %r" % d)
        return 2
    before = set(n for n in os.listdir(d) if n.startswith("stall_"))
    host, port, token = rb.resolve_endpoint()
    t0 = time.time()
    try:
        with rb.RimBridge(host, port, token, timeout=BLOCK_S + 60, client_name="prove_bridge_stall_dump.py") as c:
            out = c.call("jawa/tps_test_block", {"seconds": BLOCK_S})
    except Exception as ex:  # noqa: BLE001
        print("UNMEASURED: jawa/tps_test_block failed: %s" % ex)
        return 2
    time.sleep(2)
    new = sorted(n for n in os.listdir(d) if n.startswith("stall_") and n.endswith(".json") and n not in before)
    fails = []
    if not new:
        fails.append("no new stall dump in %s after a %.0f s block (reply %r)" % (d, BLOCK_S, out))
    for n in new[:1]:
        r = json.load(open(os.path.join(d, n), encoding="utf-8"))
        if not r.get("silentS", 0) >= 60:
            fails.append("%s silentS %r < 60" % (n, r.get("silentS")))
        if not r.get("phaseStack"):
            fails.append("%s has no phaseStack" % n)
        if not isinstance(r.get("probe"), dict):
            fails.append("%s probe is not an object" % n)
        else:   # the probe's shape on a real stall (offline twin: src/RimMandrake/Utils/selftest_stall_probe.py)
            pr = r["probe"]
            for k in ("ticksGameNow", "capture", "tickList", "errors"):
                if k not in pr:
                    fails.append("%s probe lacks %r: %r" % (n, k, sorted(pr)))
            if pr.get("errors"):
                fails.append("%s probe read errors on a still main thread: %r" % (n, pr.get("errors")))
            if pr.get("tickList") is not None:   # inside a tick list: the bucket is the entered tick's, and nothing moved
                iv = {"Rare": 250, "Long": 2000}.get(pr.get("tickList"), 1)
                et = pr.get("enteredTick")
                if not isinstance(et, int) or et < 0 or pr.get("bucket") != et % iv:
                    fails.append("%s probe bucket %r is not enteredTick %r %% %d" % (n, pr.get("bucket"), et, iv))
                if pr.get("changedDuringRead") is not False:
                    fails.append("%s probe changedDuringRead %r on a frozen main thread" % (n, pr.get("changedDuringRead")))
        ms = r.get("mainStack") or {}
        if not ("text" in ms or "error" in ms):
            fails.append("%s mainStack has neither text nor error" % n)
        if not any(t.get("main") for t in r.get("threads") or []):
            fails.append("%s does not flag the main thread among %d threads" % (n, len(r.get("threads") or [])))
        print("dump %s: phaseStack=%s silentS=%s mainStack=%s probe.keys=%s tickList=%r"
              % (n, r.get("phaseStack"), r.get("silentS"), (ms.get("error") or "text")[:120], sorted(r.get("probe") or {}),
                 (r.get("probe") or {}).get("tickList")))
    ends = []
    if rb.EVIDENCE_LOG and os.path.exists(rb.EVIDENCE_LOG):
        rows = [json.loads(x) for x in open(rb.EVIDENCE_LOG, encoding="utf-8").read().splitlines()[-400:] if x.strip()]
        starts = {r["cid"] for r in rows if r.get("ev") == "start" and r.get("tool") == "jawa/tps_test_block"}
        ends = [r for r in rows if r.get("ev") == "end" and r.get("cid") in starts]
    if not ends:
        fails.append("no evidence end row for the block call in %r" % rb.EVIDENCE_LOG)
    elif new and new[0] not in (ends[-1].get("stall_dumps") or []):
        fails.append("the call's end row does not name %s: %r" % (new[0], ends[-1].get("stall_dumps")))
    for f in fails:
        print("FAIL", f)
    print("prove_bridge_stall_dump: %s (%.0f s)" % ("PASS" if not fails else "FAIL", time.time() - t0))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
