#!/usr/bin/env python3
"""backfill.py — Phase 1 imports into the art ledger (design §1.4). Each step is
idempotent (deterministic event ids) and resumable under a time budget.

    disk     every PNG under src/**/Textures -> variant(kind=repo) + live(reason=backfill-observed)
    git      every blob ever committed at a src/**/Textures/*.png path -> variant(kind=git), bytes
             not on disk today copied into the store. `--all --no-renames` sees every Add, so art
             added and later renamed away is still caught (GPT #9's concern with an M/D-only walk).
    artpipe  every _artsrc render (+ done/ manifest, collected.jsonl dest join) -> variant(kind=artpipe),
             bytes copied into the store (every shown candidate archived, design §2.5)
    donor    donor sprites whose texPath matches one of OUR texPaths (bundle extracts + loose) ->
             variant(kind=donor). Not the whole 20k-file donor tree: only slots we ship.
    canon    canon-library images -> variant(kind=canon). REFERENCE ONLY, never installable.
    rulings  every decisions file in infrastructure/state/art_rulings/ (+ design/) -> ruling events.
             None of them can name exact bytes, so all import as legacy-unresolved (shown,
             protecting nothing), prefill/ as prefill, and the 2026-10-03 desert sheet as
             flawed-sheet — owner ruling 2026-10-04.
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import time
from pathlib import Path

import artledger as L

ARTPIPE = Path(os.environ.get("ARTPIPE_STATE_DIR") or "/mnt/d/Luke/dev/_artpipe")
LEGACY_ARTPIPE = Path(os.environ.get("ARTPIPE_LEGACY_DIR") or "/mnt/d/Luke/dev/RimMandrake/infrastructure/artpipe")
BUNDLES = Path("/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures")
CENSUS_CSV = L.REPO_ROOT / "Transient" / "art_census_desert_2026-10-04.csv"
CANON = L.REPO_ROOT / "design" / "RimStarWars" / "canon_references"
RULINGS = L.REPO_ROOT / "infrastructure" / "state" / "art_rulings"
FLAWED = "2026-10-03_desert_art_review_2026-10-03"
FLAWED_REASON = ("made against a flawed sheet: its 'current' column showed corpse "
                 "(dessicated) textures for 65 of 109 rows, and facings were not coherent")

_PH = None


def _phcache():
    global _PH
    if _PH is None:
        p = L.ledger_dir() / "phash_cache.json"
        _PH = json.loads(p.read_text()) if p.exists() else {}
    return _PH


def _phsave():
    if _PH is not None:
        p = L.ledger_dir() / "phash_cache.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(_PH))
        os.replace(tmp, p)


def _ph(sha, b):
    c = _phcache()
    if sha not in c:
        try:
            c[sha] = list(L.dhash(b))
        except Exception:                       # unreadable image: recorded, not fatal
            c[sha] = ["", 0, 0]
    return c[sha]


def _variant(w, *, sha, b, kind, loc, rel=None, date="", extra=None, idkey=None):
    if sha in _purged():
        return False
    ph, wd, ht = _ph(sha, b)
    ev = {"type": "variant", "id": L.det_id("variant", kind, sha, idkey or loc), "sha": sha,
          "ph": ph, "w": wd, "h": ht, "kind": kind, "loc": loc, "date": date}
    if rel:
        pt = L.parse_texfile(rel)
        ev.update(res=pt["res"], facing=pt["facing"], mask=pt["mask"])
    if extra:
        ev.update(extra)
    return w.add(ev)


_PURGED = None


def _purged():
    global _PURGED
    if _PURGED is None:
        _PURGED = {e["sha"] for e in L.read_events() if e.get("type") == "purge"}
    return _PURGED


def _roles():
    slots = L.scan_def_slots()
    return slots


def step_disk(budget=480):
    t0 = time.time()
    w = L.Writer()
    root = L.src_root()
    slots = _roles()
    n0 = len(w.known)
    count = 0
    for p in sorted(root.rglob("*.png")):
        sp = L.split_texture_path(str(p.relative_to(root.parent)))
        if not sp:
            continue
        mod, rel = sp
        b = p.read_bytes()
        sha = L.sha256_bytes(b)
        pt = L.parse_texfile(rel)
        role = L.role_of(pt["res"], pt["mask"], slots)
        subj = sorted({s["subject"] for s in slots.get(pt["res"], [])})
        _variant(w, sha=sha, b=b, kind="repo", loc=f"{mod}/Textures/{rel}", rel=rel,
                 date=time.strftime("%Y-%m-%d", time.localtime(p.stat().st_mtime)),
                 extra={"role": role, "mod": mod, "subjects": subj})
        w.add({"type": "live", "id": L.det_id("live-backfill", mod, rel, sha), "mod": mod, "rel": rel,
               "sha": sha, "prev": None, "role": role, "reason": "backfill-observed"})
        count += 1
    w.flush()
    _phsave()
    return {"files": count, "new_events": len(w.known) - n0, "secs": round(time.time() - t0)}


def _git(*args, **kw):
    return subprocess.run(["git", "-C", str(L.REPO_ROOT), *args], capture_output=True, check=True, **kw).stdout


def step_git(budget=480):
    t0 = time.time()
    out = _git("log", "--all", "--no-renames", "--raw", "--no-abbrev", "--diff-filter=AM",
               "--format=C\t%H\t%cs\t%s").decode("utf-8", "replace")
    blobs = {}          # blob -> list of (commit, date, subj, path)
    cur = None
    for line in out.splitlines():
        if line.startswith("C\t"):
            _, h, d, s = line.split("\t", 3)
            cur = (h, d, s)
        elif line.startswith(":") and cur:
            meta, path = line.split("\t", 1)
            if not path.lower().endswith(".png") or "/Textures/" not in path:
                continue
            blob = meta.split()[3]
            blobs.setdefault(blob, []).append((cur[0], cur[1], cur[2], path))
    disk = {}
    snap = sorted((L.ledger_dir() / "snapshots").glob("*_textures.tsv"))
    if snap:
        for line in snap[-1].read_text().splitlines()[1:]:
            sha, _sz, path = line.split("\t")
            disk[path] = sha
    w = L.Writer()
    n0 = len(w.known)
    done_marker = L.ledger_dir() / "git_backfill_done.txt"
    done = set(done_marker.read_text().split()) if done_marker.exists() else set()
    todo = [b for b in blobs if b not in done]
    print(f"  git: {len(blobs)} distinct Texture blobs in history; {len(todo)} to import", flush=True)
    proc = subprocess.Popen(["git", "-C", str(L.REPO_ROOT), "cat-file", "--batch"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stored = 0
    hist_only = 0
    for i, blob in enumerate(todo):
        proc.stdin.write((blob + "\n").encode())
        proc.stdin.flush()
        hdr = proc.stdout.readline().split()
        if len(hdr) < 3 or hdr[1] != b"blob":
            continue
        b = proc.stdout.read(int(hdr[2]))
        proc.stdout.read(1)
        sha = L.sha256_bytes(b)
        occ = sorted(blobs[blob], key=lambda o: o[1])
        on_disk_now = any(disk.get(o[3]) == sha for o in occ)
        if not on_disk_now and not L.store_has(sha):
            L.store_put_bytes(b, sha)
            stored += 1
        if not on_disk_now:
            hist_only += 1
        for commit, date, subj, path in occ:
            sp = L.split_texture_path(path)
            if not sp:
                continue
            mod, rel = sp
            _variant(w, sha=sha, b=b, kind="git", loc=f"git:{commit[:10]}:{path}", rel=rel, date=date,
                     idkey=f"{sha}:{path}",
                     extra={"mod": mod, "commit": commit[:10], "subject": subj[:120], "on_disk_now": on_disk_now})
            break       # first occurrence per (sha, path) is enough; later ones are the same picture
        # also record each distinct path the picture appeared at
        seen_paths = {occ[0][3]}
        for commit, date, subj, path in occ[1:]:
            if path in seen_paths:
                continue
            seen_paths.add(path)
            sp = L.split_texture_path(path)
            if sp:
                _variant(w, sha=sha, b=b, kind="git", loc=f"git:{commit[:10]}:{path}", rel=sp[1], date=date,
                         idkey=f"{sha}:{path}",
                         extra={"mod": sp[0], "commit": commit[:10], "subject": subj[:120], "on_disk_now": on_disk_now})
        done.add(blob)
        if i % 500 == 499:
            w.flush(); _phsave(); done_marker.write_text("\n".join(sorted(done)))
            print(f"  git: {i + 1}/{len(todo)} blobs, {stored} copied to store, {time.time() - t0:.0f}s", flush=True)
            if time.time() - t0 > budget:
                proc.kill()
                return {"blobs": len(blobs), "imported": i + 1, "budget_reached": True}
    proc.stdin.close()
    proc.wait()
    w.flush(); _phsave(); done_marker.write_text("\n".join(sorted(done)))
    return {"blobs": len(blobs), "history_only_pictures": hist_only, "copied_to_store": stored,
            "new_events": len(w.known) - n0, "secs": round(time.time() - t0)}


def _main_png(d: Path):
    cand = d / f"{d.name}.png"
    if cand.is_file():
        return cand
    pngs = [p for p in d.glob("*.png") if not any(t in p.name for t in ("prestroke", "reinforced", "_raw", "_src"))]
    return max(pngs, key=lambda p: p.stat().st_size) if pngs else None


def step_artpipe(budget=480):
    t0 = time.time()
    src = ARTPIPE / "_artsrc"
    if not src.is_dir():
        return {"error": f"{src} absent — UNMEASURED, not zero"}
    dest = {}
    cj = ARTPIPE / "collected.jsonl"
    if cj.exists():
        for line in cj.read_text().splitlines():
            try:
                r = json.loads(line)
                dest[r["job_id"]] = r.get("dest")
            except (ValueError, KeyError):
                pass
    w = L.Writer()
    n0 = len(w.known)
    dirs = sorted(p for p in src.iterdir() if p.is_dir())
    # renders from before the 2026-10-02 state move still sit under the old in-repo root (454 on 2026-10-05, e.g. the
    # owner-ruled rot_wildpawn_v2): ingest those the current root lacks, so no finished render stays off the sheets
    legacy = LEGACY_ARTPIPE / "_artsrc"
    have = {d.name for d in dirs}
    if legacy.is_dir():
        dirs += sorted(p for p in legacy.iterdir() if p.is_dir() and p.name not in have)
    n = 0
    for i, d in enumerate(dirs):
        p = _main_png(d)
        if not p:
            continue
        b = p.read_bytes()
        sha = L.sha256_bytes(b)
        if sha in _purged():
            continue
        man = {}
        mf = (ARTPIPE if d.parent == src else LEGACY_ARTPIPE) / "done" / f"{d.name}.json"
        if mf.exists():
            try:
                man = json.loads(mf.read_text())
            except ValueError:
                man = {}
        L.store_put_bytes(b, sha)
        rel = None
        if dest.get(d.name):
            sp = L.split_texture_path(dest[d.name])
            rel = sp[1] if sp else None
        extra = {"job": d.name, "facing": man.get("facing") or "?", "prompt": (man.get("prompt") or "")[:300],
                 "derive_from": man.get("derive_from"), "style": (man.get("style_notes") or "")[:120],
                 "item": man.get("rimflow_item_id"), "collected_to": dest.get(d.name)}
        # bind at birth (ART_SUBJECT_RESOLVER_1 §5.2): the job's own record names its subject
        tdef, inst = man.get("target_def"), man.get("install_to") or man.get("target_texpath")
        if tdef:
            extra["target_def"] = tdef
        if inst:
            extra["install_to"] = inst
        _variant(w, sha=sha, b=b, kind="artpipe", loc=f"_artsrc/{d.name}/{p.name}", rel=rel,
                 date=(man.get("created") or time.strftime("%Y-%m-%d", time.localtime(p.stat().st_mtime)))[:10],
                 extra=extra)
        if tdef:    # a variant already in the ledger never gains fields (same id), so the subject is its own event
            w.add({"type": "binding", "id": L.det_id("binding", "job", sha, d.name, tdef), "sha": sha, "job": d.name,
                   "subject": tdef, "originals": list(man.get("target_original") or []),
                   "texpath": man.get("target_texpath") or inst, "confidence": "bound",
                   "evidence": f"job {d.name} target_def {tdef}"})
        n += 1
        if i % 300 == 299:
            w.flush(); _phsave()
            print(f"  artpipe: {i + 1}/{len(dirs)} {time.time() - t0:.0f}s", flush=True)
            if time.time() - t0 > budget:
                return {"dirs": len(dirs), "done": i + 1, "budget_reached": True}
    w.flush(); _phsave()
    return {"render_dirs": len(dirs), "renders": n, "new_events": len(w.known) - n0, "secs": round(time.time() - t0)}


def step_donor(budget=480):
    t0 = time.time()
    ours = {}
    for e in L.read_events():
        if e.get("type") == "variant" and e.get("kind") in ("repo", "git") and e.get("res"):
            rel = e["loc"].split("/Textures/", 1)[-1]
            ours.setdefault(rel.lower(), rel)
    w = L.Writer()
    n0 = len(w.known)
    n = 0
    if BUNDLES.is_dir():
        for pkg in sorted(BUNDLES.iterdir()):
            if not pkg.is_dir():
                continue
            for p in pkg.rglob("*.png"):
                r = str(p.relative_to(pkg)).replace("\\", "/")
                low = r.lower()
                low = low[len("textures/"):] if low.startswith("textures/") else low
                if low not in ours:
                    continue
                b = p.read_bytes()
                sha = L.sha256_bytes(b)
                L.store_put_bytes(b, sha)
                _variant(w, sha=sha, b=b, kind="donor", loc=f"bundle:{pkg.name}/{r}", rel=ours[low],
                         extra={"donor_pkg": pkg.name, "how": "assetbundle-extract"})
                n += 1
    else:
        print(f"  donor: {BUNDLES} absent — bundle donors UNMEASURED", flush=True)
    if CENSUS_CSV.exists():
        for row in csv.DictReader(open(CENSUS_CSV)):
            if row["source"] != "donor-loose" or not os.path.isfile(row["path"]):
                continue
            pth = row["path"].replace("\\", "/")
            rel = pth.split("/Textures/", 1)[-1]
            b = Path(row["path"]).read_bytes()
            sha = L.sha256_bytes(b)
            L.store_put_bytes(b, sha)
            _variant(w, sha=sha, b=b, kind="donor", loc=f"loose:{pth}", rel=rel,
                     extra={"donor_pkg": pth.split("/294100/", 1)[-1].split("/", 1)[0], "how": "loose",
                            "subject_key": L.subject_key(row["row_id"])})
            n += 1
    w.flush(); _phsave()
    return {"our_texpaths": len(ours), "donor_matches": n, "new_events": len(w.known) - n0,
            "secs": round(time.time() - t0)}


def step_canon(budget=480):
    w = L.Writer()
    n0 = len(w.known)
    n = 0
    for p in sorted(CANON.glob("*/*")):
        if p.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            continue
        b = p.read_bytes()
        sha = L.sha256_bytes(b)
        _variant(w, sha=sha, b=b, kind="canon", loc=str(p.relative_to(L.REPO_ROOT)),
                 extra={"subject_key": p.parent.name.lower(), "reference_only": True,
                        "is_donor_sprite": p.stem == "donor_current_sprite"})
        n += 1
    w.flush(); _phsave()
    return {"canon_images": n, "new_events": len(w.known) - n0}


def _rows(doc):
    dec = doc.get("decisions", {}) if isinstance(doc, dict) else {}
    if isinstance(dec, list):
        return [(str(x.get("id")), x) for x in dec if isinstance(x, dict)]
    if isinstance(dec, dict):
        return [(k, v) for k, v in dec.items() if isinstance(v, dict)]
    return []


def step_rulings(budget=480):
    files = sorted(RULINGS.glob("*.decisions.json")) + sorted((RULINGS / "prefill").glob("*.decisions.json"))
    files += sorted(p for p in (L.REPO_ROOT / "design").rglob("*decisions*.json"))
    w = L.Writer()
    n0 = len(w.known)
    tally = {}
    for f in files:
        try:
            doc = json.loads(f.read_text())
        except ValueError:
            continue
        rel = str(f.relative_to(L.REPO_ROOT))
        in_prefill = "/prefill/" in rel
        flawed = FLAWED in f.name
        for key, v in _rows(doc):
            raw = v.get("decision", v.get("value", v.get("verdict", "")))
            if not isinstance(raw, str) or not raw.strip():
                continue
            touched = bool(v.get("at")) and not (v.get("prefilled") and not v.get("note"))
            if flawed:
                trust = "flawed-sheet"
            elif in_prefill or not touched and not doc.get("approvedSaid") and not doc.get("owner_said"):
                trust = "prefill"
            else:
                trust = "legacy-unresolved"
            ev = {"type": "ruling", "id": L.det_id("ruling-import", rel, key, raw), "row_key": key,
                  "subject_key": L.subject_key(key), "verdict": L.normalise_verdict(raw), "raw_verdict": raw,
                  "note": (v.get("note") or "")[:500], "at": v.get("at") or doc.get("approvedAt") or "",
                  "by": "agent" if trust == "prefill" else "owner", "trust": trust, "source_file": rel,
                  "target": {"subject_key": L.subject_key(key)},
                  "why_not_protecting": FLAWED_REASON if flawed else (
                      "agent prefill — no human decision evidence" if trust == "prefill" else
                      "legacy sheet names no exact bytes; shown on sheets, protects nothing until re-confirmed")}
            if doc.get("approvedSaid") and not v.get("note"):
                ev["blanket_said"] = str(doc["approvedSaid"])[:300]
            if w.add(ev):
                tally[trust] = tally.get(trust, 0) + 1
    w.flush()
    return {"files": len(files), "new_rulings": tally, "new_events": len(w.known) - n0}
