"""scene_hands.py - the two hands that can play a run, behind one shape, and the check of a kept trace.

Page: design/specs/2026-11-23-scene-library/boundary.md. The wire of jawa/session and jawa/run_until is
design/specs/2026-11-23-bridge-v2-hands/boundary.md; the wire of jawa/scene_slice and the trace are
design/specs/2026-11-23-bridge-v2/boundary.md. Nothing here decides a verdict."""
import json

import scene_cond as C
from scene_core import Fault, Refused, ReplyLost

RUN_UNTIL, SLICE, SESSION = "jawa/run_until", "jawa/scene_slice", "jawa/session"
WHY = {"hit": "hit", "done": "limit", "limit": "limit", "unknown": "unknown", "cancelled": "cancelled", "stopped": "fault",
       "error": "fault", "epoch": "fault", "aborted": "fault", "threw": "fault", "budget": "fault", "fault": "fault"}
# the game's refusal name -> the page's (scene_contracts/run.md); every other name of the game stays itself, as a Fault
REFUSALS = {"NO_LIMIT": "NO_LIMIT", "GAME_RUNNING": "GAME_RUNNING", "RUN_ACTIVE": "RUN_ACTIVE", "BAD_PATH": "BAD_PATH",
            "PATH_CALLS_METHOD": "BAD_PATH", "UNKNOWN_GROUP": "BAD_PATH", "EMPTY_GROUP": "BAD_PATH",
            "OPTIONAL_COUNTS_UNKNOWN_FALSE": "UNRECORDED_VALUE", "BAD_CONDITION": "UNRECORDED_VALUE"}


def _target(of):
    """A thing id that is no other kind of target is sent as thing:<id> (no alias is bound until s.stage is built)."""
    return of if ":" in of or of in ("map", "game", "world", "$") else "thing:" + of


def _retarget(node, key):
    if isinstance(node, dict):
        return {k: (_target(v) if k == key and isinstance(v, str) else _retarget(v, key)) for k, v in node.items()}
    return [_retarget(x, key) for x in node] if isinstance(node, list) else node


class RunUntil(object):
    """jawa/run_until inside a jawa/session: request ids, any value path, several runs in one trace."""
    tool = RUN_UNTIL
    request_ids = True

    def __init__(self, call, driver):
        self.call, self.driver, self.names = call, driver, {}

    def plan(self, tree, tracks):
        # the game names a track "thing:Human12.path", or by the canonical text of its probe (JawaBenchHandsCore.TrackName)
        for p, _opt in C.walk(tree):
            if p["p"] not in C.VALUE_PROBES:
                self.names[C.conds.canon(p)] = C.probe_name(p)
        return {"until": _retarget(tree, "of"), "record": [{"of": _target(t.of), "path": t.path} for t in tracks]}

    def start(self, request, plan, limit, speed):
        r = self.call(RUN_UNTIL, action="start", driver=self.driver, request=request, until=json.dumps(plan["until"], sort_keys=True),
                      limit=limit, speed=speed, record=json.dumps(plan["record"], sort_keys=True))
        return self._read(r, request)

    def find(self, request):
        """-> the run of this request, or None when the game does not know the id."""
        r = self.call(RUN_UNTIL, action="status", driver=self.driver, request=request)
        if r.get("success") is False and r.get("refused") == "UNKNOWN_REQUEST":
            return None
        if r.get("success") is True and (r.get("request") != request or not r.get("run")):
            raise Fault("COULD_NOT_LOOK", detail="%s did not identify the run for request %s" % (RUN_UNTIL, request), request=request)
        return self._read(r, request)

    def live(self):
        """-> the id of a run that has not ended, or None."""
        r = self.call(SESSION, action="state", driver=self.driver)
        last = r.get("lastRun")
        if r.get("success") is not True:
            raise Fault("COULD_NOT_LOOK", detail="jawa/session did not say its state: %s" % str(r))
        return (last.get("request") or last.get("run")) if isinstance(last, dict) and last.get("stage") not in (None, "none", "closed") else None

    def cancel(self, request):
        return self._read(self.call(RUN_UNTIL, action="cancel", driver=self.driver, request=request), request)

    def _read(self, r, request):
        if r.get("success") is not True:
            name = r.get("refused")
            say = "%s %s" % (r.get("message") or r.get("detail") or str(r), r.get("repair") or "")
            if name in REFUSALS:
                raise Refused(REFUSALS[name], "%s (the game: %s)" % (say.strip(), name))
            raise Fault(name or "RUN_NOT_STARTED", detail=say.strip(), request=request)
        return {"run": r.get("run"), "request": request, "stage": r.get("stage"), "state": r.get("state") or r.get("why"),
                "why": r.get("why"), "tick": r.get("tick"), "tickFrom": r.get("tickFrom"), "rows": r.get("rows"),
                "recordDir": r.get("recordDir"), "writer": r.get("writerSession"), "detail": r.get("unknownValue") or r.get("detail") or r.get("faults")}

    def name(self, track):
        return self.names.get(track) or (track[6:] if track.startswith("thing:") else track)

    def note(self):
        return []


class Slice(object):
    """jawa/scene_slice: one pawn is asked for, and there is no request id. Kept until jawa/run_until has landed."""
    tool = SLICE
    request_ids = False

    def __init__(self, call):
        self.call, self.pawn, self.before, self.lost = call, None, None, False

    def plan(self, tree, tracks):
        def probe(of, path):
            if ":" in of and not of.startswith("thing:") or of in ("map", "game", "world"):
                raise Refused("BAD_PATH", "%s.%s: the hand in this game (%s) reads the fields of a thing only; a static, a def or the "
                              "map needs %s (a newer companion)" % (of, path, SLICE, RUN_UNTIL))
            return {"p": "thing.field", "thing": of[6:] if of.startswith("thing:") else of, "path": path}

        def go(n):
            if isinstance(n, dict):
                if n.get("p") == "value":
                    return probe(n["of"], n["path"])
                if n.get("p") == "value.state" or "any_of" in n or "all_of" in n:
                    raise Refused("UNRECORDED_VALUE", "gone_ok() and groups need %s, which this game's companion does not have" % RUN_UNTIL)
                return {k: go(v) for k, v in n.items()}
            return [go(x) for x in n] if isinstance(n, list) else n
        sample = {}
        for p, _opt in C.walk(tree):
            if p["p"] != C.TICK:
                sample[C.probe_name(p)] = go(p)
        for t in tracks:
            sample[t.name] = probe(t.of, t.path)
        return {"until": go(tree), "record": sample}

    def start(self, request, plan, limit, speed):
        self.before = self._status().get("run")
        rows = self.call("jawa/pawn_get", limit=200).get("pawns")
        if not isinstance(rows, list):
            raise Fault("COULD_NOT_LOOK", detail="the pawns of the map could not be read, and %s asks for one" % SLICE)
        if not rows:
            raise Fault("NO_PAWN", detail="%s asks for a pawn and the map has none (looked, found none)" % SLICE)
        self.pawn = next((p for p in rows if p.get("faction") == "PlayerColony"), rows[0])["thingId"]
        r = self.call(SLICE, action="start", pawn=self.pawn, until=json.dumps(plan["until"], sort_keys=True), maxTicks=limit, speed=speed,
                      tracks=json.dumps(plan["record"], sort_keys=True))
        if r.get("success") is not True:
            name, at = r.get("refused"), str(r.get("at") or "")
            if name:
                raise Refused("BAD_PATH" if "sample" in at else "UNRECORDED_VALUE", "%s at %s: %s" % (name, at, r.get("detail")))
            raise Fault("RUN_NOT_STARTED", detail=str(r.get("message") or r), request=request)
        return self._read(r, request)

    def find(self, request):
        """No id in the game: the run is ours when it is not the run that was there before the call (we hold the driver lock)."""
        r = self._status()
        self.lost = True
        return None if r.get("run") in (None, self.before) else self._read(r, request)

    def live(self):
        r = self._status()
        return r.get("run") if r.get("stage") not in (None, "none", "closed") else None

    def cancel(self, request):
        return self._read(self.call(SLICE, action="cancel"), request)

    def _status(self):
        r = self.call(SLICE, action="status")
        if "stage" not in r:
            raise Fault("COULD_NOT_LOOK", detail="%s did not say its state: %s" % (SLICE, str(r)))
        return r

    def _read(self, r, request):
        res = r.get("result") if isinstance(r.get("result"), dict) else {}
        return {"run": r.get("run"), "request": request, "stage": r.get("stage"), "state": r.get("state"), "why": WHY.get(r.get("state")),
                "tick": r.get("endTick"), "tickFrom": res.get("tickFrom"), "rows": r.get("rows"), "recordDir": r.get("recordDir"),
                "writer": r.get("session"), "detail": r.get("why") or r.get("lastFault"),
                "unknown": [v for v in res.get("values") or [] if v.get("status") not in (None, "ok", "ignored")]}

    def name(self, track):
        return track

    def note(self):
        out = ["the run was played by %s (%s is not in this game's companion); it asked for a pawn and was given %s" % (SLICE, RUN_UNTIL, self.pawn)]
        if self.lost:
            out.append("%s has no request id: the run was known as the first one that began after the call" % SLICE)
        return out


# ------------------------------------------------------------------------------------------------ the kept trace
def trace_fault(rows):
    """None when the records of one run are whole, else the point that is not. Pure."""
    def recs(k):
        return [r for r in rows if r.get("rec") == k]
    if len(recs("open")) != 1 or len(recs("end")) != 1 or len(recs("close")) != 1:
        return "open/end/close records: %s, want one of each" % [len(recs(k)) for k in ("open", "end", "close")]
    if rows[-1].get("rec") != "close":
        return "the closing record is not the last one"
    ns = [r.get("n") for r in rows]
    if None in ns or ns != list(range(ns[0], ns[0] + len(ns))):
        return "a gap in the row numbers: %s" % [a for a, b in zip(ns, ns[1:]) if b != (a or 0) + 1][:3]
    c = recs("close")[0]
    if c.get("drained") is not True or c.get("dropped") != 0:
        return "drained %s, dropped %s" % (c.get("drained"), c.get("dropped"))
    if c.get("rows") != len(rows) - 1:
        return "the closing record counts %s rows, the file holds %d" % (c.get("rows"), len(rows) - 1)
    return None


def ran_on(rows):
    """None, or what the trace says about ticks after the stop or a pause that did not hold. -> (fault name, detail)."""
    for r in rows:
        if r.get("rec") == "fault" and r.get("what") in ("ran_past_end", "pause_refused"):
            return ("RAN_PAST_END" if r["what"] == "ran_past_end" else "PAUSE_REFUSED"), str(r.get("detail"))
    e = next(r for r in rows if r.get("rec") == "end")
    c = next(r for r in rows if r.get("rec") == "close")
    if c.get("paused") is not True:
        return "PAUSE_REFUSED", "the closing record says paused=%s" % c.get("paused")
    if c.get("tickAfter") != e.get("tick"):
        return "RAN_PAST_END", "the run ended on tick %s and the game stood on %s" % (e.get("tick"), c.get("tickAfter"))
    return None


def other_faults(rows):
    return ["%s: %s" % (r.get("what"), r.get("detail")) for r in rows if r.get("rec") == "fault"]


def last_values(rows):
    """-> {track: (state, v, detail, tick)} at the end of the last tick."""
    return {r["name"]: (r.get("st"), r.get("v"), r.get("detail"), r.get("tick")) for r in rows if r.get("rec") == "track" and r.get("phase") == "last"}


def unreadable(rows):
    """-> {track: (state, first tick, ticks, detail)} for each track that was not readable on some tick."""
    end = rows[-1].get("tick")
    by, out = {}, {}
    for r in rows:
        if r.get("rec") == "track" and r.get("phase") != "last":
            by.setdefault(r["name"], []).append(r)
    for name, rs in by.items():
        for i, r in enumerate(rs):
            if r.get("st") == "ok":
                continue
            to = rs[i + 1]["tick"] if i + 1 < len(rs) else end + 1
            st, first, n, d = out.get(name, (r.get("st"), r["tick"], 0, r.get("detail")))
            out[name] = (st, first, n + max(to - r["tick"], 0), d)
    for name, (st, _v, d, tick) in last_values(rows).items():
        if st != "ok" and name not in out:
            out[name] = (st, tick, 1, d)
    return out


__all__ = ["RunUntil", "Slice", "ReplyLost", "trace_fault", "ran_on", "other_faults", "last_values", "unreadable", "RUN_UNTIL", "SLICE", "SESSION"]
