"""DEEPFIRE_GOD_BRIDGE_DELTAS_1 -- spec §10 step 10 quicktest, driven over the bridge. NOT YET RUN.

Run under WINDOWS python.exe from the repo root (the bridge binds Windows loopback):
    python.exe src\\RimMandrake\\bridgetools\\prove_deepfire_god_deltas.py [--start] [--x 60 --z 60]

Needs a mod list with LuminousPigment (this build), Ninefold (mandrake.rm.ninefold) AND LightsOut
(juanlopez2008.lightsout). Without Ninefold the god checks are UNMEASURED, and without LightsOut the
LightsOut checks are; either way the script exits 2 and does not report a pass.

--start   start a fresh dev quicktest first (rimworld/start_debug_game_ready).
--x/--z   SOUTH-WEST corner of the 6x6 interior of the test room (jawa/make_empty_room: walled,
          roofed, WoodPlankFloor).

Spec row 10: "quicktest with Ninefold: GetSatiation before/after one coat shows +3 on eight gods,
+8 on the trio, -3 Ishko; a tagged test idol def -> +15 on its god. With LightsOut: proxies survive
an empty room being 'switched off'". "+3 on eight gods" is read with §5.2's "+Medium INSTEAD for
Mob'Unloo, Rekko, Zizzik", so a plain first coat is: Ishko -3, the trio +8, the other five +3.

Every god action reports each god's satiation before ("b") and its change ("d") around ONE real call.
Expected changes are the spec's numbers x Ninefold's eventMagnitudeMultiplier (reported), clamped to
Ninefold's [-100, 100] satiation range from the reported start point.

  1  first coat on a new steel wall            Ishko -3, trio +8, the rest +3   (deepfire.coat)
  2  a second coat on the same wall            nothing moves
  3  first coat on a new parka (worn class)    Ishko -8, trio +8, the rest +3   (deepfire.worn)
  4  first coat on an idol tagged Rekko        Rekko +15, Ishko -3, every other god +3
  5  first coat on an idol tagged Ishko        Ishko -15, every other god +3
  6  first coat on a WoodPlankFloor cell       as step 1
  7  diminish: godDeltaDiminishAfter walls at full strength, the next one +-1 per god
  8  sold: the TradeDeal.TryExecute prefix+postfix are registered; DealSellsDeepfire says yes to a
     sold jar and a sold coated sculpture, no to sold steel and a BOUGHT jar; OnDeepfireSold moves
     Mob'Unloo +8 and nobody else
  9  LightsOut: a coated sculpture's proxy and a StandingLamp (control) in the roofed room;
     LightsOut's own Lights.DisableAllLights(room) switches the lamp off (CanConsumeResources false)
     and leaves the proxy glowing (CanBeLight false, CanConsumeResources null)
 10  no new errors naming LuminousPigment/Deepfire.
Exit 0 = every assertion passed, 1 = at least one failed, 2 = could not run / something UNMEASURED.
"""
import argparse
import json
import sys
import time

sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb

TAG = "[DeepfireGods] "
CATEGORY = "Deepfire"
PREFIXES = ("GodDeltas:", "LightsOut:")

GODS = ("Ishko", "Ohm", "Oomo", "MobUnloo", "Rekko", "TaBaa", "Zizzik", "Shkaar", "Ozzik")
TRIO = ("MobUnloo", "Rekko", "Zizzik")
LIKE = 3.0        # EventMagnitude.Small, godDeltaLike default
ADORE = 8.0       # EventMagnitude.Medium, godDeltaAdore default
ISHKO = 3.0       # godDeltaIshko default
STATUE = 15.0     # EventMagnitude.Large, godDeltaStatue default
DIMINISHED = 1.0  # DeepfireGodDeltas.DiminishedMagnitude
SAT_MIN, SAT_MAX = -100.0, 100.0

ap = argparse.ArgumentParser()
ap.add_argument("--start", action="store_true")
ap.add_argument("--x", type=int, default=60)
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
unmeasured = []


def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", name, detail))


def skip(name, why):
    unmeasured.append(name)
    print("  UNMEASURED  %s  (%s)" % (name, why))


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
    # 1.6 flattens mod categories: the actions sit directly under Actions as "T: GodDeltas: ..."
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
        i = line.find(TAG)
        if i >= 0:
            try:
                return json.loads(line[i + len(TAG):].strip())
            except Exception:
                pass
    print("    (no tagged line; raw result: %s)" % json.dumps(r)[:400])
    return None


def coat_table(ishko_penalty):
    return {g: (-ishko_penalty if g == "Ishko" else ADORE if g in TRIO else LIKE) for g in GODS}


def statue_table(god):
    t = {}
    for g in GODS:
        if g == god:
            t[g] = -STATUE if g == "Ishko" else STATUE
        elif g == "Ishko":
            t[g] = -ISHKO
        else:
            t[g] = LIKE
    return t


def diminished(table):
    return {g: (DIMINISHED if v > 0 else -DIMINISHED if v < 0 else 0.0) for g, v in table.items()}


def expect_deltas(name, rep, table, deltas_key="deltas"):
    """table: god -> spec amount (before the multiplier). Asserts every god's change."""
    if not rep:
        check(name, False, "no report")
        return
    if not rep.get("ninefold"):
        skip(name, "Ninefold not loaded")
        return
    if not rep.get("engineEnabled") or not rep.get("godsReact"):
        skip(name, "Ninefold engine or Deepfire godsReact is OFF in settings: %s" % json.dumps(rep)[:200])
        return
    mult = rep.get("multiplier", 1.0)
    got = rep.get(deltas_key) or {}
    bad = []
    for g in GODS:
        cell = got.get(g)
        if cell is None:
            bad.append("%s missing" % g)
            continue
        b = cell.get("b")
        want = max(SAT_MIN, min(SAT_MAX, b + table.get(g, 0.0) * mult)) - b
        if not near(cell.get("d"), want):
            bad.append("%s %+.2f (want %+.2f)" % (g, cell.get("d"), want))
    check(name, not bad, "; ".join(bad) if bad else "x%.2f" % mult)


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

call("jawa/drain_log", errorsOnly=True)  # discard errors that predate this proof

room = call("jawa/make_empty_room", rect="%d,%d,8,8" % (X - 1, Z - 1),
            wallDef="Wall", stuffDef="WoodLog", floorDef="WoodPlankFloor")
print("make_empty_room:", json.dumps(room)[:300])
if not room.get("success"):
    sys.exit(2)

actions = find_actions()
print("Deepfire dev actions:", sorted(actions))
if not actions:
    print("no Deepfire dev actions under Actions -- is LuminousPigment (this build) loaded?")
    sys.exit(2)

# ---- 1-2 wall ----
print("== 1 first coat, wall ==")
w = run(actions, "GodDeltas: coat new wall", X, Z + 1)
print("   ", json.dumps(w)[:600])
check("wall: 1 coat, not worn, not a statue",
      w and w.get("coats") == 1 and not w.get("wornClass") and not w.get("statueGod"), json.dumps(w)[:200])
expect_deltas("wall first coat: Ishko -3, trio +8, other five +3", w, coat_table(ISHKO))

print("== 2 second coat ==")
w2 = run(actions, "GodDeltas: second coat", X, Z + 1)
check("wall: second coat landed (2 coats)", w2 and w2.get("coats") == 2, json.dumps(w2)[:200])
expect_deltas("second coat: no god moves", w2, {g: 0.0 for g in GODS})

# ---- 3 parka ----
print("== 3 first coat, parka ==")
p = run(actions, "GodDeltas: coat new parka", X + 1, Z + 1)
print("   ", json.dumps(p)[:600])
check("parka: worn class", p and p.get("wornClass") and p.get("coats") == 1, json.dumps(p)[:200])
expect_deltas("parka first coat: Ishko -8, trio +8, other five +3", p, coat_table(ADORE))

# ---- 4-5 idols ----
print("== 4 idol of Rekko ==")
ir = run(actions, "GodDeltas: coat idol of Rekko", X + 2, Z + 1)
print("   ", json.dumps(ir)[:600])
check("idol: extension read as Rekko", ir and ir.get("statueGod") == "Rekko", json.dumps(ir)[:200])
expect_deltas("Rekko idol: Rekko +15, Ishko -3, every other god +3", ir, statue_table("Rekko"))

print("== 5 idol of Ishko ==")
ii = run(actions, "GodDeltas: coat idol of Ishko", X + 3, Z + 1)
print("   ", json.dumps(ii)[:600])
check("idol: extension read as Ishko", ii and ii.get("statueGod") == "Ishko", json.dumps(ii)[:200])
expect_deltas("Ishko idol: Ishko -15, every other god +3", ii, statue_table("Ishko"))

# ---- 6 floor ----
print("== 6 floor cell ==")
f = run(actions, "GodDeltas: coat floor cell", X + 5, Z + 5)
print("   ", json.dumps(f)[:600])
check("floor: cell coated", f and f.get("added"), json.dumps(f)[:200])
expect_deltas("floor first coat: Ishko -3, trio +8, other five +3", f, coat_table(ISHKO))

# ---- 7 diminish ----
print("== 7 diminish ==")
d = run(actions, "GodDeltas: diminish test", X + 5, Z + 2)
print("   ", json.dumps(d)[:900])
if d:
    n = d.get("diminishAfter")
    check("diminish: diminishAfter+1 events recorded on the wall def", d.get("events") == (n or 0) + 1, json.dumps(d)[:200])
expect_deltas("diminish: event #diminishAfter still full strength", d, coat_table(ISHKO), "lastFull")
expect_deltas("diminish: the next event is +-1 per god", d, diminished(coat_table(ISHKO)), "firstDiminished")

# ---- 8 sold ----
print("== 8 sold ==")
s = run(actions, "GodDeltas: sold deepfire", X, Z)
print("   ", json.dumps(s)[:600])
check("sold: prefix and postfix registered on TradeDeal.TryExecute",
      s and s.get("prefixRegistered") and s.get("postfixRegistered"), json.dumps(s)[:200])
check("sold: a sold jar and a sold coated sculpture count; sold steel and a bought jar do not",
      s and s.get("sellsJar") and s.get("sellsCoatedSculpture") and not s.get("sellsSteel") and not s.get("buysJar"),
      json.dumps(s)[:300])
expect_deltas("sold: Mob'Unloo +8, nobody else", s, {g: (ADORE if g == "MobUnloo" else 0.0) for g in GODS})

# ---- 9 LightsOut ----
print("== 9 LightsOut ==")
lo = run(actions, "LightsOut: switch off room", X + 2, Z + 4)
print("   ", json.dumps(lo)[:700])
if not lo:
    check("LightsOut: action reported", False)
elif not lo.get("lightsOutLoaded"):
    skip("LightsOut: proxies survive a switched-off room", "LightsOut not loaded")
else:
    check("LightsOut: both compat patches applied", lo.get("canBeLightPatched") and lo.get("canConsumePatched"))
    check("LightsOut: FlickLights on and room indoors (the switch-off can run)",
          lo.get("flickLights") is True and lo.get("roomOutdoors") is False, json.dumps(lo)[:200])
    check("LightsOut control: the StandingLamp IS a light and was switched off",
          lo.get("lampCanBeLight") is True and lo.get("lampCanConsume") is False,
          "canBeLight=%s canConsume=%s" % (lo.get("lampCanBeLight"), lo.get("lampCanConsume")))
    check("LightsOut: the Deepfire proxy is NOT a light to it", lo.get("proxyFound") and lo.get("proxyCanBeLight") is False)
    check("LightsOut: proxy glows before and after the switch-off",
          lo.get("proxyGlowsBefore") and lo.get("proxyGlowsAfter"),
          "before=%s after=%s canConsume=%s" % (lo.get("proxyGlowsBefore"), lo.get("proxyGlowsAfter"), lo.get("proxyCanConsume")))
    check("LightsOut: proxy has no consume status (glow postfix leaves it alone)", lo.get("proxyCanConsume") is None)

print("== 10 log ==")
logs = call("jawa/drain_log", errorsOnly=True)
text = json.dumps(logs)
bad = [k for k in ("LuminousPigment", "Deepfire", "Ninefold") if k in text]
check("no LuminousPigment/Deepfire/Ninefold errors logged during the proof", not bad, text[:600] if bad else "")

failed = [n for n, ok in results if not ok]
print("\n%d/%d passed, %d UNMEASURED" % (len(results) - len(failed), len(results), len(unmeasured)))
for n in failed:
    print("  FAILED:", n)
for n in unmeasured:
    print("  UNMEASURED:", n)
sys.exit(1 if failed else 2 if unmeasured else 0)
