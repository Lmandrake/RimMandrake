"""scene_core.py - what every name of the scene library shares: the refusal, the fault, the receipt, the value.

Page: design/specs/2026-11-23-scene-library/boundary.md. The contract of each name: scene_contracts/. No game, no bridge here."""
import json

STATES = ("ok", "gone", "unbound", "error")
NOT_APPLICABLE = "not applicable"


class Refused(Exception):
    """The call was wrong and nothing was changed. `name` is the refusal, `repair` is what to do."""

    def __init__(self, name, repair, report=None):
        self.name, self.repair, self.report = name, repair, report
        Exception.__init__(self, "%s: %s%s" % (name, repair, "\n%s" % report if report else ""))


class NotBuilt(Refused, AttributeError):
    """A name of the ten that is not built yet (AttributeError too, so hasattr() answers no)."""


class Fault(Exception):
    """The call was tried and the game did something else, or it could not be looked at. `done`: what was changed."""

    def __init__(self, name, done=(), detail="", report=None, **more):
        self.name, self.done, self.detail, self.report = name, list(done), detail, report
        self.__dict__.update(more)
        Exception.__init__(self, "%s: %s | done: %s%s" % (name, detail or "(no detail)", self.done or "nothing",
                                                           "\n%s" % report if report else ""))


class ReplyLost(Exception):
    """A call was sent and no reply came: whether the game did it is not known."""

    def __init__(self, detail, reconcile=None):
        super().__init__(detail)
        self.reconcile = reconcile


class CallFailed(Exception):
    """The bridge answered with an error, or refused the call before it was sent: the call was not done."""


class Receipt(object):
    """What a name did. The build lines are the game's own; a script cannot set them."""

    FIELDS = ("entry", "game", "build", "did", "hands", "could_not_look", "stamps", "commit")

    def __init__(self, name, request, game=NOT_APPLICABLE, build=NOT_APPLICABLE, commit=None):
        self.entry = {"name": name, "request": request}
        self.game, self.build, self.commit = game, build, commit
        self.did, self.hands, self.could_not_look, self.stamps = [], {}, [], []

    def as_dict(self):
        row = {f: getattr(self, f) for f in self.FIELDS}
        if hasattr(self, "deviation"):
            row["deviation"] = self.deviation
        return row

    def __repr__(self):
        return "did: %s\ncould not look: %s" % ("; ".join(self.did) or "[]", "; ".join(self.could_not_look) or "[]")


class Value(object):
    """One value with its state. `v` raises when the state is not ok: an unreadable value is never 0 and never false."""
    __hash__ = None

    def __init__(self, name, state, v, tick, detail=None):
        self.name, self.state, self._v, self.tick, self.detail = name, state if state in STATES else "error", v, tick, detail
        if self.state != state:
            self.detail = "the game's state for it is %r; %s" % (state, detail or "")

    @property
    def v(self):
        if self.state != "ok":
            raise Fault("VALUE_NOT_READ", detail="%s is %s (%s) on tick %s" % (self.name, self.state, self.detail or "no detail", self.tick))
        return self._v

    def _no(self, *_a):
        raise TypeError("a Value is not its number: read .state, then .v (%s)" % self.name)
    __bool__ = __eq__ = __ne__ = __lt__ = __le__ = __gt__ = __ge__ = __int__ = __float__ = __len__ = _no

    def __repr__(self):
        return "%s=%r" % (self.name, self._v) if self.state == "ok" else "%s is %s (%s)" % (self.name, self.state, self.detail or "no detail")


class Reply(dict):
    """A bridge tool's reply as the bridge gave it, with the receipt beside it."""
    receipt = None


class RunResult(object):
    """What s.run returns (scene_contracts/run.md)."""

    def __init__(self, request, why, tick_from, tick, values, trace, detail=None):
        self.request, self.why, self.tick_from, self.tick = request, why, tick_from, tick
        self.values, self.trace, self.detail, self.receipt = values, trace, detail, None

    @property
    def hit(self):
        if self.why == "unknown":
            raise Fault("CONDITION_UNKNOWN", detail="the condition could not be read, so it is neither true nor false: %s" % self.detail)
        return self.why == "hit"

    def __repr__(self):
        return "run %s: %s on tick %s%s" % (self.request, self.why, self.tick, " (%s)" % self.detail if self.detail else "")


def text(x):
    return x if isinstance(x, str) else json.dumps(x, sort_keys=True, default=str)
