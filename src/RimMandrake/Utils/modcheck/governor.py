"""modcheck.governor -- the row governor: contract, latch, verdict, restart, and a test-environment item per threat.

Item TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO. Design: design/RimMandrake/test_control/monitor_governor_build.md;
basis GPT review §3.2/§4/§5 (design/RimMandrake/test_control/test_control_review_gpt_20261013.md).

THE OWNER'S RULINGS (debug_process.md § "Test disturbances", 2026-10-13, by card), enforced here:
  * an anomaly that was CORRECTED, with no evidence of damage to the test  -> the row may still PASS (CLEAN with a note);
  * ANY damage to the test itself (a required/support colonist hurt, downed or dead, colony loss, the specimen gone,
    an undeclared clock jump)                                               -> the row is RESTARTED, never scored FAIL;
  * EVERY threat that appears during a test is logged AND gets a test-environment item -> `env_item_lines()` prints a
    ready-to-file `rimflow file TESTENV_..._HARDEN_...` line per distinct threat;
  * long runs of game time only when clearly worth it -> a populated-map advance over the row's budget is refused by
    the companion (jawa/safe_advance) unless the contract declares `time_exception`;
  * protected (support) colonists only on rows labelled as NOT about health / needs / damage / death -> RowContract
    refuses `protected=True` on such rows.

Two independent dimensions, as in contract.py: criterion PASS / FAIL / UNMEASURED and validity CLEAN / DISRUPTED /
INDETERMINATE. The governor adds the OUTCOME the harness acts on: PASS, FAIL, RESTART, UNMEASURED.

The companion side is `jawa/vitals` (monitor + latch) and `jawa/safe_advance` (chunked, interruptible stepping). This
module is pure apart from `RowGovernor`'s session calls; every rule is a row in selftest_governor.py.
"""
import re

import contract as C

PASS, FAIL, RESTART, UNMEASURED = "PASS", "FAIL", "RESTART", "UNMEASURED"
HEALTH_TAGS = frozenset(("health", "needs", "damage", "death"))

# severities from JawaBenchVitalsCore
S_INFO, S_THREAT, S_DAMAGE, S_BLOCK, S_CLOCK, S_COVERAGE = "info", "threat", "damage", "block", "clock", "coverage"
DAMAGE_KINDS = frozenset(("colony_loss", "specimen_lost"))

# kind -> (subject word(s), twist) for the environment item name. SUBJECT_INTENT_TWIST, intent HARDEN, <= 7 words.
ENV_NAMES = {
    "hostile_arrival": ("HOSTILES", "KNOCK_FIRST"),
    "threat_structure": ("TURRETS", "NO_SURPRISE_GUNS"),
    "modal_stuck": ("POPUPS", "CLOSE_THE_DOOR"),
    "starving": ("FOOD", "PACK_A_LUNCH"),
    "downed": ("DOWNED", "STAY_STANDING"),
    "hurt": ("WOUNDS", "NO_BRUISES"),
    "death": ("DEATHS", "EVERYONE_GOES_HOME"),
    "colony_loss": ("COLONY_LOSS", "KEEP_LIGHTS_ON"),
    "clock_discontinuity": ("CLOCK_JUMP", "NO_TIME_TRAVEL"),
    "mental": ("BREAKS", "KEEP_CALM"),
    "colonist_hostile": ("TURNCOATS", "NONE_TODAY"),
    "specimen_lost": ("SPECIMEN", "KEEP_THE_SAMPLE"),
    "letter": ("THREAT_LETTERS", "READ_THE_MAIL"),
    "departed": ("ACTOR_GONE", "STAY_PUT"),
    "coverage": ("BLIND_SPOTS", "KEEP_WATCHING"),
    "cancel": ("CANCELS", "FINISH_THE_STEP"),
}


class ContractError(ValueError):
    pass


class RowContract(object):
    """What a row declares before it runs (GPT §4.1, minimal)."""

    def __init__(self, row, about=(), actors=(), specimens=(), budget_ticks=0, time_exception=False,
                 protected=False, expected=(), max_restarts=2):
        self.row = str(row)
        self.about = frozenset(a.strip().lower() for a in about)
        if protected and self.about & HEALTH_TAGS:
            raise ContractError("protected colonists refused: row %r is about %s (owner 2026-10-13: protection only on "
                                "rows NOT about health, needs, damage or death)" % (row, sorted(self.about & HEALTH_TAGS)))
        self.actors = [str(a) for a in actors]
        self.specimens = [str(s) for s in specimens]
        self.budget_ticks = int(budget_ticks or 0)
        self.time_exception = bool(time_exception)
        self.protected = bool(protected)
        # expected transitions: (kind, subject_id or None, max_count) -- bounded, field-specific (GPT §4.1)
        self.expected = []
        for e in expected:
            e = (e,) if isinstance(e, str) else tuple(e)
            self.expected.append((e[0], e[1] if len(e) > 1 else None, int(e[2]) if len(e) > 2 else 1))
        self.max_restarts = int(max_restarts)

    def arm_params(self, ttl_min=60, why=None):
        p = {"action": "arm", "ttlMin": ttl_min, "row": self.row, "timeException": self.time_exception,
             "budgetTicks": self.budget_ticks, "why": why or "row governor"}
        if self.actors:
            p["critical"] = ",".join(self.actors)
        if self.specimens:
            p["specimens"] = ",".join(self.specimens)
        return p


def _id_num(x):
    m = re.search(r"(\d+)$", str(x or ""))
    return int(m.group(1)) if m else None


def classify(trig, contract, used=None):
    """-> 'ignore' | 'expected' | 'damage' | 'anomaly' | 'coverage' | 'declared_clock'. Pure."""
    used = used if used is not None else {}
    kind, sev = trig.get("kind"), trig.get("severity")
    for i, (k, subj, cap) in enumerate(contract.expected):
        if k != kind:
            continue
        if subj is not None and _id_num(subj) != trig.get("subjectId"):
            continue
        if used.get(i, 0) < cap:
            used[i] = used.get(i, 0) + 1
            return "expected"
    if kind == "clock_discontinuity":
        if trig.get("declared"):
            return "declared_clock" if contract.time_exception else "damage"
        return "damage"
    if sev == S_COVERAGE or kind == "coverage":
        return "coverage"
    if sev == S_DAMAGE or kind in DAMAGE_KINDS:
        return "damage"
    if sev == S_INFO:
        return "ignore"
    return "anomaly"          # threat / block / undeclared non-damaging disturbance


def is_threat(trig, cls):
    """Every disturbance that is not info and not expected is a threat to the test (owner: each gets an item)."""
    return cls in ("damage", "anomaly", "coverage") and trig.get("kind") != "cancel"


class Verdict(dict):
    pass


def judge(contract, triggers, criterion, corrected=(), coverage_ok=True, coverage_why=None):
    """The row's verdict. `triggers` = jawa/vitals events since arm. `corrected` = trigger seqs the harness corrected
    (visitor removed, modal closed, fire put out) with no damage. `criterion` = PASS | FAIL | UNMEASURED (the mod's own
    assertion). Pure."""
    used, rows = {}, []
    for t in triggers:
        cls = classify(t, contract, used)
        if cls != "ignore":
            rows.append(dict(t, cls=cls))
    corrected = set(corrected)
    damage = [r for r in rows if r["cls"] == "damage"]
    coverage = [r for r in rows if r["cls"] == "coverage"]
    anomalies = [r for r in rows if r["cls"] == "anomaly"]
    open_anom = [r for r in anomalies if r.get("seq") not in corrected]
    threats = [r for r in rows if is_threat(r, r["cls"])]
    first = min((r for r in rows if r["cls"] in ("damage", "anomaly", "coverage")), key=lambda r: r.get("seq", 0), default=None)
    notes = []
    if damage:
        validity, outcome = C.DISRUPTED, RESTART
        notes.append("damage to the test: " + "; ".join("%s %s (%s)" % (r["kind"], r.get("subject"), r.get("detail")) for r in damage[:4]))
        notes.append("criterion %s is NOT scored (owner: damage restarts the row, never FAIL)" % criterion)
    elif coverage or not coverage_ok:
        validity, outcome = C.INDETERMINATE, UNMEASURED
        notes.append("coverage lost: " + ("; ".join(r.get("detail") or r["kind"] for r in coverage[:3]) or coverage_why or "monitor not covering"))
    elif open_anom:
        validity, outcome = C.INDETERMINATE, UNMEASURED
        notes.append("anomaly not corrected: " + "; ".join("%s %s" % (r["kind"], r.get("subject")) for r in open_anom[:4]))
    else:
        validity = C.CLEAN
        outcome = {"PASS": PASS, "FAIL": FAIL}.get(str(criterion).upper(), UNMEASURED)
        if anomalies:
            notes.append("CLEAN with %d corrected anomal%s, no evidence of damage: %s" % (
                len(anomalies), "y" if len(anomalies) == 1 else "ies",
                "; ".join("%s %s" % (r["kind"], r.get("subject")) for r in anomalies[:4])))
    if any(r["cls"] == "declared_clock" for r in rows):
        notes.append("declared clock reassignment under the row's time exception")
    return Verdict(row=contract.row, criterion=criterion, validity=validity, outcome=outcome,
                   first_disturbance=first, damage=damage, anomalies=anomalies, coverage=coverage,
                   threats=threats, notes=notes,
                   env_items=env_item_lines(contract.row, threats))


# ------------------------------------------------------------------------------------------ environment items

def env_item_name(kind):
    subj, twist = ENV_NAMES.get(kind, (re.sub(r"[^A-Z0-9]+", "_", str(kind).upper()).strip("_") or "THREAT", "NEVER_AGAIN"))
    return "TESTENV_%s_HARDEN_%s" % (subj, twist)


def _q(s):
    return '"%s"' % str(s).replace('"', "'").replace("\n", " ")[:220]


def env_item_lines(row, threats):
    """One ready-to-file line per distinct threat KIND in this row (the item's job: stop that interference next time)."""
    out, seen = [], set()
    for t in threats:
        k = t.get("kind")
        if k in seen:
            continue
        seen.add(k)
        title = "Test environment: %s interfered with row %s at tick %s (%s); control it so it cannot recur" % (
            k, row, t.get("tick"), t.get("detail") or t.get("subject"))
        out.append("rimflow file %s --for BENCH --kind task --needs offline --title %s --why %s" % (
            env_item_name(k), _q(title), _q("row governor: every threat to a test is logged and gets a "
                                           "test-environment item (owner, 2026-10-13, debug_process.md)")))
    return out


# ------------------------------------------------------------------------------------------ the governor

def _unwrap(r):
    if isinstance(r, dict) and r.get("content"):
        try:
            import json
            return json.loads(r["content"][0]["text"])
        except Exception:                                      # noqa: BLE001
            return r
    return r if isinstance(r, dict) else {}


class RowGovernor(object):
    """PRECHECK -> ARMED -> EXECUTING -> CHECKING -> COMPLETE | LATCHED. The session is any object with
    call(tool, **params) -> dict. Never depends on telemetry ingestion (GPT §3.2)."""

    def __init__(self, session, contract, log=print):
        self.s, self.c, self.log = session, contract, log
        self.state = "PRECHECK"
        self.corrected = set()
        self.since = 0
        self.advances = []
        self.coverage_ok, self.coverage_why = True, None

    def call(self, tool, **p):
        return _unwrap(self.s.call(tool, **p))

    def arm(self, ttl_min=60):
        r = self.call("jawa/vitals", **self.c.arm_params(ttl_min))
        if not r.get("success"):
            self.coverage_ok, self.coverage_why = False, "arm failed: %s" % (r.get("message") or r.get("error") or r)
            self.state = "LATCHED"
            return r
        self.since = 0     # a fresh arm clears the latch; baseline triggers (hostiles present at arm) belong to this row
        self.state = "ARMED"
        return r

    def advance(self, ticks, stop_on="default"):
        """Governed time: the companion refuses over-budget advances and stops on the latch."""
        self.state = "EXECUTING"
        r = self.call("jawa/safe_advance", ticks=int(ticks), budgetTicks=self.c.budget_ticks,
                      timeException=self.c.time_exception, stopOn=stop_on)
        self.advances.append({k: r.get(k) for k in ("state", "requested", "executed", "refused", "stopBy")})
        if r.get("state") in ("stopped", "aborted"):
            self.state = "LATCHED"
        return r

    def correct(self, seq, how):
        """The harness corrected an anomaly (removed a visitor, closed a modal). Damage is never correctable."""
        self.corrected.add(seq)
        self.log("governor: corrected trigger %s (%s)" % (seq, how))

    def triggers(self):
        r = self.call("jawa/vitals", action="events", sinceSeq=self.since, limit=500)
        if not r.get("success"):
            self.coverage_ok, self.coverage_why = False, "events unreadable: %s" % (r.get("message") or r)
            return []
        if (r.get("truncated") or 0) > 0:
            self.coverage_ok, self.coverage_why = False, "%d triggers truncated" % r["truncated"]
        st = self.call("jawa/vitals")
        if not st.get("armed"):
            self.coverage_ok, self.coverage_why = False, "monitor not armed at verdict (%s)" % st.get("lastDisarm")
        return r.get("triggers") or []

    def verdict(self, criterion):
        self.state = "CHECKING"
        v = judge(self.c, self.triggers(), criterion, self.corrected, self.coverage_ok, self.coverage_why)
        v["advances"] = list(self.advances)
        self.state = "COMPLETE" if v["outcome"] in (PASS, FAIL) else "LATCHED"
        for t in v["threats"]:
            self.log("governor: THREAT %s %s at tick %s: %s" % (t.get("kind"), t.get("subject"), t.get("tick"), t.get("detail")))
        for line in v["env_items"]:
            self.log("governor: file -> " + line)
        return v

    def disarm(self):
        try:
            self.call("jawa/vitals", action="disarm", why="row %s done" % self.c.row)
        except Exception:                                      # noqa: BLE001
            pass


def run_row(session, contract, body, setup=None, log=print):
    """Run one row under the governor, restarting it on damage (never FAIL), up to contract.max_restarts.
    `setup(attempt)` rebuilds the fixture (a reload is preferred: GPT §3.4); `body(gov)` runs the row and returns the
    criterion PASS | FAIL | UNMEASURED. Returns {'final': verdict, 'attempts': [verdicts]}."""
    attempts = []
    for attempt in range(contract.max_restarts + 1):
        if setup is not None:
            setup(attempt)
        gov = RowGovernor(session, contract, log=log)
        gov.arm()
        try:
            crit = body(gov) if gov.state == "ARMED" else UNMEASURED
        except Exception as e:                                 # noqa: BLE001 - a harness crash is not a mod FAIL
            log("governor: row body raised %r" % (e,))
            crit = UNMEASURED
        v = gov.verdict(crit)
        gov.disarm()
        v["attempt"] = attempt
        attempts.append(v)
        log("governor: row %s attempt %d -> %s (%s) %s" % (contract.row, attempt, v["outcome"], v["validity"],
                                                          " | ".join(v["notes"])))
        if v["outcome"] != RESTART:
            break
    return {"final": attempts[-1], "attempts": attempts,
            "restarts_exhausted": attempts[-1]["outcome"] == RESTART}
