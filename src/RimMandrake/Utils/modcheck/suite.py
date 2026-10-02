"""modcheck.suite -- L4a: the scenario layer, per
design/RimMandrake/mod_validation_runner_spec.md (owner-designed sitting
2026-09-12) and design/RimMandrake/bridge_library_design.md.

    from modcheck import Suite

    suite = Suite("RM_PitTraps")

    @suite.chain("pit_capture")
    def pit_capture(t):
        t.clear_area(size=40)
        pits = t.spawn("RM_PitDigSite_Shallow_Bare", count=3, at="line")
        raider = t.spawn_pawn("Pirate", hostile=True, beyond=pits)
        with t.component("falls_in", toggle=None, beyond_toggle=True):
            t.walk_over(raider, pits)
            t.wait_ticks(600)
            t.expect_in_cell_of(raider, "RM_PitDigSite_Shallow_Bare")
            t.screenshot()
        # teardown is automatic: the runner's Session.sweep() runs at chain end

RULES THIS MODULE ENFORCES

- **Build-up and tear-down are absolute** (spec §1b): a chain's `fn(t)` runs
  against a fresh `rimdrive.Session`; the runner sweeps it at chain end AND
  on an uncaught exception, then re-reads the area to confirm it's empty.
  This module does not own the Session lifecycle (the runner does) -- it
  owns what happens to the CHAIN's bookkeeping when a component fails.
- **A failing component files a finding and the run continues** (spec §1):
  `component()` catches an exception raised inside its `with` block,
  records the component FAIL, and marks the chain `upstream_failed`. It
  does not re-raise -- the chain function's remaining `with t.component()`
  blocks execute normally, but every `TestContext` verb short-circuits to a
  no-op once `upstream_failed` is set (see `_guard`), so nothing further
  actually touches the game. Their component records UNMEASURED (upstream
  failed), never PASS or FAIL (spec: "never pass or fail"). This achieves
  the spec's semantics without fighting Python's `with`-statement, which
  has no clean way to skip a block's body from outside it.
- **UNVERIFIED is not silent** (rimdrive.verify's rule, inherited): a
  component whose evidence contains an UNVERIFIED write reports
  `PASS(UNVERIFIED n)`, never a clean PASS.
- **Checkpoints are debug-mode only** (spec, owner addendum 2026-09-12):
  `t.checkpoint(name)` is a no-op in smoke mode and dumps full local state
  (things/pawns in the test area, ticksGame) plus a screenshot in debug
  mode. `--debug` additionally implies halt-on-fail, which is the RUNNER's
  concern (it stops calling further chains), not this module's.
"""
import time

PASS, FAIL, UNMEASURED = "PASS", "FAIL", "UNMEASURED"


class ExpectationFailed(Exception):
    """A `t.expect_*` read-back did not match what the component asserted."""


class Precondition(Exception):
    """A component's setup came from outside the script -- refused, not
    warned about (spec §1: 'a component whose preconditions came from
    outside the script is a lint error')."""


class Component(object):
    """One `with t.component(...):` block's record. Appended to
    `TestContext.components` by `component()`'s context manager on exit."""

    def __init__(self, name, toggle, beyond_toggle, shows=None):
        self.name = name
        self.toggle = toggle
        self.beyond_toggle = beyond_toggle
        # must-show ids from the mod's walk `## north star` section that this
        # component's screenshots are evidence for. State assertions cannot see
        # appearance; `shows` is the only wiring between intent and evidence.
        self.shows = list(shows or ())
        self.evidence = []          # list of {"call": ..., "result": ...}
        self.unverified = 0
        self.screenshots = []
        self.checkpoints = []
        self.verdict = None         # PASS / FAIL / UNMEASURED, set on exit
        self.detail = ""
        self.surprises = None       # watch.SurpriseAbort.summary() when a detector ended the component

    def as_dict(self):
        verdict = self.verdict
        if verdict == PASS and self.unverified:
            verdict = "PASS(UNVERIFIED %d)" % self.unverified
        return {
            "name": self.name, "toggle": self.toggle,
            "beyond_toggle": self.beyond_toggle, "verdict": verdict,
            "detail": self.detail, "evidence": self.evidence,
            "screenshots": self.screenshots, "checkpoints": self.checkpoints,
            "shows": list(self.shows),
            "surprises": self.surprises,
        }


class _Shot(object):
    n = 0       # process-wide screenshot counter, part of every rect shot's fileName


class TestContext(object):
    """The `t` a chain function receives. Wraps a `rimdrive.Session` with the
    verb vocabulary v1 (spec §2). Every verb calls `self._guard()` first --
    once a component in this chain has failed, every later verb in the same
    chain is a no-op (see module docstring).

    `anchor` is the fixed (x, z) the test area is built around -- a chain
    creates every element of the state it tests (spec §1b), so it needs a
    stable, arbitrary point to build at. `debug` toggles checkpoint capture.
    """

    def __init__(self, session, anchor=(500, 500), debug=False,
                 on_finding=None, watch=None):
        self.session = session
        self.anchor = anchor
        self.debug = debug
        # `watch` (modcheck.watch.Watch) is the situational envelope: bland map, tick budget, detector
        # sweeps, surprise evidence. None keeps every verb exactly as it was before it existed.
        self.watch = watch
        self.upstream_failed = False
        self.upstream_reason = "upstream failed -- this chain's state is meaningless"
        self.components = []
        self._current = None
        self._on_finding = on_finding or (lambda component: None)

    # ----------------------------------------------------------- guard
    def _guard(self):
        """True if this verb should actually run. False means: do nothing,
        touch nothing, return None -- the chain is past its point of
        meaningful state (spec: 'state is now meaningless')."""
        return not self.upstream_failed

    # --------------------------------------------------------- component
    def component(self, name, toggle=None, beyond_toggle=False, shows=None):
        return _ComponentCtx(self, name, toggle, beyond_toggle, shows)

    # ------------------------------------------------------------ setup
    def clear_area(self, size=40):
        """The whole test area, cleared. A chain builds every element of the
        state it tests (spec §1b) -- this is always step one."""
        if not self._guard():
            return None
        x, z = self.anchor
        half = size // 2
        r = self.session.call("jawa/destroy_batch",
                              rects="%d,%d,%d,%d" % (x - half, z - half, size, size),
                              categories="All")
        self._record("clear_area(%d)" % size, r)
        return r

    def spawn(self, defName, count=1, at="line"):
        """Spawn `count` of `defName` near the anchor, tracked for teardown.
        Returns the list of (x, z) cells spawned into."""
        if not self._guard():
            return []
        x0, z0 = self.anchor
        cells = [(x0 + i * 2, z0) for i in range(count)] if at == "line" else \
                [(x0, z0)] * count
        ops = ";".join("%s:%d,%d" % (defName, x, z) for x, z in cells)
        r = self.session.call("jawa/spawn_batch", ops=ops)
        for x, z in cells:
            still = self.session.things_at(x, z)
            if defName in still:
                # spawn_batch does not hand back per-cell ids; litter is
                # tracked by CELL for things, which destroy_batch clears by
                # rect regardless of id (see rimdrive.Session.sweep).
                self.session.track("thing", "%s@%d,%d" % (defName, x, z),
                                   x=x, z=z)
        self._record("spawn %s x%d at %s" % (defName, count, at), r)
        return cells

    def spawn_pawn(self, kindDef, hostile=False, beyond=None):
        """Spawn one pawn of `kindDef`. Placed one cell past the furthest
        `beyond` cell along whichever axis they spread on, or at the anchor
        if `beyond` is empty."""
        if not self._guard():
            return None
        x, z = self._past(beyond) if beyond else self.anchor
        faction = "hostile" if hostile else "player"
        r = self.session.call("jawa/spawn_pawn", kindDef=kindDef, x=x, z=z,
                              faction=faction, count=1)
        row = ((r or {}).get("pawns") or [{}])[0]
        pid = row.get("id")
        if pid:
            self.session.track("pawn", pid, x=x, z=z)
            if self.watch is not None:
                self.watch.expect_fixture(pid, row.get("name"))   # the TEST made it: not a surprise
        self._record("spawn_pawn %s hostile=%s" % (kindDef, hostile), r)
        return pid

    @staticmethod
    def _past(cells):
        xs = [c[0] for c in cells]
        zs = [c[1] for c in cells]
        if max(xs) - min(xs) >= max(zs) - min(zs):
            return max(xs) + 3, zs[0]
        return xs[0], max(zs) + 3

    # -------------------------------------------------------------- act
    def walk_over(self, pawn_id, cells, wait_ticks=600):
        if not self._guard():
            return None
        tx, tz = cells[-1] if cells else self.anchor
        r = self.session.call("jawa/order_pawn", pawnId=pawn_id, x=tx, z=tz,
                              waitTicks=wait_ticks)
        self._record("walk_over %s -> (%d,%d)" % (pawn_id, tx, tz), r)
        if self.watch is not None:
            self.watch.charge_verb("walk_over")
        return r

    def order_to(self, pawn_id, dest, wait_ticks=1200):
        if not self._guard():
            return None
        if dest == "map-edge":
            x, z = self.anchor[0] + 200, self.anchor[1]
        else:
            x, z = dest
        r = self.session.call("jawa/order_pawn", pawnId=pawn_id, x=x, z=z,
                              waitTicks=wait_ticks)
        self._record("order_to %s -> %s" % (pawn_id, dest), r)
        if self.watch is not None:
            self.watch.charge_verb("order_to")
        return r

    def wait_ticks(self, n, _chunk=2000):
        """Advance the game clock by `n` REAL ticks, verified.

        🔴 `rimworld/step_game_ticks` silently truncates well below the ticks
        requested under load -- measured 600-2800 ticks per call, degrading
        with mod-list size, not a fixed constant
        (skills/rimbridge/references/silent-failures.md). It still reports
        outer `Success:true` and an inner "Advanced N game tick(s)" message
        for whatever N it actually managed, which reads exactly like success
        if the real clock isn't checked. A single un-looped call here (the
        prior behavior) is exactly why several modcheck suites read RED
        against a mechanism that never got the wall-clock time it needed --
        `Antiquities.wait_ticks(95000)` and `ShipMemory`'s 600-tick wait were
        both trusting this call's own report instead of the real clock.

        Ground truth is `ticksGame`, read independently before/after each
        call via `Session._ticks()` (the same instrument `paused()` verifies
        with) -- never the call's own reported tick count or a running
        Python counter. Loops in bounded chunks (each sized to complete
        cleanly rather than truncate) until the real clock has advanced by
        `n`, and raises rather than returning a result nothing after it can
        trust if the clock stalls."""
        if not self._guard():
            return None
        if self.watch is not None:
            # budgeted, chunked, swept every chunk; may raise watch.SurpriseAbort (component -> UNMEASURED)
            r = self.watch.wait(self, n)
            self._record("wait_ticks(%d) [watched] -> %d tick(s)" % (n, r["advanced"]), r)
            return r
        start = self.session._ticks()
        max_calls = max(30, (n // 300) + 20)
        last = None
        calls = 0
        advanced = 0
        while advanced < n and calls < max_calls:
            step = min(_chunk, n - advanced)
            r = self.session.call("rimworld/step_game_ticks", ticks=step,
                                  pauseFirst=True)
            calls += 1
            last = r
            now = self.session._ticks()
            if start is None or now is None:
                # Can't verify independently (e.g. off the map screen) --
                # fall back to the old single-call, unverified behavior
                # rather than looping blind.
                self._record("wait_ticks(%d) [unverifiable clock]" % n, r)
                return r
            new_advanced = now - start
            if new_advanced <= advanced:
                # A call that reported completion but moved nothing is a
                # stalled clock, not a slow one -- stop burning calls.
                advanced = new_advanced
                break
            advanced = new_advanced
        self._record("wait_ticks(%d) -> %d real tick(s) over %d call(s)"
                     % (n, advanced, calls), last)
        if advanced < n:
            raise ExpectationFailed(
                "wait_ticks(%d) only advanced %d real game tick(s) over %d "
                "call(s) before giving up -- rimworld/step_game_ticks "
                "silently truncates under load (silent-failures.md); the "
                "game clock never reached the requested point, so nothing "
                "checked after this call is meaningful evidence." % (n, advanced, calls))
        return last

    def set_setting(self, type_name, values, persist=False):
        """Flip a mod's Mod Settings field(s) for the duration of THIS live
        session -- `jawa/mod_settings_field` (BRIDGE_STATIC_SETTINGS_FIELDS_1:
        resolves the field as STATIC first, falling back to INSTANCE; our
        own mods' settings classes are almost all `public static`, which
        `rimworld/update_mod_settings` could never reach at all).
        `type_name` is the settings class's `Type.FullName`
        (e.g. `"RimMandrake.Pits.PitsSettings"`), not a mod packageId. The
        tool never calls `ModSettings.Write()` -- a static-field write is
        never serialized to `ModSettings.xml` in the first place, so
        `persist=True` is refused rather than silently ignored. Verified
        via an independent read-back (`action="get"`), never the setter's
        own echoed `valueAfter`."""
        if not self._guard():
            return None
        if persist:
            raise ValueError(
                "jawa/mod_settings_field never persists to ModSettings.xml "
                "-- persist=True is not supported")
        for field, value in values.items():
            r = self.session.call("jawa/mod_settings_field", typeName=type_name,
                                  action="set", field=field, value=str(value))
            if not (r or {}).get("success"):
                raise ExpectationFailed(
                    "mod_settings_field(set, %s.%s=%r) failed: %s"
                    % (type_name, field, value, r))
        settings = {}
        for field in values:
            got = self.session.call("jawa/mod_settings_field", typeName=type_name,
                                    action="get", field=field)
            settings[field] = (got or {}).get("value")
        ok = all(settings.get(k) == str(v) for k, v in values.items())
        self._record("set_setting(%s, %s)" % (type_name, values), ok)
        if not ok:
            raise ExpectationFailed(
                "mod_settings_field(%s, %s) did not take -- read back %s"
                % (type_name, values, settings))
        return ok

    def ensure_faction(self, def_name):
        """Make sure a live Faction instance of `def_name` exists in this
        world, creating one via `jawa/faction_create` if not.

        🔴 Several suites assumed a vanilla FactionDef with
        `requiredCountAtGameStart > 0` (Pirate, most often) is therefore
        GUARANTEED to have a live instance in any generated world -- false
        on this project's own mandated all-DLC test environment.
        `jawa/faction_create`'s own C# docstring names the deterministic
        cause: Biotech's `PirateWaster` declares `replacesFaction` at
        vanilla `Pirate` with `requiredCountAtGameStart` above zero, so
        `FactionGenerator.InitializeFactions` skips generating `Pirate`
        outright whenever Biotech is active -- and CLAUDE.md's standing
        rule is that every test mod list carries all five expansions, no
        ablation. So a quicktest world here never has a live `Pirate`
        faction on its own, ever, by construction (measured live
        2026-09-13 against both Aftermath's and RimProperty's suites,
        independently, same failure). Tolerates the tool's "already
        exists" refusal as success."""
        if not self._guard():
            return None
        r = self.session.call("jawa/faction_create", defName=def_name, dryRun=False)
        self._record("ensure_faction(%s)" % def_name, r)
        if (r or {}).get("success") or (r or {}).get("existingCount"):
            return r
        raise ExpectationFailed(
            "jawa/faction_create(defName=%r) could not ensure a live faction "
            "instance exists: %r" % (def_name, r))

    def bridge_call(self, tool, **params):
        """The escape valve. A mutation through here still owes its own
        `expect_*` afterward -- this does not pay a read-back for you."""
        if not self._guard():
            return None
        r = self.session.call(tool, **params)
        self._record("bridge_call %s" % tool, r)
        if self.watch is not None:
            if tool == "jawa/spawn_pawn":
                # a pawn the test spawns through the escape valve is as much its own fixture as one made
                # by spawn_pawn(): its injuries and its teardown death are not surprises (MEASURED live)
                for row in (r or {}).get("pawns") or []:
                    if row.get("id"):
                        self.watch.expect_fixture(row["id"], row.get("name"))
            self.watch.charge_verb("bridge_call:%s" % tool)
        return r

    def expect(self, kind, matcher, until_tick=None):
        """Declare something THIS chain causes on purpose, so the situational detectors do not call it a
        surprise: a letter (`"letter", {"label_contains": "Wild droid"}`), a hostile
        (`"hostile", {"id": pid}`), a condition, a fire. Only the PRESENCE alarm is suppressed. A no-op
        when no watch is attached, so a script may declare it unconditionally."""
        if self.watch is not None:
            self.watch.expect(kind, matcher, until_tick=until_tick)

    def check_surroundings(self):
        """Sweep the detectors NOW (no game time spent). A script calls this right after a mutation it
        wants proven clean. Returns the hits; raises watch.SurpriseAbort under the abort policy."""
        if not self._guard() or self.watch is None:
            return []
        return self.watch.check()

    # ---------------------------------------------------------- asserts
    def _pawn_pos(self, pawn_id):
        rows = self.session.call("jawa/list_pawns", limit=500).get("pawns") or []
        for p in rows:
            if p.get("id") == pawn_id:
                return p.get("x"), p.get("z")
        return None, None

    def expect_pawn_despawned(self, pawn_id):
        """The pawn no longer appears in `jawa/list_pawns` at all -- the
        correct check for a mod that CONTAINS a pawn (e.g. a trap's
        `innerContainer`, a crate, a vehicle) rather than merely moving it:
        a contained pawn is despawned from the map, so its (x, z) stops
        meaning anything and `expect_in_cell_of` would be the wrong tool
        entirely (see modcheck.suite's `bridge_call` note and the Pits
        pilot's own docstring for why this was learned, not assumed)."""
        if not self._guard():
            return None
        x, z = self._pawn_pos(pawn_id)
        got = x is None
        self._record("expect_pawn_despawned(%s)" % pawn_id, got)
        if not got:
            raise ExpectationFailed(
                "%s is still on the map at (%s,%s), expected despawned/contained"
                % (pawn_id, x, z))
        return got

    def expect_log_contains(self, tag, field=None, value=None, limit=200):
        """Read `jawa/drain_log` for the most recent line containing `tag`
        (a mod's own debug-action log prefix, e.g. '[RMPitsDebug] SCAN_DONE')
        and optionally require `field=value` inside it (a simple
        substring check on '<field>=<value>', matching the
        'key=value key2=value2' shape these debug actions log in). This is
        the read-back channel for any mechanism whose real state lives in a
        C# field with no bridge getter -- see the module docstring on
        writing a component's own debug-action Report line instead of
        inventing a new primitive for every mod."""
        if not self._guard():
            return None
        r = self.session.call("jawa/drain_log", limit=limit, contains=tag)
        msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
        line = msgs[-1] if msgs else None
        got = line is not None and (field is None or
                                    ("%s=%s" % (field, value)) in line)
        self._record("expect_log_contains(%s, %s=%s)" % (tag, field, value), got)
        if not got:
            raise ExpectationFailed(
                "no recent log line matched tag=%r field=%r value=%r "
                "(last matching line: %r)" % (tag, field, value, line))
        return line

    def expect_in_cell_of(self, pawn_id, defName):
        if not self._guard():
            return None
        x, z = self._pawn_pos(pawn_id)
        got = defName in (self.session.things_at(x, z) if x is not None else [])
        self._record("expect_in_cell_of(%s, %s)" % (pawn_id, defName), got)
        if not got:
            raise ExpectationFailed(
                "%s is not in a cell holding %s (at %s,%s)"
                % (pawn_id, defName, x, z))
        return got

    def expect_not_in_cell_of(self, pawn_id, defName):
        if not self._guard():
            return None
        x, z = self._pawn_pos(pawn_id)
        got = defName not in (self.session.things_at(x, z) if x is not None else [])
        self._record("expect_not_in_cell_of(%s, %s)" % (pawn_id, defName), got)
        if not got:
            raise ExpectationFailed(
                "%s IS in a cell holding %s (at %s,%s), expected not to be"
                % (pawn_id, defName, x, z))
        return got

    def expect_reached_past(self, pawn_id, cells):
        """The pawn's position is past the far edge of `cells` along
        whichever axis they spread on -- 'walked through', not 'stopped at'."""
        if not self._guard():
            return None
        px, pz = self._pawn_pos(pawn_id)
        xs = [c[0] for c in cells]
        zs = [c[1] for c in cells]
        along_x = max(xs) - min(xs) >= max(zs) - min(zs)
        got = (px is not None and px > max(xs)) if along_x else \
              (pz is not None and pz > max(zs))
        self._record("expect_reached_past(%s, %d cells)" % (pawn_id, len(cells)), got)
        if not got:
            raise ExpectationFailed(
                "%s did not reach past %s (at %s,%s)" % (pawn_id, cells, px, pz))
        return got

    # ----------------------------------------------------------- evidence
    def screenshot(self, name=None, rect=None, padding=1):
        """`rect=(x, z, w, h)` frames THAT rect (`rimworld/screenshot_cell_rect`)
        instead of the anchor -- a component that must be judged on one subject
        needs the subject in frame, not the anchor. Omitted: unchanged behaviour."""
        if not self._guard():
            return None
        x, z = self.anchor
        name = name or (self._current.name if self._current else "modcheck")
        path = None
        try:
            self.session.call("jawa/clear_ui")
            if rect:
                rx, rz, rw, rh = rect
                # A unique fileName: without one the tool names the file by the
                # SECOND, so two shots in one second overwrite each other (live
                # 2026-10-01: three spree_wall shots left two files).
                _Shot.n += 1
                r = self.session.call("rimworld/screenshot_cell_rect",
                                      x=rx, z=rz, width=rw, height=rh,
                                      paddingCells=padding,
                                      fileName="%s_%d_%d" % (name, int(time.time() * 1000), _Shot.n))
            else:
                self.session.call("rimworld/jump_camera_to_cell", x=x, z=z)
                r = self.session.call("rimworld/take_screenshot",
                                      fileName="%s_%d" % (name, int(time.time())),
                                      suppressMessage=True)
            path = (r or {}).get("path")
        except Exception:
            path = None
        if not path:
            # The bridge screenshot can return success-and-nothing (spec
            # §2). system_screenshot.py is the OS-level fallback -- see
            # that script's own docstring; imported lazily so an offline
            # selftest never needs pywin32/ctypes on the loader path.
            import os
            import subprocess
            import sys as _sys
            utils = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            out = os.path.join(utils, "..", "..", "..", "Transient", "modcheck",
                               "%s_fallback_%d.bmp" % (name, int(time.time())))
            os.makedirs(os.path.dirname(out), exist_ok=True)
            subprocess.run(["python.exe",
                            os.path.join(utils, "system_screenshot.py"), out],
                           check=False)
            path = out
        if self._current is not None:
            self._current.screenshots.append(path)
        return path

    def checkpoint(self, name):
        """No-op in smoke mode. In debug mode, dumps local state so a
        failure can be localised between two checkpoints instead of
        autopsied from the end state (spec, owner addendum 2026-09-12)."""
        if not self.debug or not self._guard():
            return None
        x, z = self.anchor
        state = {
            "name": name,
            "ticksGame": self.session._ticks(),
            "things": self.session.things_at(x, z),
            "pawns": self.session.call("jawa/list_pawns", limit=50).get("pawns"),
        }
        state["screenshot"] = self.screenshot(name="checkpoint_%s" % name)
        if self._current is not None:
            self._current.checkpoints.append(state)
        return state

    # ------------------------------------------------------------- misc
    def _record(self, call, result):
        if self._current is not None:
            self._current.evidence.append({"call": call, "result": result})
            from rimdrive import UNVERIFIED
            if result is UNVERIFIED:
                self._current.unverified += 1


class _ComponentCtx(object):
    def __init__(self, ctx, name, toggle, beyond_toggle, shows=None):
        self.ctx = ctx
        self.component = Component(name, toggle, beyond_toggle, shows)

    def __enter__(self):
        self.ctx._current = self.component
        return self.ctx

    def __exit__(self, exc_type, exc, tb):
        c = self.component
        if self.ctx.upstream_failed:
            c.verdict = UNMEASURED
            c.detail = self.ctx.upstream_reason
        elif exc is not None and getattr(exc, "is_surprise_abort", False):
            # A detector (or the harness's own budget/clock guard) ended the run. That is a statement
            # about the ENVIRONMENT, never a verdict on the mod: UNMEASURED, evidence named, no finding.
            c.verdict = UNMEASURED
            c.surprises = exc.summary()
            c.detail = "%s: %s" % (exc.kind, exc)
            if c.surprises["evidence"]:
                c.detail += " [evidence: %s]" % ", ".join(c.surprises["evidence"])
            self.ctx.upstream_failed = True
            self.ctx.upstream_reason = "a surprise ended this chain earlier: " + c.detail[:200]
        elif exc is not None:
            c.verdict = FAIL
            c.detail = "%s: %s" % (exc_type.__name__, exc)
            self.ctx.upstream_failed = True
            self.ctx._on_finding(c)
        else:
            c.verdict = PASS
        self.ctx.components.append(c)
        self.ctx._current = None
        # Suppress the exception (if any): the CHAIN function continues to
        # its next `with t.component()` block, which will see
        # upstream_failed=True and record UNMEASURED, per spec §1.
        return True


class Suite(object):
    """A named collection of chains for one mod. `chains` preserves
    registration order -- the order components run in, and the order the
    HTML sheet lists them."""

    def __init__(self, name):
        self.name = name
        self.chains = []          # [(name, fn)]
        self.chain_caps = {}      # name -> situational session tick cap override (default: watch.DEFAULT_SESSION_CAP)
        self.toggles = []         # Mod Settings toggle names this mod has

    def chain(self, name, tick_cap=None):
        """`tick_cap`: a chain that legitimately needs more in-game time than the default situational session
        cap (60000) declares its own total here; the watch still sweeps every chunk and caps each wait."""
        def deco(fn):
            self.chains.append((name, fn))
            if tick_cap:
                self.chain_caps[name] = int(tick_cap)
            return fn
        return deco

    def components_declared(self):
        """Run every chain fn with a NO-OP recording context (no session, no
        game) to enumerate {"toggle", "beyond_toggle", "shows"} per component,
        for `modcheck.floor.uncovered()` and `floor.uncovered_shows()`. Used by
        lint/floor checks that must not touch a live game to answer 'is the
        floor met' -- including the VISUAL floor, which has to be answerable
        BEFORE a run, since an uncovered must-show line refuses the mod rather
        than failing it."""
        out = []
        probe = _DeclarationProbe()
        for _, fn in self.chains:
            probe.upstream_failed = False
            fn(probe)
            out.extend({"toggle": c.toggle, "beyond_toggle": c.beyond_toggle,
                        "shows": list(c.shows)}
                       for c in probe.components)
            probe.components = []
        return out


class _DeclarationProbe(TestContext):
    """A `TestContext` whose every verb is a pure no-op -- used only to walk
    a chain function's `with t.component(...)` structure for floor/lint
    checks, offline, with no `Session` and no game. Every method that would
    call `self.session` is overridden to do nothing instead."""

    def __init__(self):
        super(_DeclarationProbe, self).__init__(session=None)

    def _guard(self):
        return False   # every verb becomes a no-op; only component() bookkeeping runs
