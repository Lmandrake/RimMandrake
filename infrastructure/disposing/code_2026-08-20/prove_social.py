"""Parties, marriages, funerals, rituals."""
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

print("== 1. WHAT CAN THIS GAME RUN? ==")
l = call("jawa/social_list")
print("   ideologyActive:", l.get("ideologyActive"), " activeLords:", l.get("activeLords"))
for g in (l.get("gatherings") or []):
    print("   gathering %-18s now=%-5s ignoringConditions=%-5s respectsTimetable=%s hasDuty=%s" % (
        g["def"], g["canExecuteNow"], g["canExecuteIgnoringConditions"], g["respectTimetable"], g["hasDuty"]))
print("   ritual precepts on the player ideo:", l.get("ritualCount"))
for r in (l.get("rituals") or [])[:8]:
    print("      %-22s blocked: %s" % (r["precept"], (r["blockedBecause"] or "(nothing - can start)")[:70]))

print("\n== 2. THROW A PARTY (forced) ==")
p = call("jawa/social_gathering_start", gathering="Party", force=True)
print("   started:", p.get("started"), " lords %s -> %s" % (p.get("lordsBefore"), p.get("lordsAfter")))
for n in (p.get("notes") or []): print("      ", n[:130])

print("\n== 3. UNFORCED, to see which gate refuses ==")
call("jawa/social_cancel", action="remove", all=True)
u = call("jawa/social_gathering_start", gathering="Party", force=False)
print("   ok:", u.get("success"), "|", (u.get("message") or "")[:170])

print("\n== 4. MARRIAGE — ceremony ==")
brief = call("jawa/pawn_get", limit=20)["pawns"]
cols = [b for b in brief if b.get("faction") == "PlayerColony"]
A, B = str(cols[0]["thingIdNumber"]), str(cols[1]["thingIdNumber"])
call("jawa/social_cancel", action="remove", all=True)
m = call("jawa/social_marry", pawn=A, otherPawn=B, ceremony=True)
print("   ceremonyStarted:", m.get("ceremonyStarted"), " lords:", m.get("lords"))
for n in (m.get("notes") or []): print("      ", n[:140])
print("   relations:", [(x["def"], x["with"]) for x in (m.get("relations") or [])])

print("\n== 5. MARRIAGE — instant, no party ==")
call("jawa/social_cancel", action="remove", all=True)
C = str(cols[2]["thingIdNumber"]); D = str(cols[3]["thingIdNumber"]) if len(cols) > 3 else B
mi = call("jawa/social_marry", pawn=C, otherPawn=D, ceremony=False)
print("   married:", mi.get("married"))
for n in (mi.get("notes") or []): print("      ", n[:130])

print("\n== 6. FUNERAL — the ritual path ==")
f = call("jawa/ritual_start", ritual="Funeral")
print("   ok:", f.get("success"), " started:", f.get("started"), " participants:", f.get("participants"))
print("   ", (f.get("message") or f.get("note") or "")[:190])

print("\n== 7. A RITUAL THAT SHOULD RUN ==")
for cand in ("Festival", "Classic_DrumParty", "Classic_DanceParty", "LeaderSpeech"):
    r = call("jawa/ritual_start", ritual=cand)
    print("   %-20s ok=%-5s started=%-5s participants=%-4s %s" % (
        cand, r.get("success"), r.get("started"), r.get("participants"), (r.get("message") or "")[:80]))
    if r.get("started"): break

print("\n== 8. THE ESCAPE HATCH ==")
c = call("jawa/social_cancel", action="list")
print("   lords on map:", c.get("lordsBefore"))
for x in (c.get("lords") or [])[:6]: print("      ", x)
c2 = call("jawa/social_cancel", action="remove", all=True)
print("   removed:", c2.get("removed"), " lords now:", c2.get("lordsAfter"))
