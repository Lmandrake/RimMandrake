"""TICKBURST_PROVE_MANY_TICKS_ONE_FRAME: one switchable clock step for the equivalence arms.

A proof that takes part in the experiment routes its DIRECT clock steps through `Stepper.advance(n)` instead of calling
`rimworld/step_game_ticks` itself. The arm is chosen by `--step` (stripped from argv by `take_args`) or by the env var
TICKBURST_STEP; a proof's default stays what it did before (`step`), so nothing is adopted by this switch alone.

Arms (design/RimMandrake/tickburst_2026-11-06/final.md §2.1):
  play   R: unpaused Normal speed, UltraSpeedBoost false; the game is paused again once ticksGame reaches the target and the
            overshoot is recorded. Counts only if ticksGame is seen to move (set_time_speed has left the game paused before,
            MODCHECK_ULTRAFAST_CLOCK_STALL_1).
  step   A: rimworld/step_game_ticks, paused, one tick per frame (today's direct callers).
  safe   B/C: jawa/safe_advance, chunk 60, frame budget --step-budget-ms (40 = B, 200 = C), optional --step-cap
            (perFrameTickCap, 0 = unlimited) for the N-per-frame sweep.

Every advance re-reads ticksGame before and after (never inferred from "executed") and appends one JSON line to
TICKBURST_STEP_LOG when set, so the bench runner can join a proof's verdicts to how its clock moved.
"""
import json
import os
import time

MODES = ("play", "step", "safe")
ENV_MODE, ENV_BUDGET, ENV_CAP, ENV_LOG = "TICKBURST_STEP", "TICKBURST_STEP_BUDGET_MS", "TICKBURST_STEP_CAP", "TICKBURST_STEP_LOG"
PLAY_STALL_S = 5.0          # an unpaused clock that does not move in this long is a stall, not a slow game
PLAY_POLL_S = 0.05


def take_args(argv, default="step"):
    """Strip `--step MODE`, `--step-budget-ms X`, `--step-cap N` (also `--opt=value`) from `argv`.
    -> (rest, opts dict). Env vars fill what argv leaves out. Raises ValueError on a bad value."""
    opts = {"mode": os.environ.get(ENV_MODE) or default,
            "budget_ms": float(os.environ.get(ENV_BUDGET) or 40),
            "cap": int(os.environ.get(ENV_CAP) or 0)}
    keys = {"--step": ("mode", str), "--step-budget-ms": ("budget_ms", float), "--step-cap": ("cap", int)}
    rest, i = [], 0
    argv = list(argv)
    while i < len(argv):
        a = argv[i]
        k, _, v = a.partition("=")
        if k in keys:
            if not _:
                if i + 1 >= len(argv):
                    raise ValueError("%s needs a value" % k)
                v = argv[i + 1]
                i += 1
            name, typ = keys[k]
            opts[name] = typ(v)
        else:
            rest.append(a)
        i += 1
    if opts["mode"] not in MODES:
        raise ValueError("--step must be one of %s, not %r" % ("|".join(MODES), opts["mode"]))
    if not 5 <= opts["budget_ms"] <= 200:
        raise ValueError("--step-budget-ms must be 5..200 (safe_advance clamps there)")
    if opts["cap"] < 0:
        raise ValueError("--step-cap must be >= 0")
    return rest, opts


def _ticks(call):
    r = call("jawa/time_clock") or {}
    try:
        return int(r.get("ticksGame"))
    except (TypeError, ValueError):
        return None


class Stepper:
    """`call(tool, **kw) -> dict`. `advance(n)` -> a record dict; `ok` False means the clock did not move as asked."""

    def __init__(self, call, mode="step", budget_ms=40.0, cap=0, log_path=None, label=""):
        if mode not in MODES:
            raise ValueError(mode)
        self.call, self.mode, self.budget_ms, self.cap, self.label = call, mode, float(budget_ms), int(cap), label
        self.log_path = log_path if log_path is not None else os.environ.get(ENV_LOG)
        self.records = []

    @classmethod
    def from_opts(cls, call, opts, label=""):
        return cls(call, opts["mode"], opts["budget_ms"], opts["cap"], label=label)

    def arm(self):
        if self.mode == "step":
            return "A"
        if self.mode == "play":
            return "R"
        return ("B" if self.budget_ms < 200 else "C") + ("" if not self.cap else "@%d" % self.cap)

    def advance(self, n, timeout_ms=None, why=""):
        n = int(n)
        rec = {"label": self.label, "why": why, "mode": self.mode, "arm": self.arm(), "requested": n,
               "budgetMs": self.budget_ms if self.mode == "safe" else None, "perFrameTickCap": self.cap if self.mode == "safe" else None}
        t0 = _ticks(self.call)
        w0 = time.time()
        rec["t0"] = t0
        if n <= 0:
            rec.update(t1=t0, moved=0, ok=True)
            return self._done(rec, w0)
        if t0 is None and self.mode != "step":
            rec.update(ok=False, unmeasured="ticksGame unreadable before the step")
            return self._done(rec, w0)
        timeout_ms = int(timeout_ms or max(60000, n * 40))
        if self.mode == "step":
            rec["reply"] = _short(self.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=timeout_ms))
        elif self.mode == "safe":
            r = self.call("jawa/safe_advance", ticks=n, chunk=60, frameBudgetMs=self.budget_ms, perFrameTickCap=self.cap,
                          timeoutMs=timeout_ms, frameSamples=True) or {}
            rec["reply"] = _short(r)
            for k in ("state", "executed", "frames", "stepMs", "maxFrameMs", "perFrameTickCap", "frameBudgetMs", "frameStats"):
                rec["sa_" + k] = r.get(k)
            if r.get("state") == "running":
                self.call("jawa/safe_advance", action="cancel")
        else:
            self._play(rec, t0 + n, timeout_ms / 1000.0)
        t1 = _ticks(self.call)
        rec["t1"] = t1
        if t0 is None:
            # arm A only, on a bridge with no clock reader (the proofs' offline mocks): today's behaviour, the reply decides
            rec.update(moved=None, clock="unread", ok=(rec.get("reply") or {}).get("success") is not False)
            return self._done(rec, w0)
        rec["moved"] = None if t1 is None else t1 - t0
        if self.mode == "play":
            rec["overshoot"] = None if t1 is None else t1 - (t0 + n)
            rec["ok"] = rec.get("unmeasured") is None and t1 is not None and t1 >= t0 + n
        else:
            rec["ok"] = rec["moved"] == n
        if not rec["ok"] and not rec.get("unmeasured"):
            rec["unmeasured"] = "clock moved %s of %d ticks" % (rec["moved"], n)
        return self._done(rec, w0)

    def _play(self, rec, target, limit_s):
        self.call("rimworld/set_time_speed", speed="Normal", ultraSpeedBoost=False)
        self.call("rimworld/pause_game", pause=False)
        c = self.call("jawa/time_perf") or {}
        rec["readback"] = {"curTimeSpeed": c.get("curTimeSpeed"), "paused": c.get("paused"), "ultraSpeedBoost": c.get("ultraSpeedBoost")}
        start, last, last_move = time.time(), _ticks(self.call), time.time()
        try:
            while True:
                t = _ticks(self.call)
                if t is not None and t >= target:
                    break
                now = time.time()
                if t is not None and t != last:
                    last, last_move = t, now
                if now - last_move > PLAY_STALL_S:
                    rec["unmeasured"] = "unpaused clock did not move (readback %s)" % rec["readback"]
                    break
                if now - start > limit_s:
                    rec["unmeasured"] = "unpaused clock short of the target at the timeout"
                    break
                time.sleep(PLAY_POLL_S)
        finally:
            self.call("rimworld/pause_game", pause=True)

    def _done(self, rec, w0):
        rec["wallS"] = round(time.time() - w0, 3)
        self.records.append(rec)
        if self.log_path:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, sort_keys=True, default=str) + "\n")
        return rec


def _short(r):
    if not isinstance(r, dict):
        return r
    return {k: r[k] for k in ("success", "state", "executed", "error", "abortWhy", "ticksGame") if k in r}
