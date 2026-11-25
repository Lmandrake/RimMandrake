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

0.4.0 (RIMMANDRAKE_TIGHTEN_SET_DOWN_CLASSES_ANY_TWELVE_LETTERS_PASS): on 2026-11-25 the Conductor read 25 set-downs and
found about 16 with no sincere attempt, so `decide` now checks what a program can decide from the words (three theories
for fix-unknown, a choice between known fixes, a Conductor call named as owner-act, a held game, a workaround, a run that
says it did not look), and `at_door` then asks the set-down judge (set_down_judge.py, one bare model call that reads the
filing run's transcript). The judge binds only when its calibration row reads CALIBRATED; until then it is a shadow. The
refusal states one requirement and prints no menu (owner, 2026-11-25). `at_defer` is the same check at the other doors of
a defer: `rimflow wait`, `rimflow block`, and a LEFT OPEN or NEXT note that names the Conductor or the owner.
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
# class -> the requirement of a valid set-down of that class (the evidence list of test 2; "it is large" and "my own
# work would not finish" are not on it: a run has no limit of time, and a second run must read again all that the first
# run read). A refusal prints the one requirement that the set-down tried to meet, never this list (owner, 2026-11-25:
# "NO it should not be offering a menu of possibilities. It should instead state the Requirements of a valid ticket with
# examples only for clarification."). `rimflow file --help` names the classes.
FIXER = ("You are the fixer. When you find a fault, fix it in this run, test first. A later run knows less than you do "
         "now. Hand it on only with evidence.")
GAME_WAIT = 'python3 src/RimMandrake/rimflow/game_lock.py run <game> --for "<what>" -- <command>'
DELEGATED = ('--per-ruling RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME --why "delegated: evidence-for-ask: '
             '<the call and why>"')
FIVE_ACTS = ("a live flight test of a flyer, a replacement of art that he kept, the pass at his walk, a money spend, or "
             "publication outside the private repos")
REQUIREMENTS = collections.OrderedDict((
    ("no-tool", "the run lacks a tool or an access that the work needs, and the set-down names it. A game that is held "
                "now is not a missing tool: wait for it with `%s`. A missing bridge function is yours to build, test "
                "first." % GAME_WAIT),
    ("fix-unknown", "the cause is still unknown after three theories. Name three different theories of the cause, and "
                    "for each the experiment that tested it and its reading. Before the third, ask GPT for new theories "
                    "(`python3 src/RimMandrake/Utils/gpt_consult.py`) and say so. Example: \"theory 1: the cache is "
                    "stale; experiment: cleared it and ran the scene again; reading: the same failure. theory 2: ... "
                    "theory 3 (from gpt_consult.py): ...\". A choice between known fixes is not an unknown cause."),
    ("owner-act", "the work is one of the owner's five acts (%s), or it makes a bar looser; the set-down names that act. "
                  "A call of the Conductor is not one of the five acts: when you know the answers, the choice is "
                  "yours. Take the one you recommend and log it with %s." % (FIVE_ACTS, DELEGATED)),
    ("files-held", "another live run holds the files, and the set-down names the unit of that run "
                   "(`detached_helper.py status` lists the live runs)."),
    ("independent", "the verdict of this run must stay independent of the work, and the set-down names that verdict."),
    ("other-mod", "the work belongs to another mod, not to the mod of this run, and the set-down names that mod's "
                  "folder."),
))
CLASSES = REQUIREMENTS   # the class names (`--help`, the count by class); the text of each is its requirement
NO_CLASS = ('A valid set-down shows, with evidence that a reader can check, why this run cannot do the work. For example: '
            'the cause is still unknown after three theories, each with its experiment and reading. The form is '
            '--not-now "<class>: <evidence>"; `rimflow file --help` names the classes.')
# RIMMANDRAKE_REFUSE_OWN_MOD_HANDOFF_DRIVER_RENAMED_NOTHING: on 2026-11-25 Explosive Knockback's visit-1 driver filed the
# rename of 12 of its own defNames as other-mod. A fault of the run's own mod is fixed in the sitting (CLAUDE.md
# §Touching code has a cost, "Fix a fault in the sitting").
OWN_MOD_REFUSAL = ("other-mod names %s, the mod of this run. Fix the fault in this sitting, red test first: a test red "
                   "on the parent build and green on the fix, then the fix, then run again the checks it touches. If "
                   "the cause is unknown after a sincere attempt, file with --not-now \"fix-unknown: <what you tried, "
                   "each thing>\".")
MIN_EVIDENCE = 12  # danger: a one-word reason passes as evidence (page, LIMITS)
_UNIT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.@:-]{5,95}")
_WORD = re.compile(r"[A-Za-z][A-Za-z0-9_]+")


def refusal(why, cls=None, missing="", again=None):
    """The one home of the refusal's wording: FIXER first, then the one requirement that the set-down tried to meet and
    what is missing (or, with no class, what a valid set-down shows). Never the list of classes."""
    lines = ["REFUSED: %s" % why, FIXER]
    if cls in REQUIREMENTS:
        lines.append("A set-down of class %s is valid only when %s" % (cls, REQUIREMENTS[cls]))
        if missing:
            lines.append("Missing: %s" % missing)
        lines.append(again or 'If the requirement holds, file again with --not-now "%s: <evidence>".' % cls)
    else:
        lines.append(NO_CLASS)
    return "\n".join(lines)


# ---- what a program can decide from the words (0.4.0; each pattern is from one of the 25 real set-downs of
# 2026-11-25, design/specs/2026-11-24-filing-gate/set_down_cases.json) -------------------------------------------------
_THEORY = re.compile(r"\btheory\s*([1-9])\b", re.I)
_EXPERIMENT = re.compile(r"\b(experiment|tested|test|tried|ran|run|probe|probed|measured)\b", re.I)
_READING = re.compile(r"\b(reading|read|result|saw|seen|showed|shows|got|printed|gave)\b", re.I)
_GPT = re.compile(r"\b(gpt|gpt_consult(\.py)?|chatgpt|codex)\b", re.I)
_CHOICE = re.compile(r"\btwo (known |possible |open )?(fixes|ways|options|routes|answers|directions)\b"
                     r"|\b(design|routing|scope) (call|choice)\b|\bwhich (one|way|fix|route) is right\b"
                     r"|\(a\)[^()]{3,}\(b\)", re.I)
_CONDUCTOR = re.compile(r"\bconductor\b", re.I)
_OWNER = re.compile(r"\b(the owner|owner's|his (decision|ruling|pick|call|word|look)|mandrake|ask him)\b", re.I)
_ACT = re.compile(r"\b(fl(y|ies|ying|ight|yer|yers)|art (that )?he kept|kept art|his walk|walk|money|spend|purchase|"
                  r"buy|publish|publication|public|loos(e|er|en|ening)|relax(es|ing)?|weaken|lower(ing)? (a|the) bar)\b",
                  re.I)
_HOLD = re.compile(r"\b(hold|holds|held|pause|paused|stop order|lift|lifts)\b", re.I)
_GAMES = r"(?:game|games|archbig|archsmall|steve1|steve2)"
_HELD_GAME = re.compile(r"\bno (free|idle) %s\b|\b%s\b[^.;]{0,60}?\b(held|busy|taken|in use)\b"
                        r"|\b(held|busy|taken)\b[^.;]{0,20}?\b%s\b" % (_GAMES, _GAMES, _GAMES), re.I)
_WORKAROUND = re.compile(r"\bwork(ed|ing)?[ -]?around\b|\bworkaround\b", re.I)
_NOT_LOOKED = re.compile(r"\b(I|we|this run|the run|the filer|this helper|this session|operations|it)\s+(did not|didn't|"
                         r"has not|hasn't|have not|haven't|never)\s+(read|look(ed)?|open(ed)?|tr(y|ied)|check(ed)?)\b"
                         r"|\btried (neither|nothing|none)\b", re.I)


def theories(evidence):
    """-> (the distinct theories named, each a (number, text) with an experiment and a reading; why the form fails or
    "" when it holds)."""
    marks = list(_THEORY.finditer(evidence))
    parts = [(m.group(1), evidence[m.end():(marks[i + 1].start() if i + 1 < len(marks) else len(evidence))])
             for i, m in enumerate(marks)]
    if len({n for n, _ in parts}) < 3:
        return parts, "it names %d theor%s; three are needed (`theory 1:`, `theory 2:`, `theory 3:`)" % (
            len({n for n, _ in parts}), "y" if len({n for n, _ in parts}) == 1 else "ies")
    for n, text in parts:
        head = re.split(r"\b(experiment|tested|test|tried|ran|probe)\b", text, 1, re.I)[0]
        if not _EXPERIMENT.search(text[len(head):] or "") or not _READING.search(text):
            return parts, "theory %s names no experiment and reading" % n
    heads = {re.sub(r"\W+", " ", re.split(r"[;,]|\bexperiment\b", t, 1, re.I)[0]).strip().lower() for _, t in parts}
    if len(heads) < 3:
        return parts, "the theories are not different: each names the same cause"
    if not _GPT.search(evidence):
        return parts, "it names no GPT consult before the third theory (`python3 src/RimMandrake/Utils/gpt_consult.py`)"
    return parts, ""


def words_check(cls, evidence):
    """-> None when the words pass the program, or (why, missing) of the refusal. The checks that a program can decide
    from the words alone; the judge reads the rest."""
    if _WORKAROUND.search(evidence):
        return ("the set-down says that the run worked around the fault. A hand workaround with no permanent fix is not "
                "allowed: make the permanent fix in this run, test first."), ""
    if cls in ("fix-unknown", "no-tool") and _CHOICE.search(evidence):
        return ("the set-down offers a choice between known fixes (%r). The choice is yours: take the fix that you "
                "recommend, do it in this run, test first, and log the choice as delegated with %s."
                % (_CHOICE.search(evidence).group(0), DELEGATED)), ""
    if _NOT_LOOKED.search(evidence):
        return ("the set-down says that the run did not read, try or check what it sets down (%r). Do that first: "
                "it is the attempt." % _NOT_LOOKED.search(evidence).group(0)), ""
    if cls != "files-held" and _HELD_GAME.search(evidence):
        return ("a game that is held now is not a reason: a run has no limit of time. Wait for the game with `%s`, "
                "then do the work." % GAME_WAIT), ""
    if cls == "fix-unknown":
        _, why = theories(evidence)
        if why:
            return "fix-unknown: %s." % why, why
    if cls == "owner-act" and _CONDUCTOR.search(evidence) and not _ACT.search(evidence):
        return ("owner-act names a call of the Conductor and none of the owner's five acts (%s) or a looser bar."
                % FIVE_ACTS), "the act: one of the five, or the bar that would be looser"
    return None


def _evidence_left(cls, evidence):
    """The evidence with the class name's own words removed: what is left must still say something."""
    words = set(cls.split("-")) | {cls}
    return " ".join(w for w in re.split(r"\s+", evidence) if w.strip(".,;:").lower() not in words)


def decide(kind, unit, owner, program, not_now, live_units, mod_exists, own_mod=None):
    """-> Decision(ok, text, record). kind: the ticket's kind (None reads as task). unit: RM_ROLE_UNIT of the filing run,
    empty in a window. owner: the filing carries --owner-said or --by-card (--per-ruling alone is not the owner). program: RM_FILING_PROGRAM. not_now: the
    flag's text or None. live_units: the units that are live, or None when they cannot be read. mod_exists(name) -> bool.
    own_mod: the mod of the filing run (own_mod_of), or None when it cannot be read: other-mod then is not refused on it."""
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
        return Decision(False, refusal("--not-now gives the class %s with no evidence." % cls, cls), None)
    bad = words_check(cls, evidence)
    if bad:
        return Decision(False, refusal(bad[0], cls, bad[1]), None)
    record = {"class": cls, "evidence": evidence}
    if cls == "files-held":
        if live_units is None:
            record["checked"] = "could not look: the live runs could not be read"
        else:
            named = [u for u in _UNIT.findall(evidence) if u in live_units and u != unit]
            if not named:
                return Decision(False, refusal("files-held names no other run that is live now.", cls), None)
            record["checked"] = "live: " + named[0]
    elif cls == "other-mod":
        named = [w for w in _WORD.findall(evidence) if mod_exists(w)]
        if not named:
            return Decision(False, refusal("other-mod names no mod folder that exists "
                                           "(design/concepts/<Mod> or src/RimMandrake/<Mod>).", cls), None)
        own = (own_mod or "").strip().lower()
        others = [w for w in named if w.lower() != own] if own else named
        if not others:
            return Decision(False, refusal(OWN_MOD_REFUSAL % named[0], cls), None)
        record["checked"] = "mod: " + others[0]
        if not own:
            record["own_mod"] = "could not look: the mod of this run could not be read"
    return Decision(True, "", record)


def own_mod_of(unit, read_record=None):
    """-> a probe_result answer: value(the mod of the run `unit`, RM_CONTROL_MOD in its launch record's env;
    detached_helper.py, set by every maturation and Dispatch launch, maturation.launch_mod), empty() when the record names
    no mod (absent, blank or "none"), or could_not_look(cause) when there is no record or it cannot be read."""
    import probe_result as PR
    try:
        if read_record is None:
            import detached_helper as DH
            read_record = DH.read_record
        rec = read_record(unit)
    except Exception as e:  # noqa: BLE001 - could not look: the gate does not refuse on it, and says so
        return PR.could_not_look("the launch record of %s: %s: %s" % (unit, type(e).__name__, e))
    if not isinstance(rec, dict):
        return PR.could_not_look("no launch record of %s" % unit)
    env = rec.get("env")
    mod = env.get("RM_CONTROL_MOD") if isinstance(env, dict) else None
    mod = mod.strip() if isinstance(mod, str) else ""
    return PR.value(mod) if mod and mod.lower() != "none" else PR.empty()


def own_mod_read(answer):
    """-> (the mod or None, why it is None: "" when a mod was read) from own_mod_of's answer (None: not read at all)."""
    if answer is None:
        return None, "not read"
    if answer.kind == "value":
        return answer.value, ""
    return None, ("its launch record names no mod (no RM_CONTROL_MOD)" if answer.kind == "empty" else
                  "could not look: %s" % answer.cause)


def facts(repo, unit=None):
    """-> (live_units or None, mod_exists, the run's own mod or None) read from this machine, for the door."""
    try:
        import detached_helper as DH
        live = {r["unit"] for r in DH.all_records() if DH.live_status(r) in ("launching", "running")}
    except Exception:  # noqa: BLE001 - could not look: the door files the ticket and says so
        live = None

    def mod_exists(name):
        return any(os.path.isdir(os.path.join(repo, d, name)) for d in ("design/concepts", "src/RimMandrake"))
    return live, mod_exists, (own_mod_of(unit) if unit else None)     # facts_fn's third: an answer, or a mod (tests)


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
        return None, "%s: %s: %s" % (path, type(e).__name__, str(e))
    return list(open_.values()), ""


def refusals_of(unit, state_dir, iid):
    """-> every refusal row of `iid` in this unit's record, oldest first ([] when the unit has no record): what each
    earlier refusal asked for, which the set-down judge reads. Raises OSError when the record cannot be read (could not
    look is never an empty record)."""
    out = []
    if not os.path.exists(refusals_path(unit, state_dir)):
        return out
    with open(refusals_path(unit, state_dir), encoding="utf-8") as f:
        for line in f:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if isinstance(row, dict) and row.get("id") == iid and not row.get("resolved"):
                out.append(row)
    return out


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
            now=None, judge_fn=None, binds=None):
    """The one gate of both doors (door "file" or "spawn"). -> Door(go, rc, text, record, err).
    go: write the event (record: its `not_now` field, or None). Not go: print text, exit rc (0 when the run resolved the
    ticket in another way: nothing is filed). err: a line for stderr (a record that could not be written).
    judge_fn(setdown, earlier) -> the set-down judge's verdict (set_down_judge.door_judge), asked only of a set-down
    that the program passed; binds() -> True when the judge's calibration row reads CALIBRATED."""
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
    got = tuple(facts_fn()) if unit and not owner and not program else (None, lambda m: False)
    live, mod_exists, own = (got + (None,))[:3]
    own, own_why = (own, "") if isinstance(own, str) else own_mod_read(own)
    d = decide(kind, unit, owner, program, not_now, live, mod_exists, own_mod=own)
    if not d.ok:
        why = d.text.splitlines()[0][len("REFUSED: "):]
        err = record_refusal(unit, state_dir, iid, title, kind, why, door=door, now=now)
        return Door(False, 6, d.text + "\nThe refusal is recorded; this run must resolve it before it ends: " +
                    HOW_TO_RESOLVE + ".", None, _err(err))
    note = ("filing_gate: note: could not read the mod of run %s (%s), so other-mod was not checked against it"
            % (unit, own_why or "not read")) if (d.record or {}).get("own_mod") else ""
    if judge_fn is not None and d.record and d.record.get("class"):
        sd = {"door": door, "id": iid, "title": title or "", "kind": kind or "task", "class": d.record["class"],
              "evidence": d.record["evidence"]}
        stop = _judged(sd, unit, state_dir, judge_fn, binds, d.record, now)
        if stop:
            err = record_refusal(unit, state_dir, iid, title, kind, stop.splitlines()[0][len("REFUSED: "):], door=door,
                                 now=now)
            return Door(False, 6, stop + "\nThe refusal is recorded; this run must resolve it before it ends: " +
                        HOW_TO_RESOLVE + ".", None, _err(err))
    return Door(True, 0, "", d.record, note)


def judge_log_path(unit, state_dir):
    return os.path.join(state_dir, "set_down_judge", re.sub(r"[^A-Za-z0-9_.@-]", "_", unit or "nounit") + ".jsonl")


def _judged(sd, unit, state_dir, judge_fn, binds, record, now=None):
    """Ask the judge; put its verdict on the record (`judge`) and in the judge log. -> the refusal text when a binding
    judge refused, else None. A judge that raises is a judge that could not answer: the set-down passes."""
    try:
        earlier = refusals_of(unit, state_dir, sd["id"])
    except OSError as e:
        earlier = [{"at": "?", "why": "could not look: the record of earlier refusals of this run cannot be read (%s)" % e}]
    try:
        res = judge_fn(sd, earlier)
        v = dict(res) if isinstance(res, dict) else {"verdict": "could not judge",
                                                      "why": "the judge returned no verdict (%r)" % (res,)}
    except Exception as e:  # noqa: BLE001 - a dead judge never stops filing (page, a-judge-that-cannot-answer...)
        v = {"verdict": "could not judge", "why": "%s: %s" % (type(e).__name__, str(e)[:300])}
    if v.get("verdict") not in ("PASS", "REFUSED"):
        v["verdict"] = "could not judge"
        v.setdefault("why", "no verdict")
    try:
        bind = bool(binds()) if binds else False
    except Exception:  # noqa: BLE001 - a calibration that cannot be read binds nothing
        bind = False
    v["binds"] = bind
    record["judge"] = {k: v[k] for k in ("verdict", "binds", "requirement", "missing", "next_act", "why") if k in v}
    path = judge_log_path(unit, state_dir)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(dict(v, at=_now(now), unit=unit, id=sd["id"], door=sd["door"], cls=sd["class"],
                                    evidence=sd["evidence"]), sort_keys=True) + "\n")
    except OSError:
        pass        # the log is a record of the shadow; the verdict on the event stands
    if bind and v["verdict"] == "REFUSED":
        return refusal("the set-down judge: %s" % v.get("missing", ""), sd["class"],
                       "%s Next: %s" % (v.get("missing", ""), v.get("next_act", "")))
    return None


# ---- the other doors of a defer: wait, block, a LEFT OPEN or NEXT note -------------------------------------------
_DATED = re.compile(r"\b(reset|resets|timer|\.timer)\b", re.I)
_DEFER_NOTE = re.compile(r"^\s*LEFT OPEN:|\bNEXT:")   # the footer's words, upper case: a PROGRESS "next:" is no defer


def defer_check(door, text, unit, live_units):
    """-> (None, record) when a defer's words pass the program, or (refusal text, None). Only the words: the doors that
    a defer can use besides `file` (`wait`, `block`, a note) carry no class, so the reason is read as the set-down."""
    text = (text or "").strip()
    if door == "note" and not (_DEFER_NOTE.search(text) and (_CONDUCTOR.search(text) or _OWNER.search(text))):
        return None, None                       # a note that defers to nobody is no set-down
    rec = {"door": door, "reason": text}
    named = [u for u in _UNIT.findall(text) if live_units and u in live_units and u != unit]
    if named:
        rec["checked"] = "live: " + named[0]
        return None, rec
    if door in ("wait", "block") and _DATED.search(text):
        rec["checked"] = "dated: " + _DATED.search(text).group(0)
        return None, rec
    cls = "no-tool"     # the words checks of a set-down with no class: held game, workaround, did not look, choice
    bad = words_check(cls, text)
    if bad:
        return refusal("%s: %s" % (door, bad[0])), None
    if (_CONDUCTOR.search(text) or _OWNER.search(text)) and not (_ACT.search(text) or _HOLD.search(text)):
        return refusal("%s names the Conductor or the owner and none of the owner's five acts (%s), a looser bar or a "
                       "hold to lift." % (door, FIVE_ACTS), "owner-act",
                       "the act that is his, or the hold, or the dated event (a reset, a timer, a live run)",
                       again="If the requirement holds, do the %s again with a reason that names it." % door), None
    return None, rec


def at_defer(door, iid, text, unit, owner, program, state_dir, live_units, judge_fn=None, binds=None, now=None):
    """The gate of the other doors of a defer (door "wait", "block" or "note"). -> Door(go, rc, text, record, err).
    The owner, the Conductor window (no unit) and a program are never refused."""
    unit = (unit or "").strip()
    if owner or program or not unit:
        return Door(True, 0, "", None, "")
    stop, rec = defer_check(door, text, unit, live_units)
    if stop:
        err = record_refusal(unit, state_dir, iid, (text or "")[:120], door, stop.splitlines()[0][len("REFUSED: "):],
                             door=door, now=now)
        return Door(False, 6, stop + "\nThe refusal is recorded; this run must resolve it before it ends: " +
                    HOW_TO_RESOLVE + ", or do the act again with a reason that meets the requirement.", None, _err(err))
    if rec is not None and judge_fn is not None and not rec.get("checked"):
        sd = {"door": door, "id": iid, "title": "", "kind": door, "class": door, "evidence": rec["reason"]}
        stop = _judged(sd, unit, state_dir, judge_fn, binds, rec, now)
        if stop:
            err = record_refusal(unit, state_dir, iid, (text or "")[:120], door,
                                 stop.splitlines()[0][len("REFUSED: "):], door=door, now=now)
            return Door(False, 6, stop + "\nThe refusal is recorded; this run must resolve it before it ends: " +
                        HOW_TO_RESOLVE + ".", None, _err(err))
    if rec is not None:
        after_filed(unit, state_dir, iid, rec, now=now)
    return Door(True, 0, "", rec, "")


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
