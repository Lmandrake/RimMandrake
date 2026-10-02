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
  * the game is left verified-paused on every exit path; the debug/difficulty settings are restored.
"""
import os

import clockgate
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
                 prepare=True, kill=True, expected_ids=(), resurrect=False, companion=None, feed=True):
        if policy not in ("abort", "record"):
            raise ValueError("policy must be 'abort' or 'record'")
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
        self.gate.observe(clockgate.read_ticks(self.session), reason="baseline")
        return self

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

    def expect(self, kind, matcher, until_tick=None, phase=None):
        return self.exps.expect(kind, matcher, until_tick=until_tick, phase=phase)

    # ------------------------------------------------------------------ sweeping
    def sweep(self):
        since = (self.baseline.damage_next_seq - 1) if (self.baseline and self.baseline.damage_next_seq is not None) else -1
        snap = S.take_snapshot(self.session, "full", companion=self.companion, damage_since_seq=since)
        self._last_snap = snap
        self.sweeps += 1
        hits = D.sweep(snap, self.baseline, self.exps, anchor=self.anchor)
        for h in hits:
            self.seen_hits.append({"tick": snap.get("tick"), "detector": h.detector, "severity": h.severity,
                                   "summary": h.summary})
        return hits, snap

    def _serious(self, hits):
        return [h for h in hits if D.SEV_RANK[h.severity] >= D.SEV_RANK[D.SURPRISE]]

    def handle(self, hits, snap):
        """Capture evidence for NEW serious hits, then apply policy. Raises SurpriseAbort under 'abort'."""
        serious = self._serious(hits)
        if not serious:
            return []
        tick = snap.get("tick")
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
            raise SurpriseAbort("surprise", "; ".join("%s: %s" % (h.detector, h.summary) for h in serious[:4]),
                                serious, self.captures[-1:] if self.captures else [])
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
                "close_problems": getattr(self, "close_problems", [])}
