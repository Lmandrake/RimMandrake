#!/usr/bin/env python3
"""prove_tap_certificate.py - the live certification session of the scene taps (RIMMANDRAKE_BUILD_TAP_CERTIFICATE_CANARY_RUNS_OFF_STAGE).

It makes the tap certificate that tap_certificate.arm_check reads at every scene arm. Until it has run and written RESULT,
every arm reads BOOTSTRAP. Page: design/specs/2026-11-23-bridge-v2/boundary.md; core and its selftest: tap_certificate.py,
selftest_tap_certificate.py.

    python3 src/RimMandrake/rimflow/game_lock.py run ArchSmall --for "tap certificate session" -- \\
        python.exe src\\RimMandrake\\bridgetools\\prove_tap_certificate.py --host ArchSmall
    python3 src/RimMandrake/bridgetools/prove_tap_certificate.py --dry      the fixture plan, no bridge call

THE LOCK IS THE CALLER'S. This script takes no game lock: run it under game_lock.py run as above (python.exe, not WSL
python, reaches the bridge).

What it does, in order:
 1. Refuses a game that is not the TEST profile, and a canonical world save (CAMPAIGN policy; the list is
    infrastructure/state/CANONICAL_SAVE.md through Utils/canonical_saves.py). With no map it starts a quicktest map; a loaded
    map that is not canonical is used as it is. Every def that a fixture names is read back by jawa/get_def first.
 2. Identity, by reads only (tap_certificate.read_identity: jawa/running_mods, jawa/harmony_patches). Settings: for each
    foreign owner of a patch on a tapped method, the sha256 of its Config Mod_*.xml, best effort (--config, else
    RM_GAME_USERDATA/Config, else the LocalLow Config). An owner whose file it cannot find stays absent: it hashes "unread".
 3. One jawa/run_until run per fixture: the fixture's pawns are bound as the cast, its acts go in `acts`, and the run's trace
    is read from disk. A route counts as shown only when its row came with the fields that the judge names (shown_by).
 4. The blind plant: jawa/tap_fixture unpatch removes jawabench.cast from ReservationManager.Reserve at tick 0 of a reserve
    run. The reserve route must come out NOT shown, while the job_start row says the reserving job started, and
    tap_certificate.arm_check must read COULD NOT ARM with "our hook is not on". The hook comes back at the next run with a
    cast (JawaBenchCast.Join calls EnsurePatched); the script runs one and reads Harmony again. If it is still off, the log
    says: restart the game.
 5. Four rows: R1 every fixture left its record on the loaded small list; R2 NOT OWED (full-list testing is retired,
    repo CLAUDE.md, Mod development runs on small lists), with the foreign patches on each tapped method named; R3 the
    blind hook is reported; R4 the suite's wall time.
 Writes RESULT {"made", "rows", "certificate", "fixtures"} and a plain-text log beside it (tap_certificate_log.txt).
Exit: 0 every row holds, 1 a row failed, 2 unmeasured (no game, no session, a refusal before any fixture ran).
"""
import argparse
import datetime
import glob
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "rimflow"))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
sys.path.insert(0, HERE)
import tap_certificate as K  # noqa: E402

LOG = os.path.join(os.path.dirname(K.RESULT), "tap_certificate_log.txt")
LINES = []
CAST_OWNER = "jawabench.cast"
BLIND = {"tap": "reserve", "type": "Verse.AI.ReservationManager", "method": "Reserve"}
# Every def a fixture names, read back from the running game before any fixture (never guessed: the core defs of 1.6).
DEFS = [("Muffalo", "PawnKindDef"), ("Gun_Revolver", "ThingDef"), ("Goto", "JobDef"), ("Equip", "JobDef"), ("Cut", "DamageDef"),
        ("Smoke", "DamageDef"), ("ToxicBuildup", "HediffDef"), ("Wander_Sad", "MentalStateDef"), ("OpportunitySite_ItemStash", "QuestScriptDef"),
        ("Eclipse", "IncidentDef"), ("NeutralEvent", "MessageTypeDef"), ("NeutralEvent", "LetterDef")]
QUEST, MENTAL, INCIDENT = "OpportunitySite_ItemStash", "Wander_Sad", "Eclipse"


def log(s):
    LINES.append(s)
    print(s, flush=True)


# ------------------------------------------------------------------------------------------------ the fixtures
def act(tool, tick, **args):
    return {"tool": tool, "at": tick, "args": args}


def gun(c, i):
    return c["guns"][i]


def fixtures(c):
    """c: the stage (A, B, Ax, Az, beasts[5], guns[3], sizeX, sizeZ, t0 tag). -> the fixture list. Each judge gets
    (rows, reply, extra) and returns {route: evidence or None}: a route is shown only by non-None evidence."""
    A, B, ax, az = c["A"], c["B"], c["Ax"], c["Az"]
    m = c["beasts"]
    tag = c["tag"]
    return [
        {"name": "job", "taps": {"job_start": ["ordered", "think_tree"], "job_end": ["interrupted", "succeeded"]},
         "bind": {"jA": A}, "ticks": 700,
         "acts": [act("jawa/ordered_job", 0, pawnId=A, jobDef="Goto", targetAX=ax + 5, targetAZ=az, waitTicks=0),
                  act("jawa/ordered_job", 30, pawnId=A, jobDef="Goto", targetAX=ax + 8, targetAZ=az + 3, waitTicks=0)],
         "judge": judge_job},
        {"name": "reserve", "taps": {"reserve": ["made", "refused"]}, "bind": {"rA": A, "rB": B}, "ticks": 300,
         "acts": [act("jawa/ordered_job", 1, pawnId=A, jobDef="Equip", targetAId=gun(c, 0), waitTicks=0),
                  act("jawa/ordered_job", 1, pawnId=B, jobDef="Equip", targetAId=gun(c, 0), waitTicks=0)],
         "judge": judge_reserve},
        {"name": "blind", "taps": {}, "bind": {"rB": B}, "ticks": 300, "blind": True,
         "acts": [act("jawa/tap_fixture", 0, action="unpatch", typeName=BLIND["type"], methodName=BLIND["method"], owner=CAST_OWNER),
                  act("jawa/ordered_job", 1, pawnId=B, jobDef="Equip", targetAId=gun(c, 1), waitTicks=0)],
         "judge": judge_blind},
        {"name": "kill", "taps": {"kill": ["by_damage", "by_hediff"]}, "bind": {"kD": m[1], "kH": m[2]}, "ticks": 300,
         "acts": [act("jawa/damage", 0, damageDef="Cut", amount=5000, thingId=m[1], armorPenetration=9, bodyPart="Body"),
                  act("jawa/pawn_health", 0, pawn=m[2], action="add", hediff="ToxicBuildup", severity=1.0, confirmDestructive=True)],
         "judge": judge_kill, "unbind_after": True},
        {"name": "mental", "taps": {"mental": ["started", "refused"]}, "bind": {"mB": B}, "ticks": 40,
         "acts": [act("jawa/pawn_mental", 0, pawn=B, action="start", state=MENTAL),
                  act("jawa/pawn_mental", 2, pawn=B, action="start", state=MENTAL),
                  act("jawa/pawn_mental", 20, pawn=B, action="end")],
         "judge": judge_mental},
        {"name": "gate_mental", "taps": {"gate.mental": ["allowed", "held"]}, "bind": {"mB": B}, "ticks": 40,
         "acts": [act("jawa/scene_gate", 0, action="arm", kind="mental", allow=MENTAL),
                  act("jawa/pawn_mental", 1, pawn=B, action="start", state=MENTAL),
                  act("jawa/pawn_mental", 3, pawn=B, action="end"),
                  act("jawa/pawn_mental", 5, pawn=B, action="start", state=MENTAL),
                  act("jawa/scene_gate", 7, action="release", kind="mental", why="tap certificate fixture done")],
         "judge": judge_gate("mental")},
        {"name": "quest", "taps": {"quest": ["added", "already_there"]}, "bind": {}, "ticks": 20,
         "acts": [act("jawa/fire_quest", 0, questDef=QUEST, points=500.0),
                  act("jawa/tap_fixture", 1, action="quest_add_again", questId=-1)],
         "judge": judge_quest},
        {"name": "gate_quest", "taps": {"gate.quest": ["allowed", "held"]}, "bind": {}, "ticks": 20,
         "acts": [act("jawa/scene_gate", 0, action="arm", kind="quest", allow=QUEST),
                  act("jawa/fire_quest", 1, questDef=QUEST, points=500.0),
                  act("jawa/fire_quest", 2, questDef=QUEST, points=500.0),
                  act("jawa/scene_gate", 3, action="release", kind="quest", why="tap certificate fixture done")],
         "judge": judge_gate("quest")},
        {"name": "letter", "taps": {"letter": ["shown", "queued"]}, "bind": {}, "ticks": 20, "tag": tag,
         "acts": [act("jawa/letter_send_delayed", 0, label="tapcert shown " + tag, text="tap certificate fixture", textLetterDef="NeutralEvent",
                      delayTicks=0, playSound=False),
                  act("jawa/letter_send_delayed", 0, label="tapcert queued " + tag, text="tap certificate fixture", textLetterDef="NeutralEvent",
                      delayTicks=600, playSound=False)],
         "judge": judge_letter},
        {"name": "message", "taps": {"message": ["shown", "hidden_repeat"]}, "bind": {}, "ticks": 10, "tag": tag,
         "acts": [act("jawa/static_call", 0, type="Verse.Messages", method="Message", args="tapcert message %s|NeutralEvent|false" % tag),
                  act("jawa/static_call", 0, type="Verse.Messages", method="Message", args="tapcert message %s|NeutralEvent|false" % tag)],
         "judge": judge_message},
        {"name": "fire", "taps": {"fire": ["by_pawn", "by_thing"]}, "bind": {}, "ticks": 20,
         "acts": [act("jawa/tap_fixture", 0, action="fire_attach", thingId=m[3], instigatorId=A, size=0.5),
                  act("jawa/tap_fixture", 0, action="fire_attach", thingId=m[4], instigatorId=gun(c, 2), size=0.5),
                  act("jawa/map_fire", 5, action="extinguish", rect="0,0,%d,%d" % (c["sizeX"], c["sizeZ"]))],
         "judge": judge_fire},
        {"name": "explosion", "taps": {"explosion": ["with_instigator", "no_instigator"]}, "bind": {}, "ticks": 20,
         "acts": [act("jawa/tap_fixture", 0, action="explode", cell="%d,%d" % (ax + 4, az - 4), radius=1.9, damType="Smoke", instigatorId=A),
                  act("jawa/explosion_at", 0, at="%d,%d" % (ax - 4, az - 4), radius=1.9, damType="Smoke")],
         "judge": judge_explosion},
        {"name": "incident", "taps": {"incident": ["fired", "held"]}, "bind": {}, "ticks": 20, "journal": True,
         "acts": [act("jawa/fire_incident", 0, incidentDef=INCIDENT, forced=True),
                  act("jawa/scene_gate", 1, action="arm", kind="incident", allow=""),
                  act("jawa/fire_incident", 2, incidentDef=INCIDENT, forced=True),
                  act("jawa/scene_gate", 3, action="release", kind="incident", why="tap certificate fixture done")],
         "judge": judge_incident},
    ]


def recs(rows, rec, **kw):
    return [r for r in rows if r.get("rec") == rec and all(r.get(k) == v for k, v in kw.items())]


def first(xs, *keys):
    """The first row as evidence: its rec, seq and the named fields."""
    if not xs:
        return None
    r = xs[0]
    return dict({"rec": r.get("rec"), "seq": r.get("seq")}, **{k: r.get(k) for k in keys})


def judge_job(rows, rep, x):
    s = recs(rows, "job_start", alias="jA")
    e = recs(rows, "job_end", alias="jA")
    tree = [r for r in recs(rows, "job_start") if r.get("giver") not in (None, "", "player", "queue", "direct")]
    return {("job_start", "ordered"): first([r for r in s if r.get("giver") == "player" and r.get("def") == "Goto"], "alias", "def", "giver"),
            ("job_start", "think_tree"): first(tree, "alias", "def", "giver"),
            ("job_end", "interrupted"): first([r for r in e if r.get("cond") == "InterruptForced"], "alias", "def", "cond"),
            ("job_end", "succeeded"): first([r for r in e if r.get("cond") == "Succeeded"], "alias", "def", "cond")}


def judge_reserve(rows, rep, x):
    r = recs(rows, "reserve")
    return {("reserve", "made"): first([y for y in r if y.get("made") is True and y.get("target")], "alias", "target", "made"),
            ("reserve", "refused"): first([y for y in r if y.get("made") is False and y.get("holder")], "alias", "target", "made", "holder")}


def judge_blind(rows, rep, x):
    """The planted fault: Reserve ran (B's Equip job started) and no reserve row came."""
    started = [r for r in recs(rows, "job_start", alias="rB") if r.get("def") == "Equip"]
    unp = [a for a in rep.get("acts") or [] if (a.get("reply") or {}).get("action") == "unpatch"]
    return {"reserve_rows": len(recs(rows, "reserve")), "reached": first(started, "alias", "def", "giver"),
            "unpatched": [(a.get("state"), (a.get("reply") or {}).get("unpatched")) for a in unp]}


def judge_kill(rows, rep, x):
    k = recs(rows, "kill")
    return {("kill", "by_damage"): first([r for r in k if r.get("alias") == "kD" and r.get("culprit") in ("damage Cut", "hediff Cut")], "alias", "culprit"),
            ("kill", "by_hediff"): first([r for r in k if r.get("alias") == "kH" and r.get("culprit") == "hediff ToxicBuildup"], "alias", "culprit")}


def judge_mental(rows, rep, x):
    a = [r for r in recs(rows, "mental_attempt", alias="mB") if r.get("state") == MENTAL]
    st = [r for r in recs(rows, "mental_start") if r.get("state") == MENTAL]
    return {("mental", "started"): first([r for r in a if r.get("started") is True], "alias", "state", "started") if st else None,
            ("mental", "refused"): first([r for r in a if r.get("started") is False], "alias", "state", "started", "reason")}


def judge_gate(kind):
    def j(rows, rep, x):
        g = recs(rows, "gate", gate=kind)
        return {("gate." + kind, "allowed"): first([r for r in g if r.get("outcome") == "allowed"], "gate", "outcome", "name"),
                ("gate." + kind, "held"): first([r for r in g if r.get("outcome") == "held"], "gate", "outcome", "name")}
    j.__name__ = "judge_gate_" + kind
    return j


def judge_quest(rows, rep, x):
    q = [r for r in recs(rows, "quest") if r.get("root") == QUEST]
    return {("quest", "added"): first([r for r in q if r.get("added") is True], "quest", "root", "added"),
            ("quest", "already_there"): first([r for r in q if r.get("refused") == "already there"], "quest", "root", "refused")}


def judge_letter(rows, rep, x):
    tag = x["tag"]
    lt = recs(rows, "letter")
    return {("letter", "shown"): first([r for r in lt if r.get("label") == "tapcert shown " + tag and r.get("shown") is True], "label", "shown", "queued"),
            ("letter", "queued"): first([r for r in lt if r.get("label") == "tapcert queued " + tag and r.get("queued") is True], "label", "shown", "queued", "delay")}


def judge_message(rows, rep, x):
    ms = [r for r in recs(rows, "message") if r.get("text") == "tapcert message " + x["tag"]]
    return {("message", "shown"): first([r for r in ms if r.get("shown") is True], "text", "shown"),
            ("message", "hidden_repeat"): first([r for r in ms if r.get("shown") is False and r.get("hidden")], "text", "shown", "hidden")}


def judge_fire(rows, rep, x):
    f = recs(rows, "fire")
    return {("fire", "by_pawn"): first([r for r in f if r.get("instigatorKind") == "pawn" and r.get("attached")], "attached", "instigator", "instigatorKind"),
            ("fire", "by_thing"): first([r for r in f if r.get("instigatorKind") == "thing" and r.get("attached")], "attached", "instigator", "instigatorKind")}


def judge_explosion(rows, rep, x):
    e = [r for r in recs(rows, "explosion") if r.get("damage") == "Smoke"]
    return {("explosion", "with_instigator"): first([r for r in e if r.get("instigatorKind") == "pawn" and r.get("instigator")], "cell", "instigator", "instigatorKind"),
            ("explosion", "no_instigator"): first([r for r in e if r.get("instigatorKind") == "none" and not r.get("instigator")], "cell", "instigator", "instigatorKind")}


def judge_incident(rows, rep, x):
    """The incident tap is the awareness prefix on IncidentWorker.TryExecute: its record is the incident journal (x["journal"]),
    and its held route is the gate row of the incident gate that sits on that prefix."""
    j = [r for r in x.get("journal") or [] if r.get("def") == INCIDENT]
    fired = [r for r in j if r.get("workerEntered") is True or r.get("returned") is True]
    held = [r for r in recs(rows, "gate", gate="incident") if r.get("outcome") == "held"]
    jheld = [r for r in j if r.get("workerEntered") is False and "gate" in str(r.get("workerEnteredWhy") or "")]
    ev = first(held, "gate", "outcome", "name")
    if ev is not None:
        ev["journal"] = first(jheld, "aseq", "def", "workerEntered", "workerEnteredWhy")
    return {("incident", "fired"): (dict(first(fired, "aseq", "def", "workerEntered", "returned"), rec="incident_journal") if fired else None),
            ("incident", "held"): ev}


# ------------------------------------------------------------------------------------------------ dry plan
def placeholder_stage():
    return {"A": "Human_A", "B": "Human_B", "Ax": 100, "Az": 100, "beasts": ["Muffalo_%d" % i for i in range(5)],
            "guns": ["Gun_Revolver_%d" % i for i in range(3)], "sizeX": 250, "sizeZ": 250, "tag": "T0"}


def plan_check(fx):
    """-> problems: a TAPS route that no fixture shows, an act tool outside ACT_TOOLS, an arm read used as an act."""
    bad = []
    planned = {}
    for f in fx:
        for tap, routes in f["taps"].items():
            planned.setdefault(tap, set()).update(routes)
        for a in f["acts"]:
            if a["tool"] not in K.ACT_TOOLS:
                bad.append("%s: act tool %s is not in tap_certificate.ACT_TOOLS" % (f["name"], a["tool"]))
            if a["tool"] in K.ARM_READS:
                bad.append("%s: act tool %s is an arm read" % (f["name"], a["tool"]))
    for tap, t in K.TAPS.items():
        miss = [r for r in t["routes"] if r not in planned.get(tap, ())]
        if miss:
            bad.append("tap %s: no fixture shows %s" % (tap, ", ".join(miss)))
    for tap in planned:
        if tap not in K.TAPS:
            bad.append("fixture names tap %s that TAPS does not hold" % tap)
    if set(K.ACT_TOOLS) & set(K.ARM_READS):
        bad.append("ACT_TOOLS holds an arm read")
    return bad


def dry():
    fx = fixtures(placeholder_stage())
    for f in fx:
        print("fixture %-11s ticks %-4d cast %s" % (f["name"], f["ticks"], ",".join("%s=%s" % kv for kv in f["bind"].items()) or "-"))
        for a in f["acts"]:
            print("   at %-3d %-24s %s" % (a["at"], a["tool"], json.dumps(a["args"], sort_keys=True)))
        print("   shows %s" % ("; ".join("%s: %s" % (t, "/".join(r)) for t, r in f["taps"].items()) or "the blind plant (reserve, %s.%s)" % (BLIND["type"], BLIND["method"])))
    bad = plan_check(fx)
    n = sum(len(t["routes"]) for t in K.TAPS.values())
    print("plan: %d fixtures, %d runs (+1 restore run), %d taps, %d routes planned of %d; problems %d" % (
        len(fx), len(fx), len(K.TAPS), n - sum(1 for b in bad if b.startswith("tap ")), n, len(bad)))
    for b in bad:
        print("PROBLEM " + b)
    return 1 if bad else 0


# ------------------------------------------------------------------------------------------------ the live session
def connect(game):
    """The bridge of the named game (as scene_world.RealBridge), or the default endpoint when none is named."""
    import prove_scene_tick_wiring as W
    import rimbridge_client as rb
    if not game:
        W.connect()
        return W
    import game_names
    import game_instance as gi
    k = game_names.name_key(game) or game_names.key(game)
    letter = game_names.letter(k) if k else None
    if not letter:
        raise SystemExit("UNMEASURED: no game named %r" % game)
    os.environ.update(gi.env(letter))
    if letter == gi.DEFAULT:
        for v in ("RM_GAME_INSTANCE", "RIMFLOW_DRIVER_LOCK", "GABP_SERVER_PORT", "GABP_TOKEN", "RM_GAME_USERDATA", "RM_GAME_LOGDIR"):
            os.environ.pop(v, None)
        host, port, token = rb.resolve_endpoint()
    else:
        host, port, token = "127.0.0.1", gi.port(letter), gi.read_token(letter)
    if not token:
        raise SystemExit("UNMEASURED: no bridge token for %s: it is not up" % game)
    W.S[0] = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
    W.S[0].connect()
    return W


def config_dir(arg):
    if arg:
        return arg
    ud = os.environ.get("RM_GAME_USERDATA")
    if ud:
        return os.path.join(ud, "Config")
    la = os.environ.get("LOCALAPPDATA")
    if la:
        return os.path.join(os.path.dirname(la), "LocalLow", "Ludeon Studios", "RimWorld by Ludeon Studios", "Config")
    return None


def settings_of(identity, cdir):
    """{foreign owner: sha256 of its Mod_*.xml} for the owners that a file names (by patch assembly or the owner's last
    segment). An owner with no file, or two candidate files, stays absent (it hashes "unread"): no guess."""
    out, notes = {}, []
    files = sorted(glob.glob(os.path.join(cdir, "Mod_*.xml"))) if cdir and os.path.isdir(cdir) else []
    if not files:
        return out, ["no Config Mod_*.xml read at %s: every foreign owner hashes unread" % cdir]
    asm = {}
    for rows in K.foreign_patches(identity.get("inventory") or {}).values():
        for r in rows:
            if r.get("owner"):
                asm.setdefault(r["owner"], set()).add(r.get("patchAssembly") or "")
    for owner in K.foreign_owners(identity.get("inventory") or {}):
        keys = {k.lower() for k in asm.get(owner, ()) if k} | {owner.split(".")[-1].lower()}
        keys = {k for k in keys if len(k) >= 4}
        hit = [p for p in files if any(k in os.path.basename(p).lower() for k in keys)]
        if len(hit) == 1:
            with open(hit[0], "rb") as f:
                out[owner] = "sha256:" + hashlib.sha256(f.read()).hexdigest()
            notes.append("settings %s <- %s" % (owner, os.path.basename(hit[0])))
        else:
            notes.append("settings %s unread (%d candidate files)" % (owner, len(hit)))
    return out, notes


def source_sha():
    try:
        return subprocess.run(["git", "-C", K.REPO, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=20).stdout.strip() or None
    except Exception:  # noqa: BLE001 - the sha is a label; no git on the path leaves it absent
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--host", default=None, help="the game by name (ArchSmall, ArchBig); none = the default endpoint")
    ap.add_argument("--dry", action="store_true", help="print the fixture plan and check it against TAPS; no bridge call")
    ap.add_argument("--config", default=None, help="the game's Config folder, for the settings hashes")
    a = ap.parse_args(argv)
    if a.dry:
        return dry()
    if plan_check(fixtures(placeholder_stage())):
        print("UNMEASURED: the fixture plan does not cover TAPS; run --dry")
        return 2

    W = connect(a.host)
    import prove_run_until as R
    import canonical_saves
    t_start = time.time()
    log("tap certificate session %s on %s, driver %s" % (datetime.datetime.now().isoformat(timespec="seconds"), a.host or "default", R.DRIVER))

    def read(tool, args):
        return W.call(tool, **args)

    # 1. refusals and the stage
    hs = W.call("jawa/companion_handshake")
    if str(hs.get("effectiveProfile") or "").lower() != "test":
        log("REFUSED: the companion's effective profile is %r, not test (CAMPAIGN policy): %s" % (hs.get("effectiveProfile"), R.brief(hs)))
        return 2
    names, starts = canonical_saves.read(K.REPO)
    g = hs.get("game") or {}
    save = g.get("save")
    if save and (save in names or any(save.startswith(s) for s in starts)):
        log("REFUSED: the loaded save %r is canonical (CAMPAIGN policy); load a test map or none" % save)
        return 2
    if g.get("programState") != "Playing":
        if not R.start_map():
            log("UNMEASURED: no quicktest map")
            return 2
        g = (W.call("jawa/companion_handshake").get("game") or {})
        save = g.get("save")
        if save and (save in names or any(save.startswith(s) for s in starts)):
            log("REFUSED: the map that came up is the canonical save %r" % save)
            return 2
    log("stage: save %r, map %s, tick %s" % (save, g.get("currentMapId"), g.get("ticksGame")))
    missing = []
    for d, ty in DEFS:
        r = W.call("jawa/get_def", defName=d, defType=ty)
        if not r.get("success", False) or r.get("error"):
            missing.append("%s %s: %s" % (ty, d, R.brief(r)))
    if missing:
        log("UNMEASURED: a fixture def is not in this game: %s" % "; ".join(missing))
        return 2

    # 2. identity
    ident0 = K.read_identity(read)
    if ident0 is None:
        log("UNMEASURED: the loaded identity could not be read")
        return 2
    settings, notes = settings_of(ident0, config_dir(a.config))
    for n in notes:
        log(n)
    ident0 = K.read_identity(read, settings)
    log("identity: companion %s, modlist %s, foreign owners %s" % (ident0["companion"], ident0["modlist"], K.foreign_owners(ident0["inventory"])))

    R.open_session(lease=120)
    W.call("jawa/scene_gate", action="release", kind="", why="tap certificate session start")
    try:
        stage = make_stage(W, R)
        if stage is None:
            return 2
        shown, results, blind = {}, [], None
        bound = set()
        for f in fixtures(stage):
            res, bound = run_fixture(W, R, f, bound)
            results.append(res)
            for (tap, route), ev in (res.get("routes") or {}).items():
                if ev is not None:
                    shown.setdefault(tap, []).append(route)
            if f.get("blind"):
                blind = blind_verdict(W, R, read, ident0, shown, settings, res, stage, bound)
                bound = set(blind.pop("_bound"))
            log("fixture %-11s %s" % (f["name"], res["line"]))
    finally:
        W.call("jawa/scene_gate", action="release", kind="", why="tap certificate session end")
        R.end_session("close")

    # 3. the certificate, on the identity read after the session (the one it is valid for)
    ident1 = K.read_identity(read, settings)
    if ident1 is None:
        log("UNMEASURED: the identity could not be read after the session")
        return 2
    if K.key_of(ident1) != K.key_of(ident0):
        log("NOTE: the certificate key changed during the session: before %s, after %s" % (K.key_of(ident0), K.key_of(ident1)))
    suite_ms = int((time.time() - t_start) * 1000)
    cert = K.make(ident1, shown, blind, game=a.host, suite_ms=suite_ms, source_sha=source_sha())
    rows = four_rows(cert, results, blind, suite_ms)
    for r in rows:
        log("%s %-8s %s" % (r["row"], r["verdict"], r["detail"]))
    res = {"made": datetime.datetime.now().isoformat(timespec="seconds"), "rows": rows, "certificate": cert,
           "fixtures": [{k: v for k, v in x.items() if k != "routes"} for x in results]}
    os.makedirs(os.path.dirname(K.RESULT), exist_ok=True)
    with open(K.RESULT, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, sort_keys=True, default=str)
    rc, line = K.audit(K.RESULT)
    log("audit: %s" % line)
    with open(LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(LINES) + "\n")
    print("wrote %s and %s" % (K.RESULT, LOG))
    return 0 if rc == 0 and all(r["verdict"] in ("PASS", "NOT OWED") for r in rows) else 1


def colonists(W):
    out = []
    for p in W.call("jawa/pawn_get", limit=200).get("pawns") or []:
        if p.get("faction") != "PlayerColony":
            continue
        x, z = p.get("x"), p.get("z")
        if x is None and isinstance(p.get("position"), dict):
            x, z = p["position"].get("x"), p["position"].get("z")
        if p.get("thingId") and x is not None:
            out.append((p["thingId"], int(x), int(z)))
    return out


def xz_of(t):
    if t.get("x") is not None:
        return int(t["x"]), int(t["z"])
    p = t.get("position")
    if isinstance(p, dict):
        return int(p.get("x")), int(p.get("z"))
    if isinstance(p, str) and "," in p:
        bits = [int(v) for v in p.strip("() ").split(",")]
        return bits[0], bits[-1]
    return None


def make_stage(W, R):
    mi = W.call("jawa/map_info")
    col = colonists(W)
    if len(col) < 2 or not mi.get("sizeX"):
        log("UNMEASURED: the map needs two colonists and a size: %d colonists, %s" % (len(col), R.brief(mi)))
        return None
    (A, ax, az), (B, _, _) = col[0], col[1]
    sx, sz = int(mi["sizeX"]), int(mi["sizeZ"])
    ax, az = min(max(ax, 12), sx - 13), min(max(az, 12), sz - 13)       # every fixture cell is within 10 of A
    beasts = []
    for i in range(5):
        bid, r = R.animal(ax - 2 + 2 * i, az - 6)
        if not bid:
            log("UNMEASURED: no Muffalo at %d,%d: %s" % (ax - 2 + 2 * i, az - 6, R.brief(r)))
            return None
        beasts.append(bid)
    cells = [(ax + 1 + i, az + 2) for i in range(3)]
    W.call("jawa/spawn_batch", ops=";".join("Gun_Revolver:%d,%d,1" % c for c in cells))
    guns = []
    things = W.call("jawa/list_things", defName="Gun_Revolver", limit=200).get("things") or []
    for c in cells:
        hit = [t.get("id") for t in things if xz_of(t) == c]
        if not hit:
            log("UNMEASURED: no Gun_Revolver came at %d,%d" % c)
            return None
        guns.append(hit[0])
    st = {"A": A, "B": B, "Ax": ax, "Az": az, "beasts": beasts, "guns": guns, "sizeX": sx, "sizeZ": sz, "tag": str(R.tick())}
    log("stage made: A %s, B %s at %d,%d; beasts %s; guns %s" % (A, B, ax, az, beasts, guns))
    return st


def run_fixture(W, R, f, bound):
    """One jawa/run_until run. -> ({name, run, why, acts, routes, line}, the aliases bound after it)."""
    binds = {k: None for k in bound if k not in f["bind"]}
    binds.update(f["bind"])
    if binds:
        W.call("jawa/session", action="bind", driver=R.DRIVER, bindings=json.dumps(binds))
    bound = set(f["bind"])
    jseq = None
    if f.get("journal"):
        j = W.call("jawa/incident_journal", sinceSeq=-1, limit=1).get("rows") or []
        jseq = max([r.get("aseq") or 0 for r in j] or [0])
    acts = [dict(x, id=R.req("%s_%d" % (f["name"], i))) for i, x in enumerate(f["acts"])]
    t0 = R.tick() or 0
    rep = R.run(R.at_tick(t0 + f["ticks"]), f["ticks"] + 200, acts=acts)
    st = W.call("jawa/session", action="state")
    rows = W.read_trace({"recordDir": st.get("recordDir"), "session": st.get("writerSession") or st.get("session"), "run": rep.get("run")}, 15) if rep.get("run") else []
    extra = {"tag": f.get("tag")}
    if jseq is not None:
        extra["journal"] = W.call("jawa/incident_journal", sinceSeq=jseq, limit=50).get("rows") or []
    routes = f["judge"](rows, rep, extra)
    acts_out = [{"id": x.get("id"), "tool": x.get("tool"), "state": x.get("state")} for x in rep.get("acts") or []]
    not_done = [x for x in acts_out if x["state"] != "done"]
    res = {"name": f["name"], "run": rep.get("run"), "why": rep.get("why"), "rows": len(rows), "acts": acts_out}
    if f.get("blind"):
        res["blind"] = routes
        line = "run %s %s, %d rows; reserve rows %d, Equip started %s, unpatch %s" % (rep.get("run"), rep.get("why"), len(rows), routes["reserve_rows"],
                                                                                    bool(routes["reached"]), routes["unpatched"])
    else:
        res["routes"] = routes
        res["shown"] = {"%s.%s" % k: v for k, v in routes.items()}
        line = "run %s %s, %d rows; %s" % (rep.get("run"), rep.get("why") or R.brief(rep), len(rows),
                                           ", ".join("%s.%s %s" % (k[0], k[1], "shown" if v else "NOT SHOWN") for k, v in routes.items()))
    if not_done:
        line += "; acts not done: %s" % ", ".join("%s %s" % (x["id"], x["state"]) for x in not_done)
        res["acts_reply"] = [{"id": x.get("id"), "state": x.get("state"), "reply": x.get("reply")} for x in rep.get("acts") or [] if x.get("state") != "done"]
    res["line"] = line
    if f.get("unbind_after"):
        W.call("jawa/session", action="bind", driver=R.DRIVER, bindings=json.dumps({k: None for k in bound}))
        bound = set()
    return res, bound


def blind_verdict(W, R, read, ident, shown, settings, res, stage, bound):
    """After the blind run: arm_check must say blind. Then the restore run (a cast run re-patches) and a Harmony read."""
    b = res["blind"]
    cert = K.make(ident, shown, None)
    arm = K.arm_check(cert, read, ["reserve.made"], settings)
    hook_off = any("our hook is not on" in r for r in arm.get("reasons") or [])
    reported = (b["reserve_rows"] == 0 and b["reached"] is not None and arm.get("verdict") == K.COULD_NOT_ARM
                and arm.get("routes", {}).get("reserve.made") == "blind" and hook_off)
    res["arm"] = {k: arm.get(k) for k in ("verdict", "routes", "reasons")}
    W.call("jawa/session", action="bind", driver=R.DRIVER, bindings=json.dumps(dict({k: None for k in bound if k != "rB"}, rB=stage["B"])))
    t0 = R.tick() or 0
    R.run(R.at_tick(t0 + 2), 50)
    rows = K._patches_of(read, BLIND["type"], BLIND["method"]) or []
    restored = any(r.get("owner") == CAST_OWNER for r in rows)
    log("blind: arm %s %s; reported %s; hook restored %s%s" % (arm.get("verdict"), arm.get("reasons"), reported, restored,
                                                             "" if restored else " - RESTART THE GAME: the reserve tap stays off"))
    return {"tap": BLIND["tap"], "method": "%s.%s" % (BLIND["type"], BLIND["method"]), "reported": bool(reported), "restored": restored,
            "_bound": ["rB"]}


def four_rows(cert, results, blind, suite_ms):
    cov = K.coverage(cert)
    miss = ["%s.%s" % (t, r) for t, c in sorted(cov.items()) for r in c["not_shown"]]
    n = sum(len(c["covered"]) for c in cov.values())
    tot = n + len(miss)
    r1 = {"row": "R1", "verdict": "PASS" if not miss else "FAIL",
          "detail": "every fixture left its record on the loaded small list: %d of %d routes shown (worst: %s; limit: all; %d fixtures read)" % (
              n, tot, ", ".join(miss) or "none missing", len(results))}
    names = []
    for tap, t in sorted((cert.get("taps") or {}).items()):
        for f in t.get("foreign") or []:
            names.append("%s %s %s" % (f.get("method"), f.get("kind"), f.get("owner")))
    names = sorted(set(names))
    r2 = {"row": "R2", "verdict": "NOT OWED",
          "detail": "full-list testing is retired (repo CLAUDE.md, Mod development runs on small lists); foreign patches on the tapped methods: %s" % (
              "; ".join(names) or "none")}
    ok3 = bool(blind and blind.get("reported"))
    r3 = {"row": "R3", "verdict": "PASS" if ok3 else "FAIL",
          "detail": "the blind hook (%s) is reported: %s; restored %s" % ((blind or {}).get("method"), ok3, (blind or {}).get("restored"))}
    r4 = {"row": "R4", "verdict": "PASS", "detail": "suite wall time %.1f s over %d fixture runs" % (suite_ms / 1000.0, len(results))}
    return [r1, r2, r3, r4]


if __name__ == "__main__":
    sys.exit(main())
