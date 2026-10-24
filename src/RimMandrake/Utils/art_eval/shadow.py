#!/usr/bin/env python3
"""Shadow mode — the owner's quick look AFTER the pipeline has decided (skill `rimworld-art-evaluation`).

Owner, 2026-10-23: *"Use the system right now, but while we're evaluating it, build human review sheets AFTER the
process works for quick human feedback. Then we turn the human review off when it looks good."*

    python3 shadow.py build <run id>            # a gated, true-scale review sheet: one row per subject, the pipeline's
                                                 # decision + model verdicts as the row's question prefill, his
                                                 # KEEP / OVERRIDE buttons; plus <stem>.prereview.json from the run
    python3 shadow.py ingest <sheet.decisions.json> --run <run id>   # his answers -> shadow_log + criteria ledger
    python3 shadow.py status                    # per template: consecutive clean subjects vs the turn-off threshold

The sheet is built by art_sheet.py (never hand-rolled: rimworld-review-sheets Rule 1), so it carries the scale
panels and passes the 14-requirement gate. The prereview record is written from the pipeline's own look (looked_by
judge:<model ids>): every row was judged by a model that did not make the art.

Turning a template's shadow sheet off is the owner's call on the evidence `status` prints: `eligible_to_turn_off`
means the streak reached infrastructure/state/art_eval/settings.json's threshold, never that it is off.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ledger as LG  # noqa: E402
import policy as P  # noqa: E402

ROOT = P.ROOT
STATE = ROOT / "infrastructure/state/art_eval"
ART = ROOT / "src/RimMandrake/Utils/art"
KEY = "pipeline_check"
OPTIONS = [["keep", "KEEP the pipeline's decision"],
           ["should_accept", "OVERRIDE: the art is fine, accept it"],
           ["should_regen", "OVERRIDE: the art is bad, regenerate"],
           ["other", "OVERRIDE: something else (write a note)"],
           ["revert", "REVERT: put my kept version back (rows that replaced your kept art)"]]


def load_run(run_id: str) -> list:
    return [json.loads(l) for l in (STATE / "runs" / run_id / "decisions.jsonl").read_text().splitlines() if l.strip()]


def row_line(r: dict) -> tuple[str, str]:
    """(why, context) shown on his row: the decision, then each reviewer's verdict and blocking codes."""
    o, g = r.get("opus") or {}, r.get("gpt") or {}
    ob = [f["code"] for f in (o.get("detail") or {}).get("blocking", []) + (o.get("detail") or {}).get("gross", [])]
    why = ("REPLACED YOUR KEPT ART · " if r.get("replaces_kept") else "") + f"PIPELINE: {r['decision']}" + (f" (regen round {r['round']})" if r.get("round") else "")
    why += f" · Opus {o.get('band', '-')}" + (f": {', '.join(sorted(set(ob)))}" if ob else "")
    if g:
        why += f" · GPT {g['reply'].get('verdict')}" + (f", unsettled {', '.join(g['detail']['unsettled'])}" if g['detail']['unsettled'] else "")
    seen = "; ".join(f"{f['code']}: {f.get('seen', '')[:140]}" for f in (o.get("detail") or {}).get("blocking", [])[:3])
    ctx = f"judged candidate {r.get('candidate') or '-'} (image sha {next(iter(r['image_sha256'].values()), '')[:10]}); {seen}"
    return why, ctx


REF_KEYS = ("south", "east", "north", "west", "single")


def reference_map(recs: list) -> dict:
    """{subject: [candidate files]} the sheet must show beside the row: the judged facings and every assembled / flight /
    variants capture, read from the run's `source_files`. Candidates are usually NOT installed, so the installed-art
    columns never show them; the composite `scale` / `siblings` / `facings` panels are not candidates."""
    out = {}
    for r in recs:
        files = [f for k, f in (r.get("source_files") or {}).items()
                 if k in REF_KEYS or re.match(r"(assembled|flight|variants)_\d+$", k)]
        if files:
            out[r["subject"]] = files
    return out


def file_sha(path: str) -> str | None:
    import hashlib
    p = Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def judged_on_row(r: dict, installed_shas: set, reference_shas: set) -> bool:
    """True when a picture the pipeline judged is on the row: installed/found by name, or shown as a candidate column."""
    judged = {v for k, v in (r.get("source_sha256") or {}).items() if k in REF_KEYS}
    return not judged or bool(judged & (installed_shas | reference_shas))


def build(run_id: str, name: str | None = None) -> Path:
    recs = load_run(run_id)
    name = name or "art_eval_shadow_" + re.sub(r"[^a-z0-9_]", "_", run_id.lower())
    q = {"key": KEY, "label": "Did the pipeline decide right?",
         "explain": "The pipeline already decided each row (accept / regenerate / hold). KEEP agrees; an OVERRIDE "
                    "teaches the criteria ledger. A blank answer counts as nothing.",
         "options": OPTIONS, "rows": {}}
    for r in recs:
        why, ctx = row_line(r)
        q["rows"][r["subject"]] = {"prefill": "keep", "why": why, "context": ctx}
    qdir = STATE / "runs" / run_id
    qf = qdir / "shadow_question.json"
    qf.write_text(json.dumps(q, indent=1))
    lead = ("<p><b>Shadow review</b> of art-eval run <code>%s</code>: the pipeline has ALREADY decided every row "
            "(owner, 2026-10-23: <i>build human review sheets AFTER the process works for quick human feedback</i>). "
            "Each row shows its decision and the reviewers' blocking reasons; press KEEP or an OVERRIDE. Skipping a "
            "row changes nothing.</p>" % run_id)
    refs = reference_map(recs)
    reff = qdir / "shadow_references.json"
    reff.write_text(json.dumps(refs, indent=1))
    jobs = [f"{r['artpipe_job']}={r['subject']}" for r in recs if r.get("artpipe_job")]
    cmd = [sys.executable, str(ART / "art_sheet.py"), "--subjects", *[r["subject"] for r in recs], "--name", name,
           "--label", f"Art-eval shadow check — {run_id}", "--lead", lead, "--question", str(qf),
           "--reopen", *[r["subject"] for r in recs]] + (["--jobs", *jobs] if jobs else []) \
        + (["--references", str(reff)] if refs else [])
    p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=900)
    (qdir / "shadow_build.log").write_text(p.stdout[-4000:] + "\n--- stderr ---\n" + p.stderr[-4000:])
    if p.returncode:
        raise SystemExit(f"art_sheet.py exit {p.returncode}; see {qdir / 'shadow_build.log'}")
    sheet = ROOT / "Transient/biome_ffar" / f"{name}_sheet_{dt.date.today().isoformat()}.html"
    if not sheet.is_file():
        raise SystemExit(f"art_sheet.py succeeded but {sheet} is missing; see the build log")
    write_prereview(sheet, recs)
    return sheet


def write_prereview(sheet: Path, recs: list):
    """Fill <stem>.prereview.json from the pipeline's look: OK for a decided row, FLAG for held/escalated ones."""
    models = sorted({m for r in recs for k in ("opus", "gpt") for meta in (r["models"].get(k) or [])
                     for m in (meta.get("models_reported") or [meta.get("model_reported")]) if m})
    by = "judge:" + "+".join(models or ["UNMEASURED"])
    subprocess.run([sys.executable, str(ART / "prereview.py"), "init", str(sheet), "--by", by],
                   cwd=str(ROOT), capture_output=True, text=True, timeout=120, check=True)
    rp = sheet.with_name(sheet.stem + ".prereview.json")
    doc = json.loads(rp.read_text())
    shown = sheet_shas(sheet)
    by_subject = {r["subject"]: r for r in recs}
    for rid, row in doc["rows"].items():
        r = by_subject.get(rid)
        if not r:
            row.update(verdict="FLAG", note="row not in the art-eval run: the pipeline did not judge it")
            continue
        why, _ = row_line(r)
        ref_shas = {h for h in map(file_sha, reference_map([r]).get(rid, [])) if h}
        if not judged_on_row(r, shown.get(rid, set()), ref_shas):
            row.update(verdict="FLAG", note="the picture the pipeline judged is NOT on this row (the sheet shows what is "
                                            "installed / found by name, and the candidate files); " + why)
            continue
        flag = r["decision"] in ("ESCALATE", "HOLD_ERROR", "HOLD_KEPT", "HOLD_INPUT") or r.get("replaces_kept")
        row.update(verdict="FLAG" if flag else "OK", note=why)
    counts = {}
    for r in recs:
        counts[r["decision"]] = counts.get(r["decision"], 0) + 1
    doc.update(looked_by=by, caught="pipeline decided %s; nothing dropped" % ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    rp.write_text(json.dumps(doc, indent=1))


def sheet_shas(sheet: Path) -> dict:
    """{row id: every picture sha the sheet shows on that row}."""
    m = re.search(r'<script id="ITEMS"[^>]*>(.*?)</script>', sheet.read_text(), re.S)
    out = {}
    for it in json.loads(m.group(1).replace("<\\/", "</")) if m else []:
        shas = out.setdefault(str(it.get("id")), set())
        for g in it.get("graphics") or []:
            for c in g.get("cols") or []:
                shas |= set((c.get("faces") or {}).values())
    return out


def revert(rec: dict, apply: bool) -> list:
    """The one-click revert: put the owner-kept picture(s) back through the art ledger (art.py install, his
    shadow-sheet click as --by-card). Dry run unless apply. Returns [(argv, exit code, output tail)]."""
    out = []
    for argv in P.revert_commands(rec, f"shadow sheet {rec['subject']}: replaced your kept art → REVERT: put my kept version back"):
        cmd = [sys.executable] + argv[1:] + ([] if apply else ["--dry-run"])
        p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=300)
        out.append((cmd, p.returncode, (p.stdout + p.stderr)[-400:]))
    return out


def ingest(decisions_path: Path, run_id: str, apply_reverts: bool = False) -> list:
    """His answers -> shadow_log.jsonl rows; every OVERRIDE also becomes a criteria-ledger entry (source
    owner_override, his note as owner_said). Blank answers are skipped — silence is not agreement."""
    d = json.loads(Path(decisions_path).read_text())
    recs = {r["subject"]: r for r in load_run(run_id)}
    log = STATE / "shadow_log.jsonl"
    out = []
    for subj, row in (d.get("decisions") or {}).items():
        ans = (row.get("q") or {}).get(KEY)
        if not ans or subj not in recs:
            continue
        r = recs[subj]
        override = ans != "keep"
        # a blocking override: he says the pipeline let bad art through, or regenerated art he would keep
        blocking = (ans == "should_regen" and r["decision"] == "ACCEPT") or (ans == "should_accept" and r["decision"] in ("REGEN", "ESCALATE")) \
            or ans in ("other", "revert")
        e = {"at": row.get("at") or dt.datetime.now().astimezone().isoformat(timespec="seconds"), "run": run_id,
             "subject": subj, "template": r["template"], "pipeline_decision": r["decision"], "owner_answer": ans,
             "override": override, "blocking": blocking, "note": row.get("note", "")}
        if ans == "revert" and r.get("replaces_kept"):
            e["revert"] = [{"cmd": c, "rc": rc, "out": o} for c, rc, o in revert(r, apply_reverts)]
        with log.open("a") as fh:
            fh.write(json.dumps(e) + "\n")
        if override:
            e["ledger"] = LG.add(subj, r["template"], "owner_override",
                                 missed=f"pipeline {r['decision']}; owner {ans}", decision=r["decision"],
                                 owner_said=row.get("note") or f"(card answer: {ans})", run=run_id)
        out.append(e)
    return out


def status() -> list:
    s = P.load_settings()
    log = STATE / "shadow_log.jsonl"
    rows = [json.loads(l) for l in log.read_text().splitlines() if l.strip()] if log.is_file() else []
    return [P.shadow_status(t, rows, s) for t in P.TEMPLATES]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("run_id"); b.add_argument("--name")
    i = sub.add_parser("ingest"); i.add_argument("decisions"); i.add_argument("--run", required=True)
    i.add_argument("--apply-reverts", action="store_true", help="run art.py install for his REVERT clicks (default dry run)")
    sub.add_parser("status")
    a = ap.parse_args(argv)
    if a.cmd == "build":
        print(build(a.run_id, a.name))
    elif a.cmd == "ingest":
        for e in ingest(Path(a.decisions), a.run, a.apply_reverts):
            print(json.dumps(e))
    else:
        for st in status():
            print(json.dumps(st))
    return 0


if __name__ == "__main__":
    sys.exit(main())
