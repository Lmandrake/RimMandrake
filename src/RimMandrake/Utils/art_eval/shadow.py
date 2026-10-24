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


def row_id(r: dict) -> str:
    """The sheet row a record belongs to: the DEF. A plant/pool card is judged per picture under `<def>__<tag>`
    (RM_Ruskara__a, RM_AgariluxPrime__TheRot) but art_sheet --subjects takes defNames — handing it the card key
    finds no art ("no row has art", ART_EVAL_SHADOW_FIX_PLANT_KEPT_ROWS). Several cards of one def share one row."""
    return r["subject"].split("__", 1)[0]


def by_row(recs: list) -> dict:
    out = {}
    for r in recs:
        out.setdefault(row_id(r), []).append(r)
    return out


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
            out.setdefault(row_id(r), []).extend(f for f in files if f not in out.get(row_id(r), []))
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
    for rid, rs in by_row(recs).items():
        lines = [row_line(r) for r in rs]
        tag = lambda r: f"[{r['subject'].split('__', 1)[1]}] " if len(rs) > 1 and "__" in r["subject"] else ""
        q["rows"][rid] = {"prefill": "keep", "why": " || ".join(tag(r) + w for r, (w, _c) in zip(rs, lines)),
                          "context": " || ".join(tag(r) + c for r, (_w, c) in zip(rs, lines))}
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
    jobs = [f"{r['artpipe_job']}={row_id(r)}" for r in recs if r.get("artpipe_job")]
    rows_ = list(by_row(recs))
    cmd = [sys.executable, str(ART / "art_sheet.py"), "--subjects", *rows_, "--name", name,
           "--label", f"Art-eval shadow check — {run_id}", "--lead", lead, "--question", str(qf),
           "--reopen", *rows_] + (["--jobs", *jobs] if jobs else []) \
        + (["--references", str(reff)] if refs else [])
    p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=900)
    (qdir / "shadow_build.log").write_text(p.stdout[-4000:] + "\n--- stderr ---\n" + p.stderr[-4000:])
    if p.returncode:
        raise SystemExit(f"art_sheet.py exit {p.returncode}; see {qdir / 'shadow_build.log'}")
    sheet = built_sheet_path(p.stdout, name)
    if not sheet.is_file():
        raise SystemExit(f"art_sheet.py succeeded but {sheet} is missing; see the build log")
    write_prereview(sheet, recs)
    return sheet


def built_sheet_path(stdout: str, name: str, today: str | None = None) -> Path:
    """The sheet art_sheet.py says it wrote (its stdout JSON's "html"); the date-derived name only when that cannot be
    read — art_sheet dates the file itself, so a build that crosses midnight would otherwise miss it."""
    m = re.search(r'"html":\s*"([^"]+)"', stdout or "")
    if m:
        h = Path(m.group(1))
        return h if h.is_absolute() else ROOT / h
    return ROOT / "Transient/biome_ffar" / f"{name}_sheet_{today or dt.date.today().isoformat()}.html"


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
    groups = by_row(recs)
    for rid, row in doc["rows"].items():
        rs = groups.get(rid)
        if not rs:
            row.update(verdict="FLAG", note="row not in the art-eval run: the pipeline did not judge it")
            continue
        why = " || ".join(row_line(r)[0] for r in rs)
        missing = [r for r in rs
                   if not judged_on_row(r, shown.get(rid, set()), {h for h in map(file_sha, reference_map([r]).get(rid, [])) if h})]
        if missing:
            row.update(verdict="FLAG", note="the picture the pipeline judged is NOT on this row (the sheet shows what is "
                                            "installed / found by name, and the candidate files); " + why)
            continue
        flag = any(r["decision"] in ("ESCALATE", "HOLD_ERROR", "HOLD_KEPT", "HOLD_INPUT", "HOLD_CANVAS") or r.get("replaces_kept") for r in rs)
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


PICKED, POOLED, PURGED, RETIRED, NOT_PICKED = "OWNER_PICKED", "OWNER_POOLED", "OWNER_PURGED", "OWNER_RETIRED", "NOT_PICKED"
POSITIVE, NEGATIVE = (PICKED, POOLED), (PURGED, RETIRED)


def pick_labels(row: dict, snap_row: dict) -> dict:
    """{column letter: label} from his pick-one sheet row (SHADOW_INGEST_FIX_IGNORES_PICKS). On owner_escalations
    sheets he never clicks the shadow buttons: he picks a column, adds columns to a random pool, retires the live
    art or purges files. Picked/pooled = he wants that picture; purged/retired = he threw it out; anything else
    on the row = NOT_PICKED (no evidence either way: an unpicked render is not a rejection). `qPrefill` is the
    sheet's own default and never counts."""
    cols = snap_row.get("columns") or {}
    purge = set(row.get("purge") or [])
    pooled = {L for p in (row.get("pool") or {}).values() for L in (p.get("add") or [])}
    pooled -= {L for p in (row.get("pool") or {}).values() for L in (p.get("remove") or [])}
    retired = {L for Ls in (row.get("retire") or {}).values() for L in Ls}
    picked = {row["decision"]} if row.get("decision") in cols else set()
    picked |= {s.get("pick") for s in (row.get("slots") or {}).values() if s.get("pick") in cols}
    out = {}
    for L, faces in cols.items():
        shas = set((faces or {}).values())
        out[L] = (PICKED if L in picked else POOLED if L in pooled else PURGED if shas & purge
                  else RETIRED if L in retired else NOT_PICKED)
    return out


def answer_from_pick(label: str, decision: str):
    """The shadow answer his pick implies for a judged picture, or None when the pick says nothing about it."""
    regen = decision in ("REGEN", "ESCALATE")
    if label in POSITIVE:
        return "keep" if decision == "ACCEPT" else "should_accept" if regen else None
    if label in NEGATIVE:
        return "keep" if regen else "should_regen" if decision == "ACCEPT" else None
    return None


def facing_shas(rec: dict) -> set:
    """The judged picture's own files (facings / single), not the card's scale panel or references."""
    return {v for k, v in (rec.get("source_sha256") or {}).items() if k in REF_KEYS and v}


def match_column(rec: dict, snap_row: dict) -> str | None:
    """The sheet column showing the judged picture: every judged source sha on that column (one shared sha is not
    enough — a render that reuses the live north would otherwise match the live column)."""
    src = facing_shas(rec)
    if not src:
        return None
    hits = [L for L, faces in (snap_row.get("columns") or {}).items() if src <= set((faces or {}).values())]
    return hits[0] if len(hits) == 1 else None


def picks_for(d: dict, recs: list) -> list:
    """[(record, column, label, implied answer)] for every judged record whose picture is a column on his sheet."""
    snap = json.loads((ROOT / d["snapshot"]).read_text()) if d.get("snapshot") else {"rows": {}}
    groups = by_row(recs)
    out = []
    for subj, row in (d.get("decisions") or {}).items():
        srow = (snap.get("rows") or {}).get(subj)
        if not srow:
            continue
        labels = pick_labels(row, srow)
        purge = set(row.get("purge") or [])
        for r in groups.get(subj, []):
            L = match_column(r, srow)
            if L:
                out.append((r, L, labels[L], answer_from_pick(labels[L], r.get("decision", ""))))
            elif facing_shas(r) & purge:
                # a purged render is often no column at all (the sheet hides files already queued for purge)
                out.append((r, "-", PURGED, answer_from_pick(PURGED, r.get("decision", ""))))
    return out


def harvest(decision_paths: list, runs: list | None = None) -> list:
    """Owner-labelled judged pictures across runs: one row per (sheet, record) whose picture he picked, pooled,
    retired or purged — the tuning set for criteria changes. Labels are his; nothing here is a model guess."""
    rdir = STATE / "runs"
    recs = []
    for rid in runs or sorted(p.name for p in rdir.iterdir() if (p / "decisions.jsonl").is_file()):
        if rid.startswith(("regress_", "race_")):
            continue
        for r in load_run(rid):
            recs.append(dict(r, _run=rid))
    out = []
    for dp in decision_paths:
        d = json.loads(Path(dp).read_text())
        for r, L, label, ans in picks_for(d, recs):
            o, g = r.get("opus") or {}, r.get("gpt") or {}
            out.append({"sheet": d.get("sheetId"), "subject": r["subject"], "run": r["_run"], "candidate": r.get("candidate"),
                        "column": L, "label": label, "owner_wants": label in POSITIVE, "pipeline_decision": r.get("decision"),
                        "implied_answer": ans, "round": r.get("round"),
                        "severity": ((r.get("prompt_versions") or {}).get("severity") or {}).get("tag"),
                        "opus_band": o.get("band"), "opus_overall": (o.get("reply") or {}).get("overall"),
                        "opus_findings": [{k: f.get(k) for k in ("code", "confidence", "model_severity")} for f in (o.get("reply") or {}).get("findings") or []],
                        "gpt_verdict": (g.get("reply") or {}).get("verdict"), "gpt_outcome": g.get("outcome"),
                        "gpt_findings": [{k: f.get(k) for k in ("code", "confidence", "model_severity")} for f in (g.get("reply") or {}).get("findings") or []],
                        "gates": r.get("gates"), "image_sha256": r.get("image_sha256"), "source_files": r.get("source_files")})
    return out


def ingest(decisions_path: Path, run_id: str, apply_reverts: bool = False) -> list:
    """His answers -> shadow_log.jsonl rows; every OVERRIDE also becomes a criteria-ledger entry (source
    owner_override, his note as owner_said). Blank answers are skipped — silence is not agreement — unless he
    picked/pooled/retired/purged columns: then each judged picture on the row gets the answer his pick implies
    (answer_from_pick; SHADOW_INGEST_FIX_IGNORES_PICKS)."""
    d = json.loads(Path(decisions_path).read_text())
    recs = load_run(run_id)
    groups = by_row(recs)
    implied = {}
    for r, L, label, ans in picks_for(d, recs) if d.get("snapshot") else []:
        if ans:
            implied.setdefault(row_id(r), []).append((r, ans, f"picks: column {L} {label}"))
    known = {(e.get("subject"), e.get("run")) for e in LG.entries().values()}
    log = STATE / "shadow_log.jsonl"
    # re-ingesting the same answers must not log them twice: shadow_status counts rows, so a duplicate would grow the
    # clean streak (and re-file ledger entries, re-run reverts). A CHANGED answer is a new ruling and is logged.
    prior = [json.loads(l) for l in log.read_text().splitlines() if l.strip()] if log.is_file() else []
    logged = {ingest_key(p) for p in prior}
    # ...but a ruling first ingested with the default dry-run revert must still get its real revert from a later
    # --apply-reverts ingest. Applied reverts: a log row whose revert really ran clean, or a REVERTS record.
    rlog = STATE / "shadow_reverts.jsonl"
    applied = {ingest_key(p) for p in prior if revert_applied(p.get("revert"))}
    applied |= {tuple(json.loads(l)["key"]) for l in rlog.read_text().splitlines() if l.strip()} if rlog.is_file() else set()
    out = []
    for subj, row in (d.get("decisions") or {}).items():
        ans = (row.get("q") or {}).get(KEY)
        # a sheet row is a DEF (several plant cards share one); a sheet built before 2026-10-24 keyed it by card subject
        rs = groups.get(subj) or [r for g in groups.values() for r in g if r["subject"] == subj]
        if ans and rs:
            todo = [(r, ans, row.get("note", ""), False) for r in rs]
        else:
            todo = [(r, a, (f"{why}; {row['note']}" if row.get("note") else why), True) for r, a, why in implied.get(subj, [])]
        for r, ans, note, from_picks in todo:
            override = ans != "keep"
            # a blocking override: he says the pipeline let bad art through, or regenerated art he would keep
            blocking = (ans == "should_regen" and r["decision"] == "ACCEPT") or (ans == "should_accept" and r["decision"] in ("REGEN", "ESCALATE")) \
                or ans in ("other", "revert")
            e = {"at": row.get("at") or dt.datetime.now().astimezone().isoformat(timespec="seconds"), "run": run_id,
                 "subject": r["subject"], "template": r["template"], "pipeline_decision": r["decision"], "owner_answer": ans,
                 "override": override, "blocking": blocking, "note": note}
            if from_picks:
                e["source"] = "picks"
            key = ingest_key(e)
            wants_revert = ans == "revert" and bool(r.get("replaces_kept"))
            if key in logged:
                if not (wants_revert and apply_reverts and key not in applied):
                    continue
                # logged before with a dry-run revert: run the real one now; the ruling itself is not logged again
                e["revert"] = [{"cmd": c, "rc": rc, "out": o} for c, rc, o in revert(r, True)]
                if revert_applied(e["revert"]):
                    applied.add(key)
                    with rlog.open("a") as fh:
                        fh.write(json.dumps({"key": list(key), "at": e["at"], "revert": e["revert"]}) + "\n")
                out.append(e)
                continue
            logged.add(key)
            if wants_revert:
                e["revert"] = [{"cmd": c, "rc": rc, "out": o} for c, rc, o in revert(r, apply_reverts)]
                if revert_applied(e["revert"]):
                    applied.add(key)
            with log.open("a") as fh:
                fh.write(json.dumps(e) + "\n")
            # a pick-derived override on a subject already hand-filed for this run is not filed twice
            if override and not (from_picks and (r["subject"], run_id) in known):
                known.add((r["subject"], run_id))
                e["ledger"] = LG.add(r["subject"], r["template"], "owner_override",
                                     missed=f"pipeline {r['decision']}; owner {ans}", decision=r["decision"],
                                     owner_said=row.get("note") or (f"(sheet {note})" if from_picks else f"(card answer: {ans})"), run=run_id)
            out.append(e)
    return out


def revert_applied(rv) -> bool:
    """True when a revert record really ran (not --dry-run) and every command exited 0."""
    return bool(rv) and all(x.get("rc") == 0 and "--dry-run" not in (x.get("cmd") or []) for x in rv)


def ingest_key(e: dict) -> tuple:
    return (e.get("run"), e.get("subject"), e.get("owner_answer"), e.get("note") or "")


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
    h = sub.add_parser("harvest", help="owner-labelled judged pictures from his pick-one sheets (jsonl to --out)")
    h.add_argument("decisions", nargs="+"); h.add_argument("--runs", nargs="*"); h.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "harvest":
        rows = harvest(a.decisions, a.runs)
        Path(a.out).write_text("".join(json.dumps(r) + "\n" for r in rows))
        n = {}
        for r in rows:
            k = (r["label"], r["pipeline_decision"])
            n[k] = n.get(k, 0) + 1
        print(f"{len(rows)} labelled judged pictures -> {a.out}")
        for k, v in sorted(n.items()):
            print(f"  {k[0]:14} pipeline {k[1]:10} {v}")
        return 0
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
