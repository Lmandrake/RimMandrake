#!/usr/bin/env python3
"""canon_check.py — grade a finished artpipe render against its canon entry (or owner note) with a vision model.

Owner, 2026-10-04: *"PLEASE ensure that art regens look carefully and closely at the canon at every step,
especially those descriptions you just comissioned. Even for flora."* Jobs already ATTACH a canon image as
guidance (87e6995b6); nothing CHECKED the finished render against canon. This is that check.

WHAT IS GRADED
  canon job   — the job has a canon entry: `target_canon`, else the entry dir of a `canon_reference` image, else a
                `canon_references/<slug>/` path named in its prompt/style_notes, else art/subject.py's resolver on
                `target_def`. Each `## Must show` line of design/RimStarWars/canon_references/<slug>/description.md
                is graded pass / fail / na, with the entry's `## Visual brief`, `## Engine limits`, the canon images
                and the job's owner note as context.
  owner job   — no canon entry, but an owner note: the job's `owner_note` field (string or list), else the
                owner-attributed passage of its prompt (from the first sentence naming the owner / a rejection /
                a ruling, to the end). Each sentence is a check line.
  neither     — skipped, recorded as such.
  A line the render's facing cannot show (a face on a north view), or a non-visual line ("Not Star Wars IP"), is
  `na` and does not count. Verdict = FAIL iff any line fails; score "passed/graded".

ROUTE
  codex.exe exec, read-only sandbox, `--output-schema` JSON, images via `-i`, prompt on stdin, cwd + image copies in
  D:\\Luke\\dev\\_rmscratch\\codex\\canoncheck-*\\ (codex.exe fails from an ext4 cwd and hangs on \\\\wsl.localhost
  reads — same staging gpt_consult.py uses). Model: $ARTPIPE_CANON_MODEL, else gpt_consult's consult default
  (gpt-6.1-sol); effort high. In the daemon it runs on the job's leased codex home (artpiped's slot pool).

CLI (retroactive grading of finished renders; never requeues unless --requeue)
    python3 canon_check.py <job_id> [...]          grade these done/ (or failed/) renders
    python3 canon_check.py --since 2026-10-04T20:41  every done/ job created at/after this (UTC, job `created`)
    python3 canon_check.py --since ... --requeue   also requeue each FAIL once, corrections appended to its prompt
    flags: --force (re-grade already-graded) · -j N parallel graders (default 2) · --dry-run (resolve only)
  Verdict lands in done/<id>.manifest.json["canon_check"] and _artsrc/<id>/<id>.canon_check.json.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402

sys.path.insert(0, str(common.REPO_ROOT / "skills" / "generating-images" / "scripts"))

CANON_ROOT = common.CANON_ROOT
IMG_EXT = {".png", ".jpg", ".jpeg", ".webp"}
MAX_CANON_IMAGES = 4
DEFAULT_MODEL = os.environ.get("ARTPIPE_CANON_MODEL") or os.environ.get("CODEX_CONSULT_MODEL") or "gpt-6.1-sol"
DEFAULT_EFFORT = "high"
DEFAULT_TIMEOUT_S = 600
OWNER_MARK = re.compile(r"\bowner\b|\brejected\b|\bruled\b|\bpraised\b", re.I)
SLUG_IN_TEXT = re.compile(r"canon_references/([A-Za-z0-9_\-]+)/")
CORRECTIONS_HEAD = "CANON CORRECTIONS"

RESPONSE_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["lines", "summary"],
    "properties": {
        "lines": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["n", "verdict", "reason"],
            "properties": {"n": {"type": "integer"},
                           "verdict": {"type": "string", "enum": ["pass", "fail", "na"]},
                           "reason": {"type": "string"}}}},
        "summary": {"type": "string"}}}


class CanonCheckError(RuntimeError):
    pass


# ───────────────────────────────────────────────────────────── spec ──

def _sections(text: str) -> dict:
    return {m.group(1).strip().lower(): m.group(2).strip()
            for m in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", text, re.S | re.M)}


def must_show_lines(section: str) -> list[str]:
    out = []
    for raw in section.splitlines():
        m = re.match(r"^\s*(?:[-*]|\d+[.)])\s+(?:\[[ xX]\]\s*)?(.+?)\s*$", raw)
        if m:
            out.append(m.group(1))
        elif raw.strip() and out and raw.startswith((" ", "\t")):
            out[-1] += " " + raw.strip()  # wrapped continuation
    return out


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9'\"(])", text.strip())
    return [p.strip() for p in parts if len(p.strip()) > 3]


def owner_note_lines(job: dict) -> list[str]:
    """Explicit `owner_note` (str | list), else the owner-attributed tail of the prompt. Prior canon corrections
    appended by a retry are excluded — they are graded via the canon lines themselves."""
    note = job.get("owner_note")
    if isinstance(note, list):
        return [str(x).strip() for x in note if str(x).strip()]
    if isinstance(note, str) and note.strip():
        return _sentences(note)
    prompt = (job.get("prompt") or "").split(CORRECTIONS_HEAD)[0]
    sents = _sentences(prompt)
    for i, s in enumerate(sents):
        if OWNER_MARK.search(s):
            return sents[i:]
    return []


_WORLD = None
_WORLD_LOCK = threading.Lock()


def _slug_from_subject(target_def: str) -> str | None:
    global _WORLD
    try:
        sys.path.insert(0, str(HERE.parent / "art"))
        import subject  # noqa: E402
        with _WORLD_LOCK:  # daemon worker threads share one lazily-built World
            if _WORLD is None:
                _WORLD = subject.World()
            c = subject.resolve_canon(target_def, _WORLD, ())
        return c.get("slug") if c.get("match") != "none" else None
    except Exception:
        return None


def resolve_slug(job: dict, use_subject: bool = True) -> tuple[str | None, str]:
    s = job.get("target_canon")
    if s and (CANON_ROOT / s / "description.md").is_file():
        return s, "target_canon"
    for p in job.get("canon_reference") or []:
        try:
            rel = Path(p).resolve().relative_to(CANON_ROOT.resolve())
            if (CANON_ROOT / rel.parts[0] / "description.md").is_file():
                return rel.parts[0], "canon_reference dir"
        except (ValueError, IndexError):
            continue
    for field in ("prompt", "style_notes"):
        for m in SLUG_IN_TEXT.finditer(job.get(field) or ""):
            if (CANON_ROOT / m.group(1) / "description.md").is_file():
                return m.group(1), f"named in {field}"
    if use_subject and job.get("target_def"):
        s = _slug_from_subject(job["target_def"])
        if s and (CANON_ROOT / s / "description.md").is_file():
            return s, "subject.resolve_canon(target_def)"
    return None, ""


def gather(job: dict, use_subject: bool = True) -> dict | None:
    """-> spec {kind: canon|owner, slug, lines, brief, engine_limits, images, owner_note, facing, prompt}, or None."""
    owner = owner_note_lines(job)
    slug, how = resolve_slug(job, use_subject)
    base = {"na_marks": job.get("canon_na") or [], "na_reason": str(job.get("canon_na_reason") or "").strip(),
            "facing": job.get("facing"), "prompt": (job.get("prompt") or "")[:3000], "owner_note": owner}
    if slug:
        secs = _sections((CANON_ROOT / slug / "description.md").read_text(errors="replace"))
        lines = must_show_lines(secs.get("must show", ""))
        if lines:
            imgs = [p for p in (job.get("canon_reference") or []) if Path(p).is_file()]
            if not imgs:
                imgs = sorted(str(p) for p in (CANON_ROOT / slug).iterdir()
                              if p.suffix.lower() in IMG_EXT and not p.name.startswith("donor_"))
            return dict(base, kind="canon", slug=slug, slug_via=how, lines=lines,
                        brief=secs.get("visual brief", ""), engine_limits=secs.get("engine limits", ""),
                        images=imgs[:MAX_CANON_IMAGES])
    if owner:
        return dict(base, kind="owner", slug=None, slug_via="", lines=owner, brief="", engine_limits="", images=[])
    return None


# ──────────────────────────────────────────────────────────── grade ──

def resolve_na(spec: dict) -> dict[int, str]:
    """canon_na marks (1-based line number or exact/substring line text) -> {line index: reason}."""
    out = {}
    reason = spec.get("na_reason") or "owner marked n/a for this job"
    for m in spec.get("na_marks") or []:
        idx = None
        if isinstance(m, int) and not isinstance(m, bool):
            idx = m if 1 <= m <= len(spec["lines"]) else None
        else:
            t = str(m).strip().lower()
            for i, line in enumerate(spec["lines"], 1):
                if line.strip().lower() == t:
                    idx = i
                    break
            if idx is None:
                hits = [i for i, line in enumerate(spec["lines"], 1) if t and t in line.lower()]
                idx = hits[0] if len(hits) == 1 else None
        if idx is None:
            raise CanonCheckError(f"canon_na {m!r} matches no single Must-show line (have {len(spec['lines'])})")
        out[idx] = reason
    return out


def build_prompt(spec: dict) -> str:
    n_canon = len(spec["images"])
    p = ["You are a strict art director grading ONE finished RimWorld game sprite (image 1, the RENDER) against "
         "its acceptance checklist. Look carefully and closely at the render before judging each line."]
    if n_canon:
        p.append(f"Images 2..{n_canon + 1} are CANON REFERENCE images of the real subject (film stills, "
                 "illustrations, infobox art). They define WHAT the subject looks like — anatomy, colour, "
                 "proportion, features — not the art style.")
    p.append("The render is a small painted top-down three-quarter game sprite in a house painterly style on a "
             "transparent background. Do NOT fail a line for art style, rendering medium, scale or level of detail "
             "a sprite cannot carry. DO fail a line when the feature is missing, wrong (colour, count, shape), or "
             "contradicted.")
    if spec.get("facing"):
        p.append(f"This render is the {spec['facing'].upper()} facing (north = seen from behind, south = facing the "
                 "viewer, east/west = side profile). A line about something this facing cannot show is 'na', "
                 "with the reason.")
    p.append("A line that is not a visual requirement at all (provenance, IP, history) is 'na'.")
    if spec.get("engine_limits") and spec["engine_limits"].lower() not in ("none known", "none"):
        p.append("ENGINE LIMITS (never a failure):\n" + spec["engine_limits"])
    if spec.get("brief"):
        p.append("CANON VISUAL BRIEF:\n" + spec["brief"])
    if spec["kind"] == "canon" and spec.get("owner_note"):
        p.append("OWNER NOTE for this job (where it deliberately departs from canon, the owner note wins):\n"
                 + " ".join(spec["owner_note"]))
    p.append("THE JOB PROMPT the render was made from (context only):\n" + spec.get("prompt", ""))
    head = "MUST SHOW (canon acceptance lines)" if spec["kind"] == "canon" else "OWNER NOTE (acceptance lines)"
    p.append(head + " — grade every line, by its number:\n"
             + "\n".join(f"{i}. {line}" for i, line in enumerate(spec["lines"], 1)))
    na = resolve_na(spec)
    if na:
        p.append("Lines the owner marked N/A for this job (answer 'na' for them; do not judge): "
                 + ", ".join(str(i) for i in sorted(na)))
    p.append("Reply with JSON only: {\"lines\":[{\"n\":<line number>,\"verdict\":\"pass\"|\"fail\"|\"na\","
             "\"reason\":\"<one line: what you see in the render>\"}...],\"summary\":\"<one sentence>\"}.")
    return "\n\n".join(p) + "\n"


def codex_vision(prompt: str, images: list[Path], *, model: str = DEFAULT_MODEL, effort: str = DEFAULT_EFFORT,
                 timeout: int = DEFAULT_TIMEOUT_S, home: Path | None = None) -> str:
    """One codex.exe exec turn with images; returns the -o last-message text. Raises CanonCheckError."""
    import codex_image  # noqa: E402 — imported lazily so selftests never need codex.exe
    job = codex_image.CODEX_SCRATCH / f"canoncheck-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    job.mkdir(parents=True, exist_ok=True)
    try:
        staged = []
        for i, img in enumerate(images):
            dst = job / f"img{i}{Path(img).suffix.lower() or '.png'}"
            shutil.copyfile(img, dst)
            staged.append(dst)
        (job / "schema.json").write_text(json.dumps(RESPONSE_SCHEMA))
        (job / "prompt.md").write_text(prompt)
        answer = job / "answer.json"
        cmd = [str(codex_image.find_codex_cli()), "exec", "--sandbox", "read-only", "--skip-git-repo-check",
               "-o", codex_image.wsl_to_win(answer),
               "--output-schema", codex_image.wsl_to_win(job / "schema.json"),
               "-c", f'model_reasoning_effort="{effort}"']
        if model and model != "inherit":
            cmd += ["-m", model]
        for s in staged:
            cmd += ["-i", codex_image.wsl_to_win(s)]
        cmd += ["--", "-"]  # `-i` is variadic: terminate it, then read the prompt from stdin
        env = codex_image.child_env(home) if home is not None else None
        try:
            with open(job / "prompt.md", "rb") as fin, open(job / "codex.log", "wb") as log:
                rc = subprocess.run(cmd, cwd=str(job), stdin=fin, stdout=log, stderr=subprocess.STDOUT,
                                    timeout=timeout, env=env).returncode
        except subprocess.TimeoutExpired:
            rc = 124
        text = answer.read_text(errors="replace").strip() if answer.is_file() else ""
        if not text:
            tail = (job / "codex.log").read_text(errors="replace")[-600:] if (job / "codex.log").is_file() else ""
            raise CanonCheckError(f"no answer from codex (exit {rc}): {tail.strip()[-400:]}")
        return text
    finally:
        shutil.rmtree(job, ignore_errors=True)


def parse_answer(text: str, lines: list[str]) -> list[dict]:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise CanonCheckError(f"grader reply is not JSON: {text[:200]!r}")
    data = json.loads(m.group(0))
    by_n = {}
    for row in data.get("lines") or []:
        try:
            by_n[int(row["n"])] = row
        except (KeyError, TypeError, ValueError):
            continue
    out = []
    for i, line in enumerate(lines, 1):
        row = by_n.get(i)
        if row is None:
            raise CanonCheckError(f"grader skipped line {i}: {line[:80]!r}")
        v = str(row.get("verdict", "")).lower()
        if v not in ("pass", "fail", "na"):
            raise CanonCheckError(f"grader gave line {i} verdict {v!r}")
        out.append({"line": line, "verdict": v, "reason": str(row.get("reason", "")).strip()})
    return out, str(data.get("summary", "")).strip()


def grade(render: Path, spec: dict, vision=None, **vision_kw) -> dict:
    """-> verdict dict. `vision(prompt, images, **kw) -> str` defaults to codex_vision (tests pass a mock)."""
    vision = vision or codex_vision
    images = [Path(render)] + [Path(p) for p in spec["images"]]
    text = vision(build_prompt(spec), images, **vision_kw)
    rows, summary = parse_answer(text, spec["lines"])
    for i, why in resolve_na(spec).items():
        rows[i - 1] = dict(rows[i - 1], verdict="na", reason=f"n/a by canon_na: {why}", canon_na=True)
    graded = [r for r in rows if r["verdict"] != "na"]
    passed = sum(r["verdict"] == "pass" for r in graded)
    failed = [r for r in graded if r["verdict"] == "fail"]
    return {"status": "graded", "verdict": "FAIL" if failed else "PASS",
            "score": f"{passed}/{len(graded)}", "passed": passed, "graded": len(graded),
            "na": len(rows) - len(graded), "kind": spec["kind"], "slug": spec.get("slug"),
            "slug_via": spec.get("slug_via"), "lines": rows, "summary": summary,
            "model": vision_kw.get("model", DEFAULT_MODEL if vision is codex_vision else "mock"),
            "render": str(render), "canon_images": [str(p) for p in spec["images"]],
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}


def corrections_text(verdict: dict) -> str:
    fails = [r for r in verdict.get("lines", []) if r["verdict"] == "fail"]
    src = "canon entry" if verdict.get("kind") == "canon" else "owner note"
    body = " ".join(f"({i}) MUST: {r['line']} — the previous render failed this: {r['reason']}"
                    for i, r in enumerate(fails, 1))
    return (f" {CORRECTIONS_HEAD} (a vision check of the previous render of this job against its {src} failed "
            f"these lines; fix every one, keep everything else): {body}")


def with_corrections(job: dict, verdict: dict) -> dict:
    j = dict(job)
    j["prompt"] = (job.get("prompt") or "").split(f" {CORRECTIONS_HEAD}")[0] + corrections_text(verdict)
    j["canon_retry"] = int(job.get("canon_retry") or 0) + 1
    return j


# ────────────────────────────────────────────────────────────── CLI ──

def _find_job(job_id: str, done: Path, failed: Path):
    for d in (done, failed):
        jp = d / f"{job_id}.json"
        if jp.is_file():
            return d, jp
    return None, None


def check_one(job_id: str, *, done: Path, failed: Path, artsrc: Path, force: bool, dry_run: bool,
              vision=None, **vkw) -> dict:
    d, jp = _find_job(job_id, done, failed)
    if jp is None:
        return {"id": job_id, "status": "missing", "note": "no done/ or failed/ job file"}
    job = json.loads(jp.read_text())
    mp = d / f"{job_id}.manifest.json"
    manifest = json.loads(mp.read_text()) if mp.is_file() else {}
    png = artsrc / job_id / f"{job_id}.png"
    if not png.is_file():
        return {"id": job_id, "status": "no_render", "note": f"{png} absent"}
    prior = manifest.get("canon_check")
    if prior and prior.get("status") == "graded" and not force:
        return {"id": job_id, "status": "already", "check": prior, "job": job, "dir": d.name}
    spec = gather(job)
    if dry_run:
        return {"id": job_id, "status": "dry", "kind": spec and spec["kind"], "slug": spec and spec["slug"],
                "note": f"{spec['kind']} {spec['slug'] or ''} {len(spec['lines'])} lines" if spec else "nothing to grade"}
    if spec is None:
        rec = {"status": "skipped", "reason": "no canon entry and no owner note"}
    elif False:
        return {"id": job_id, "status": "dry", "kind": spec["kind"], "slug": spec["slug"], "n": len(spec["lines"])}
    else:
        try:
            rec = grade(png, spec, vision=vision, **vkw)
        except Exception as exc:  # noqa: BLE001 — a grader outage is recorded, never fatal to the sweep
            return {"id": job_id, "status": "error", "note": f"{type(exc).__name__}: {exc}"[:400]}
    if mp.is_file():
        manifest["canon_check"] = rec
        common.atomic_write_json(mp, manifest)
    common.atomic_write_json(png.parent / f"{job_id}.canon_check.json", rec)
    return {"id": job_id, "status": "checked", "check": rec, "job": job, "dir": d.name}


def requeue(job: dict, verdict: dict, pending: Path) -> Path:
    j = with_corrections(job, verdict)
    j["created"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    dst = pending / f"{job['id']}.json"
    if dst.exists():
        raise CanonCheckError(f"{dst} already pending")
    common.atomic_write_json(dst, j)
    return dst


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("job_ids", nargs="*")
    ap.add_argument("--since", help="ISO timestamp; grade done/ jobs whose `created` is at/after it")
    ap.add_argument("--match", help="regex the job id must match (with --since)")
    ap.add_argument("--requeue", action="store_true", help="requeue each FAIL once with corrections")
    ap.add_argument("--force", action="store_true", help="re-grade jobs already graded")
    ap.add_argument("--dry-run", action="store_true", help="resolve canon/owner specs only; no model calls")
    ap.add_argument("-j", "--jobs", type=int, default=2)
    ap.add_argument("-m", "--model", default=DEFAULT_MODEL)
    ap.add_argument("--effort", default=DEFAULT_EFFORT)
    ap.add_argument("--json-out", type=Path, help="write all results here")
    ap.add_argument("--done-dir", type=Path, default=common.DEFAULT_DONE)
    ap.add_argument("--failed-dir", type=Path, default=common.DEFAULT_FAILED)
    ap.add_argument("--pending-dir", type=Path, default=common.DEFAULT_PENDING)
    ap.add_argument("--artsrc-dir", type=Path, default=common.DEFAULT_ARTSRC)
    a = ap.parse_args(argv)
    ids = list(a.job_ids)
    if a.since:
        since = a.since.rstrip("Z")
        for jp in sorted(a.done_dir.glob("*.json")):
            if jp.name.endswith(".manifest.json"):
                continue
            try:
                created = str(json.loads(jp.read_text()).get("created") or "").rstrip("Z")
            except (OSError, ValueError):
                continue
            if created >= since and (not a.match or re.search(a.match, jp.stem)):
                ids.append(jp.stem)
    ids = list(dict.fromkeys(ids))
    if not ids:
        ap.error("no jobs: give job ids or --since")
    print(f"[canon_check] {len(ids)} job(s), model {a.model} effort {a.effort}, -j {a.jobs}", file=sys.stderr)
    kw = dict(done=a.done_dir, failed=a.failed_dir, artsrc=a.artsrc_dir, force=a.force, dry_run=a.dry_run,
              model=a.model, effort=a.effort)
    with ThreadPoolExecutor(max_workers=max(1, a.jobs)) as ex:
        results = list(ex.map(lambda i: check_one(i, **kw), ids))
    fails = []
    for r in results:
        c = r.get("check") or {}
        if c.get("status") == "graded":
            tag = f"{c['verdict']} {c['score']} ({c['kind']}{': ' + c['slug'] if c.get('slug') else ''})"
            if c["verdict"] == "FAIL":
                fails.append(r)
        elif c.get("status") == "skipped":
            tag = "SKIP no canon/owner note"
        else:
            tag = f"{r['status'].upper()} {r.get('note') or ''}".strip()
        print(f"{r['id']}: {tag}")
        for line in c.get("lines", []):
            if line.get("canon_na"):
                print(f"    - n/a {line['line'][:70]} — {line['reason'][:100]}")
            if line["verdict"] == "fail":
                print(f"    ✗ {line['line'][:90]} — {line['reason'][:140]}")
    if a.json_out:
        a.json_out.parent.mkdir(parents=True, exist_ok=True)
        a.json_out.write_text(json.dumps([{k: v for k, v in r.items() if k != "job"} for r in results], indent=1))
    graded = [r for r in results if (r.get("check") or {}).get("status") == "graded"]
    print(f"[canon_check] graded {len(graded)}, PASS {len(graded) - len(fails)}, FAIL {len(fails)}, "
          f"other {len(results) - len(graded)}", file=sys.stderr)
    if a.requeue:
        for r in fails:
            if int(r["job"].get("canon_retry") or 0) >= 1:
                print(f"  not requeued (already retried once): {r['id']}")
                continue
            try:
                print(f"  requeued: {requeue(r['job'], r['check'], a.pending_dir)}")
            except CanonCheckError as exc:
                print(f"  not requeued: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
