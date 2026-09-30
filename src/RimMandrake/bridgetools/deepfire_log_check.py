"""DEEPFIRE_LIVE_FAILURES_1 -- the "no errors from this mod during the proof" check shared by
every prove_deepfire_*.py.

Why it exists: `jawa/drain_log` does NOT drain. It returns the newest entries of the game's
1000-entry Log.Messages buffer, and errorsOnly still includes Warnings. The old checks called it once
at the start "to discard" (which discarded nothing) and then substring-matched the WHOLE JSON of the
second read for "Deepfire". So an unrelated buffer read failed the proof, and so did a warning or an
error from an EARLIER proof (live 2026-09-30, every Deepfire proof).

Now: snapshot (text -> repeats) at the start, then at the end keep only Error-type entries that are
new or whose repeat count rose, and whose text names this mod. Our own "[Deepfire*] {json}" info
lines are Message-type, so they never count.
"""
import re

MOD_PATTERN = re.compile(r"Deepfire|LuminousPigment|Luminous|WornGlow|FirstCoat|Sumptuary")
LIMIT = 1000  # the whole Log.Messages buffer


def _rows(call):
    r = call("jawa/drain_log", errorsOnly=True, limit=LIMIT) or {}
    return [m for m in (r.get("messages") or []) if isinstance(m, dict)]


def _counts(rows, extra=()):
    # The same text can appear as several non-adjacent entries; sum their repeats.
    pat = re.compile(MOD_PATTERN.pattern + "".join("|" + re.escape(k) for k in extra))
    c = {}
    for m in rows:
        if m.get("type") != "Error":
            continue
        text = m.get("text") or ""
        if pat.search(text):
            c[text] = c.get(text, 0) + (m.get("repeats") or 1)
    return c


def baseline(call, extra=()):
    """Call once before the proof's first action. `extra`: more keywords this proof owns."""
    return _counts(_rows(call), extra)


def new_mod_errors(call, base, extra=()):
    """Error-type lines naming this mod that appeared (or repeated again) since `base`."""
    now = _counts(_rows(call), extra)
    return [t[:300] for t, n in now.items() if n > base.get(t, 0)]
