"""Party + marriage ceremony on a CALM map - the first run had a fleshbeast assault."""
import sys, json, time
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0); S.connect()
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

print("== make the map CALM: remove hostile pawns and their lords ==")
brief = call("jawa/pawn_get", limit=60)["pawns"]
hostiles = [p for p in brief if p.get("faction") not in ("PlayerColony", None)]
print("   hostile pawns present:", len(hostiles), sorted(set(str(p.get("faction")) for p in hostiles)))
for h in hostiles:
    call("jawa/destroy_batch", ops="%d,%d,1,1" % (h["x"], h["z"]))
call("jawa/social_cancel", action="remove", all=True)
lords = call("jawa/social_cancel", action="list")
print("   lords remaining:", lords.get("lordsBefore"))
for x in (lords.get("lords") or []): print("      ", x)

# time of day matters: hour must be 4-21 for a party
t = call("jawa/weather_get")
print("   danger/weather:", t.get("weather", {}).get("current"))

print("\n== PARTY, unforced (should now pass or name the real gate) ==")
u = call("jawa/social_gathering_start", gathering="Party", force=False)
print("   ok:", u.get("success"), " started:", u.get("started"), "|", (u.get("message") or "")[:150])

print("\n== PARTY, forced ==")
call("jawa/social_cancel", action="remove", all=True)
p = call("jawa/social_gathering_start", gathering="Party", force=True)
print("   started:", p.get("started"), " lords %s -> %s" % (p.get("lordsBefore"), p.get("lordsAfter")))
for n in (p.get("notes") or []): print("      ", n[:140])

print("\n== step time so colonists can SELF-JOIN (attendees are pull, not push) ==")
call("rimworld/step_game_ticks", ticks=400)
c = call("jawa/social_cancel", action="list")
for x in (c.get("lords") or []):
    if x["social"]: print("   %s now has %d pawns" % (x["job"], x["pawns"]))

print("\n== MARRIAGE CEREMONY on the calm map ==")
call("jawa/social_cancel", action="remove", all=True)
cols = [b for b in call("jawa/pawn_get", limit=20)["pawns"] if b.get("faction") == "PlayerColony"]
A, B = str(cols[0]["thingIdNumber"]), str(cols[1]["thingIdNumber"])
m = call("jawa/social_marry", pawn=A, otherPawn=B, ceremony=True)
print("   ceremonyStarted:", m.get("ceremonyStarted"), " lords:", m.get("lords"))
for n in (m.get("notes") or []): print("      ", n[:140])
call("rimworld/step_game_ticks", ticks=400)
c2 = call("jawa/social_cancel", action="list")
for x in (c2.get("lords") or []):
    if x["social"]: print("   %s has %d pawns" % (x["job"], x["pawns"]))
