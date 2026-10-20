"""preconditions.py -- a row may read PASS or FAIL only when every precondition it stands on was confirmed.

PROOF_VERDICTS_REPAIR_SAME_BUG_EVERY_ROUND (2026-10-20). Three fresh reviews in a row found NEW call sites in the proof
scripts where a refused bridge call, a staging that did not take or a dead probe read was scored as a mod FAIL, or let a
row PASS vacuously. Each fix guarded one call; the next review found the next call. This module inverts the default: the
harness records every failure it can see, and a verdict is withheld by construction.

    import preconditions as PC
    pre = PC.Preconditions()
    with pre.scope("scene 3"):                 # what is staged inside a scope belongs to the rows emitted inside it
        r = bridge_call(...)                   # the harness calls pre.reply(tool, kw, r) for every call
        pre.require(kv.get("ok") == "True", "bridge built", txt)     # a read-back that must hold
        status, cls, detail = pre.judge("FAIL", "MOD", detail)       # -> UNMEASURED/<fault's class> if anything above failed

A FAULT is recorded in the innermost open scope when
  - a bridge reply is not a dict, or says success=False                      (HARNESS: could not ask)
  - a known staging tool answered success but did not take (NOOP_CHECKS)     (SITE: the scene is not what the row assumes)
  - a probe channel failed (no frame serviced it, unparseable result)        (HARNESS)
  - require(cond, ...) is false                                              (SITE by default)
`judge(status, ...)` turns a PASS or FAIL into UNMEASURED while ANY open scope holds a fault, names the faults, and keeps
the withheld verdict in the detail. UNMEASURED/SKIP/anything else passes through. Faults die with their scope, so a
fault in scene 3 never touches scene 4; a fault in a block's opening staging taints every row of that block.

A reply that IS the measured answer (the mod's own refusal under test, an existence probe, best-effort cleanup) is
passed with `answer=True` and is never a fault: the caller judges it.

No scope open: nothing is recorded and nothing is judged. A harness user that never opens a scope behaves exactly as
before (backward compatibility for validation_hose, proof_all and every modcheck suite that does not opt in).
"""
import contextlib

PASS, FAIL, UNMEASURED = "PASS", "FAIL", "UNMEASURED"
MAX_FAULTS = 40


def _asked_ops(kw):
    return [o for o in str((kw or {}).get("ops") or "").split(";") if o.strip()]


def _noop_build(kw, r):
    survived = r.get("survived")
    asked = len(_asked_ops(kw))
    if survived is not None and asked and int(survived) < asked:
        return "built %s of %d asked (failed: %s)" % (survived, asked, str(r.get("failed"))[:160])
    return None


def _noop_spawn_pawn(kw, r):
    pawns = [p for p in (r.get("pawns") or []) if isinstance(p, dict) and p.get("id")]
    want = int((kw or {}).get("count") or 1)
    if len(pawns) < want:
        return "spawned %d of %d pawns" % (len(pawns), want)
    return None


def _noop_set_draft(kw, r):
    if "drafted" in r and "drafted" in (kw or {}) and bool(r.get("drafted")) != bool(kw.get("drafted")):
        return "drafted reads %r, asked %r" % (r.get("drafted"), kw.get("drafted"))
    return None


def _noop_roof(kw, r):
    if r.get("cellsFailedVerify"):
        return "roof write did not read back on %s cells" % r.get("cellsFailedVerify")
    return None


# tool -> fn(kw, reply) returning why the call did not take (None when it took or the reply carries no evidence either way).
# Only fields the harness already reads elsewhere are trusted here; a reply without the field is NOT a fault.
NOOP_CHECKS = {
    "jawa/build_batch": _noop_build,
    "jawa/spawn_pawn": _noop_spawn_pawn,
    "jawa/set_draft": _noop_set_draft,
    "jawa/set_roof_batch": _noop_roof,
}


def refusal(tool, kw, r):
    """Why this reply means the call did not happen or did not take, as (class, why); None when it did."""
    if not isinstance(r, dict):
        return "HARNESS", "no reply (%s)" % str(r)[:120]
    if r.get("success") is False:
        return "HARNESS", "refused: %s" % str(r.get("error") or r.get("message") or r.get("raw") or r)[:200]
    chk = NOOP_CHECKS.get(tool)
    why = chk(kw, r) if chk else None
    if why:
        return "SITE", why
    return None


class Preconditions(object):
    """A stack of scopes, each holding the faults recorded while it was the innermost one."""

    def __init__(self):
        self.frames = []
        self._quiet = 0

    @contextlib.contextmanager
    def quiet(self):
        """Harness housekeeping with its own read-back gate (prepare_site, site recovery, the log tap): its replies are not
        the rows' preconditions, so nothing inside is recorded."""
        self._quiet += 1
        try:
            yield
        finally:
            self._quiet -= 1

    def active(self):
        return bool(self.frames)

    @contextlib.contextmanager
    def scope(self, name):
        frame = {"name": name, "faults": []}
        self.frames.append(frame)
        try:
            yield frame
        finally:
            if frame in self.frames:
                del self.frames[self.frames.index(frame):]

    def fault(self, what, why, cls="HARNESS"):
        if not self.frames or self._quiet:
            return
        f = self.frames[-1]["faults"]
        if len(f) < MAX_FAULTS:
            f.append({"scope": self.frames[-1]["name"], "what": str(what)[:120], "why": str(why)[:240], "class": cls})

    def adopt(self, *frames):
        """Carry CLOSED scopes' faults into the current one: a staging run in its own scope, whose result a later row
        depends on."""
        for frame in frames:
            for x in (frame or {}).get("faults") or []:
                self.fault(x.get("what"), x.get("why"), x.get("class", "SITE"))

    def require(self, ok, what, detail=None, cls="SITE"):
        """A precondition read back: when it does not hold, every PASS/FAIL judged in this scope is withheld."""
        if not ok:
            self.fault(what, detail if detail is not None else "did not hold", cls)
        return bool(ok)

    def reply(self, tool, kw, r, answer=False):
        """Record a bridge reply that refused or did not take. `answer=True`: the reply is the measurement, the caller judges."""
        if answer or not self.frames or self._quiet:
            return r
        bad = refusal(tool, kw, r)
        if bad:
            self.fault(tool, bad[1], bad[0])
        return r

    def pending(self):
        return [x for f in self.frames for x in f["faults"]]

    def judge(self, status, cls, detail):
        """(status, class, detail) after the precondition rule: a PASS or FAIL with any pending fault is UNMEASURED."""
        if status not in (PASS, FAIL) or not self.frames:
            return status, cls, detail
        p = self.pending()
        if not p:
            return status, cls, detail
        d = dict(detail) if isinstance(detail, dict) else {"detail": detail}
        d["verdictWithheld"] = status
        d["unmeasuredBecause"] = p[:8]
        if len(p) > 8:
            d["unmeasuredBecauseMore"] = len(p) - 8
        return UNMEASURED, p[0]["class"], d
