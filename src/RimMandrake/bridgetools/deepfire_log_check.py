"""DEEPFIRE_LIVE_FAILURES_1 -- the "no errors from this mod during the proof" check shared by
every prove_deepfire_*.py.

Why it exists: `jawa/drain_log` does NOT drain. It returns the newest entries of the game's
1000-entry Log.Messages buffer, and errorsOnly still includes Warnings. The old checks called it once
at the start "to discard" (which discarded nothing) and then substring-matched the WHOLE JSON of the
second read for "Deepfire". So an unrelated buffer read failed the proof, and so did a warning or an
error from an EARLIER proof (live 2026-09-30, every Deepfire proof).

Now: read the WHOLE buffer (every type, oldest first) at the start and at the end, find where the end
buffer continues the start buffer, and count only the Error-type entries (and repeats) added after it
whose text names this mod. Our own "[Deepfire*] {json}" info lines are Message-type, so they never count.

Engine facts (decompiled Verse/LogMessageQueue.cs, rw16): the queue holds maxMessages = 1000 entries and
drops the OLDEST past that; only the newest entry can combine with an identical message, and its repeat
count stops at 99 (further repeats are dropped, not counted). Verse.Log.messageCount (jawa/health
log.headroom = 10000 - messageCount) rises once per message that was not repeat-capped.

Blind cases that abort instead of passing (BRIDGE_PROOFS_W50_LOG_CHECK_ROLLOVER_AND_REPEAT_CAP):
- the end buffer does not continue the start buffer at any drop count the message counter allows
  (Log cleared, or a rollover the counter cannot bound);
- more messages were logged than the buffer holds (new entries may have rolled out unseen);
- two drop counts fit and disagree about which mod errors are new;
- the start buffer's newest entry is a mod error already at the 99-repeat cap (its repeats during the
  proof were dropped by the engine, so a repeat cannot be seen).
"""
import re

MOD_PATTERN = re.compile(r"Deepfire|LuminousPigment|Luminous|WornGlow|FirstCoat|Sumptuary")
MAXQ = 1000          # Verse.LogMessageQueue.maxMessages
REPEAT_CAP = 99      # LogMessageQueue.Enqueue stops counting repeats here
VERSE_CAP = 10000    # Verse.Log StopLoggingAtMessageCount; headroom = VERSE_CAP - messageCount
LIMIT = 100000       # larger than any buffer: the read must be the whole buffer, checked against totalInBuffer


def _blind(why):
    raise SystemExit("deepfire_log_check is blind, so 'no new errors' would mean nothing: " + why)


def _health(call):
    # A silenced Verse.Log (cap reached / logger off / lock held, reported by jawa/health's log.state) aborts
    # the proof (DEEPFIRELOG_FIX_BLIND_READ_PASSES). Only "emitting" is a seeing log.
    h = call("jawa/health", action="status") or {}
    log = h.get("log") if isinstance(h, dict) else None
    if not isinstance(log, dict) or log.get("state") != "emitting":
        _blind("the game log is not proven to be writing (%s)"
               % ((log.get("text") or log.get("state")) if isinstance(log, dict) else str(h)[:300]))
    m = re.match(r"\s*(\d+)\s+messages before", str(log.get("headroom") or ""))
    count = VERSE_CAP - int(m.group(1)) if m else None
    return count, log.get("capResets")


def _buffer(call):
    # A failed drain_log (no `messages` list), or a read that is not the whole buffer, must never read as clean.
    r = call("jawa/drain_log", errorsOnly=False, limit=LIMIT) or {}
    msgs = r.get("messages") if isinstance(r, dict) else None
    total = r.get("totalInBuffer") if isinstance(r, dict) else None
    if not isinstance(msgs, list) or r.get("success") is False:
        _blind("jawa/drain_log did not return a message list: %s" % str(r)[:300])
    if not isinstance(total, int) or len(msgs) != total or not all(isinstance(m, dict) for m in msgs):
        _blind("jawa/drain_log returned %d row(s) of totalInBuffer=%r: not the whole buffer" % (len(msgs), total))
    return [(m.get("type"), m.get("text") or "", m.get("repeats") or 1) for m in msgs]


def _pat(extra):
    return re.compile(MOD_PATTERN.pattern + "".join("|" + re.escape(k) for k in extra))


def baseline(call, extra=()):
    """Call once before the proof's first action. `extra`: more keywords this proof owns."""
    # counter BEFORE the read: a message logged between the two is over-counted later, never missed
    count, resets = _health(call)
    rows = _buffer(call)
    pat = _pat(extra)
    if rows and rows[-1][0] == "Error" and rows[-1][2] >= REPEAT_CAP and pat.search(rows[-1][1]):
        _blind("the newest log entry is a mod error already at the engine's %d-repeat cap (%r), so its repeats "
               "during the proof would be dropped uncounted" % (REPEAT_CAP, rows[-1][1][:120]))
    return {"rows": rows, "count": count, "resets": resets}


def _new_after(B, E, D, pat):
    """Mod-error text -> new repeats if E continues B after dropping B's oldest D entries; None if it does not."""
    surv = B[D:]
    n = len(surv)
    if n > len(E):
        return None
    for i in range(n):
        if E[i][0] != surv[i][0] or E[i][1] != surv[i][1]:
            return None
        if (E[i][2] != surv[i][2]) if i < n - 1 else (E[i][2] < surv[i][2]):
            return None           # only the newest entry can still gain repeats
    new = {}
    if n and E[n - 1][2] > surv[-1][2] and E[n - 1][0] == "Error" and pat.search(E[n - 1][1]):
        new[E[n - 1][1]] = E[n - 1][2] - surv[-1][2]
    for t, text, rep in E[n:]:
        if t == "Error" and pat.search(text):
            new[text] = new.get(text, 0) + rep
    return new, len(E) - n + (E[n - 1][2] - surv[-1][2] if n else 0)


def new_mod_errors(call, base, extra=()):
    """Error-type lines naming this mod that appeared (or repeated again) since `base`."""
    E = _buffer(call)
    count, resets = _health(call)   # counter AFTER the read: over-counts, never under-counts
    B = base["rows"]
    pat = _pat(extra)
    if resets != base["resets"]:
        _blind("jawa/health counted a Verse.Log reset since the baseline (capResets %r -> %r)" % (base["resets"], resets))
    logged = None if count is None or base["count"] is None else count - base["count"]
    if logged is not None and logged < 0:
        _blind("Verse.Log messageCount fell since the baseline (%d): the log was cleared" % logged)
    if logged is not None and logged > MAXQ:
        _blind("%d messages were logged since the baseline, more than the %d-entry buffer holds: new entries "
               "may have rolled out unseen" % (logged, MAXQ))
    if len(E) < MAXQ:
        dmax = 0                  # the queue drops entries only once it is full
    elif logged is None:
        _blind("the buffer is full and Verse.Log messageCount is unreadable, so a rollover cannot be bounded")
    else:
        dmax = max(0, min(len(B), len(B) + logged - MAXQ))
    fits = {}
    for D in range(dmax + 1):
        got = _new_after(B, E, D, pat)
        if got is None:
            continue
        new, added = got
        if logged is not None and added > logged:
            continue              # more new entries/repeats than messages logged: not this drop count
        fits[D] = new
    if not fits:
        _blind("the log buffer does not continue the baseline at any drop count 0..%d (cleared or rewritten)" % dmax)
    verdicts = {frozenset(v) for v in fits.values()}
    if len(verdicts) > 1:
        _blind("drop counts %s all fit the buffers and disagree about which mod errors are new" % sorted(fits))
    return [t[:300] for t in next(iter(fits.values()))]
