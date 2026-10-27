"""contracts.models -- the Pydantic v2 wire contracts for five record families (pinned: contracts/requirements.lock).

Two levels per record, on purpose:
  * the COMPAT check a program is wired to: it reproduces that program's acceptance rule exactly, so wiring changes no
    decision. audits.problems() uses AuditRecord here; every reader the dispatcher tick imports (arbiter_pending via
    role_launch, the dispatcher itself, testq's tick, close_evidence) uses the stdlib twins in contracts.compat and
    contracts.jsonl, so the 2-minute tick never pays for pydantic;
  * the STRICT model (extra=forbid, closed enums, typed): the intended contract, run in shadow by contracts.replay,
    which lists every line where the two levels disagree.

Models never mutate or re-serialise the raw dict: close_evidence's mac is over the dict as written.
Import cost: pydantic ~50 ms (measured 2026-10-27, WSL python 3.14). Never import this from a hook.
"""
import re
from typing import Annotated, Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

HEX7_40 = r"^[0-9a-f]{7,40}$"
ISO_UTC_Z = r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?Z$"
ISO_OFFSET = r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?(Z|[+-]\d\d:\d\d)$"


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class Open(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True, frozen=True)


def errors(model, value):
    """-> [] when `value` validates against `model`, else one 'loc: msg' string per error. Never raises."""
    try:
        model.model_validate(value)
        return []
    except ValidationError as e:
        return ["%s: %s" % (".".join(str(x) for x in er["loc"]) or "<root>", er["msg"]) for er in e.errors()]
    except Exception as e:  # noqa: BLE001 - a contract check never crashes its reader
        return ["<root>: %s: %s" % (type(e).__name__, e)]


# ------------------------------------------------------------------ 1. close_evidence (Utils/close_evidence.py, v4)

class CEStart(Strict):
    sha: Optional[str]
    dirty: Optional[bool]
    dirty_n: Optional[int]


class CEOrigin(Strict):
    via: str
    start: Literal["snapshot", "caller"]
    end: Literal["git", "caller"]
    tree: Literal["isolated", "shared"]
    who: Literal["caller", "whoami"]
    pid: int
    host: str


class CloseEvidenceV4(Strict):
    """One line close_evidence.record() writes (build_record + seal). `evidence_shaped` is the shape half of
    counts_as_evidence (schema_problems() == []); the mac and the start/end agreement stay in close_evidence."""
    v: Literal[4]
    ts: str = Field(pattern=ISO_OFFSET)
    nonce: Optional[Annotated[str, Field(pattern=r"^[0-9a-f]{32}$")]] = None
    tool: str = Field(min_length=1)
    clone: Optional[str]
    sha: Optional[Annotated[str, Field(pattern=r"^[0-9a-fA-F]{40}$")]]
    dirty: Optional[bool]
    dirty_n: Optional[int] = None
    dirty_paths: list[str] = []
    start: Optional[CEStart]
    paths: list[str]
    covers: list[str]
    result: Literal["PASS", "FAIL", "UNMEASURED"]
    item: Optional[str] = None
    seat: Optional[str]
    who: dict[str, Any]
    origin: CEOrigin
    live_only: bool
    variant: Optional[str]
    detail: dict[str, Any] = {}
    mac: str = Field(pattern=r"^[0-9a-f]{64}$")
    route: Optional[Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]] = None

    @field_validator("v", mode="before")
    @classmethod
    def _int_version(cls, v):
        if type(v) is not int:      # Literal[4] alone accepts 4.0 (equality); a float version is version confusion
            raise ValueError("v must be the integer 4")
        return v

    @property
    def evidence_shaped(self):
        o = self.origin
        return (o.via, o.start, o.end, o.tree) == ("inproc", "snapshot", "git", "isolated")


class CloseEvidenceLegacy(Open):
    """v1/v2/v3 and v-less lines: readable, never evidence (close_evidence V=4 rule). The adapter only names them."""
    v: Optional[Literal[1, 2, 3]] = None


def close_evidence_kind(d):
    """-> ("v4", model) | ("legacy", model) | ("fault", [errors]) for one decoded close_evidence object."""
    if isinstance(d, dict) and d.get("v") == 4:
        e = errors(CloseEvidenceV4, d)
        return ("fault", e) if e else ("v4", CloseEvidenceV4.model_validate(d))
    e = errors(CloseEvidenceLegacy, d)
    return ("fault", e) if e else ("legacy", CloseEvidenceLegacy.model_validate(d))


# ------------------------------------------------------------------ 2. testq result (Utils/testq/schema.py)

TESTQ_OUTCOMES = Literal["DONE", "INVALID", "INTERRUPTED", "REFUSED"]
TESTQ_CAUSES = Optional[Literal["GUARD_HELD", "SOURCE_SHA_MISSING", "SYNC", "DEPLOY", "LOAD", "CANARY", "HANG",
                                "HARNESS", "BLOCKED_SELECTION", "CRASH", "GAME_DIED"]]


class TestqRow(Strict):
    chain: Optional[str]
    row: str
    verdict: str
    validity: Any = None
    freshness: Any = None
    detail: str = Field(default="", max_length=4000)


class TestqArtifact(Open):
    name: str
    path: str
    sha256: str
    bytes: int


class TestqResult(Strict):
    """testq.result/1 as testq_schema.json declares it, plus the two fields the Steve worker writes without declaring
    them (moot_markers, bounced_for_markers: schema drift, filed). validate_result() is the stdlib check the worker
    still runs (SteveDesktop has no pydantic yet)."""
    schema_: Literal["testq.result/1"] = Field(alias="schema")
    job: str = Field(pattern=r"^J\d{8}T\d{6}Z-[0-9a-f]{6}$")
    attempt: str
    host: str = ""
    runner_sha: Optional[str] = None
    outcome: TESTQ_OUTCOMES
    cause: TESTQ_CAUSES
    deployed: dict[str, Any] = {}
    rows: list[TestqRow]
    counts: dict[str, int] = {}
    phase_s: dict[str, Any] = {}
    retries: int = 0
    modcheck_exit: Optional[int] = None
    artifacts: list[TestqArtifact] = []
    started: str = ""
    finished: Optional[str] = None
    note: str = ""
    moot_markers: list[str] = []
    bounced_for_markers: list[str] = []

    @model_validator(mode="after")
    def _rules(self):
        if not self.attempt.startswith(self.job + ".a"):
            raise ValueError("attempt must be <job>.a<n>")
        if self.outcome != "DONE" and not self.cause:
            raise ValueError("a non-DONE outcome needs a cause")
        return self


# ------------------------------------------------------------------ 3. audits.jsonl (rimflow/audits.py)

def _py_pattern(p):
    rx = re.compile(p)

    def check(v):
        if not rx.search(v):        # re.search, as audits.problems() did: `$` also matches before a final newline
            raise ValueError("does not match %s" % p)
        return v
    return check


class AuditRecord(Open):
    """One Auditor line == audits.schema.json (additionalProperties true, so extra keys stay allowed). This IS the
    acceptance rule audits.problems() now delegates to; selftest_contracts proves it equals the old interpreter."""
    ts: str
    item: str = Field(min_length=1)
    sha: str
    run: str = Field(min_length=1)
    why_picked: Literal["mandatory", "disagreement", "flag", "rank", "random"]
    flags: list[str]
    verdict: Literal["SOUND", "DEFECT", "UNRESOLVED"]
    defect_class: Optional[str]
    evidence: list[str]
    waiting_for: Optional[str] = None

    @field_validator("sha")
    @classmethod
    def _sha(cls, v):
        return _py_pattern(HEX7_40)(v)

    @model_validator(mode="after")
    def _conditionals(self):
        dc = self.defect_class
        if self.verdict == "DEFECT" and not (isinstance(dc, str) and dc.strip()):
            raise ValueError("a DEFECT needs a defect_class")
        if self.verdict in ("SOUND", "UNRESOLVED") and dc is not None:
            raise ValueError("defect_class must be null unless verdict is DEFECT")
        if self.waiting_for not in (None, "") and self.verdict != "UNRESOLVED":
            raise ValueError("waiting_for only on an UNRESOLVED line")
        return self


def audits_problems(d):
    if not isinstance(d, dict):
        return ["not a JSON object"]
    return errors(AuditRecord, d)


# ------------------------------------------------------------------ 4. Arbiter verdicts (rimflow/arbiter_pending.py)

class ArbiterVerdict(Strict):
    """One line of arbiter/verdicts.jsonl (roles/arbiter.md 'Every advisory verdict goes ...'). Exported as JSON Schema
    (contracts/schemas/arbiter_verdict.schema.json) for `claude -p --json-schema`."""
    item: str = Field(min_length=1, description="ledger item id")
    sha: str = Field(pattern=HEX7_40, description="the judged commit, at least 7 hex characters")
    disposition: Literal["PASS", "CONDITIONAL-PASS", "FAIL-module", "FAIL-check", "RESTART-environment",
                         "BAR-defect", "UNRESOLVED"]
    causes: list[Literal["module", "check", "environment", "bar"]] = Field(
        description="coexisting cause tags beside the disposition")
    interim: Optional[str] = Field(description="the interim reviewer's verdict, null when there was none")
    evidence: list[str] = Field(min_length=1, description="absolute Windows paths of the evidence")
    ts: str = Field(pattern=ISO_UTC_Z, description="UTC ISO-8601, Z suffix")


class TiersHistoryRow(Strict):
    """One line of arbiter_tiers' tiers_history.jsonl."""
    generated: str = Field(pattern=ISO_UTC_Z)
    item: str = Field(min_length=1)
    sha: str = Field(pattern=HEX7_40)
    tier: Literal["T0_BOUNCE", "T0_PASS", "T1_PASS", "T2_NOEVIDENCE", "T2_RISK", "T2_UNMEASURED"]
    calibration: bool
    decision: Literal["BOUNCE", "AI", "PASS"]


# ------------------------------------------------------------------ 5. dispatcher observations (rimflow/dispatcher.py)

class AgentSession(Open):
    """One entry of `claude agents --json` (captured 2026-10-27): interactive windows carry pid/status, background
    ones id/state. Open: the CLI may add fields; the dispatcher reads name, sessionId, status/state, cwd."""
    name: Optional[str] = None
    sessionId: Optional[str] = None
    cwd: Optional[str] = None
    kind: Optional[str] = None
    status: Optional[str] = None
    state: Optional[str] = None
    pid: Optional[int] = None
    id: Optional[str] = None
    startedAt: Optional[Union[int, str]] = None


class LedgerEventMin(Open):
    """The fields dispatcher.seat_events_since compares (shadow): seat a string, ts an ISO-8601 string when present.
    The compat rule (contracts.compat.ledger_event_usable) only asks for a string ts; a non-ISO string sorts as
    'after any cutoff' there (filed)."""
    seat: Optional[str] = None
    ts: Optional[Annotated[str, Field(pattern=ISO_OFFSET)]] = None
    event: Optional[str] = None


def sessions_problems(data):
    if not isinstance(data, list):
        return ["not a list"]
    out = []
    for i, s in enumerate(data):
        out += ["[%d] %s" % (i, e) for e in (errors(AgentSession, s) if isinstance(s, dict) else ["not an object"])]
    return out
