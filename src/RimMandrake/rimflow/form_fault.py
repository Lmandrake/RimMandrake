#!/usr/bin/env python3
"""form_fault.py — the one way a gate answers a fault of form (item RIMMANDRAKE_REPAIR_AT_THE_REFUSAL_NO_STOP_FOR_UNTIED_SHOES).

The ruling: design/RimMandrake/standing_rulings.md §A fault of form is repaired where it is found (owner, 2026-11-20
about 11:50 PM PST: "Any agent doing "something wrong" should be given the chance to fix it and redo it right now
without any delay. Period. No more large consequences for trivialities."). Promises and their tests:
design/specs/2026-11-21-repair-at-the-refusal/boundary.md (selftest_repair_at_refusal.py).

A fault of FORM is in how work is presented (a name, a flag, a missing paste, a missing section, a stale stamp, a file a
tool can make, a format). A fault of SUBSTANCE is in the work (the mod is wrong, the test is wrong, the run died, the
machine or an account failed without a plan). A WAIT ends by itself (a planned drain, a held bridge, his hold on a
game) and counts nothing.

Two routes, in this order:
  repaired(what, how, event=None)   the tool repaired the input itself: one NOTE line, the note on the event, go on (exit 0)
  refusal(what, repair)             only the agent can repair it: the text names the exact repair; the agent does it and
                                    repeats the act at once (BRIEF_LINE teaches every launched agent this)
A program caller (the tick) never sends a refused input again unchanged: it launches one repair run with the refusal
as its brief (maturation_dispatch.form_repair_step).

The fault loop's one principle: only a run that STARTED and DIED is a fault of substance (run_void.system_cause). A
launch that never started was refused before any work began: that is a fault of form, whatever gate said no, and it is
repaired, never counted. The only exception is a wait (maturation_autonomy.wait_refusal: a planned drain, a held
bridge, a stop someone chose), which waits. There is no table of refusal kinds: a machine fault that stops a launch
also stops the repair run's launch, and that repair launcher, refused REPAIR_LAUNCH_MOST times, names the Conductor.
"""
import hashlib
import re
import sys

FORM_HEAD = "REFUSED (form): "
NOTE_HEAD = "NOTE (form, repaired): "
REPAIR_HEAD = "REPAIR: "
BRIEF_LINE = ("- A refusal that names its repair is an instruction: do the repair and repeat the act; never stop or hand "
              "off for it. A fault of form (a name, a flag, a missing paste, a stale stamp, a file a tool can make) is "
              "repaired where it is found and the work goes on "
              "(`design/RimMandrake/standing_rulings.md` §A fault of form is repaired where it is found).\n")


def repaired(what, how, event=None, stream=None):
    """Route 1: the tool repaired the input itself. Prints one NOTE line, appends {what, how} to event["form_notes"]
    (when an event dict is given) and returns the note. Never exits."""
    note = {"what": str(what), "how": str(how)}
    print("%s%s -> %s" % (NOTE_HEAD, what, how), file=stream or sys.stdout)
    if isinstance(event, dict):
        event.setdefault("form_notes", []).append(note)
    return note


def refusal(what, repair):
    """Route 2: the refusal text an agent can act on. A form refusal with no repair is not allowed: ValueError."""
    if not str(repair or "").strip():
        raise ValueError("a form refusal must name its repair (what to run or the text to add): %s" % what)
    return "%s%s\n%s%s" % (FORM_HEAD, what, REPAIR_HEAD, str(repair).strip())


def repair_of(text):
    """-> the REPAIR line's text of a refusal, or None."""
    m = re.search(r"^%s(.+)$" % re.escape(REPAIR_HEAD), str(text or ""), re.M)
    return m.group(1).strip() if m else None


def fault_class(text):
    """-> "wait" for a launch refusal whose cause ends by itself (maturation_autonomy.wait_refusal), else "form"."""
    import maturation_autonomy as AUT
    return "wait" if AUT.wait_refusal(text) else "form"


_NOISE = re.compile(r"\d{4}-\d\d-\d\dT[\d:.]+Z?|\b[0-9a-f]{7,40}\b|\b\d+(\.\d+)?\b|rm-[\w.-]+")


def fingerprint(text):
    """-> a short hash of a refusal with its times, hashes, numbers and unit names taken out: the same refusal on a
    later tick has the same fingerprint."""
    return hashlib.sha256(_NOISE.sub("#", str(text or "")).encode()).hexdigest()[:12]


def what_of(text, room=160):
    """-> the refusal's head for a status line: its first non-empty line after any 'its launch never started: '."""
    t = str(text or "").strip()
    t = re.sub(r"^its launch never started:\s*", "", t)
    first = next((ln.strip() for ln in t.splitlines() if ln.strip()), "")
    return first if len(first) <= room else first[:room - 1] + "…"


# ---- the tick's repair records (state.json mods.<Mod>.form_repairs / fault_repairs / auto_cleared) -----------------

OPEN = ("owed", "running")


def open_repair(s):
    """-> the mod's first open form repair (owed or running), or None."""
    return next((r for r in (s or {}).get("form_repairs") or [] if isinstance(r, dict) and r.get("state") in OPEN), None)


def owe_repair(s, text, where, now, book=None, key=None):
    """Record a form refusal on the mod's state s: one repair is owed for it (one open record per fingerprint).
    -> None, or the cause of ONE fault of substance when the same refusal came back after a finished repair run
    ("the repair of <what> did not hold"); a new repair is owed then too."""
    fp = fingerprint(text)
    reps = s.setdefault("form_repairs", [])
    for r in reps:
        if isinstance(r, dict) and r.get("fp") == fp and r.get("state") in OPEN:
            r["seen"] = int(r.get("seen") or 1) + 1
            return None
    held = next((r for r in reversed(reps) if isinstance(r, dict) and r.get("fp") == fp and r.get("state") == "done"),
                None)
    reps.append({"fp": fp, "what": what_of(text), "text": str(text), "where": where, "book": book, "key": key,
                 "at": now, "state": "owed", "unit": None, "item": None, "seen": 1,
                 **({"after": held.get("unit")} if held else {})})
    if held:
        return "the repair of %s did not hold (repair run %s ended; the same refusal came back): %s" % (
            what_of(text, 100), held.get("unit") or "?", what_of(text))
    return None


def _ended(rec, live=None):
    if not isinstance(rec, dict):
        return None          # could not look: the repair stays as it is
    if rec.get("status") == "finished":
        return True
    if live is not None:
        try:
            return live(rec) == "dead"
        except Exception:    # noqa: BLE001
            return None
    return False


def _killed(rec):
    """-> the Reading of an ended run whose outcome is classed and does not count (failure_class), else None. A run whose
    unit died with its finish never run is KILLED; a record with no result reads as before."""
    import failure_class as FC
    fc = FC.of_run(rec) if rec.get("status") == "finished" else FC.read(FC.KILLED, "its unit died, its finish never ran")
    return fc if fc.classed and not fc.counts else None


def sync_repairs(st, record, now, live=None):
    """Mark each running repair (form and fault) whose run has ended `done`, or `void` when it was killed from outside; a fault repair that ended resets the mod's
    fault count (auto_cleared, read by run_void.faults: the tick's own reset, never a hand `clear`).
    -> [(mod, kind, unit)] ended this call."""
    out = []
    for mod, s in ((st or {}).get("mods") or {}).items():
        if not isinstance(s, dict):
            continue
        for kind in ("form_repairs", "fault_repairs"):
            for r in s.get(kind) or []:
                if not (isinstance(r, dict) and r.get("state") == "running" and r.get("unit")):
                    continue
                rec = record(r["unit"])
                e = _ended(rec, live)
                if e:
                    fc = _killed(rec)
                    if fc:      # a run that died repaired nothing: no repair that did not hold, no reset of the count
                        r.update(state="void", ended_at=now, void="%s (%s)" % (fc.word, fc.why))
                        out.append((mod, kind, r["unit"]))
                        continue
                    r.update(state="done", ended_at=now)
                    out.append((mod, kind, r["unit"]))
                    if kind == "fault_repairs":
                        s.setdefault("auto_cleared", []).append(
                            {"at": now, "why": "the tick's repair run %s on the fault loop ended" % r["unit"]})
    return out


def repair_brief(mod, records, kind="form"):
    """-> the brief of one repair run: the refusal (or the faults) whole, and what to do."""
    head = ("A gate on %s's pipeline path refused work for a fault of form, and the tick never sends a refused input "
            "again unchanged. Repair it where it was found, so the same act passes:" % mod) if kind == "form" else (
            "The fault loop (OPS_MATURATION_SYSTEM_FAULT_LOOP) tripped on %s: faults of substance (runs that died, "
            "machine or account failures) repeated. The evidence:" % mod)
    out = ["# Repair run: %s (%s)" % (mod, kind), "", head, ""]
    for r in records:
        out += ["## %s" % (r.get("where") or r.get("book") or "refusal"), "", "```", str(r.get("text") or r.get("cause")),
                "```", ""]
    out += [
        "Do, in this order:",
        "1. Find the gate that refused (search the refusal text under src/RimMandrake and .claude/hooks) and the "
        "caller that built the input.",
        "2. If the refusal names its repair (a `REPAIR:` line or a command in the text), do it." if kind == "form" else
        "2. Read the dead runs' records (detached_helper.py status --all; the unit names above) and find the cause.",
        "3. Fix the caller or the gate, test first (a selftest red on the parent, green on the fix), so the same act "
        "passes on the next tick. A gate that refuses a fault of form becomes repair-and-continue or names its repair "
        "(src/RimMandrake/rimflow/form_fault.py).",
        "4. Publish with ./publish and explicit paths. Do not stop, kill or disturb any live run; take no bridge.",
        "5. Close your item with the sha. If the fix is unknown or outside your tools, write a `LEFT OPEN:` note "
        "with the evidence; the Conductor reads it.",
        "",
        "The ruling: design/RimMandrake/standing_rulings.md §A fault of form is repaired where it is found.",
    ]
    return "\n".join(out) + "\n"
