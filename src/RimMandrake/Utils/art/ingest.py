#!/usr/bin/env python3
"""ingest.py — an art compare sheet's decisions file -> owner ruling / purge events.

Rules (design §3, owner rulings 2026-10-04):
  * The file must carry the sidecar's plumbing stamp (`savedBy` + `writeCount`) or a
    `reviewStatus.state == "ruled"`. A file only a generator wrote is the agent's guess.
  * ONLY rows the owner touched (an `at` stamp) become rulings. An untouched prefill is
    never a ruling, even on a ruled sheet.
  * A column decision resolves through the sheet's SNAPSHOT (row -> column -> facing -> sha)
    written at generation time, so a regenerated column cannot be approved under an old label.
  * Each row may carry `purge: [sha...]` — the owner's reject+purge. A purge of a live
    picture is refused (counted, reported); everything else is deleted from the store.
  * Nothing is installed. Installing is `art.py install`, a separate step.
  * PLACEHOLDERS ARE NEVER KEPT (owner, 2026-10-07 22:33 PDT: "make sure that at no time can geometric placeholder
    art ever remain a viable Variant or selection"). A pick naming a column whose pictures are all geometric
    placeholders is recorded as a `redo` ruling (raw_verdict `placeholder-pick`, `why` says so) — a regen request —
    and its in-game pictures are rejected; a placeholder variant is refused (listed under `placeholder_refused`).
  * REGEN JOBS CARRY HIS NOTE VERBATIM (scaled-game-image-review req 9). `--redo-jobs <jobs.json>` checks every job
    queued for the sheet: `target_def` must be a decided row, and when that row has a note the job's `owner_note`
    must contain it character for character; a `redo` row with no job is refused too. A sheet with `redo` decisions
    and no `--redo-jobs` is REFUSED (nothing ingested) unless `--defer-redo-jobs` says the jobs come later.
"""
from __future__ import annotations

import json
from pathlib import Path

import artledger as L

_PH: dict = {}
MIRROR_ROOT = Path("/mnt/d/Luke/dev/RimMandrake")


def rel_via(p) -> str:
    """A decisions path as the ledger records it: repo-relative POSIX whenever it lies in this clone or the
    read-only D: mirror (an absolute spelling once minted 231 duplicate events for one sitting)."""
    pp = Path(p)
    rp = (pp if pp.is_absolute() else Path.cwd() / pp).resolve()
    for root in (L.REPO_ROOT.resolve(), MIRROR_ROOT):
        try:
            return rp.relative_to(root).as_posix()
        except ValueError:
            continue
    return str(p)


def ts(x):
    """An ISO stamp (Z or +HHMM) as an aware datetime, None when absent/unparseable."""
    import datetime as _dt
    if not isinstance(x, str) or not x:
        return None
    try:
        d = _dt.datetime.fromisoformat(x.replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=_dt.timezone.utc)


def stale_letter_rows(doc: dict, ruled: dict | None, now: dict) -> dict:
    """{row: [letters]} whose used letter the RULED snapshot never had (so letter_mismatches could not verify it) while
    the row was last clicked BEFORE the current snapshot was built: a rebuild in between may have re-pointed it."""
    if not ruled:
        return {}
    built = ts(now.get("built"))
    out = {}
    for row, v in ((doc.get("decisions") or {}).items()):
        if not isinstance(v, dict) or not v.get("at"):
            continue
        rc = ((ruled.get("rows") or {}).get(row) or {}).get("columns") or {}
        nc = ((now.get("rows") or {}).get(row) or {}).get("columns") or {}
        absent = sorted(l for l in L.decision_letters(v) if l not in rc and l in nc)
        if not absent:
            continue
        clicks = [c for c in (ts(v.get(k)) for k in ("decidedAt", "at", "variantsAt")) if c]
        if built is None or not clicks or max(clicks) < built:
            out[row] = absent
    return out


def content_key(ev: dict):
    """What makes two ruling/rejected events THE SAME decision, whatever path spelled their decisions file:
    the row, column, graphic, verdict and his click time. None = no content identity (fall back to the id)."""
    t = ev.get("type")
    tg = ev.get("target") or {}
    if t == "ruling" and tg.get("row") and ev.get("at"):
        return ("ruling", L.normalise_verdict(ev.get("verdict") or ""), tg.get("row"), tg.get("column"),
                tg.get("graphic"), tg.get("variant_of"), ev.get("at"))
    if t == "rejected" and ev.get("row") and ev.get("at"):
        return ("rejected", ev.get("sha"), ev.get("row"), ev.get("column"), ev.get("at"))
    return None


def known_content(events) -> set:
    return {k for k in (content_key(e) for e in events) if k}


def placeholder_set(shas) -> str:
    """The reason when EVERY picture of a column is a geometric placeholder (owner rule 2026-10-07 22:33 PDT), else ''.
    A picture not in the store is not judged here (install refuses it anyway)."""
    shas = [s for s in shas if s]
    if not shas:
        return ""
    for s in shas:
        if s not in _PH:
            try:
                import placeholder_detect as PD
                _PH[s] = (PD.placeholder_reason(L.store_get(s)) or "") if L.store_has(s) else ""
            except Exception:                           # noqa: BLE001
                _PH[s] = ""
        if not _PH[s]:
            return ""
    return _PH[shas[0]]


def _note_text(on) -> str:
    return "\n".join(on) if isinstance(on, list) else (on if isinstance(on, str) else "")


def followed_notes(v: dict) -> list[str]:
    """His exact words of every note already followed on this row (kept in `notes_followed`, never in `note`)."""
    return [str(f.get("note") or "").strip() for f in (v.get("notes_followed") or []) if isinstance(f, dict)
            if str(f.get("note") or "").strip()]


def open_note(v: dict) -> str:
    """The row's note that is still an OPEN request. A note identical to one already followed is not open: a stale
    browser tab re-posting it must not fire it a second time (owner, 2026-10-08)."""
    note = (v.get("note") or "").strip()
    return "" if note and note in followed_notes(v) else note


def check_redo_jobs(doc: dict, jobs: list) -> list[str]:
    """Problems (empty = fine) with the regen jobs queued for a decisions file: each carries the row's note verbatim."""
    rows = doc.get("decisions") or {}
    problems, covered = [], set()
    for j in jobs:
        if not isinstance(j, dict):
            problems.append(f"UNMEASURED: a job entry is not an object ({type(j).__name__})")
            continue
        jid = j.get("id", "?")
        row = j.get("target_def") or j.get("row")
        v = rows.get(row)
        if not isinstance(v, dict):
            problems.append(f"UNMEASURED: job {jid} targets {row!r}, which is not a row of this decisions file")
            continue
        covered.add(row)
        note = open_note(v)
        if note and note not in _note_text(j.get("owner_note")):
            problems.append(f"job {jid} (row {row}): owner_note does not carry his note verbatim: {note[:60]!r}")
    for row, v in rows.items():
        if isinstance(v, dict) and v.get("at") and (v.get("decision") or "").strip() == "redo" and row not in covered:
            problems.append(f"row {row} is a redo with no regen job in the jobs file")
    return problems


def rejected_events(ruling: dict, srow: dict) -> list[dict]:
    """A redo/reject on a row sends back the picture that was IN GAME when he looked: record those exact
    bytes, so no later install can quietly put them back or copy them onto another creature
    (ART_RULING_RENAME_CARRY_1). Columns he picked or kept as variants carry keeps, which win."""
    labels = srow.get("labels") or {}
    cols = srow.get("columns") or {}
    out = []
    for letter, lab in sorted(labels.items()):
        if not str(lab).startswith("IN GAME"):
            continue
        for sha in sorted({s for s in (cols.get(letter) or {}).values() if s}):
            out.append({"type": "rejected", "id": L.det_id("rejected", ruling["id"], sha), "sha": sha,
                        "ruling_id": ruling["id"], "verdict": ruling["verdict"], "by": "owner",
                        "said": ruling.get("said"), "via": ruling.get("via"), "at": ruling.get("at"),
                        "row": (ruling.get("target") or {}).get("row"), "column": letter,
                        "subject_key": ruling.get("subject_key", "")})
    return out


def ingest(decisions_path: Path, dry_run: bool = False, redo_jobs: Path | None = None,
           defer_redo_jobs: bool = False, purge: bool = True, skip_rows=()) -> dict:
    """purge=False leaves every ✕ alone (art.py enact purges itself, never releasing a keep);
    skip_rows: row keys not ingested at all (enact --hold)."""
    doc = json.loads(Path(decisions_path).read_text())
    redo_rows = [r for r, v in (doc.get("decisions") or {}).items()
                 if isinstance(v, dict) and v.get("at") and (v.get("decision") or "").strip() == "redo"]
    if redo_jobs is not None:
        try:
            jobs = json.loads(Path(redo_jobs).read_text())
        except (OSError, ValueError) as e:
            return {"ok": False, "error": f"REFUSED (req 9): UNMEASURED — jobs file {redo_jobs} unreadable ({e})"}
        jobs = jobs.get("jobs", jobs) if isinstance(jobs, dict) else jobs
        bad = check_redo_jobs(doc, jobs)
        if bad:
            return {"ok": False, "error": "REFUSED (req 9): every regen job must carry the decision's note verbatim as "
                                          "owner_note — " + " | ".join(bad[:12]) + (f" … +{len(bad) - 12} more" if len(bad) > 12 else "")}
    elif redo_rows and not defer_redo_jobs:
        return {"ok": False, "error": f"REFUSED (req 9): {len(redo_rows)} redo decision(s) and no --redo-jobs file to check "
                                      f"their owner_note against (rows: {', '.join(redo_rows[:6])}). Pass --redo-jobs <jobs.json>, "
                                      f"or --defer-redo-jobs if the jobs are queued later."}
    rs = doc.get("reviewStatus") if isinstance(doc.get("reviewStatus"), dict) else {}
    plumbed = bool(doc.get("savedBy")) and int(doc.get("writeCount") or 0) > 0
    if not plumbed and rs.get("state") != "ruled":
        return {"ok": False, "error": "no sidecar plumbing stamp and reviewStatus is not 'ruled' — "
                                      "this is still the generator's prefill; nothing ingested"}
    snap_path = Path(doc.get("snapshot") or "")
    if not snap_path.is_absolute():
        snap_path = L.REPO_ROOT / snap_path
    if not snap_path.is_file():
        return {"ok": False, "error": f"snapshot {snap_path} missing — cannot resolve columns to pictures"}
    snap = json.loads(snap_path.read_text())
    ruled = None
    stale: dict = {}
    if doc.get("snapshotId") and snap.get("snapshotId") and doc["snapshotId"] != snap["snapshotId"]:
        # letters are stable across rebuilds: what matters is that every letter the decisions USE still
        # names the same pictures as in the snapshot they were made against (found in git history)
        ruled = L.snapshot_by_id(snap_path, doc["snapshotId"])
        if ruled is None:
            return {"ok": False, "error": f"decisions were made against snapshot {doc['snapshotId']}, which is "
                                          f"neither on disk nor in the git history of {snap_path.name}"}
        bad = L.letter_mismatches(doc, ruled, snap)
        if bad:
            return {"ok": False, "error": "decisions were made against a different snapshot of this sheet and these "
                                          "letters now name different pictures: "
                                          + ", ".join(f"{r}:{l}" for r, l in bad[:20])}
        stale = stale_letter_rows(doc, ruled, snap)
    idx = L.Index()
    w = L.Writer({e["id"] for e in idx.events})
    cks = known_content(idx.events)
    via = rel_via(decisions_path)

    def put(ev) -> bool:
        """Append unless this id OR this content is already in the ledger. Dry-run counts without writing."""
        ck = content_key(ev)
        if ev["id"] in w.known or (ck and ck in cks):
            return False
        if ck:
            cks.add(ck)
        if dry_run:
            w.known.add(ev["id"])
            return True
        return w.add(ev)

    out = {"ok": True, "rulings": 0, "purged": 0, "purge_refused": 0, "untouched": 0, "unresolved": []}
    skip = set(skip_rows) | set(stale)
    out["stale_rows"] = stale
    for row, v in (doc.get("decisions") or {}).items():
        if not isinstance(v, dict) or row in skip:
            continue
        if not v.get("at"):
            out["untouched"] += 1
            continue
        # A row touched only to purge never turns its prefill into a ruling: the page stamps
        # decidedAt on a real decision click; purgeTouched marks a purge-only touch.
        decided = bool(v.get("decidedAt")) or not v.get("purgeTouched")
        srow = (snap.get("rows") or {}).get(row)
        dec = (v.get("decision") or "").strip()
        note = open_note(v)
        cols = (srow or {}).get("columns") or {}
        if dec and srow and decided:
            ph = placeholder_set(cols[dec].values()) if dec in cols else ""
            if ph:
                ev = {"type": "ruling", "id": L.det_id("ruling-sheet-placeholder", via, row, dec, v.get("at")),
                      "target": {"row": row, "subject_key": srow.get("subject_key", ""), "column": dec},
                      "verdict": "redo", "raw_verdict": "placeholder-pick", "by": "owner", "said": note,
                      "note": note, "at": v.get("at"), "trust": "ruled", "via": via,
                      "subject_key": srow.get("subject_key", ""), "source_file": via,
                      "why": f"he picked column {dec}, which is a {ph}; a placeholder is never kept, so the pick "
                             f"is a regen request ({L.PLACEHOLDER_RULE})"}
                out.setdefault("placeholder_redo", []).append(f"{row}:{dec}")
            elif dec in cols:
                shas = sorted({s for s in cols[dec].values() if s})
                ev = {"type": "ruling", "id": L.det_id("ruling-sheet", via, row, dec, v.get("at")),
                      "target": {"shas": shas, "column": dec, "row": row}, "verdict": "keep", "by": "owner",
                      "said": note, "note": note, "at": v.get("at"), "trust": "ruled", "via": via,
                      "subject_key": srow.get("subject_key", ""), "source_file": via,
                      "evidence": "sidecar savedBy/writeCount" if plumbed else "reviewStatus ruled"}
            else:
                ev = {"type": "ruling", "id": L.det_id("ruling-sheet", via, row, dec, v.get("at")),
                      "target": {"row": row, "subject_key": srow.get("subject_key", "")},
                      "verdict": L.normalise_verdict(dec), "raw_verdict": dec, "by": "owner", "said": note,
                      "note": note, "at": v.get("at"), "trust": "ruled", "via": via,
                      "subject_key": srow.get("subject_key", ""), "source_file": via}
            if put(ev):
                out["rulings"] += 1
            if ev["verdict"] in ("redo", "reject"):
                # the pictures IN GAME when he looked = the RULED snapshot's row, not whatever a later rebuild shows
                rsrow = ((ruled or {}).get("rows") or {}).get(row) or srow
                for rev in rejected_events(ev, rsrow):
                    if put(rev):
                        out["rejected"] = out.get("rejected", 0) + 1
            # per-biome sheets: a row's extra graphics (swimming, flying …) carry their own pick
            for g, pl in sorted((v.get("picks") or {}).items()):
                if pl in cols and pl != dec and placeholder_set(cols[pl].values()):
                    out.setdefault("placeholder_refused", []).append(f"{row}:{g}:{pl} (pick)")
                    continue
                if pl in cols and pl != dec:
                    pev = {**ev, "id": L.det_id("ruling-sheet", via, row, pl, v.get("at")), "verdict": "keep",
                           "target": {"shas": sorted({s for s in cols[pl].values() if s}), "column": pl,
                                      "row": row, "graphic": g}}
                    pev.pop("raw_verdict", None)
                    if put(pev):
                        out["rulings"] += 1
        # kept variants: extra columns the owner marked as valid in-game variants of the pick
        if srow and decided:
            for vl in sorted(set(v.get("variants") or [])):
                if vl in cols and vl != dec and placeholder_set(cols[vl].values()):
                    out.setdefault("placeholder_refused", []).append(f"{row}:{vl} (variant)")
                    continue
                if vl in cols and vl != dec:
                    vev = {"type": "ruling", "id": L.det_id("ruling-sheet", via, row, vl, v.get("variantsAt") or v.get("at")),
                           "target": {"shas": sorted({s for s in cols[vl].values() if s}), "column": vl,
                                      "row": row, "variant_of": dec},
                           "verdict": "keep", "by": "owner", "said": note, "note": note,
                           "at": v.get("variantsAt") or v.get("at"), "trust": "ruled", "via": via,
                           "subject_key": srow.get("subject_key", ""), "source_file": via,
                           "evidence": "sidecar savedBy/writeCount" if plumbed else "reviewStatus ruled"}
                    if put(vev):
                        out["rulings"] += 1
        if dec and decided and not (srow and dec):
            out["unresolved"].append(row)
        for sha in v.get("purge") or []:
            if dry_run or not purge:
                continue
            w.flush()
            try:
                L.purge(sha, owner_said=note or f"reject+purge on sheet {snap.get('sheetId')}",
                        via=via, release_keep=True)
                out["purged"] += 1
            except L.Refused as e:
                out["purge_refused"] += 1
                out.setdefault("refusals", []).append(f"{sha[:12]}: {e}")
            w = L.Writer()
    if not dry_run:
        w.flush()
    return out


def backfill_rejections(dry_run: bool = False) -> dict:
    """Derive `rejected` events for owner redo/reject rulings ingested before they were recorded: each
    ruling's decisions file names its snapshot, whose IN GAME columns are the pictures he sent back."""
    idx = L.Index()
    w = L.Writer({e["id"] for e in idx.events})
    out = {"rulings": 0, "rejected": 0, "no_snapshot": [], "no_row": 0}
    snaps: dict = {}
    for r in idx.rulings:
        if r.get("by") != "owner" or r.get("trust") != "ruled" or r.get("verdict") not in ("redo", "reject"):
            continue
        row, via = (r.get("target") or {}).get("row"), r.get("via") or r.get("source_file")
        if not row or not via:
            continue
        out["rulings"] += 1
        if via not in snaps:
            snaps[via] = None
            try:
                vp = next((c for c in (L.REPO_ROOT / via, Path(__file__).resolve().parent / via) if c.is_file()),
                          L.REPO_ROOT / via)
                doc = json.loads(vp.read_text())
                sp = Path(doc.get("snapshot") or "")
                sp = sp if sp.is_absolute() else L.REPO_ROOT / sp
                snaps[via] = L.snapshot_by_id(sp, doc.get("snapshotId")) or (
                    json.loads(sp.read_text()) if sp.is_file() and not doc.get("snapshotId") else None)
            except (OSError, ValueError):
                pass
        snap = snaps[via]
        if snap is None:
            if via not in out["no_snapshot"]:
                out["no_snapshot"].append(via)
            continue
        srow = (snap.get("rows") or {}).get(row)
        if not srow:
            out["no_row"] += 1
            continue
        for rev in rejected_events(r, srow):
            if not dry_run and w.add(rev):
                out["rejected"] += 1
            elif dry_run:
                out["rejected"] += 1
    if not dry_run:
        w.flush()
    return out
