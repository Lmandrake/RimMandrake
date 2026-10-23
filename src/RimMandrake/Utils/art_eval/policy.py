#!/usr/bin/env python3
"""The art-eval decision policy — pure functions, no I/O beyond reading the skill's policy files.

The owner's pipeline (2026-10-23, his words): *"Opus scores first. If it says good, auto-accept. If it says really
bad, regen. If it says weak/need a call, send to GPT. If GPT says strong accept, accept, otherwise regen."*

Every rule below is that pipeline plus one of the seat's guards (skill `rimworld-art-evaluation`,
`references/pipeline.md`):

  band (Opus)      GOOD       zero policy-blocking findings, every applicable checklist item answered ok (or an
                              allowed n/a), no gross code, and the model itself did not say weak/really_bad
                   REALLY_BAD a gross code, or a policy-blocking finding at confidence >= high_confidence
                   WEAK       everything else (low-confidence blocking, unreadable items, model doubt)
  GPT outcome      ACCEPT only on strong_accept + every concern refuted WITH evidence + no policy-blocking finding
                   of its own; anything else REGEN
  regen            reason-driven (the blocking findings' fixes), at most max_rounds per subject, then ESCALATE
  owner-kept art   MAY be redrawn when the pipeline says regen (owner card 2026-10-23 06:42, KEPT_ART_CARD) — only
                   with a revert record (the kept picture's install path + sha), flagged on the next shadow sheet as
                   "replaced your kept art" with a one-click revert; no revert record -> HOLD_KEPT
  catch items      follow their living creature: living REGEN/ESCALATE -> REGEN_AFTER_SOURCE
  incomplete card  HOLD_INPUT, never sent to a model

Severity is decided by `references/severity_policy.md` (a ```json policy block), never by the model; the
model's own severity guess is kept beside it so disagreement is visible.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SKILL = ROOT / "skills" / "rimworld-art-evaluation"
REFS = SKILL / "references"
TEMPLATES = ("creature", "plant", "machine")
STATUSES = ("ok", "fail", "unreadable", "n/a")
BANDS = ("GOOD", "WEAK", "REALLY_BAD")
KEPT_ART_CARD = "Kept art judged really bad: may the pipeline redraw it on its own? → Yes, but show me after"
KEPT_ART_EVENT = "1792763093645804582"          # the OWNER ledger event (tsn) carrying that card
DECISIONS = ("ACCEPT", "REGEN", "ESCALATE", "HOLD_KEPT", "HOLD_INPUT", "REGEN_AFTER_SOURCE", "HOLD_ERROR")
DEFAULT_SETTINGS = {
    "max_regen_rounds": 3,
    "min_refute_evidence_chars": 15,
    "shadow": {t: {"on": True, "off_after_consecutive_clean": 30} for t in TEMPLATES},
}


class SchemaError(ValueError):
    """A reviewer reply that does not fit the schema (the runner re-asks once, then HOLD_ERROR)."""


# ------------------------------------------------------------------ policy files
_BLOCK_RE = re.compile(r"```json (\w+)\n(.*?)\n```", re.S)


def json_block(md_text: str, tag: str) -> dict:
    """The ```json <tag> block of a markdown file, parsed. Raises if absent or not exactly one."""
    blocks = [b for t, b in _BLOCK_RE.findall(md_text) if t == tag]
    if len(blocks) != 1:
        raise ValueError(f"expected exactly one ```json {tag} block, found {len(blocks)}")
    return json.loads(blocks[0])


def load_policy(path: Path | None = None) -> dict:
    return json_block(Path(path or REFS / "severity_policy.md").read_text(), "policy")


def load_template(name: str, path: Path | None = None) -> dict:
    if name not in TEMPLATES and path is None:
        raise ValueError(f"unknown template {name!r}; one of {TEMPLATES}")
    text = Path(path or REFS / "templates" / f"{name}.md").read_text()
    t = json_block(text, "template")
    t["module_text"] = text.split("```json template")[0].rstrip()   # the part sent to the reviewer
    return t


def prompt_version(path: Path) -> dict:
    """{'tag': 'preamble@v1', 'sha': '<12 hex>'} — the tag is the file's own version line, the sha its bytes."""
    text = Path(path).read_text()
    m = re.search(r"<!-- version: (\S+) -->", text) or re.search(r'"version": "([^"]+)"', text)
    return {"tag": m.group(1) if m else "UNVERSIONED", "sha": hashlib.sha256(text.encode()).hexdigest()[:12]}


# ------------------------------------------------------------------ card facts and checklist
def card_facts(card: dict) -> set:
    """The facts the policy's `when` / `polish_when` clauses test, derived from the card."""
    f = set()
    f.add("invented" if card.get("invented") else "not_invented")
    for key in ("departures", "canon", "siblings", "owner_notes", "flight", "swim_lane", "ports"):
        if card.get(key):
            f.add(key)
    if card.get("earth_body_named"):
        f.add("earth_body_named")
    if card.get("body_plan"):
        f.add("body_plan:" + card["body_plan"])
    return f


def checklist_for(template: dict, module: str, facts: set) -> list:
    out = []
    for it in template["checklist"]:
        if "modules" in it and module not in it["modules"]:
            continue
        if module in it.get("not_modules", []):
            continue
        if it.get("when") and it["when"] not in facts:
            continue
        out.append(it)
    return out


def required_panels(template: dict, module: str) -> list:
    rp = template["required_panels"]
    return rp.get(module, rp.get("*", []))


def missing_panels(template: dict, module: str, panels: dict) -> list:
    return [p for p in required_panels(template, module) if not panels.get(p)]


def severity(code: str, facts: set, policy: dict) -> str:
    """blocking | polish | gross | input. An unknown code is blocking (fail closed) — a reviewer inventing a code
    must not be able to slip a defect past the policy."""
    c = policy["codes"].get(code)
    if c is None:
        return "blocking"
    if c["default"] == "blocking" and any(cond in facts for cond in c.get("polish_when", [])):
        return "polish"
    return c["default"]


# ------------------------------------------------------------------ reviewer replies
def parse_reply(text: str) -> dict:
    """The JSON object in a model reply (tolerates a code fence or leading prose)."""
    text = (text or "").strip()
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    if m:
        text = m.group(1)
    else:
        i, j = text.find("{"), text.rfind("}")
        if i < 0 or j < i:
            raise SchemaError("no JSON object in the reply")
        text = text[i:j + 1]
    try:
        return json.loads(text)
    except ValueError as e:
        raise SchemaError(f"reply JSON does not parse: {e}") from e


def _check_findings(fs):
    if not isinstance(fs, list):
        raise SchemaError("findings is not a list")
    for f in fs:
        if not isinstance(f, dict) or not f.get("code"):
            raise SchemaError(f"finding without a code: {f!r}")
        try:
            float(f.get("confidence", 0.5))
        except (TypeError, ValueError):
            raise SchemaError(f"finding {f.get('code')} has a non-numeric confidence") from None


def validate_opus(reply: dict, items: list) -> dict:
    if not isinstance(reply, dict) or reply.get("schema") != "rm-art-eval/opus@v1":
        raise SchemaError("schema is not rm-art-eval/opus@v1")
    cl = reply.get("checklist")
    if not isinstance(cl, dict):
        raise SchemaError("checklist missing")
    for it in items:
        a = cl.get(it["id"])
        if not isinstance(a, dict) or a.get("status") not in STATUSES:
            raise SchemaError(f"checklist item {it['id']} not answered with one of {STATUSES}")
    _check_findings(reply.get("findings", []))
    if reply.get("overall") not in ("good", "weak", "really_bad"):
        raise SchemaError("overall must be good|weak|really_bad")
    return reply


def validate_gpt(reply: dict, concerns: list) -> dict:
    if not isinstance(reply, dict) or reply.get("schema") != "rm-art-eval/gpt@v1":
        raise SchemaError("schema is not rm-art-eval/gpt@v1")
    _check_findings(reply.get("findings", []))
    if reply.get("verdict") not in ("strong_accept", "regen", "unsure"):
        raise SchemaError("verdict must be strong_accept|regen|unsure")
    if not isinstance(reply.get("concerns", []), list):
        raise SchemaError("concerns is not a list")
    return reply


# ------------------------------------------------------------------ the Opus band
def classify_findings(findings: list, facts: set, policy: dict) -> dict:
    out = {"blocking": [], "polish": [], "gross": []}
    for f in findings:
        sev = severity(f["code"], facts, policy)
        g = dict(f, policy_severity=sev)
        out.get(sev, out["blocking"]).append(g)
    return out


def opus_band(reply: dict, items: list, facts: set, policy: dict) -> tuple[str, dict]:
    """(band, detail). A checklist `fail` with no matching finding becomes a finding of that item's code at
    confidence 0.7 (a definite observation, but not a confident defect report), so it can never pass silently."""
    findings = list(reply.get("findings", []))
    codes = {f["code"] for f in findings}
    incomplete = []
    for it in items:
        a = reply["checklist"][it["id"]]
        if a["status"] == "fail" and it["code"] not in codes:
            findings.append({"code": it["code"], "where": "checklist " + it["id"], "seen": a.get("seen", ""),
                             "confidence": 0.7, "fix": "", "synthetic": True})
            codes.add(it["code"])
        elif a["status"] == "unreadable":
            incomplete.append(it["id"])
        elif a["status"] == "n/a" and not it.get("when") and "modules" not in it:
            incomplete.append(it["id"] + " (n/a on an unconditional item)")
    cls = classify_findings(findings, facts, policy)
    hi = policy.get("high_confidence", 0.8)
    confident_blocking = [f for f in cls["blocking"] if float(f.get("confidence", 0.5)) >= hi]
    if cls["gross"] or confident_blocking:
        band = "REALLY_BAD"
    elif not cls["blocking"] and not incomplete and reply.get("overall") == "good":
        band = "GOOD"
    else:
        band = "WEAK"
    return band, {"blocking": cls["blocking"], "polish": cls["polish"], "gross": cls["gross"],
                  "incomplete": incomplete, "model_overall": reply.get("overall"),
                  "severity_disagreements": [f["code"] for f in cls["blocking"] + cls["polish"]
                                             if f.get("model_severity") and f.get("model_severity") != f["policy_severity"]]}


def concerns_from(detail: dict) -> list:
    """What GPT is asked to settle: every blocking finding and every unreadable checklist item."""
    ks = []
    for f in detail["blocking"]:
        ks.append({"id": f"K{len(ks) + 1}", "code": f["code"], "where": f.get("where", ""), "seen": f.get("seen", ""),
                   "kind": "finding"})
    for item in detail["incomplete"]:
        ks.append({"id": f"K{len(ks) + 1}", "code": "CHECKLIST", "where": item,
                   "seen": "the first reviewer could not tell from the images", "kind": "unreadable"})
    if not ks and detail.get("model_overall") != "good":
        ks.append({"id": "K1", "code": "OVERALL", "where": "whole subject",
                   "seen": "the first reviewer rated it '%s' without a blocking finding" % detail.get("model_overall"),
                   "kind": "doubt"})
    return ks


def gpt_outcome(reply: dict, concerns: list, facts: set, policy: dict, min_evidence: int = 15) -> tuple[str, dict]:
    answers = {c.get("id"): c for c in reply.get("concerns", []) if isinstance(c, dict)}
    unsettled = []
    for k in concerns:
        a = answers.get(k["id"])
        if not a or a.get("answer") != "refuted" or len((a.get("evidence") or "").strip()) < min_evidence:
            unsettled.append(k["id"])
    cls = classify_findings(reply.get("findings", []), facts, policy)
    own_blocking = cls["blocking"] + cls["gross"]
    strong = reply.get("verdict") == "strong_accept" and not unsettled and not own_blocking
    return ("ACCEPT" if strong else "REGEN"), {"unsettled": unsettled, "blocking": own_blocking,
                                               "polish": cls["polish"], "verdict": reply.get("verdict")}


# ------------------------------------------------------------------ routing
def pre_route(card: dict, template: dict, living_decision: str | None) -> str | None:
    """A decision taken before any model is asked, or None to proceed."""
    if missing_panels(template, card.get("module", ""), card.get("panels", {})):
        return "HOLD_INPUT"
    if card.get("module") == "catch" and living_decision in ("REGEN", "ESCALATE", "REGEN_AFTER_SOURCE"):
        return "REGEN_AFTER_SOURCE"
    return None


def after_opus(band: str, card: dict) -> str:
    """'ACCEPT' | 'REGEN' | 'GPT' | 'HOLD_KEPT'. Owner-kept art routes like any other (owner card 2026-10-23:
    "Yes, but show me after") — but only when it can be put back: no revert record -> HOLD_KEPT."""
    if card.get("owner_kept") and not revert_record_ok(card):
        return "HOLD_KEPT"
    return {"GOOD": "ACCEPT", "REALLY_BAD": "REGEN", "WEAK": "GPT"}[band]


def revert_record_ok(card: dict) -> bool:
    """A kept picture can be put back only if the card names every kept file: [{mod, rel, sha}]."""
    k = card.get("kept_install")
    return bool(k) and all(isinstance(x, dict) and x.get("mod") and x.get("rel") and x.get("sha") for x in k)


def revert_commands(card_or_rec: dict, by_card: str) -> list:
    """art.py install argv lists that put the owner-kept picture(s) back (the one-click revert)."""
    return [["python3", "src/RimMandrake/Utils/art/art.py", "install", k["mod"], k["rel"], k["sha"], "--by-card", by_card]
            for k in card_or_rec.get("kept_install") or []]


def replaces_kept(card: dict, decision: str) -> bool:
    return bool(card.get("owner_kept")) and decision == "REGEN"


def cap_regen(decision: str, prior_rounds: int, max_rounds: int) -> tuple[str, int]:
    """(decision, round). A REGEN past the cap becomes ESCALATE (one line to the owner, not a sheet)."""
    if decision != "REGEN":
        return decision, prior_rounds
    if prior_rounds >= max_rounds:
        return "ESCALATE", prior_rounds
    return "REGEN", prior_rounds + 1


def regen_findings(opus_detail: dict, gpt_detail: dict | None, gpt_reply: dict | None) -> list:
    """The findings a regeneration must fix: Opus's blocking ones that GPT did not refute, plus GPT's own."""
    refuted = set()
    if gpt_reply:
        refuted = {c.get("id") for c in gpt_reply.get("concerns", []) if c.get("answer") == "refuted"}
    ks = concerns_from(opus_detail) if gpt_reply else []
    refuted_codes = {k["code"] for k in ks if k["id"] in refuted}
    out = [f for f in opus_detail["blocking"] + opus_detail["gross"] if f["code"] not in refuted_codes]
    if gpt_detail:
        out += gpt_detail["blocking"]
    return out


def deterministic_regen_prompt(card: dict, findings: list) -> dict:
    """The fallback next prompt when the regen-prompt model call fails: description + every fix, positive."""
    fixes = [f.get("fix") for f in findings if f.get("fix")]
    anatomy = any(f["code"] in ("STYLE_EARTHLY", "DEPARTURE_MISSING", "X_WRONG", "CATCH_WRONG") for f in findings)
    body = [f"{card.get('label') or card['subject']}: {card.get('description', '').strip()}"]
    if card.get("departures"):
        body.append("It is NOT an Earth animal: " + "; ".join(card["departures"]) + ".")
    body += fixes
    body.append("Painterly vanilla RimWorld style, realistic, clean dark outline, transparent background.")
    return {"schema": "rm-art-eval/regen@v1", "subject": card["subject"],
            "edits": [{"finding": f["code"], "change": f.get("fix", "")} for f in findings],
            "invariants": [], "reference": "none" if anatomy else "keep", "prompt": " ".join(body),
            "by": "deterministic"}


# ------------------------------------------------------------------ shadow mode
def shadow_status(template: str, shadow_rows: list, settings: dict) -> dict:
    """Per template: consecutive owner-reviewed subjects since the last BLOCKING override, and whether the shadow
    sheet is still owed. shadow_rows are {template, at, override: bool, blocking: bool} in time order."""
    cfg = settings["shadow"].get(template, DEFAULT_SETTINGS["shadow"]["creature"])
    streak = 0
    for r in sorted((r for r in shadow_rows if r.get("template") == template), key=lambda r: r.get("at", "")):
        if r.get("override") and r.get("blocking"):
            streak = 0
        else:
            streak += 1
    need = cfg["off_after_consecutive_clean"]
    return {"template": template, "on_setting": cfg["on"], "consecutive_clean": streak, "threshold": need,
            "shadow_owed": bool(cfg["on"]) and streak < need,
            "eligible_to_turn_off": streak >= need}


def load_settings(path: Path | None = None) -> dict:
    p = Path(path or ROOT / "infrastructure/state/art_eval/settings.json")
    s = json.loads(json.dumps(DEFAULT_SETTINGS))
    if p.is_file():
        user = json.loads(p.read_text())
        for k, v in user.items():
            if k == "shadow":
                for t, cfg in v.items():
                    s["shadow"].setdefault(t, {}).update(cfg)
            elif not k.startswith("_"):
                s[k] = v
    return s
