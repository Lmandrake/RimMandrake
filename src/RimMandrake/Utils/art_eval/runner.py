#!/usr/bin/env python3
"""Run the automated art-evaluation pipeline (skill `rimworld-art-evaluation`) over a set of subjects.

Owner, 2026-10-23: *"Opus scores first. If it says good, auto-accept. If it says really bad, regen. If it says
weak/need a call, send to GPT. If GPT says strong accept, accept, otherwise regen."* The guards (policy-decided
severity, targeted GPT concerns, reason-driven regen with a 3-round cap, owner-kept art held, catch items following
their living animal, every decision logged with prompt versions, model ids and image hashes) are in policy.py.

    python3 runner.py run --pilot RM_Huldu:C RM_HulduCatch:C:D --run-id e2e_20261023 --test
    python3 runner.py run --spec a.json b.json --run-id <id> [--record] [--file-regens]
    python3 runner.py regress                        # re-run the regression set on the current prompt versions
    python3 runner.py brief RM_Huldu                 # write the departures brief for an invented creature

Reviewers: Opus = `claude -p` (Read tool only, cwd = the card directory), model from ART_EVAL_OPUS_MODEL, else
ANTHROPIC_DEFAULT_OPUS_MODEL, else the CLI alias `opus` (resolved by the CLI from the same environment; nothing
here names an account). The model id actually used is read back from the CLI's `modelUsage` and logged.
GPT = src/RimMandrake/Utils/gpt_consult.py with the images attached (its default model, CODEX_CONSULT_MODEL
overrides; the model is read back from its own log line). Regen prompt edits: `claude -p` on the sonnet rung.

Outputs: cards + raw replies under the agent storage root (art_eval/runs/<run-id>/); the decision log, raw reviewer
replies, summary and regen jobs under infrastructure/state/art_eval/runs/<run-id>/ (committed). `--test` runs
never touch the regen-round counter or the delegated verdict files; `--record` writes
infrastructure/state/delegated/<date>/<subject>.json (delegation_policy §3).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cards as C  # noqa: E402
import policy as P  # noqa: E402

ROOT = P.ROOT
STATE = ROOT / "infrastructure/state/art_eval"
PROMPTS = P.REFS / "prompts"
GPT_CONSULT = ROOT / "src/RimMandrake/Utils/gpt_consult.py"


def storage_root() -> Path:
    """The machine's agent storage root (Lodestar agent_storage.py); fails by name if it cannot say."""
    env = os.environ.get("ART_EVAL_WORK")
    if env:
        return Path(env)
    r = subprocess.run([sys.executable, str(Path.home() / "dev/Lodestar/bin/lib/agent_storage.py")],
                       capture_output=True, text=True, timeout=30)
    if r.returncode or not r.stdout.strip():
        raise SystemExit("agent storage root unknown (agent_storage.py failed); set ART_EVAL_WORK")
    return Path(r.stdout.strip()) / "rimmandrake" / "art_eval"


def model_for(rung: str) -> str:
    return (os.environ.get(f"ART_EVAL_{rung.upper()}_MODEL") or os.environ.get(f"ANTHROPIC_DEFAULT_{rung.upper()}_MODEL")
            or rung)


def now():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


# ------------------------------------------------------------------ transports
def call_claude(prompt: str, cwd: Path, rung: str = "opus", timeout: int = 420, tools: str = "Read") -> tuple[str, dict]:
    model = model_for(rung)
    cmd = ["claude", "-p", "--output-format", "json", "--model", model]
    if tools:
        cmd += ["--allowed-tools", tools]
    t0 = time.time()
    try:
        r = subprocess.run(cmd, input=prompt, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "", {"error": f"claude -p timed out after {timeout}s", "model_requested": model}
    meta = {"model_requested": model, "seconds": round(time.time() - t0, 1)}
    try:
        env = json.loads(r.stdout)
    except ValueError:
        meta["error"] = (r.stderr or r.stdout or f"exit {r.returncode}")[-500:]
        return "", meta
    meta["models_reported"] = sorted((env.get("modelUsage") or {}).keys())
    meta["cost_usd"] = env.get("total_cost_usd")
    if env.get("is_error"):
        meta["error"] = str(env.get("result"))[:500]
    return env.get("result") or "", meta


def call_gpt(prompt: str, images: list, workdir: Path, timeout: int = 900) -> tuple[str, dict]:
    pf = workdir / "gpt_prompt.md"
    pf.write_text(prompt)
    out = workdir / "gpt_answer.md"
    cmd = [sys.executable, str(GPT_CONSULT), "--prompt-file", str(pf), "--out", str(out), "--timeout", str(timeout)]
    for im in images:
        cmd += ["-i", str(im)]
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 60, cwd=str(ROOT))
    except subprocess.TimeoutExpired:
        return "", {"error": "gpt_consult timed out"}
    m = re.search(r"model (\S+), job", r.stderr or "")
    meta = {"model_reported": m.group(1) if m else "UNMEASURED", "seconds": round(time.time() - t0, 1)}
    if r.returncode or not out.is_file():
        meta["error"] = (r.stderr or "")[-500:]
        return "", meta
    return out.read_text(), meta


# ------------------------------------------------------------------ prompt assembly
def codes_table(policy: dict, items: list) -> str:
    used = {i["code"] for i in items} | {c for c in policy["codes"] if c.startswith("X_")}
    rest = sorted(set(policy["codes"]) - used - {"X_INPUT"})
    lines = ["| code | means |", "|---|---|"]
    lines += [f"| `{c}` | {policy['codes'][c]['means']} |" for c in sorted(used - {"X_INPUT"}) + rest]
    return "\n".join(lines)


def image_list(card: dict) -> list:
    order = ["facings", "south", "east", "north", "west", "single", "scale", "wall_context", "living_reference", "siblings"]
    out = [card["panels"][k] for k in order if isinstance(card["panels"].get(k), str)]
    for many in ("flight", "variants", "assembled"):
        out += [card["panels"][k] for k in card["panels"].get(many, [])]
    return out


def opus_prompt(card: dict, tpl: dict, items: list, policy: dict, card_dir: Path) -> str:
    imgs = image_list(card)
    return "\n\n".join([
        (PROMPTS / "preamble.md").read_text(),
        "# Class module\n\n" + tpl["module_text"],
        "# Reason codes (use only these)\n\n" + codes_table(policy, items),
        "# The card\n\n" + (card_dir / "card.md").read_text(),
        "# Checklist — answer EVERY id\n\n" + "\n".join(f"- `{i['id']}` — {i['q']} (fails as `{i['code']}`)" for i in items),
        "# Images — Read every one\n\n" + "\n".join(f"- {card_dir / f}" for f in imgs),
        (PROMPTS / "opus_first_pass.md").read_text()])


def gpt_prompt(card: dict, tpl: dict, items: list, policy: dict, card_dir: Path, concerns: list, attached: list) -> str:
    return "\n\n".join([
        (PROMPTS / "preamble.md").read_text(),
        "# Class module\n\n" + tpl["module_text"],
        "# Reason codes (use only these)\n\n" + codes_table(policy, items),
        "# The card\n\n" + (card_dir / "card.md").read_text(),
        "# Attached images, in order\n\n" + "\n".join(f"{n}. {Path(f).name}" for n, f in enumerate(attached, 1)),
        "# Concerns from the first reviewer\n\n" + "\n".join(
            f"- **{k['id']}** `{k['code']}` at {k['where']}: {k['seen']}" for k in concerns),
        (PROMPTS / "gpt_targeted_second_look.md").read_text()])


def regen_prompt(card: dict, findings: list, previous_prompt: str | None) -> str:
    return "\n\n".join([
        (PROMPTS / "regen_prompt_edit.md").read_text(),
        "# Subject\n\n" + json.dumps({k: card.get(k) for k in ("subject", "label", "template", "module", "description",
                                                                 "departures", "depends_on", "size")}, indent=1),
        "# Previous generator prompt\n\n" + (previous_prompt or "(unknown — write the prompt from the description)"),
        "# Findings that made this render fail\n\n" + json.dumps(
            [{k: f.get(k) for k in ("code", "where", "seen", "fix")} for f in findings], indent=1)])


def prompt_versions(template: str) -> dict:
    v = {n: P.prompt_version(PROMPTS / f"{n}.md") for n in
         ("preamble", "opus_first_pass", "gpt_targeted_second_look", "regen_prompt_edit", "departures_brief")}
    v["template"] = P.prompt_version(P.REFS / "templates" / f"{template}.md")
    v["severity"] = P.prompt_version(P.REFS / "severity_policy.md")
    return v


def versions_key(v: dict) -> str:
    return "+".join(f"{x['tag']}#{x['sha'][:6]}" for _, x in sorted(v.items()))


# ------------------------------------------------------------------ reviewer steps (injectable for the selftest)
class Reviewers:
    def opus(self, prompt, card_dir):
        return call_claude(prompt, card_dir, "opus")

    def gpt(self, prompt, images, work):
        return call_gpt(prompt, images, work)

    def regen(self, prompt, work):
        return call_claude(prompt, work, "sonnet", timeout=300, tools="")


def ask_validated(ask, validate, retry_note):
    """One re-ask on a schema error. Returns (reply|None, raw_texts, metas, error)."""
    raws, metas, err = [], [], None
    for attempt in (1, 2):
        text, meta = ask("" if attempt == 1 else retry_note.format(err=err))
        raws.append(text); metas.append(meta)
        if meta.get("error"):
            err = meta["error"]
            continue
        try:
            return validate(P.parse_reply(text)), raws, metas, None
        except P.SchemaError as e:
            err = str(e)
    return None, raws, metas, err


# ------------------------------------------------------------------ the pipeline for one subject
def evaluate(spec: dict, card_dir: Path, rev: Reviewers, policy: dict, settings: dict, living: dict,
             rounds: dict) -> dict:
    tpl = P.load_template(spec["template"])
    card = C.build_card(spec, card_dir)
    facts = P.card_facts(card)
    items = P.checklist_for(tpl, card.get("module", ""), facts)
    rec = {"subject": card["subject"], "candidate": card.get("candidate"), "template": spec["template"],
           "module": card.get("module"), "at": now(), "card_sha": card["card_sha"],
           "image_sha256": card["image_sha256"], "source_sha256": card.get("source_sha256", {}),
           "artpipe_job": spec.get("artpipe_job"), "gates": card["gates"], "prompt_versions": prompt_versions(spec["template"]),
           "models": {}, "opus": None, "gpt": None, "regen": None, "reasons": []}
    living_dec = living.get(card.get("depends_on")) if card.get("depends_on") else None
    pre = P.pre_route(card, tpl, living_dec)
    if pre:
        rec["decision"] = pre
        rec["reasons"].append(f"missing panels {P.missing_panels(tpl, card.get('module', ''), card['panels'])}"
                              if pre == "HOLD_INPUT" else f"living {card['depends_on']} decision {living_dec}")
        return rec
    if card.get("depends_on") and living_dec is None:
        rec["reasons"].append(f"living {card['depends_on']} not decided in this run or the log — judged on its own")

    # 1. Opus first pass
    base = opus_prompt(card, tpl, items, policy, card_dir)
    (card_dir / "opus_prompt.md").write_text(base)
    reply, raws, metas, err = ask_validated(
        lambda extra: rev.opus(base + (("\n\n# Your previous reply was rejected\n\n" + extra) if extra else ""), card_dir),
        lambda r: P.validate_opus(r, items),
        "{err}. Return the JSON object exactly as specified, every checklist id answered.")
    rec["models"]["opus"] = metas
    (card_dir / "opus_raw.txt").write_text("\n\n=====\n\n".join(raws))
    if reply is None:
        rec.update(decision="HOLD_ERROR", reasons=[f"opus: {err}"])
        return rec
    band, od = P.opus_band(reply, items, facts, policy)
    rec["opus"] = {"band": band, "reply": reply, "detail": od}
    step = P.after_opus(band, card)
    rec["reasons"].append(f"opus band {band} (model said {reply.get('overall')}); blocking "
                          f"{[f['code'] for f in od['blocking'] + od['gross']]}; polish {[f['code'] for f in od['polish']]}"
                          + (f"; unreadable {od['incomplete']}" if od["incomplete"] else ""))
    gd = greply = None
    if step == "HOLD_KEPT":
        rec["decision"] = "HOLD_KEPT"
        if band != "GOOD":
            rec["reasons"].append("kept-but-flagged: owner-kept art the first reviewer did not pass — reaches him, never replaced")
        return rec
    if step == "GPT":
        concerns = P.concerns_from(od)
        attached = [card_dir / f for f in image_list(card)][:8]
        gp = gpt_prompt(card, tpl, items, policy, card_dir, concerns, attached)
        work = card_dir / "gpt"; work.mkdir(exist_ok=True)
        greply, graws, gmetas, gerr = ask_validated(
            lambda extra: rev.gpt(gp + (("\n\n# Your previous reply was rejected\n\n" + extra) if extra else ""), attached, work),
            lambda r: P.validate_gpt(r, concerns),
            "{err}. Return the JSON object exactly as specified.")
        rec["models"]["gpt"] = gmetas
        (card_dir / "gpt_raw.txt").write_text("\n\n=====\n\n".join(graws))
        if greply is None:
            rec.update(decision="HOLD_ERROR")
            rec["reasons"].append(f"gpt: {gerr}")
            return rec
        step, gd = P.gpt_outcome(greply, concerns, facts, policy, settings.get("min_refute_evidence_chars", 15))
        rec["gpt"] = {"concerns": concerns, "reply": greply, "detail": gd, "outcome": step}
        rec["reasons"].append(f"gpt {greply.get('verdict')}: unsettled {gd['unsettled']}, own blocking "
                              f"{[f['code'] for f in gd['blocking']]}")
    decision, rnd = P.cap_regen(step, rounds.get(card["subject"], 0), settings["max_regen_rounds"])
    rec["decision"], rec["round"] = decision, rnd
    if decision == "ESCALATE":
        rec["reasons"].append(f"still failing after {rnd} regen rounds — one line to the owner")
    if decision == "REGEN":
        fs = P.regen_findings(od, gd, greply)
        rp_prompt = regen_prompt(card, fs, spec.get("previous_prompt"))
        text, meta = rev.regen(rp_prompt, card_dir)
        rec["models"]["regen"] = meta
        try:
            rq = P.parse_reply(text)
            if not rq.get("prompt"):
                raise P.SchemaError("no prompt")
            rq["by"] = "model"
        except P.SchemaError as e:
            rq = P.deterministic_regen_prompt(card, fs)
            rq["fallback_why"] = str(e) if not meta.get("error") else meta["error"]
        rec["regen"] = {"findings": [f["code"] for f in fs], "request": rq}
    return rec


# ------------------------------------------------------------------ run
def history_decisions() -> dict:
    """Latest non-test decision per subject across committed runs (for catch dependencies across runs)."""
    out = {}
    for f in sorted((STATE / "runs").glob("*/decisions.jsonl")):
        meta = f.parent / "run.json"
        if meta.is_file() and json.loads(meta.read_text()).get("test"):
            continue
        for line in f.read_text().splitlines():
            r = json.loads(line)
            out[r["subject"]] = r["decision"]
    return out


def run(specs: list, run_id: str, rev: Reviewers | None = None, test: bool = False, record: bool = False,
        work_root: Path | None = None, state_root: Path | None = None, file_regens: bool = False) -> list:
    rev = rev or Reviewers()
    policy, settings = P.load_policy(), P.load_settings()
    work = (work_root or storage_root() / "runs") / run_id
    out = (state_root or STATE / "runs") / run_id
    work.mkdir(parents=True, exist_ok=True); out.mkdir(parents=True, exist_ok=True)
    rounds_file = STATE / "regen_rounds.json"
    rounds = {} if test else (json.loads(rounds_file.read_text()) if rounds_file.is_file() else {})
    living = {} if test else history_decisions()
    specs = sorted(specs, key=lambda s: s.get("module") == "catch")      # living animals first
    recs, done = [], set()
    if (out / "decisions.jsonl").is_file():                               # resume: a run id is appended to, never redone
        for line in (out / "decisions.jsonl").read_text().splitlines():
            r = json.loads(line)
            recs.append(r); done.add(r["subject"]); living[r["subject"]] = r["decision"]
    meta = json.loads((out / "run.json").read_text()) if (out / "run.json").is_file() else {
        "run_id": run_id, "test": test, "started": now(), "subjects": [],
        "versions_key": versions_key(prompt_versions("creature"))}
    meta["subjects"] = list(dict.fromkeys(meta["subjects"] + [s["subject"] for s in specs]))
    (out / "run.json").write_text(json.dumps(meta, indent=1))
    for s in specs:
        if s["subject"] in done:
            continue
        t0 = time.time()
        rec = evaluate(s, work / s["subject"], rev, policy, settings, living, rounds)
        rec["seconds"] = round(time.time() - t0, 1)
        living[s["subject"]] = rec["decision"]
        if rec["decision"] == "REGEN" and not test:
            rounds[s["subject"]] = rec["round"]
        recs.append(rec)
        with (out / "decisions.jsonl").open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"[art_eval] {s['subject']}: {rec['decision']} ({rec['seconds']}s) — {'; '.join(rec['reasons'])[:300]}",
              file=sys.stderr)
    if not test:
        rounds_file.write_text(json.dumps(rounds, indent=1, sort_keys=True))
    jobs = regen_jobs(recs, run_id)
    if jobs:
        (out / "regen_jobs.json").write_text(json.dumps(jobs, indent=1))
        if file_regens and not test:
            subprocess.run([sys.executable, str(ROOT / "src/RimMandrake/Utils/artpipe/fill_queue.py"),
                            "--input", str(out / "regen_jobs.json")], check=False, timeout=120)
    if record and not test:
        write_delegated(recs)
    (out / "summary.md").write_text(summary(recs, run_id, test))
    return recs


def regen_jobs(recs: list, run_id: str) -> list:
    """fill_queue.py rows (JSON art list) for every REGEN — filed only with --file-regens."""
    rows = []
    for r in recs:
        if r["decision"] != "REGEN":
            continue
        rq = r["regen"]["request"]
        rows.append({"id": f"arteval_{r['subject']}_r{r.get('round', 1)}", "rimflow_item_id": "ART_EVAL_PIPELINE_BUILD_OPUS_GRADES_FIRST",
                     "target_def": r["subject"], "prompt": rq["prompt"], "canvas_w": 1024, "canvas_h": 1024,
                     "facings": [] if r["module"] in ("catch", "ground_cover", "bush", "tree", "special") else ["south", "east", "north"],
                     "style_notes": "art_eval regen round %s; fixes: %s" % (r.get("round"), ", ".join(r["regen"]["findings"])),
                     "reference": "", "priority": 40, "source_run": run_id})
    return rows


def write_delegated(recs: list):
    day = dt.date.today().isoformat()
    d = ROOT / "infrastructure/state/delegated" / day
    d.mkdir(parents=True, exist_ok=True)
    for r in recs:
        (d / f"{r['subject']}.json").write_text(json.dumps({
            "judge_model": r["models"], "brief": "skills/rimworld-art-evaluation (prompt versions inside)",
            "subject": r["subject"], "decision": r["decision"], "reasons": r["reasons"],
            "prompt_versions": r["prompt_versions"], "image_sha256": r["image_sha256"]}, indent=1))


def summary(recs: list, run_id: str, test: bool) -> str:
    L = [f"# art_eval run {run_id}{' (TEST — nothing installed, no rounds counted)' if test else ''}", "",
         "| subject | cand | template/module | Opus band | GPT | decision | s | reasons |", "|---|---|---|---|---|---|---|---|"]
    for r in recs:
        g = r.get("gpt") or {}
        L.append(f"| {r['subject']} | {r.get('candidate') or ''} | {r['template']}/{r['module']} | "
                 f"{(r.get('opus') or {}).get('band', '-')} | {(g.get('reply') or {}).get('verdict', '-')} | **{r['decision']}** | "
                 f"{r.get('seconds', '')} | {'; '.join(r['reasons'])[:400]} |")
    esc = [r for r in recs if r["decision"] in ("ESCALATE", "HOLD_ERROR") or "kept-but-flagged" in " ".join(r["reasons"])]
    if esc:
        L += ["", "## One line each for the owner"] + [f"- {r['subject']}: {r['decision']} — {r['reasons'][-1]}" for r in esc]
    models = sorted({m for r in recs for k in r["models"].values() for meta in (k if isinstance(k, list) else [k])
                     for m in (meta.get("models_reported") or [meta.get("model_reported")] if meta else []) if m})
    L += ["", f"Models reported: {', '.join(models) or 'none'} · prompt versions: `{versions_key(recs[0]['prompt_versions']) if recs else ''}`"]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ departures brief
def write_brief(defname: str, rev_call=None) -> dict:
    spec = C.pilot_spec(defname + ":A") if ":" not in defname else C.pilot_spec(defname)
    prompt = (PROMPTS / "departures_brief.md").read_text() + "\n\n# Subject\n\n" + json.dumps(
        {"defName": spec["subject"], "label": spec.get("label"), "description": spec.get("description")}, indent=1)
    work = storage_root() / "briefs"; work.mkdir(parents=True, exist_ok=True)
    text, meta = (rev_call or (lambda p: call_claude(p, work, "opus", timeout=240, tools="")))(prompt)
    b = P.parse_reply(text)
    b.update({"by": meta.get("models_reported"), "prompt_version": P.prompt_version(PROMPTS / "departures_brief.md"),
              "at": now(), "source": "description only (no image)"})
    C.BRIEFS.mkdir(parents=True, exist_ok=True)
    (C.BRIEFS / f"{spec['subject']}.json").write_text(json.dumps(b, indent=1))
    return b


# ------------------------------------------------------------------ regression
def regress(rev: Reviewers | None = None) -> dict:
    """Re-run every regression row on the current prompt versions; a row passes when the decision lands in its
    expected class (ACCEPT vs not). Writes infrastructure/state/art_eval/regression_runs/<versions>.json."""
    rows = [json.loads(l) for l in (STATE / "regression.jsonl").read_text().splitlines() if l.strip()]
    specs = [C.pilot_spec(r["pilot"]) if r.get("pilot") else json.loads((ROOT / r["spec"]).read_text()) for r in rows]
    rid = "regress_" + dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    recs = {r["subject"]: r for r in run(specs, rid, rev=rev, test=True)}
    res = []
    for row, s in zip(rows, specs):
        d = recs[s["subject"]]["decision"]
        ok = (d == "ACCEPT") == (row["expect"] == "ACCEPT")
        res.append({"subject": s["subject"], "expect": row["expect"], "got": d, "pass": ok, "why": row.get("why")})
    out = {"versions_key": versions_key(prompt_versions("creature")), "run": rid, "at": now(),
           "passed": sum(r["pass"] for r in res), "total": len(res), "rows": res}
    (STATE / "regression_runs").mkdir(exist_ok=True)
    (STATE / "regression_runs" / f"{rid}.json").write_text(json.dumps(out, indent=1))
    return out


# ------------------------------------------------------------------ selftest support (mock reviewers)
def selftest_dry_run(tmp: Path) -> list:
    from PIL import Image, ImageDraw
    def sprite(p, h):
        im = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        ImageDraw.Draw(im).ellipse([60, 256 - h, 196, 250], fill=(120, 90, 60, 255))
        im.save(p)
        return str(p)
    imgs = {f: sprite(tmp / f"{f}.png", 150 + i) for i, f in enumerate(("south", "east", "north"))}
    imgs["scale"] = sprite(tmp / "scale.png", 100)
    base = {"template": "creature", "module": "walker", "invented": True, "description": "a beast", "images": imgs}
    specs = [dict(base, subject=n) for n in ("RM_DryGood", "RM_DryBad", "RM_DryWeak", "RM_DryKept")]
    specs[3]["owner_kept"] = True
    specs.append({"subject": "RM_DryBadCatch", "template": "creature", "module": "catch", "invented": True,
                  "depends_on": "RM_DryBad", "description": "dead beast",
                  "images": {"single": imgs["south"], "scale": imgs["scale"], "living_reference": {"south": imgs["south"]}}})
    tpl = P.load_template("creature")

    class Mock(Reviewers):
        def opus(self, prompt, card_dir):
            subj = re.search(r"^# (\S+) —", (card_dir / "card.md").read_text(), re.M).group(1)
            items = P.checklist_for(tpl, "walker", P.card_facts({"invented": True}))
            f = {"RM_DryBad": [{"code": "F_NORTH_FACE", "confidence": 0.95, "fix": "rear view"}],
                 "RM_DryWeak": [{"code": "F_NORTH_FACE", "confidence": 0.4, "fix": "rear view"}],
                 "RM_DryKept": [{"code": "STYLE_CARTOON", "confidence": 0.9}]}.get(subj, [])
            return json.dumps({"schema": "rm-art-eval/opus@v1", "subject": subj, "observed": {},
                               "checklist": {i["id"]: {"status": "ok", "seen": "-"} for i in items},
                               "findings": f, "overall": "good" if not f else "weak"}), {"models_reported": ["mock-opus"]}

        def gpt(self, prompt, images, work):
            return json.dumps({"schema": "rm-art-eval/gpt@v1", "verdict": "strong_accept", "findings": [],
                               "concerns": [{"id": "K1", "answer": "refuted",
                                             "evidence": "the north tile shows haunches and a tail, no eyes"}]}), {"model_reported": "mock-gpt"}

        def regen(self, prompt, work):
            return json.dumps({"schema": "rm-art-eval/regen@v1", "subject": "x", "edits": [], "invariants": [],
                               "reference": "keep", "prompt": "rear view, seen from behind"}), {"models_reported": ["mock-sonnet"]}

    return run(specs, "selftest", rev=Mock(), test=True, work_root=tmp / "work", state_root=tmp / "state")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--pilot", nargs="*", default=[], metavar="DEF:LETTER[:LIVING]")
    r.add_argument("--spec", nargs="*", default=[])
    r.add_argument("--run-id", required=True)
    r.add_argument("--test", action="store_true", help="no regen rounds counted, no delegated verdicts, no filing")
    r.add_argument("--record", action="store_true", help="write infrastructure/state/delegated/<date>/<subject>.json")
    r.add_argument("--file-regens", action="store_true", help="file the regen jobs with artpipe fill_queue.py")
    b = sub.add_parser("brief"); b.add_argument("defs", nargs="+")
    sub.add_parser("regress")
    a = ap.parse_args(argv)
    if a.cmd == "brief":
        for d in a.defs:
            print(d, json.dumps(write_brief(d))[:400])
        return 0
    if a.cmd == "regress":
        o = regress()
        print(f"regression {o['passed']}/{o['total']} on {o['versions_key']}")
        return 0 if o["passed"] == o["total"] else 1
    specs = [C.pilot_spec(x) for x in a.pilot] + [json.loads(Path(x).read_text()) for x in a.spec]
    recs = run(specs, a.run_id, test=a.test, record=a.record, file_regens=a.file_regens)
    for x in recs:
        print(f"{x['subject']}\t{x['decision']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
