"""modcheck.quiet_site -- ONE shared "quiet isolated test site" profile (GPT review 2026-10-13 s3: rank 5 scoped
quiet-world profile, rank 6 modal broker, rank 10 environmental presets; owner 2026-10-13 by card: two suites --
isolated mechanism tests on quiet maps + a separate integration suite, all five DLCs loaded in both).

Every site builder (Pyrelands/northstar_site.py, the GSS/FlowWorks fresh-map paths, the quicktest helpers) applies
THIS instead of its own partial copy. It composes what already existed and READS BACK each piece:

    helpers.storyteller_off / random_events_off / quiet_world      storyteller, queue, threat scale, mental/disease, wild spawner
    helpers.kill_hostiles                                          hostile pawns removed by Vanish (no death action)
    jawa/quiet_site  (companion, new)                              hostile threat STRUCTURES (the vitals classifier) + proximity letters
    jawa/incident_queue_remove                                     selective drain of named queued incidents (StrangerInBlackJoin)
    jawa/window_list_close + rimworld/get_ui_layout/click_ui_target  modal broker with EXPLICIT handlers only
    helpers.restore_colonists                                      opt-in support-colonist guard (never on health/needs/damage/death rows)
    jawa/damage_log                                                attribution of any colonist harm (observation, not a control)

Rules (owner + GPT):
  * Controls are DECLARED PER ROW/SUITE: `QuietSite(session, suite="integration")` applies NOTHING and says so.
  * Every control carries what it could HIDE (CONTROLS[name]["hides"]); the receipt lists the controls applied, their
    read-back, and the hides column, so a row's evidence shows what it could not have seen.
  * A control never hides the mod under test: `keep_defs` spares its buildings, and the support guard refuses rows whose
    topic is health/needs/damage/death.
  * DebugSettings.enableStoryteller is a static NOT saved with the game: a load turns it back on. Re-apply after any load.
  * Every DLC stays loaded; nothing here removes content, it only quiets a map.

`session` is anything with call(tool, **params) -> dict (rimdrive Session, or rimdrive.fake.FakeWorld).
"""
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.append(_HERE)

import clockgate
import helpers as H

# ------------------------------------------------------------------ the controls, each with what it could hide
CONTROLS = {
    "storyteller_off": {
        "what": "DebugSettings.enableStoryteller=false, threatScale 0, no big threats, incident queue cleared",
        "hides": "storyteller-fired incidents incl. the mod's own IncidentDefs and conditions (seasonal flooding, "
                 "cinderfall), pacing, threat-point scaling",
        "items": ["TESTENV_FLOODS_HARDEN_SEASON_CRASHES_PARTY"]},
    "random_events_off": {
        "what": "random mental states and diseases off",
        "hides": "mood-break and disease interactions with the mod",
        "items": []},
    "wild_spawner_off": {
        "what": "wild-animal replenishment blocked (jawa/wild_spawner_block, dead-man)",
        "hides": "the mod's effect on ongoing wildlife arrival; mapgen wildlife is untouched",
        "items": []},
    "threat_structures_cleared": {
        "what": "hostile threat structures vanished at setup (vitals classifier: turret, spawner, dormant, condition "
                "causer, non-humanlike faction); keep_defs spared",
        "hides": "hive/infestation/mech-cluster interactions; insect-faction behaviour on the site",
        "items": ["TESTENV_HIVES_HARDEN_RIVER_MAP_SQUATTERS", "TESTENV_QUICKTEST_HIVES_HARDEN_EMPTY_NEST",
                  "TESTENV_MEGAPEDE_HARDEN_GATECRASHER"]},
    "hostiles_removed": {
        "what": "hostile pawns present at setup removed by Vanish (no death action, no corpse)",
        "hides": "combat interactions with the mod's things",
        "items": ["TESTENV_MEGAPEDE_HARDEN_GATECRASHER"]},
    "toxic_sources_cleared": {
        "what": "toxic sources removed at setup and read back: toxic game conditions ended, ToxGas cleared, POLLUTED terrain "
                "within TOXIC_SCAN_RADIUS of every colonist repainted to its clean counterpart (Biotech pollution gives "
                "ToxicBuildup to a pawn standing on it); the receipt also counts stacked 'Forced weather' controllers",
        "hides": "the mod's interaction with pollution, toxic fallout and tox gas near the colonists",
        "items": ["TESTENV_TOXIC_DIAGNOSE_RIVER_SITE_SNIFFLES"]},
    "proximity_letters_sent": {
        "what": "every CompProximityLetter marked sent (the mapgen void monolith's 'Fallen monolith')",
        "hides": "the Anomaly monolith discovery letter and any mod building's proximity letter",
        "items": ["TESTENV_MONOLITH_HARDEN_UNINVITED_GUEST"]},
    "queue_drain": {
        "what": "named queued incidents removed at every drain (default StrangerInBlackJoin: the colony-loss rescue "
                "is QUEUED by StorytellerComp_Triggered on the death and fires 180 ticks later through "
                "IncidentQueueTick, which runs even with the storyteller off)",
        "hides": "the end-of-colony rescue; a row ABOUT that rescue must not use this control",
        "items": ["TESTENV_STRANGER_JOINS_HARDEN_LET_IT_END"]},
    "modal_broker": {
        "what": "explicit window handlers only (MODAL_HANDLERS); an unknown force-pause window is CAPTURED and blocks "
                "the row, never closed blindly; the same window still open after its handler escalates",
        "hides": "the handled dialog's other choices (VEF new-faction: 'Do nothing' means the faction is not spawned)",
        "items": ["TESTENV_FACTION_DIALOG_HARDEN_FIVE_KNOCKS"]},
    "support_guard": {
        "what": "OPT-IN: support colonists' NEW injuries/heatstroke reversed at every drain (baseline delta), each "
                "repair recorded BEFORE it is made",
        "hides": "health, damage, heat, starvation and death on support colonists; refused for rows whose topic is "
                 "health/needs/damage/death (owner 2026-10-13 by card)",
        "items": ["TESTENV_BURROW_HEAT_HARDEN_COLONISTS_COOKED", "TESTENV_INJURY_HARDEN_WHO_HURT_CAIT"]},
}

PROFILES = {
    "isolated": ("storyteller_off", "random_events_off", "wild_spawner_off", "threat_structures_cleared",
                 "hostiles_removed", "toxic_sources_cleared", "proximity_letters_sent", "queue_drain", "modal_broker"),
    "integration": (),      # the integration suite runs the world as it is: no controls, said so in the receipt
}
TOXIC_SCAN_RADIUS = 14
TOXIC_CONDITION_WORDS = ("toxic",)          # ToxicFallout and any mod condition that says toxic
TOXIC_GASES = ("ToxGas",)
# Fresh-map settling: Divide flyers in flight and entity spawns land AFTER the setup read (TESTENV_QUICKTEST_DIAGNOSE_SPIKES_UNINVITED:
# 14 Toughspike/Fingerspike by tick ~135 on a map that read 0 threats). settle() advances in short chunks, draining each time.
SETTLE_CHUNK = 60
SETTLE_MAX_TICKS = 600
SETTLE_QUIET_CHUNKS = 3
GUARD_REFUSED_TOPICS = frozenset(["health", "needs", "damage", "death"])
# SeasonalFlooding (Odyssey IncidentDef, Misc, Map_PlayerHome; rimsage 1.6 source) is fired ONLY through the storyteller or
# the incident queue -- IncidentWorker_SeasonalFlooding just spawns the SeasonalFlood thing and its ThreatSmall letter -- so
# storyteller_off + this drain cover it (TESTENV_FLOODS_HARDEN_SEASON_CRASHES_PARTY). A row ABOUT flooding declares its own.
DRAIN_DEFS = ("StrangerInBlackJoin", "SeasonalFlooding")

# Known windows and their ONE approved handler. Value: ("click", label) clicks that button via the UI layout.
MODAL_HANDLERS = {
    # VEF on loading a save that lacks a mod's factions (RimUtinni Patches on NS_FlowWorks_TrialSite_v1: five knocks,
    # 2026-10-13). 'Do nothing' keeps the save's world as it is.
    "Dialog_NewFactionSpawning": ("click", "Do nothing"),
}
MODAL_MAX_ROUNDS = 64       # distinct windows answered per call (RimUtinni adds many factions)


def _wtype(w):
    return str(w.get("type") or w.get("typeName") or "")


class QuietSiteUnclean(RuntimeError):
    """The site could not be shown quiet (a control failed read-back, or a modal has no handler)."""


def _ok(r):
    return isinstance(r, dict) and r.get("success") is not False


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class QuietSite(object):
    """apply() once after the site exists (and again after any load); drain() after every advance chunk (advance() does
    it for you); verify() before scoring; restore() in finally. receipt() is the evidence the row records."""

    def __init__(self, session, suite="isolated", controls=None, keep_defs=(), topic=None, support_ids=None,
                 protect_support=False, row=None, drain_defs=DRAIN_DEFS, min_colonists=1):
        if suite not in PROFILES:
            raise ValueError("suite must be one of %s" % sorted(PROFILES))
        self.s = session
        self.suite = suite
        self.row = row
        self.topic = (topic or "").lower() or None
        self.keep_defs = tuple(keep_defs or ())
        self.drain_defs = tuple(drain_defs or ())
        self.controls = list(PROFILES[suite] if controls is None else controls)
        for c in self.controls:
            if c not in CONTROLS:
                raise ValueError("unknown control %r" % c)
        if suite == "integration" and self.controls:
            raise ValueError("the integration suite takes no controls (owner 2026-10-13: two suites)")
        if protect_support:
            if self.topic in GUARD_REFUSED_TOPICS:
                raise ValueError("support_guard refused: this row's topic is %r (owner 2026-10-13 by card)" % self.topic)
            if not self.topic:
                raise ValueError("support_guard needs a declared row topic (it is refused for health/needs/damage/death)")
            self.controls.append("support_guard")
        self.support_ids = list(support_ids or [])
        self.sleep = time.sleep
        self.min_colonists = min_colonists
        self.tx = None
        self.applied = {}           # control -> read-back evidence
        self.events = []            # every drain/modal/guard action, with the tick
        self.baseline = None
        self.problems = []

    # ---------------------------------------------------------------- apply
    def apply(self):
        if not self.controls:
            self.applied = {"_": "integration suite: no controls applied"}
            return self.receipt()
        H.pause(self.s)
        if self.tx is None:
            self.tx = H.SettingsTransaction(self.s).__enter__()
        on = set(self.controls)
        if "storyteller_off" in on or "random_events_off" in on or "wild_spawner_off" in on:
            q = H.quiet_world(self.s, self.tx, wild_spawner="wild_spawner_off" in on)
            self.applied["storyteller_off"] = q.evidence.get("readBack")
            self.applied["wild_spawner_off"] = q.evidence.get("wildSpawner")
            self.applied["random_events_off"] = "read back in storyteller_off readBack"
            if not q.verified:
                self.problems.append("quiet_world unverified: %s" % q.residue)
        if "modal_broker" in on:
            self.applied["modal_broker"] = self.modals()
        if "threat_structures_cleared" in on or "proximity_letters_sent" in on:
            r = self.s.call("jawa/quiet_site", action="apply", clearThreats="threat_structures_cleared" in on,
                            keepDefs=",".join(self.keep_defs), proximityLetters="proximity_letters_sent" in on)
            if not isinstance(r, dict) or r.get("success") is not True:
                self.problems.append("jawa/quiet_site apply: %s" % (str(r)[:300],))
            r = r if isinstance(r, dict) else {}
            if "threat_structures_cleared" in on:
                self.applied["threat_structures_cleared"] = {
                    "removed": [(x.get("def"), x.get("id")) for x in r.get("removed") or []],
                    "threatsAfter": r.get("threatsAfter"), "kept": r.get("kept"), "errors": r.get("errors")}
            if "proximity_letters_sent" in on:
                self.applied["proximity_letters_sent"] = {
                    "letters": [(x.get("def"), x.get("label"), x.get("sentBefore")) for x in r.get("letters") or []],
                    "unsentAfter": r.get("lettersUnsentAfter")}
        if "hostiles_removed" in on:
            k = H.kill_hostiles(self.s, self.support_ids)
            self.applied["hostiles_removed"] = {"acted": k.acted, "residue": k.residue}
            if not k.verified:
                self.problems.append("hostiles not all removed: %s" % k.residue)
        if "toxic_sources_cleared" in on:
            self.applied["toxic_sources_cleared"] = self.clear_toxic_sources()
        if "queue_drain" in on:
            self.applied["queue_drain"] = {"defs": list(self.drain_defs), "atApply": self._drain_queue()}
        if "support_guard" in self.controls:
            ids = self.support_ids or [r["id"] for r in H.read_pawns(self.s, health=False)
                                       if H.is_colonist(r) and not r["dead"]]
            self.support_ids = ids
            base = H.colonist_baseline(self.s)
            self.baseline = dict((k, v) for k, v in base.items() if k in set(ids))
            self.applied["support_guard"] = {"support": ids, "topic": self.topic}
        if self.problems:
            raise QuietSiteUnclean("; ".join(self.problems))
        return self.receipt()

    # ---------------------------------------------------------------- drain (after every chunk)
    def _drain_queue(self):
        removed = []
        for d in self.drain_defs:
            peek = self.s.call("jawa/incident_queue_peek") or {}
            if not any((q.get("defName") or "").lower() == d.lower() for q in peek.get("queue") or []):
                continue
            r = self.s.call("jawa/incident_queue_remove", defName=d, dryRun=False) or {}
            removed.append({"def": d, "removed": r.get("removedCount"), "ok": _ok(r)})
            if not _ok(r) or not r.get("removedCount"):
                self.problems.append("queue drain %s failed: %s" % (d, str(r)[:200]))
        return removed

    def drain(self, tick=None):
        """Run after every advance chunk. Records every action with the tick."""
        if not self.controls:
            return []
        acts = []
        if "queue_drain" in self.controls:
            for x in self._drain_queue():
                acts.append(dict(x, control="queue_drain"))
        if "modal_broker" in self.controls:
            m = self.modals()
            if m.get("handled") or m.get("unknown"):
                acts.append(dict(m, control="modal_broker"))
        acts.extend(self._arrival_sweep())
        if "support_guard" in self.controls and self.baseline is not None:
            # record the attempted harm BEFORE the repair (GPT s3.4)
            rows = dict((r["id"], r) for r in H.read_pawns(self.s))
            harm = []
            for pid, base in self.baseline.items():
                row = rows.get(pid)
                if row is None or row["dead"]:
                    harm.append((pid, "missing" if row is None else "DEAD"))
                    continue
                for h in row["health"]["hediffs"]:
                    if H.hediff_key(h) not in base and h["def"] in H.INJURY_DEFS:
                        harm.append((pid, "%s/%s" % H.hediff_key(h)))
            if harm:
                res = H.restore_colonists(self.s, self.baseline)
                acts.append({"control": "support_guard", "harmBeforeRepair": harm, "repaired": res.acted,
                             "residue": res.residue})
                if any(w == "DEAD" or w == "missing" for _, w in harm):
                    self.problems.append("support colonist lost: %s" % harm)
        for a in acts:
            a["tick"] = tick
            a["utc"] = _now()
        self.events.extend(acts)
        return acts

    # ---------------------------------------------------------------- toxic sources
    def clear_toxic_sources(self):
        """End toxic conditions, clear ToxGas, repaint polluted terrain near the colonists; READ BACK each. Every step is
        best-effort and reported (a tool that is missing is 'unavailable', never a crash); only what could be read is
        claimed. The receipt names the sources it found, which is the diagnosis the next ToxicBuildup surprise needs."""
        out = {"conditionsEnded": [], "gasCleared": [], "pollutedRepainted": 0, "pollutedLeft": None,
               "stackedWeatherControllers": None, "unavailable": []}
        wg, err = H._try_call(self.s, "jawa/weather_get")
        if wg is None:
            out["unavailable"].append("weather_get: %s" % err)
        else:
            conds = wg.get("conditions") or []
            out["stackedWeatherControllers"] = len([c for c in conds if isinstance(c, dict) and c.get("def") == "WeatherController"])
            for c in conds:
                nm = c if isinstance(c, str) else (c.get("def") or c.get("defName") or "")
                lab = "" if isinstance(c, str) else str(c.get("label") or "")
                if any(w in (nm + " " + lab).lower() for w in TOXIC_CONDITION_WORDS):
                    r, e = H._try_call(self.s, "jawa/game_condition", action="end", condition=nm)
                    out["conditionsEnded"].append({"def": nm, "ok": r is not None, "error": e})
                    if r is None:
                        self.problems.append("toxic condition %s could not be ended: %s" % (nm, e))
        mi = self.s.call("jawa/map_info") or {}
        nx = int(mi.get("sizeX", 250))
        nz = int(mi.get("sizeZ", nx))
        for g in TOXIC_GASES:
            r, e = H._try_call(self.s, "jawa/set_gas", action="clear", rect="0,0,%d,%d" % (nx, nz), gasType=g)
            if r is None:
                out["unavailable"].append("set_gas %s: %s" % (g, e))
            else:
                out["gasCleared"].append(g)
        cols = [r for r in H.read_pawns(self.s, health=False) if H.is_colonist(r) and not r["dead"] and r.get("x") is not None]
        left = 0
        scanned = False
        for r in cols:
            x0, z0 = max(0, int(r["x"]) - TOXIC_SCAN_RADIUS), max(0, int(r["z"]) - TOXIC_SCAN_RADIUS)
            w = min(nx - x0, 2 * TOXIC_SCAN_RADIUS + 1)
            h = min(nz - z0, 2 * TOXIC_SCAN_RADIUS + 1)
            t, e = H._try_call(self.s, "jawa/get_terrain_batch", rects="%d,%d,%d,%d" % (x0, z0, w, h), layer="top")
            if t is None:
                out["unavailable"].append("get_terrain_batch: %s" % e)
                break
            scanned = True
            import bland_world as BW
            cells = BW._parse_terrain_ops(str(t.get("ops") or ""))
            dirty = dict((c, n) for c, n in cells.items() if "pollut" in n.lower())
            if not dirty:
                continue
            paint = ";".join("%s:%d,%d,1,1" % (n.replace("Polluted", "").replace("polluted", "").strip("_") or "Soil", c[0], c[1])
                             for c, n in dirty.items())
            r2, e2 = H._try_call(self.s, "jawa/set_terrain_batch", ops=paint, layer="top", refresh=True)
            if r2 is None:
                out["unavailable"].append("set_terrain_batch: %s" % e2)
                left += len(dirty)
                continue
            t2, _e = H._try_call(self.s, "jawa/get_terrain_batch", rects="%d,%d,%d,%d" % (x0, z0, w, h), layer="top")
            now = BW._parse_terrain_ops(str((t2 or {}).get("ops") or ""))
            still = len([c for c in dirty if "pollut" in now.get(c, "pollut").lower()])
            left += still
            out["pollutedRepainted"] += len(dirty) - still
        out["pollutedLeft"] = left if scanned else None
        return out

    def settle(self, max_ticks=None, chunk=None, quiet_chunks=None):
        """Advance a fresh map in short chunks, draining each time, until `quiet_chunks` consecutive chunks produce no arrival
        (or max_ticks is spent). Divide-flyers and entity spawns land within ~150 ticks of a map's first tick, AFTER the
        setup read said 0 threats; this removes them before the row starts instead of during it. -> dict with the arrivals."""
        max_ticks = SETTLE_MAX_TICKS if max_ticks is None else max_ticks
        chunk = SETTLE_CHUNK if chunk is None else chunk
        need = SETTLE_QUIET_CHUNKS if quiet_chunks is None else quiet_chunks
        spent, quiet, arrivals = 0, 0, []
        while spent < max_ticks and quiet < need:
            self.advance(chunk, chunk=chunk)
            spent += chunk
            new = [e for e in self.events if e.get("control") == "arrival_sweep" and e not in arrivals]
            arrivals.extend(new)
            quiet = 0 if new else quiet + 1
        res = {"ticks": spent, "arrivals": len(arrivals), "settled": quiet >= need}
        self.events.append(dict(res, control="settle", utc=_now()))
        return res

    # ---------------------------------------------------------------- arrivals after apply
    def _arrival_sweep(self):
        """Hostile pawns / threat structures that APPEARED after apply() (a Megapede walking in from an uncleared hive,
        a mod's own spawner): removed at once and RECORDED as an 'arrival' so the row can PASS-with-note (owner
        2026-10-13: corrected anomaly, no damage) and the run files a test-environment item. Never silent."""
        acts = []
        on = set(self.controls)
        if "hostiles_removed" in on:
            hostile = [r for r in H.read_pawns(self.s, health=False) if H.is_hostile(r) and not r["dead"]]
            if hostile:
                k = H.kill_hostiles(self.s, self.support_ids)
                org, _e = H._try_call(self.s, "jawa/pawn_origin", ids=",".join(r["id"] for r in hostile[:20]))
                acts.append({"control": "arrival_sweep", "kind": "hostile_pawns",
                             "arrived": [(r["id"], r.get("kind") or r.get("kindDef"), r.get("faction"), r.get("x"), r.get("z"))
                                         for r in hostile],
                             "origin": [(x.get("id"), (x.get("spawn") or {}).get("classification"), x.get("statement"))
                                        for x in (org or {}).get("pawns") or []],
                             "removed": k.acted, "verified": k.verified, "ticket": "TESTENV: hostile arrival"})
        if "threat_structures_cleared" in on:
            st = self.s.call("jawa/quiet_site", action="status") or {}
            thr = [t for t in st.get("threats") or [] if not t.get("kept")]
            if thr:
                r = self.s.call("jawa/quiet_site", action="apply", clearThreats=True, keepDefs=",".join(self.keep_defs),
                                proximityLetters=False) or {}
                acts.append({"control": "arrival_sweep", "kind": "threat_structures",
                             "arrived": [(t.get("def"), t.get("id")) for t in thr],
                             "threatsAfter": r.get("threatsAfter"), "ticket": "TESTENV: threat structure appeared"})
        return acts

    # ---------------------------------------------------------------- modal broker
    def _windows(self):
        r = self.s.call("jawa/window_list_close", action="list") or {}
        return r.get("windows") or []

    def _click_label(self, label, surface_key=None):
        """Click the button labelled `label`, looking only inside the surface whose type contains `surface_key`."""
        lay = self.s.call("rimworld/get_ui_layout") or {}
        surfaces = [x for x in lay.get("surfaces") or [] if not surface_key or surface_key in str(x.get("type"))]
        hits = []

        def walk(o):
            if isinstance(o, dict):
                txt = " ".join(str(o.get(k) or "") for k in ("label", "text", "title", "caption"))
                tid = o.get("targetId") or o.get("id")
                if tid and txt.strip().lower() == label.lower():
                    hits.append(tid)
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(surfaces[:1])
        if not hits:
            return None, "no UI target labelled %r in %s" % (label, surface_key)
        r = self.s.call("rimworld/click_ui_target", targetId=hits[0]) or {}
        return hits[0], (None if _ok(r) else str(r)[:200])

    def modals(self):
        """Handle KNOWN windows with their one handler; capture unknown force-pause windows and block.
        LIVE 2026-10-13 (NS_FlowWorks_TrialSite_v1 on ratchet_pilot+patches): VEF raises ONE new-faction dialog at a
        time and the next appears as the previous is answered, so the window COUNT never drops; a click lands a frame
        later. So each answered window is tracked by its window ID: wait until THAT window is gone; the same ID still
        open after its click is a stuck modal (escalate), a new ID is the next question."""
        handled, unknown, answered = [], [], set()
        for _ in range(MODAL_MAX_ROUNDS):
            ws = self._windows()
            known = [w for w in ws if any(k in _wtype(w) for k in MODAL_HANDLERS)]
            unknown = [{"type": _wtype(w), "title": w.get("optionalTitle")} for w in ws
                       if w.get("forcePause") and w not in known and not w.get("isDebug")]
            if not known:
                break
            w = known[0]
            wid = w.get("ID", w.get("id"))
            if wid is not None and wid in answered:
                self.problems.append("modal %s (window %s) still open after its handler ran" % (_wtype(w), wid))
                break
            key = [k for k in MODAL_HANDLERS if k in _wtype(w)][0]
            verb, arg = MODAL_HANDLERS[key]
            tid, err = self._click_label(arg, key)
            gone = None
            for _ in range(20):
                if err:
                    break
                ids = [x.get("ID", x.get("id")) for x in self._windows() if key in _wtype(x)]
                gone = (wid not in ids) if wid is not None else (len(ids) < len(known))
                if gone:
                    break
                self.sleep(0.25)
            if wid is not None:
                answered.add(wid)
            handled.append({"type": _wtype(w), "window": wid, "title": w.get("optionalTitle"),
                            "handler": "%s %s" % (verb, arg), "target": tid, "closed": gone, "error": err})
            if err:
                self.problems.append("modal %s: handler failed: %s" % (_wtype(w), err))
                break
        else:
            self.problems.append("modal broker: still answering after %d windows" % MODAL_MAX_ROUNDS)
        if unknown:
            self.problems.append("unknown force-pause window(s), not closed: %s" % unknown)
        return {"handled": handled, "unknown": unknown}

    # ---------------------------------------------------------------- advance with drain
    def advance(self, ticks, chunk=600, stop_on="default"):
        """Advance through clockgate.advance_chunk (safe_advance) in chunks, draining after each. A GovernorStop is
        recorded in the receipt and re-raised (the row is UNMEASURED/restarted, never FAIL)."""
        done = 0
        while done < ticks:
            n = min(chunk, ticks - done)
            try:
                ex = clockgate.advance_chunk(self.s, n, stop_on=stop_on)
            except clockgate.GovernorStop as g:
                self.events.append({"control": "governor_stop", "message": str(g), "stopBy": g.result.get("stopBy"),
                                    "utc": _now()})
                raise
            done += n if ex is None else int(ex)
            try:
                tick = clockgate.read_ticks(self.s)
            except Exception:                                   # noqa: BLE001 - a lost clock read is not a quiet-site fault
                tick = None
            self.drain(tick=tick)
        return done

    # ---------------------------------------------------------------- verify
    def verify(self):
        """The quiet-site postcondition, read from the game: 0 hostile pawns, 0 threat structures (incl. dormant),
        0 unknown force-pause windows, support colonists alive and unhurt since baseline; plus damage_log attribution."""
        out = {}
        pawns = H.read_pawns(self.s)
        out["hostiles"] = [r["id"] for r in pawns if H.is_hostile(r)]
        st = self.s.call("jawa/quiet_site", action="status") or {}
        thr = [t for t in st.get("threats") or [] if not t.get("kept")]
        out["threatStructures"] = len(thr)
        out["dormantThreats"] = len([t for t in thr if t.get("dormant")])
        out["unsentProximityLetters"] = st.get("lettersUnsentAfter")
        ws = self._windows()
        out["forcePauseWindows"] = [_wtype(w) for w in ws if w.get("forcePause") and not w.get("isDebug")]
        cols = [r for r in pawns if H.is_colonist(r)]
        out["colonists"] = [{"id": r["id"], "dead": r["dead"],
                             "health": (r.get("health") or {}).get("summary", (r.get("health") or {}).get("summaryHealth")),
                             "injuries": [H.hediff_key(h) for h in (r.get("health") or {}).get("hediffs") or []
                                          if h.get("def") in H.INJURY_DEFS]} for r in cols]
        dl, err = H._try_call(self.s, "jawa/damage_log", action="read", limit=50)
        out["damageToColonists"] = ([e for e in (dl or {}).get("events") or [] if e.get("victimColonist")]
                                    if dl else "unavailable: %s" % err)
        # TESTENV_TRIALSITE_DIAGNOSE_NOBODY_HOME: an EMPTY colonist list used to satisfy all(...) -- a pawn-less golden
        # fixture read quiet=True and then ended the game (GameEnded) within 360 ticks. Nobody home is not quiet.
        out["livingColonists"] = len([c for c in out["colonists"] if not c["dead"]])
        out["quiet"] = (not out["hostiles"] and out["threatStructures"] == 0 and not out["forcePauseWindows"]
                        and out["livingColonists"] >= self.min_colonists and all(not c["dead"] for c in out["colonists"]))
        self.verified = out
        return out

    # ---------------------------------------------------------------- restore + receipt
    def restore(self):
        if self.tx is not None:
            try:
                self.tx.restore()
            finally:
                self.tx = None

    def receipt(self):
        return {
            "profile": "quiet_site", "suite": self.suite, "row": self.row, "topic": self.topic,
            "controls": [{"name": c, "what": CONTROLS[c]["what"], "hides": CONTROLS[c]["hides"],
                          "readBack": self.applied.get(c)} for c in self.controls],
            "notSuppressed": list(H.QUIET_NOT_SUPPRESSED),
            "keepDefs": list(self.keep_defs), "events": list(self.events), "problems": list(self.problems),
            "verify": getattr(self, "verified", None),
            "arrivals": [e for e in self.events if e.get("control") == "arrival_sweep"],
            "note": "enableStoryteller is not saved with the game: re-apply after any load",
        }

    def write_receipt(self, path):
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.receipt(), fh, indent=1, default=str)
        return path


def ensure_colonists(session, count=3, x=None, z=30, kind="Colonist"):
    """The pawn-less golden fixtures (FlowWorks NS_FlowWorks_TrialSite_v1: prep_site.py step 2 despawns EVERY pawn, so a
    fresh load holds no player colonist and the game ends within ~360 ticks) need colonists spawned before anything
    advances the clock. If >= `count` living colonists exist this does nothing. Otherwise it spawns the shortfall, DRAFTED
    (idle colonists wander into sites), off the plot grid (row z=30, centre x). Returns {'had','spawned','ids','problems'}.
    TESTENV_TRIALSITE_DIAGNOSE_NOBODY_HOME."""
    have = [r["id"] for r in H.read_pawns(session, health=False) if H.is_colonist(r) and not r["dead"]]
    out = {"had": len(have), "spawned": 0, "ids": list(have), "problems": []}
    if len(have) >= count:
        return out
    if x is None:
        mi = session.call("jawa/map_info") or {}
        x = int(mi.get("sizeX", 250)) // 2
    for i in range(count - len(have)):
        sp = session.call("jawa/spawn_pawn", kindDef=kind, x=x + 2 * i, z=z, faction="player", count=1) or {}
        got = [p["id"] for p in sp.get("pawns") or [] if p.get("id")]
        if not got:
            out["problems"].append("spawn_pawn %s at (%d,%d) returned no pawn: %s" % (kind, x + 2 * i, z, str(sp)[:160]))
            continue
        for pid in got:
            out["ids"].append(pid)
            out["spawned"] += 1
            if not _ok(session.call("jawa/set_draft", pawnId=pid, drafted=True)):
                out["problems"].append("set_draft %s refused" % pid)
    after = [r["id"] for r in H.read_pawns(session, health=False) if H.is_colonist(r) and not r["dead"]]
    if len(after) < count:
        out["problems"].append("only %d of %d living colonists after spawning" % (len(after), count))
    return out


MAP_ONLY = ("threat_structures_cleared", "hostiles_removed", "proximity_letters_sent")


def apply_site_profile(session, suite="isolated", row=None, controls=None, keep_defs=(), **kw):
    """The one call a site builder makes. Applies the suite's profile, attaches the QuietSite to the session as
    `session.quiet_site` (so the runner can drain()/verify()/restore() it later) and returns it. `controls=MAP_ONLY`
    is for fixture BUILDS: it changes only the saved map (no static debug settings, which a load would undo anyway)."""
    qs = QuietSite(session, suite=suite, controls=controls, keep_defs=keep_defs, row=row, **kw)
    qs.apply()
    try:
        session.quiet_site = qs
    except Exception:                                           # noqa: BLE001 - a session that refuses attributes
        pass
    return qs


def site_profile_receipt(session, row, suite="isolated", controls=None, keep_defs=(), **kw):
    """apply_site_profile for runners that must not die on a quiet-site fault: returns the RECEIPT (a dict for the run
    evidence) with any failure in receipt['problems'] / receipt['error'], never raises. The QuietSite stays attached as
    session.quiet_site for drain()/restore()."""
    try:
        return apply_site_profile(session, suite=suite, row=row, controls=controls, keep_defs=keep_defs, **kw).receipt()
    except QuietSiteUnclean as e:
        qs = getattr(session, "quiet_site", None)
        rc = qs.receipt() if isinstance(qs, QuietSite) else {"profile": "quiet_site", "row": row}
        rc["error"] = "UNCLEAN: %s" % e
        return rc
    except Exception as e:                                      # noqa: BLE001 - recorded, the runner decides
        return {"profile": "quiet_site", "row": row, "suite": suite, "error": "%s: %s" % (type(e).__name__, e)}


def restore_attached(session):
    """Restore what session.quiet_site changed (debug + difficulty, wild spawner). Returns None or the problem text."""
    qs = getattr(session, "quiet_site", None)
    if not isinstance(qs, QuietSite):
        return None
    try:
        qs.restore()
        return None
    except Exception as e:                                      # noqa: BLE001
        return "%s: %s" % (type(e).__name__, e)
