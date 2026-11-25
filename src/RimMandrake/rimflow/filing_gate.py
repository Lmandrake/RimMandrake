"""filing_gate.py: a helper run that files a work ticket shows why the run cannot do the work now. No model, no tokens.

Item RIMMANDRAKE_REFUSE_FILING_WITHOUT_EVIDENCE_WHY_NOT_FIX_IT_NOW; page design/specs/2026-11-24-filing-gate/boundary.md;
selftest selftest_filing_gate.py. Why: CLAUDE.md §Touching code has a cost (test 2) says that the run that judges a
finding worth the fix is its fixer, and sets it down only with evidence. On 2026-11-24 three runs wrote up work in place
of doing the work, and no check stood at the door. `at_door` is the check; both doors of the ledger that make work
(`cli._file` and `cli.cmd_spawn`) call it before they write.

A refusal is a path to pass, and it is recorded (`<state>/filing_refusals/<unit>.jsonl`). The run resolves it in one of
three ways: it files again with `--not-now "<class>: <evidence>"` (filed), it does the work and says
`--did-it <sha>` (did), or it says `--not-worth-it "<why>"` (dropped). The Stop hook
`.claude/hooks/filing_refusal_before_stop.py` and the run-end text of `detached_helper.finish` name each refusal that
is not resolved.
"""
import collections
import datetime
import json
import os
import re

Decision = collections.namedtuple("Decision", "ok text record")
Door = collections.namedtuple("Door", "go rc text record err")

# The kinds that hold a debt or a question, not work. Every other kind is work (the ledger to 2026-11-24 holds 61 filings
# of kinds other than bug and task: fix, defect, build, problem, ...), so the list is of what passes, not of what stops.
REMINDER_KINDS = ("owed", "design", "notice", "alarm")
RESOLUTIONS = ("filed", "did", "dropped")
# class -> the evidence that the class asks for (the evidence list of test 2; "it is large" and "my own work would not
# finish" are not on it: a run has no limit of time, and a second run must read again all that the first run read)
CLASSES = collections.OrderedDict((
    ("no-tool", "you lack a tool, an access or a model that the work needs: name it"),
    ("fix-unknown", "the fix is not known: name what you tried"),
    ("owner-act", "the work is one of the owner's five acts, or changes a north-star bar: name the act"),
    ("files-held", "another live run holds the files: name its unit"),
    ("independent", "your verdict must stay independent of the work: name the verdict"),
    ("other-mod", "the work belongs to a mod's own Maturation Pipeline run: name the mod folder"),
))
MIN_EVIDENCE = 12  # danger: a one-word reason passes as evidence (page, LIMITS)
_UNIT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.@:-]{5,95}")
_WORD = re.compile(r"[A-Za-z][A-Za-z0-9_]+")


def refusal(why):
    lines = ["REFUSED: %s" % why,
             "Do the work now, in this run, test first: you hold its context, and a later run must read it all again.",
             'If this run cannot do the work, file again with --not-now "<class>: <evidence>". The classes:']
    lines += ["  %-12s %s" % (c, what) for c, what in CLASSES.items()]
    lines.append('"It is large" and "my own work would not finish" are not classes.')
    return "\n".join(lines)


def _evidence_left(cls, evidence):
    """The evidence with the class name's own words removed: what is left must still say something."""
    words = set(cls.split("-")) | {cls}
    return " ".join(w for w in re.split(r"\s+", evidence) if w.strip(".,;:").lower() not in words)


def decide(kind, unit, owner, program, not_now, live_units, mod_exists):
    """-> Decision(ok, text, record). kind: the ticket's kind (None reads as task). unit: RM_ROLE_UNIT of the filing run,
    empty in a window. owner: the filing carries --owner-said or --by-card (--per-ruling alone is not the owner). program: RM_FILING_PROGRAM. not_now: the
    flag's text or None. live_units: the units that are live, or None when they cannot be read. mod_exists(name) -> bool."""
    if program:
        return Decision(True, "", {"program": program})
    if owner or not (unit or "").strip() or (kind or "task").strip().lower() in REMINDER_KINDS:
        return Decision(True, "", None)
    text = (not_now or "").strip()
    if not text:
        return Decision(False, refusal("a helper run files a %s ticket with no evidence why this run cannot do the work now."
                                       % (kind or "task")), None)
    cls, sep, evidence = text.partition(":")
    cls, evidence = cls.strip().lower(), evidence.strip()
    if not sep or cls not in CLASSES:
        return Decision(False, refusal("--not-now %r names no class of the list." % text[:80]), None)
    if len(evidence) < MIN_EVIDENCE or len(_evidence_left(cls, evidence)) < MIN_EVIDENCE:
        return Decision(False, refusal("--not-now gives the class %s with no evidence (%s)." % (cls, CLASSES[cls])), None)
    record = {"class": cls, "evidence": evidence}
    if cls == "files-held":
        if live_units is None:
            record["checked"] = "could not look: the live runs could not be read"
        else:
            named = [u for u in _UNIT.findall(evidence) if u in live_units and u != unit]
            if not named:
                return Decision(False, refusal("files-held names no other run that is live now "
                                               "(`detached_helper.py status` lists the live runs)."), None)
            record["checked"] = "live: " + named[0]
    elif cls == "other-mod":
        named = [w for w in _WORD.findall(evidence) if mod_exists(w)]
        if not named:
            return Decision(False, refusal("other-mod names no mod folder that exists "
                                           "(design/concepts/<Mod> or src/RimMandrake/<Mod>)."), None)
        record["checked"] = "mod: " + named[0]
    return Decision(True, "", record)


def facts(repo):
    """-> (live_units or None, mod_exists) read from this machine, for the door."""
    import os
    try:
        import detached_helper as DH
        live = {r["unit"] for r in DH.all_records() if DH.live_status(r) in ("launching", "running")}
    except Exception:  # noqa: BLE001 - could not look: the door files the ticket and says so
        live = None

    def mod_exists(name):
        return any(os.path.isdir(os.path.join(repo, d, name)) for d in ("design/concepts", "src/RimMandrake"))
    return live, mod_exists


# ---- the record of refusals, and their resolution ------------------------------------------------------------------

def _now(now=None):
    return now or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def refusals_path(unit, state_dir):
    return os.path.join(state_dir, "filing_refusals", re.sub(r"[^A-Za-z0-9_.@-]", "_", unit or "nounit") + ".jsonl")


def _append(unit, state_dir, row):
    """-> None, or the why when the line could not be written."""
    path = refusals_path(unit, state_dir)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    except OSError as e:
        return "%s: %s" % (type(e).__name__, e)
    return None


def record_refusal(unit, state_dir, iid, title, kind, why, door="file", now=None):
    return _append(unit, state_dir, {"at": _now(now), "unit": unit, "id": iid, "title": title or "", "kind": kind or "task",
                                     "why": why, "door": door})


def record_resolution(unit, state_dir, how, iid, now=None, **extra):
    assert how in RESOLUTIONS, how
    row = dict(extra, resolved=how, id=iid, at=_now(now))
    return _append(unit, state_dir, row)


def read_refusals(unit, state_dir):
    """-> (the refusals not resolved, in order, the last refusal of an id counting; None when the file cannot be read),
    why. No file: no refusal. A line that is not JSON is a file that cannot be read: never read as empty."""
    path = refusals_path(unit, state_dir)
    if not os.path.exists(path):
        return [], ""
    open_ = collections.OrderedDict()
    try:
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict) or not row.get("id"):
                    return None, "%s line %d is no refusal and no resolution" % (path, n)
                if row.get("resolved"):
                    open_.pop(row["id"], None)
                else:
                    open_.pop(row["id"], None)
                    open_[row["id"]] = row
    except (OSError, ValueError) as e:
        return None, "%s: %s: %s" % (path, type(e).__name__, str(e)[:200])
    return list(open_.values()), ""


def unresolved(unit, state_dir):
    """-> the refusals not resolved, or None when the record cannot be read."""
    return read_refusals(unit, state_dir)[0]


def run_end_lines(unit, state_dir):
    """The lines for the run-end text that the Conductor's wake shows: one per refusal not resolved."""
    left, why = read_refusals(unit, state_dir)
    if left is None:
        return ["filing refusals: could not look (%s)" % why]
    return ["REFUSED FILING NOT RESOLVED: %s: %s" % (r["id"], r.get("title") or "") for r in left]


HOW_TO_RESOLVE = ('do the work and say --did-it <sha> (a commit on origin/main); or file again with --not-now '
                  '"<class>: <evidence>"; or say --not-worth-it "<why>"')


# ---- the door ------------------------------------------------------------------------------------------------------

def judge_did(sha, look):
    """look: {"looked": bool, "why": str, "exists": bool, "published": bool, "ledger_only": bool, "sha": full}.
    -> (ok, text, record)."""
    if not look.get("looked"):
        return True, "", {"sha": sha, "checked": "could not look: %s" % (look.get("why") or "git could not be read")}
    if not look.get("exists"):
        return False, "REFUSED: --did-it %s: git says that commit does not exist here." % sha, None
    if not look.get("published"):
        return False, ("REFUSED: --did-it %s is not on origin/main. Publish it first (./publish), then say --did-it "
                       "again." % sha), None
    if look.get("ledger_only"):
        return False, ("REFUSED: --did-it %s touches nothing but the ledger: that is a record of work, not the "
                       "work." % sha), None
    return True, "", {"sha": look.get("sha") or sha, "checked": "on origin/main"}


def at_door(door, iid, title, kind, unit, owner, program, not_now, did_it, not_worth_it, state_dir, facts_fn, look_sha,
            now=None):
    """The one gate of both doors (door "file" or "spawn"). -> Door(go, rc, text, record, err).
    go: write the event (record: its `not_now` field, or None). Not go: print text, exit rc (0 when the run resolved the
    ticket in another way: nothing is filed). err: a line for stderr (a record that could not be written)."""
    unit = (unit or "").strip()
    ways = [f for f, v in (("--not-now", not_now), ("--did-it", did_it), ("--not-worth-it", not_worth_it))
            if v is not None]
    if len(ways) > 1:
        return Door(False, 2, "REFUSED: %s are three ways; give one." % " and ".join(ways), None, "")
    if did_it is not None:
        ok, text, rec = judge_did(did_it.strip(), look_sha(did_it.strip()))
        if not ok:
            return Door(False, 6, text, None, "")
        err = record_resolution(unit, state_dir, "did", iid, now=now, **rec) if unit else None
        return Door(False, 0, "nothing filed: %s was done in this run at %s" % (iid, rec["sha"]) +
                    ("" if "could not look" not in rec["checked"] else " (%s)" % rec["checked"]), rec,
                    _err(err))
    if not_worth_it is not None:
        why = not_worth_it.strip()
        if len(why) < MIN_EVIDENCE:
            return Door(False, 6, "REFUSED: --not-worth-it needs a why of %d characters or more." % MIN_EVIDENCE,
                        None, "")
        err = record_resolution(unit, state_dir, "dropped", iid, now=now, why=why) if unit else None
        return Door(False, 0, "nothing filed: %s dropped as not worth the touch: %s" % (iid, why), {"why": why},
                    _err(err))
    live, mod_exists = facts_fn() if unit and not owner and not program else (None, lambda m: False)
    d = decide(kind, unit, owner, program, not_now, live, mod_exists)
    if not d.ok:
        why = d.text.splitlines()[0][len("REFUSED: "):]
        err = record_refusal(unit, state_dir, iid, title, kind, why, door=door, now=now)
        return Door(False, 6, d.text + "\nThe refusal is recorded; this run must resolve it before it ends: " +
                    HOW_TO_RESOLVE + ".", None, _err(err))
    return Door(True, 0, "", d.record, "")


def _err(why):
    return "" if not why else "filing_gate: the record could not be written (%s); the door's answer stands" % why


def after_filed(unit, state_dir, iid, record, now=None):
    """The door wrote the event: a refusal of this id is resolved as filed. -> the stderr line or ""."""
    unit = (unit or "").strip()
    if not unit:
        return ""
    left = unresolved(unit, state_dir)
    if not left or iid not in {r["id"] for r in left}:
        return ""
    return _err(record_resolution(unit, state_dir, "filed", iid, now=now, **({"not_now": record} if record else {})))


def state_dir():
    """The dispatcher's state folder (doorbell.state_dir: RM_DISPATCHER_STATE redirects it)."""
    import doorbell
    return doorbell.state_dir()


def filing_unit(env_unit, state, under_test, real_state, run_unit=None):
    """-> the unit the gate reads. A test process (test_process.under_test) files as a window when it did not bring its
    own state folder, or when its unit is the one its nearest test program was launched with (`run_unit`): that is the
    unit of the run the test runs within (a selftest run inside a helper inherits the helper's RM_ROLE_UNIT), not the
    test's own. A test never writes the real state (test_process.py: a test that wants an effect brings its own target),
    and a test that wants the gate sets a unit of its own. `run_unit` None: the launch could not be read."""
    unit = (env_unit or "").strip()
    if under_test and os.path.realpath(state) == os.path.realpath(real_state):
        return ""
    if under_test and run_unit is not None and unit == run_unit.strip():
        return ""
    return unit


def _proc_argv(pid):
    with open("/proc/%d/cmdline" % pid, "rb") as f:
        return [x.decode("utf-8", "replace") for x in f.read().split(b"\0") if x]


def run_unit(name="RM_ROLE_UNIT"):
    """-> the `name` that the nearest test program in this process's line (itself or an ancestor: a Python run of
    selftest*.py or run_selftests.py) was launched with ("" when it had none), or None when there is no such program or
    /proc cannot be read. /proc/<pid>/environ is the launch env, untouched by the program's own os.environ edits."""
    import test_process
    pid = os.getpid()
    try:
        while pid > 1:
            if test_process._test_program(_proc_argv(pid)):
                with open("/proc/%d/environ" % pid, "rb") as f:
                    env = dict(x.decode("utf-8", "replace").partition("=")[::2] for x in f.read().split(b"\0") if x)
                return (env.get(name) or "").strip()
            with open("/proc/%d/stat" % pid) as f:
                pid = int(f.read().rsplit(")", 1)[1].split()[1])
    except (OSError, ValueError, IndexError):
        return None
    return None


def door_unit():
    """filing_unit, read from this process."""
    import doorbell
    import test_process
    under = test_process.under_test()
    return filing_unit(os.environ.get("RM_ROLE_UNIT", ""), doorbell.state_dir(), under, doorbell.DEFAULT_STATE,
                       run_unit() if under else None)
