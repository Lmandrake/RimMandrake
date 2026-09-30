"""DEEPFIRE_FIRSTCOAT_BONUS_1 -- spec §10 step 7 quicktest, driven over the bridge.

Run under WINDOWS python.exe from the repo root (the bridge binds Windows loopback):
    python.exe src\\RimMandrake\\bridgetools\\prove_deepfire_firstcoat.py [--start] [--x 60 --z 60]

--start   start a fresh dev quicktest first (rimworld/start_debug_game_ready); omit to use
          the map already loaded.
--x/--z   the cell to spawn/coat/report at.

What it does (every step goes through the mod's own "Deepfire" dev actions -- 1.6 flattens
mod categories, so they appear directly under Actions as "T: FirstCoat: ..." rather than
inside a "Deepfire" child node; find_actions() below reads the leaf paths from the live
Actions tree rather than constructing them, exactly like prove_deepfire_floor.py). Coat/
remove go straight through CompDeepfire.AddCoat()/RemoveAllCoats() -- the same entry points
the real WorkGiver/JobDriver path ends in -- so the Harmony-free C# this item adds
(DeepfireFirstCoatBonus, RM_StatPart_Deepfire) is what is actually being exercised.

  0  spawn a Normal-quality SculptureSmall (CompArt+CompQuality -- unambiguously an "art
     item" per spec §3.5 bullet 1) -> baseline report: coats 0, bonusApplied false,
     quality Normal.
  1  "FirstCoat: coat thing"        -> coats 1, bonusApplied true, quality Good (Normal + 1
                                        quality step).
  2  "FirstCoat: coat thing" again  -> coats 2, quality UNCHANGED at Good (later coats never
                                        touch the bonus).
  3  destroy it; spawn a Legendary-quality SculptureSmall; coat once -> quality stays
     Legendary (capped, enum max), coat is still charged (coats -> 1).
  4  destroy it; spawn a Wall (paintable, CompColorable, no CompArt -- the spec's own
     "everything else" worked example, "a wall (beauty 0) gets +3") -> baseline report:
     coats 0, beauty == the wall's plain stat value (no Deepfire bonus yet).
  5  "FirstCoat: coat thing"        -> coats 1, beauty risen by EXACTLY
     beautyFlat*sizeFactor + beautyPct*baseBeauty (sizeFactor = min(area,4) = 1 for a 1x1
     wall segment, baseBeauty = the step-4 beauty reading, since a wall carries no quality
     stat part to fold in first) -- i.e. +3 + 0.25*baseBeauty (defaults flat=3, pct=0.25).
  6  "FirstCoat: remove coats"      -> coats 0, beauty back to the step-4 baseline (the
     StatPart is stateless: no coats means no bonus, nothing to "un-bump").
  7  "FirstCoat: coat thing" again  -> coats 1, beauty rises by the SAME amount as step 5,
     not double -- proves "remove + reapply does not re-bump" for the Beauty path too.
  8  no new errors in the log naming LuminousPigment/Deepfire/FirstCoat.

Exit 0 = every assertion passed, 1 = at least one failed, 2 = could not run.
"""
import argparse
import json
import sys
import time

sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb

TAG = "[DeepfireFirstCoat] "
CATEGORY = "Deepfire"

ap = argparse.ArgumentParser()
ap.add_argument("--start", action="store_true")
ap.add_argument("--x", type=int, default=61)
ap.add_argument("--z", type=int, default=61)
args = ap.parse_args()
X, Z = args.x, args.z

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


def near(a, b, tol=0.02):
    return a is not None and b is not None and abs(a - b) <= tol


# ---- debug-action discovery: read the leaf paths, never construct them ----
def find_actions():
    r = call("rimworld/list_debug_action_children", path="Actions")
    if not r.get("success", True) and not r.get("children"):
        raise SystemExit("debug tree will not enumerate: %s" % json.dumps(r)[:300])
    for c in r.get("children") or []:
        label = c.get("label") or ""
        if label == CATEGORY or (c.get("path") or "").endswith("\\" + CATEGORY):
            sub = call("rimworld/list_debug_action_children", path=c.get("path"))
            return {(leaf.get("label") or ""): leaf.get("path") for leaf in sub.get("children") or []}
    # 1.6 flattens mod categories: the actions sit directly under Actions as "T: FirstCoat: ..."
    return {(c.get("label") or ""): c.get("path") for c in r.get("children") or []
            if "FirstCoat:" in (c.get("label") or c.get("path") or "")}


def run(actions, label_part, tag=TAG):
    path = next((p for l, p in actions.items() if label_part.lower() in l.lower()), None)
    if not path:
        raise SystemExit("no FirstCoat debug action matching %r (have: %s)" % (label_part, list(actions)))
    r = call("rimworld/execute_debug_action", path=path, x=X, z=Z)
    logs = [str(x.get("message") if isinstance(x, dict) else x)
            for x in ((r.get("effects") or {}).get("logs") or [])]
    for line in logs:
        i = line.find(tag)
        if i >= 0:
            try:
                return json.loads(line[i + len(tag):].strip())
            except Exception:
                pass
    print("    (no %s line; raw result: %s)" % (tag.strip(), json.dumps(r)[:400]))
    return None


# ---- 0. game ----
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

call("jawa/drain_log", errorsOnly=True)  # discard errors that predate this proof

actions = find_actions()
print("FirstCoat dev actions:", sorted(actions))
if not actions:
    print("no 'FirstCoat' actions under Actions -- is LuminousPigment (this build) loaded?")
    sys.exit(2)

print("== 0 spawn Normal-quality sculpture ==")
a0 = run(actions, "spawn art normal")
check("spawn: art, Normal quality, 0 coats, bonus not applied",
      a0 and a0.get("isArt") and a0.get("quality") == "Normal" and a0.get("coats") == 0 and not a0.get("bonusApplied"),
      json.dumps(a0))

print("== 1 first coat ==")
a1 = run(actions, "coat thing")
check("coat 1: coats=1, bonusApplied=true, quality Good",
      a1 and a1.get("coats") == 1 and a1.get("bonusApplied") is True and a1.get("quality") == "Good",
      json.dumps(a1))

print("== 2 second coat (bonus must not re-fire) ==")
a2 = run(actions, "coat thing")
check("coat 2: coats=2, quality UNCHANGED at Good",
      a2 and a2.get("coats") == 2 and a2.get("quality") == "Good",
      json.dumps(a2))

print("== 3 Legendary caps, coat still charged ==")
run(actions, "destroy thing")
a3s = run(actions, "spawn art legendary")
check("spawn: art, Legendary quality", a3s and a3s.get("quality") == "Legendary", json.dumps(a3s))
a3 = run(actions, "coat thing")
check("coat: Legendary stays Legendary, coats=1 (still charged)",
      a3 and a3.get("quality") == "Legendary" and a3.get("coats") == 1,
      json.dumps(a3))
run(actions, "destroy thing")

print("== 4 wall baseline (everything-else / Beauty StatPart path) ==")
r0 = run(actions, "spawn wall")
check("spawn: wall, not art, 0 coats", r0 and not r0.get("isArt") and r0.get("coats") == 0, json.dumps(r0))
base_beauty = r0["beauty"]

print("== 5 coat the wall ==")
r1 = run(actions, "coat thing")
size_factor = 1  # a Wall segment is 1x1: min(area,4) = 1
expected_bonus = 3.0 * size_factor + 0.25 * base_beauty  # DeepfirePaintDefaults.FirstCoatBeautyFlat/Pct
check("coat: coats=1, Beauty rises by flat*sizeFactor + pct*baseBeauty",
      r1["coats"] == 1 and near(r1["beauty"] - base_beauty, expected_bonus),
      "%.4f -> %.4f (rise %.4f, expected %.4f)" % (base_beauty, r1["beauty"], r1["beauty"] - base_beauty, expected_bonus))

print("== 6 strip coats: bonus disappears, no permanent mark ==")
r2 = run(actions, "remove coats")
check("strip: coats=0, Beauty back to baseline", r2["coats"] == 0 and near(r2["beauty"], base_beauty),
      "%.4f vs baseline %.4f" % (r2["beauty"], base_beauty))

print("== 7 reapply: same rise, not double (remove + reapply does not re-bump) ==")
r3 = run(actions, "coat thing")
check("reapply: coats=1, Beauty rise matches step 5 exactly (no double-count)",
      r3["coats"] == 1 and near(r3["beauty"], r1["beauty"]),
      "%.4f vs step-5 %.4f" % (r3["beauty"], r1["beauty"]))
run(actions, "destroy thing")

print("== 8 log ==")
logs = call("jawa/drain_log", errorsOnly=True)
text = json.dumps(logs)
bad = [k for k in ("LuminousPigment", "Deepfire", "FirstCoat") if k in text]
check("no LuminousPigment/Deepfire/FirstCoat errors logged during the proof", not bad, text[:600] if bad else "")

failed = [n for n, ok in results if not ok]
print("\n%d/%d passed" % (len(results) - len(failed), len(results)))
for n in failed:
    print("  FAILED:", n)
sys.exit(0 if not failed else 1)
