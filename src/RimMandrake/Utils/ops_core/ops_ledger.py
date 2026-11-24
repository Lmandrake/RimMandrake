"""ops_ledger.py (RimPulse's pulse_core.py until 2026-11-18) -- the shared ledger readers the ops tools use: every clone's rimflow ledger, folded by rimflow's own model, and the
owner-ask classifier streams.py counts (owner_rulings, ask_class, ask_addressee, ask_label).

What is left of RimPulse's spine (the dashboard retired 2026-11-03; its collectors, rows and pages went
2026-11-18 and this moved from Utils/pulse/, RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES). Readers: ops_watch, deadman_check,
known_reds, streams, testing_metrics, usage. The ledger key is `id`, NOT `item`.
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import tarfile
from pathlib import Path

HOME = Path.home()

STATE_DIR = Path(os.environ.get("RM_PULSE_STATE", HOME / ".local" / "state" / "rm-dashboard"))
CLONES = [Path("/home/mandrake/rm/bench")]


def read_jsonl_tail(path: Path, tail_bytes: int = 1 << 20, strict: bool = False,
                    allow_missing: bool = True) -> list[dict]:
    """The last `tail_bytes` of a JSONL file as records; torn lines are skipped.

    strict=True is for a collector SOURCE (RIMPULSE_SOURCES_FIX_SILENCE_READS_HEALTHY): an unreadable file
    raises instead of reading as "nothing happened", a missing one raises unless `allow_missing` (a log
    nobody has written yet is a valid empty), and a non-empty tail with no parseable line raises."""
    try:
        with open(path, "rb") as fh:
            fh.seek(0, 2)
            size = fh.tell()
            fh.seek(max(0, size - tail_bytes))
            chunk = fh.read().decode("utf-8", "replace")
    except FileNotFoundError:
        if strict and not allow_missing:
            raise
        return []
    except OSError:
        if strict:
            raise
        return []
    return _parse_jsonl(chunk, path, strict)


def _parse_jsonl(chunk: str, path: Path, strict: bool) -> list[dict]:
    out, bad = [], 0
    for line in chunk.splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            bad += bool(line.strip())
    if strict and bad and not out:
        raise ValueError(f"{path.name}: {bad} line(s), none parseable")
    return out


def _model():
    """rimflow's own fold (src/RimMandrake/rimflow/model.py): the single source of item state."""
    import sys
    root = str(Path(__file__).resolve().parents[2])
    if root not in sys.path:
        sys.path.insert(0, root)
    from rimflow import model
    return model


def _origin_jsonl(root: Path, shard_dir: str):
    """Read history and shards from one immutable, locally available origin/main tree."""
    ref = "refs/remotes/origin/main"
    ledger = Path("infrastructure/state/ledger")
    r = subprocess.run(["git", "--git-dir", str(root / ".git"), "archive", "--format=tar", ref, ledger.as_posix()],
                       capture_output=True, timeout=5, env={**os.environ, "GIT_NO_LAZY_FETCH": "1"})
    if r.returncode:
        raise RuntimeError(f"{root} {ref}: git archive: {r.stderr.decode(errors='replace').strip()}")
    with tarfile.open(fileobj=io.BytesIO(r.stdout), mode="r:") as archive:
        files = [f for f in archive if Path(f.name) == ledger / "events.jsonl"
                 or (Path(f.name).parent == ledger / shard_dir and f.name.endswith(".jsonl"))]
        if not files:
            raise RuntimeError(f"{root} {ref}: no ledger history or shards")
        for f in files:
            if not f.isfile():
                raise ValueError(f"{root} {ref}: {f.name} is not a regular file")
            with archive.extractfile(f) as fh:
                yield from _parse_jsonl(fh.read().decode("utf-8", "replace"), Path(f.name), strict=True)


def read_ledger(clones: list[Path] = CLONES, *, origin: Path | None = None) -> list[dict]:
    """Union of every clone's shards (each seat's own shard is freshest in its own clone), deduped and
    ordered by rimflow's reader invariant (identity = content, never file position). WHOLE files: a
    tail would drop the `file` events and rimflow's replay would lose the items (FOUNDRY.jsonl was
    1.9 MB on 2026-10-10 and the old tail was 4 MB). A torn line is skipped here, not raised - a
    window mid-append must not blank the widget. With `origin`, read only that clone's local origin/main."""
    model = _model()
    events = (_origin_jsonl(origin, model.SHARD_DIR) if origin is not None else
              (e for f in ledger_files(clones) for e in read_jsonl_tail(f, 1 << 40, strict=True, allow_missing=False)))
    return model.canonical_order(model.from_disk(e) for e in events)     # model.WRITE_NAMES folds CONDUCTOR/RELENTLESS to BENCH


def ledger_files(clones: list[Path] = CLONES) -> list[Path]:
    """rimflow's own file list per clone: the frozen history `events.jsonl` + every seat shard. Without
    the history file the replay never sees pre-cutover `file` events and those items do not exist."""
    model = _model()
    return [Path(f) for c in clones for f in model.ledger_files(str(c / "infrastructure/state/ledger/events.jsonl"))]


def owner_rulings(ledger: list[dict]) -> dict:
    """iid -> the event that made an OPEN item's `needs` "owner", for every item rimflow itself says
    is waiting on him right now. Derived from rimflow's replay, never from a second reading of the
    verbs: `implemented`, `verify`, `file --needs`, `needs`, close/drop/... all move `needs` or the
    state, and pulse once only knew about `needs` (SCRAPNEST stayed "to rule" after `implemented`
    made it needs=bridge, 2026-10-10). A repeated `needs --to owner` re-asks and moves the time."""
    import re
    became: dict[str, dict] = {}
    answered: dict[str, dict] = {}
    decided: set[str] = set()

    def obs(ev, world, ok):
        iid = ev.get("id")
        it = world.items.get(iid) if iid else None
        if it is None:
            return
        # a BLOCKED item is parked on something else (another item, or his own "later"): he cannot act on it
        # now, so it is not an ask; unblocking re-asks it fresh (owner 2026-10-23: answered rows lingered)
        if (it.open and it.needs == "owner" and not it.blocked and iid in decided
                and not (ok and ev.get("event") == "needs")):
            return                      # filed from his card: only a fresh `needs --to owner` asks him again
        if (it.open and it.needs == "owner" and not it.blocked and ev.get("event") == "file" and ev.get("byCard")
                and re.search(r"\blater\b|until he asks", f"{it.title or ''} {ev.get('reason') or ''}", re.I)):
            # filed FROM his own card as a "later - until he asks": the decision is made, the item is parked for
            # when he calls for it, and no question is waiting on him (owner 2026-10-24,
            # CONTAGION_PEAKS_WIRE_WEEPING_RULES_LATER). A card-filed ask with no "later" stays an ask.
            decided.add(iid)
            became.pop(iid, None)
            answered.pop(iid, None)
        elif it.open and it.needs == "owner" and not it.blocked:
            decided.discard(iid)
            if iid not in became or (ok and ev.get("event") == "needs"):
                became[iid] = ev            # (re-)asked: any earlier answer was to an earlier question
                answered.pop(iid, None)
            elif ok and (ev.get("ownerSaid") or ev.get("byCard")):
                # his words or his card AFTER the ask, on this item: the question is answered even though
                # nobody has moved `needs` yet (owner 2026-10-23: rows for answered cards persisted)
                answered[iid] = ev
        else:
            became.pop(iid, None)
            answered.pop(iid, None)
    world = _model().replay(list(ledger), observe=obs)
    filed: dict[str, dict] = {}
    for e in ledger:
        if e.get("event") == "file" and e.get("id") in became:
            filed.setdefault(e["id"], e)
    blocks: dict[str, list[str]] = {}       # ask id -> open items blocked on it (the agents waiting on his call)
    for other in world.items.values():
        if other.open and other.blocked:
            for on in (other.blocked_on, *(other.blocked_also or ())):
                if on in became and other.id not in blocks.setdefault(on, []):
                    blocks[on].append(other.id)
    out = {}
    for iid, ev in became.items():
        it = world.items[iid]
        an = answered.get(iid)
        klass, why = ask_class(it, ev)
        to, to_why = ask_addressee(it, ev, filed.get(iid))
        out[iid] = {"ev": ev, "t": iso_to_epoch(ev.get("ts", "")), "seat": (ev.get("seat") or "").upper(),
                    "reason": ev.get("reason") or it.title, "state": it.state, "class": klass, "class_why": why,
                    "addressee": to, "addressee_why": to_why, "blocks": sorted(blocks.get(iid, ())),
                    "answered": ({"t": iso_to_epoch(an.get("ts", "")), "event": an.get("event"),
                                  "seat": (an.get("seat") or "").upper(),
                                  "by": "card" if an.get("byCard") else "his words",
                                  "text": an.get("byCard") or an.get("ownerSaid")} if an else None)}
    return out

# What the owner is being asked for, from the item itself (owner 2026-10-23: a look masqueraded as a ruling).
RULE_KINDS = {"decision", "ruling", "question", "card", "decide", "design"}
LOOK_KINDS = {"art", "review", "check", "verify", "trial"}
_LOOK_RE = r"(\(?\blook\b[,:)]|\bL4\b|\blooks? at\b|\bglances?\b|\bin[- ]situ\b|\bwalk\b|\bsheet\b|\bscreenshot|\bkeeper save|\bjoint\b)"
# a FACT only he has (an address, a host, a key); verbs like "address the issue" or "provide feedback" are not
_PROVIDE_RE = (r"(\bname/address\b|\b(ip|e-?mail|network|home) address\b|\baddress (of|for)\b|\bhostname\b|"
               r"\bpassword\b|\bcredentials?\b|\bwhich (pc|machine|account)\b|"
               r"\bneeds (its|his|the) (name|address|number|path|url|key)\b)")

# a LIVE walkthrough (game running, a joint session) is not an artifact he opens: never in "to look at"
# (owner 2026-10-23). "in-game" alone stays a look when the thing is a saved picture, so only walk wording counts.
_WALK_RE = r"(\bwalk-?through\b|\bwalk\b|\bin[- ]game\b|\bjoint\b|\bkeeper save|\bbridge run\b)"

# A hands-on machine job (a RUNBOOK step, a BIOS setting, the router, a power cord) is work only his hands at home
# can do: never a ruling. It goes to the folded "when you're home" list with its total time (owner card
# 2026-10-25: "Folded 'when you're home' list"; RIMPULSE_PAGE_FIX_CHORES_POSE_AS_RULINGS).
_HANDS_RE = (r"(\bRUNBOOK step\b|\bBIOS\b|\brouter\b|\bpower (cord|cable|button|strip)\b|\bPSU\b|\bunplug|"
             r"\bplug (it )?in\b|\bethernet cable\b|\bDHCP\b.{0,40}\breservation\b|\bpower[- ]cycle\b)")

_RUNBOOK_HEAD_RE = r"^\s*RUNBOOK step \d+\s*(\([^)]*\))?\s*:\s*"


def ask_label(iid: str, title: str, reason: str = "") -> str:
    """The question in plain words, noun first, for his list (owner 2026-10-25: labels showed cut-off ticket
    names). A chore is its task with the RUNBOOK head dropped; a ruling is '<subject>: <the which/whether
    question>' when its words hold one, else '<subject>: <its title>'. The slug itself goes in the hover."""
    import re
    text = " ".join(str(title or reason or "").split())
    bare = re.sub(_RUNBOOK_HEAD_RE, "", text, flags=re.I)
    if bare != text:
        return (bare[:1].upper() + bare[1:]) if bare else text
    try:
        parsed = _model().parse_name(iid)
    except Exception:  # noqa: BLE001 - a label must never break the snapshot
        parsed = None
    subj = " ".join(parsed[0]).lower() if parsed else nice_id(iid)
    words = f"{text} {reason or ''}"
    q = re.search(r"\b(which|whether|what|how (?:many|much|big|often)|should (?:we|it|the))\b[^.;:()?]*", words, re.I)
    if q:
        body = re.split(r"\s+(?:is|are|stays?|remains?)\s+(?:an?\s+|the\s+)?(?:owner|his|lukas)\b", q.group(0), flags=re.I)[0]
        body = body.strip(" ,")
        return f"{subj.capitalize()}: {body[:1].lower() + body[1:]}?"
    if not text or text.lower() == nice_id(iid):
        return subj.capitalize() if parsed else nice_id(iid).capitalize()
    return f"{subj.capitalize()}: {text[:1].lower() + text[1:]}" if not text.lower().startswith(subj) else text


def ask_class(it, ev: dict) -> tuple[str, str]:
    """ask_class_raw, but a look that is a live interactive walkthrough is class 'walk' (not listed anywhere)."""
    klass, why = ask_class_raw(it, ev)
    if klass == "look":
        crit = " ".join(str(c.get("text") or c.get("desc") or "") for c in getattr(it, "criteria", [])
                        if c.get("id") in getattr(it, "outstanding", ()) and c.get("level") == "L4")
        import re
        text = f"{it.title or ''} {ev.get('reason') or ev.get('why') or ''} {crit}"
        if re.search(_WALK_RE, text, re.I):
            return "walk", f"live walkthrough, not an artifact ({why})"
    return klass, why


def ask_class_raw(it, ev: dict) -> tuple[str, str]:
    """('rule' | 'look' | 'provide' | 'hands', why) for an open item waiting on the owner. Pure over the item fold.

    Order: an explicit word on the needs event wins ('look:', 'provide:', 'rule:', or '(LOOK, not a ruling)');
    an item whose only owed criteria are L4 is a look; then the item's kind; then its words. Anything else is
    a ruling - the only class that asks him for a verdict."""
    import re
    reason = str(ev.get("reason") or ev.get("why") or "")
    text = f"{it.title or ''} {reason}"
    head = reason.strip().lower()
    for k in ("look", "provide", "rule", "hands"):
        if head.startswith(k + ":"):
            return k, f"needs event says '{k}:'"
    if re.search(r"\bLOOK, not a ruling\b", reason, re.I):
        return "look", "needs event says it is a look"
    if re.search(_HANDS_RE, text, re.I):
        return "hands", "a hands-on machine job at home"
    owed = it.owed_levels() if hasattr(it, "owed_levels") else []
    if owed and set(owed) == {"L4"}:
        return "look", "only an L4 (owner look) criterion is owed"
    kind = (it.kind or "").lower()
    if kind in RULE_KINDS:
        return "rule", f"kind {kind}"
    if re.search(_PROVIDE_RE, text, re.I):
        return "provide", "asks for a fact"
    if kind in LOOK_KINDS:
        return "look", f"kind {kind}"
    if re.search(_LOOK_RE, text, re.I):
        return "look", "asks him to look"
    return "rule", "default: waiting on his verdict"

# WHO an ask is addressed to (owner 2026-10-25: "do NOT tell me about pending questions that aren't for the user").
# rimflow's `needs=owner` is set freely by any seat, and `--for` names the seat that WORKS the item, never who must
# answer; so needs=owner alone does not make a question his. Only an explicit sign does. An ask with no sign either
# way is 'unknown': kept out of his list (fail closed for display) but counted in one dim line, never hidden silently.
_AGENT_ADDR_RE = (r"\b(?:for|to|asks?|asking|awaits?|awaiting|waiting on|needs?|over to|delegated to)\s+(?:the\s+|an?\s+)?"
                  r"(?:BENCH|FOUNDRY|agents?|seats?|(?:art[- ])?judges?|GPT|Codex|Opus|Nemotron)\b")
# Words that ADDRESS him, not words that merely mention him ("owner 2026-10-23 redraw", "owner's AFK" are provenance).
_OWNER_NOUN = (r"(?:cards?|picks?|calls?|verdict|grade|ruling|looks?|eyes?|words?|choice|decision|approval|sign-?off|ok|"
               r"curation|answer|say|review)")
_OWNER_VERB = r"(?:decides|picks|rules|chooses|sees|looks|grades|approves|watches|opens|judges|reviews|curates|answers)"
_OWNER_ADDR_RE = (r"(?:\b(?:for|to|with|asks?|asking|needs?|awaits?|awaiting|waiting on|held for)\s+(?:the\s+)?(?:owner|lukas|him)\b|"
                  r"\b(?:owner|lukas)(?:'s)?\s+(?:\w+\s+)?(?:" + _OWNER_NOUN + "|" + _OWNER_VERB + r")\b|"
                  r"\bhis\s+(?:\w+\s+)?" + _OWNER_NOUN + r"\b|\bhe\s+" + _OWNER_VERB + r"\b|"
                  r"(?:^|[.;(]\s*|\s)(?:owner|lukas):)")


def ask_addressee(it, ev: dict, file_ev: dict | None = None) -> tuple[str, str]:
    """('owner' | 'agent' | 'unknown', why) for an open needs=owner ask. Pure.

    Order: a structural owner sign (the ask or the item's filing was written by the OWNER seat or carries his
    words / card / ruling; the item is `--for OWNER`; the only criteria still owed are L4, the owner level) wins;
    then an explicit head word on the ask ('agent:' / 'owner:'); then words that address an agent, seat or judge;
    then words that address him. Anything else is 'unknown'."""
    import re
    fe = file_ev or {}
    for e, what in ((ev, "the ask"), (fe, "the filing")):
        if (e.get("seat") or "").upper() == "OWNER":
            return "owner", f"{what} was written by the OWNER seat"
        for k, w in (("ownerSaid", "his words"), ("byCard", "his card"), ("perRuling", "his ruling")):
            if e.get(k):
                return "owner", f"{what} carries {w}"
    if str(getattr(it, "owner", None) or fe.get("for") or "").upper() == "OWNER":
        return "owner", "the item is for OWNER"
    owed = it.owed_levels() if hasattr(it, "owed_levels") else []
    if owed and set(owed) == {"L4"}:
        return "owner", "only an L4 (owner) criterion is owed"
    reason = str(ev.get("reason") or ev.get("why") or "")
    head = reason.strip().lower()
    if head.startswith("agent:"):
        return "agent", "the ask says 'agent:'"
    if head.startswith("owner:"):
        return "owner", "the ask says 'owner:'"
    text = " ".join(str(x or "") for x in (getattr(it, "title", None), reason,
                                           fe.get("why") if fe is not ev else None))
    m = re.search(_AGENT_ADDR_RE, text, re.I)
    if m:
        return "agent", f"addressed to an agent: '{m.group(0)}'"
    m = re.search(_OWNER_ADDR_RE, text, re.I)
    if m:
        return "owner", f"names him: '{m.group(0)}'"
    return "unknown", "needs=owner with nothing that says it is his"


def nice_id(iid: str) -> str:
    import re
    return re.sub(r"_\d+$", "", str(iid or "")).lower().replace("_", " ")


def iso_to_epoch(ts: str) -> float:
    from datetime import datetime
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except (ValueError, AttributeError):
        return 0.0
