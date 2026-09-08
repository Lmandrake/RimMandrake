"""DROID_PROTOCOL_TRADE_ADVANTAGE_1 (C4) live proof.

Measures a real trade's buy/sell prices with and without a Protocol-family
droid in the player's party, through jawa/trade_price_probe (which opens a
headless TradeSession and reads Tradeable.GetPriceFor - the same accessor the
trade dialog uses).
"""
import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rbc

host, port, token = rbc.resolve_endpoint()
S = rbc.RimBridge(host=host, port=port, token=token, timeout=600.0)
S.connect()


def call(tool, **p):
    r = S.call(tool, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r


print("== starting quicktest ==")
print(call("rimworld/start_debug_game_ready", timeoutMs=280000,
           readiness="mapData", pauseIfNeeded=True).get("success"))
for _ in range(120):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing":
        break
    time.sleep(1)
print("state:", st.get("programState"))

cols = call("rimworld/list_colonists", currentMapOnly=True)
lst = cols.get("colonists") or cols.get("pawns") or []
print("colonists:", len(lst))
if not lst:
    print("NO COLONISTS - abort")
    sys.exit(1)
first = lst[0]
cx = first.get("x") or (first.get("position") or {}).get("x")
cz = first.get("z") or (first.get("position") or {}).get("z")
print("anchor cell:", cx, cz, first.get("name"))

print("\n== firing trade caravan ==")
inc = call("jawa/fire_incident", incidentDef="TraderCaravanArrival", dryRun=False)
print(json.dumps({k: inc.get(k) for k in ("success", "fired", "canFireNow", "message", "error")}))
call("rimworld/step_game_ticks", ticks=200)


def probe(tag):
    r = call("jawa/trade_price_probe", maxRows=12)
    print("\n---- probe:", tag, "----")
    if not r.get("success"):
        print("FAILED:", json.dumps(r)[:600])
        return None
    print("trader:", r.get("traderName"), r.get("traderKind"), r.get("traderFaction"))
    print("negotiator:", r.get("negotiatorName"),
          "TradePriceImprovement=", r.get("negotiatorTradePriceImprovement"))
    pp = r.get("playerParty") or []
    tp = r.get("traderParty") or []
    print("playerParty n=%d  protocol(chassis1)=%s"
          % (len(pp), [p["label"] for p in pp if p.get("droidChassisClass") == 1]))
    print("traderParty n=%d  protocol(chassis1)=%s"
          % (len(tp), [p["label"] for p in tp if p.get("droidChassisClass") == 1]))
    print("tradeables:", r.get("tradeableCount"))
    for row in (r.get("prices") or []):
        print("   %-28s base %8.2f  buy %8.2f  sell %8.2f"
              % (row["defName"], row["baseMarketValue"], row["buy"], row["sell"]))
    return r


a = probe("BEFORE - no protocol droid in the colony")

print("\n== spawning a protocol droid into the player faction ==")
sp = call("jawa/spawn_pawn", kindDef="RSW_DW_OuterRim_ProtocolDroid",
          x=cx, z=cz, faction="player", count=1)
print(json.dumps({k: sp.get(k) for k in ("success", "spawned", "pawnIds", "message", "error")})[:500])

# The patch caches its verdict for 250 ticks per (trader, negotiator); step past it.
call("rimworld/step_game_ticks", ticks=400)

b = probe("AFTER - protocol droid in the colony")

if a and b:
    print("\n==== DELTA ====")
    # Key by POSITION, not defName: a trader can carry two distinct tradeables
    # of the same def (two Chicken stacks) and a defName dict silently aliases
    # them into a nonsense ratio.
    for i, r in enumerate(b["prices"]):
        if i >= len(a["prices"]):
            break
        d = a["prices"][i]
        if d["defName"] != r["defName"]:
            print("   row %d order changed (%s vs %s) - skipped" % (i, d["defName"], r["defName"]))
            continue
        bf = r["buy"] / d["buy"] if d["buy"] else 0
        sf = r["sell"] / d["sell"] if d["sell"] else 0
        print("   %-28s buy x%.4f   sell x%.4f" % (r["defName"], bf, sf))
