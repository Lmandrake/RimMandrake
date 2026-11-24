#!/usr/bin/env python3
"""art_calibration.py - the art judge brief's planted cases (RIMMANDRAKE_BUILD_ART_BRIEF_CALIBRATION_NOTHING_TO_RUN).

The `model_check` of the `art_judge_brief` row in infrastructure/state/judge_calibration.json, on the pattern of
coverage_calibration.py: it stages each planted subject in a temp dir, puts it to a fresh Opus judge with the brief's
real text (design/RimMandrake/art_judge_brief.md, whole), and writes one {id, expect, got} row per case to
$RM_CALIBRATION_RESULTS. Every picture is art already made and already ruled by the owner (no art is generated):

  regress_<def>_<candidate>   the art-eval regression set (infrastructure/state/art_eval/regression.jsonl): ACCEPT rows
                              must pass, NOT_ACCEPT rows must be refused. Judged blind, as that set is: the subject's
                              def facts and description only, never the row's verdict or provenance, and shown as a
                              candidate (no keep on record), so E3 does not decide them. A row marked `taste` (a
                              verdict he gave for taste, in his words) is left out: no written line delivers it.
  kept_RM_Gawpsack_live       a picture the owner KEPT (criteria_ledger CL-030) that the art-eval pipeline banded
                              REALLY_BAD, staged with his keep -> must pass: checklist step 2, E3, a delegated call
                              never REDOes kept art (it says its concerns in the report)
  north_from_south_RM_DecayDrake_r2   owner-picked art whose north.png is replaced by its own south.png (a face where
                              the rear belongs) -> must be refused on C1 at north.png with a rear-view redraw as the
                              fix, never a rotation of the south (point 27); any other refusal is misdirected
  variant_RM_DecayDrake_p1..p3   the same owner-picked art altered offline (make_b2_planted_cases.py, named in each
                              case's `why`): p1 blends into the ground and p2 is dull with no clear shapes -> each must
                              be refused on B2 (owner card 2026-11-23); p3 is plain but legible -> must pass. The ids
                              and card names tell the judge nothing: the id is the item name in its prompt

What the judge is given per subject (the brief's "What you are given"): each facing picture (or the single plant
picture) at full resolution, the true-scale panel beside a vanilla human (scale.png), a 32 px/cell play-zoom copy of
each picture (drawSize x 32, made here by resizing), and subject.json: the def facts and description, his notes (none
in these cases), sibling keeps (none), donor or past art (none) and the keep record. Its answer is the brief's Output
file as structured output. Verdict to registry: no REDO and no refusal record, every verdict KEEP -> "pass"; a REDO or
a refusal record -> "refuse", but only as production would act on it: the contract block must pass
refusal_contract.check against the given (criteria = every lettered line of the brief, inputs = the staged files),
re-asked once on the same session as the brief promises, and every REDO must quote its line and say what it saw;
otherwise "refuse, malformed" or "refuse, invalid", which is not the planted refusal. UNSURE with no REDO is "unsure".

The pictures come from the art-eval regress run named in art_calibration.json (the agent storage root's
art_eval/runs/<source_run>, or $RM_ART_CAL_SOURCE), each pinned by sha256 there: a picture missing or off its pin
leaves its case out of the results (did not run: the brief stays UNTESTED), never a substitute. It spends (one Opus
judge per case, capped from outside by spend_watchdog at CASE_BUDGET_USD, plus at most one re-ask): it runs only from
`refusal_contract.py calibrate --model art_judge_brief`, never on a schedule.

    python3 src/RimMandrake/rimflow/art_calibration.py run          judge every case, print one line each
    python3 src/RimMandrake/rimflow/art_calibration.py stage <dir>  stage the cases there, judge none
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import refusal_contract as RC  # noqa: E402
import spend_watchdog  # noqa: E402  (the hard spend stop, from outside the agent; owner 2026-11-16)

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
BRIEF = "design/RimMandrake/art_judge_brief.md"
CONFIG = os.path.join(HERE, "art_calibration.json")
REGRESSION = "infrastructure/state/art_eval/regression.jsonl"
FAMILY = "art_judge_brief"
CLAUDE = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")  # systemd's PATH lacks ~/.local/bin
MODEL = "opus"
CASE_BUDGET_USD = 4
# budget: danger=a judge call that never returns holds the calibration; longest=134s (100 case sessions, agent transcripts, 14
# budget: days to 2026-11-24)
CASE_TIMEOUT_S = 1500
PX_PER_CELL = 32
FACT_KEYS = ("subject", "label", "template", "module", "body_plan", "tier", "invented", "canon", "description", "size",
             "canvas_px")
ROLE = {"south": "south facing, full resolution", "east": "east facing, full resolution (west mirrors it)",
        "north": "north facing, full resolution", "west": "west facing, full resolution",
        "single": "the plant's one picture, full resolution", "scale": "true-scale panel beside a vanilla human"}

CLAUSE_RE = re.compile(r"^- ([A-F]\d+a?)\. (.*)$")
REAR_RE = re.compile(r"\b(rear|back view|from behind|back of)\b")
ROTATE_RE = re.compile(r"rotat|180|\bflip")
# a rotation named only to forbid it ("Do not copy or flip south.png") is not a rotate fix: a ROTATE_RE hit counts unless
# a negation precedes it in its own sentence (RIMMANDRAKE_FIX_REAR_CHECK_NEGATED_FLIP_READ_AS_ROTATION)
SENTENCE_RE = re.compile(r"[.;:!?](?:\s|$)")
NEGATION_RE = re.compile(r"\b(not|never|no|don't|without|avoid|instead of)\b")


def rotate_fix(what):
    """-> True when the fix text asks for a rotation or flip of another facing (one not named only to forbid it)."""
    for s in SENTENCE_RE.split(str(what or "").lower()):
        m = ROTATE_RE.search(s)
        if m and not NEGATION_RE.search(s[:m.start()]):
            return True
    return False

SCHEMA = {"type": "object", "required": ["verdicts", "contract"], "properties": {
    "judge_model": {"type": "string"}, "brief": {"type": "string"}, "subject": {"type": "string"},
    "verdicts": {"type": "array", "items": {"type": "object", "required": ["picture", "verdict"], "properties": {
        "picture": {"type": "string"}, "facing": {"type": "string"}, "verdict": {"enum": ["KEEP", "REDO", "UNSURE"]},
        "notes": {"type": "string"}, "violated": {"type": "string"}, "quote": {"type": "string"},
        "seen": {"type": "string"}, "redo_brief": {"type": "string"}, "why": {"type": "string"}}}},
    "proposals": {"type": "array", "items": {"type": "string"}},
    "contract": {"type": "object", "required": ["item", "family", "sha", "passed", "refusals"], "properties": {
        "item": {"type": "string"}, "family": {"type": "string"}, "sha": {"type": "string"},
        "passed": {"type": "array", "items": {"type": "object", "required": ["clause", "evidence"], "properties": {
            "clause": {"type": "string"}, "evidence": {"type": "array", "items": {"type": "string"}}}}},
        "refusals": {"type": "array", "items": {"type": "object", "required": [
            "clause", "evidence", "observed", "would_pass", "smallest_fix", "criterion_verdict", "criterion_why"],
            "properties": {"clause": {"type": "string"}, "criterion_hash": {"type": "string"},
                           "evidence": {"type": "array", "items": {"type": "string"}}, "observed": {"type": "string"},
                           "would_pass": {"type": "string"},
                           "smallest_fix": {"type": "object", "required": ["what", "attainable", "cost"], "properties": {
                               "what": {"type": "string"}, "attainable": {"enum": ["yes", "no"]},
                               "cost": {"enum": list(RC.COSTS)}}},
                           "criterion_verdict": {"enum": list(RC.VERDICTS)}, "criterion_why": {"type": "string"},
                           "new_since": {"type": "string"}}}}}}}}


def config():
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def _spec(row):
    with open(os.path.join(REPO, row["spec"]), encoding="utf-8") as f:
        return json.load(f)


def card_of(row):
    """A regression row -> its card dir name in the regress run (runner.spec_key: <subject>__<candidate>)."""
    if row.get("pilot"):
        d, letter = row["pilot"].split(":")[:2]
        return "%s__%s" % (d, letter)
    s = _spec(row)
    return "%s__%s" % (s["subject"], s["candidate"])


def case_id(row):
    return "regress_" + card_of(row).replace("__", "_")


def cases():
    """The regression rows, then the planted cases of art_calibration.json. A row with `taste` (his words: a verdict he
    gave for taste, which no written line of the brief carries) is not a planted case: the brief judges only against
    what is written, so it cannot be expected to reach that verdict (his Durrok r2 and Gawpsack picks, owner 2026-11-17:
    "I was undoubtedly expressing style decisions."; C2 may refuse both on facing size)."""
    out = []
    with open(os.path.join(REPO, REGRESSION), encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                if str(r.get("taste") or "").strip():
                    continue
                out.append({"id": case_id(r), "expect": {"ACCEPT": "pass", "NOT_ACCEPT": "refuse"}[r["expect"]],
                            "card": card_of(r), "why": r.get("why")})
    return out + [dict(c) for c in config()["planted"]]


def planted():
    """The registry row's `planted` list (refusal_contract.judge_cases)."""
    return [{"id": c["id"], "expect": c["expect"]} for c in cases()]


def brief_text():
    with open(os.path.join(REPO, BRIEF), encoding="utf-8") as f:
        return f.read()


def criteria(text=None):
    """-> {clause id: its whole line} for every lettered constraint of the brief (continuation and sub-bullets
    included): the constraint lines the judge is given, so the contract's coverage check runs over all of them."""
    out, cur = {}, None
    for line in (text if text is not None else brief_text()).splitlines():
        m = CLAUSE_RE.match(line)
        if m:
            cur = m.group(1)
            out[cur] = m.group(2).strip()
        elif cur and line.startswith(" ") and line.strip():
            out[cur] += " " + line.strip()
        else:
            cur = None
    return out


def source_dir():
    env = os.environ.get("RM_ART_CAL_SOURCE")
    if env:
        return env
    r = subprocess.run([sys.executable, os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")],
                       # budget: danger=a hung agent_storage.py holds the calibration; never reached in the 14 days to
                       # budget: 2026-11-24; no record of its run
                       capture_output=True, text=True, timeout=30)
    if r.returncode or not r.stdout.strip():
        raise SystemExit("agent storage root unknown (agent_storage.py failed); set RM_ART_CAL_SOURCE")
    return os.path.join(r.stdout.strip(), "rimmandrake", "art_eval", "runs", config()["source_run"])


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _play_zoom(src, dst, draw):
    from PIL import Image
    w, h = (max(1, round(float(x) * PX_PER_CELL)) for x in draw)
    Image.open(src).convert("RGBA").resize((w, h), Image.LANCZOS).save(dst)


def stage_one(c, src, pins, d):
    """Copy one case's pinned pictures into d and write subject.json. -> None, or why it could not be staged."""
    card_dir = os.path.join(src, c["card"])
    pin = pins.get(c["card"])
    if not pin:
        return "no pins for %s" % c["card"]
    for f, h in pin.items():
        p = os.path.join(card_dir, f)
        if not os.path.exists(p):
            return "missing %s" % p
        if _sha(p) != h:
            return "sha off pin: %s" % p
    try:
        with open(os.path.join(card_dir, "card.json"), encoding="utf-8") as f:
            card = json.load(f)
    except (OSError, ValueError) as e:
        return "card.json: %s" % e
    os.makedirs(d)
    for f in pin:
        shutil.copyfile(os.path.join(card_dir, f), os.path.join(d, f))
    if c.get("plant") == "north_from_south":
        shutil.copyfile(os.path.join(d, "south.png"), os.path.join(d, "north.png"))
    facts = {k: card.get(k) for k in FACT_KEYS if card.get(k) is not None}
    facts["candidate"] = c["card"].split("__", 1)[1]
    pictures = {f[:-4]: f for f in sorted(pin) if f[:-4] in ROLE and f != "scale.png"}
    zoom = {}
    draw = (card.get("size") or {}).get("drawSize")
    if draw:
        for facing, f in pictures.items():
            zoom[facing] = "playzoom_%s.png" % facing
            _play_zoom(os.path.join(d, f), os.path.join(d, zoom[facing]), draw)
    facts.update(pictures=pictures, true_scale_panel="scale.png", play_zoom_32px_per_cell=zoom,
                 owner_kept=c["kept"] if c.get("plant") == "owner_kept" else "no keep on record: this is a candidate",
                 his_notes="none on this subject", sibling_keeps="none: no other live slot of this subject exists here",
                 donor_or_past_art="none", canon_entry=None if facts.get("invented") else "not on file")
    with open(os.path.join(d, "subject.json"), "w", encoding="utf-8") as f:
        json.dump(facts, f, indent=1, ensure_ascii=False)
    return None


def stage(root, source=None, pins=None):
    """Stage every case under root. -> [(case, dir or None, why not staged or None)]."""
    src = source or source_dir()
    pins = pins if pins is not None else config()["pins"]
    out = []
    for c in cases():
        d = os.path.join(root, c["id"])
        err = stage_one(c, src, pins, d)
        out.append((c, None if err else d, err))
    return out


def inputs(d):
    return sorted(f for f in os.listdir(d) if f.endswith(".png") or f == "subject.json")


def given(d):
    """What the launching window writes as `given`: the brief's constraint lines and the staged files."""
    h = hashlib.sha256()
    for f in inputs(d):
        h.update(f.encode())
        with open(os.path.join(d, f), "rb") as fh:
            h.update(fh.read())
    return {"criteria": criteria(), "inputs": inputs(d), "root": d, "sha": h.hexdigest()[:16]}


def prompt(d, item=None):
    g = given(d)
    role = {}
    for f in g["inputs"]:
        stem = f[:-4]
        role[f] = ("the def facts, description, keep record, his notes, sibling keeps and donor art" if f == "subject.json"
                   else "play-zoom copy at %d px/cell of %s" % (PX_PER_CELL, stem[9:]) if stem.startswith("playzoom_")
                   else ROLE.get(stem, "picture"))
    files = "\n".join("- %s: %s" % (f, role[f]) for f in g["inputs"])
    return ("You are the judge the brief below describes: a fresh agent, not the one that made the art. The subject's "
            "inputs are these files in your working directory:\n%s\n\nRead subject.json and look at every picture with "
            "the Read tool. Then answer with the brief's Output file as your structured output: `verdicts` (one per "
            "picture you judged), `proposals`, and its `contract` block with item %s, family %s and sha %s. The "
            "constraint lines you are given are every lettered line of the brief (A1 to F1): put each one in `passed` "
            "or in `refusals` (one record per refused constraint; a constraint that does not apply to this subject is "
            "passed, citing the file that shows it does not apply), cite as evidence only the file names listed above, "
            "and cite every one of them at least once. Leave `criterion_hash` empty: the window that launched you "
            "computes it.\n\n=== %s ===\n%s"
            % (files, json.dumps(item or os.path.basename(d)), json.dumps(FAMILY), json.dumps(g["sha"]), BRIEF,
               brief_text()))


def _refusing(so):
    v = [x for x in so.get("verdicts") or [] if isinstance(x, dict)]
    refs = [r for r in (so.get("contract") or {}).get("refusals") or [] if isinstance(r, dict)]
    return [x for x in v if x.get("verdict") == "REDO"], refs, v


def contract_errors(so, g):
    """refusal_contract.check on the answer's contract block, criterion hashes filled in as the window does."""
    con = json.loads(json.dumps((so or {}).get("contract") or {}))
    for r in con.get("refusals") or []:
        if isinstance(r, dict) and r.get("clause") in g["criteria"]:
            r["criterion_hash"] = RC.criterion_hash(g["criteria"][r["clause"]])
    return RC.check(con, g)


def outcome(route, so, errs):
    """-> "pass", "unsure", "refuse", or a refusal production would not act on: "refuse, malformed" (the record failed
    the contract after its re-ask), "refuse, invalid" (a REDO without its quoted line or what was seen) or "refuse,
    misdirected (<clauses>)" on the north case (no C1 refusal at north.png whose fix is a rear-view redraw) or on a B2
    case (no B2 refusal)."""
    redo, refs, v = _refusing(so or {})
    if not redo and not refs:
        return "pass" if v and all(x.get("verdict") == "KEEP" for x in v) else "unsure"
    if errs:
        return "refuse, malformed"
    if any(not (x.get("violated") and x.get("quote") and x.get("seen")) for x in redo):
        return "refuse, invalid"
    if route == "north_rear":
        ok = any(r.get("clause") == "C1" and any("north" in str(e) for e in r.get("evidence") or [])
                 and REAR_RE.search(str((r.get("smallest_fix") or {}).get("what", "")).lower())
                 and not rotate_fix((r.get("smallest_fix") or {}).get("what")) for r in refs)
    elif route == "b2":
        ok = any(r.get("clause") == "B2" for r in refs)
    else:
        ok = True
    if not ok:
        return "refuse, misdirected (%s)" % ", ".join(sorted({str(r.get("clause")) for r in refs}) or ["no record"])
    return "refuse"


def default_runner(argv, cwd):
    p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=CASE_TIMEOUT_S)
    return p.returncode, p.stdout


def _tokens(res):
    try:
        import role_launch
        return role_launch.run_tokens(res, MODEL)
    except Exception as e:  # noqa: BLE001 - spend is reported, never guessed: an unweighable run says why
        return "UNMEASURED: %s: %s" % (type(e).__name__, e)


def _call(argv, d, runner):
    """-> (structured output or None, the result dict, error or None)."""
    try:
        code, out = runner(spend_watchdog.wrap(argv, CASE_BUDGET_USD), d)   # the cap from outside: never told its spend
        res = json.loads(out or "null")
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return None, {}, "%s: %s" % (type(e).__name__, e)
    res = res if isinstance(res, dict) else {}
    so = res.get("structured_output")
    if code != 0 or not isinstance(so, dict):
        return None, res, "no well-formed answer (exit %s)" % code
    return so, res, None


def judge(c, d, runner=None):
    """One fresh Opus judge on one staged case, its refusal record checked as production checks it. -> (got, detail)."""
    runner = runner or default_runner
    g = given(d)
    base = [CLAUDE, "-p", None, "--model", MODEL, "--output-format", "json",
            "--json-schema", json.dumps(SCHEMA, separators=(",", ":")), "--dangerously-skip-permissions",
            "--allowed-tools", "Read",
            "--name", "ART CALIBRATION %s" % c["id"]]
    argv = list(base)
    argv[2] = prompt(d, c["id"])
    so, res, err = _call(argv, d, runner)
    detail = {"cost_usd": [res.get("total_cost_usd")], "weighted_tokens": [_tokens(res)]}
    if err:
        detail["error"] = err
        return None, detail
    errs = []
    redo, refs, _v = _refusing(so)
    if redo or refs:
        errs = contract_errors(so, g)
        if errs and res.get("session_id"):   # the brief: a malformed record is re-asked once with its errors
            argv = list(base) + ["--resume", res["session_id"]]
            argv[2] = ("refusal_contract.py refused your record:\n%s\nAnswer again with the whole corrected file."
                       % "\n".join("- " + e for e in errs[:40]))
            so2, res2, err2 = _call(argv, d, runner)
            detail["cost_usd"].append(res2.get("total_cost_usd"))
            detail["weighted_tokens"].append(_tokens(res2))
            detail["reasked"] = errs[:12]
            if not err2:
                so = so2
                redo, refs, _v = _refusing(so)
                errs = contract_errors(so, g) if (redo or refs) else []
    got = outcome(c.get("route"), so, errs)
    detail.update(verdicts=[{k: str(x.get(k))[:160] for k in ("picture", "verdict", "violated", "seen", "why", "notes")
                             if x.get(k)} for x in so.get("verdicts") or [] if isinstance(x, dict)][:8],
                  refusals=[{"clause": r.get("clause"), "evidence": r.get("evidence"),
                             "fix": str((r.get("smallest_fix") or {}).get("what"))[:200]} for r in refs][:8],
                  errors=errs[:12], proposals=[str(p)[:200] for p in so.get("proposals") or []][:4])
    return got, detail


def run():
    with tempfile.TemporaryDirectory(prefix="rm-art-cal-") as root:
        staged = stage(root)
        ready = [(c, d) for c, d, _e in staged if d]
        with ThreadPoolExecutor(max(1, len(ready))) as ex:
            got = list(ex.map(lambda s: judge(*s), ready))
    rows = [dict({"id": c["id"], "expect": c["expect"], "got": g}, **det) for (c, _d), (g, det) in zip(ready, got)]
    path = os.environ.get(RC.RESULTS_ENV)
    if path:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"cases": rows}, f, indent=1)
    for c, _d, e in staged:
        if e:
            print("%-36s expect %-6s NOT STAGED (did not run): %s" % (c["id"], c["expect"], e))
    for r in rows:
        print("%-36s expect %-6s got %-6s %s" % (r["id"], r["expect"], r["got"], r.get("error") or "; ".join(
            "%s %s" % (x.get("clause"), x.get("fix", "")[:80]) for x in r.get("refusals") or []) or "KEEP"))
    return 0 if all(r["got"] is not None for r in rows) else 1


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["run"]:
        return run()
    if argv[:1] == ["stage"] and len(argv) == 2:
        for c, d, e in stage(argv[1]):
            print(c["id"], c["expect"], d or "NOT STAGED: %s" % e)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
