#!/usr/bin/env python3
"""Regen round SERIES and OWNER-WRITTEN PROMPTS for the art-eval fauna loop.

Round series (owner card 2026-10-24 06:29, "After round 3 fate -> 1 + user improved prompts"): a creature whose
regen rounds were spent on foreign-image copies gets fresh rounds. Nobody edits regen_rounds.json or decision logs
for that: a RESET is one appended line in infrastructure/state/art_eval/round_resets.jsonl

    {"at": ISO, "def": DEF, "series": k, "source_run": RUN, "by_card"|"owner_said"|"why": ...}

and every counter reads through it:
  - rounds filed in the current series = 1 (the reset files round 1 from source_run's prompt) + REGEN decisions on
    the subject dated after the reset;
  - job / candidate tags carry the series so fresh jobs never collide with the old ones:
    series 0 -> "r2", series 1 -> "s1r2" (artpipe job arteval_<DEF>_s1r2_<facing>).

Owner prompts: his improvement for a creature is used VERBATIM as the creature description of the next round's
prompt, wrapped by the template sentences (style, alpha, camera/size consistency) that the pipeline owns; the facing
is stamped per job by the artpipe daemon. Sources, newest wins:
  1. infrastructure/state/art_eval/owner_prompts.jsonl  {"at", "def", "text", "owner_said"|"by_card", "source"}
     (the main window appends what he sends in chat with `fauna_drive.py owner-prompt`);
  2. a non-empty `prompt` or `note` he typed on a row of an owner escalation sheet
     Transient/biome_ffar/owner_escalations_*_sheet_*.decisions.json (prefill notes are always empty, so a non-empty one is his).
Both are re-read on every `rows` call, so notes he adds later are picked up with no extra step.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STATE = ROOT / "infrastructure/state/art_eval"
RESETS = STATE / "round_resets.jsonl"
OWNER_PROMPTS = STATE / "owner_prompts.jsonl"
SHEET_GLOB = "Transient/biome_ffar/owner_escalations_*_sheet_*.decisions.json"

STYLE_HEAD = ("A single RimWorld creature sprite of the {label}, painterly vanilla RimWorld style, realistic, clean "
              "dark outline, transparent background.")
STYLE_TAIL = ("Same low, angled game camera and the same body size in every drawing. The edges fade cleanly into "
              "transparency with crisp dark outline pixels and no coloured fringe.")


def _instant(s):
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def _jsonl(p: Path) -> list:
    if not p.is_file():
        return []
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]


def resets(path: Path = RESETS) -> dict:
    """{def: latest reset record}; the record's series = how many resets that def has had."""
    out = {}
    for r in _jsonl(path):
        if r.get("def") and (r["def"] not in out or _instant(r["at"]) >= _instant(out[r["def"]]["at"])):
            out[r["def"]] = r
    return out


def series(defname: str, rs: dict | None = None) -> int:
    r = (resets() if rs is None else rs).get(defname)
    return int(r["series"]) if r else 0


def tag(defname: str, n: int, rs: dict | None = None) -> str:
    k = series(defname, rs)
    return f"r{n}" if k == 0 else f"s{k}r{n}"


def decisions(runs_dir: Path = STATE / "runs", prefix: str = "fauna_"):
    for f in sorted(runs_dir.glob(f"{prefix}*/decisions.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                yield f.parent.name, json.loads(line)


def regen_counts(recs, rs: dict | None = None) -> dict:
    """{def: rounds filed in the CURRENT series}. Series 0: the number of REGEN decisions (the old rule). After a
    reset: 1 (round 1 re-filed by the reset) + REGEN decisions dated after it."""
    rs = resets() if rs is None else rs
    n = {}
    for _, r in recs:
        d = r["subject"]
        if r.get("decision") != "REGEN":
            continue
        if d in rs and _instant(r.get("at")) <= _instant(rs[d]["at"]):
            continue
        n[d] = n.get(d, 0) + 1
    for d in rs:
        n[d] = n.get(d, 0) + 1
    return n


def apply_to_rounds(rounds: dict, recs, rs: dict | None = None) -> dict:
    """runner.run's `rounds` (prior regen rounds per subject) with every reset subject replaced by its series count,
    so the cap of 3 applies to the fresh series. regen_rounds.json itself is never rewritten for a reset."""
    rs = resets() if rs is None else rs
    if not rs:
        return rounds
    cnt = regen_counts(recs, rs)
    out = dict(rounds)
    for d in rs:
        out[d] = cnt.get(d, 1)
    return out


def add_reset(defname: str, source_run: str, prov: dict, path: Path = RESETS, now: str | None = None) -> dict:
    if not any(prov.get(k) for k in ("by_card", "owner_said", "per_ruling")):
        raise ValueError("a round reset is the owner's decision: give --by-card, --owner-said or --per-ruling")
    rec = {"at": now or datetime.now().astimezone().isoformat(timespec="seconds"), "def": defname,
           "series": series(defname, resets(path)) + 1, "source_run": source_run}
    rec.update({k: v for k, v in prov.items() if v})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(json.dumps(rec) + "\n")
    return rec


# ------------------------------------------------------------------ owner prompts
def owner_prompts(root: Path = ROOT, path: Path = OWNER_PROMPTS) -> dict:
    """{def: {"text", "at", "source"}} newest per def across owner_prompts.jsonl and the owner sheets' notes."""
    found = {}

    def put(d, text, at, source):
        text = (text or "").strip()
        if not text:
            return
        if d not in found or _instant(at) >= _instant(found[d]["at"]):
            found[d] = {"text": text, "at": at, "source": source}

    for r in _jsonl(path):
        put(r.get("def"), r.get("text"), r.get("at"), f"{path.name}:{r.get('at')}")
    for f in sorted(root.glob(SHEET_GLOB)):
        try:
            sheet = json.loads(f.read_text())
        except (ValueError, OSError):
            continue
        rs = sheet.get("reviewStatus") or {}
        at = rs.get("at") or datetime.fromtimestamp(f.stat().st_mtime).astimezone().isoformat(timespec="seconds")
        decs = sheet.get("decisions")
        if not isinstance(decs, dict):
            continue
        for d, v in decs.items():
            if isinstance(v, dict):
                put(d, v.get("prompt") or v.get("note"), at, f"{f.relative_to(root)}#{d}")
    return found


def compose_owner_prompt(label: str, text: str) -> str:
    """His text verbatim between the template's own sentences. Nothing of his is reworded or dropped."""
    return " ".join([STYLE_HEAD.format(label=label), text.strip(), STYLE_TAIL])


def label_of(spec: dict) -> str:
    lab = spec.get("label") or spec.get("subject", "creature")
    return re.sub(r"\s+", " ", str(lab)).strip()
