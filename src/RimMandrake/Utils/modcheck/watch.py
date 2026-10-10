"""modcheck.watch -- one chain's situational envelope: bland map, tick budget, sweeps, evidence, policy.

    with Watch(session, anchor, outdir, mod="Pits", chain="capture") as w:
        if not w.bland: ...                # chain is UNMEASURED: no bland map could be established
        w.expect_fixture(pid, name)        # something the TEST spawned: exempt from presence/death alarms
        w.wait(ctx, 2600)                  # chunked, budgeted, swept every `chunk` ticks

Rules (plan sections 5, 6, 10, all enforced HERE in Python; nothing asks a model when to stop):
  * game time moves only through `clockgate.step`, charged from MEASURED ticksGame deltas;
  * every chunk is followed by a full snapshot and a detector sweep;
  * the first new SURPRISE/FATAL captures evidence (sidecar + one screenshot, no refresh tick) BEFORE
    anything else happens, then policy applies: `abort` (default) raises SurpriseAbort so the component
    is recorded UNMEASURED with the evidence named; `record` keeps going (diagnostics only);
  * the game is left verified-paused on every exit path; the debug/difficulty settings are restored;
  * THE OWNER'S VISITOR RULE (question card 2026-10-10, VISITOR_DETECTORS_MEND_NAME_THE_STRANGER): when the only
    serious hits are VISITORS (contract.VISITOR_DETECTORS) and there is no EVIDENCE they disrupted a colonist or
    a test subject, the visitors are RECORDED (evidence captured first), REMOVED by exact id, and the wait goes on
    -- the run stays CLEAN with a note. Evidence of disruption makes it DISRUPTED and aborts (the redo case); a
    failed observation makes it INDETERMINATE. `visitor_policy="abort"` restores the old abort-on-any-visitor.
"""
import os

import clockgate
import contract as C
import detectors as D
import helpers as H
import snapshot as S
import surprise

DEFAULT_CHUNK = 600
DEFAULT_SESSION_CAP = 60000       # one in-game day; a PLACEHOLDER to be re-set from measured runs
UNPLANNED_TICK_CAP = 1500          # a non-wait verb that moved the clock more than this is a runaway (E6)


class SurpriseAbort(Exception):
    """Raised out of a wait/verb when a detector says the run left the script. `kind` is 'surprise'
    (a detector fired) or 'harness' (budget, clock, pause: the harness itself could not guarantee the
    run). The component records UNMEASURED, never FAIL: this is not a verdict about the mod."""
    is_surprise_abort = True

    def __init__(self, kind, message, hits=(), captures=()):
        Exception.__init__(self, message)
        self.kind = kind
        self.hits = list(hits)
        self.captures = list(captures)

    def summary(self):
        return {"kind": self.kind, "message": str(self),
                "hits": [{"detector": h.detector, "severity": h.severity, "summary": h.summary}
                         for h in self.hits],
                "evidence": [c.get("sidecar") for c in self.captures],
                "screenshots": [c.get("png") for c in self.captures if c.get("png")]}


class Watch(object):
    def __init__(self, session, anchor, outdir, mod="mod", chain="chain", policy="abort",
                 chunk=DEFAULT_CHUNK, session_cap=DEFAULT_SESSION_CAP, screenshots=True,
                 prepare=True, kill=True, expected_ids=(), resurrect=False, companion=None, feed=True,
                 visitor_policy="remove", scene=True):
        if policy not in ("abort", "record"):
            raise ValueError("policy must be 'abort' or 'record'")
        if visitor_policy not in ("remove", "abort"):
            raise ValueError("visitor_policy must be 'remove' or 'abort'")
        self.visitor_policy = visitor_policy
        self.validity = C.RunValidity()
        self.receipts = []            # contract.spawn_receipt rows, filled by TestContext
        self._visitor_fps = set()
        self.scene = scene            # write a baseline scene report before the timed stage (first-look protocol)
        self.baseline_scene = None
        self.session, self.anchor, self.outdir = session, anchor, outdir
        self.mod, self.chain, self.policy = mod, chain, policy
        self.chunk, self.screenshots = chunk, screenshots
        self.prepare_map, self.kill, self.expected_ids = prepare, kill, tuple(expected_ids)
        self.resurrect = resurrect
        self.feed = feed              # top up a colonist's Food only when it is LOW (starvation aborted 5 long chains)
        self.fed = []                 # ids fed, one entry per top-up (evidence for the summary)
        self.companion = companion    # None = probe at enter: read the companion tools iff they answer
        self.gate = clockgate.ClockGate(session_cap)
        self.exps = D.Expectations()
        self.dedup = D.Dedup()
        self.tx = None
        self.baseline = None
        self.report = None
        self.bland = True
        self.captures = []
        self.seen_hits = []          # every hit of every sweep, as dicts (for the summary)
        self.sweeps = 0
        self._seq = 0
        self._prev_md5 = None
        self._last_snap = None
        self.fixture_ids = set()      # every pawn the test spawned (the runner carries these to later chains)

    # ------------------------------------------------------------------ lifecycle
    def __enter__(self):
        self.tx = H.SettingsTransaction(self.session).__enter__()
        self.gate.observe(clockgate.read_ticks(self.session), reason="watch-open")
        if self.prepare_map:
            self.report = H.prepare_bland_map(self.session, self.tx, self.expected_ids, kill=self.kill,
                                              resurrect=self.resurrect)
            self.bland = self.report.bland
        for pid in self.expected_ids:                 # earlier chains' leftover fixtures stay the test's own
            self.exps.expect("fixture", {"id": pid})
        if self.companion is None:
            self.companion = H.companion_available(self.session)
        self.baseline = S.Baseline(S.take_snapshot(self.session, "full", companion=self.companion))
        for name in C.REQUIRED_SOURCES:
            src = self.baseline.snap["sources"][name]
            if src["read"] and (src["error"] or not src["complete"]):
                self.validity.note_observation_failure(name, "baseline read %s" % (src["error"] or "incomplete"),
                                                       self.baseline.tick)
        if self.scene:
            self.baseline_scene = self._write_scene("baseline")
        self.gate.observe(clockgate.read_ticks(self.session), reason="baseline")
        return self

    def _write_scene(self, label):
        """Automatic first-look capture (GPT review s6: baseline before a timed stage, not agent memory). Best
        effort: a failed report is noted as an observation gap of the REPORT, never fails the run."""
        try:
            import json
            import scene_report as R
            rep = R.collect(self.session, anchor=self.anchor, receipts=self.receipts, expectations=self.exps,
                            companion=self.companion)
            os.makedirs(self.outdir, exist_ok=True)
            path = os.path.join(self.outdir, "%s_%s_scene_%s.json" % (self.mod, self.chain, label))
            with open(path, "w") as f:
                json.dump(rep, f, indent=1, default=str)
            return path
        except Exception as e:                                  # noqa: BLE001
            self.seen_hits.append({"tick": None, "detector": "scene_report_error", "severity": "WARN",
                                   "summary": repr(e)})
            return None

    def __exit__(self, et, ev, tb):
        problems = []
        try:
            clockgate.ensure_paused(self.session)
        except Exception as e:                                  # noqa: BLE001
            problems.append("pause unverified at close: %r" % (e,))
        try:
            if self.tx is not None:
                self.tx.__exit__(et, ev, tb)
        except Exception as e:                                  # noqa: BLE001
            problems.append("settings not restored: %r" % (e,))
        self.close_problems = problems
        return False

    # ------------------------------------------------------------------ expectations
    def expect_fixture(self, pid, name=None):
        """A pawn the TEST spawned. The Death letter names the pawn, not its id, so both are registered."""
        self.exps.expect("fixture", {"id": pid})
        self.fixture_ids.add(pid)
        if name:
            self.exps.expect("fixture", {"name": name})

    def expect(self, kind, matcher, until_tick=None, phase=None, max_count=None):
        return self.exps.expect(kind, matcher, until_tick=until_tick, phase=phase, max_count=max_count)

    # ------------------------------------------------------------------ sweeping
    def sweep(self):
        since = (self.baseline.damage_next_seq - 1) if (self.baseline and self.baseline.damage_next_seq is not None) else -1
        snap = S.take_snapshot(self.session, "full", companion=self.companion, damage_since_seq=since)
        self._last_snap = snap
        self.sweeps += 1
        hits = D.sweep(snap, self.baseline, self.exps, anchor=self.anchor)
        for h in hits:
            if h.detector in ("evidence_stale", "listing_truncated") and h.evidence.get("source") in C.REQUIRED_SOURCES:
                self.validity.note_observation_failure(h.evidence["source"], h.summary, snap.get("tick"))
            self.seen_hits.append({"tick": snap.get("tick"), "detector": h.detector, "severity": h.severity,
                                   "summary": h.summary})
        return hits, snap

    def _serious(self, hits):
        return [h for h in hits if D.SEV_RANK[h.severity] >= D.SEV_RANK[D.SURPRISE]]

    def _protected_ids(self, snap):
        """Colonists of the baseline and every test fixture: the pawns a visitor must not touch."""
        prot = set(self.fixture_ids) | set(self.expected_ids)
        prot.update(p["id"] for p in self.baseline.snap["pawns"] if D.is_colonist(p) and not p["dead"])
        prot.update(p["id"] for p in snap["pawns"] if D.is_colonist(p) and not p["dead"])
        return prot

    def _handle_visitors(self, visitors, snap):
        """The owner's rule. Returns the captures when the visitors were recorded + removed (run goes on), or
        None when there is evidence of disruption (the caller aborts)."""
        tick = snap.get("tick")
        ids = C.visitor_ids(visitors)
        evidence = C.disruption_evidence(snap, ids, self._protected_ids(snap))
        if evidence:
            self.validity.note_disruption(evidence)
            return None
        for name in C.JUDGEMENT_SOURCES:
            src = snap["sources"][name]
            if not (src["read"] and src["complete"]):
                self.validity.note_observation_failure(
                    name, "disruption by a visitor could not be checked (%s)" % (src["error"] or
                                                                                ("unread" if not src["read"] else "incomplete")), tick)
        new = [h for h in visitors if h.fingerprint not in self._visitor_fps]
        caps = []
        if new:
            self._seq += 1
            name = surprise.unique_name(self.mod, self.chain, "visitor_" + new[0].detector, tick, self._seq)
            cap = surprise.capture(self.session, visitors, snap, self.outdir, name, self.anchor,
                                   gate=self.gate, prev_md5=self._prev_md5, screenshot=self.screenshots,
                                   context={"mod": self.mod, "chain": self.chain, "policy": "visitor:remove"})
            self._prev_md5 = cap.get("md5") or self._prev_md5
            self.captures.append(cap)
            caps.append(cap)
            self._visitor_fps.update(h.fingerprint for h in new)
        by_id = dict((p["id"], p) for p in snap["pawns"])
        removal = H.remove_visitors(self.session, ids) if ids else None
        left = set(removal.residue) if removal else set()
        for pid in ids:
            p = by_id.get(pid, {"id": pid})
            self.validity.note_visitor({
                "id": pid, "kind": p.get("kindDef"), "def": p.get("def"), "faction": p.get("faction"),
                "hostileFaction": p.get("hostile"), "state": D.pawn_state(p) if p.get("kindDef") else "unread",
                "x": p.get("x"), "z": p.get("z"), "tick": tick,
                "detectors": sorted({h.detector for h in visitors if pid in (h.evidence.get("ids") or [])}),
                "removed": pid not in left, "origin": "unknown"})
        for h in visitors:
            if h.detector == "raid_arrived":
                self.validity.note_letter({"detector": h.detector, "summary": h.summary, "tick": tick})
        if left:
            raise SurpriseAbort("harness", "visitor removal unverified: %s still on the map" % sorted(left),
                                visitors, self.captures[-1:])
        return caps

    def handle(self, hits, snap):
        """Capture evidence for NEW serious hits, then apply policy. Raises SurpriseAbort under 'abort'.
        Visitor-only hits under visitor_policy 'remove' are recorded + removed instead (owner rule, 2026-10-10)."""
        serious = self._serious(hits)
        if not serious:
            return []
        tick = snap.get("tick")
        visitors = [h for h in serious if h.detector in C.VISITOR_DETECTORS]
        if self.policy == "abort" and self.visitor_policy == "remove" and visitors and len(visitors) == len(serious):
            caps = self._handle_visitors(visitors, snap)
            if caps is not None:
                return caps
        elif visitors and self.policy == "abort":
            # a visitor AND another surprise in one sweep: is the visitor the cause? only evidence says so
            self.validity.note_disruption(C.disruption_evidence(snap, C.visitor_ids(visitors), self._protected_ids(snap)))
        if self.policy == "abort" and not self.validity.disruptions:
            others = [h for h in serious if h.detector not in C.VISITOR_DETECTORS]
            self.validity.aborted_by = "; ".join("%s: %s" % (h.detector, h.summary) for h in (others or serious)[:3])
        fresh = [h for h in serious if self.dedup.should_capture(h, tick)]
        caps = []
        if fresh:
            self._seq += 1
            name = surprise.unique_name(self.mod, self.chain, fresh[0].detector, tick, self._seq)
            cap = surprise.capture(self.session, serious, snap, self.outdir, name, self.anchor,
                                   gate=self.gate, prev_md5=self._prev_md5, screenshot=self.screenshots,
                                   context={"mod": self.mod, "chain": self.chain, "policy": self.policy})
            self._prev_md5 = cap.get("md5") or self._prev_md5
            self.captures.append(cap)
            caps.append(cap)
        if self.policy == "abort":
            msg = "; ".join("%s: %s" % (h.detector, h.summary) for h in serious[:4])
            if self.validity.disruptions:
                msg = self.validity.note_text() + " | " + msg
            raise SurpriseAbort("surprise", msg, serious, self.captures[-1:] if self.captures else [])
        return caps

    def check(self):
        """Public: sweep now (no time spent) and handle. Scripts call this after a mutation."""
        hits, snap = self.sweep()
        self.handle(hits, snap)
        return hits

    # ------------------------------------------------------------------ time
    def wait(self, ctx, n):
        """Chunked, budgeted, swept wait. The component cap is 1.25 x the request + one chunk."""
        n = int(n)
        cap = int(n * 1.25) + self.chunk
        try:
            with self.gate.frame("component", cap):
                adv = clockgate.step(self.session, self.gate, n, chunk=self.chunk, on_chunk=self._on_chunk)
        except SurpriseAbort:
            self._pause_quietly()
            raise
        except (clockgate.BudgetExceeded, clockgate.ClockLost, clockgate.ClockStall,
                clockgate.UnleasedTickMove, clockgate.PauseUnverified) as e:
            self._pause_quietly()
            raise SurpriseAbort("harness", "%s: %s" % (type(e).__name__, e), [], self.captures[-1:])
        self._pause_or_abort()
        return {"success": True, "advanced": adv, "requested": n}

    def _on_chunk(self, now):
        if self.feed:
            try:
                import bland_world  # noqa: E402
                self.fed.extend(bland_world.feed_colonists(self.session))
            except Exception:                                   # noqa: BLE001 - upkeep, never a verdict
                pass
        hits, snap = self.sweep()
        self.handle(hits, snap)

    def charge_verb(self, label):
        """After a verb that is NOT a wait (order_to, walk_over, bridge_call): charge whatever the clock
        did behind its back; a big jump is a runaway (E6: order_pawn ran 18,000 ticks) and aborts."""
        try:
            now = clockgate.read_ticks(self.session)
        except clockgate.ClockLost as e:
            raise SurpriseAbort("harness", "clock unreadable after %s: %s" % (label, e), [], [])
        if label == "bridge_call:jawa/time_set_ticks":
            # A DELIBERATE warp (the mod scripts for LeaningScrub/Stillsand/Contagion call it by name to pass a growth
            # or shed timer), not an unplanned run: re-base the clock as an epoch change instead of charging it, which
            # read every such jump as `clock_runaway` and aborted the chain (LIVE 2026-10-03, LeaningScrub 330000 ticks).
            self.gate.observe(now, epoch_change=True, reason="verb:%s" % label)
            return 0
        moved = self.gate.observe(now, reason="verb:%s" % label)
        if moved > UNPLANNED_TICK_CAP:
            self._pause_quietly()
            raise SurpriseAbort("harness", "clock_runaway: %s moved the clock %d ticks (cap %d); it must be "
                                "driven through wait_ticks" % (label, moved, UNPLANNED_TICK_CAP), [], [])
        try:
            self.gate.check()
        except clockgate.BudgetExceeded as e:
            raise SurpriseAbort("harness", "BudgetExceeded: %s" % e, [], [])
        return moved

    def _pause_quietly(self):
        try:
            clockgate.ensure_paused(self.session)
        except Exception:                                       # noqa: BLE001
            pass

    def _pause_or_abort(self):
        try:
            clockgate.ensure_paused(self.session)
        except clockgate.PauseUnverified as e:
            raise SurpriseAbort("harness", "game left running: %s" % e, [], [])

    def final(self):
        """End-of-chain sweep: deaths or fires that happened during verbs that spend no waits still count.
        Records and captures evidence but never raises (the chain is over)."""
        old, self.policy = self.policy, "record"
        try:
            hits, snap = self.sweep()
            self.handle(hits, snap)
        except Exception as e:                                  # noqa: BLE001
            self.seen_hits.append({"tick": None, "detector": "final_sweep_error", "severity": "WARN",
                                   "summary": repr(e)})
        finally:
            self.policy = old

    # ------------------------------------------------------------------ summary
    def summary(self):
        return {"bland": self.bland, "companion": bool(self.companion),
                "bland_problems": (self.report.problems if self.report else []),
                "bland_notes": (self.report.notes if self.report else []),
                "policy": self.policy, "chunk": self.chunk, "sweeps": self.sweeps, "fed": len(self.fed),
                "ticks_spent": self.gate.total_spent,
                "surprises": [{"sidecar": c.get("sidecar"), "png": c.get("png"), "notes": c.get("notes")}
                              for c in self.captures],
                "hits_seen": self.seen_hits[-40:],
                "close_problems": getattr(self, "close_problems", []),
                # owner rule 2026-10-10: CLEAN / DISRUPTED / INDETERMINATE, beside (never instead of) the verdicts
                "runValidity": self.validity.as_dict(),
                "receipts": list(self.receipts),
                "receiptProblems": C.receipt_problems(self.receipts),
                "baselineScene": self.baseline_scene}
