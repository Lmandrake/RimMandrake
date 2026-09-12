"""rimdrive.session -- L1: a hardened bridge session.

Extraction of `rimbench.core.Session`'s connection lifecycle
(design/RimMandrake/bridge_library_design.md, owner-ruled 2026-09-12), plus
the hardening rimbench never had:

- **reconnect with post-condition polling** -- a timeout poisons the socket
  by design (skill rimbridge §1: the in-flight call's effect is unknown, and
  re-issuing it assumes an idempotence nothing declared). `call()` drops the
  dead socket, reopens it, and raises `rimdrive.verify.Reconnected` so the
  caller (normally `mutate()`) re-checks the POST-CONDITION rather than
  blindly retrying.
- **verified pause** -- `paused()` reads `ticksGame` twice through an
  independent channel (`rimbridge/get_bridge_status`) rather than trusting
  `pause_game`'s own success flag. The 2026-08-12 two-pawn colony loss
  happened because a script trusted that flag alone.
- **litter registry** -- every id this session spawns is tracked; `sweep()`
  destroys it and re-reads the area empty. Runs on normal exit AND on an
  exception exit (modcheck spec §1b: build-up and tear-down are absolute).
- **runtime tool census at connect** -- `self.tools` is the `tools/list`
  response already fetched for the param guard (16 ms); `require_tools()`
  lets a caller fail AT CONNECT with a deploy hint instead of mid-run as a
  mystery. (No L3 verb registry exists yet to call this automatically --
  that lands with the first L3 family; see the design doc §1's own note that
  verb families land "verb-by-verb as consumers need them".)
- **game-focus preflight** -- the game does not render, and therefore the
  bridge's main-thread calls do not complete, while its window is
  unfocused. `Session(focus=True)` (the default) brings it forward for the
  session's lifetime and restores whatever had focus before, on exit.
- **optional bridge-lock integration** -- `Session(lock="rimflow")` takes and
  releases the project's one bridge-driver lock through `rimflow bridge`, so
  a script cannot forget the release. KNOWN LIMITATION: this shells out to
  `python3 rimflow/cli.py`, a WSL-side tool with no socket of its own: it
  works when the whole process runs under WSL python3, but NOT when this
  Session itself runs under `python.exe` (which everything touching the
  actual bridge socket must, per the WSL-loopback limitation in
  rimbridge_client.py) -- there is no wiring yet from a Windows python.exe
  process back into WSL to take the lock. `lock="rimflow"` raises
  `SessionError` naming this rather than silently no-op'ing. File a follow-up
  if a live consumer needs it before it's built.

One `Session` per process -- a second concurrent instance is refused, per the
design doc's concurrency ruling and the 2026-08-15 two-driver stall.
"""
import os
import subprocess
import sys
import time

_UTILS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _UTILS not in sys.path:
    sys.path.insert(0, _UTILS)
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402
import game_focus  # noqa: E402

from .verify import Reconnected, mutate as _mutate  # noqa: E402

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_UTILS))))
_RIMFLOW_CLI = os.path.join(_REPO_ROOT, "src", "RimMandrake", "rimflow", "cli.py")

# A timeout/dropped-connection poisons the socket (skill rimbridge §1); these
# are the shapes that mean "the wire died", not "the game said no".
_RECONNECTABLE = (ConnectionError, OSError, TimeoutError)

_ACTIVE = []   # module-level: enforces "one Session per process"


class SessionError(RuntimeError):
    """A rimdrive session could not do what was asked of it."""


class ToolCensusError(SessionError):
    """A caller needs a jawa/ tool this connection's census does not have."""


class Session(object):
    """A connected bridge session with reconnect, verified pause, litter
    tracking and an optional bridge lock built in.

    `strict` (default True) makes `mutate()` raise `verify.Unchanged` when a
    verifier says nothing happened. Set False for exploration, where a no-op
    is information rather than an error.
    """

    def __init__(self, strict=True, quiet=False, lock=None, focus=True,
                 settle=0, host=None, port=None, token=None):
        if _ACTIVE:
            raise SessionError(
                "a Session is already open in this process (one per process, "
                "by design -- see the 2026-08-15 two-driver stall). Close it "
                "first, or run this in a separate process.")
        self.strict = strict
        self.quiet = quiet
        self.settle = settle
        self._lock = lock
        self._lock_taken = False
        self._focus = focus
        self._focus_prev = None
        self._host, self._port, self._token = host, port, token
        self._rb = None
        self.tools = set()
        self.calls = 0
        self.mutations = 0
        self.no_ops = []
        self.unverified = []
        self.litter = []
        self._shots = 0

    # ------------------------------------------------------------ lifecycle
    def __enter__(self):
        self.connect()
        _ACTIVE.append(self)
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            self.sweep()
        finally:
            self._disconnect()
            if self._lock_taken:
                self._bridge_release()
            if self._focus_prev is not None:
                game_focus.restore_focus(self._focus_prev)
            if self in _ACTIVE:
                _ACTIVE.remove(self)
        return False   # never swallow the caller's exception

    def connect(self):
        if self._lock == "rimflow":
            self._bridge_take()
        if self._focus:
            self._focus_prev = game_focus.preflight()
        self._open()
        if self.settle:
            # See bridgetools/load_session.py's settle(): the bridge answering
            # is not the game being reactive. Owner-measured ~40s window.
            time.sleep(self.settle)

    def _open(self):
        host, port, token = resolve_endpoint(self._host, self._port, self._token)
        if not token:
            raise SessionError(
                "No bridge token (CLI/env/Player.log). Is RimWorld running "
                "with RimBridgeServer active?")
        self._rb = RimBridge(host, port, token)
        self._rb.__enter__()
        self.tools = {t.get("name") for t in self._rb.list_tools()}

    def _disconnect(self):
        if self._rb is not None:
            try:
                self._rb.__exit__(None, None, None)
            except Exception:
                pass
            self._rb = None

    def _reconnect(self):
        """The socket is poisoned. Drop it and reopen -- never re-issue the
        call that timed out; that is `verify.mutate()`'s decision to make,
        against a post-condition, not this method's."""
        self._disconnect()
        self._open()

    def require_tools(self, *names):
        """Fail now, with a deploy hint, rather than mid-run as a mystery."""
        missing = [n for n in names if n not in self.tools]
        if missing:
            raise ToolCensusError(
                "missing tool(s) %s -- stale companion deploy. Rebuild+deploy: "
                "python.exe src/RimMandrake/bridgetools/build.py --gm --apply"
                % ", ".join(sorted(missing)))

    # -------------------------------------------------------- bridge lock
    def _bridge_take(self):
        try:
            r = subprocess.run(
                ["python3", _RIMFLOW_CLI, "bridge", "take", "--for",
                 "rimdrive.Session"],
                capture_output=True, text=True, cwd=_REPO_ROOT)
        except FileNotFoundError:
            raise SessionError(
                "lock='rimflow' needs a WSL-side `python3` to drive "
                "rimflow/cli.py; not available from this process (see this "
                "module's docstring, 'optional bridge-lock integration'). "
                "Take the bridge yourself: rimflow bridge take --for '...'")
        if r.returncode != 0:
            raise SessionError("could not take the bridge: %s"
                               % (r.stdout + r.stderr).strip())
        self._lock_taken = True

    def _bridge_release(self):
        try:
            subprocess.run(["python3", _RIMFLOW_CLI, "bridge", "release"],
                           capture_output=True, text=True, cwd=_REPO_ROOT)
        except FileNotFoundError:
            pass    # best-effort on the way out; _bridge_take already warned
        self._lock_taken = False

    # ---------------------------------------------------------- raw calls
    def call(self, tool, **params):
        self.calls += 1
        try:
            return self._rb.call(tool, params)
        except _RECONNECTABLE:
            self._reconnect()
            raise Reconnected(
                "%s was in flight when the socket died; reconnected. Its "
                "effect is UNKNOWN until a post-condition says otherwise."
                % tool)

    def action(self, path, **params):
        """Run a debug action. `path` uses real backslashes."""
        return self.call("rimworld/execute_debug_action", path=path, **params)

    def log(self, msg):
        if not self.quiet:
            print("   " + msg)

    # ------------------------------------------------------- L2 mutation
    def mutate(self, what, do, verify, idempotent=False):
        """See `rimdrive.verify.mutate` -- this is that function bound to
        `self`, kept as a method because every rimbench-era caller already
        writes `session.mutate(...)`."""
        return _mutate(self, what, do, verify, idempotent=idempotent)

    # ------------------------------------------------------------ reading
    def cell(self, x, z):
        return self.call("rimworld/get_cell_info", x=x, z=z)["cell"]

    def things_at(self, x, z):
        return [t.get("defName") for t in (self.cell(x, z).get("things") or [])]

    def pawns_at(self, rect):
        """`rect` is 'x,z,w,h'. Independent of `things_at` -- get_cell_info's
        `things` list does not include pawns (rimbench.core's own lesson)."""
        r = self.call("jawa/list_pawns", rect=rect)
        return (r or {}).get("pawns") or []

    def _ticks(self):
        st = (self.call("rimbridge/get_bridge_status") or {}).get("state") or {}
        return st.get("ticksGame")

    # ------------------------------------------------------- pause discipline
    def paused(self):
        """Context manager: pause, VERIFY it (ticksGame read twice through an
        independent channel), restore on exit -- verified the same way. See
        module docstring re: the 2026-08-12 two-pawn colony loss."""
        return _PausedCtx(self)

    # --------------------------------------------------------------- litter
    def track(self, kind, id_, x=None, z=None):
        """Record something this session spawned, for `sweep()`. `kind` is
        'thing' or 'pawn' -- they are torn down differently (see `sweep`)."""
        self.litter.append({"kind": kind, "id": id_, "x": x, "z": z})

    def sweep(self):
        """Tear down everything tracked, then prove the area is empty on an
        INDEPENDENT read. Runs from `__exit__` on every exit path, including
        an exception -- build-up and tear-down are absolute (modcheck spec
        §1b): a chain that dies partway must not leave the map dirtier than
        it found it.

        Returns {"swept": n, "left": [...]}; `left` is never silently
        dropped -- a caller that cares checks it.
        """
        if not self.litter:
            return {"swept": 0, "left": []}

        things = [l for l in self.litter if l["kind"] == "thing"]
        pawns = [l for l in self.litter if l["kind"] == "pawn"]

        for l in things:
            if l["x"] is None:
                continue
            self.call("jawa/destroy_batch",
                      rects="%d,%d,1,1" % (l["x"], l["z"]), categories="All")

        # jawa/destroy_batch NEVER destroys pawns, by design (a bad rect must
        # not be able to kill a colonist). The only route to remove a spawned
        # TEST pawn is: kill it (lethal jawa/damage; litter is never a player
        # colonist, so the allowColonists safety rail never needs overriding),
        # which turns it into a Corpse -- an Item, not a pawn -- then
        # destroy_batch that.
        for l in pawns:
            self.call("jawa/damage", thingId=l["id"], damageDef="Bomb",
                      amount=99999.0)
            if l["x"] is not None:
                self.call("jawa/destroy_batch",
                          rects="%d,%d,1,1" % (l["x"], l["z"]), categories="Item")

        left = []
        if pawns:
            alive = {p.get("id") for p in
                     (self.call("jawa/list_pawns", limit=500) or {}).get("pawns") or []}
            left += [l for l in pawns if l["id"] in alive]
        for l in things:
            if l["x"] is None:
                left.append(l)
                continue
            still = self.things_at(l["x"], l["z"])
            if still:
                left.append(dict(l, remaining=still))

        swept = len(self.litter) - len(left)
        self.litter = left
        return {"swept": swept, "left": left}

    # --------------------------------------------------------------- report
    def summary(self):
        return ("%d calls, %d verified mutations, %d no-ops, %d unverified%s"
                % (self.calls, self.mutations, len(self.no_ops),
                   len(self.unverified),
                   (": " + "; ".join(self.no_ops[:3])) if self.no_ops else ""))


class _PausedCtx(object):
    def __init__(self, session):
        self.s = session

    def __enter__(self):
        self.s.call("rimworld/pause_game", pause=True)
        t1 = self.s._ticks()
        time.sleep(0.2)
        t2 = self.s._ticks()
        if t1 is None or t2 is None or t1 != t2:
            raise SessionError(
                "pause_game reported success but ticksGame moved (%s -> %s) "
                "or could not be read -- the game is NOT actually paused."
                % (t1, t2))
        return self.s

    def __exit__(self, exc_type, exc, tb):
        self.s.call("rimworld/pause_game", pause=False)
        t1 = self.s._ticks()
        time.sleep(0.2)
        t2 = self.s._ticks()
        if t1 is not None and t2 is not None and t1 == t2:
            raise SessionError(
                "pause_game(False) reported success but ticksGame did not "
                "move (%s -> %s) -- the game is NOT actually unpaused."
                % (t1, t2))
        return False
