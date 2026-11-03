#!/usr/bin/env python3
"""binding_sheet.py — the binding review sheet for renders no mechanical step could bind (ART_SUBJECT_RESOLVER_1 §5.3 step 4).

    python3 binding_sheet.py build [--index PATH] [--out DIR]     worklist JSON + HTML sheet + decisions skeleton
    python3 binding_sheet.py enact DECISIONS.json --by owner|agent [--why "..."] [--dry-run]

`build` reads the derived subject index (render_subjects.py; rebuilt when --index is absent) and puts every render whose
resolution is `unresolved` or `ambiguous` on one row per job FAMILY (all facings of one job are one picture of one
subject): its thumbnails, the candidate defs the token match found, and the canon entry each candidate — or a family
token — resolves to. The sheet is a picker: per row, a candidate, a typed defName, or "no subject" (a mock, a concept
scene, a texture part no def draws, a creature that does not exist yet). Its Export button writes the decisions file.

`enact` turns a decisions file into art-ledger events, the only write:
  * {"decision": "bind", "subject": "<defName>"}  -> a `binding` for every render of the family. Confidence follows the
    spec: an OWNER pick is `bound`; an AGENT pick is `name-matched` (only an owner click or byte evidence gives `bound`)
    and its evidence starts "delegated: art-binding" (delegation_policy, owner 2026-10-22). The defName must be a def
    the resolver can see — never a guess.
  * {"decision": "no-subject", "reason": "..."}   -> a `no_subject` event per render: it leaves the open list, and no
    sheet or census ever shows it as some def's picture.
  * {"decision": "skip"} or no entry               -> nothing; the row stays open for the next sheet.
Event ids are deterministic, so a re-run writes nothing new.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402
import subject as S  # noqa: E402

OPEN = ("unresolved", "ambiguous")
DECISIONS = ("bind", "no-subject", "skip")
SHEET_ID = "binding_sheet"
MAX_THUMBS = 4


def open_families(entries: dict) -> dict:
    """family -> {"renders": [{sha, job}], "resolution", "candidates", "evidence"} for every open render."""
    fam = {}
    for key, r in sorted(entries.items()):
        if r.get("resolution") not in OPEN:
            continue
        sha, job = key.split(":", 1)
        row = fam.setdefault(r["family"], {"renders": [], "resolution": r["resolution"], "candidates": set(),
                                           "evidence": r.get("evidence", "")})
        row["renders"].append({"sha": sha, "job": job})
        row["candidates"].update(r.get("subjects") or [])
        if r["resolution"] == "ambiguous":
            row["resolution"] = "ambiguous"
    for row in fam.values():
        row["candidates"] = sorted(row["candidates"])
    return fam


def canon_for(family: str, candidates: list, w: "S.World") -> list:
    """Canon entries a reviewer should see: each candidate's resolved entry, else any family token naming a canon dir."""
    out, seen = [], set()
    for c in candidates:
        try:
            r = S.resolve_canon(c, w)
        except Exception as e:  # a resolver failure is shown on the row, never swallowed into "no canon"
            out.append({"for": c, "slug": None, "match": "error", "evidence": f"{type(e).__name__}: {e}"})
            continue
        if r.get("slug") and r["slug"] not in seen:
            seen.add(r["slug"])
            out.append({"for": c, "slug": r["slug"], "match": r["match"], "evidence": r.get("evidence", ""),
                        "images": r.get("images", [])[:2]})
    if not out:
        for k, slug in sorted(w.canon_dirs.items()):
            if len(k) >= S.MIN_KEY and slug not in seen and S.token_match(family, k):
                seen.add(slug)
                p = w.canon_payload(slug)
                out.append({"for": family, "slug": slug, "match": "family-token", "evidence": f"job family token {k!r}",
                            "images": p["images"][:2]})
    return out


def worklist(entries: dict, w: "S.World") -> list:
    rows = []
    for fam, row in sorted(open_families(entries).items()):
        rows.append({"id": fam, "family": fam, "resolution": row["resolution"], "evidence": row["evidence"],
                     "renders": row["renders"], "candidates": row["candidates"],
                     "canon": canon_for(fam, row["candidates"], w)})
    return rows


PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>Binding review — {n} render families</title>
<style>body{{font:14px sans-serif;margin:16px;background:#1d1d1d;color:#ddd}} .row{{border-top:1px solid #444;padding:8px 0;
display:flex;gap:12px}} .th img{{width:96px;height:96px;object-fit:contain;background:#555;margin-right:4px}}
.meta{{flex:1}} code{{color:#9cf}} .canon img{{width:64px;height:64px;object-fit:contain}} label{{margin-right:10px}}</style>
</head><body><h1>Binding review — {n} render families, {r} renders</h1>
<p>Pick what each render is a picture of. A candidate, a typed defName, or <b>no subject</b> (mock, concept, texture part,
creature not in the game). Skipped rows stay open. Export writes <code>{sid}.decisions.json</code>; enact with
<code>binding_sheet.py enact</code>.</p><button onclick="exp()">Export decisions</button>
{rows}
<script>const ITEMS={items};
function exp(){{const d={{}};for(const id of ITEMS){{const f=document.querySelector('[data-id="'+CSS.escape(id)+'"]');
const c=f.querySelector('input[type=radio]:checked');if(!c)continue;let v=c.value;
if(v==='__typed'){{const t=f.querySelector('input[type=text]').value.trim();if(!t)continue;d[id]={{decision:'bind',subject:t}};}}
else if(v==='__none'){{d[id]={{decision:'no-subject',reason:(f.querySelector('.why').value||'reviewer: no subject')}};}}
else if(v==='__skip'){{d[id]={{decision:'skip'}};}} else d[id]={{decision:'bind',subject:v}};}}
const o={{sheetId:'{sid}',reviewStatus:{{state:'ruled'}},decisions:d}};
const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(o,null,1)],{{type:'application/json'}}));
a.download='{sid}.decisions.json';a.click();}}</script></body></html>"""


def render_html(rows: list, thumbs: dict) -> str:
    out = []
    for row in rows:
        i = html.escape(row["id"], quote=True)
        th = "".join(f'<img src="{html.escape(thumbs[r["sha"]])}" title="{html.escape(r["job"])}">'
                     for r in row["renders"][:MAX_THUMBS] if r["sha"] in thumbs)
        opts = "".join(f'<label><input type="radio" name="{i}" value="{html.escape(c, quote=True)}"> <code>{html.escape(c)}</code></label>'
                       for c in row["candidates"])
        canon = "".join(f'<span class="canon">{html.escape(c["slug"] or "")} [{html.escape(c["match"])}] '
                        + "".join(f'<img src="{html.escape(thumbs.get(p, ""))}">' for p in c.get("images", []) if p in thumbs)
                        + "</span> " for c in row["canon"]) or "none found"
        out.append(f'<div class="row" data-id="{i}"><div class="th">{th}</div><div class="meta"><b>{html.escape(row["family"])}</b> '
                   f'({len(row["renders"])} render(s), {row["resolution"]}) — {html.escape(row["evidence"])}<br>'
                   f'{opts}<label><input type="radio" name="{i}" value="__typed"> defName <input type="text" size="28"></label>'
                   f'<label><input type="radio" name="{i}" value="__none"> no subject <input class="why" size="24" placeholder="why"></label>'
                   f'<label><input type="radio" name="{i}" value="__skip"> skip</label><br>canon: {canon}</div></div>')
    n_r = sum(len(r["renders"]) for r in rows)
    return PAGE.format(n=len(rows), r=n_r, sid=SHEET_ID, rows="\n".join(out), items=json.dumps([r["id"] for r in rows]))


def build(index: Path | None, out_dir: Path) -> dict:
    import render_subjects as RS
    w = S.World()
    res = json.loads(index.read_text()) if index else RS.build(w)
    rows = worklist(res["entries"], w)
    out_dir.mkdir(parents=True, exist_ok=True)
    img = out_dir / "img"
    img.mkdir(exist_ok=True)
    thumbs, missing = {}, 0
    for row in rows:
        for r in row["renders"][:MAX_THUMBS]:
            p = L.store_path(r["sha"])
            if p.exists():
                shutil.copyfile(p, img / p.name)
                thumbs[r["sha"]] = f"img/{p.name}"
            else:
                missing += 1
        for c in row["canon"]:
            for k, src in enumerate(c.get("images", [])):
                sp = Path(src)
                if sp.exists():
                    dst = img / f"canon_{c['slug']}_{k}{sp.suffix.lower()}"
                    shutil.copyfile(sp, dst)
                    thumbs[src] = f"img/{dst.name}"
    (out_dir / f"{SHEET_ID}.worklist.json").write_text(json.dumps(rows, indent=1))
    (out_dir / f"{SHEET_ID}.html").write_text(render_html(rows, thumbs))
    dec = out_dir / f"{SHEET_ID}.decisions.json"
    if not dec.exists():
        dec.write_text(json.dumps({"sheetId": SHEET_ID, "reviewStatus": {"state": "prefill"}, "decisions": {}}, indent=1))
    return {"families": len(rows), "renders": sum(len(r["renders"]) for r in rows),
            "ambiguous": sum(r["resolution"] == "ambiguous" for r in rows), "thumbs_missing_from_store": missing,
            "sheet": str(out_dir / f"{SHEET_ID}.html")}


def enact(decisions: dict, rows: list, by: str, why: str | None, known_defs, dry_run: bool = False) -> dict:
    """Validate every decision first; write nothing unless all are valid. Returns counts and refusals."""
    if by not in ("owner", "agent"):
        raise ValueError("--by must be owner or agent")
    if by == "agent" and not why:
        raise ValueError("an agent pick needs --why (logged as 'delegated: art-binding — <why>')")
    by_id = {r["id"]: r for r in rows}
    bad, plan = [], []
    for rid, d in sorted((decisions.get("decisions") or {}).items()):
        dec = (d or {}).get("decision")
        if rid not in by_id:
            bad.append(f"{rid}: not a row of this worklist")
        elif dec not in DECISIONS:
            bad.append(f"{rid}: decision {dec!r} not one of {DECISIONS}")
        elif dec == "bind" and d.get("subject") not in known_defs:
            bad.append(f"{rid}: subject {d.get('subject')!r} is not a def the resolver can see")
        elif dec == "no-subject" and not (d.get("reason") or "").strip():
            bad.append(f"{rid}: no-subject needs a reason")
        elif dec != "skip":
            plan.append((by_id[rid], d))
    if bad:
        return {"written": 0, "refused": bad}
    conf = "bound" if by == "owner" else "name-matched"
    src = "owner pick on binding sheet" if by == "owner" else f"delegated: art-binding — {why}"
    wr = L.Writer()
    n0 = len(wr.known)
    planned = 0
    for row, d in plan:
        for r in row["renders"]:
            planned += 1
            if d["decision"] == "bind":
                ev = {"type": "binding", "id": L.det_id("binding", "sheet", by, r["sha"], r["job"], d["subject"]),
                      "sha": r["sha"], "job": r["job"], "subject": d["subject"], "originals": [], "texpath": None,
                      "confidence": conf, "evidence": f"{src} ({SHEET_ID}, family {row['family']})", "by": by}
            else:
                ev = {"type": "no_subject", "id": L.det_id("no_subject", by, r["sha"], r["job"]), "sha": r["sha"],
                      "job": r["job"], "reason": d["reason"], "by": by,
                      "evidence": f"{src} ({SHEET_ID}, family {row['family']})"}
            if not dry_run:
                wr.add(ev)
    if not dry_run:
        wr.flush()
    return {"written": len(wr.known) - n0, "planned": planned, "refused": []}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--index", help="a render_subjects.json to read (default: rebuild it)")
    b.add_argument("--out", default=str(L.REPO_ROOT / "Transient" / "binding_sheet"))
    e = sub.add_parser("enact")
    e.add_argument("decisions")
    e.add_argument("--by", required=True, choices=("owner", "agent"))
    e.add_argument("--why")
    e.add_argument("--worklist", help="default: <decisions dir>/binding_sheet.worklist.json")
    e.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "build":
        print(json.dumps(build(Path(a.index) if a.index else None, Path(a.out)), indent=1))
        return 0
    dp = Path(a.decisions)
    rows = json.loads(Path(a.worklist or dp.parent / f"{SHEET_ID}.worklist.json").read_text())
    w = S.World(read_jobs=False)
    try:
        import render_subjects as RS
        r = enact(json.loads(dp.read_text()), rows, a.by, a.why, set(w.defs) | RS.VANILLA_JUNK, a.dry_run)
    except ValueError as ex:
        print(f"REFUSED: {ex}")
        return 2
    print(json.dumps(r, indent=1))
    return 1 if r["refused"] else 0


if __name__ == "__main__":
    sys.exit(main())
