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
  PEN2       PEN_ANIMALS_UNSTICK_STATUES_LEARN_TO_WALK A2: human_review.py --build --save makes a review keeper save from
             the newest NS_Pyrelands_site_*.rws in <data root>/fixtures (tier ratchet_pilot holds its mods), the keeper
             is loaded from the menu, and human_review.py's --release-pens call releases
             every pen specimen (none left on the 60000-tick pin: each next job comes from its think tree, the pin
             reading proven on the pinned state first); by 9000 ticks at least half have moved (on the hot Pyrelands
             map an animal in a roofed pen first rests 600-1500 ticks by design, RM_JobGiver_ShadeHop, so 600 ticks
             cannot tell a rest from a pin) and each is inside its pen; its --pin-pens call brings every one home and
             restores the facing it was released with
  KEEPER     KEEPER_SAVES_HARDEN_WRONG_SLOT_WRITES A1: save_guard.snapshot on this game's real Saves folder hashes every
             keeper and holds a store copy of each; a save_base through the guard writes a new save, verified, with no
             keeper changed (the new save is deleted after: it is the proof's own)
  TPSC3      BRIDGE_TPS_REVIEW2_FIXES_1 C3 (tps_record.md Acceptance items 1 and 2), its own cold launches (python.exe
             only): two launches with no bridge client write a session row (bridge-registration, sampler complete),
             menu heartbeats and gameplay windows; a new game, a menu load, an in-game load and a new game after the
             menu each carry their own game seq and save label; 2-10 s blocks (with a 2.05-2.45 s edge sweep, at
             Superfast and paused) and 40/90 s blocks are each ONE strict-JSON incident with the right gapS, a
             "blocked in" phase, local time with offset, the game id and a containing window (simShare <= 1); saves are
             longevents; a 120 s hang killed inside leaves silence rows, a stopped mainBeat under an advancing
             watchdog, one exited-without-shutdown observer row that survives a relaunch and no retention pattern that
             deletes it; kills after/before a sample, at a full segment and after rotation read back with no replayed,
             conflicting or glued rows (malformed only from torn tails)
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
           "EPOCH", "FRAME", "KEEPER", "ORIGIN", "WILDBLOCK", "PLAYTEST", "CAMPAIGN", "SETTLE", "PEN2",
           "TPSC3")


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
    first = [w for w in wild if re.search(r"\bmapgen\b.*>.*\bwild-spawner\b", str(ch.get(w) or ""))]
    late = [w for w in wild if str(ch.get(w) or "").startswith("wild-spawner")]   # arrived after mapgen: honest
    bad = [w for w in wild if w not in first and w not in late]
    if not first:
        f.append("no wild animal reads mapgen > wild-spawner (%d late arrivals)" % len(late))
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
    ids, moved = d.get("ids") or [], d.get("moved") or []
    # the known-bad control: before the release every specimen is on the pin, so the pin reading must name each one.
    # A reading that misses the pin there could not see a pin that the release left (UNMEASURED, never PASS).
    if len(d.get("pinBefore") or []) != len(ids):
        return 2, "the pin reading named %d of %d pinned specimens before the release: it cannot see a pin" % (
            len(d.get("pinBefore") or []), len(ids))
    f = []
    if d.get("released") != d.get("selected") or d.get("notReleased"):
        f.append("released %s of %s (%s still on the pin)" % (d.get("released"), d.get("selected"), d.get("notReleased")))
    if d.get("pinAfter"):
        f.append("still on the pin right after release: %s" % d["pinAfter"][:5])
    late = d.get("lateTicks") or 600
    if len(moved) * 2 < len(ids):
        f.append("only %d of %d moved in %d ticks" % (len(moved), len(ids), late))
    if d.get("outside"):
        f.append("outside their pen: %s" % d["outside"][:5])
    if d.get("facingWrong"):
        f.append("facing not restored: %s" % d["facingWrong"][:5])
    if (d.get("returnedHome") or 0) + len(d.get("homeOccupied") or []) < len(ids):   # a held cell: the tool's rule
        f.append("returned home %s of %d" % (d.get("returnedHome"), len(ids)))
    if f and (d.get("giversAfter") or d.get("unmovedDetail")):
        f.append("givers right after release %s; unmoved kind/job/giver %s" % (d.get("giversAfter"), d.get("unmovedDetail")))
    return (1 if f else 0), "; ".join(f) or (
        "%d released (none left on the pin; givers %s), %d moved by 600 ticks and %d by %d, all inside their pens, all "
        "home with their facing (%s)" % (len(ids), d.get("giversAfter"), len(d.get("moved600") or []), len(moved), late,
                                         d.get("save")))



# ---- TPSC3: BRIDGE_TPS_REVIEW2_FIXES_1 C3 = design/RimMandrake/tps_record.md §Acceptance items 1 and 2
C3_RUN_BLOCKS = (2.0, 2.5, 5.0, 7.0, 10.0)   # bar: "2-10 s hitches", both ends and between, at Normal speed
# range: the watchdog samples the main thread's beat once a second and names the phase only past 1.5 s
# (JawaBenchTpsWatchdog.cs Loop), so a gap in (2.0, 2.5) s is the region where a hitch can lose its phase:
# swept densely, three of each
C3_EDGE_BLOCKS = (2.05, 2.15, 2.25, 2.35, 2.45) * 3
C3_FAST_BLOCK = 5.0                          # range: the speed multiplier (Superfast), one hitch
C3_PAUSED_BLOCK = 3.0                        # range: paused (frames run, no ticks), one hitch
C3_LONG_BLOCKS = (40.0, 90.0)                # bar: "40 s / 90 s main-thread blocks"
C3_HANG_S = 120.0                            # fact: jawa/tps_test_block's clamp (JawaBenchTpsSampler.cs); killed inside it
C3_ROUND_S = 0.005                           # fact: gapS, blockedS and mono are written with 3 decimals
C3_MONO_TOL_S = 0.5                          # = tps_record.MONO_TOLERANCE_S (a frame's own work beside the block)
C3_GAP_S = 2.0                               # = tps_record.GAP_SECONDS / JawaBenchTpsMath.GapSeconds
C3_EXPLAINED = 0.8                           # = tps_record.EXPLAINED_SHARE: a longevent is at least this explained
C3_BEAT_JITTER_S = 0.1                       # fact: mainBeatUtc is derived from the watchdog's clock each write (ms jitter)
C3_HB_READS = 3                              # item 1: three heartbeat reads, C3_HB_GAP_S apart
C3_HB_GAP_S = 6.0                            # fact: the heartbeat is rewritten every 5 s (JawaBenchTpsWatchdog.cs)
C3_HANG_READS = 4                            # bar: "mainBeatUtc stops while watchdogUtc advances", four reads
C3_SILENCE_MIN = 2                           # bar: "silence rows" (plural)
C3_KILLS = ("K1-after-sample", "K2-before-sample", "K3-segment-full", "K4-after-rotation")   # bar: "near sample/segment boundaries"
C3_SEGMENT_BYTES = 2 * 1024 * 1024           # = tps_record.SEGMENT_BYTES / JawaBenchTpsWriter.SegmentBytes
C3_MARK_CHARS = 30000                        # our own: one fill mark's size; K3 must stand within one mark of the boundary
C3_GAMES = ("new game (cold A)", "menu load (cold E)", "in-game load (cold E)", "new game after menu (cold E)")
_C3_OFFSET = re.compile(r" [+-]\d\d:\d\d ")


def _c3_block_lines(b, fails, worst):
    lab = b.get("label")
    if b.get("refused"):
        return
    inc = b.get("incidents") or []
    if len(inc) != 1:
        fails.append("%s: %d incidents over the block %s..%s (want ONE)" % (lab, len(inc), b.get("utcStart"), b.get("utcEnd")))
        return
    i = inc[0]
    worst["n"] += 1
    delta = float(i["gapS"]) - float(b["blockedS"])
    worst["dLo"], worst["dHi"] = min(worst["dLo"], delta), max(worst["dHi"], delta)
    if not (-C3_ROUND_S <= delta <= C3_MONO_TOL_S):
        fails.append("%s: gapS %s against blockedS %s (want within -%s..+%s)" % (lab, i["gapS"], b["blockedS"], C3_ROUND_S,
                                                                             C3_MONO_TOL_S))
    if i.get("kind") != "incident":
        fails.append("%s: kind %r" % (lab, i.get("kind")))
    if not (isinstance(i.get("quietPhase"), str) and i["quietPhase"]):
        worst["noPhase"].append("%s(%.3fs)" % (lab, float(b["blockedS"])))
    elif "blocked in " not in (i.get("rendered") or ""):
        fails.append("%s: the rendered row has no 'blocked in': %s" % (lab, (i.get("rendered") or "")[:120]))
    if not _C3_OFFSET.search(i.get("rendered") or ""):
        fails.append("%s: the rendered row has no local time with offset: %s" % (lab, (i.get("rendered") or "")[:80]))
    if i.get("game") != b.get("game"):
        fails.append("%s: incident game %r, current game %r" % (lab, i.get("game"), b.get("game")))
    c = b.get("contain")
    if not c:
        fails.append("%s: no window of game %s contains [mono-gapS, mono] = [%s, %s]" % (
            lab, b.get("game"), i.get("gapStartMono"), i.get("mono")))
        return
    worst["slack"] = min(worst["slack"], c["slack"])
    worst["share"] = max(worst["share"], c["simShare"] if c.get("simShare") is not None else 0)
    if c["slack"] < -C3_ROUND_S:
        fails.append("%s: the window [%s, %s] misses the gap by %.3f s" % (lab, c["monoStart"], c["monoEnd"], -c["slack"]))
    if c.get("simShare") is None or c["simShare"] > 1:
        fails.append("%s: containing window simShare %r (want <= 1)" % (lab, c.get("simShare")))


def v_TPSC3(d):
    if d.get("platform") != "nt":
        return 2, ("needs python.exe on the game's machine (the record files, taskkill and the observer's process probe); "
                   "os.name %r" % d.get("platform"))
    fails, gaps = [], []
    if d.get("aborted"):
        gaps.append("aborted: %s" % d["aborted"])
    # item 1: two cold launches with no client, each read from disk before any call
    i1 = d.get("item1") or []
    for c in i1:
        lab = c.get("label")
        if not c.get("segment"):
            fails.append("%s: no record segment of the new pid %s in %s" % (lab, c.get("pid"), d.get("recordDir")))
            continue
        if c.get("startedBy") != "bridge-registration":
            fails.append("%s: session row startedBy %r (want bridge-registration)" % (lab, c.get("startedBy")))
        if c.get("sampler") != "complete":
            fails.append("%s: session row install.sampler %r (want complete)" % (lab, c.get("sampler")))
        hb = c.get("hbs") or []
        seqs = [h.get("hbSeq") for h in hb]
        if len(hb) < C3_HB_READS:
            fails.append("%s: %d heartbeat reads (want %d)" % (lab, len(hb), C3_HB_READS))
        elif any(not isinstance(s, int) for s in seqs) or any(b <= a for a, b in zip(seqs, seqs[1:])):
            fails.append("%s: heartbeat hbSeq %s does not rise %.0f s apart" % (lab, seqs, C3_HB_GAP_S))
        if any(h.get("scene") != "menu" for h in hb):
            fails.append("%s: heartbeat scenes %s (want menu)" % (lab, [h.get("scene") for h in hb]))
    if len(i1) < 2:
        gaps.append("item 1 read on %d of 2 cold launches" % len(i1))
    games = dict((g.get("label"), g) for g in d.get("games") or [])
    for lab in C3_GAMES:
        g = games.get(lab)
        if g is None:
            gaps.append("%s not reached" % lab)
            continue
        if g.get("why"):
            gaps.append("%s: %s" % (lab, g["why"]))
            continue
        if not g.get("row"):
            fails.append("%s: no game row %s" % (lab, g.get("wantSeq")))
            continue
        if g["row"].get("game") != g.get("wantSeq") or g["row"].get("save") != g.get("wantSave"):
            fails.append("%s: game row game %r save %r (want %r, %r)" % (lab, g["row"].get("game"), g["row"].get("save"),
                                                                      g.get("wantSeq"), g.get("wantSave")))
        if (g.get("windows") or 0) < 1:
            fails.append("%s: no gameplay window of game %s" % (lab, g.get("wantSeq")))
    # item 2: the blocks
    blocks = d.get("blocks") or []
    want = len(C3_RUN_BLOCKS) + len(C3_EDGE_BLOCKS) + 1 + 1 + len(C3_LONG_BLOCKS)
    refused = [b.get("label") for b in blocks if b.get("refused")]
    if refused:
        gaps.append("jawa/tps_test_block refused: %s (%s)" % (refused[:3], blocks[0].get("refused")))
    if len(blocks) < want:
        gaps.append("%d of %d blocks run" % (len(blocks), want))
    worst = {"n": 0, "dLo": 9e9, "dHi": -9e9, "slack": 9e9, "share": 0.0, "noPhase": []}
    for b in blocks:
        _c3_block_lines(b, fails, worst)
    if worst["noPhase"]:
        fails.append("%d of %d hitches have no 'blocked in' phase (quietPhase empty): %s" % (
            len(worst["noPhase"]), worst["n"], ", ".join(worst["noPhase"][:8])))
    st = d.get("strict")
    if not st:
        gaps.append("no strict scan")
    elif st.get("bad"):
        fails.append("strict parse: %d bad complete lines in %d files (%d lines): %s" % (st["bad"], st["files"], st["lines"],
                                                                                     st.get("badSample")))
    # the save
    saves = d.get("saves") or []
    big = [s for s in saves if s.get("saveS") is not None and s["saveS"] > C3_GAP_S + C3_ROUND_S]
    for s in saves:
        inc = s.get("incidents") or []
        if s.get("saveS") is None:
            fails.append("save %s: no save row" % s.get("label"))
            continue
        if len(inc) > 1 or (s in big and len(inc) != 1):
            fails.append("save %s (saveS %s): %d incidents (want %s)" % (s.get("label"), s["saveS"], len(inc),
                                                                        "ONE" if s in big else "at most one"))
        for i in inc:
            if i.get("type") != "longevent" or float(i.get("explainedS") or 0) < C3_EXPLAINED * float(i["gapS"]):
                fails.append("save %s (saveS %s): incident %s gapS %s explainedS %s (want longevent, >= %.0f%% explained)" % (
                    s.get("label"), s["saveS"], i.get("type"), i.get("gapS"), i.get("explainedS"), 100 * C3_EXPLAINED))
    if not big:
        gaps.append("no save longer than %.1f s (longest %s of %d saves; %s)" % (
            C3_GAP_S, max([s.get("saveS") or 0 for s in saves] or [None]), len(saves), d.get("rampWhy")))
    # the hang and kill
    h = d.get("hang") or {}
    if not h:
        gaps.append("no hang")
    else:
        hb = h.get("hbs") or []
        if len(hb) < C3_HANG_READS:
            gaps.append("hang: %d heartbeat reads (want %d)" % (len(hb), C3_HANG_READS))
        else:
            wm = [x["watchdogMono"] for x in hb]
            wu = [x["watchdogEp"] for x in hb]
            bm = [x["mainBeatMono"] for x in hb]
            bu = [x["mainBeatEp"] for x in hb]
            sil = [x["silentS"] for x in hb]
            h["beatSpread"] = max(bu) - min(bu)
            if any(b <= a for a, b in zip(wm, wm[1:])) or any(b <= a for a, b in zip(wu, wu[1:])):
                fails.append("hang: watchdogMono %s / watchdogUtc do not advance" % wm)
            if max(bm) - min(bm) > 1e-6 or h["beatSpread"] > C3_BEAT_JITTER_S:
                fails.append("hang: the main beat moved (mainBeatMono %s, mainBeatUtc spread %.3f s, limit %s)" % (
                    bm, h["beatSpread"], C3_BEAT_JITTER_S))
            if any(b <= a for a, b in zip(sil, sil[1:])):
                fails.append("hang: silentS %s does not rise" % sil)
        if (h.get("silenceRows") or 0) < C3_SILENCE_MIN:
            fails.append("hang: %s silence rows (want >= %d)" % (h.get("silenceRows"), C3_SILENCE_MIN))
        if not h.get("killed"):
            gaps.append("hang: the game was not killed (%s)" % h.get("killWhy"))
        elif h.get("observerErr"):
            gaps.append("hang: observer pass failed: %s" % h["observerErr"])
        elif h.get("observerRows") != 1:
            fails.append("hang: %s exited-without-shutdown observer rows for session %s (want ONE; pass findings %s)" % (
                h.get("observerRows"), h.get("session"), h.get("findings")))
        if h.get("observerRowsAfter") is None:
            gaps.append("hang: observer.jsonl not reread after the relaunch")
        elif h.get("observerRowsAfter") < 1:
            fails.append("hang: the exited-without-shutdown row is gone after the relaunch")
        ret = h.get("retention") or {}
        if not ret.get("patterns") or not ret.get("sane"):
            gaps.append("retention: deletion patterns not read (%s)" % ret)
        elif ret.get("hits"):
            fails.append("retention: observer.jsonl matches deletion pattern(s) %s: it will not be on disk the next day" % ret["hits"])
    # the kills
    kills = dict((k.get("label"), k) for k in d.get("kills") or [])
    for lab in C3_KILLS:
        k = kills.get(lab)
        if not k or not k.get("killed"):
            gaps.append("%s not run (%s)" % (lab, (k or {}).get("why")))
            continue
        fs = k.get("files") or []
        for n, f in enumerate(fs):
            if f["bad"]:
                fails.append("%s: %s has %d bad complete lines (glued or torn mid-file)" % (lab, f["name"], f["bad"]))
            if f["torn"] and n != len(fs) - 1:
                fails.append("%s: torn line in %s, not the session's last file" % (lab, f["name"]))
            if f["bytes"] > C3_SEGMENT_BYTES:
                fails.append("%s: %s is %d bytes (limit %d)" % (lab, f["name"], f["bytes"], C3_SEGMENT_BYTES))
        if lab == "K4-after-rotation" and len(fs) < 2:
            gaps.append("%s: the segment never rotated (%d files)" % (lab, len(fs)))
        if lab == "K3-segment-full" and (not fs or fs[-1]["bytes"] < C3_SEGMENT_BYTES - 2 * C3_MARK_CHARS):
            gaps.append("%s: the segment stood at %s bytes, not within two marks of %d" % (
                lab, fs[-1]["bytes"] if fs else None, C3_SEGMENT_BYTES))
    rb = d.get("readback")
    if not rb:
        gaps.append("no read-back of the killed sessions")
    else:
        if rb.get("replayed") or rb.get("conflicts"):
            fails.append("read-back: replayed %s, conflicts %s (want 0)" % (rb.get("replayed"), rb.get("conflicts")))
        if rb.get("malformed") != rb.get("torn"):
            fails.append("read-back: malformed %s, torn tails %s (want malformed from the torn tail only)" % (
                rb.get("malformed"), rb.get("torn")))
    if fails:
        return 1, "; ".join(fails[:12]) + ("; ... %d more" % (len(fails) - 12) if len(fails) > 12 else "")
    if gaps:
        return 2, "; ".join(gaps[:10])
    rb = d["readback"]
    return 0, (
        "item 1 on %d cold launches (no client: session row bridge-registration/complete, %d menu heartbeats each), "
        "%d games with their seq and label; %d hitches/blocks ONE incident each: gapS-blockedS worst %.3f..%.3f s "
        "(limit -%s..+%s), window slack worst %.3f s (limit -%s), simShare worst %.3f (limit 1), all 'blocked in' with "
        "offset; strict scan %d lines / %d files 0 bad; %d saves, %d over %.1f s each ONE longevent; hang: %d hb reads "
        "beat spread %.3f s (limit %s), %d silence rows, ONE exited-without-shutdown row, still there after the relaunch, "
        "no deletion pattern of %d matches it; %d kills: read-back of %d files replayed 0 conflicts 0 malformed %d = "
        "torn %d, seqMissing %s" % (
            len(i1), C3_HB_READS, len(games), worst["n"], worst["dLo"], worst["dHi"], C3_ROUND_S, C3_MONO_TOL_S,
            worst["slack"], C3_ROUND_S, worst["share"], st["lines"], st["files"], len(saves), len(big), C3_GAP_S,
            len(h["hbs"]), h["beatSpread"], C3_BEAT_JITTER_S, h["silenceRows"], len(h["retention"]["patterns"]),
            len(kills), rb.get("files"), rb["malformed"], rb["torn"], rb.get("seqMissing")))


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


PEN_PIN_TICKS = 60000          # jawa/pen_pin's and the artboard stager's pin: a Wait started directly, no think node
PEN_LATE_TICKS = 9000          # the second reading: several of the longest designed shade rests (RM_SunHeatExtension
#                                restTicks 600-1500, RM_JobGiver_ShadeHop) after the 600-tick one


def _hist(xs):
    out = {}
    for x in xs:
        out[str(x)] = out.get(str(x), 0) + 1
    return out


def pen_job_class(job):
    """-> 'pin' (the 60000-tick pin: a Wait with no think-tree giver), 'rest' (a Wait a think node gave: the animal's own
    behaviour, e.g. a shade rest), 'none' or 'other'. Reads jawa/pawn_census's job row."""
    if not isinstance(job, dict) or not job.get("def"):
        return "none"
    if job.get("def") != "Wait":
        return "other"
    if not job.get("giver"):
        return "pin"
    return "rest"


def _pen_jobs(L, ids):
    """-> {id: census job row} for ids (batches of 80, the census's own row cap is higher)."""
    out = {}
    for k in range(0, len(ids), 80):
        for r in L.call("jawa/pawn_census", ids=",".join(ids[k:k + 80])).get("pawns") or []:
            out[_bare(r.get("id") or r.get("pawn"))] = r.get("job")
    return out


def g_PEN2(L):
    import glob
    import shutil
    import subprocess
    import rmpaths
    from game_paths import SAVES
    from await_lifecycle import await_lifecycle
    fx = rmpaths.rm_win("fixtures") if os.name == "nt" else rmpaths.rm_str("fixtures")
    sites = sorted(glob.glob(os.path.join(fx, "NS_Pyrelands_site_*.rws")))
    if not sites:
        return {"why": "no NS_Pyrelands_site_*.rws fixture in %s" % fx}
    site, review = "bundle_pen2_site", "bundle_pen2_review_%d" % int(time.time())
    shutil.copyfile(sites[-1], os.path.join(SAVES, site + ".rws"))
    hr = os.path.join(HERE, "..", "..", "..", "Pyrelands", "human_review.py")
    try:
        # the review keeper save is made now, on this list (a keeper of an older list does not load: 2026-11-25)
        b = subprocess.run([sys.executable, hr, "--build", "--load", site, "--save", "--name", review],
                           capture_output=True, text=True, timeout=5400, stdin=subprocess.DEVNULL)  # hang guard
        m = re.search(r"^save (\S+): ok=True", b.stdout or "", re.M)
        if b.returncode != 0 or not m:
            return {"why": "human_review.py --build --save did not save a keeper (exit %d): %s" % (
                b.returncode, ((b.stdout or "") + (b.stderr or ""))[-300:])}
        review = m.group(1)
        L.call("rimworld/go_to_main_menu")                     # loading over a live game NREs (human_review Review.load)
        if not await_lifecycle(lambda t, **k: L.call(t, **k), "menu", 120).ok:
            return {"why": "never reached the main menu before loading %s" % review}
        r = L.call("rimworld/load_game_ready", saveName=review, readiness="playable", timeoutMs=900000,
                   pauseIfNeeded=True)
        if not _ok(r):
            return {"why": "the review keeper save did not load: %s" % json.dumps(r)[:200]}
    finally:
        for n in [site, review]:                               # the proof's own saves, never anyone's keeper
            for f in glob.glob(os.path.join(SAVES, n + ".rws")):
                os.remove(f)
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "Pyrelands"))
    import human_review as HR
    S = HR.station_list()
    rects = [HR.footprint(s) for s in HR.pen_stations(S)]
    rstr = HR.pen_rects(S)
    before = dict((_bare(p.get("pawn")), p) for p in L.call("jawa/pen_pin", rects=rstr, restore=False).get("pawns") or [])
    ids0 = sorted(before)
    jobs0 = _pen_jobs(L, ids0)                                   # the known-bad control: all of them on the pin now
    rel = L.call("jawa/pen_release", rects=rstr)                 # exactly human_review.py --release-pens (Review.pens)
    jobs1 = _pen_jobs(L, ids0)                                   # paused, at once: whose behaviour drives each one now
    L.call("rimworld/step_game_ticks", ticks=600, pauseFirst=True)
    now600 = dict((_bare(p.get("id")), p) for p in L.call("jawa/list_pawns").get("pawns") or [])
    L.call("rimworld/step_game_ticks", ticks=PEN_LATE_TICKS - 600, pauseFirst=True)
    now = dict((_bare(p.get("id")), p) for p in L.call("jawa/list_pawns").get("pawns") or [])
    still = [i for i in ids0 if (now.get(i, {}).get("x"), now.get(i, {}).get("z")) == (before[i].get("x"), before[i].get("z"))]
    jobs2 = _pen_jobs(L, still) if still else {}                 # read before the pin: what holds the unmoved
    pin = L.call("jawa/pen_pin", rects=rstr, restore=True)       # exactly human_review.py --pin-pens
    pinned = dict((_bare(p.get("pawn")), p) for p in pin.get("pawns") or [])

    def rect_of(x, z):
        for (rx, rz, w, h) in rects:
            if rx <= x < rx + w and rz <= z < rz + h:
                return (rx, rz, w, h)
        return None

    ids = sorted(before)
    moved, moved600, outside, facing = [], [], [], []
    for i in ids:
        b, n = before[i], now.get(i) or {}
        home = rect_of(b.get("x"), b.get("z"))
        if (n.get("x"), n.get("z")) != (b.get("x"), b.get("z")):
            moved.append(i)
        n6 = now600.get(i) or {}
        if (n6.get("x"), n6.get("z")) != (b.get("x"), b.get("z")):
            moved600.append(i)
        if home is None or rect_of(n.get("x"), n.get("z")) != home:
            outside.append("%s at %s,%s" % (i, n.get("x"), n.get("z")))
        held = any(_bare(h.get("pawn")) == i and " holds " in str(h.get("reason")) for h in pin.get("homeRefused") or [])
        if not held and str((pinned.get(i) or {}).get("rotation")) != str(b.get("rotation")):
            facing.append("%s: %s -> %s" % (i, b.get("rotation"), (pinned.get(i) or {}).get("rotation")))
    unmoved = [i for i in ids if i not in moved]
    kinds = dict((_bare(r.get("pawn")), r.get("kind")) for r in rel.get("pawns") or [])
    detail = {}
    for i in unmoved:            # what holds an unmoved animal: the reading that classes a FAIL (mod, check, scene)
        j = jobs2.get(i)
        key = "%s/%s/%s" % (kinds.get(i), (j or {}).get("def"), (j or {}).get("giver"))
        detail[key] = detail.get(key, 0) + 1
    return {"save": review, "selected": rel.get("selected"), "released": rel.get("released"),
            "jobsAfterRelease": rel.get("jobsAfter"), "unmovedDetail": detail, "moved600": moved600,
            "lateTicks": PEN_LATE_TICKS, "pinBefore": [i for i in ids if pen_job_class(jobs0.get(i)) == "pin"],
            "pinAfter": [i for i in ids if pen_job_class(jobs1.get(i)) == "pin"],
            "giversAfter": _hist([(jobs1.get(i) or {}).get("giver") or (jobs1.get(i) or {}).get("def") for i in ids]),
            "notReleased": rel.get("notReleased"), "ids": ids, "moved": moved, "outside": outside,
            "facingWrong": facing, "returnedHome": pin.get("returnedHome"),
            "homeOccupied": [_bare(h.get("pawn")) for h in pin.get("homeRefused") or [] if " holds " in str(h.get("reason"))]}


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


# ---- TPSC3 gatherer: runs outside main's one Session (it kills and relaunches the game five times)
C3_LOAD_SAVE = "bundle_tps_c3_load"          # our own: the proof's base save (deleted at the end)
C3_RAMP_SAVE = "bundle_tps_c3_ramp"          # our own: the ramp's save (deleted at the end)
C3_RAMP_TARGET_S = 3.0                       # our own: a save comfortably past the 2 s gap (bar: GapSeconds)
C3_RAMP_STEPS, C3_RAMP_BUDGET_S = 40, 900    # our own: the ramp's caps
# one item, one plant and two filths per cell (an item displaces items, a plant wipes plants). Two layers saved in
# 1.80 s at the whole 250x250 map in J20261126T003734Z-db96b8 (3.10 s in J20261126T000829Z-98bb6f, saves taken inside
# spawn stalls): never past the 2 s gap, so the ramp has four layers (Core defNames, ThingDefs_Misc/Filth_Various.xml)
C3_RAMP_DEFS = ("Steel", "Plant_Grass", "Filth_Dirt", "Filth_RubbleRock")
C3_FILL_SMALL = 2000                         # our own: the fine fill mark, to stand within C3_FILL_SLACK of the boundary
C3_FILL_SLACK = 4096
C3_SETTLE_S = 3.0                            # our own: frames resume between a stalling call and the save after it


class _C3Stop(Exception):
    pass


class _C3S:
    """A bridge client for the CURRENT game (resolve_endpoint reads each relaunch's port and token)."""
    def __init__(self, timeout):
        import rimbridge_client as rb
        h, p, t = rb.resolve_endpoint()
        self.c = rb.RimBridge(h, p, t, timeout=timeout, client_name="bridge_bundle_proof.py TPSC3")

    def __enter__(self):
        self.c.__enter__()
        return self

    def __exit__(self, *e):
        return self.c.__exit__(*e)

    def call(self, tool, **p):
        return self.c.call(tool, p)


def _c3_files(T, rdir, session=None, pid=None):
    """[(startUtc, seg, path, session)] of the record's segments, in write order."""
    out = []
    for n in os.listdir(rdir):
        m = T.SEGMENT_RE.match(n)
        if not m or (session and m.group(2) != session) or (pid is not None and m.group(3) != str(pid)):
            continue
        out.append((m.group(1), int(m.group(4)), os.path.join(rdir, n), m.group(2)))
    return sorted(out)


def _c3_paths(T, rdir, session):
    return [f[2] for f in _c3_files(T, rdir, session=session)]


def _c3_read(T, paths):
    """-> (valid placed rows, per-file scan {name, bytes, lines, bad, torn, badSample}) with the strict parser."""
    rows, scan = [], []
    for p in paths:
        f = {"name": os.path.basename(p), "bytes": 0, "lines": 0, "bad": 0, "torn": False, "badSample": None}
        scan.append(f)
        try:
            with open(p, "rb") as fh:
                data = fh.read()
        except OSError as e:
            f["err"] = str(e)[:120]
            continue
        f["bytes"] = len(data)
        parts = data.split(b"\n")
        f["torn"] = bool(parts.pop())               # bytes after the last newline: a line not finished
        for raw in parts:
            if not raw.strip():
                continue
            f["lines"] += 1
            try:
                r = T.loads_strict(raw.decode("utf-8"))
            except ValueError:                      # UnicodeDecodeError is a ValueError
                f["bad"] += 1
                f["badSample"] = f["badSample"] or raw[:120].decode("utf-8", "replace")
                continue
            if T._valid(r):
                T.place(r, T._epoch(r["utc"]))
                rows.append(r)
    return rows, scan


def _c3_launch(d, label, no_ping):
    bt = os.path.normpath(os.path.join(HERE, "..", "..", "..", "bridgetools"))
    if bt not in sys.path:
        sys.path.insert(0, bt)
    import launch_ready as LR
    import load_policy
    pol_all = load_policy.load()
    name = load_policy.profile_name(load_policy.active_count_from_modsconfig(), pol_all)
    pol = dict(pol_all["profiles"][name], name=name)
    env = LR.RealEnv()
    if no_ping:     # item 1: no bridge client at all, so the launcher's own ping is not made either
        env.ping = lambda port, token: (True, "not called (item 1: a cold launch with no bridge client)")
    r = LR.run(env, pol, kill_existing=True, log=lambda m: None)
    d.setdefault("launches", []).append({"label": label, "verdict": r.get("verdict"), "pid": r.get("pid"),
                                         "why": (r.get("why") or "")[:200]})
    if r.get("verdict") != "READY":
        raise _C3Stop("%s: launch_ready %s: %s" % (label, r.get("verdict"), (r.get("why") or "")[:200]))
    return r


def _c3_kill(pid):
    import subprocess
    import game_instance
    try:
        import signal
        os.kill(pid, signal.SIGTERM)                # Windows: TerminateProcess, at once
    except OSError:
        subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True, timeout=60)
    t0 = time.time()
    while time.time() - t0 < 60:
        try:
            if not game_instance.alive([pid]):
                return True
        except Exception:                           # noqa: BLE001 - Blind: read again
            pass
        time.sleep(0.5)
    return False


def _c3_hb(T, rdir, session):
    p = os.path.join(rdir, "hb_%s.json" % session)
    for _ in range(5):                              # the writer replaces the file: a read can meet the swap
        try:
            with open(p, encoding="utf-8") as fh:
                return T.loads_strict(fh.read()), os.path.getmtime(p)
        except (OSError, ValueError):
            time.sleep(0.2)
    return None, None


def _c3_save_json(d):
    try:
        import rmpaths
        out = rmpaths.rm_win("scratch", "tpsc3")
    except Exception:                               # noqa: BLE001
        import tempfile
        out = os.path.join(tempfile.gettempdir(), "tpsc3")
    try:
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "tpsc3.json"), "w", encoding="utf-8") as fh:
            json.dump(d, fh, indent=1, default=str)
        d["evidence"] = os.path.join(out, "tpsc3.json")
    except OSError:
        pass


def _c3_item1(T, d, rdir, label, r):
    """Item 1, read from disk only: the new pid's segment, its session row, three menu heartbeats."""
    import calendar
    pid, t0 = r["pid"], r["launched_at"]
    c = {"label": label, "pid": pid}
    d["item1"].append(c)
    end = time.time() + 90
    while time.time() < end:
        fs = [f for f in _c3_files(T, rdir, pid=pid)
              if calendar.timegm(time.strptime(f[0], "%Y%m%dT%H%M%SZ")) >= t0 - 60]
        if fs:
            c["session"], c["segment"] = fs[0][3], os.path.basename(fs[0][2])
            rows, _ = _c3_read(T, _c3_paths(T, rdir, c["session"]))
            s = [x for x in rows if x.get("kind") == "session"]
            if s:
                c["startedBy"], c["sampler"] = s[0].get("startedBy"), (s[0].get("install") or {}).get("sampler")
                c["menuRows"] = sum(1 for x in rows if x.get("kind") == "menu")
                break
        time.sleep(1)
    if not c.get("session"):
        return None
    c["hbs"], c["preMenuHbs"] = [], 0
    # the heartbeat's scene is "" until the main thread's first frame at the menu (JawaBenchTpsWatchdog._scene):
    # the session row can precede it (J20261126T000829Z-98bb6f cold E read '' first). Item 1's three reads are
    # MENU heartbeats, so they start at the first menu one; a game that never reaches the menu leaves none (red).
    end = time.time() + 120
    while time.time() < end:
        hb, _mt = _c3_hb(T, rdir, c["session"])
        if hb and hb.get("scene") == "menu":
            break
        c["preMenuHbs"] += 1
        time.sleep(1)
    for k in range(C3_HB_READS):
        if k:
            time.sleep(C3_HB_GAP_S)
        hb, _mt = _c3_hb(T, rdir, c["session"])
        if hb:
            c["hbs"].append({"hbSeq": hb.get("hbSeq"), "scene": hb.get("scene")})
    return c["session"]


def _c3_game(T, d, rdir, sess, label, seq, save, why=None):
    g = {"label": label, "wantSeq": seq, "wantSave": save, "row": None, "windows": 0}
    d["games"].append(g)
    if why:
        g["why"] = why
        return g
    end = time.time() + 60
    while time.time() < end:
        rows, _ = _c3_read(T, _c3_paths(T, rdir, sess))
        g["allGames"] = [(x.get("game"), x.get("save")) for x in rows if x.get("kind") == "game"]
        gr = [x for x in rows if x.get("kind") == "game" and x.get("game") == seq]
        if gr:
            g["row"] = {"game": gr[0].get("game"), "save": gr[0].get("save"), "ticksGame": gr[0].get("ticksGame")}
            g["windows"] = sum(1 for x in rows if x.get("kind") == "sample" and x.get("game") == seq)
            if g["windows"]:
                break
        time.sleep(2)
    return g


def _c3_speed(s, speed):
    from common import call
    return call(s, "rimworld/set_time_speed", speed=speed)


def _c3_block(s, d, label, secs, seq):
    from common import call
    b = {"label": label, "requestedS": secs, "game": seq}
    d["blocks"].append(b)
    try:
        r = call(s, "jawa/tps_test_block", seconds=secs)
    except Exception as e:                          # noqa: BLE001
        b["refused"] = "%s: %s" % (type(e).__name__, str(e)[:160])
        return b
    if not r.get("success"):
        b["refused"] = str(r.get("message") or r.get("error") or r)[:160]
        return b
    b.update(blockedS=r.get("blockedS"), utcStart=r.get("utcStart"), utcEnd=r.get("utcEnd"))
    time.sleep(2)                                   # bar: ONE incident per block; the next block starts apart from it
    return b


def _c3_attach(T, rdir, sess, blocks, tz):
    rows, _ = _c3_read(T, _c3_paths(T, rdir, sess))
    incs = [x for x in rows if x.get("kind") == "incident"]
    wins = [x for x in rows if x.get("kind") == "sample" and x.get("monoStart") is not None and x.get("monoEnd") is not None]
    for b in blocks:
        if b.get("refused") or b.get("utcStart") is None or "incidents" in b:
            continue
        a, z = T._epoch(b["utcStart"]) - C3_MONO_TOL_S, T._epoch(b["utcEnd"]) + C3_MONO_TOL_S
        mine = [i for i in incs if i["_t0"] <= z and i["_t"] >= a]
        b["incidents"] = [{"gapS": i.get("gapS"), "kind": i.get("kind"), "type": i.get("type"),
                           "quietPhase": i.get("quietPhase"), "game": i.get("game"), "rendered": T.render_row(i, tz),
                           "mono": i.get("mono"), "gapStartMono": round(i["mono"] - i["gapS"], 3)} for i in mine]
        if len(mine) != 1:
            continue
        i, best = mine[0], None
        for w in wins:
            if w.get("game") != b["game"] or w.get("session") != sess:
                continue
            slack = min((i["mono"] - i["gapS"]) - w["monoStart"], w["monoEnd"] - i["mono"])
            if best is None or slack > best["slack"]:
                best = {"slack": round(slack, 3), "simShare": w.get("simShare"), "monoStart": w["monoStart"],
                        "monoEnd": w["monoEnd"], "gaps": w.get("gaps"), "stallS": w.get("stallS")}
        b["contain"] = best


def _c3_save(T, d, rdir, sess, name):
    from common import call
    t = time.time()
    with _C3S(900) as s:                            # budget: a save is seconds; the ramp stops near 3 s
        call(s, "rimworld/save_game", saveName=name)
    time.sleep(3)                                   # the writer's flush
    rows, _ = _c3_read(T, _c3_paths(T, rdir, sess))
    sv = [x for x in rows if x.get("kind") == "save" and x["_t"] >= t - 1]
    e = {"label": "%s#%d" % (name, len(d["saves"]) + 1), "saveS": None, "incidents": []}
    d["saves"].append(e)
    if not sv:
        return e
    r = sv[-1]
    e["saveS"] = r.get("saveS")
    # the save's own incident is the gap that ENDS with the save (its frame resumes within a frame of the save row);
    # one that merely overlaps may be the stall of the call before it (J20261126T000829Z-98bb6f: spawn_fill_area's
    # 10-17 s stalls ended just before the ramp's saves and were read as theirs)
    a, z = r["_t"] - (r.get("saveS") or 0) - C3_MONO_TOL_S, r["_t"] + C3_MONO_TOL_S
    e["incidents"] = [{"type": i.get("type"), "gapS": i.get("gapS"), "explainedS": i.get("explainedS")}
                      for i in rows if i.get("kind") == "incident" and a <= i["_t"] <= z]
    return e


def _c3_ramp(T, d, rdir, sess):
    """Saves of a growing map until one passes C3_RAMP_TARGET_S: layers of C3_RAMP_DEFS per cell, extrapolated; C3_RAMP_STEPS counts steps (spawn batches), not rects."""
    from common import call
    with _C3S(120) as s:
        mi = call(s, "jawa/map_info")
        _c3_speed(s, "Paused")
    X, Z = int(mi["sizeX"]), int(mi["sizeZ"])
    rects = [(x, z) for dn in C3_RAMP_DEFS for z in range(0, Z - 49, 50) for x in range(0, X - 49, 50)]
    defs = [dn for dn in C3_RAMP_DEFS for z in range(0, Z - 49, 50) for x in range(0, X - 49, 50)]
    t0, done, filled, steps = time.time(), 0, {}, 0
    base = _c3_save(T, d, rdir, sess, C3_RAMP_SAVE).get("saveS") or 0.0
    last = base
    while steps < C3_RAMP_STEPS and time.time() - t0 < C3_RAMP_BUDGET_S and last <= C3_RAMP_TARGET_S:
        if done >= len(rects):
            break
        slope = (last - base) / done if done else 0
        n = 2 if slope <= 0 else max(1, min(8, int((C3_RAMP_TARGET_S * 1.2 - last) / slope)))
        with _C3S(300) as s:
            for k in range(done, min(len(rects), done + n)):
                x, z = rects[k]
                r = call(s, "jawa/spawn_fill_area", rect="%d,%d,50,50" % (x, z), thingDef=defs[k])
                filled[defs[k]] = filled.get(defs[k], 0) + int(r.get("cellsFilled") or 0)
        done, steps = min(len(rects), done + n), steps + 1
        time.sleep(C3_SETTLE_S)                     # the spawns' own stall ends before the save starts
        last = _c3_save(T, d, rdir, sess, C3_RAMP_SAVE).get("saveS") or last
    d["rampWhy"] = "map %dx%d, %d of %d rects in %d steps (%s), cells filled %s, base save %.3f s, last %.3f s, %.0f s" % (
        X, Z, done, len(rects), steps, "+".join(C3_RAMP_DEFS), ",".join("%s %d" % kv for kv in sorted(filled.items())),
        base, last, time.time() - t0)


def _c3_hang(T, O, d, rdir, sess):
    import fnmatch
    import threading
    h = {"session": sess, "hbs": [], "silenceRows": 0}
    d["hang"] = h

    def blocker():
        try:
            with _C3S(C3_HANG_S + 60) as s:
                s.call("jawa/tps_test_block", seconds=C3_HANG_S)
        except Exception:                           # noqa: BLE001 - the kill ends the call
            pass
    th = threading.Thread(target=blocker, daemon=True)
    th.start()
    t0 = time.time()
    for at in (15, 25, 35, 45):                     # after the 10 s silence threshold, inside the 120 s block
        time.sleep(max(0, t0 + at - time.time()))
        hb, _mt = _c3_hb(T, rdir, sess)
        if hb:
            h["hbs"].append({"watchdogMono": hb.get("watchdogMono"), "watchdogEp": T._epoch(hb.get("watchdogUtc")),
                             "mainBeatMono": hb.get("mainBeatMono"), "mainBeatEp": T._epoch(hb.get("mainBeatUtc")),
                             "silentS": hb.get("silentS")})
    while time.time() < t0 + 80:                    # silence rows at 10 s, then every 30 s (SilenceRepeatSeconds)
        rows, _ = _c3_read(T, _c3_paths(T, rdir, sess))
        h["silenceRows"] = sum(1 for x in rows if x.get("kind") == "silence" and x["_t"] >= t0)
        if h["silenceRows"] >= C3_SILENCE_MIN:
            break
        time.sleep(2)
    pid = d["item1"][0]["pid"]
    h["killed"] = _c3_kill(pid) and time.time() < t0 + C3_HANG_S
    h["killWhy"] = "pid %s, %.0f s into the %.0f s block" % (pid, time.time() - t0, C3_HANG_S)
    th.join(30)
    h["settled"] = _c3_settle("jawa/tps_test_block", "TPSC3 hang: the block ran until the proof killed the game (pid %s)" % pid)
    _hb, mt = _c3_hb(T, rdir, sess)
    time.sleep(max(0, (mt or time.time()) + T.HB_FRESH_SECONDS + 1 - time.time()))
    p = O.one_pass()
    h["observerErr"], h["findings"] = p.get("error"), [f for f in p.get("findings") or [] if f.get("session") == sess]
    h["observerRows"] = _c3_observer_rows(T, rdir, sess)
    # retention: every deletion pattern of the record's writers, read from the source
    src = os.path.normpath(os.path.join(HERE, "..", "..", "..", "bridgetools", "JawaBench.BridgeTools"))
    pats = set()
    for n in os.listdir(src):
        if n.startswith("JawaBenchTps") and n.endswith(".cs"):
            for ln in open(os.path.join(src, n), encoding="utf-8", errors="replace"):
                if "Prune(" in ln or "GetFiles(" in ln or "EnumerateFiles(" in ln:
                    pats.update(p for p in re.findall(r'"([^"]*\*[^"]*)"', ln))
    ut = os.path.normpath(os.path.join(HERE, "..", ".."))
    py = [n for n in os.listdir(ut) if n.endswith(".py") and not n.startswith("selftest_")
          and any(("remove(" in ln or "unlink(" in ln) and "observer" in ln
                  for ln in open(os.path.join(ut, n), encoding="utf-8", errors="replace"))]
    h["retention"] = {"patterns": sorted(pats), "sane": any(fnmatch.fnmatch("tps_x_1_2_000.jsonl", p) for p in pats),
                      "hits": [p for p in sorted(pats) if fnmatch.fnmatch("observer.jsonl", p)] + py}


def _c3_settle(tool, note):
    """The kill cut this process's own call off mid-reply, so the client marked it INDETERMINATE and refuses every
    later mutation (J20261126T000829Z-98bb6f aborted at load_game_ready). Its outcome is known here: the block ran
    until the kill. Only THIS process's markers of THIS tool are settled; any other marker still refuses."""
    import rimbridge_client as rb
    n = 0
    for rec in rb.outstanding_indeterminate():
        if rec.get("tool") == tool and rec.get("pid") == os.getpid() and rec.get("cid"):
            rb.reconcile_resolve(rec["cid"], "applied", note)
            n += 1
    return n


def _c3_observer_rows(T, rdir, sess):
    n = 0
    try:
        with open(os.path.join(rdir, "observer.jsonl"), encoding="utf-8") as fh:
            for ln in fh:
                try:
                    r = json.loads(ln)
                except ValueError:
                    continue
                n += r.get("session") == sess and r.get("finding") == "exited-without-shutdown"
    except OSError:
        return None
    return n


def _c3_last_kind(path):
    try:
        with open(path, "rb") as fh:
            fh.seek(max(0, os.path.getsize(path) - 8192))
            lines = fh.read().split(b"\n")[:-1]
        return json.loads(lines[-1].decode("utf-8")).get("kind") if lines else None
    except (OSError, ValueError, IndexError):
        return None


def _c3_kill_row(T, d, rdir, label, sess, pid, why):
    ok = _c3_kill(pid)
    d["kills"].append({"label": label, "killed": ok, "why": why, "session": sess,
                       "files": _c3_read(T, _c3_paths(T, rdir, sess))[1]})


def _c3_fill(T, rdir, sess, rotate):
    """Marks until the session's open segment stands within C3_FILL_SLACK of SegmentBytes (or, rotate, past it)."""
    from common import call
    with _C3S(60) as s:
        for big in (True, False):
            mark = "x" * (C3_MARK_CHARS if big else C3_FILL_SMALL)
            for _ in range(400):                    # our own: 2 MiB / 2 KB marks plus margin
                cur = os.path.getsize(_c3_paths(T, rdir, sess)[-1])
                room = C3_SEGMENT_BYTES - cur
                if room < (2 * C3_MARK_CHARS if big else C3_FILL_SLACK):
                    break
                call(s, "jawa/telemetry_mark", why=mark)
                time.sleep(1.5)                     # the writer's flush, then measure again
        if rotate:
            call(s, "jawa/telemetry_mark", why="x" * C3_MARK_CHARS)


def g_TPSC3_cold():
    import tps_record as T
    import tps_observer as O
    import game_paths
    from common import call, ensure_map
    d = {"platform": os.name, "item1": [], "games": [], "blocks": [], "saves": [], "kills": []}
    if os.name != "nt":
        return d
    rdir = T.record_dir()
    d["recordDir"] = rdir
    T._tz(None)                                     # fails here when the zone database is missing (tzdata)
    tz = None                                       # render_row takes a zone NAME; None is DEFAULT_TZ
    sessions = []
    try:
        # A: cold launch, no client; item 1 from disk; then a new game
        r = _c3_launch(d, "A", no_ping=True)
        sa = _c3_item1(T, d, rdir, "cold A", r)
        if not sa:
            raise _C3Stop("cold A: no record segment of pid %s within 90 s" % r["pid"])
        sessions.append(sa)
        with _C3S(960) as s:                        # ensure_map waits up to 900 s
            why = ensure_map(s)
            d["profile"] = call(s, "jawa/companion_handshake").get("effectiveProfile")
            _c3_speed(s, "Normal")
        _c3_game(T, d, rdir, sa, C3_GAMES[0], 1, "", why)
        _c3_save_json(d)
        # B: the blocks (Normal, edge sweep, Superfast, Paused, long)
        with _C3S(C3_LONG_BLOCKS[-1] + 120) as s:
            _c3_speed(s, "Normal")
            for x in C3_RUN_BLOCKS:
                _c3_block(s, d, "run %.2fs" % x, x, 1)
            for k, x in enumerate(C3_EDGE_BLOCKS):
                _c3_block(s, d, "edge %.2fs #%d" % (x, k // len(set(C3_EDGE_BLOCKS)) + 1), x, 1)
            _c3_speed(s, "Superfast")
            _c3_block(s, d, "superfast %.1fs" % C3_FAST_BLOCK, C3_FAST_BLOCK, 1)
            _c3_speed(s, "Paused")
            _c3_block(s, d, "paused %.1fs" % C3_PAUSED_BLOCK, C3_PAUSED_BLOCK, 1)
            _c3_speed(s, "Normal")
            for x in C3_LONG_BLOCKS:
                _c3_block(s, d, "long %.0fs" % x, x, 1)
        time.sleep(8)                               # the window holding the last gap closes (5 s cadence)
        _c3_attach(T, rdir, sa, d["blocks"], tz)
        _c3_save_json(d)
        # C: saves
        _c3_save(T, d, rdir, sa, C3_LOAD_SAVE)
        _c3_ramp(T, d, rdir, sa)
        _c3_save_json(d)
        # D: the hang and kill, the observer by hand
        _c3_hang(T, O, d, rdir, sa)
        _c3_save_json(d)
        # E: cold launch, no client; item 1; the observer again; loads; kill after a sample
        r = _c3_launch(d, "E", no_ping=True)
        se = _c3_item1(T, d, rdir, "cold E", r)
        if not se:
            raise _C3Stop("cold E: no record segment of pid %s within 90 s" % r["pid"])
        sessions.append(se)
        d["hang"]["observerRowsAfter"] = None
        p = O.one_pass()
        d["hang"]["observerRowsAfter"] = _c3_observer_rows(T, rdir, d["hang"]["session"])
        d["hang"]["observerAfterErr"] = p.get("error")
        with _C3S(960) as s:
            r1 = call(s, "rimworld/load_game_ready", saveName=C3_LOAD_SAVE, readiness="playable", timeoutMs=600000,
                      pauseIfNeeded=True)
            _c3_speed(s, "Normal")
        _c3_game(T, d, rdir, se, C3_GAMES[1], 1, C3_LOAD_SAVE, None if r1.get("success", True) else str(r1)[:160])
        with _C3S(960) as s:
            r2 = call(s, "rimworld/load_game_ready", saveName=C3_LOAD_SAVE, readiness="playable", timeoutMs=600000,
                      pauseIfNeeded=True)
            _c3_speed(s, "Normal")
        _c3_game(T, d, rdir, se, C3_GAMES[2], 2, C3_LOAD_SAVE, None if r2.get("success", True) else str(r2)[:160])
        with _C3S(960) as s:
            call(s, "rimworld/go_to_main_menu")
            from await_lifecycle import await_lifecycle
            await_lifecycle(lambda tool, **p: call(s, tool, **p), state="menu", deadline_s=300)
            why = ensure_map(s)
            _c3_speed(s, "Normal")
        _c3_game(T, d, rdir, se, C3_GAMES[3], 3, "", why)
        end, why = time.time() + 60, "no sample landed in 60 s"
        while time.time() < end:                    # K1: kill as soon as a sample is the last complete line
            if _c3_last_kind(_c3_paths(T, rdir, se)[-1]) == "sample":
                why = "killed right after a sample landed"
                break
            time.sleep(0.02)
        _c3_kill_row(T, d, rdir, C3_KILLS[0], se, r["pid"], why)
        _c3_save_json(d)
        # F1: kill just before the next sample
        r = _c3_launch(d, "F1", no_ping=False)
        f1 = [f for f in _c3_files(T, rdir, pid=r["pid"])][0][3]
        sessions.append(f1)
        with _C3S(960) as s:
            ensure_map(s)
            _c3_speed(s, "Normal")
            rep = call(s, "jawa/tps_report")
        d["reportDir"] = rep.get("recordDir")
        d["reportDirSame"] = bool(rep.get("recordDir")) and os.path.normcase(os.path.normpath(rep["recordDir"])) == \
            os.path.normcase(os.path.normpath(rdir))
        time.sleep(20)                              # four windows at the 5 s cadence
        rows, _ = _c3_read(T, _c3_paths(T, rdir, f1))
        ends = sorted(x["monoEnd"] for x in rows if x.get("kind") == "sample" and x.get("monoEnd") is not None)
        diffs = sorted(b - a for a, b in zip(ends, ends[1:]))
        cad = diffs[len(diffs) // 2] if diffs else 5.0
        n0 = sum(1 for x in rows if x.get("kind") == "sample")
        end, why = time.time() + 30, "no sample landed in 30 s"
        while time.time() < end:
            rows, _ = _c3_read(T, _c3_paths(T, rdir, f1))
            if sum(1 for x in rows if x.get("kind") == "sample") > n0:
                time.sleep(max(0, cad - 0.15))
                why = "killed %.2f s after a sample landed (cadence %.2f s)" % (cad - 0.15, cad)
                break
            time.sleep(0.05)
        _c3_kill_row(T, d, rdir, C3_KILLS[1], f1, r["pid"], why)
        # F2 and F3: a segment filled to its boundary, killed there and just after the rotation
        for lab, rot in ((C3_KILLS[2], False), (C3_KILLS[3], True)):
            r = _c3_launch(d, lab, no_ping=False)
            sf = _c3_files(T, rdir, pid=r["pid"])[0][3]
            sessions.append(sf)
            _c3_fill(T, rdir, sf, rot)
            why = "segment at %d bytes" % os.path.getsize(_c3_paths(T, rdir, sf)[-1])
            if rot:
                end = time.time() + 30
                while time.time() < end and len(_c3_paths(T, rdir, sf)) < 2:
                    time.sleep(0.02)
                why = "killed after rotation to %d files" % len(_c3_paths(T, rdir, sf))
            _c3_kill_row(T, d, rdir, lab, sf, r["pid"], why)
        _c3_save_json(d)
    except Exception as e:                          # noqa: BLE001 - a stop is a gap, never a verdict
        d["aborted"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    finally:
        try:
            killed = [d["hang"]["session"]] if d.get("hang", {}).get("killed") else []
            killed += [k["session"] for k in d["kills"] if k.get("killed")]
            if killed:
                import shutil
                import tempfile
                cp = tempfile.mkdtemp(prefix="tpsc3_")
                torn = 0
                for sess in killed:
                    for p in _c3_paths(T, rdir, sess):
                        shutil.copy2(p, cp)
                        with open(p, "rb") as fh:
                            fh.seek(max(0, os.path.getsize(p) - 1))
                            torn += fh.read(1) not in (b"\n", b"")
                rb = T.read_record(cp, now=time.time() + 86400)
                d["readback"] = {k: rb.get(k) for k in ("replayed", "conflicts", "malformed", "files", "seqMissing")}
                d["readback"]["torn"] = torn
                d["readback"]["seqMissing"] = str(d["readback"]["seqMissing"])[:120]
            scans = []
            for sess in sessions:
                scans += _c3_read(T, _c3_paths(T, rdir, sess))[1]
            d["strict"] = {"files": len(scans), "lines": sum(f["lines"] for f in scans),
                           "bad": sum(f["bad"] for f in scans),
                           "badSample": next((f["badSample"] for f in scans if f["badSample"]), None)}
        except Exception as e:                      # noqa: BLE001
            d["aborted"] = (d.get("aborted") or "") + " readback: %s: %s" % (type(e).__name__, str(e)[:200])
        try:
            _c3_launch(d, "restore", no_ping=False)   # leave the lane a READY game
        except Exception as e:                      # noqa: BLE001
            d["restoreErr"] = str(e)[:200]
        for n in (C3_LOAD_SAVE, C3_RAMP_SAVE):
            try:
                os.remove(os.path.join(game_paths.SAVES, n + ".rws"))
            except OSError:
                pass
        _c3_save_json(d)
    return d


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
    if clause == "TPSC3":
        try:
            d = g_TPSC3_cold()
        except Exception as e:                                  # noqa: BLE001 - a stop is a gap, not a verdict
            print("%s UNMEASURED: %s: %s" % (clause, type(e).__name__, str(e)[:300]))
            return 2
        rc, msg = verdict(clause, d)
        print("%s %s: %s" % (clause, ("PASS", "FAIL", "UNMEASURED")[rc], msg))
        return rc
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
