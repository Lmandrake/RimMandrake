"""P1 proof: name, title, backstory refresh, trait conflicts, skill read-back, appearance."""
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

lst = call("jawa/pawn_get", limit=5)
print("spawned pawns:", lst.get("count"))
target = None
for p in (lst.get("pawns") or []):
    if p.get("faction") == "PlayerColony": target = p; break
if target is None and lst.get("pawns"): target = lst["pawns"][0]
PID = str(target["thingIdNumber"])
print("target:", target["name"], PID, target.get("kindDef"))

print("\n== 1. DEEP READ ==")
g = call("jawa/pawn_get", pawn=PID)["pawns"][0]
print("   name:", g["name"], "| title:", g["title"], "| xenotype:", g["xenotype"])
print("   childhood:", g["childhood"], "| adulthood:", g["adulthood"])
print("   traits:", [t["def"] for t in g["traits"]])
sk = {s["skill"]: (s["levelRaw"], s["levelEffective"]) for s in g["skills"]}
print("   skills (raw,effective):", dict(list(sk.items())[:5]))

print("\n== 2. NAME + TITLE (title is the only free text a pawn has) ==")
n = call("jawa/set_pawn_identity", pawn=PID, first="Kel", nick="Rustjaw", last="Vex",
         title="keeper of the third crawler")
print("   changed:", n.get("changed"))
print("   before:", n.get("before"))
print("   after :", n.get("after"))

print("\n== 3. BACKSTORY + the four refreshes vanilla skips ==")
b = call("jawa/set_pawn_backstory", pawn=PID, childhood="ColonyScavenger")
if not b.get("success"):
    b = call("jawa/set_pawn_backstory", pawn=PID, childhood="Vatgrown")
print("   success:", b.get("success"), (b.get("message") or "")[:90])
print("   before:", b.get("before"), "-> after:", b.get("after"))
print("   refreshed:", b.get("refreshed"))
print("   disabledWorkTypes now:", b.get("disabledWorkTypes"))

print("\n== 4. TRAITS - conflict refusal is the point ==")
t1 = call("jawa/pawn_traits", pawn=PID, action="add", trait="Kind")
print("   add Kind      -> added:", t1.get("added"), "refused:", t1.get("refused"))
t2 = call("jawa/pawn_traits", pawn=PID, action="add", trait="Psychopath")
print("   add Psychopath-> added:", t2.get("added"))
print("     refused:", t2.get("refused"))
t3 = call("jawa/pawn_traits", pawn=PID, action="add", trait="Psychopath", force=True)
print("   force=True    -> added:", t3.get("added"), " traits now:", [x["def"] for x in t3.get("traits", [])])
t4 = call("jawa/pawn_traits", pawn=PID, action="remove", trait="Psychopath")
print("   remove        -> removed:", t4.get("removed"), " traits now:", [x["def"] for x in t4.get("traits", [])])
t5 = call("jawa/pawn_traits", pawn=PID, action="add", trait="Kind", degree=99)
print("   bad degree    -> success:", t5.get("success"), (t5.get("message") or "")[:80])

print("\n== 5. SKILL - levelRaw vs levelEffective ==")
s1 = call("jawa/set_pawn_skill", pawn=PID, skill="Shooting", level=14, passion="Major")
print("   success:", s1.get("success"), (s1.get("message") or "")[:80])
print("   before:", s1.get("before"))
print("   after :", s1.get("after"))
print("   wroteLevel:", s1.get("wroteLevel"), " readBackMatches(levelRaw):", s1.get("readBackMatches"))

print("\n== 6. APPEARANCE + renderer dirty ==")
a = call("jawa/set_pawn_appearance", pawn=PID, hairColor="0.9,0.1,0.1", skinColor="0.35,0.25,0.2")
print("   changed:", a.get("changed"), " rendererDirtied:", a.get("rendererDirtied"))

print("\n== 7. FINAL READ-BACK ==")
f = call("jawa/pawn_get", pawn=PID)["pawns"][0]
print("   name:", f["name"], "| title:", f["title"])
print("   childhood:", f["childhood"])
print("   traits:", [t["def"] for t in f["traits"]])
sh = [s for s in f["skills"] if s["skill"] == "Shooting"][0]
print("   Shooting raw=%s effective=%s passion=%s xp=%s" % (sh["levelRaw"], sh["levelEffective"], sh["passion"], sh["xpSinceLastLevel"]))
