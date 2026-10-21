#!/usr/bin/env python3
"""titanoslime_gates.py -- the seven live gates of design/RimMandrake/RM_titanoslime_spec.md section 8
(item TITANOSLIME_SLIME_BIOME_1). Bridge-side: run with python.exe from the repo root, bridge HELD:

    python.exe src/RimMandrake/GelatinousSlime/northstar/titanoslime_gates.py [--only g1,g3] [--fresh] | tr -d '\\r'

Writes Transient/afk_2026-10-17/titanoslime_gates_result.json (rows: gate, check, status, cls, evidence).
PASS = asked the game and the answer met the bar; FAIL = asked, missed; UNMEASURED = could not ask.

LIST. The gates need GelatinousSlime (composed in mandrake.rm.biomes) + mandrake.rm.hugethings (Titanic tier, corpse
site) + neku.largepawns (footprint) + all five DLC. The preflight row reads the running list, not a label.

PROOF SURFACE. RimMandrake.GelatinousSlime.RM_TitanoslimeProof (Source/TitanoslimeProof.cs) through jawa/static_call:
ProofRead / ProofSetMass (the DEV gizmo path) / ProofFeed (AddMass, the path every growth source takes) /
ProofEngulf (RM_Verb_MeleeEngulf's own CanEngulf+Engulf outcome) / ProofKill / ProofFind / ProofGhostScan. Titanic tier is
RimMandrake.TitanicCreatures.TitanicTierUtility.GetTier; the footprint is LargePawns.LargePawnUtility.GetSize.

LIES this script guards against (spec section 8): BodySize is read from the pawn, never the sprite; Large Pawns'
footprint is read after 60 ticks (its cache); burst-out uses TEN muffalo; a stage that "grew" on screen proves nothing.
VANISH (MEASURED 2026-10-17): Destroy(DestroyMode.Vanish) on a titanoslime (jawa/pawn_force_incapacitate action=vanish)
left it in the cell grid: any later spawn in the 3x3 around it NREd in
PawnCollisionTweenerUtility.GetPawnsStandingAtOrAboutToStandAt and Update/OnGUI threw every frame. MECHANISM (code read
2026-10-17, item TITANOSLIME_VANISH_DIAGNOSE_GHOST_IN_GRID): Large Pawns registers the pawn in every cell of a square
sized from BodySize AT REGISTRATION and deregisters by the size it has NOW; Thing.SpawnSetup registers before
RM_CompEngulfer.PostSpawnSetup locks the stage, so a lock to a SMALLER stage than the generator's random-age one left
the outer ring behind. Kill leaves the same ring, but of a dead pawn, which the tweener skips (GetPosture != Standing);
a vanished pawn is Standing with pather == null, hence the NRE. Fix: RM_CompEngulfer.LockStageReregistering. Gate g8
proved it: g8 PASSED live 2026-10-17 (6/6 cases ghosts=0, Muffalo respawn 9/9 each, 22-mod list incl. Large Pawns +
Huge Things), so this script VANISHES slimes it is done with again. Positive control for ProofGhostScan is the
respawn count, which read 0-4/9 before the fix.
RULED (owner, 2026-09-21): growth is PERMANENT by default, so gate 4's "drops to stage 1" is checked only with
titanoslimeReversible ON; with the shipped default the stage must HOLD while gelatids are shed.
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))

PROOF = "RimMandrake.GelatinousSlime.RM_TitanoslimeProof"
SETTINGS = "RimMandrake.GelatinousSlime.SlimeSettings"
TIER = "RimMandrake.TitanicCreatures.TitanicTierUtility"
LP = "LargePawns.LargePawnUtility"
KIND = "RM_Titanoslime"
BODY = [6.0, 10.02, 16.02, 24.0, 40.02]          # baseBodySize 6 x LifeStageDef bodySizeFactor 1/1.67/2.67/4/6.67
DRAW = [4.0, 5.0, 6.0, 7.5, 9.0]                  # Titanoslime.xml kind lifeStages drawSize
OUT = os.path.join(REPO, "Transient", "afk_2026-10-17", "titanoslime_gates_result.json")
NEED_MODS = ("mandrake.rm.biomes", "mandrake.rm.hugethings", "neku.largepawns", "ludeon.rimworld.royalty",
             "ludeon.rimworld.ideology", "ludeon.rimworld.biotech", "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey")

ROWS = []


def say(m):
    print("%s %s" % (time.strftime("%H:%M:%S"), m), flush=True)


def row(gate, check, status, cls, evidence):
    ROWS.append({"gate": gate, "check": check, "status": status, "cls": cls, "evidence": evidence})
    say("ROW %s %-44s %-10s %-7s %s" % (gate, check, status, cls or "", str(evidence)[:260]))


class Unmeasured(Exception):
    pass


class G(object):
    def __init__(self):
        from modcheck import reviewmap as RM
        self.B = RM.LiveBridge()

    def call(self, tool, **kw):
        return self.B.call(tool, **kw)

    def ok(self, tool, **kw):
        r = self.call(tool, **kw)
        if r.get("success") is not True:
            raise Unmeasured("%s refused: %s" % (tool, json.dumps(r)[:300]))
        return r

    def gone(self, pid):
        """Vanish a pawn we are done with and CHECK it left (the vanish/kill reply was never read before)."""
        r = self.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")
        # a colonist still HELD inside another slime answers "No pawn matching" (2 per full run): harmless, expected.
        if r.get("destroyedAfter") is not True:
            say("VANISH-MISS %s %s" % (pid, json.dumps(r)[:300]))
        return r

    def ticks(self, n):
        while n > 0:
            k = min(n, 1000)
            self.ok("rimworld/step_game_ticks", ticks=k, pauseFirst=True, timeoutMs=120000)
            n -= k

    def sc(self, type_, method, args=""):
        r = self.ok("jawa/static_call", type=type_, method=method, args=args)
        return str(r.get("result"))

    def proof(self, method, *args):
        txt = self.sc(PROOF, method, "|".join(str(a) for a in args))
        if txt.startswith("ERROR"):
            raise Unmeasured("%s: %s" % (method, txt))
        return txt

    def read(self, pid):
        """ProofFind by id number: also sees a pawn that died or left the map (ProofRead resolves map things only)."""
        r = kv(self.proof("ProofFind", re.sub(r"\D", "", pid)))
        if r.get("found") != "True":
            raise Unmeasured("pawn %s not found anywhere" % pid)
        return r

    def setting(self, field, value):
        self.ok("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field, value=str(value).lower()
                if isinstance(value, bool) else str(value))
        got = self.ok("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field).get("value")
        if str(got).lower() != (str(value).lower()):
            raise Unmeasured("setting %s read back %r, wanted %r" % (field, got, value))

    def spawn(self, kind, x, z, faction="none", count=1):
        r = self.ok("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=count)
        ids = [str(p.get("id")).replace("Thing_", "") for p in (r.get("pawns") or []) if p.get("id")]
        if len(ids) != count:
            raise Unmeasured("spawn_pawn %s x%d returned %d ids" % (kind, count, len(ids)))
        return ids

    def tier(self, pid):
        return self.sc(TIER, "GetTier", pid)

    def lpsize(self, pid):
        return self.sc(LP, "GetSize", pid)

    def pawns(self, corpses=False):
        r = self.ok("jawa/list_pawns", includeHealth=False, includeCorpses=corpses, limit=500)
        return r.get("pawns") or []

    def things(self, rect, limit=2000):
        r = self.ok("jawa/list_things", rect=rect, includePawns=False, limit=limit)
        return r.get("things") or []


def kv(text):
    return dict(re.findall(r"(\w+)=(\S+)", text))


def near(a, b, tol=0.1):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def gate(fn):
    """Each gate runs to the end of its own body; an Unmeasured anywhere becomes one UNMEASURED/HARNESS row."""
    def run(g, S):
        say("=== %s" % fn.__name__)
        a = log_errors()
        try:
            fn(g, S)
        except Unmeasured as e:
            row(fn.__name__, "could_not_ask", "UNMEASURED", "HARNESS", str(e))
        except Exception as e:  # noqa: BLE001
            row(fn.__name__, "script_error", "UNMEASURED", "HARNESS", "%s: %s" % (type(e).__name__, e))
        sent = "TITANO_GATES_SENTINEL %s %d" % (fn.__name__, int(time.time() * 1000))
        g.call("jawa/static_call", type="Verse.Log", method="Warning", args=sent)
        alive = False
        for _ in range(8):                       # Player.log is flushed lazily; a capped Verse.Log never writes it
            time.sleep(1.0)
            try:
                alive = any(sent in line for line in open(PLAYER_LOG, encoding="utf-8", errors="replace"))
            except OSError:
                alive = False
            if alive:
                break
        b = log_errors()
        if a is None or b is None or b[0] < a[0] or not alive:
            row(fn.__name__, "log_budget", "UNMEASURED", "HARNESS",
                "Player.log blind (sentinel seen=%s; Verse.Log stops at 10,000 messages)" % alive)
        else:
            d = (b[1] - a[1], b[2] - a[2])
            row(fn.__name__, "log_budget", "PASS" if d == (0, 0) else "FAIL", None if d == (0, 0) else "MOD?",
                "+%d log lines, +%d exception lines, +%d naming GelatinousSlime/Titanoslime" % (b[0] - a[0], d[0], d[1]))
    run.__name__ = fn.__name__
    return run


def site(S, i):
    """Disjoint 14-cell pads in a row across the map centre (pad i)."""
    cx, cz = S["cx"], S["cz"]
    return cx - 60 + (i % 9) * 14, cz - 30 + (i // 9) * 14


# --------------------------------------------------------------------------- preflight

def preflight(g, S, fresh):
    run = g.ok("jawa/running_mods")
    ids = [str(m).lower() for m in (run.get("packageIds") or [])]
    S["mods"] = len(ids)
    missing = [m for m in NEED_MODS if m not in ids]
    row("pre", "running_list", "PASS" if not missing else "UNMEASURED", None if not missing else "HARNESS",
        "len(env.running)=%d missing=%s" % (len(ids), missing))
    if missing:
        raise SystemExit(2)
    info = g.call("rimworld/get_game_info")
    if fresh or not (info.get("state") or {}).get("hasCurrentGame"):
        if (info.get("state") or {}).get("hasCurrentGame"):
            g.call("rimworld/go_to_main_menu")
            time.sleep(8)
        say("starting a quicktest map")
        try:
            g.call("rimworld/start_debug_game_ready")
        except Exception as e:  # noqa: BLE001   the late reply is expected (rimworld-debug-testing section 1)
            say("start_debug_game_ready raised %s; polling" % e)
        from modcheck import reviewmap as RM
        for _ in range(40):
            time.sleep(5)
            try:
                g.B = RM.LiveBridge()
                if g.call("jawa/map_info").get("success"):
                    break
            except Exception:  # noqa: BLE001
                pass
    mi = g.ok("jawa/map_info")
    S["cx"], S["cz"] = int(mi.get("sizeX", 250)) // 2, int(mi.get("sizeZ", 250)) // 2
    for f, v in (("titanoslimeEngulfs", True), ("titanoslimeGrows", True), ("titanoslimeReversible", False),
                 ("titanoslimeMaxStage", 5), ("titanoslimeSheds", True)):
        g.setting(f, v)
    c = g.call("jawa/static_call", type="Verse.Log", method="Clear")   # reset Verse.Log's 10,000-message cap
    say("Verse.Log.Clear: %s" % c.get("success"))
    g.call("jawa/kill_hostiles")
    row("pre", "site", "PASS", None, "map %sx%s centre %d,%d; settings at shipped defaults" %
        (mi.get("sizeX"), mi.get("sizeZ"), S["cx"], S["cz"]))


# --------------------------------------------------------------------------- gates

@gate
def g1(g, S):
    d = g.ok("jawa/get_defs", defs="ThingDef/%s;PawnKindDef/%s" % (KIND, KIND))
    nf = d.get("notFound") or []
    row("g1", "def_resolves_live", "PASS" if not nf else "FAIL", None if not nf else "MOD", "notFound=%s" % nf)
    x, z = site(S, 0)
    ids = g.spawn(KIND, x, z, count=5)
    rs = [g.read(i) for i in ids]
    stages = [int(r["stage"]) for r in rs]
    bad = [(r["id"], r["stage"], r["bodySize"]) for r in rs if not near(r["bodySize"], BODY[int(r["stage"])])]
    row("g1", "spawn_places_and_rolls_stage_1_to_3", "PASS" if all(0 <= s <= 2 for s in stages) else "FAIL",
        None if all(0 <= s <= 2 for s in stages) else "MOD", "5 spawned, stage idx %s" % stages)
    s1 = [r for r in rs if r["stage"] == "0"]
    if not s1:
        r = kv(g.proof("ProofSetMass", ids[0], 0))
        s1 = [r]
    r = s1[0]
    good = near(r["bodySize"], 6.0) and not bad
    row("g1", "bodysize_6_at_stage_1", "PASS" if good else "FAIL", None if good else "MOD",
        "stage1 %s bodySize=%s; per-stage mismatches %s" % (r["id"], r["bodySize"], bad))
    S["g1_ids"] = ids


@gate
def g2(g, S):
    x, z = site(S, 1)
    pid = g.spawn(KIND, x, z)[0]
    g.proof("ProofSetMass", pid, 0)
    g.proof("ProofSetMass", pid, 12)
    g.ticks(60)
    r = g.read(pid)
    t, lp = g.tier(pid), g.lpsize(pid)
    four = dict(bodySize=r["bodySize"], drawSize=r["drawSize"], tier=t, footprint=lp, stage=r["stage"], mass=r["mass"])
    ok = near(r["bodySize"], 16.02) and near(r["drawSize"], 6.0) and t == "T2" and lp == "3"
    row("g2", "mass12_bodysize16_draw6_T2_3x3", "PASS" if ok else "FAIL", None if ok else "MOD", four)
    name = "RM_titano_gate2"
    g.ok("rimworld/save_game", saveName=name)
    say("saved; loading %s" % name)
    sp = os.path.join(__import__("game_paths").SAVES, name + ".rws")
    if not os.path.exists(sp) or time.time() - os.path.getmtime(sp) > 120:
        raise Unmeasured("save %s not written (stat %s)" % (name, sp))
    lr = g.call("rimworld/load_game_ready", saveName=name)
    if lr.get("success") is not True:
        raise Unmeasured("load_game_ready: %s" % json.dumps(lr)[:300])
    for _ in range(60):                          # the reply can precede the load; wait until a step really advances
        time.sleep(3)
        st = g.call("rimworld/step_game_ticks", ticks=60, pauseFirst=True, timeoutMs=60000)
        if st.get("success") is True and st.get("advancedTicks", 0) >= 60:
            break
    else:
        raise Unmeasured("no steppable game within 180 s of load_game_ready")
    r2 = g.read(pid)
    t2, lp2 = g.tier(pid), g.lpsize(pid)
    after = dict(bodySize=r2["bodySize"], drawSize=r2["drawSize"], tier=t2, footprint=lp2, stage=r2["stage"], mass=r2["mass"])
    same = after == four
    row("g2", "survives_save_reload", "PASS" if same else "FAIL", None if same else "MOD",
        {"before": four, "after": after})


@gate
def g3(g, S):
    # Natural route, FOUR replicates 30 cells apart (one fight is RNG: on 2026-10-17 one stage-1 swallowed at
    # 1680 ticks and the next was downed by its four colonists at 2520 ticks without ever swallowing).
    reps = []
    for k in range(4):
        x, z = S["cx"] - 60 + k * 30, S["cz"] + 40
        slime = g.spawn(KIND, x, z)[0]
        g.proof("ProofSetMass", slime, 0)
        cols = g.spawn("Colonist", x + 1, z, faction="player", count=4)
        for c in cols:
            g.call("jawa/pawn_need", pawn=c, action="need", need="Food", level=1.0)
            g.call("jawa/pawn_need", pawn=c, action="need", need="Rest", level=1.0)
            g.call("jawa/set_draft", pawnId=c, drafted=True, fireAtWill=True)
        g.call("jawa/damage", damageDef="Blunt", amount=2, thingId=slime, instigatorId=cols[0])   # 100 % manhunter on damage
        reps.append({"slime": slime, "cols": cols, "at": None, "end": None})
    t_used = 0
    while t_used < 3600 and any(r["at"] is None and r["end"] is None for r in reps) and not any(r["at"] is not None for r in reps):
        g.ticks(120)
        t_used += 120
        for r in reps:
            if r["at"] is not None or r["end"] is not None:
                continue
            st = g.read(r["slime"])
            if int(st.get("held", 0)) > 0:
                r["at"], r["state"] = t_used, st
            elif st.get("dead") == "True" or st.get("downed") == "True":
                r["end"] = "downed@%d" % t_used
    say("checkpoint natural-arm log %s" % (log_errors(),))
    won = [r for r in reps if r["at"] is not None]
    summary = ["swallow@%d" % r["at"] if r["at"] is not None else (r["end"] or "nothing") for r in reps]
    row("g3", "colonist_swallowed_within_60s_natural", "PASS" if won else "FAIL", None if won else "MOD",
        "4 replicates (stage-1 vs 4 drafted colonists): %s" % summary)
    if not won:
        for r in reps:                           # no leak into later gates' log budgets
            g.gone(r["slime"])
            for p in r["cols"]:
                g.gone(p)
        return
    first = won[0]
    slime, cols, swallowed = first["slime"], first["cols"], first["state"]
    for r in reps:                               # quiet the map: the other fights end now
        if r is not first:
            g.gone(r["slime"])   # vanish is safe since g8 PASSED live
            for p in r["cols"]:
                g.gone(p)
    held_id = swallowed["heldClock"].strip("[]").split(":")[0]
    for c in cols:                               # stop the beating, so the countdown and the down are ours
        if re.sub(r"\D", "", c) != re.sub(r"\D", "", held_id):
            g.gone(c)
    ins = g.ok("jawa/inspect_string", thingIds=slime)
    text = json.dumps(ins.get("things") or ins)
    m = re.search(r"Digesting [^\"]*?(\d+) s left", text)
    row("g3", "inspect_shows_countdown", "PASS" if m else "FAIL", None if m else "MOD",
        m.group(0) if m else text[:240])
    # downing the slime drops the colonist stunned, acid-burned, slimification +0.15
    pre = kv(g.proof("ProofFind", re.sub(r"\D", "", held_id)))
    g.ok("jawa/pawn_force_incapacitate", pawn=slime, action="downed")
    rel = kv(g.proof("ProofFind", re.sub(r"\D", "", held_id)))
    ok = (rel.get("spawned") == "True" and rel.get("stunned") == "True" and int(rel.get("acidHediffs", 0)) > 0
          and rel.get("slimification", "none") != "none" and float(rel["slimification"]) >= 0.15)
    row("g3", "downed_slime_releases_stunned_acid_slimified", "PASS" if ok else "FAIL", None if ok else "MOD",
        "before slim=%s | after spawned=%s stunned=%s acid=%s slim=%s" % (pre.get("slimification"), rel.get("spawned"),
                                                                       rel.get("stunned"), rel.get("acidHediffs"), rel.get("slimification")))
    g.gone(slime)
    g.gone(held_id)
    say("checkpoint after down+vanish log %s" % (log_errors(),))
    # absorb arm: three pairs (a struggling human bursts out ~0.4 %/round), first one absorbed is read
    pairs = []
    for k in range(3):
        px, pz = site(S, 3 + k)
        s = g.spawn(KIND, px, pz)[0]
        g.proof("ProofSetMass", s, 0)
        c = g.spawn("Colonist", px + 2, pz, faction="player")[0]
        g.call("jawa/pawn_need", pawn=c, action="need", need="Food", level=1.0)
        pg = (g.ok("jawa/pawn_get", pawn=c).get("pawns") or [{}])[0]
        before = sorted(a.get("def") for a in (pg.get("apparel") or []) + (pg.get("equipment") or []))
        e = g.proof("ProofEngulf", s, c)
        if "canEngulf=True" not in e:
            raise Unmeasured("forced engulf refused: %s" % e[:200])
        pairs.append((s, c, px, pz, before))
    done, lastheld = None, {}
    for _ in range(50):                          # digest ~4500 ticks for a colonist
        g.ticks(120)
        for s, c, px, pz, before in pairs:
            r = g.read(s)
            if int(r.get("held", 0)) > 0:
                lastheld[s] = r.get("heldClock")
            if int(r.get("held", 1)) == 0 and done is None:
                f = kv(g.proof("ProofFind", re.sub(r"\D", "", c)))
                if f.get("dead") == "True" or f.get("found") == "False":
                    done = (s, c, px, pz, before, r, f)
        if done:
            break
        say("checkpoint absorb-wait log %s" % (log_errors(),)) if _ % 10 == 0 else None
        for s, *_ in pairs:
            g.call("jawa/pawn_need", pawn=s, action="need", need="Food", level=0.3)
    if not done:
        row("g3", "timer_absorbs", "UNMEASURED", "SITE", "no pair absorbed in 6000 ticks (all burst out?): %s" %
            [g.proof("ProofFind", re.sub(r"\D", "", c))[:120] for _, c, *_ in pairs])
        return
    s, c, px, pz, before, r, f = done
    me = [p for p in g.pawns() if str(p.get("id")).replace("Thing_", "") == s]
    if not me:
        raise Unmeasured("absorbing slime %s not on the map" % s)
    sx, sz = int(me[0]["x"]), int(me[0]["z"])
    ground = {t.get("def") for t in g.things("%d,%d,21,21" % (sx - 10, sz - 10))}
    gear_found = [d for d in before if d in ground]
    smear = "RM_Filth_SlimeSmear" in ground
    # The slime gains the VICTIM's BodySize (Absorb: AddMass(held.BodySize)). A random "Colonist" is sometimes a
    # HumanlikeTeenager, BodySize 0.8: 2026-10-17 a fixed 1.0 bar FAILed 4 of 11 runs on mass=0.8 with the victim
    # reading bodySize=0.8 lifeStage=HumanlikeTeenager (HARNESS, not MOD). A 20-colonist spawn probe that read all 1.0
    # made this look false once; one probe of a minority outcome proves nothing.
    vb = float(f.get("bodySize") or 1.0)
    ok = (f.get("found") == "False" or f.get("corpse") in ("none", "destroyed")) and near(r["mass"], vb, 0.05) \
        and near(r.get("food", 0), 1.0, 0.02) and before and len(gear_found) == len(before)
    row("g3", "timer_absorbs_no_corpse_gear_mass_food", "PASS" if ok else "FAIL", None if ok else "MOD",
        "victim corpse=%s destroyed=%s | slime mass=%s food=%s | victim after: bodySize=%s lifeStage=%s | worn %s, "
        "on ground near slime %s, smear %s" % (f.get("corpse"), f.get("destroyed"), r["mass"], r.get("food"),
                                               f.get("bodySize"), f.get("lifeStage"), before, gear_found, smear)
        + " | victim %s, slime last held %s, arm masses %s" % (c, lastheld.get(s), [g.read(ps).get("mass") for ps, *_ in pairs]))
    # LEAK (2026-10-17): the three absorb-arm slimes were never removed, stayed manhunter and logged 100+ "Resolved path
    # returned no nodes ... for RM_Titanoslime" lines into every LATER gate's log budget. Clear the arm.
    for ps, pc, *_ in pairs:
        g.gone(ps)
        if pc != c:
            g.gone(pc)


@gate
def g4(g, S):
    pairs = []
    for k in range(10):
        x, z = site(S, 6 + k)
        s = g.spawn(KIND, x, z)[0]
        g.proof("ProofSetMass", s, 0)
        m = g.spawn("Muffalo", x + 2, z)[0]
        e = g.proof("ProofEngulf", s, m)
        if "canEngulf=True" not in e:
            raise Unmeasured("muffalo engulf refused: %s" % e[:200])
        pairs.append((s, m))
    out, t_used = set(), 0
    for _ in range(30):                          # 3600 ticks = 60 s
        g.ticks(120)
        t_used += 120
        for s, m in pairs:
            if m not in out:
                f = kv(g.proof("ProofFind", re.sub(r"\D", "", m)))
                if f.get("spawned") == "True" and f.get("dead") == "False":
                    out.add(m)
    ok = len(out) >= 6
    row("g4", "muffalo_bursts_out_most_runs_60s", "PASS" if ok else "FAIL", None if ok else "MOD",
        "%d/10 burst out within %d ticks (model: ~86 %%)" % (len(out), t_used))
    for s, m in pairs:                           # vanish the slimes so later gates have a quiet map
        g.gone(s)

    def cut_to_half(pid):
        shed = 0
        base = len([p for p in g.pawns() if (p.get("kind") or p.get("kindDef")) == "RM_Gelatid"])
        for _ in range(60):
            r = g.read(pid)
            if float(r["health"]) <= 0.5 or r.get("dead") == "True":
                break
            g.call("jawa/damage", damageDef="Cut", amount=12, thingId=pid, armorPenetration=1.0)
        shed = len([p for p in g.pawns() if (p.get("kind") or p.get("kindDef")) == "RM_Gelatid"]) - base
        return shed, g.read(pid)

    for rev in (False, True):
        g.setting("titanoslimeReversible", rev)
        try:
            x, z = site(S, 17 + int(rev))
            pid = g.spawn(KIND, x, z)[0]
            g.proof("ProofSetMass", pid, 0)
            # mass 8 = mid stage 2. At exactly 4 (the threshold) a reversible slime drops to stage 1 after two sheds
            # and stage 1 never sheds, so "3 sheds AND a drop" is unreachable there by design (run 2026-10-17: 2 sheds).
            g.proof("ProofSetMass", pid, 8 if rev else 4)
            st0 = g.read(pid)["stage"]
            shed, r = cut_to_half(pid)
            want_stage = "0" if rev else "1"
            ok = st0 == "1" and shed >= 3 and r["stage"] == want_stage
            row("g4", "cut_stage2_to_half_sheds_3%s" % ("_and_drops_to_1_reversible_on" if rev else "_holds_stage_default"),
                "PASS" if ok else "FAIL", None if ok else "MOD",
                "stage %s -> %s, shed %d, health %s, mass %s" % (st0, r["stage"], shed, r["health"], r["mass"]))
        finally:
            g.setting("titanoslimeReversible", False)


@gate
def g5(g, S):
    x, z = site(S, 19)
    a = g.spawn(KIND, x, z)[0]
    # maxStage
    g.setting("titanoslimeMaxStage", 2)
    try:
        g.proof("ProofSetMass", a, 0)
        r = kv(g.proof("ProofSetMass", a, 12))
    finally:
        g.setting("titanoslimeMaxStage", 5)
    ok = r["stage"] == "1"
    row("g5", "maxStage2_refuses_stage3_at_mass12", "PASS" if ok else "FAIL", None if ok else "MOD",
        "stage idx %s mass %s" % (r["stage"], r["mass"]))
    # grows
    g.proof("ProofSetMass", a, 0)
    g.setting("titanoslimeGrows", False)
    try:
        off = kv(g.proof("ProofFeed", a, 4))
    finally:
        g.setting("titanoslimeGrows", True)
    on = kv(g.proof("ProofFeed", a, 4))
    ok = near(off["mass"], 0, 0.01) and near(on["mass"], 4, 0.01) and on["stage"] == "1"
    row("g5", "grows_toggle", "PASS" if ok else "FAIL", None if ok else "MOD",
        "off: mass %s | on: mass %s stage %s" % (off["mass"], on["mass"], on["stage"]))
    # reversible
    g.proof("ProofSetMass", a, 12)
    off = kv(g.proof("ProofFeed", a, -6))
    g.setting("titanoslimeReversible", True)
    try:
        on = kv(g.proof("ProofFeed", a, -6))
    finally:
        g.setting("titanoslimeReversible", False)
    ok = near(off["mass"], 12, 0.01) and near(on["mass"], 6, 0.01)
    row("g5", "reversible_toggle", "PASS" if ok else "FAIL", None if ok else "MOD",
        "off: mass %s stage %s | on: mass %s stage %s" % (off["mass"], off["stage"], on["mass"], on["stage"]))
    # engulfs: gate refuses when off; a mid-hold switch-off releases
    b = g.spawn(KIND, x + 6, z)[0]
    g.proof("ProofSetMass", b, 0)
    m1 = g.spawn("Muffalo", x + 8, z)[0]
    g.setting("titanoslimeEngulfs", False)
    try:
        e_off = g.proof("ProofEngulf", b, m1)
    finally:
        g.setting("titanoslimeEngulfs", True)
    e_on = g.proof("ProofEngulf", b, m1)
    g.setting("titanoslimeEngulfs", False)
    try:
        g.ticks(240)
        rel = kv(g.proof("ProofFind", re.sub(r"\D", "", m1)))
        held = g.read(b)["held"]
    finally:
        g.setting("titanoslimeEngulfs", True)
    ok = "canEngulf=False" in e_off and "canEngulf=True" in e_on and rel.get("spawned") == "True" and held == "0"
    row("g5", "engulfs_toggle_gate_and_midhold_release", "PASS" if ok else "FAIL", None if ok else "MOD",
        "off:%s on:%s | after switch-off held=%s muffalo spawned=%s" % (e_off.split()[0], e_on.split()[0], held, rel.get("spawned")))
    # sheds
    c = g.spawn(KIND, x + 12, z)[0]
    g.proof("ProofSetMass", c, 0)
    g.proof("ProofSetMass", c, 4)
    g.setting("titanoslimeSheds", False)
    try:
        # positive controls: shed==0 must not PASS blind (kind key unreadable, or the cuts never landed)
        if not any((p.get("kind") or p.get("kindDef")) == KIND for p in g.pawns()):
            raise Unmeasured("list_pawns exposes no kind/kindDef for %s: cannot count gelatids" % KIND)
        h0 = float(g.read(c)["health"])
        base = len([p for p in g.pawns() if (p.get("kind") or p.get("kindDef")) == "RM_Gelatid"])
        for _ in range(8):
            g.call("jawa/damage", damageDef="Cut", amount=12, thingId=c, armorPenetration=1.0)
        h1 = float(g.read(c).get("health", h0))
        if not h1 < h0:
            raise Unmeasured("cuts did not land (health %s -> %s): sheds-off zero proves nothing" % (h0, h1))
        shed = len([p for p in g.pawns() if (p.get("kind") or p.get("kindDef")) == "RM_Gelatid"]) - base
    finally:
        g.setting("titanoslimeSheds", True)
    ok = shed == 0
    row("g5", "sheds_toggle_off_sheds_nothing", "PASS" if ok else "FAIL", None if ok else "MOD",
        "8 x 12 Cut on a stage-2 with sheds off: %d gelatids" % shed)


@gate
def g6(g, S):
    x, z = site(S, 21)
    s = g.spawn(KIND, x, z)[0]
    g.proof("ProofSetMass", s, 0)
    r = kv(g.proof("ProofSetMass", s, 28))
    tier = g.tier(s)
    m = g.spawn("Muffalo", x + 3, z)[0]
    e = g.proof("ProofEngulf", s, m)
    if "canEngulf=True" not in e:
        raise Unmeasured("stage-4 engulf refused: %s" % e[:200])
    before = {t.get("id") for t in g.things("%d,%d,21,21" % (x - 10, z - 10))}
    k = g.proof("ProofKill", s)
    g.ticks(60)
    rel = kv(g.proof("ProofFind", re.sub(r"\D", "", m)))
    sites = g.ok("jawa/list_things", defName="RM_TitanicCorpseSite", limit=20).get("things") or []
    new_sites = [t for t in sites if t.get("id") not in before]
    ok = r["stage"] == "3" and tier == "T3" and len(new_sites) >= 1 and rel.get("spawned") == "True" and rel.get("dead") == "False"
    row("g6", "stage4_kill_corpse_site_and_held_released", "PASS" if ok else "FAIL", None if ok else "MOD",
        "stage %s bodySize %s tier %s | sites %d | muffalo spawned=%s dead=%s | %s" % (
            r["stage"], r["bodySize"], tier, len(new_sites), rel.get("spawned"), rel.get("dead"), k[:80]))


@gate
def g7(g, S):
    shots = []
    x, z = site(S, 23)
    for stage, mass in ((0, 0), (4, 60)):
        pid = g.spawn(KIND, x + stage * 3, z)[0]
        g.proof("ProofSetMass", pid, 0)
        r = kv(g.proof("ProofSetMass", pid, mass))
        pos = g.ok("jawa/list_pawns", rect="%d,%d,25,25" % (x - 10, z - 10), includeHealth=False).get("pawns") or []
        me = [p for p in pos if str(p.get("id")).replace("Thing_", "") == pid]
        px, pz = (me[0].get("x"), me[0].get("z")) if me and me[0].get("x") is not None else (x + stage * 3, z)
        for rot, nm in ((2, "south"), (1, "east"), (0, "north")):
            rr = g.call("jawa/set_pawn_rotation", pawnId=pid, dir=nm)
            if rr.get("success") is not True:
                raise Unmeasured("set_pawn_rotation %s refused: %s" % (nm, json.dumps(rr)[:200]))
            g.call("jawa/set_fog", action="unfog", rect="%d,%d,24,24" % (int(px) - 12, int(pz) - 12))
            g.call("jawa/clear_ui")
            g.call("rimworld/jump_camera_to_cell", x=int(px), z=int(pz))
            g.call("rimworld/frame_cell_rect", x=int(px) - 6, z=int(pz) - 6, width=12, height=12, paddingCells=2)
            time.sleep(1.6)
            name = "titano_g7_stage%d_%s_%s" % (stage + 1, nm, time.strftime("%H%M%S"))
            sh = g.call("rimworld/take_screenshot", fileName=name, suppressMessage=True)
            if sh.get("success") is not True or not sh.get("path"):
                raise Unmeasured("take_screenshot %s failed: %s" % (name, json.dumps(sh)[:200]))
            shots.append(sh.get("path"))
        g.call("jawa/set_pawn_rotation", pawnId=pid, dir="unlock")
        g.gone(pid)
        say("stage idx %s bodySize %s" % (r["stage"], r["bodySize"]))
    row("g7", "art_screenshots_stage1_and_5_three_facings", "UNMEASURED", None,
        "captured for judging (a look, not a state read): %s" % shots)


@gate
def g8(g, S):
    """PASSED live 2026-10-17 (BENCH, 6/6). TITANOSLIME_VANISH_DIAGNOSE_GHOST_IN_GRID: vanish leaves no ghost.
    Each case spawns a titanoslime (the generator rolls a random-age stage that is registered BEFORE the lock), sets a
    stage, optionally shrinks it while spawned, vanishes it, then reads the whole map's thingGrid for ghosts and respawns
    a Muffalo on the 9 cells around where it stood (the 2026-10-17 repro: 0-4 of 9 before the fix)."""
    g.setting("titanoslimeReversible", False)
    base = kv(g.proof("ProofGhostScan"))
    if base.get("ghosts") != "0":
        raise Unmeasured("map already holds ghosts before g8: %s" % base)
    cases = [("stage1", [0]), ("stage1", [0]), ("stage1", [0]), ("stage2", [4]), ("stage3", [12]),
             ("shrink4to1", [28, 0])]
    for i, (name, masses) in enumerate(cases):
        x, z = site(S, 24 + i)
        pid = g.spawn(KIND, x, z)[0]
        for m in masses:
            g.proof("ProofSetMass", pid, m)
        g.ticks(60)
        before = kv(g.proof("ProofGhostScan"))
        g.ok("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")
        g.ticks(5)
        after = kv(g.proof("ProofGhostScan"))
        ok_spawn, muff = 0, []
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                r = g.call("jawa/spawn_pawn", kindDef="Muffalo", x=x + dx, z=z + dz, faction="none", count=1)
                if r.get("success") is True and (r.get("pawns") or []):
                    ok_spawn += 1
                    muff.append(str(r["pawns"][0].get("id")).replace("Thing_", ""))
        for m in muff:
            g.call("jawa/pawn_force_incapacitate", pawn=m, action="kill")
        ok = before.get("ghosts") == "0" and after.get("ghosts") == "0" and ok_spawn == 9
        row("g8", "vanish_no_ghost_%s_%d" % (name, i), "PASS" if ok else "FAIL", None if ok else "MOD",
            "ghosts alive=%s after_vanish=%s %s | muffalo respawn %d/9" % (before.get("ghosts"), after.get("ghosts"),
                                                                          after.get("sample"), ok_spawn))


GATES = [g1, g2, g3, g4, g5, g6, g7, g8]
PLAYER_LOG = __import__("game_paths").PLAYER_LOG


def log_errors():
    """(lines, exception-ish lines, lines naming our mod) in Player.log; None when it cannot be read."""
    try:
        n = e = ours = 0
        for line in open(PLAYER_LOG, encoding="utf-8", errors="replace"):
            n += 1
            if "Exception" in line or line.startswith("Root level exception"):
                e += 1
            if "GelatinousSlime" in line or "Titanoslime" in line or "RM_CompEngulfer" in line:
                ours += 1
        return n, e, ours
    except OSError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--fresh", action="store_true", help="start a new quicktest map first")
    a = ap.parse_args()
    only = set(x for x in a.only.split(",") if x)
    g = G()
    S = {}
    preflight(g, S, a.fresh)
    for fn in GATES:
        if only and fn.__name__ not in only:
            continue
        fn(g, S)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    prev = []
    if only and os.path.exists(OUT):
        prev = [r for r in json.load(open(OUT)).get("rows", []) if r["gate"] not in only and r["gate"] != "pre"]
    json.dump({"mode": "partial" if only else "live", "mods": S.get("mods"), "rows": prev + ROWS,
               "when": time.strftime("%Y-%m-%dT%H:%M:%S")}, open(OUT, "w"), indent=1)
    say("wrote %s" % OUT)


if __name__ == "__main__":
    main()
