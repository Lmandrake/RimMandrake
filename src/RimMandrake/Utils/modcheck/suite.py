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

    def __init__(self, name, toggle, beyond_toggle):
        self.name = name
        self.toggle = toggle
        self.beyond_toggle = beyond_toggle
        self.evidence = []          # list of {"call": ..., "result": ...}
        self.unverified = 0
        self.screenshots = []
        self.checkpoints = []
        self.verdict = None         # PASS / FAIL / UNMEASURED, set on exit
        self.detail = ""

    def as_dict(self):
        verdict = self.verdict
        if verdict == PASS and self.unverified:
            verdict = "PASS(UNVERIFIED %d)" % self.unverified
        return {
            "name": self.name, "toggle": self.toggle,
            "beyond_toggle": self.beyond_toggle, "verdict": verdict,
            "detail": self.detail, "evidence": self.evidence,
            "screenshots": self.screenshots, "checkpoints": self.checkpoints,
        }


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
                 on_finding=None):
        self.session = session
        self.anchor = anchor
        self.debug = debug
        self.upstream_failed = False
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
    def component(self, name, toggle=None, beyond_toggle=False):
        return _ComponentCtx(self, name, toggle, beyond_toggle)

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
        return r

    def wait_ticks(self, n):
        if not self._guard():
            return None
        r = self.session.call("rimworld/step_game_ticks", ticks=n,
                              pauseFirst=True)
        self._record("wait_ticks(%d)" % n, r)
        return r

    def set_setting(self, mod_id, values, persist=False):
        """Flip a mod's Mod Settings field(s) for the duration of THIS live
        session -- `rimworld/update_mod_settings`. `persist=False` (the
        default) applies the change in-memory only (`write=False`): a
        test toggling `trapTriggerEnabled` off must never leave that
        written to the owner's actual `ModSettings.xml` on disk. Verified
        via an independent read-back (`rimworld/get_mod_settings`), never
        the setter's own echoed values."""
        if not self._guard():
            return None
        self.session.call("rimworld/update_mod_settings", modId=mod_id,
                          values=values, write=persist)
        got = self.session.call("rimworld/get_mod_settings", modId=mod_id)
        settings = (got or {}).get("settings") or {}
        ok = all(settings.get(k) == v for k, v in values.items())
        self._record("set_setting(%s, %s)" % (mod_id, values), ok)
        if not ok:
            raise ExpectationFailed(
                "update_mod_settings(%s, %s) did not take -- read back %s"
                % (mod_id, values, settings))
        return ok

    def bridge_call(self, tool, **params):
        """The escape valve. A mutation through here still owes its own
        `expect_*` afterward -- this does not pay a read-back for you."""
        if not self._guard():
            return None
        r = self.session.call(tool, **params)
        self._record("bridge_call %s" % tool, r)
        return r

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
    def screenshot(self, name=None):
        if not self._guard():
            return None
        x, z = self.anchor
        name = name or (self._current.name if self._current else "modcheck")
        path = None
        try:
            self.session.call("jawa/clear_ui")
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
    def __init__(self, ctx, name, toggle, beyond_toggle):
        self.ctx = ctx
        self.component = Component(name, toggle, beyond_toggle)

    def __enter__(self):
        self.ctx._current = self.component
        return self.ctx

    def __exit__(self, exc_type, exc, tb):
        c = self.component
        if self.ctx.upstream_failed:
            c.verdict = UNMEASURED
            c.detail = "upstream failed -- this chain's state is meaningless"
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
        self.toggles = []         # Mod Settings toggle names this mod has

    def chain(self, name):
        def deco(fn):
            self.chains.append((name, fn))
            return fn
        return deco

    def components_declared(self):
        """Run every chain fn with a NO-OP recording context (no session, no
        game) to enumerate {"toggle", "beyond_toggle"} per component, for
        `modcheck.floor.uncovered()`. Used by lint/floor checks that must
        not touch a live game to answer 'is the floor met'."""
        out = []
        probe = _DeclarationProbe()
        for _, fn in self.chains:
            probe.upstream_failed = False
            fn(probe)
            out.extend({"toggle": c.toggle, "beyond_toggle": c.beyond_toggle}
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
