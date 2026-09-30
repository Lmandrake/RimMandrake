"""DEEPFIRE_WORN_GLOW_1 -- spec §10 step 8 quicktest, driven over the bridge.

Run under WINDOWS python.exe from the repo root (the bridge binds Windows loopback):
    python.exe src\\RimMandrake\\bridgetools\\prove_deepfire_worn_glow.py [--start] [--x 40 --z 60]

--start   start a fresh dev quicktest first (rimworld/start_debug_game_ready); omit to use
          the map already loaded.
--x/--z   west end of the 30-cell walk. The hit-report pairs run at (x+15, z+15) and the
          styling test at (x+15, z-15); keep all three on open, walkable ground.

Every step goes through the mod's own "WornGlow:" dev actions (1.6 flattens mod categories,
so they sit directly under Actions as "T: WornGlow: ..."; find_actions() reads the leaf
paths from the live tree, exactly like prove_deepfire_floor.py). Coats go through
CompDeepfire.AddCoat and wearing through Pawn_ApparelTracker.Wear (the real
Notify_Equipped path); the combat numbers are ShotReport.HitReportFor and the
MeleeDodgeChance stat called directly -- no live shooting (spawn-many-for-bridge-tests).

"At night on an unlit map" is realised by ROOFING the test area: GroundGlowAt ignores sky
on a roofed cell, so the only light there is ours whatever the hour, and the darkness test
takes its indoor branch. (The outdoor branch -- sky glow <= 0.35 -- is not exercised here.)

  0  roof a 36x7 strip -> baseline GroundGlowAt at the walk start < 0.3 (dark).
  1  spawn a colonist in a 3-coat cloth parka -> tracked, one worn light, proxy on its cell,
     GroundGlowAt(pawn) > 0.3, glowingInDark true.
  2  order it 30 cells east; step to the next 15-tick poll, then every 15 ticks until it
     arrives: at EVERY sample the proxy sits on the pawn's cell and GroundGlowAt(pawn) > 0.3.
     It must actually travel (>= 25 cells covered, proxy seen at >= 5 distinct cells).
  3  strip its coats -> untracked, no worn light, glow at its cell back under 0.3.
  4  20 fresh coated/uncoated baseliner-adult pairs, symmetric about one rifle shooter under
     a roof: every pair -> coated twin glowingInDark, its AimOnTargetChance per unit of its
     own clamped body size > the plain twin's, its hit readout carries the "Glowing in the
     dark" line, its stat explanation names the line, and its MeleeDodgeChance while coated
     is lower than the SAME pawn's own MeleeDodgeChance once its coat is stripped (or both
     are 0 -- the dodge curve floors low-skill pawns). DEEPFIRE_DODGE_PROOF_TWINS_1: the
     dodge compare used to read the coated twin against the plain twin, which isn't
     skill-matched -- fixed to compare one pawn against itself before/after RemoveAllCoats.
  5  styling station + 3 deepfire + an uncoated colonist -> the lacquer job is queued via
     the dialog's own Accept entry point; step ticks until done -> parka coats 1 and the
     3 deepfire are consumed.
  6  cleanup; no NEW Error-type log line naming this mod (deepfire_log_check.py).
Exit 0 = every assertion passed, 1 = at least one failed, 2 = could not run.
"""
import argparse
import json
import sys
import time

sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
import deepfire_log_check

TAG = "[DeepfireWorn] "
CATEGORY = "Deepfire"
LABEL = "WornGlow:"
POLL = 15            # DeepfirePaintDefaults.WornLightTickInterval
LIT = 0.3            # GlowGrid.GameGlowLitThreshold
WALK = 30
PAIRS = 20
STYLE_COST = 3       # DeepfireCostUtility.CostFor(apparel)

ap = argparse.ArgumentParser()
ap.add_argument("--start", action="store_true")
ap.add_argument("--x", type=int, default=40)
ap.add_argument("--z", type=int, default=60)
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


def find_actions():
    r = call("rimworld/list_debug_action_children", path="Actions")
    if not r.get("success", True) and not r.get("children"):
        raise SystemExit("debug tree will not enumerate: %s" % json.dumps(r)[:300])
    for c in r.get("children") or []:
        label = c.get("label") or ""
        if label == CATEGORY or (c.get("path") or "").endswith("\\" + CATEGORY):
            sub = call("rimworld/list_debug_action_children", path=c.get("path"))
            return {(leaf.get("label") or ""): leaf.get("path") for leaf in sub.get("children") or []}
    return {(c.get("label") or ""): c.get("path") for c in r.get("children") or []
            if LABEL in (c.get("label") or c.get("path") or "")}


def run(actions, label_part, x=None, z=None):
    path = next((p for l, p in actions.items() if label_part.lower() in l.lower()), None)
    if not path:
        raise SystemExit("no WornGlow debug action matching %r (have: %s)" % (label_part, list(actions)))
    r = call("rimworld/execute_debug_action", path=path, x=X if x is None else x, z=Z if z is None else z)
    logs = [str(x.get("message") if isinstance(x, dict) else x)
            for x in ((r.get("effects") or {}).get("logs") or [])]
    for line in logs:
        i = line.find(TAG)
        if i >= 0:
            try:
                return json.loads(line[i + len(TAG):].strip())
            except Exception:
                pass
    print("    (no %s line; raw result: %s)" % (TAG.strip(), json.dumps(r)[:400]))
    return None


def step(n):
    if n > 0:
        call("rimworld/step_game_ticks", ticks=n)


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

LOG_BASE = deepfire_log_check.baseline(call)  # errors already in the buffer do not count

actions = find_actions()
print("WornGlow dev actions:", sorted(actions))
if not actions:
    print("no 'WornGlow' actions under Actions -- is LuminousPigment (this build) loaded?")
    sys.exit(2)

print("== 0 roofed dark strip ==")
r0 = run(actions, "roof dark strip")
check("baseline: walk start is dark (< 0.3) under the roof", r0 and r0.get("baselineGlow", 1) < LIT, json.dumps(r0))

print("== 1 coated walker ==")
w0 = run(actions, "spawn coated walker")
w1 = run(actions, "report walker")
check("walker: coats 3, tracked, proxy on its cell, glow > 0.3, glowing in the dark",
      w1 and w1.get("coats") == 3 and w1.get("tracked") and (w1.get("proxyX"), w1.get("proxyZ")) == (w1.get("x"), w1.get("z"))
      and w1.get("groundGlow", 0) > LIT and w1.get("glowingInDark"),
      json.dumps(w1))

print("== 2 walk 30 cells, sample every 15 ticks on the poll tick ==")
wk = run(actions, "walk 30 east")
check("walk ordered", wk and wk.get("ordered"), json.dumps(wk))
dest = (wk or {}).get("destX"), (wk or {}).get("destZ")
start_x = (w1 or {}).get("x")
cur = run(actions, "report walker")
step((POLL - (cur or {}).get("ticks", 0) % POLL) % POLL or POLL)  # land on a poll tick
samples, bad = [], []
for _ in range(80):
    s = run(actions, "report walker")
    if not s:
        break
    samples.append(s)
    on_proxy = (s.get("proxyX"), s.get("proxyZ")) == (s.get("x"), s.get("z"))
    if not (s.get("tracked") and on_proxy and s.get("roofed") and s.get("groundGlow", 0) > LIT):
        bad.append(s)
    if (s.get("x"), s.get("z")) == dest and s.get("job") != "Goto":
        break
    step(POLL)
travelled = (samples[-1].get("x", 0) - start_x) if samples and start_x is not None else 0
# DEEPFIRE_LIVE_FAILURES_1: the old ">= 10 samples" bar assumed ~13 ticks/cell (26 polls for
# 30 cells). Live 2026-09-30 the walker covered all 30 cells in 7 polls with every sample on its
# proxy, so the bar failed a correct light. The count of polls depends on walk speed; what the proof
# needs is that the light was seen FOLLOWING the pawn, i.e. at several distinct cells along the walk.
distinct = len({(s.get("x"), s.get("z")) for s in samples})
check("walk: >= 25 cells travelled, proxy sampled at >= 5 distinct cells along the way",
      travelled >= 25 and distinct >= 5,
      "%d samples at %d distinct cells, %s cells travelled, moveSpeed %s, ticks %s"
      % (len(samples), distinct, travelled, (samples[0].get("moveSpeed") if samples else None),
         [(s.get("ticks"), s.get("x")) for s in samples][:12]))
check("walk: proxy on the pawn's cell, cell roofed (no sky), GroundGlowAt > 0.3 at EVERY sample", samples and not bad,
      "%d bad: %s" % (len(bad), json.dumps(bad[:3])))

print("== 3 strip coats ==")
s3 = run(actions, "strip walker")
check("strip: untracked, glow < 0.3, not glowing in the dark",
      s3 and not s3.get("tracked") and s3.get("groundGlow", 1) < LIT and not s3.get("glowingInDark"),
      json.dumps(s3))

print("== 4 %d hit-report pairs ==" % PAIRS)
h = run(actions, "hit-report pairs", x=X + 15, z=Z + 15)
if h:
    print("    first rows:", json.dumps(h.get("rows", [])[:3]))
check("pairs: coated twin glowing in the dark in all %d" % PAIRS, h and h.get("darkCount") == PAIRS, json.dumps({k: v for k, v in (h or {}).items() if k != "rows"}))
check("pairs: coated AimOnTargetChance > plain twin's (per unit body size) in all %d" % PAIRS,
      h and h.get("coatedHigher") == PAIRS,
      json.dumps([r for r in (h or {}).get("rows", [])
                  if r.get("coatedAim", 0) / max(r.get("coatedSize") or 1, 0.5)
                  <= r.get("plainAim", 0) / max(r.get("plainSize") or 1, 0.5)][:4]))
check("pairs: 'Glowing in the dark' line in the hit readout in all %d" % PAIRS, h and h.get("readoutLines") == PAIRS)
check("pairs: coated MeleeDodgeChance lower (or both floored at 0) in all %d" % PAIRS, h and h.get("dodgeLowerOrZero") == PAIRS)
check("pairs: dodge stat explanation names the line in all %d" % PAIRS, h and h.get("dodgeExplained") == PAIRS)

print("== 5 styling station lacquer ==")
y0 = run(actions, "styling lacquer setup", x=X + 15, z=Z - 15)
check("styling: lacquer job queued, parka 0 coats, %d deepfire on map" % STYLE_COST,
      y0 and y0.get("queued") and y0.get("coats") == 0 and y0.get("deepfireOnMap") == STYLE_COST, json.dumps(y0))
y = y0
for _ in range(40):
    step(250)
    y = run(actions, "report styler")
    if y and y.get("coats") == 1:
        break
check("styling: parka reads coats 1", y and y.get("coats") == 1, json.dumps(y))
check("styling: the %d deepfire were consumed" % STYLE_COST, y and y.get("deepfireOnMap") == 0, json.dumps(y))

print("== 6 cleanup + log ==")
run(actions, "cleanup test pawns")
new_errors = deepfire_log_check.new_mod_errors(call, LOG_BASE)
check("no LuminousPigment/Deepfire/WornGlow Error-type lines logged (new) during the proof", not new_errors, json.dumps(new_errors[:5]))

failed = [n for n, ok in results if not ok]
print("\n%d/%d passed" % (len(results) - len(failed), len(results)))
for n in failed:
    print("  FAILED:", n)
sys.exit(0 if not failed else 1)
