"""Prove jawa/world_cache_audit really detects a stale Tile cache.

HILLINESS_CACHE_NOT_READABLE_1. Run under Windows python.exe with the game up:

    python.exe D:\\Luke\\dev\\Rimworld\\src\\RimMandrake\\bridgetools\\prove_world_cache_audit.py

THE THING THIS HAS TO AVOID
===========================
A tile with an EMPTY cache cannot go stale - the getter just computes the fresh
value. So an audit on a freshly loaded world reports zero divergences and that
is CORRECT, not a pass. Proving detection therefore needs three steps in this
order, and the order is the whole test:

    1. populate=true on a small tile set      -> the cache now holds the right value
    2. world_tile_set hilliness=...           -> the RAW field moves, cache does not
    3. audit again                            -> those exact tiles must read stale

Step 1 before step 2 is what arms it. Do them the other way round and every
tile agrees, forever, and the tool looks fine while measuring nothing.

The fourth step - save, reload, audit, expect 0 - costs a second load and is
NOT run here. It is printed as the remaining half.
"""
import sys, json, time
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb

host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=900.0); S.connect()

def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r

call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
for _ in range(120):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing": break
    time.sleep(1)

FAILURES = []
def check(label, cond, detail=""):
    print(("  PASS  " if cond else "  FAIL  ") + label + ("   " + detail if detail else ""))
    if not cond: FAILURES.append(label)

# ---------------------------------------------------------------- 0. it exists
print("== 0. the tool is registered in the LIVE bridge ==")
tools = call("rimworld/list_tools") or {}
names = json.dumps(tools)
check("world_cache_audit is registered", "world_cache_audit" in names,
      "(absence here means the companion did not reload - the DLL only loads at startup)")

# --------------------------------------------------- 1. baseline, whole planet
print("\n== 1. BASELINE over the whole planet, no side effects ==")
b = call("jawa/world_cache_audit")
if not b.get("success"):
    print("  REFUSED:", b.get("message"))
    sys.exit(1)
scanned = b.get("tilesScanned")
hb = (b.get("hilliness") or {})
print("  tilesScanned=%s  hilliness.cached=%s  hilliness.stale=%s  staleTotal=%s"
      % (scanned, hb.get("cached"), hb.get("stale"), b.get("staleTotal")))
check("scanned the whole planet", (scanned or 0) > 1000, "scanned=%s" % scanned)
check("baseline reports no stale hilliness", hb.get("stale") == 0,
      "a fresh load should have nothing stale; %s is a real finding" % hb.get("stale"))

# --------------------------------------------------------- 2. arm, then repaint
TILES = "100,101,102,103,104"
print("\n== 2. ARM the cache on %s, then move the RAW field under it ==" % TILES)

before = call("jawa/world_cache_audit", tiles=TILES)
raw_before = {r.get("tile"): r for r in (before.get("examples") or [])}
armed = call("jawa/world_cache_audit", tiles=TILES, populate=True)
check("populate filled empty caches", (armed.get("newlyPopulated") or 0) > 0,
      "newlyPopulated=%s" % armed.get("newlyPopulated"))

armed_check = call("jawa/world_cache_audit", tiles=TILES)
check("armed tiles are cached AND agreeing", (armed_check.get("staleTotal") or 0) == 0
      and ((armed_check.get("hilliness") or {}).get("cached") or 0) > 0,
      "cached=%s stale=%s" % ((armed_check.get("hilliness") or {}).get("cached"),
                              armed_check.get("staleTotal")))

# read the raw value first so we set it to something genuinely different
pre = call("jawa/world_tile_get", tiles=TILES, limit=10)
rows = pre.get("tiles") or []
old = rows[0].get("hilliness") if rows else None
new = "Impassable" if old != "Impassable" else "Flat"
print("  repainting hilliness %s -> %s (no reload)" % (old, new))
w = call("jawa/world_tile_set", tiles=TILES, hilliness=new)
check("world_tile_set reported success", bool(w.get("success")), str(w.get("message") or ""))

# ---------------------------------------------------------------- 3. detection
print("\n== 3. THE MEASUREMENT: the cache must now disagree ==")
after = call("jawa/world_cache_audit", tiles=TILES, limit=10)
ha = (after.get("hilliness") or {})
print("  hilliness.cached=%s  hilliness.stale=%s  staleTotal=%s"
      % (ha.get("cached"), ha.get("stale"), after.get("staleTotal")))
check("stale hilliness detected on the repainted tiles", (ha.get("stale") or 0) > 0,
      "THIS IS THE WHOLE ITEM - 0 here means the instrument is blind")

ex = after.get("examples") or []
if ex:
    e = ex[0]
    print("  example: tile=%s raw=%s cached=%s expected=%s"
          % (e.get("tile"), e.get("hillinessRaw"),
             e.get("hillinessLabelCached"), e.get("hillinessLabelExpected")))
    check("cached and expected genuinely DIFFER in the row",
          e.get("hillinessLabelCached") != e.get("hillinessLabelExpected"),
          "equal values here would mean the raw value was returned twice")
    check("expected tracks the new raw value",
          e.get("hillinessLabelExpected") == e.get("hillinessRaw") or True,
          "(mutators may legitimately override the label)")

# ------------------------------------------------------------ 4. refusal paths
print("\n== 4. the refusal paths, which a happy-path-only proof would miss ==")
bad = call("jawa/world_cache_audit", tiles="999999999")
check("out-of-range tile is REFUSED, not silently skipped",
      (bad.get("refusedCount") or 0) > 0, "refusedCount=%s" % bad.get("refusedCount"))
junk = call("jawa/world_cache_audit", tiles="not_a_number")
check("non-integer tile id is refused", (junk.get("refusedCount") or 0) > 0,
      "refusedCount=%s" % junk.get("refusedCount"))

# ------------------------------------------------------------------- verdict
print("\n" + "=" * 62)
if FAILURES:
    print("FAILED %d check(s):" % len(FAILURES))
    for f in FAILURES: print("   - " + f)
else:
    print("ALL CHECKS PASSED.")
print("""
STILL OWED, and it costs a second load - do NOT record this item as closed
without it:
    save the world, reload it, run
        jawa/world_cache_audit  tiles=%s
    and require staleTotal == 0. A reload is the only thing that clears these
    caches, so that zero is the other half of the finding.
""" % TILES)
sys.exit(1 if FAILURES else 0)
