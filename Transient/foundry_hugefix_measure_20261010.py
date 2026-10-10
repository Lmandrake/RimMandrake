# HUGE_FOOTPRINTS_FIX_PROVE_SIXTY_ON_ROT: one fixed measurement procedure, run before and after the fix.
# python.exe Transient/foundry_hugefix_measure_20261010.py <label> [blockSeconds]   (from the repo root)
import sys, json, time, glob, os, subprocess, pathlib, datetime
sys.path.insert(0, str(pathlib.Path("src/RimMandrake/Utils").resolve()))
import rimbridge_client as rb

LABEL = sys.argv[1]; BLOCK = int(sys.argv[2]) if len(sys.argv) > 2 else 45
GIANTS = "AB_AgaricusDomeCap,AB_AgariluxPrime,AB_ArbuscularMycorrhiza,AB_DribblingCap,AB_GiantAgarilux,AB_WitchesOyster,RM_Arpeau,RM_Nogtyl,RM_PaleTree"
TPSDIR = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\JawaBench\tps"
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=200.0); S.connect()

def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r

def mem():
    o = subprocess.run(["powershell.exe", "-NoProfile", "-Command",
        "Get-Process RimWorldWin64 | % { \"$($_.Id) $($_.PrivateMemorySize64) $($_.WorkingSet64)\" }"], capture_output=True, text=True).stdout.split()
    return {"pid": int(o[0]), "privateGB": round(int(o[1]) / 2**30, 2), "wsGB": round(int(o[2]) / 2**30, 2)} if len(o) >= 3 else {"raw": o}

def rows_between(t0, t1):
    f = max(glob.glob(os.path.join(TPSDIR, "tps_*.jsonl")), key=os.path.getmtime)
    out = []
    for line in open(f, encoding="utf-8"):
        try: r = json.loads(line)
        except Exception: continue
        if r.get("kind") != "sample": continue
        u = datetime.datetime.strptime(r["utc"][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp()
        if t0 <= u - r["dReal"] and u <= t1: out.append(r)
    return f, out

def summarise(rows):
    if not rows: return {"rows": 0}
    ticks = sum(r["dTicks"] for r in rows); real = sum(r["dReal"] for r in rows); run = sum(r["runS"] for r in rows)
    stage = {}
    for r in rows:
        for k, v in (r.get("attr") or {}).items(): stage[k] = stage.get(k, 0) + v[1]
    return {"rows": len(rows), "ticks": ticks, "realS": round(real, 1), "tpsWall": round(ticks / real, 2) if real else None,
            "tpsRun": round(ticks / run, 2) if run else None, "ratioMean": round(sum((r["ratio"] or 0) for r in rows) / len(rows), 3),
            "gc": rows[-1]["gc"] - rows[0]["gc"] + 0, "gcPerMin": round((rows[-1]["gc"] - rows[0]["gc"]) / (real / 60), 2) if real else None,
            "gapMaxMs": max(r["gapMaxMs"] for r in rows), "heapMBmax": max(r["heapMB"] for r in rows), "fpsMean": round(sum(r["fps"] for r in rows) / len(rows), 1),
            "tickMsLast": rows[-1].get("tickMs"), "stageMsPerTick": {k: round(v / ticks, 2) for k, v in stage.items() if ticks and v / ticks >= 0.05},
            "tops": sorted({r.get("top") for r in rows if r.get("top")})}

res = {"label": LABEL, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "memStart": mem()}
cnt = call("jawa/list_things", defName=GIANTS, limit=1); blk = call("jawa/list_things", defName="RM_HugeTrunkBlocker", limit=1)
res["giants"] = cnt.get("countMatched"); res["blockers"] = blk.get("countMatched"); res["scanned"] = cnt.get("scanned")
pc = call("jawa/static_call", type="RimMandrake.HugeThings.MapComponent_HugeFootprints", method="DebugCounts", args="current")
res["footprintCounts"] = pc.get("result") if pc.get("success") else ("UNMEASURED: " + str(pc.get("error") or pc)[:200])
print(json.dumps(res), flush=True)
call("jawa/set_game_speed", speed="Normal"); time.sleep(5)
mct = call("jawa/map_comp_timing", ticks=300, maxSeconds=120)
res["mapCompTiming"] = {k: mct.get(k) for k in ("success", "ticksElapsed", "realSeconds", "sumMsPerTick", "componentsTimed")}
res["mapCompTiming"]["top"] = (mct.get("components") or [])[:5]
print(json.dumps(res["mapCompTiming"]), flush=True)
res["speeds"] = {}
for sp in ("Normal", "Fast", "Superfast"):
    call("jawa/set_game_speed", speed=sp); time.sleep(10)
    t0 = time.time(); time.sleep(BLOCK); t1 = time.time()
    time.sleep(6)   # let the covering 5 s sample land
    f, rows = rows_between(t0, t1 + 0.5)
    res["speeds"][sp] = summarise(rows); res["tpsFile"] = f
    print(sp, json.dumps(res["speeds"][sp]), flush=True)
call("jawa/set_game_speed", speed="Paused")
res["memEnd"] = mem()
blk2 = call("jawa/list_things", defName="RM_HugeTrunkBlocker", limit=1); cnt2 = call("jawa/list_things", defName=GIANTS, limit=1)
res["giantsEnd"] = cnt2.get("countMatched"); res["blockersEnd"] = blk2.get("countMatched")
out = "Transient/foundry_hugefix_measure_%s_20261010.json" % LABEL
json.dump(res, open(out, "w"), indent=1)
print("WROTE", out, json.dumps({k: res[k] for k in ("memStart", "memEnd", "giants", "blockers", "giantsEnd", "blockersEnd")}))
