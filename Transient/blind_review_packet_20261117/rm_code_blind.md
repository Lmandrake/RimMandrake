# The code the changes would touch (verbatim excerpts)


## `src/RimMandrake/rimflow/model.py:510-525` — the finding verb's schema

```python
    # criterion passes. `criteria` is the level-tagged manifest, [{"id","level","text"}];
    # the non-L0 ones are what is still OWED, and `needs` is derived from the cheapest of
    # them IN THIS SAME EVENT (review §2: never two separately forgettable writes).
    # Enters `built`, or `done` when nothing is owed. Any seat, like `close`.
    # ⚠️ A reader older than step 2 refuses the unknown verb into `world.errors`: the item
    # keeps its previous state and needs there.
    "implemented": {"who": "any", "req": ("sha",), "opt": ("ref", "criteria", "needs", "live")},
    "finding":   {"who": "any",   "req": ("from", "type", "severity", "name"), "opt": ()},
    # ⚠️ `spawn` carries no `id`. Its cause is `from` — a finding name, a run name, or
    # an item id — and its product is `name`. Requiring an `id` too forced the caller to
    # nominate some existing HOST item, which is not what §4 describes
    # (`spawn --from BLACKSTAR_SPAWNS_VESSELLESS_1 --for BUILD --name …`) and made the
    # documented command impossible. Found 2026-08-20 by the renderer, which tried it.
    "spawn":     {"who": "any",   "req": ("from", "for", "name"),
                  "opt": ("kind", "needs", "this_deployment", "spec", "title")},
    # ⚠️ `reason` moved from `req` to `opt` on these three — owner's ruling, 2026-08-22.
```

## `src/RimMandrake/rimflow/model.py:2758-2770` — _apply: what a finding event actually stores

```python
        elif cid and ev["result"] == "pass":
            _criterion_passed(item, cid, level, run, ev)
    elif verb == "implemented":
        _apply_implemented(ev, item)
    elif verb == "finding":
        world.findings[ev["name"]] = {"from": ev["from"], "type": ev["type"],
                                      "severity": ev["severity"], "at": ev["ts"]}
        item.findings.append(ev["name"])
    elif verb == "retarget":
        item.target = ev["to"]
    elif verb == "needs":
        item.needs = ev["to"]
    elif verb == "reassign":
```

## `src/RimMandrake/rimflow/cli.py:3185-3200` — cmd_finding

```python
def cmd_finding(args, seat):
    _, w = load()
    iid = args.id or _item_of(args.from_, w)
    if not iid:
        die("cannot tell which item this finding hangs on. Pass --id, or make --from a "
            "run name like C40/run-3@full-578.")
    ev = {"seat": seat, "event": "finding", "id": iid, "type": args.type,
          "severity": args.severity, "name": args.name}
    ev["from"] = args.from_
    _emit(ev, w, quiet=True)
    print("%s recorded against %s (from %s)." % (args.name, iid, args.from_))
    return 0


def cmd_spawn(args, seat):
    """`spawn --from <cause> --for <SEAT> --name <NEW>` — no host item.
```

## `src/RimMandrake/rimflow/cli.py:3205-3218` — cmd_spawn's causeless-cause refusal

```python
    ⛔ Do not reintroduce `--id` here.
    """
    args.for_ = _unretire(args.for_)
    _reader_or_die(args.for_)
    _, w = load()
    _mint_or_die(args.name, w)
    known = (args.from_ in w.items or args.from_ in w.findings
             or model.RUN_RE.match(args.from_ or ""))
    if not known:
        die("--from %r names nothing in the ledger. It must be an item id, a finding "
            "name, or a run like C40/run-3@full-578 — `from` IS the causal link, and a "
            "cause that resolves to nothing is not one." % args.from_)
    ev = {"seat": seat, "event": "spawn", "name": args.name,
          "kind": args.kind, "needs": args.needs, "spec": args.spec,
```

## `src/RimMandrake/rimflow/relentless_explain.py:55-90` — _pairs and validate (the lifted grammar)

```python
                         % (name.replace("_", "-"), MIN, v[:80]))
    return v


def _pairs(name, vals, what):
    out = []
    for v in vals or []:
        if SEP not in (v or ""):
            raise ValueError("--%s takes \"%s %s %s\": got %r" % (name.replace("_", "-"), what[0], SEP, what[1], (v or "")[:80]))
        a, b = (x.strip() for x in v.split(SEP, 1))
        if len(a) < 4 or len(b) < 4 or PLACEHOLDER.search(a + b):
            raise ValueError("--%s: both sides of %r must be said (no <placeholder>): got %r" % (name.replace("_", "-"), SEP, v[:80]))
        out.append({what[0]: a, what[1]: b})
    if not out:
        raise ValueError("give at least one --%s \"%s %s %s\"" % (name.replace("_", "-"), what[0], SEP, what[1]))
    return out


def validate(a, kinds, item, cause=None):
    """CLI args (a dict: expected, observed, mechanism, step|steps, ruled_out) -> the explanation fields, or ValueError
    naming what is missing. `kinds`: the classes or targets it explains; `cause`: the follow-up item id."""
    rec = {k: _text(k, a.get(k)) for k in TEXT}
    rec["steps"] = _pairs("step", a.get("step") or a.get("steps"), ("claim", "evidence"))
    rec["ruled_out"] = _pairs("ruled_out", a.get("ruled_out"), ("theory", "why_not"))
    cause = (cause or "").strip()
    if cause != item and not ID_RX.match(cause):        # the item itself is its own follow-up whatever its id's shape
        raise ValueError("--cause must name the follow-up item that addresses the cause (a filed id): got %r" % cause)
    if cause == item and any(k in OUTSIDE for k in kinds):
        raise ValueError("%s is a cause outside this item: name the repair item (`rimflow namecheck`, `rimflow file <NAME> "
                         "--for BENCH`, or the open one in the cause book), not %s itself" % ("/".join(kinds), item))
    rec["cause"] = cause
    rec["kinds"] = list(kinds)
    return rec


def check_cause(cause, state_of):
```

## `src/RimMandrake/rimflow/testpilot_route.py:1-50` — the Test Pilot route: header, calibration, NOT_A_TEST

```python
"""testpilot_route.py -- which items go to a Test Pilot instead of another code-and-retest cycle.

Owner, 2026-10-31: "Ok, so the "test pilot" agent is a real idea we should simply implement and accept, period."
This is the PERMANENT sitting agent (.claude/agents/rm-testpilot.md, one live debugging session on one item). It is not
the arena's `trio` lane, src/RimMandrake/Utils/arena/testpilot.py, which is a trial arm and has its own rules.

THE RULE: an open item goes to a Test Pilot when any of these holds (since its last TESTPILOT_SAT note):
  streak    3 or more non-pass runs (fail or partial) in a row, over the whole item or within one criterion or config;
  wanted    a seat wrote a TESTPILOT_WANTED note: this defect needs live observation;
  diagnose  the item's INTENT is DIAGNOSE and it needs the live game (needs bridge or game-up), and no pilot has sat.

WHY 3. Measured from the ledger 2026-10-31, 858 items and 2664 runs, chance the next run passes after N non-pass runs
in a row. Whole item: N=0 .75, 1 .52, 2 .42, 3 .21, 4 .11, 5 or more about .05. Per criterion or config: 0 .72, 1 .54,
2 .40, 3 .06, 4 .07, 5 or more under .01. A third miss is the cliff: the retest stops being worth its run.
CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP had 314 and stayed red; one sitting found the cause.

A sitting's core job is MEASURING SURPRISE (owner 2026-11-04): it LOOKs at the screen regularly, reads the test-state
monitor (jawa/vitals) and the window stack, and scores each observation EXPECTED / ODD / ALARMING given the biome, the
test's purpose and the map's history, with the one bridge read that explains it. Each ODD or ALARMING one gets one
EXPLAIN-AWAY from context (the SURPRISE BOOK, surprise_book.py: the biome's real roster, the test's purpose, recent
letters, what earlier sittings learned) before it is filed; a (kind, context) that keeps ending explained or not a
bug is retired there, and a real bug revives it (owner 2026-11-04: "This can be the agent learning.").

Once the item is answered or blocked, a sitting explores the same loaded map like a player would (EXPLORATION PASS,
TEST_PILOT_WIDEN_PAST_THE_CHECKLIST) and files what surprised it as checkable events.

A sitting ends with `rimflow note <ID> --text "TESTPILOT_SAT: ..."`. That restarts the count, so a pilot's finding is
given its fix and retest, and three fresh misses send the item back to a pilot. Items that never route: closed,
blocked (something else is wrong), needs owner (his look, not a live debug), intent JUDGE (an art verdict: no live
debugging answers it). Runs in NOT_A_TEST are not tests of the
item: testq records lane pauses and item-less filler FAILs there.

The Dispatcher reads the ROUTE line `rimflow next` prints (dispatcher.parse_peek), so the marker wording below is a
contract with it and with selftest_testpilot_route.py.
"""
import collections
import json

STREAK = 3
OPEN_STATES = ("proposed", "ready", "doing", "built", "validated")      # model.OPEN_STATES (selftest pins them equal)
LIVE_NEEDS = ("bridge", "game-up")
NOT_A_TEST = ("steve-lane",         # STEVE_LANE_MONITOR_PAUSE_FINDINGS: a lane pause, recorded as a failed run
              "steve-filler", "archmagi-filler")   # STEVE_FILLER_MONITOR_FAIL_FINDINGS: item-less filler FAILs (ingest)
SAT, WANTED = "TESTPILOT_SAT", "TESTPILOT_WANTED"
ROUTE = "ROUTE rm-testpilot"
HOSTS = ("stevedesktop", "archmagi")    # preference order: SteveDesktop's game is ours, Archmagi's list is his
FREE_STATES = ("FREE", "STALE")
EXPLORE = "EXPLORATION PASS"      # the brief's marker for the after-the-item pass (selftest pins it)
EXPLORE_MAX_FILED = 5             # new items one sitting files from exploring; the rest wait in its PROGRESS file
SURPRISE = "MEASURING SURPRISE"   # the brief's marker for the pilot's core framing (owner 2026-11-04; selftest pins it)
```

## `src/RimMandrake/rimflow/testpilot_route.py:115-130` — judge(): the predicate and its why

```python
def judge(item, evs):
    """-> None, or {"id", "kind": streak|wanted|diagnose, "why"} for an item that goes to a Test Pilot. Pure."""
    if item.state not in OPEN_STATES or item.blocked or item.needs == "owner" or "_JUDGE_" in item.id:
        return None
    sat = _last_note(evs, item, SAT)
    runs = [r for r in item.runs if r.index > sat and r.config not in NOT_A_TEST]
    whole, worst, key = streaks(runs)
    if whole >= STREAK or worst >= STREAK:
        where = "in a row" if whole >= worst else "in a row on %s" % key
        return {"id": item.id, "kind": "streak", "why": "%d non-pass runs %s" % (max(whole, worst), where)}
    if _last_note(evs, item, WANTED) > sat:
        return {"id": item.id, "kind": "wanted", "why": "a seat asked for live observation"}
    if "_DIAGNOSE_" in item.id and item.needs in LIVE_NEEDS and sat < 0:
        return {"id": item.id, "kind": "diagnose", "why": "a DIAGNOSE that needs the live game"}
    return None

```

## `src/RimMandrake/rimflow/testpilot_route.py:163-175` — brief(): what the routed agent is told

```python

def brief(verdict, host):
    """The ready-to-paste brief for an rm-testpilot subagent on `host`."""
    i = verdict["id"]
    lines = ["Spawn subagent_type rm-testpilot with model \"fable\" (Fable 5.2, owner 2026-11-16) and this brief. One "
             "sitting, one item.",
             "",
             "Item %s. Routed by the Test Pilot rule: %s." % (i, verdict["why"]),
             "Host: %s. Take: rimflow bridge take --host %s --for \"test pilot %s\"" % (host, host, i)]
    if host == "stevedesktop":
        lines.append("Every live call runs on SteveDesktop: ssh \"$STEVE_WSL\" 'cd ~/rm/runner && ...'. That clone is "
                     "read-only to you; code and deploys go by remote_modcheck.sh --sync --no-run from your own clone. "
                     "A running testq job holds the guard: a refused take means pick the other host, never --force.")
```

## `src/RimMandrake/rimflow/maturation_dispatch.py:1270-1300` — retriable()

```python
            s.setdefault("launches", []).append({"unit": unit, "item": item, "at": now, "cap": cap,
                                                 "stage": "offline_build", "cert_reds": reds})
    s["cert_red"] = {"tests": reds, "items": chosen, "unit": unit, "at": now, "failed": None if unit else text,
                     "code": cfg.get("_code"),
                     "tries": int(prior.get("tries") or 0) + 1 if not prior.get("unit") and prior else 1}
    if unit:
        row.update(decision="launched", unit=unit, item=sorted(set(chosen.values()))[0], why=text,
                   items=sorted(set(chosen.values())))
        return True
    row.update(decision="launch_failed", why=str(text), need="%s: the launch on red deciders %s failed (%s); the step "
               "will not retry it on its own" % (mod, ", ".join(reds), text))
    return False


def retriable(cfg, x, killed=None):
    """-> True when a blind or in-game book entry is a launch that NEVER STARTED on a transient fault (a git lock, its
    item not yet on origin/main: maturation_autonomy.transient) with tries left (launch_tries, 3). Such a launch judged
    nothing, so it is not the visit's automatic run; one that started, or failed any other way, is
    (RIMMANDRAKE_RETRY_JUDGE_LAUNCH_GIT_LOCK_SPENT_THE_CYCLE). An older entry without tries reads as its first try.
    killed ({unit: ...}, killed_runs): a run that started and was KILLED before it wrote a result is retried the same
    way (RIMMANDRAKE_RETRY_RUN_KILLED_BY_ACCOUNT_SWITCH_CYCLE_KEPT); one that ended by itself with no record is not."""
    if not isinstance(x, dict):
        return False
    if x.get("unit"):
        # a started run's retries count its KILLS (killed_before plus this one), not the launch faults before it
        # started: Gimme Some Slack's visit 1 started on launch try 3, was stopped for his look, and stood stopped
        # (RIMMANDRAKE_ENACT_TOKENS_NOT_DOLLARS_NO_LIVE_HOLD, 2026-11-16)
        kills = len(x.get("killed_before") or []) + 1
        return not x.get("failed") and x["unit"] in (killed or {}) and kills < int(cfg.get("launch_tries", 3))
    if int(x.get("tries") or 1) >= int(cfg.get("launch_tries", 3)):
        return False
```

## `src/RimMandrake/rimflow/maturation_dispatch.py:1520-1548` — decide_ingame: the terminals and the per gate

```python
            now - le, n, settle))
        return False
    owed = f.get("owed")
    if owed == "blocked":
        b = "; ".join(f.get("blocked") or [])
        put("held" if "hold" in b else "blocked", b)
        return False
    if owed == "exit met":
        put("exit_met", "in-game visit %s: exit met (%s)" % (n, (ex.get("why") or ["-"])[0]),
            "in-game visit %s: exit met (a program's reading of %s, its build match counting every check on the walk "
            "build); the steward reads it and confirms: maturation.py advance %s --to pre_human --steward-confirms "
            "\"...\" (a Conductor step; the program never advances)"
            % (n, summ, mod))
        return False
    if owed == "exit not met":
        put("exit_not_met", "; ".join((ex.get("why") or [])[:3]),
            "in-game visit %s ended, exit not met (%s); nothing more launches on it: the Conductor reads %s and sends "
            "each failed line item down its road back" % (n, "; ".join((ex.get("why") or [])[:3]), summ))
        return False
    mine = [x for x in ours if x.get("visit") == n]
    retry = mine[-1] if mine and retriable(cfg, mine[-1], f.get("killed")) else None
    resume = bool(retry and retry.get("unit"))     # a killed driver's half-written visit is resumed, not unfinished
    if owed == "no exit block" and not resume:
        put("visit_unfinished", "nothing is live and %s has no exit block" % summ,
            "in-game visit %s has a record (%s) with no exit block and nothing live on it; nothing launches: the "
            "Conductor reads it (and checks the game was left closed or healthy)" % (n, summ))
        return False
    if owed != "run" and not (resume and owed == "no exit block"):
        put("blind", "in-game acceptance's state cannot be read (%s)" % owed,
```

## `src/RimMandrake/rimflow/maturation_autonomy.py:50-72` — TRANSIENT / NEVER_TRANSIENT: the existing fault vocabulary

```python
import maturation as M          # noqa: E402

UNM = "UNMEASURED"
EXCLUDE_MARKER = ".maturation-exclude"      # a concept folder holding it is never discovered (test fixtures)
WAIT = {"live", "settling", "driver_busy", "bridge_held", "slots_full", "slots_unknown", "account_hold", "designer_wait",
        "queued", "launch_retry", "upstream_wait", "certificate"}
# a launch that never started on one of these is retried (measured 2026-11-15: a git index.lock at publish, then the
# launcher's "not on origin/main" refusal, read as a spent steward run)
TRANSIENT = re.compile(r"index\.lock|is not on origin/main|ingest\.lock stayed busy|publish stopped|another "
                       r"ingest/publish holds|systemd-run did not answer")
# a refusal no retry can pass: the clone is held by a run whose finish never ran (detached_helper.clone_holders). It
# read transient when the filing's own publish line said "publish stopped", and three tries went in two minutes
# (RIMMANDRAKE_UNSTICK_DISPATCH_CLONE_PUBLISH_LINT_REFUSES_HEAD, 2026-11-16)
NEVER_TRANSIENT = re.compile(r"finish step never ran")


def transient(text):
    """-> True when a launch failure's text names a transient fault (a lock, an unpublished shard, a silent
    systemd-run that left no unit), and no refusal a retry cannot pass."""
    return bool(text) and bool(TRANSIENT.search(str(text))) and not NEVER_TRANSIENT.search(str(text))


def releasable(s, key, x):
```

## `src/RimMandrake/Utils/findings_fold.py:98-118` — normalise/row_key/signature: the existing comparator

```python


def normalise(text, rules):
    t = text or ""
    for rx, rep in rules["_norm"]:
        t = rx.sub(rep, t)
    return t


def row_key(mod, chain, row, text, rules, name=None):
    """The identity of a failure: the whole tuple. name: given only for a finding no done record explains."""
    return (mod, chain, row, normalise(text, rules), name)


def signature(key):
    """Its full sha256 over an unambiguous encoding: a label for the tuple, which is what rows are grouped by."""
    return "S" + hashlib.sha256(json.dumps(list(key)).encode("utf-8")).hexdigest()


# ------------------------------------------------------------------ inputs (each fails closed)
def _strs(x):
```

## `src/RimMandrake/Utils/modcheck/status.py:415-450` — verdict_for and record_run

```python
def verdict_for(all_green, walk, refused="", reviewed=False):
    """The GREEN definition of north_star_validation_spec.md §5, in one place.

    GREEN requires all five: state assertions pass, every validated must-show
    line is claimed, every claim is judged, the checklist is VALIDATED, and he
    has reviewed the sheet once. The last three are what this function adds.

      REFUSED              the visual floor or an orphaned `shows=` (never ran)
      RED                  something failed -- state or judge
      DRAFT-CHECKLIST      both halves passed against a bar that is not his yet
      PENDING-OWNER-REVIEW both halves passed; his own eyes not yet on a sheet
      GREEN                all five

    ⚠️ A mod whose walk has NO `## north star` section reaches GREEN exactly as
    it did before this system existed. Enforcement is per mod, as he validates
    (owner, 2026-09-15) -- that is what makes the whole change additive.
    """
    if refused:
        return "REFUSED"
    if not all_green:
        return "RED"
    present, state = _checklist_state(walk)
    if present and state != "VALIDATED":
        return "DRAFT-CHECKLIST"
    if present and not reviewed:
        return "PENDING-OWNER-REVIEW"
    return "GREEN"


def record_run(mod, mod_dir, run_id, all_green, walk=None, refused="", extra=None):
    """Called once per `modcheck run <mod>`. Never hand-called mid-run --
    the runner calls this exactly once, after every chain has finished.

    `all_green` is the run's BOTH-HALVES verdict (state and judge); `walk` is the
    mod's validation walk, whose checklist state and the owner's recorded review
    decide whether an all-green run is allowed to be called GREEN.
```

## `src/RimMandrake/Utils/modcheck/status.py:615-632` — step4_live: UNMEASURED is DERIVED, not written

```python
def step4_required(mod_dir):
    return bool(mod_dir) and os.path.isfile(os.path.join(mod_dir, *STEP4_SCRIPT))


def step4_live(entry, mod_dir):
    """The step-4 state as it stands NOW: None for a mod with no step 4, else PASS / FAIL / UNMEASURED / STALE.
    Only a stored PASS at the mod's current hash reads PASS -- a missing step-4 record is UNMEASURED, never PASS."""
    if not step4_required(mod_dir):
        return None
    s4 = (entry or {}).get("step4") or {}
    st = s4.get("status")
    if st not in ("PASS", "FAIL"):
        return "UNMEASURED"
    if s4.get("mod_hash") != mod_hash(mod_dir):
        return "STALE"
    return st


```
