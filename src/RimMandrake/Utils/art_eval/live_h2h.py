#!/usr/bin/env python3
"""Live art is judged head-to-head against its candidates, never by its own band (ARTEVAL_JUDGE_LIVE_HEAD_TO_HEAD).

Why: the first pass judges every picture ALONE against a departures brief a model wrote from the description. On the
owner's four escalation sheets of 2026-10-24 (pipeline_tuning/owner_labelled.jsonl) DEPARTURE_MISSING at confidence
>= 0.8 marked 15 live pictures he then PICKED as REALLY_BAD, and no threshold separates them: the code fires at the
same confidences on pictures he purged (sizejump_floor_replay_2026-10-24.json). So the absolute band may start the
regen rounds (a candidate has to exist before anything can be compared), but it never decides the live art's fate.
When a fauna series runs out of rounds (ESCALATE), one fresh Opus sees the description and EVERY picture of the
series side by side - the live art and each candidate, under shuffled letters, nothing saying which is installed -
and picks the best picture of the description:

    winner is the live art   -> KEEP_LIVE: the installed art stays, the escalation is dropped (a delegated art call,
                                logged like every other; it reaches the owner in the daily digest, not as a sheet row)
    winner is a candidate    -> ESCALATE stands, naming that candidate as the field's pick
    no readable verdict      -> ESCALATE stands (an errored compare is no verdict)

MEASURED 2026-11-05 (infrastructure/state/art_eval/live_h2h_replays/, 27 sheet subjects with a live column: 17 he
kept live, 10 he did not): NOT WIRED into the pipeline, because no variant clears the bar (no wrong keep, >= half kept):
    blind run 1        kept 4/17 wanted, 0/10 unwanted
    blind run 2        kept 4/17 wanted, 1/10 unwanted (Scaldhide); the kept set changed between runs
    incumbent          kept 8/17 wanted, 4/10 unwanted (no better than the 17/27 base rate)
Kept by every run: RM_BedBug, RM_Crustweevil, RM_Fuzzviper. The judge rewards redraws that illustrate the description
more literally (they were drawn to it), the same failure as DEPARTURE_MISSING.

    python3 live_h2h.py judge <DEF> --live <card dir> --cand TAG=<card dir> ... --out <dir>
    python3 live_h2h.py replay [--labels owner_labelled.jsonl] [--work DIR] [--out replay.json] [--jobs 6]
    python3 live_h2h.py check-replay <replay.json>      exit 0 when the replay clears the bar, 1 when not
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import random
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import policy as P  # noqa: E402

FACES = ("south", "east", "north")
LETTERS = "ABCDEFGH"
# the owner's verdict on the live column of an escalation sheet: picked = he wanted it kept; anything else = he did not
LIVE_WANTED = ("OWNER_PICKED",)
LIVE_UNWANTED = ("OWNER_RETIRED", "OWNER_PURGED", "NOT_PICKED", "OWNER_POOLED")
# the bar (contract): never keep live art he did not keep; keep at least this share of the live art he did keep
MIN_RESCUE_SHARE = 0.5

PROMPT_INCUMBENT = """You are an independent art judge for RimWorld animal sprites. Several pictures of the SAME creature are image
files in the current directory: {files}. Each is one picture set (south / east / north facings, left to right).
Set {live} is the art INSTALLED in the game now; the others are redraws offered to replace it. Read every one of them
(Read tool) at full resolution before answering, then answer with ONE JSON object and nothing else.

The creature (the description says WHICH creature this is - a guide to its identity, not a checklist: a picture does
not lose for leaving out a detail the description lists, and a redraw does not win for ticking more of them off):

{desc}

House rules (each is a hard defect on the set that breaks it):
- south = face toward the camera; north = the rear (back/tail, no face, no eyes); east = true side profile. A top-down
  / overhead plan view on any facing is a hard defect; so is a facing that is a different animal or pose family.
- The three facings are the same size and the same individual (same markings, horns, tail, colours).
- Realistic and painterly, not cartoon, not cute (glossy round eyes, smiling face, thick uniform black keyline are
  defects). Alien where the description says alien; an ordinary Earth body is fine when the description names one.
- Clean real alpha: no baked ground, no halo, no cropped limbs.

Replace the installed set only when a redraw is CLEARLY the better picture for a player to see in game: it fixes a
hard defect the installed set has without bringing one of its own, or it is plainly the better piece of art of this
creature. When the installed set is sound, painterly art of a creature that fits the description, keep it. Reply
(decision first):
{{"replace_with": "<letter of the redraw, or none>", "reason": "<two sentences>",
  "sets": {{"<letter>": {{"hard_defects": ["..."], "art_quality": 0-10}}, ...one entry per set...}}}}
"""

PROMPT_BLIND = """You are an independent art judge for RimWorld animal sprites. Several pictures of the SAME creature are image
files in the current directory: {files}. Each is one picture set (south / east / north facings, left to right). Read
every one of them (Read tool) at full resolution before answering, then answer with ONE JSON object and nothing else.

The creature (the description is the ONLY authority on what it should look like; do not demand features it does not
state, and do not punish a plain, realistic animal when the description describes one):

{desc}

House rules (each is a defect on the set that breaks it):
- south = face toward the camera; north = the rear (back/tail, no face, no eyes); east = true side profile. A top-down
  / overhead plan view on any facing is a hard defect; so is a facing that is a different animal or pose family.
- The three facings are the same size and the same individual (same markings, horns, tail, colours).
- Realistic and painterly, not cartoon, not cute (glossy round eyes, smiling face, thick uniform black keyline are
  defects). Alien where the description says alien; an ordinary Earth body is fine when the description names one.
- Clean real alpha: no baked ground, no halo, no cropped limbs.

Pick the ONE set that is the best picture of THIS description for a player to see in game. Reply (winner first):
{{"winner": "<letter>", "reason": "<two sentences>",
  "sets": {{"<letter>": {{"hard_defects": ["..."], "serves_description": 0-10}}, ...one entry per set...}}}}
"""

# variant -> (prompt tag, prompt). blind: shuffled letters, nothing says which set is installed, pick the best one.
# incumbent: the installed set is named, a redraw replaces it only when clearly better.
VARIANTS = {"blind": ("live_h2h_field@v2", PROMPT_BLIND), "incumbent": ("live_h2h_incumbent@v3", PROMPT_INCUMBENT)}
DEFAULT_VARIANT = "blind"


# ------------------------------------------------------------------ pure
def letters_for(subject: str, tags: list) -> dict:
    """{tag: letter}, shuffled by a hash of the subject (stable across reruns, so a replay is repeatable; the live
    art is not always A, so position never tells the judge which picture is installed)."""
    tags = list(tags)
    rnd = random.Random(int(hashlib.sha256(subject.encode()).hexdigest()[:12], 16))
    order = tags[:]
    rnd.shuffle(order)
    return {t: LETTERS[i] for i, t in enumerate(order)}


def field_winner(reply: dict | None, letter_of: dict) -> str | None:
    """The tag the judge picked, or None when the reply is no verdict (error, no winner, a letter not shown)."""
    if not isinstance(reply, dict) or reply.get("error"):
        return None
    back = {v: k for k, v in letter_of.items()}
    if "winner" in reply:                                  # blind: the best set
        return back.get(str(reply.get("winner") or "").strip().upper())
    w = str(reply.get("replace_with") or "").strip().upper()   # incumbent: a redraw, or none = keep
    if w in ("NONE", "NULL", ""):
        return "live" if "replace_with" in reply and "live" in letter_of else None
    return back.get(w)


def live_verdict(reply: dict | None, letter_of: dict, live_tag: str = "live") -> tuple[str, str | None]:
    """('KEEP_LIVE', 'live') when the live art won the field; ('ESCALATE', <winning tag or None>) otherwise."""
    w = field_winner(reply, letter_of)
    if w is not None and w == live_tag:
        return "KEEP_LIVE", w
    return "ESCALATE", w


def score(rows: list) -> dict:
    """rows: [{subject, live_label, winner}] -> the replay's tally and whether it clears the bar."""
    wanted = [r for r in rows if r["live_label"] in LIVE_WANTED]
    unwanted = [r for r in rows if r["live_label"] in LIVE_UNWANTED]
    nov = [r for r in rows if r.get("winner") is None]
    kept_wanted = [r["subject"] for r in wanted if r.get("winner") == "live"]
    kept_unwanted = [r["subject"] for r in unwanted if r.get("winner") == "live"]
    out = {"subjects": len(rows), "live_wanted": len(wanted), "live_unwanted": len(unwanted),
           "no_verdict": [r["subject"] for r in nov],
           "keep_live_on_wanted": kept_wanted, "keep_live_on_unwanted": kept_unwanted,
           "rescue_share": round(len(kept_wanted) / len(wanted), 3) if wanted else None}
    out["clears_bar"] = bool(wanted) and len(nov) == 0 and not kept_unwanted and \
        len(kept_wanted) >= MIN_RESCUE_SHARE * len(wanted)
    return out


_WINNER_RE = re.compile(r'"(winner|replace_with)"\s*:\s*"([A-H]|none)"', re.I)


def parse_field(text: str) -> dict:
    """The judge's reply. A reply whose JSON is broken (a brace dropped after the per-set notes) still names its
    winner once; that one field is taken, and the reply is marked `parsed: winner_only` so it is never mistaken for
    a whole reply. Two different winners, or none, is no verdict."""
    try:
        return P.parse_reply(text)
    except Exception as e:  # noqa: BLE001
        ws = set(_WINNER_RE.findall(text or ""))
        if len(ws) == 1:
            m = re.search(r'"reason"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
            key, val = ws.pop()
            return {key: val, "reason": m.group(1) if m else "", "parsed": "winner_only", "parse_error": str(e)}
        return {"error": str(e), "raw": (text or "")[:800]}


# ------------------------------------------------------------------ judging
def compose(sets: dict, letter_of: dict, out: Path, subject: str) -> list:
    """One strip per set: <letter>.png. sets: {tag: {face: path}}."""
    import cards as C  # PIL only when judging
    out.mkdir(parents=True, exist_ok=True)
    names = []
    for tag, imgs in sets.items():
        L = letter_of[tag]
        faces = [f for f in FACES if imgs.get(f)]
        C.strip([imgs[f] for f in faces], [f"{L} {f}" for f in faces], tile=384,
                title=f"set {L} - {subject}").save(out / f"{L}.png")
        names.append(f"{L}.png")
    return sorted(names)


def card_images(card_dir: Path) -> dict:
    return {f: str(card_dir / f"{f}.png") for f in FACES if (card_dir / f"{f}.png").exists()}


def judge_field(subject: str, desc: str, sets: dict, out: Path, call=None, variant: str = DEFAULT_VARIANT) -> tuple[dict, dict]:
    """(reply, letter_of). Writes <out>/field.json. `call(prompt, cwd)` -> (text, meta) is runner.call_claude."""
    letter_of = letters_for(subject, list(sets))
    files = compose(sets, letter_of, out, subject)
    if call is None:
        import runner as R
        call = lambda p, cwd: R.call_claude(p, cwd, "opus", timeout=420, tools="Read")  # noqa: E731
    tag, prompt = VARIANTS[variant]
    text, meta = call(prompt.format(files=", ".join(files), live=letter_of.get("live", "?"), desc=desc), out)
    reply = parse_field(text) if text else {"error": meta.get("error") or "empty reply"}
    reply["_meta"] = {k: meta.get(k) for k in ("models_reported", "seconds", "cost_usd", "error")}
    (out / "field.json").write_text(json.dumps({"subject": subject, "letters": letter_of, "prompt": tag,
                                                "reply": reply}, indent=1))
    return reply, letter_of


# ------------------------------------------------------------------ replay on the owner-labelled sheets
def storage() -> Path:
    return Path(os.environ.get("RM_DATA_ROOT") or "/mnt/d/ClaudeWork/rimmandrake")


def replay_groups(labels: Path, runs: Path) -> list:
    """[{sheet, subject, live_label, sets: {tag: card dir}, desc}] for every sheet subject that has a live column."""
    rows = [json.loads(x) for x in labels.read_text().splitlines() if x.strip()]
    by = collections.defaultdict(list)
    for r in rows:
        by[(r["sheet"], r["subject"])].append(r)
    out = []
    for (sheet, subj), rs in sorted(by.items()):
        live = [r for r in rs if r["candidate"] == "live"]
        if not live:
            continue
        sets, label, desc = {}, live[0]["label"], None
        for r in rs:
            tag = r["candidate"]
            if tag in sets:
                continue
            d = runs / r["run"] / (subj if tag == "live" else f"{subj}__{tag}")
            if not (d / "south.png").exists():
                d = runs / r["run"] / subj
            if (d / "south.png").exists() and (d / "card.json").exists():
                sets[tag] = d
                desc = desc or json.loads((d / "card.json").read_text()).get("description")
        if "live" in sets and len(sets) > 1:
            out.append({"sheet": sheet, "subject": subj, "live_label": label, "sets": sets, "desc": desc})
    return out


def cmd_replay(a) -> int:
    runs = storage() / "art_eval/runs"
    groups = replay_groups(Path(a.labels), runs)
    work = Path(a.work)

    def one(g):
        out = work / f"{g['sheet']}__{g['subject']}"
        f = out / "field.json"
        if f.exists() and json.loads(f.read_text()).get("prompt") == VARIANTS[a.variant][0] \
                and not json.loads(f.read_text())["reply"].get("error"):
            j = json.loads(f.read_text())
            return g, j["reply"], j["letters"]
        sets = {t: card_images(Path(d)) for t, d in g["sets"].items()}
        reply, letters = judge_field(g["subject"], g["desc"], sets, out, variant=a.variant)
        return g, reply, letters

    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        res = list(ex.map(one, groups[: a.limit] if a.limit else groups))
    rows = []
    for g, reply, letters in res:
        rows.append({"sheet": g["sheet"], "subject": g["subject"], "live_label": g["live_label"],
                     "tags": sorted(g["sets"]), "letters": letters, "winner": field_winner(reply, letters),
                     "reason": str(reply.get("reason") or reply.get("error") or "")[:300],
                     "cost_usd": (reply.get("_meta") or {}).get("cost_usd")})
    rep = {"item": "ARTEVAL_JUDGE_LIVE_HEAD_TO_HEAD", "prompt": VARIANTS[a.variant][0], "labels": str(a.labels),
           "work": str(work), "rows": rows, "score": score(rows)}
    Path(a.out).write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps(rep["score"]))
    return 0


def cmd_check(a) -> int:
    rep = json.loads(Path(a.replay).read_text())
    s = score(rep["rows"])                       # recomputed from the rows, never the stored tally
    print(json.dumps(s))
    if s != rep.get("score"):
        print("stored score disagrees with the rows", file=sys.stderr)
        return 1
    return 0 if s["clears_bar"] else 1


def cmd_judge(a) -> int:
    sets = {"live": card_images(Path(a.live))}
    for c in a.cand:
        tag, d = c.split("=", 1)
        sets[tag] = card_images(Path(d))
    desc = json.loads((Path(a.live) / "card.json").read_text()).get("description")
    reply, letters = judge_field(a.defname, desc, sets, Path(a.out))
    print(a.defname, *live_verdict(reply, letters))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("judge"); j.add_argument("defname"); j.add_argument("--live", required=True)
    j.add_argument("--cand", action="append", default=[]); j.add_argument("--out", required=True)
    r = sub.add_parser("replay")
    r.add_argument("--labels", default=str(storage() / "pipeline_tuning/owner_labelled.jsonl"))
    r.add_argument("--work", default=str(storage() / "pipeline_tuning/live_h2h_field"))
    r.add_argument("--out", default=str(storage() / "pipeline_tuning/live_h2h_replay.json"))
    r.add_argument("--variant", choices=sorted(VARIANTS), default=DEFAULT_VARIANT)
    r.add_argument("--jobs", type=int, default=6); r.add_argument("--limit", type=int, default=0)
    c = sub.add_parser("check-replay"); c.add_argument("replay")
    a = ap.parse_args(argv)
    return {"judge": cmd_judge, "replay": cmd_replay, "check-replay": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
