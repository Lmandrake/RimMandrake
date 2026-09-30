"""DEEPFIRE_STATUS_THOUGHTS_1 -- spec §10 step 9 quicktest, driven over the bridge. NOT YET RUN.

Run under WINDOWS python.exe from the repo root (the bridge binds Windows loopback):
    python.exe src\\RimMandrake\\bridgetools\\prove_deepfire_status_thoughts.py [--start] [--x 60 --z 60]

--start   start a fresh dev quicktest first (rimworld/start_debug_game_ready).
--x/--z   SOUTH-WEST corner of the bedroom's 6x6 interior. The public room is built 12 cells
          east of it, the test pawns stand 6 cells south.

Spec row 9: "quicktest with Royalty: titled pawn wearing 2 coats shows RM_WearingDeepfire
stage 1; a commoner with 2 coats -> titled pawn's opinion -15 and the -3 mood". "Stage 1"
there is the FIRST stage (score bucket 1-2, +3), i.e. StageIndex 0. The row's "no DLC -> only
the wearer's thought" bar is NOT proven here: every DLC is a hard prerequisite (owner,
2026-09-26), so there is no DLC-absent configuration to test.

  1  a titled (Empire Knight) and a commoner colonist; neither shows any Deepfire thought.
  2  the titled pawn puts on a 2-coat parka -> displayScore 2, RM_WearingDeepfireTitled at
     StageIndex 0 with live mood +3; the commoner-reaction thoughts stay off.
  3  the commoner puts on a 2-coat parka -> the titled pawn holds RM_WearsAboveStation
     toward it (opinion -15 in the live social thoughts) and RM_SawCommonerInDeepfire
     (mood -3); the commoner gets its own RM_WearingDeepfireCommon (+1) and nothing else.
  4  bedroom: a bed claimed by the titled pawn in an 8x8 room -> no RM_DeepfireBedroom;
     36 coated floor cells -> room score 3 -> stage 0 (+4); two 3-coat sculptures -> score 9
     -> stage 1 (+6).
  5  RM_ImpressedByDeepfire: a public room (36 coated cells + two 3-coat sculptures, score 9)
     and a titled visitor of a non-hostile faction -> goodwill +2 on the first check, +0 on
     the second (cap once per faction per quadrum).
  6  no new errors naming LuminousPigment/Deepfire.
Exit 0 = every assertion passed, 1 = at least one failed, 2 = could not run.
"""
import argparse
import json
import sys
import time

sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
import deepfire_log_check

TAGS = ("[DeepfireStatus] ", "[DeepfireFloor] ")
CATEGORY = "Deepfire"
PREFIXES = ("Status:", "Floor:")
PUBLIC_ROOM_DX = 12
PAWN_DZ = -6
GOODWILL_PER_VISIT = 2

ap = argparse.ArgumentParser()
ap.add_argument("--start", action="store_true")
ap.add_argument("--x", type=int, default=60)
ap.add_argument("--z", type=int, default=60)
args = ap.parse_args()
X, Z = args.x, args.z
PX = X + PUBLIC_ROOM_DX

host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
S.connect()


def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r


results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", name, detail))


def near(a, b, tol=0.01):
    return a is not None and b is not None and abs(a - b) <= tol


def find_actions():
    r = call("rimworld/list_debug_action_children", path="Actions")
    if not r.get("success", True) and not r.get("children"):
        raise SystemExit("debug tree will not enumerate: %s" % json.dumps(r)[:300])
    for c in r.get("children") or []:
        label = c.get("label") or ""
        if label == CATEGORY or (c.get("path") or "").endswith("\\" + CATEGORY):
            sub = call("rimworld/list_debug_action_children", path=c.get("path"))
            return {(leaf.get("label") or ""): leaf.get("path") for leaf in sub.get("children") or []}
    # 1.6 flattens mod categories: the actions sit directly under Actions as "T: Status: ..."
    return {(c.get("label") or ""): c.get("path") for c in r.get("children") or []
            if any(p in (c.get("label") or c.get("path") or "") for p in PREFIXES)}


def run(actions, label_part, x, z):
    path = next((p for l, p in actions.items() if label_part.lower() in l.lower()), None)
    if not path:
        raise SystemExit("no Deepfire debug action matching %r (have: %s)" % (label_part, list(actions)))
    r = call("rimworld/execute_debug_action", path=path, x=x, z=z)
    logs = [str(v.get("message") if isinstance(v, dict) else v)
            for v in ((r.get("effects") or {}).get("logs") or [])]
    for line in logs:
        for tag in TAGS:
            i = line.find(tag)
            if i >= 0:
                try:
                    return json.loads(line[i + len(tag):].strip())
                except Exception:
                    pass
    print("    (no tagged line; raw result: %s)" % json.dumps(r)[:400])
    return None


def report(actions, label):
    rep = run(actions, "Status: report pair", X, Z)
    print("  [%s] %s" % (label, json.dumps(rep)[:1200]))
    if not rep or not rep.get("found"):
        raise SystemExit("pair report returned nothing parseable")
    return rep


def thought(p, name):
    return p.get(name) or {}


# ---- setup ----
if args.start:
    r = call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
    print("start_debug_game_ready:", json.dumps(r)[:300])
st = {}
for _ in range(90):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing":
        break
    time.sleep(1)
if st.get("programState") != "Playing":
    print("not Playing:", st.get("programState"))
    sys.exit(2)

LOG_BASE = deepfire_log_check.baseline(call)  # errors already in the buffer do not count

for (rx, label) in ((X, "bedroom"), (PX, "public room")):
    room = call("jawa/make_empty_room", rect="%d,%d,8,8" % (rx - 1, Z - 1),
                wallDef="Wall", stuffDef="WoodLog", floorDef="WoodPlankFloor")
    print("make_empty_room (%s):" % label, json.dumps(room)[:300])
    if not room.get("success"):
        sys.exit(2)

actions = find_actions()
print("Deepfire dev actions:", sorted(actions))
if not actions:
    print("no Deepfire dev actions under Actions -- is LuminousPigment (this build) loaded?")
    sys.exit(2)

# ---- 1 pair ----
print("== 1 titled + commoner ==")
a1 = run(actions, "spawn titled + commoner", X, Z + PAWN_DZ)
check("pair: Empire title set, titled is titled, commoner is not",
      a1 and a1.get("titleSet") and a1.get("titledIsTitled") and not a1.get("commonerIsTitled"), json.dumps(a1))
r1 = report(actions, "undressed")
t, c = r1["titled"], r1["commoner"]
check("undressed: no Deepfire thought on either pawn",
      not any(thought(p, d).get("active") for p in (t, c) for d in
              ("RM_WearingDeepfireTitled", "RM_WearingDeepfireCommon", "RM_SawCommonerInDeepfire", "RM_DeepfireBedroom"))
      and not r1["aboveStationActive"])

# ---- 2 titled wears 2 coats ----
print("== 2 titled in 2 coats ==")
a2 = run(actions, "dress titled in 2 coats", X, Z)
check("titled: parka at 2 coats, display score 2", a2 and a2.get("coats") == 2 and a2.get("displayScore") == 2, json.dumps(a2))
r2 = report(actions, "titled dressed")
wt = thought(r2["titled"], "RM_WearingDeepfireTitled")
check("titled: RM_WearingDeepfireTitled at its first stage (+3)",
      wt.get("active") and wt.get("stage") == 0 and near(wt.get("liveMood"), 3.0), json.dumps(wt))
check("titled: not RM_WearingDeepfireCommon", not thought(r2["titled"], "RM_WearingDeepfireCommon").get("active"))
check("titled alone: no commoner reaction yet",
      not thought(r2["titled"], "RM_SawCommonerInDeepfire").get("active") and not r2["aboveStationActive"])

# ---- 3 commoner wears 2 coats ----
print("== 3 commoner in 2 coats ==")
a3 = run(actions, "dress commoner in 2 coats", X, Z)
check("commoner: display score 2", a3 and a3.get("displayScore") == 2, json.dumps(a3))
r3 = report(actions, "commoner dressed")
social = {s["def"]: s["opinion"] for s in r3.get("titledSocialThoughtsOfCommoner") or []}
check("titled -> commoner: RM_WearsAboveStation active", r3["aboveStationActive"])
check("titled -> commoner: live opinion offset -15", near(social.get("RM_WearsAboveStation"), -15.0), json.dumps(social))
saw = thought(r3["titled"], "RM_SawCommonerInDeepfire")
check("titled: RM_SawCommonerInDeepfire mood -3", saw.get("active") and near(saw.get("liveMood"), -3.0), json.dumps(saw))
wc = thought(r3["commoner"], "RM_WearingDeepfireCommon")
check("commoner: own RM_WearingDeepfireCommon (+1)", wc.get("active") and wc.get("stage") == 0 and near(wc.get("liveMood"), 1.0),
      json.dumps(wc))
check("commoner: feels no offence and no titled thought",
      not thought(r3["commoner"], "RM_SawCommonerInDeepfire").get("active")
      and not thought(r3["commoner"], "RM_WearingDeepfireTitled").get("active"))

# ---- 4 bedroom ----
print("== 4 bedroom ==")
b = run(actions, "bed for titled at cell", X + 1, Z + 1)
check("bedroom: bed claimed, room is the titled pawn's Bedroom",
      b and b.get("claimed") and b.get("ownedRoom") and b.get("role") == "Bedroom", json.dumps(b))
rs0 = run(actions, "room score at cell", X + 3, Z + 3)
r4a = report(actions, "bed, no deepfire")
check("bedroom: score 0 -> no RM_DeepfireBedroom",
      rs0 and rs0.get("score") == 0 and not thought(r4a["titled"], "RM_DeepfireBedroom").get("active"), json.dumps(rs0))
fc = run(actions, "Floor: coat 6x6", X, Z)
check("bedroom: 36 floor cells coated", fc and fc.get("added") == 36, json.dumps(fc))
rs1 = run(actions, "room score at cell", X + 3, Z + 3)
check("bedroom: 36 coated cells -> room score 3", rs1 and rs1.get("score") == 3, json.dumps(rs1))
r4b = report(actions, "bed + floor")
bd = thought(r4b["titled"], "RM_DeepfireBedroom")
check("bedroom: RM_DeepfireBedroom stage 0 (+4)", bd.get("active") and bd.get("stage") == 0 and near(bd.get("liveMood"), 4.0),
      json.dumps(bd))
s1 = run(actions, "coated sculpture at cell", X + 4, Z + 4)
s2 = run(actions, "coated sculpture at cell", X + 4, Z + 1)
check("bedroom: two 3-coat sculptures -> room score 9", s2 and s2.get("roomScore") == 9 and s1 and s1.get("coats") == 3,
      "%s / %s" % (json.dumps(s1), json.dumps(s2)))
run(actions, "room score at cell", X + 3, Z + 3)  # invalidates the score cache
r4c = report(actions, "bed + floor + sculptures")
bd2 = thought(r4c["titled"], "RM_DeepfireBedroom")
check("bedroom: RM_DeepfireBedroom stage 1 (+6)", bd2.get("active") and bd2.get("stage") == 1 and near(bd2.get("liveMood"), 6.0),
      json.dumps(bd2))
check("bedroom: the commoner (no bed there) gets no RM_DeepfireBedroom",
      not thought(r4c["commoner"], "RM_DeepfireBedroom").get("active"))

# ---- 5 impressed visitor ----
print("== 5 impressed visitor ==")
run(actions, "Floor: coat 6x6", PX, Z)
run(actions, "coated sculpture at cell", PX + 4, Z + 4)
run(actions, "coated sculpture at cell", PX + 4, Z + 1)
pr = run(actions, "room score at cell", PX + 3, Z + 3)
check("public room: score 9 and public", pr and pr.get("score") == 9 and pr.get("public"), json.dumps(pr))
im = run(actions, "visitor impress test", PX + 3, Z + PAWN_DZ)
check("visitor: a non-hostile faction was found and its pawn is an impressible titled visitor",
      im and im.get("faction") and im.get("visitorImpressible"), json.dumps(im))
if im and im.get("faction"):
    check("visitor: best public room score >= 8", im.get("bestPublicRoomScore", 0) >= 8)
    check("visitor: first check raises goodwill by +2",
          im.get("impressed1") == 1 and im.get("goodwill1") - im.get("goodwill0") == GOODWILL_PER_VISIT,
          "%s -> %s" % (im.get("goodwill0"), im.get("goodwill1")))
    check("visitor: second check in the same quadrum does nothing",
          im.get("impressed2") == 0 and im.get("goodwill2") == im.get("goodwill1"))

run(actions, "cleanup test pawns", X, Z)

print("== 6 log ==")
new_errors = deepfire_log_check.new_mod_errors(call, LOG_BASE)
check("no LuminousPigment/Deepfire Error-type lines logged (new) during the proof", not new_errors, json.dumps(new_errors[:5]))

failed = [n for n, ok in results if not ok]
print("\n%d/%d passed" % (len(results) - len(failed), len(results)))
for n in failed:
    print("  FAILED:", n)
sys.exit(0 if not failed else 1)
