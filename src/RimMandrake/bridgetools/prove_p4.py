"""P4: psylink (incl. the 0->N quirk), pregnancy, mental states, romance."""
import sys, json, time
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
ps = [p for p in call("jawa/pawn_get", limit=12)["pawns"] if p.get("faction") == "PlayerColony"]
A, B = str(ps[0]["thingIdNumber"]), str(ps[1]["thingIdNumber"])
print("pawns:", ps[0]["name"], "|", ps[1]["name"], " (%d colonists)" % len(ps))

print("\n== A. PSYLINK — the 0->N quirk ==")
g = call("jawa/pawn_psychic", pawn=A, action="get")
print("   royalty:", g.get("royaltyActive"), " psylink now:", g.get("psylinkLevel"))
r = call("jawa/pawn_psychic", pawn=A, action="psylink", level=4)
print("   ask for level 4 -> psylinkLevel:", r.get("psylinkLevel"))
for n in (r.get("notes") or []): print("      ", n)
r2 = call("jawa/pawn_psychic", pawn=A, action="psylink", level=6)
print("   ask for 6 -> ", r2.get("psylinkLevel"))
r3 = call("jawa/pawn_psychic", pawn=A, action="grant", ability="Skip")
if not r3.get("success"): r3 = call("jawa/pawn_psychic", pawn=A, action="grant", ability="PsychicBlinding")
print("   grant -> ok:", r3.get("success"), (r3.get("message") or "")[:60])
for n in (r3.get("notes") or []): print("      ", n)
pc = [a for a in (r3.get("abilities") or []) if a["isPsycast"]]
print("   psycasts on pawn:", [a["def"] for a in pc][:6])
r4 = call("jawa/pawn_psychic", pawn=A, action="psyfocus", psyfocus=1.0, clearEntropy=True)
print("   psyfocus:", r4.get("psyfocus"), " entropy:", r4.get("entropy"), "/", r4.get("maxEntropy"))

print("\n== B. PREGNANCY ==")
females = [p for p in ps if p.get("gender") == "Female"]
males = [p for p in ps if p.get("gender") == "Male"]
if females and males:
    M, F = str(males[0]["thingIdNumber"]), str(females[0]["thingIdNumber"])
    print("   mother:", females[0]["name"], " father:", males[0]["name"])
    s1 = call("jawa/pawn_pregnancy", pawn=F, action="start", father=M)
    print("   start -> ok:", s1.get("success"), (s1.get("message") or "")[:110])
    for n in (s1.get("notes") or []): print("      ", n)
    print("   pregnant:", s1.get("pregnant"), " gestation:", s1.get("gestation"), " father:", s1.get("father"))
    s2 = call("jawa/pawn_pregnancy", pawn=F, action="progress", progress=0.75)
    print("   progress 0.75 -> gestation:", s2.get("gestation"))
    for n in (s2.get("notes") or []): print("      ", n)
    s3 = call("jawa/pawn_pregnancy", pawn=F, action="end", quiet=True)
    print("   end -> pregnant:", s3.get("pregnant"), (s3.get("notes") or [""])[0][:70])
else:
    print("   need one male and one female colonist; have M=%d F=%d" % (len(males), len(females)))

print("\n== C. MENTAL STATES ==")
l = call("jawa/pawn_mental", pawn=A, action="list", limit=200)
never = [d["def"] for d in (l.get("states") or []) if d["neverRecoversAlone"]]
print("   total MentalStateDefs:", l.get("totalDefs"), " never recover alone:", never)
m1 = call("jawa/pawn_mental", pawn=A, action="start", state="Berserk")
print("   start Berserk -> started:", m1.get("started"), " current:", m1.get("currentState"))
for n in (m1.get("notes") or []): print("      ", n)
m2 = call("jawa/pawn_mental", pawn=A, action="start", state="Berserk")
print("   start AGAIN  -> started:", m2.get("started"), "(expect False - already in it)")
for n in (m2.get("notes") or []): print("      ", n[:110])
m3 = call("jawa/pawn_mental", pawn=A, action="end")
print("   end -> current:", m3.get("currentState"))

print("\n== D. ROMANCE — full transactions ==")
r1 = call("jawa/pawn_romance", pawn=A, action="romance", otherPawn=B)
print("   romance -> opinion %s/%s" % (r1.get("opinionAtoB"), r1.get("opinionBtoA")))
for n in (r1.get("notes") or []): print("      ", n[:100])
r2 = call("jawa/pawn_romance", pawn=A, action="marry", otherPawn=B)
print("   marry -> ok:", r2.get("success"), " opinion %s/%s" % (r2.get("opinionAtoB"), r2.get("opinionBtoA")))
for n in (r2.get("notes") or []): print("      ", n[:130])
print("   relations:", [(x["def"], x["with"]) for x in (r2.get("relations") or [])])
r3 = call("jawa/pawn_romance", pawn=A, action="breakup", otherPawn=B)
print("   breakup -> opinion %s/%s" % (r3.get("opinionAtoB"), r3.get("opinionBtoA")))
for n in (r3.get("notes") or []): print("      ", n[:110])
print("   relations:", [(x["def"], x["with"]) for x in (r3.get("relations") or [])])
