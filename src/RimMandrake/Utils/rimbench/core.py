"""RimBench core: a session, and the rule that every mutation must prove itself.

THE RULE THIS MODULE EXISTS TO ENFORCE

    `success: true` from RimBridge means the tool RAN, not that the game
    CHANGED.

That has been wrong repeatedly. `spawn_thing` returns a real thingId while
logging an error; `Set terrain (rect)` returns success on every call and changes
nothing. On 2026-08-11 that cost 45 wasted calls and five save-parses before
anyone noticed, because nothing in the response said so.

So `Session.mutate()` takes a verifier. If the verifier cannot see the world
change, the call raises. A silent no-op becomes a loud failure at the moment it
happens, which is the only time it is cheap to diagnose.

USAGE

    from rimbench.core import Session

    with Session() as s:
        s.god(True)
        tid = s.spawn("Apparel_PlateArmor", 100, 100)   # verified present
        s.set_stuff(tid, "Plasteel")                     # verified changed
        s.set_quality(tid, "Legendary")

Every helper here is mod-list independent. Nothing references a Star Wars def, a
xenotype, or anything outside vanilla Core, so the same code drives a 3-mod
bench and a 568-mod campaign.
"""
import os
import sys
import time

_UTILS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _UTILS not in sys.path:
    sys.path.insert(0, _UTILS)
from rimbridge_client import RimBridge, resolve_endpoint

BS = chr(92)          # debug action paths are backslash-separated; see traps.md


class Unchanged(Exception):
    """A mutation reported success and the world did not move."""


class Session(object):
    """A connected bridge session with verification built in.

    `strict` (default True) raises Unchanged when a verifier says nothing
    happened. Set it False for exploration, where a no-op is information rather
    than an error.
    """

    def __init__(self, strict=True, quiet=False):
        host, port, token = resolve_endpoint()
        if not token:
            raise RuntimeError(
                "No bridge token in Player.log. Is RimWorld running with "
                "RimBridgeServer active?")
        self._rb = RimBridge(host, port, token)
        self.strict = strict
        self.quiet = quiet
        self.calls = 0
        self.mutations = 0
        self.no_ops = []
        self._shots = 0

    def __enter__(self):
        self._rb.__enter__()
        return self

    def __exit__(self, *a):
        return self._rb.__exit__(*a)

    # ---------------------------------------------------------------- raw
    def call(self, tool, **params):
        self.calls += 1
        return self._rb.call(tool, params)

    def action(self, path, **params):
        """Run a debug action. `path` uses real backslashes."""
        return self.call("rimworld/execute_debug_action", path=path, **params)

    def log(self, msg):
        if not self.quiet:
            print("   " + msg)

    # ------------------------------------------------------------ verified
    def mutate(self, what, do, verify):
        """Run `do`, then require `verify()` to return truthy.

        `verify` should read the world back through an INDEPENDENT channel --
        get_cell_info, list_colonists, a parsed save -- never the response of
        the mutating call itself. That independence is the whole point.
        """
        do()
        self.mutations += 1
        got = verify()
        if got:
            return got
        self.no_ops.append(what)
        if self.strict:
            raise Unchanged(
                "%s reported success but the world did not change. "
                "See skills/rimbridge/references/traps.md." % what)
        self.log("NO-OP: %s" % what)
        return None

    # ------------------------------------------------------------- reading
    def cell(self, x, z):
        return self.call("rimworld/get_cell_info", x=x, z=z)["cell"]

    def things_at(self, x, z):
        return [t.get("defName") for t in (self.cell(x, z).get("things") or [])]

    def terrain_at(self, x, z):
        return self.cell(x, z).get("terrainDefName")

    def colonists(self):
        return self.call("rimworld/list_colonists", currentMapOnly=True)["colonists"]

    def pawn(self, name_or_id):
        for c in self.colonists():
            if name_or_id in (c.get("pawnId"), c.get("name"), c.get("fullName")):
                return c
        return None

    # ------------------------------------------------------------ mutating
    def god(self, on=True):
        """God mode makes architect placement instant rather than blueprints."""
        return self.call("rimworld/set_god_mode", enabled=bool(on))

    def spawn(self, defName, x, z, stack=None):
        """Spawn a thing and verify it is really in the cell.

        NOTE: spawn_thing has no `stuff` parameter, so stuff-based items arrive
        with a default material and log 'madeFromStuff but stuff=null'. Follow
        with set_stuff(); see set_stuff's docstring.
        """
        box = {}

        def do():
            p = {"defName": defName, "x": x, "z": z}
            if stack:
                p["stackCount"] = stack
            box["r"] = self.call("rimworld/spawn_thing", **p)

        self.mutate("spawn %s at (%d,%d)" % (defName, x, z), do,
                    lambda: defName in self.things_at(x, z))
        return box["r"].get("thingId")

    def set_stuff(self, thingId, stuffDef, at=None):
        """Set a thing's material. `at` is (x,z) for verification."""
        path = "Actions" + BS + "T: Set Stuff..." + BS + stuffDef

        def verify():
            if not at:
                return True                     # unverifiable without a cell
            for t in (self.cell(*at).get("things") or []):
                if t.get("stuffDefName") == stuffDef:
                    return True
            return False

        return self.mutate("set stuff %s" % stuffDef,
                           lambda: self.action(path, thingId=thingId), verify)

    def set_quality(self, thingId, quality, at=None):
        path = "Actions" + BS + "T: Set Quality..." + BS + quality

        def verify():
            if not at:
                return True
            q = quality.lower()
            return any(q in (t.get("label") or "").lower()
                       for t in (self.cell(*at).get("things") or []))

        return self.mutate("set quality %s" % quality,
                           lambda: self.action(path, thingId=thingId), verify)

    def spawn_pawn(self, kindDef, x, z):
        """Spawn a pawn kind. Verified via list_colonists, NOT via the cell.

        ⚠️ This used to verify with `things_at()`, which **cannot ever work**:
        `get_cell_info`'s `things` list does not include pawns. So every
        successful spawn reported a no-op, and under `strict=True` raised
        `Unchanged` on a spawn that had actually happened. Found by WORLD
        2026-08-12 while spawning Jawas; see traps.md.

        `Actions\\Spawn Pawn...` spawns player-side, so the roster is a real
        independent channel. A pawn spawned into another faction would not show
        up here — verify those with `screenshot_cell_rect` instead, which is the
        honest channel for anything the data APIs cannot see.
        """
        before = len(self.colonists())
        path = "Actions" + BS + "Spawn Pawn..." + BS + kindDef
        return self.mutate("spawn pawn %s" % kindDef,
                           lambda: self.action(path, x=x, z=z),
                           lambda: len(self.colonists()) > before)

    def select(self, pawnId):
        return self.call("rimworld/select_pawn", pawnId=pawnId)

    def wear(self, pawnId, apparelDef):
        """Dress the SELECTED pawn. Acts on selection, so we select first."""
        self.select(pawnId)
        path = "Actions" + BS + "Wear apparel (selected)..." + BS + apparelDef
        return self.action(path)

    def strip(self, pawnId):
        self.select(pawnId)
        return self.action("Actions" + BS + "Wear apparel (selected)..." +
                           BS + "*Remove all apparel")

    # ---------------------------------------------------------------- time
    def step(self, ticks=60):
        """Deterministic tick advance. Build tests on this, not play_for."""
        return self.call("rimworld/step_game_ticks", ticks=ticks, pauseFirst=True)

    def play(self, ms=1000, speed="Normal"):
        """Wall-clock play. Non-deterministic; use only for 'eventually'."""
        return self.call("rimworld/play_for", durationMs=ms, speed=speed)

    # ---------------------------------------------------------------- view
    def _shot_name(self, name):
        """Make a screenshot filename unique per call.

        `take_screenshot` OVERWRITES by filename, so reusing one hands you the
        previous run's image — which reads exactly like the action having done
        nothing. That produced two false negatives in one session. A filename is
        shared mutable state; treat an image file as a cache, not an
        observation.
        """
        self._shots += 1
        return "%s_%03d" % (name, self._shots)

    def look(self, x, z, name="rimbench", zoom=None):
        """Point the camera and take a screenshot. Returns the file path.

        `zoom` is a rootSize NUMBER (11-15 is the safe band), not a zoom name.
        """
        self.call("rimworld/jump_camera_to_cell", x=x, z=z)
        if zoom is not None:
            # 🔴 The parameter is `rootSize`, a NUMBER — not `zoom`, and not a
            # zoom name. `{"zoom": "Furthest"}` is an unknown key: the bridge
            # drops it silently, returns success: true, and the camera does not
            # move. This call spent a year of session-time looking correct.
            # traps.md, "Client-call gotchas". The bare `except: pass` that used
            # to wrap it made the silence total, so it is gone too.
            # ⚠️ rootSize below ~11 breaks the world mesh render (flat red);
            # 11-15 are clean, and the extension must be enabled for >23.
            self.call("rimworld/set_camera_zoom", rootSize=float(zoom))
        r = self.call("rimworld/take_screenshot", fileName=self._shot_name(name),
                      suppressMessage=True)
        return r.get("path")

    def frame(self, x, z, w, h, name="rimbench"):
        """Frame a rect and shoot it, so the whole thing is in view."""
        try:
            self.call("rimworld/frame_cell_rect", x=x, z=z, width=w, height=h)
        except Exception:
            self.call("rimworld/jump_camera_to_cell", x=x + w // 2, z=z + h // 2)
        r = self.call("rimworld/take_screenshot", fileName=self._shot_name(name),
                      suppressMessage=True)
        return r.get("path")

    def save(self):
        """Save and return the path. NOTE: the bridge ignores any fileName."""
        return self.call("rimworld/save_game")["path"]

    # -------------------------------------------------------------- report
    def summary(self):
        return ("%d calls, %d verified mutations, %d no-ops%s"
                % (self.calls, self.mutations, len(self.no_ops),
                   (": " + "; ".join(self.no_ops[:3])) if self.no_ops else ""))
