"""Live proofs of the built pipeline:bridge tickets (work bundle WB-pipeline-bridge-20261125-192133), one clause per call:

    python.exe src/RimMandrake/Utils/modcheck/live_queue/bridge_bundle_proof.py <CLAUSE>

Runs on the CURRENT map through the bridge (Session focus=False), removes what it spawns, and prints one
"<clause> PASS|FAIL|UNMEASURED: ..." line. Exit 0 = holds, 1 = it answered and something is wrong, 2 = UNMEASURED.
Any non-canonical game will do; the test lane's games are disposable.

  EVIDENCE   BRIDGE_CALL_EVIDENCE_WIRE_LOST_REPLY_UNKNOWN A1: every call of this python.exe session writes a start row
             and an end row to the bridge call evidence log, and no in-flight marker of this process is left
  TPS        BRIDGE_TPS_REGULAR_REPORT_1 C2: 60 real seconds at speed 1 -> the record segment grows, jawa/tps_report
             returns the last windows at a ~5 s cadence with min/median/max, median ratio near 1 (60 tps)
  NORTHSTAR  NORTHSTAR_COMPANION_GAPS_1 A2: pawn_census, pawn_roles, incident_queue_peek, incident_queue_remove (dry
             run changes nothing), damage_log (a damage we deal is logged), thing_lineage (the victim is found)
  STATICCALL STATIC_CALL_THINGID_FIX_DIGIT_EATS_ITSELF A1 (live half): static_call GenAdj.OccupiedRect resolves a whole
             ThingID and a bare id number of a live pawn
  TILECACHE  TILE_TEMP_CACHE_RESET_TOOL_1 A1: retile one far tile's temperature -> world_cache_audit includeTemps
             reads it stale, world_tile_cache_reset returns verifiedNull, a re-audit reads it fresh (restored after)
  PROFILE    COMPANION_PROFILE_ENFORCE_SAFE_BY_DEFAULT A1+A2: no profile file -> effectiveProfile campaign, spawn_pawn
             runs, static_call refuses; the test file back -> test within 2 s (the file is restored in every case)
  PEN        PEN_ANIMALS_UNSTICK_STATUES_LEARN_TO_WALK A1: animals given a Wait pin are released (released ==
             selected, no Wait after), re-pinned with return home
  EXPLAIN    THING_LOOKUP_BUILD_OWNER_IS_NOT_PAINTER A3: an ambiguous cell or name lists candidates and picks none;
             a vanished id is refused
  HOOKS      TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS A1+A2: after PLAY minutes of play (env BUNDLE_PLAY_MINUTES,
             default 10) every TPS and attribution hook reads coverage ok, with no hook fault or foreign-thread reject
  AWARE      AWARENESS_GENPAWN_TAME_ARM_BEFORE_USE A1 (test-profile half): with no install.generation-early the
             GeneratePawn hook is not installed until an arm, and the arm installs it
  EPOCH      BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD A1+A2: save, reload the same save -> a call with the old
             expectGameEpoch is refused, an absent expectMapId is refused, the current values pass; a wild-spawner
             block reads lastRelease new-game after the load, and expired after a short TTL
  FRAME      RIMMANDRAKE_REPAIR_FRAME_HIST_READS_THREE_WAYS_WRONG: after a load, jawa/health's frame-hist session and
             merged strings parse as JSON, an arm starts the session fresh, and 5 s later it holds only those frames
             (no late-merged load frames). Run after EPOCH: it reloads the save EPOCH wrote
  ORIGIN     PAWN_ORIGIN_BUILD_SAY_ORIGIN_UNKNOWN A2: awareness_settings.json set to install.generation-early, a cold
             launch (launch_ready.py), then the first call reads startedBy bridge-registration and the first map's wild
             animals read a mapgen > wild-spawner chain. The file is restored in every case; the early hook stays
             until the next launch (AWARE reads that game as a precondition, not a FAIL)
  WILDBLOCK  THING_LOOKUP_BUILD_OWNER_IS_NOT_PAINTER A4: wild_spawner_block block reads back blocked, skippedTicks rises
             by every spawner tick over 1213+ ticks, and release restores it (no tick skipped after)
  PLAYTEST   RIMMANDRAKE_PROVE_COMPANION_REFUSALS_THE_MINIMAL_LIST_CANNOT (1): jawa/playtest_start and
             jawa/gss_playtest_start refuse each other while one runs (needs FlowWorks + Gimme Some Slack: tier
             ratchet_pilot; it modifies the scratch map)
  CAMPAIGN   the same item (2): under the CAMPAIGN profile (a loaded disposable save, the profile file set, restored
             after) artboard_stage killHostiles=true and mod_settings_field set refuse by the profile
  SETTLE     the same item (5): world_settlements_import apply clearExisting with a row on the player's mapped tile
             refuses "REFUSING before clearing" and the settlement count is unchanged (python.exe: the game reads the CSV)
  PEN2       PEN_ANIMALS_UNSTICK_STATUES_LEARN_TO_WALK A2: the newest RM_pyre_review_*.rws in <data root>/fixtures is
             copied in as bundle_pen2_review and loaded (tier pyrelands); human_review.py's --release-pens call releases
             every pen specimen; after 600 ticks at least half have moved and each is inside its pen; its --pin-pens
             call brings every one home and restores the facing it was released with
  KEEPER     KEEPER_SAVES_HARDEN_WRONG_SLOT_WRITES A1: save_guard.snapshot on this game's real Saves folder hashes every
             keeper and holds a store copy of each; a save_base through the guard writes a new save, verified, with no
             keeper changed (the new save is deleted after: it is the proof's own)
PROFILE needs a loaded save (with none loaded the companion reads test by design): run it after EPOCH.
"""
SAVE = "bundle_wb_bridge_epoch"
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CLAUSES = ("EVIDENCE", "TPS", "NORTHSTAR", "STATICCALL", "TILECACHE", "PROFILE", "PEN", "EXPLAIN", "HOOKS", "AWARE",
           "EPOCH", "FRAME", "KEEPER", "ORIGIN", "WILDBLOCK", "PLAYTEST", "CAMPAIGN", "SETTLE", "PEN2")


def _ok(r):
    return isinstance(r, dict) and r.get("success", True) is not False


# ------------------------------------------------------------------------------------------------ pure verdicts
def v_EVIDENCE(d):
    rows, cids = d.get("rows") or [], d.get("cids") or []
    if not cids:
        return 2, "no calls were made: %s" % d.get("why")
    starts = {r.get("cid") for r in rows if r.get("ev") == "start"}
    ends = {r.get("cid") for r in rows if r.get("ev") == "end"}
    f = ["call %s has no %s row" % (c, w) for c in cids for w, s in (("start", starts), ("end", ends)) if c not in s]
    if d.get("inflight"):
        f.append("in-flight markers left: %s" % d["inflight"][:5])
    return (1 if f else 0), "; ".join(f) or "%d calls, each with start and end rows; no in-flight marker" % len(cids)


def v_TPS(d):
    if d.get("why"):
        return 2, d["why"]
    w = [x for x in d.get("windows") or [] if x.get("state") == "run"]
    f = []
    if d.get("grew", 0) <= 0:
        f.append("record segment did not grow (%s bytes)" % d.get("grew"))
    if len(w) < 8:
        f.append("%d run windows in 60 s, want >= 8 at a 5 s cadence" % len(w))
    ratios = sorted(x.get("ratio") for x in w if isinstance(x.get("ratio"), (int, float)))
    med = ratios[len(ratios) // 2] if ratios else None
    if med is None or not 0.8 <= med <= 1.2:
        f.append("median ratio %s, want near 1 at speed 1" % med)
    s = d.get("summary") or {}
    if not all(k in s for k in ("min", "median", "max")):
        f.append("report summary lacks min/median/max: %s" % sorted(s))
    return (1 if f else 0), "; ".join(f) or "%d run windows, median ratio %.3f, segment +%d bytes" % (
        len(w), med, d["grew"])


def v_NORTHSTAR(d):
    if d.get("why"):
        return 2, d["why"]
    f = [k + ": " + v for k, v in sorted((d.get("faults") or {}).items())]
    return (1 if f else 0), "; ".join(f) or "six tools answered correctly: %s" % d.get("note")


def v_STATICCALL(d):
    if d.get("why"):
        return 2, d["why"]
    f = ["%s: %s" % (k, r.get("message")) for k, r in sorted((d.get("calls") or {}).items()) if not r.get("ok")]
    return (1 if f else 0), "; ".join(f) or "whole ThingID and bare number both resolve: %s" % d.get("note")


def v_TILECACHE(d):
    if d.get("why"):
        return 2, d["why"]
    f = []
    if not d.get("staleBefore"):
        f.append("audit after the retile reads no stale temperature cache: %s" % d.get("audit1"))
    if not d.get("verifiedNull"):
        f.append("reset did not return verifiedNull: %s" % d.get("reset"))
    if d.get("staleAfter"):
        f.append("re-audit still stale: %s" % d.get("audit2"))
    return (1 if f else 0), "; ".join(f) or "tile %s: stale after retile, verifiedNull, fresh after reset" % d.get("tile")


def v_PROFILE(d):
    if d.get("why"):
        return 2, d["why"]
    f = []
    if d.get("noFileProfile") != "campaign":
        f.append("no profile file reads %s, want campaign" % d.get("noFileProfile"))
    if not d.get("spawnRan"):
        f.append("spawn_pawn refused in campaign: %s" % d.get("spawnMsg"))
    if d.get("staticRefused") is not True:
        f.append("static_call not refused in campaign: %s" % d.get("staticMsg"))
    if d.get("backProfile") != "test" or (d.get("flipS") or 99) > 2.0:
        f.append("test file back reads %s after %s s, want test within 2 s" % (d.get("backProfile"), d.get("flipS")))
    if d.get("listedProfile") != "campaign":
        f.append("a test file listing the loaded save in campaignSaves reads %s, want campaign" % d.get("listedProfile"))
    return (1 if f else 0), "; ".join(f) or "campaign with no file (spawn runs, static_call refused); test again in %.2f s; a listed save reads campaign" % d["flipS"]


def v_PEN(d):
    if d.get("why"):
        return 2, d["why"]
    rel, pin = d.get("release") or {}, d.get("pin") or {}
    f = []
    n = len(d.get("ids") or [])
    if d.get("waitBefore") != n:
        f.append("%s of %d had a Wait pin before release" % (d.get("waitBefore"), n))
    if rel.get("released") != n or rel.get("notReleased"):
        f.append("released %s of %d, notReleased %s" % (rel.get("released"), n, rel.get("notReleased")))
    if d.get("waitAfter"):
        f.append("%d still on Wait after release" % d["waitAfter"])
    if pin.get("pinned") != n:
        f.append("re-pinned %s of %d" % (pin.get("pinned"), n))
    return (1 if f else 0), "; ".join(f) or "%d animals released (no Wait after), re-pinned %s, returnedHome %s" % (
        n, pin.get("pinned"), pin.get("returnedHome"))


def v_EXPLAIN(d):
    if d.get("why"):
        return 2, d["why"]
    f = []
    for k in ("name", "cell"):
        r = d.get(k) or {}
        if r.get("resolved") is not False or len(r.get("ambiguous") or []) < 2:
            f.append("%s selector: resolved %s with %d candidates, want false with >= 2" % (
                k, r.get("resolved"), len(r.get("ambiguous") or [])))
    gone = d.get("gone") or {}
    if _ok(gone) and gone.get("resolved") is not False:
        f.append("vanished id answered: %s" % json.dumps(gone)[:160])
    dead = d.get("dead")
    if dead is not None and not (_ok(dead) and dead.get("resolved") is True):
        f.append("a killed pawn's id no longer explains: %s" % json.dumps(dead)[:160])
    return (1 if f else 0), "; ".join(f) or "name and cell list candidates, pick none; vanished id refused"


def v_HOOKS(d):
    if d.get("why"):
        return 2, d["why"]
    f = ["%s coverage %s" % (k, v) for k, v in sorted((d.get("coverage") or {}).items()) if v != "ok"]
    if not d.get("coverage"):
        f.append("no hook coverage read")
    for k in ("faults", "foreignThreadRejects"):
        if d.get(k):
            f.append("%s %s" % (k, d[k]))
    return (1 if f else 0), "; ".join(f) or "%d hooks coverage ok after %s min, 0 faults, 0 foreign-thread rejects" % (
        len(d["coverage"]), d.get("minutes"))


def v_AWARE(d):
    if d.get("why"):
        return 2, d["why"]
    f = []
    if d.get("early"):
        return 2, "precondition: awareness_settings.json sets install.generation-early"
    if d.get("genBefore"):
        f.append("GeneratePawn hook installed before any arm: %s" % d.get("detailBefore"))
    if not d.get("genAfter"):
        f.append("GeneratePawn not read as installed lazily by an arm after startup: %s" % d.get("detailAfter"))
    if d.get("campaignMeasured") and str(d.get("campaign")).startswith("installed"):
        f.append("an arm in campaign installed GeneratePawn: %s" % d.get("campaign"))
    if f:
        return 1, "; ".join(f)
    if not d.get("campaignMeasured"):
        return 2, "test half holds (%s); the campaign half needs a game whose hook is not yet installed" % d.get("detailAfter")
    return 0, "campaign arm leaves it off (%s); test arm: %s" % (d.get("campaign"), d.get("detailAfter"))


def v_EPOCH(d):
    if d.get("why"):
        return 2, d["why"]
    f = []
    if d.get("epochAfter") == d.get("epochBefore"):
        f.append("the reload kept epoch %s" % d.get("epochBefore"))
    for k, want in (("oldEpoch", False), ("absentMap", False), ("currentBoth", True)):
        msg = str(d.get(k + "Msg") or "")
        if bool(d.get(k)) != want or (not want and "refus" not in msg.lower()):
            f.append("%s answered %s, want %s: %s" % (k, d.get(k), "pass" if want else "the companion's refusal", msg))
    if d.get("releaseAfterLoad") != "new-game":
        f.append("block after the load reads lastRelease %s, want new-game" % d.get("releaseAfterLoad"))
    if d.get("releaseAfterTtl") != "expired":
        f.append("block after its TTL reads lastRelease %s, want expired" % d.get("releaseAfterTtl"))
    return (1 if f else 0), "; ".join(f) or "epoch %s -> %s; old epoch and absent map refused; block new-game, then expired" % (
        d.get("epochBefore"), d.get("epochAfter"))


def v_FRAME(d):
    if d.get("why"):
        return 2, d["why"]
    f = []
    for k in ("sessionParses", "mergedParses"):
        if not d.get(k):
            f.append("%s false: %s" % (k, d.get(k + "Err")))
    n0, n1 = d.get("n0"), d.get("n1")
    if n0 is None or n0 > 120:
        f.append("session right after the arm holds %s frames, want a fresh count (<= 120)" % n0)
    if n0 is not None and n1 is not None and n1 - n0 > 5 * 90:
        f.append("5 s after the arm the session grew %d frames: load frames merged late" % (n1 - n0))
    return (1 if f else 0), "; ".join(f) or "both strings parse; arm fresh (%s), +%s frames in 5 s" % (n0, (n1 or 0) - (n0 or 0))


def v_KEEPER(d):
    if d.get("why"):
        return 2, d["why"]
    if not d.get("keepers"):
        return 2, "the Saves folder holds no keeper, so nothing shows the guard keeps one"
    f = []
    if d.get("unstored"):
        f.append("keepers with no store copy: %s" % d["unstored"])
    sv = d.get("save") or {}
    if not sv.get("verified"):
        f.append("save_base through the guard did not verify: %s" % "; ".join(sv.get("problems") or ["no reading"]))
    return (1 if f else 0), "; ".join(f) or "%d keepers hashed and stored; %s.rws written new (slot %s), no keeper changed" % (
        d["keepers"], d.get("target"), d.get("slot"))


def v_ORIGIN(d):
    if d.get("why"):
        return 2, d["why"]
    if d.get("launchRc") != 0:
        return 2, "the cold launch did not read READY (exit %s): %s" % (d.get("launchRc"), d.get("launchTail"))
    f = []
    if d.get("restored") is not True:
        f.append("awareness_settings.json was not restored: %s" % d.get("restoreErr"))
    if not str(d.get("genHook") or "").startswith("installed early"):
        return 2, "precondition: the GeneratePawn hook was not installed early (%s)%s" % (
            d.get("genHook"), "; " + "; ".join(f) if f else "")
    if d.get("startedBy") != "bridge-registration":
        f.append("awareness startedBy %s, want bridge-registration" % d.get("startedBy"))
    wild = d.get("wild") or []
    if not wild:
        return (1 if f else 2), "; ".join(f + ["the first map holds no wild animal to read"])
    ch = d.get("chains") or {}
    bad = [w for w in wild if not re.search(r"\bmapgen\b.*>.*\bwild-spawner\b", str(ch.get(w) or ""))]
    if bad:
        f.append("%d of %d wild animals do not read mapgen > wild-spawner: %s" % (
            len(bad), len(wild), ", ".join("%s=%s" % (w, ch.get(w)) for w in bad[:5])))
    return (1 if f else 0), "; ".join(f) or "startedBy bridge-registration; %d wild animals read mapgen > wild-spawner" % len(wild)


WILD_TICKS = 1300          # the spawner check period is 1213 ticks (the tool's own text): one full period and more


def v_WILDBLOCK(d):
    if d.get("why"):
        return 2, d["why"]
    if (d.get("ticks") or 0) < 1213:
        return 2, "the clock moved %s ticks under the block, want 1213+" % d.get("ticks")
    f = []
    if not d.get("blocked"):
        f.append("the block did not read back blocked")
    if (d.get("skipped") or 0) < 0.9 * d["ticks"]:
        f.append("skippedTicks rose %s over %s ticks: the block was not exercised" % (d.get("skipped"), d["ticks"]))
    if d.get("releasedBlocked") is not False or d.get("lastRelease") != "released":
        f.append("after release: blocked %s, lastRelease %s" % (d.get("releasedBlocked"), d.get("lastRelease")))
    if d.get("skippedAfter"):
        f.append("%s spawner ticks skipped after the release" % d["skippedAfter"])
    return (1 if f else 0), "; ".join(f) or "blocked; %d of %d ticks skipped; released, then 0 skipped in %s ticks" % (
        d["skipped"], d["ticks"], d.get("afterTicks"))


def v_PLAYTEST(d):
    if d.get("why"):
        return 2, d["why"]
    if d.get("gssStarted") and d.get("fwRefused") is False:   # the fault itself; its stray run then blocks fwStarted
        return 1, "playtest_start beside a GSS run: %s" % (d.get("fwRefusal") or "it started")
    if not d.get("gssStarted") or not d.get("fwStarted"):
        return 2, "a first run did not start (gss %s, flowworks %s): %s" % (d.get("gssStarted"), d.get("fwStarted"),
                                                                           d.get("startMsg"))
    if d.get("fwRunningAtCall") is not True:
        return 2, "the FlowWorks run was not running at the cross-call (%s), so the GSS start proves nothing" % (
            d.get("fwStateAtCall"))
    f = []
    if not (d.get("fwRefused") and "GSS playtest run is active" in str(d.get("fwRefusal"))):
        f.append("playtest_start beside a GSS run: %s" % (d.get("fwRefusal") or "it started"))
    if not (d.get("gssRefused") and "FlowWorks playtest run is active" in str(d.get("gssRefusal"))):
        f.append("gss_playtest_start beside a FlowWorks run: %s" % (d.get("gssRefusal") or "it started"))
    return (1 if f else 0), "; ".join(f) or "each runner refused while the other ran"


def v_CAMPAIGN(d):
    if d.get("why"):
        return 2, d["why"]
    if d.get("profile") != "campaign":
        return 2, "precondition: the profile read %s, not campaign" % d.get("profile")
    f = []
    if not (d.get("artRefused") and "CAMPAIGN profile" in str(d.get("artMsg")) and "killHostiles" in str(d.get("artMsg"))):
        f.append("artboard_stage killHostiles: %s" % (d.get("artMsg") or "it ran"))
    if not (d.get("setRefused") and "CAMPAIGN profile" in str(d.get("setMsg"))):
        f.append("mod_settings_field set: %s" % (d.get("setMsg") or "it wrote"))
    if d.get("restored") != "test":
        f.append("the profile after the restore reads %s, want test" % d.get("restored"))
    return (1 if f else 0), "; ".join(f) or "killHostiles and settings set both refused by the CAMPAIGN profile"


def v_SETTLE(d):
    if d.get("why"):
        return 2, d["why"]
    msg = str(d.get("msg") or "")
    if "REFUSING the whole import" in msg:
        return 2, "precondition: the probe row did not resolve, so the clear check was not reached: %s" % msg[:200]
    f = []
    if not (d.get("refused") and "REFUSING before clearing" in msg):
        f.append("the import did not refuse before clearing: %s" % (msg[:200] or "it applied"))
    if d.get("after") != d.get("before"):
        f.append("settlements %s -> %s" % (d.get("before"), d.get("after")))
    return (1 if f else 0), "; ".join(f) or "refused before clearing; %s settlements before and after" % d.get("before")


def v_PEN2(d):
    if d.get("why"):
        return 2, d["why"]
    if not d.get("selected"):
        return 2, "the review layout's pen rects selected no animal on %s (the save's layout differs)" % d.get("save")
    f = []
    if d.get("released") != d.get("selected") or d.get("notReleased"):
        f.append("released %s of %s (%s still Wait)" % (d.get("released"), d.get("selected"), d.get("notReleased")))
    ids, moved = d.get("ids") or [], d.get("moved") or []
    if len(moved) * 2 < len(ids):
        f.append("only %d of %d moved in 600 ticks" % (len(moved), len(ids)))
    if d.get("outside"):
        f.append("outside their pen: %s" % d["outside"][:5])
    if d.get("facingWrong"):
        f.append("facing not restored: %s" % d["facingWrong"][:5])
    if (d.get("returnedHome") or 0) < len(ids):
        f.append("returned home %s of %d" % (d.get("returnedHome"), len(ids)))
    return (1 if f else 0), "; ".join(f) or "%d released, %d moved, all inside their pens, all home with their facing (%s)" % (
        len(ids), len(moved), d.get("save"))


VERDICTS = dict((c, globals()["v_" + c]) for c in CLAUSES)


def verdict(clause, d):
    try:
        return VERDICTS[clause](d)
    except Exception as e:                                      # noqa: BLE001 - a malformed read is not a pass
        return 2, "verdict could not read the data: %s: %s" % (type(e).__name__, e)


# ------------------------------------------------------------------------------------------------ live gathering
class Live(object):
    def __init__(self, s):
        sys.path.insert(0, HERE)
        from common import call
        self.s, self._call, self.spawned = s, call, []

    def call(self, tool, **p):
        return self._call(self.s, tool, **p)

    def anchor(self):
        import helpers as H
        ax, az, _ = H.safe_anchor(self.s)
        return ax, az

    def spawn(self, kind, x, z, count=1, faction="none"):
        r = self.call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=count)
        ids = [p.get("id") for p in r.get("pawns") or [] if p.get("id")]
        self.spawned += ids
        return r, ids

    def cleanup(self):
        import helpers as H
        if self.spawned:
            try:
                H.remove_visitors(self.s, self.spawned)
            except Exception:                                   # noqa: BLE001 - housekeeping, never a verdict
                pass


def g_EVIDENCE(L):
    import rimbridge_client as RC
    path = RC.EVIDENCE_LOG
    if not path:
        return {"why": "no evidence log configured in this interpreter (RIMBRIDGE_EVIDENCE_LOG empty or not Windows)"}
    size0 = os.path.getsize(path) if os.path.isfile(path) else 0
    for t in ("jawa/map_info", "jawa/companion_handshake", "jawa/tps_report"):
        L.call(t) if t != "jawa/tps_report" else L.call(t, last=1)
    time.sleep(0.5)
    rows = []
    with open(path, "rb") as fh:
        fh.seek(size0)
        for line in fh.read().decode("utf-8", "replace").splitlines():
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
    # a start row names the pid; its end row carries only the cid (measured 2026-11-25)
    cids = sorted({r.get("cid") for r in rows if r.get("ev") == "start" and r.get("pid") == os.getpid()})
    mine = [r for r in rows if r.get("cid") in cids]
    idir = RC._inflight_dir()
    inflight = [n for n in (os.listdir(idir) if os.path.isdir(idir) else []) if str(os.getpid()) in n]
    return {"rows": mine, "cids": cids, "inflight": inflight}


def g_TPS(L):
    r0 = L.call("jawa/tps_report", last=1)
    seg = r0.get("segment")
    if not seg or not os.path.isfile(seg):
        return {"why": "tps_report names no readable segment: %s" % seg}
    size0 = os.path.getsize(seg)
    L.call("rimworld/set_time_speed", speed="Normal")
    try:
        time.sleep(62)
    finally:
        L.call("rimworld/set_time_speed", speed="Paused")
    r = L.call("jawa/tps_report", last=12)
    seg1 = r.get("segment") or seg
    grew = os.path.getsize(seg1) - (size0 if seg1 == seg else 0)
    # the report returns its last windows as JSONL strings (samplesJsonl); min/median/max are read from them
    wins = []
    for x in r.get("samplesJsonl") or []:
        try:
            wins.append(json.loads(x))
        except ValueError:
            pass
    # the report's own ratioMin/Median/Max over its run windows: the criterion is that the TOOL returns them
    summ = {k: r.get(f) for k, f in (("min", "ratioMin"), ("median", "ratioMedian"), ("max", "ratioMax"))
            if isinstance(r.get(f), (int, float))}
    return {"windows": wins, "summary": summ, "grew": grew}


def g_NORTHSTAR(L):
    faults, notes = {}, []
    ax, az = L.anchor()
    _, ids = L.spawn("Muffalo", ax, az)
    if not ids:
        return {"why": "Muffalo spawn failed"}
    L.call("jawa/pen_pin", pawns=ids[0].replace("Thing_", ""), restore=False, ticks=600)
    c = L.call("jawa/pawn_census", ids=ids[0])
    row = (c.get("pawns") or c.get("rows") or [{}])[0]
    if not _ok(c) or not row or "wait" not in json.dumps(row).lower():
        faults["pawn_census"] = "no row with a job for %s: %s" % (ids[0], json.dumps(c)[:200])
    ro = L.call("jawa/pawn_roles", faction="player")
    rows = ro.get("pawns") or ro.get("rows") or []
    if not _ok(ro) or not rows or not all(x.get("isColonist") for x in rows
                                                       if not (x.get("isSlave") or x.get("isAnimal") or x.get("isColonyMech"))):
        faults["pawn_roles"] = "player pawns not read as colonists: %s" % json.dumps(ro)[:200]
    pk = L.call("jawa/incident_queue_peek")
    q = pk.get("queue") or pk.get("incidents") or pk.get("entries") or []
    if not _ok(pk):
        faults["incident_queue_peek"] = json.dumps(pk)[:200]
    if q:
        rm = L.call("jawa/incident_queue_remove", defName=(q[0].get("def") or q[0].get("defName")), dryRun=True)
        q2 = (L.call("jawa/incident_queue_peek").get("queue") or [])
        if not _ok(rm) or len(q2) != len(q):
            faults["incident_queue_remove"] = "dry run changed the queue %d -> %d: %s" % (len(q), len(q2), json.dumps(rm)[:160])
    else:
        rm = L.call("jawa/incident_queue_remove", defName="RaidEnemy", dryRun=True)
        if not _ok(rm) and "nothing" not in json.dumps(rm).lower() and "no " not in json.dumps(rm).lower():
            faults["incident_queue_remove"] = json.dumps(rm)[:200]
        notes.append("queue empty")
    dmg = L.call("jawa/damage", damageDef="Cut", amount=3, thingId=ids[0])
    log = L.call("jawa/damage_log", thingId=ids[0])
    ev = log.get("events") or []
    if not _ok(dmg) or not ev:
        faults["damage_log"] = "dealt %s, logged %d events: %s" % (_ok(dmg), len(ev), json.dumps(log)[:200])
    ln = L.call("jawa/thing_lineage", ids=ids[0])
    # a miss still echoes the id ({id, found=false, fate}): require a found row
    if not _ok(ln) or not any(r.get("found") is True for r in ln.get("results") or []):
        faults["thing_lineage"] = json.dumps(ln)[:200]
    notes.append("victim %s, %d damage events, %d queued incidents" % (ids[0], len(ev), len(q)))
    return {"faults": faults, "note": "; ".join(notes)}


def g_STATICCALL(L):
    ax, az = L.anchor()
    _, ids = L.spawn("Muffalo", ax, az)
    if not ids:
        return {"why": "Muffalo spawn failed"}
    whole = ids[0].replace("Thing_", "")
    num = re.sub(r"^\D+", "", whole)
    calls = {}
    for k, a in (("whole ThingID", whole), ("bare number", num)):
        r = L.call("jawa/static_call", type="Verse.GenAdj", method="OccupiedRect", args=a)
        calls[k] = {"ok": _ok(r), "message": (r.get("message") or json.dumps(r.get("result"))[:80])}
    return {"calls": calls, "note": "%s -> %s" % (whole, calls["whole ThingID"]["message"])}


def g_TILECACHE(L):
    mi = L.call("jawa/map_info")
    home = mi.get("tile")
    g = L.call("jawa/world_tile_get", range="%d-%d" % (max(0, (home or 0) + 400), (home or 0) + 460), limit=60)
    rows = [r for r in g.get("tiles") or g.get("rows") or [] if (r.get("elevation") or 0) > 0]
    if not rows:
        return {"why": "no land tile read near %s: %s" % (home, json.dumps(g)[:160])}
    t = rows[0].get("tile", rows[0].get("id"))
    temp0 = rows[0].get("temperature")
    L.call("jawa/world_cache_audit", tiles=str(t), includeTemps=True, populate=True)
    try:
        L.call("jawa/world_tile_set", tiles=str(t), temperature=(temp0 or 0) + 25)
        a1 = L.call("jawa/world_cache_audit", tiles=str(t), includeTemps=True)
        rs = L.call("jawa/world_tile_cache_reset", tiles=str(t))
        a2 = L.call("jawa/world_cache_audit", tiles=str(t), includeTemps=True)
    finally:
        L.call("jawa/world_tile_set", tiles=str(t), temperature=temp0)
        L.call("jawa/world_tile_cache_reset", tiles=str(t))

    def stale(a):
        return sum(int((a.get(k) or {}).get("stale") or 0) for k in ("minTemp", "maxTemp"))
    return {"tile": t, "audit1": json.dumps(a1)[:300], "audit2": json.dumps(a2)[:300], "reset": json.dumps(rs)[:300],
            "staleBefore": stale(a1) > 0, "staleAfter": stale(a2) > 0, "verifiedNull": "verifiednull" in json.dumps(rs).lower()}


def _profile(L):
    h = L.call("jawa/companion_handshake")
    return h.get("effectiveProfile"), h.get("profileFile")


def g_PROFILE(L):
    # always the bundle's own save: A2 lists the loaded save's name in campaignSaves
    r = L.call("rimworld/save_game", saveName=SAVE)
    ok, msg = _load(L) if _ok(r) else (False, "save_game failed: %s" % json.dumps(r)[:160])
    if not ok:
        return {"why": "precondition: no loaded save (the companion reads test by design while none is): %s" % msg}
    prof, path = _profile(L)
    if not path:
        return {"why": "handshake names no profile file"}
    path = path.replace("/", "\\") if os.name == "nt" else path
    if not os.path.isfile(path):
        return {"why": "profile file %s absent at start: cannot restore what is not there" % path}
    keep = open(path, "rb").read()
    aside = path + ".bundle_aside"
    out = {}
    os.replace(path, aside)
    try:
        time.sleep(2.5)
        out["noFileProfile"], _ = _profile(L)
        ax, az = L.anchor()
        r, ids = L.spawn("Muffalo", ax, az)
        out["spawnRan"], out["spawnMsg"] = bool(ids), r.get("message")
        sc = L.call("jawa/static_call", type="Verse.GenAdj", method="OccupiedRect", args=(ids[0] if ids else "1"))
        out["staticRefused"] = not _ok(sc) and "profile" in json.dumps(sc).lower()
        out["staticMsg"] = (sc.get("message") or "")[:160]
    finally:
        with open(path, "wb") as fh:
            fh.write(keep)
        t0 = time.time()
        if os.path.exists(aside):
            os.remove(aside)
    out["backProfile"], out["flipS"] = _wait_profile(L, "test", t0=t0)
    try:
        d = json.loads(keep.decode("utf-8"))
        d["campaignSaves"] = SAVE
        with open(path, "w") as fh:
            json.dump(d, fh)
        out["listedProfile"], _ = _wait_profile(L, "campaign")
    finally:
        with open(path, "wb") as fh:
            fh.write(keep)
    _wait_profile(L, "test")
    return out


def _waits(L, ids):
    c = L.call("jawa/pawn_census", ids=",".join(ids))
    rows = c.get("pawns") or c.get("rows") or []
    return sum(1 for r in rows if "wait" == str((r.get("job") or {}).get("def") if isinstance(r.get("job"), dict)
                                                else r.get("job") or r.get("jobDef")).lower())


def g_PEN(L):
    ax, az = L.anchor()
    _, ids = L.spawn("Muffalo", ax, az, count=3)
    if len(ids) < 3:
        return {"why": "spawned %d of 3 Muffalo" % len(ids)}
    pins = ",".join(i.replace("Thing_", "") for i in ids)
    p0 = L.call("jawa/pen_pin", pawns=pins, restore=False, ticks=60000)
    if not _ok(p0):
        return {"why": "the first pin failed: %s" % json.dumps(p0)[:160]}
    wb = _waits(L, ids)
    rel = L.call("jawa/pen_release", pawns=pins)
    wa = _waits(L, ids)
    pin = L.call("jawa/pen_pin", pawns=pins, restore=True)
    return {"ids": ids, "waitBefore": wb, "release": rel, "waitAfter": wa, "pin": pin}


def g_EXPLAIN(L):
    ax, az = L.anchor()
    _, ids = L.spawn("Muffalo", ax, az, count=2)
    if len(ids) < 2:
        return {"why": "spawned %d of 2 Muffalo" % len(ids)}
    rows = L.call("jawa/pawn_census", ids=",".join(ids)).get("pawns") or []
    label = (rows[0].get("name") if rows else None) or "Muffalo"
    name = L.call("jawa/thing_explain", name=label)
    # one cell that holds two pawns: stand both Muffalo on the first one's cell
    x, z = rows[0].get("x"), rows[0].get("z")
    st = L.call("rimworld/spawn_thing", defName="Steel", x=x, z=z, stackCount=10)
    c = L.call("jawa/thing_explain", cell="%s,%s" % (x, z))
    for t in (c.get("ambiguous") or []):                      # the Steel goes again: the clause restores the map
        if t.get("def") == "Steel":
            L.call("jawa/destroy_batch", rects="%s,%s,1,1" % (x, z), categories="Item")
            break
    import helpers as H
    H.remove_visitors(L.s, [ids[0]])
    L.spawned.remove(ids[0])
    gone = L.call("jawa/thing_explain", id=ids[0])
    # a killed pawn is Destroyed too (Kill -> Destroy(KillFinalize)) but not gone: it must still explain
    L.call("jawa/damage", damageDef="Cut", amount=5000, thingId=ids[1])
    dead = L.call("jawa/thing_explain", id=ids[1])
    return {"name": name, "cell": c, "gone": gone, "dead": dead, "nameUsed": label}


def g_HOOKS(L):
    mins = float(os.environ.get("BUNDLE_PLAY_MINUTES") or 10)
    L.call("rimworld/set_time_speed", speed="Superfast")
    try:
        time.sleep(mins * 60)
    finally:
        L.call("rimworld/set_time_speed", speed="Paused")
    r = L.call("jawa/tps_report", last=1)
    cov, faults, rejects = {}, 0, 0
    for fam in ("hooks", "attributionHooks"):
        for k, x in (r.get(fam) or {}).items():
            cov["%s.%s" % (fam, k)] = x.get("coverage")
            faults += sum(int(x.get(f) or 0) for f in ("faults", "unbalanced", "orphanExits", "originalThrew"))
            rejects += int(x.get("foreignRejected") or 0)
    faults += int((r.get("tier") or {}).get("hookFaults") or 0)
    return {"coverage": cov, "faults": faults, "foreignThreadRejects": rejects, "minutes": mins}


def g_AWARE(L):
    st = L.call("jawa/awareness", action="status")
    path = st.get("settings")
    early = False
    if path:
        p = path.replace("/", "\\") if os.name == "nt" else path
        try:
            early = bool(json.load(open(p)).get("install.generation-early"))
        except (OSError, ValueError):
            early = False
    early = early or bool((st.get("options") or {}).get("install.generation-early"))
    det0 = str(st.get("generationHook") or "")
    early = early or det0.startswith("installed early")   # launched with the option (ORIGIN's cold launch): no lazy half
    camp = None
    if not det0.startswith("installed") and not early:
        # campaign half: a fresh hook, a loaded save, the profile file at campaign -> an arm leaves GeneratePawn off
        ok, msg = _ensure_loaded(L)
        prof, path = _profile(L)
        if ok and path:
            path = path.replace("/", "\\") if os.name == "nt" else path
            keep = open(path, "rb").read()
            try:
                _write_profile(path, "campaign", keep)
                if _wait_profile(L, "campaign")[0] == "campaign":
                    L.call("jawa/awareness", action="arm", minutes=5)
                    camp = str(L.call("jawa/awareness", action="status").get("generationHook") or "")
            finally:
                with open(path, "wb") as fh:
                    fh.write(keep)
            _wait_profile(L, "test")
    L.call("jawa/awareness", action="arm", minutes=5)
    det1 = str(L.call("jawa/awareness", action="status").get("generationHook") or "")
    # installed at startup reads 'installed early ...'; a lazy install names the arm and its time, after the startup
    m = re.search(r"installed lazily by jawa/awareness arm at (\S+)", det1)
    lazy_after_start = bool(m) and m.group(1) > str(st.get("installedUtc") or "")
    return {"early": early, "genBefore": det0.startswith("installed") and "lazily" not in det0,
            "genAfter": lazy_after_start, "detailBefore": det0[:300], "detailAfter": det1[:300],
            "campaign": camp, "campaignMeasured": camp is not None}


def _epoch(L):
    return (L.call("jawa/companion_handshake").get("game") or {}).get("epoch")


def _load(L):
    r = L.call("rimworld/load_game_ready", saveName=SAVE, readiness="playable", timeoutMs=600000, pauseIfNeeded=True)
    return _ok(r), json.dumps(r)[:200]


def _ensure_loaded(L):
    """A loaded save (the companion reads test while none is): save the current game as SAVE and reload it, once."""
    if "no save was loaded" not in str(L.call("jawa/companion_handshake").get("profileWhy")):
        return True, "a save is loaded"
    r = L.call("rimworld/save_game", saveName=SAVE)
    if not _ok(r):
        return False, "save_game failed: %s" % json.dumps(r)[:160]
    return _load(L)


def _write_profile(path, profile, keep):
    try:
        d = json.loads(keep.decode("utf-8"))
    except ValueError:
        d = {}
    d["profile"] = profile
    with open(path, "w") as fh:
        json.dump(d, fh)


def _wait_profile(L, want, limit=10.0, t0=None):
    """-> (profile, seconds from t0 to the START of the first call that read `want`). The call's own round trip
    (0.3-0.5 s on Steve1) is not the companion's latency: a 2.45 s end-of-call reading was 1.9 s of cache (2026-11-25)."""
    t0 = time.time() if t0 is None else t0
    while time.time() - t0 < limit:
        ts = time.time()
        p, _ = _profile(L)
        if p == want:
            return p, round(ts - t0, 2)
        time.sleep(0.2)
    return p, round(time.time() - t0, 2)


def g_EPOCH(L):
    mi = L.call("jawa/map_info")
    r = L.call("rimworld/save_game", saveName=SAVE)
    if not _ok(r):
        return {"why": "save_game failed: %s" % json.dumps(r)[:200]}
    e0 = _epoch(L)
    cur0 = (L.call("jawa/companion_handshake").get("game") or {}).get("currentMapId")
    L.call("jawa/wild_spawner_block", action="block", minutes=30)
    ok, msg = _load(L)
    if not ok:
        return {"why": "reload failed: %s" % msg}
    e1 = _epoch(L)
    rel_load = (L.call("jawa/wild_spawner_block", action="get").get("lastRelease"))
    g = L.call("jawa/companion_handshake").get("game") or {}
    out = {"epochBefore": e0, "epochAfter": e1, "releaseAfterLoad": rel_load, "mapBefore": mi.get("uniqueID")}
    for k, args in (("oldEpoch", {"expectGameEpoch": e0}), ("absentMap", {"expectMapId": 987654}),
                    ("currentBoth", {"expectGameEpoch": e1, "expectCurrentMapId": g.get("currentMapId", cur0)})):
        try:
            r = L.call("jawa/map_info", **args)
            out[k], out[k + "Msg"] = _ok(r) and "REFUSED" not in json.dumps(r), (r.get("message") or "")[:160]
        except Exception as e:                                  # noqa: BLE001 - a refusal may arrive as an error
            out[k], out[k + "Msg"] = False, str(e)[:160]
    L.call("jawa/wild_spawner_block", action="block", minutes=0.25)
    time.sleep(20)
    out["releaseAfterTtl"] = L.call("jawa/wild_spawner_block", action="get").get("lastRelease")
    return out


def g_FRAME(L):
    ok, msg = _ensure_loaded(L)
    ok, msg = _load(L) if ok else (ok, msg)
    if not ok:
        return {"why": "could not reload a save: %s" % msg}
    time.sleep(3)
    L.call("jawa/health", action="arm", minutes=5)

    def read():
        fh = (L.call("jawa/health", action="status").get("frameHist") or {})
        out = {}
        for k in ("session", "merged"):
            try:
                out[k] = json.loads(fh.get(k) or "")
            except ValueError as e:
                out[k + "Err"] = "%s: %s" % (e, (fh.get(k) or "")[:120])
        return out
    a = read()
    n0 = (a.get("session") or {}).get("n")
    L.call("rimworld/set_time_speed", speed="Normal")
    try:
        time.sleep(5)
    finally:
        L.call("rimworld/set_time_speed", speed="Paused")
    b = read()
    return {"sessionParses": "session" in a and "session" in b, "mergedParses": "merged" in a and "merged" in b,
            "sessionParsesErr": a.get("sessionErr") or b.get("sessionErr"),
            "mergedParsesErr": a.get("mergedErr") or b.get("mergedErr"),
            "n0": n0, "n1": (b.get("session") or {}).get("n")}


def g_KEEPER(L):
    import save_guard
    import saved_base
    try:
        snap = save_guard.snapshot()
    except OSError as e:
        return {"why": "cannot back up keepers: %s" % e}
    keep = snap["keepers"]
    unstored = sorted(n for n, k in keep.items()
                      if not os.path.exists(save_guard.store_path(snap["store"], k["sha256"])))
    slot = "none" if "no save was loaded" in str(L.call("jawa/companion_handshake").get("profileWhy")) else None
    target = "bundle_keeper_%d" % int(time.time())
    path = os.path.join(snap["saves_dir"], target + ".rws")
    try:
        sv = saved_base.save_base(L.s, snap["saves_dir"], name=target, current_slot=slot)
    finally:
        if os.path.exists(path):
            os.remove(path)                   # the proof's own save, never a keeper
    return {"keepers": len(keep), "unstored": unstored, "save": sv, "target": target, "slot": slot,
            "savesDir": snap["saves_dir"]}


def g_WILDBLOCK(L):
    def tick():
        return L.call("jawa/time_clock").get("ticksGame")

    def step(n):
        t0 = tick()
        L.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True)
        t1 = tick()
        return (t1 - t0) if isinstance(t0, int) and isinstance(t1, int) else None

    b = L.call("jawa/wild_spawner_block", action="block", minutes=10)
    if not _ok(b):
        return {"why": "block failed: %s" % json.dumps(b)[:200]}
    s0 = b.get("skippedTicks") or 0
    try:
        n = step(WILD_TICKS)
        g = L.call("jawa/wild_spawner_block", action="get")
    finally:
        r = L.call("jawa/wild_spawner_block", action="release")
    g2 = L.call("jawa/wild_spawner_block", action="get")
    s2 = g2.get("skippedTicks") or 0
    n2 = step(120)
    s3 = L.call("jawa/wild_spawner_block", action="get").get("skippedTicks") or 0
    return {"blocked": bool(b.get("blocked")) and bool(g.get("blocked")), "ticks": n,
            "skipped": (g.get("skippedTicks") or 0) - s0, "releasedBlocked": g2.get("blocked"),
            "lastRelease": g2.get("lastRelease") or r.get("lastRelease"), "afterTicks": n2, "skippedAfter": s3 - s2}


def _refusal(r):
    """-> (refused, message) of a reply or a raised refusal."""
    if not isinstance(r, dict):
        return False, str(r)[:300]
    return r.get("success") is False or bool(r.get("_error")), str(r.get("message") or r.get("error") or r.get("_error")
                                                                  or json.dumps(r))[:300]


def _call_or_err(L, tool, **p):
    try:
        return L.call(tool, **p)
    except Exception as e:                                      # noqa: BLE001 - a refusal may arrive as an error
        return {"success": False, "_error": "%s: %s" % (type(e).__name__, e)}


def _await_run(L, status_tool, run_id, limit=600.0):
    """Wait for a playtest run to leave running (hang guard: a quick run is a minute; the run steps itself)."""
    t0 = time.time()
    while time.time() - t0 < limit:
        st = L.call(status_tool, runId=run_id).get("state")
        if st != "running":
            return st
        time.sleep(3)
    return "running"


def g_PLAYTEST(L):
    out = {}
    g = _call_or_err(L, "jawa/gss_playtest_start", recipe="quick")
    out["gssStarted"] = _ok(g) and bool(g.get("runId"))
    if not out["gssStarted"]:
        out["startMsg"] = _refusal(g)[1]
        return out
    stray = _call_or_err(L, "jawa/playtest_start", recipe="fluids")
    out["fwRefused"], out["fwRefusal"] = _refusal(stray)
    _await_run(L, "jawa/gss_playtest_status", g["runId"])
    L.call("jawa/gss_playtest_collect", runId=g["runId"])
    if not out["fwRefused"] and _ok(stray) and stray.get("runId"):   # it started beside GSS: FAIL, and leave no run behind
        _await_run(L, "jawa/playtest_status", stray["runId"])
        L.call("jawa/playtest_collect", runId=stray["runId"])
        return out
    # pilot = fluids,dig,pit: 'fluids' alone completed in 4 frames (0.165 s) on 2026-11-25, before the cross-call
    p = _call_or_err(L, "jawa/playtest_start", recipe="pilot")
    out["fwStarted"] = _ok(p) and bool(p.get("runId"))
    if not out["fwStarted"]:
        out["startMsg"] = _refusal(p)[1]
        return out
    g2 = _call_or_err(L, "jawa/gss_playtest_start", recipe="quick")
    out["fwStateAtCall"] = L.call("jawa/playtest_status", runId=p["runId"]).get("state")
    out["fwRunningAtCall"] = out["fwStateAtCall"] == "running"     # read after: still running then, so running at the call
    out["gssRefused"], out["gssRefusal"] = _refusal(g2)
    _await_run(L, "jawa/playtest_status", p["runId"])
    L.call("jawa/playtest_collect", runId=p["runId"])
    if not out["gssRefused"] and _ok(g2) and g2.get("runId"):       # a GSS run started: leave no run behind
        _await_run(L, "jawa/gss_playtest_status", g2["runId"])
        L.call("jawa/gss_playtest_collect", runId=g2["runId"])
    return out


SETTINGS_TYPE, SETTINGS_FIELD = "RimMandrake.GimmeSomeSlack.Aerial.AerialSettings", "enabled"   # a GSS ModSettings field


def g_CAMPAIGN(L):
    ok, msg = _ensure_loaded(L)
    if not ok:
        return {"why": "no loaded save: %s" % msg}
    prof, path = _profile(L)
    if not path:
        return {"why": "the handshake names no profile file"}
    path = path.replace("/", "\\") if os.name == "nt" else path
    keep = open(path, "rb").read()
    out = {}
    try:
        _write_profile(path, "campaign", keep)
        out["profile"] = _wait_profile(L, "campaign")[0]
        if out["profile"] == "campaign":
            out["artRefused"], out["artMsg"] = _refusal(_call_or_err(L, "jawa/artboard_stage", phase="subjects",
                                                                     killHostiles=True))
            cur = L.call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="get", field=SETTINGS_FIELD)
            # restore-check: ok writes the field's own current value, so a set that is not refused changes nothing
            out["setRefused"], out["setMsg"] = _refusal(_call_or_err(
                L, "jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="set", field=SETTINGS_FIELD,
                value=str(cur.get("value", "True"))))
    finally:
        with open(path, "wb") as fh:
            fh.write(keep)
        out["restored"] = _wait_profile(L, "test")[0]
    return out


def g_SETTLE(L):
    if os.name != "nt":
        return {"why": "run under python.exe: the game reads the probe CSV from a Windows path"}
    import tempfile
    rows = L.call("jawa/world_objects_get", **{"def": "Settlement", "limit": 5000})   # def is a Python keyword
    objs = [o for o in rows.get("objects") or [] if o.get("isSettlement")]
    before = rows.get("settlements")
    player = [o for o in objs if str(o.get("faction") or "").startswith("Player")]
    names = {}
    for o in objs:
        if o.get("faction") and not str(o["faction"]).startswith("Player"):
            names.setdefault(o["faction"], set()).add(o.get("factionName"))
    one = sorted(fd for fd, ns in names.items() if len(ns) == 1)
    if not player or not one:
        return {"why": "no player settlement (%d) or no faction def with one live faction (%s)" % (len(player), sorted(names))}
    path = os.path.join(tempfile.gettempdir(), "bundle_settle_probe_%d.csv" % int(time.time()))
    with open(path, "w") as fh:
        fh.write("faction_def,name,tile\n%s,BundleProbe,%d\n" % (one[0], player[0]["tile"]))
    try:
        r = _call_or_err(L, "jawa/world_settlements_import", path=path, apply=True, clearExisting=True)
    finally:
        os.remove(path)
    refused, msg = _refusal(r)
    after = L.call("jawa/world_objects_get", limit=1).get("settlements")
    return {"refused": refused, "msg": msg, "before": before, "after": after, "row": [one[0], player[0]["tile"]]}


def _bare(i):
    i = str(i or "")
    return i[6:] if i.startswith("Thing_") else i


def g_PEN2(L):
    import glob
    import shutil
    import rmpaths
    from game_paths import SAVES
    fx = rmpaths.rm_win("fixtures") if os.name == "nt" else rmpaths.rm_str("fixtures")
    keep = sorted(glob.glob(os.path.join(fx, "RM_pyre_review_*.rws")))
    if not keep:
        return {"why": "no RM_pyre_review_*.rws fixture in %s" % fx}
    name = "bundle_pen2_review"
    staged = os.path.join(SAVES, name + ".rws")
    shutil.copyfile(keep[-1], staged)
    try:
        r = L.call("rimworld/load_game_ready", saveName=name, readiness="playable", timeoutMs=900000, pauseIfNeeded=True)
    finally:
        os.remove(staged)                     # the loaded game holds it now; the proof's own copy, never a keeper
    if not _ok(r):
        return {"why": "the review save did not load: %s" % json.dumps(r)[:200]}
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "Pyrelands"))
    import human_review as HR
    S = HR.station_list()
    rects = [HR.footprint(s) for s in HR.pen_stations(S)]
    rstr = HR.pen_rects(S)
    before = dict((_bare(p.get("pawn")), p) for p in L.call("jawa/pen_pin", rects=rstr, restore=False).get("pawns") or [])
    rel = L.call("jawa/pen_release", rects=rstr)                 # exactly human_review.py --release-pens (Review.pens)
    L.call("rimworld/step_game_ticks", ticks=600, pauseFirst=True)
    now = dict((_bare(p.get("id")), p) for p in L.call("jawa/list_pawns").get("pawns") or [])
    pin = L.call("jawa/pen_pin", rects=rstr, restore=True)       # exactly human_review.py --pin-pens
    pinned = dict((_bare(p.get("pawn")), p) for p in pin.get("pawns") or [])

    def rect_of(x, z):
        for (rx, rz, w, h) in rects:
            if rx <= x < rx + w and rz <= z < rz + h:
                return (rx, rz, w, h)
        return None

    ids = sorted(before)
    moved, outside, facing = [], [], []
    for i in ids:
        b, n = before[i], now.get(i) or {}
        home = rect_of(b.get("x"), b.get("z"))
        if (n.get("x"), n.get("z")) != (b.get("x"), b.get("z")):
            moved.append(i)
        if home is None or rect_of(n.get("x"), n.get("z")) != home:
            outside.append("%s at %s,%s" % (i, n.get("x"), n.get("z")))
        if str((pinned.get(i) or {}).get("rotation")) != str(b.get("rotation")):
            facing.append("%s: %s -> %s" % (i, b.get("rotation"), (pinned.get(i) or {}).get("rotation")))
    return {"save": os.path.basename(keep[-1]), "selected": rel.get("selected"), "released": rel.get("released"),
            "notReleased": rel.get("notReleased"), "ids": ids, "moved": moved, "outside": outside,
            "facingWrong": facing, "returnedHome": pin.get("returnedHome")}


def g_ORIGIN_cold(Session):
    """ORIGIN runs outside main's one Session: the cold launch ends the game the first Session talked to."""
    import subprocess
    from common import call, ensure_map
    with Session(lock=None, focus=False, strict=False, quiet=True) as s:
        path = call(s, "jawa/awareness", action="status").get("settings")
    if not path:
        return {"why": "jawa/awareness status names no settings file"}
    path = path.replace("/", "\\") if os.name == "nt" else path
    keep = open(path, "rb").read() if os.path.exists(path) else None
    out = {"restored": False}
    try:
        try:
            d = json.loads(keep.decode("utf-8")) if keep else {}
        except ValueError:
            d = {}
        d["install.generation-early"] = True
        with open(path, "w") as fh:
            json.dump(d, fh)
        lr = os.path.join(HERE, "..", "..", "..", "bridgetools", "launch_ready.py")
        p = subprocess.run([sys.executable, lr], capture_output=True, text=True, timeout=5400,  # hang guard: a cold
                           stdin=subprocess.DEVNULL)                                           # load is minutes
        out["launchRc"], out["launchTail"] = p.returncode, (p.stdout + p.stderr)[-300:]
        if p.returncode != 0:
            return out
        with Session(lock=None, focus=False, strict=False, quiet=True) as s:
            st = call(s, "jawa/awareness", action="status")         # the first tool call after the launch
            out["startedBy"], out["genHook"] = st.get("startedBy"), str(st.get("generationHook") or "")
            why = ensure_map(s)
            if why:
                out["why"] = why
                return out
            pawns = call(s, "jawa/list_pawns", faction="nonplayer").get("pawns") or []
            wild = [r.get("id") for r in pawns if r.get("id") and not r.get("faction") and not r.get("dead")]
            po = call(s, "jawa/pawn_origin", ids=",".join(wild)) if wild else {}
            out["wild"] = wild
            out["chains"] = dict((r.get("id"), (r.get("generation") or {}).get("chain")) for r in po.get("pawns") or [])
        return out
    finally:
        try:
            if keep is None:
                os.remove(path)
            else:
                with open(path, "wb") as fh:
                    fh.write(keep)
            out["restored"] = True
        except OSError as e:
            out["restoreErr"] = str(e)[:160]


def main(argv):
    if len(argv) != 2 or argv[1] not in CLAUSES:
        print(__doc__)
        return 2
    clause = argv[1]
    try:
        sys.path.insert(0, HERE)
        import common  # noqa: F401  (puts modcheck, Utils on sys.path)
        from rimdrive import Session
    except Exception as e:                                      # noqa: BLE001
        print("%s UNMEASURED: harness import failed: %s" % (clause, e))
        return 2
    if clause == "ORIGIN":
        try:
            d = g_ORIGIN_cold(Session)
        except Exception as e:                                  # noqa: BLE001 - no bridge is not a verdict
            print("%s UNMEASURED: %s: %s" % (clause, type(e).__name__, str(e)[:300]))
            return 2
        rc, msg = verdict(clause, d)
        print("%s %s: %s" % (clause, ("PASS", "FAIL", "UNMEASURED")[rc], msg))
        return rc
    try:
        with Session(lock=None, focus=False, strict=False, quiet=True) as s:
            L = Live(s)
            from common import ensure_map
            why = ensure_map(s)
            if why:
                print("%s UNMEASURED: %s" % (clause, why))
                return 2
            try:
                d = globals()["g_" + clause](L)
            finally:
                L.cleanup()
    except Exception as e:                                      # noqa: BLE001 - no bridge is not a verdict
        print("%s UNMEASURED: %s: %s" % (clause, type(e).__name__, str(e)[:300]))
        return 2
    rc, msg = verdict(clause, d)
    print("%s %s: %s" % (clause, ("PASS", "FAIL", "UNMEASURED")[rc], msg))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
