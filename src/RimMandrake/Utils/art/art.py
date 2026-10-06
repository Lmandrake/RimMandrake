#!/usr/bin/env python3
"""art — the art ledger CLI (ART_VERSION_WRANGLING_1).

    art.py snapshot  [--budget S]           Phase 0: every src/**/Textures PNG -> the art store,
                                            plus a committed sha manifest. Resumable.
    art.py backfill  <step|all> [--budget S] Phase 1 imports: disk | git | artpipe | donor |
                                            canon | rulings  (idempotent: deterministic ids)
    art.py status    <subject|texPath>      live picture(s), protections, rulings, flags
    art.py variants  <subject|texPath>      every known picture of it, with provenance
    art.py install   <mod> <rel> <sha> (--ruling ID | --owner-said "..." | --reason TAG) [--dry-run]
                                            TAG: artpipe-collect | script:<writer path>; a mechanical
                                            install is refused over an owner-kept picture
    art.py guard     range A..B | worktree [paths]   texture changes the ledger did not make
    art.py purge     <sha> --owner-said "..." [--release-keep]   reject+purge (owner only)
    art.py ingest    <decisions.json>       owner sheet decisions -> ruling/purge events
    art.py index                            write the gitignored projection index.json

Design: design/RimMandrake/art_ledger_design_2026-10-04.md. Library: artledger.py.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artledger as L  # noqa: E402


def _pngs(root: Path):
    for p in sorted(root.rglob("*.png")):
        if "/Textures/" in str(p).replace("\\", "/"):
            yield p


# ─────────────────────────────────────────────────────────── phase 0 ──

def cmd_snapshot(a):
    root = L.src_root()
    rels = []
    for p in _pngs(root):
        rels.append(p)
    out = L.ledger_dir() / "snapshots" / f"{a.date}_textures.tsv"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {}
    if out.exists():
        for line in out.read_text().splitlines()[1:]:
            sha, size, path = line.split("\t")
            done[path] = (sha, size)
    t0 = time.time()
    todo = [p for p in rels if str(p.relative_to(root.parent)) not in done]
    print(f"snapshot: {len(rels)} PNGs under {root}; {len(done)} already recorded; {len(todo)} to go", flush=True)

    def one(p):
        b = p.read_bytes()
        sha = L.store_put_bytes(b)
        return str(p.relative_to(root.parent)), sha, len(b)

    n = 0
    with ThreadPoolExecutor(max_workers=12) as ex:
        it = iter(todo)
        while True:
            batch = [x for _, x in zip(range(200), it)]
            if not batch:
                break
            for path, sha, size in ex.map(one, batch):
                done[path] = (sha, str(size))
            n += len(batch)
            _write_manifest(out, done)
            print(f"  {n}/{len(todo)}  {time.time() - t0:.0f}s", flush=True)
            if time.time() - t0 > a.budget:
                print("BUDGET REACHED — re-run to resume", flush=True)
                return 3
    missing = [p for p, (sha, _) in done.items() if not L.store_has(sha)]
    if missing:
        print(f"BYTES_MISSING: {len(missing)} recorded shas absent from the store, e.g. {missing[0]}")
        return 1
    print(f"snapshot complete: {len(done)} files, {len({s for s, _ in done.values()})} distinct "
          f"pictures, all verified in {L.store_dir()}; manifest {out}")
    return 0


def _write_manifest(out: Path, done: dict):
    tmp = out.with_suffix(".tmp")
    with open(tmp, "w") as fh:
        fh.write("sha256\tbytes\tpath\n")
        for path in sorted(done):
            sha, size = done[path]
            fh.write(f"{sha}\t{size}\t{path}\n")
    os.replace(tmp, out)


# ─────────────────────────────────────────────────────────── phase 1 ──

def cmd_backfill(a):
    import backfill
    steps = ["disk", "git", "artpipe", "donor", "canon", "rulings"] if a.step == "all" else [a.step]
    rc = 0
    for s in steps:
        r = getattr(backfill, f"step_{s}")(budget=a.budget)
        print(f"backfill {s}: {json.dumps(r)}", flush=True)
        rc = rc or (3 if r.get("budget_reached") else 0)
    return rc


def _match(idx: L.Index, q: str, slots: dict) -> list[str]:
    """Resources for a query: a texPath stem, a defName, or a bare creature word."""
    ql = q.lower()
    hits = set()
    for tp, ss in slots.items():
        if any(s["subject"].lower().split("#")[0] in (ql, "rsw_" + ql, "rm_" + ql, "rut_" + ql) for s in ss):
            hits.add(tp)
    if not hits:
        hits = {r for r in idx.by_res if r.lower() == ql or r.lower().rsplit("/", 1)[-1] == ql
                or ("/" + ql + "/") in ("/" + r.lower() + "/")}
    return sorted(hits)


def cmd_status(a, verbose=False):
    idx = L.Index()
    slots = L.scan_def_slots()
    ress = _match(idx, a.query, slots)
    if not ress:
        print(f"{a.query}: no resource matches (UNMEASURED, not absent: try a texPath stem)")
        return 1
    for res in ress:
        print(f"\n== {res}   slots: {', '.join(sorted({s['subject'] + '/' + s['role'] for s in slots.get(res, [])})) or '(none in our defs)'}")
        lives = [(k, ev) for k, ev in idx.live.items() if L.parse_texfile(k[1])["res"] == res]
        for (mod, rel), ev in sorted(lives):
            prot = idx.protected(ev["sha"])
            print(f"   LIVE {mod.split('/')[-1]:<24} {rel.rsplit('/', 1)[-1]:<28} {ev['sha'][:12]}"
                  f"{'  PROTECTED' if prot else ''}")
        mods = {m for (m, _r), _e in lives}
        if len(mods) > 1:
            print(f"   FLAG SHADOWED: shipped by {len(mods)} of our mods ({', '.join(sorted(m.split('/')[-1] for m in mods))})")
        shas = idx.by_res.get(res, set())
        live_shas = {ev["sha"] for _k, ev in lives}
        kinds = {}
        for s in shas:
            for v in idx.variants[s]:
                kinds[v.get("kind")] = kinds.get(v.get("kind"), 0) + 1
        print(f"   variants: {len(shas)} distinct pictures ({', '.join(f'{k} {n}' for k, n in sorted(kinds.items()))}); "
              f"purged {sum(1 for s in shas if idx.is_purged(s))}")
        if verbose:
            for s in sorted(shas, key=lambda s: min(v.get("date", "") for v in idx.variants[s])):
                vs = idx.variants[s]
                tag = "LIVE " if s in live_shas else ("PURGED " if idx.is_purged(s) else "")
                v0 = vs[0]
                print(f"     {tag}{s[:12]} {v0.get('facing','?'):<6} {v0.get('role','?'):<10} "
                      + "; ".join(f"{v.get('kind')}:{v.get('date','')}:{(v.get('loc') or '')[-60:]}" for v in vs[:3]))
    keys = {L.subject_key(a.query)}
    rul = idx.subject_rulings(keys)
    if rul:
        print(f"\n   rulings on '{a.query}': {len(rul)}")
        for r in sorted(rul, key=lambda r: r.get("at") or ""):
            print(f"     {(r.get('at') or '')[:10]} {r.get('verdict'):<14} trust={r.get('trust'):<17} "
                  f"{Path(r.get('source_file') or '').name[:48]}  {(r.get('note') or '')[:70]}")
    return 0


def cmd_install(a):
    try:
        r = L.install(a.mod, a.rel, a.sha, ruling_id=a.ruling, owner_said=a.owner_said, reason=a.reason,
                      dry_run=a.dry_run)
    except L.Refused as e:
        print(f"REFUSED: {e}")
        return 2
    print(json.dumps(r))
    return 0


def cmd_purge(a):
    idx = L.Index()
    full = [s for s in idx.variants if s.startswith(a.sha)] or ([a.sha] if len(a.sha) == 64 else [])
    if len(full) != 1:
        print(f"REFUSED: {a.sha} matches {len(full)} known pictures")
        return 2
    try:
        r = L.purge(full[0], owner_said=a.owner_said, release_keep=a.release_keep)
    except L.Refused as e:
        print(f"REFUSED: {e}")
        return 2
    print(json.dumps(r))
    return 0


def cmd_ingest(a):
    import ingest
    r = ingest.ingest(Path(a.decisions), dry_run=a.dry_run, redo_jobs=Path(a.redo_jobs) if a.redo_jobs else None,
                      defer_redo_jobs=a.defer_redo_jobs)
    print(json.dumps(r, indent=1))
    return 0 if r.get("ok") else 2


def cmd_backfill_rejections(a):
    import ingest
    print(json.dumps(ingest.backfill_rejections(dry_run=a.dry_run), indent=1))
    return 0


def cmd_index(a):
    idx = L.Index()
    out = L.ledger_dir() / "index.json"
    lives = {}
    for (mod, rel), ev in idx.live.items():
        pt = L.parse_texfile(rel)
        lives.setdefault(pt["res"], []).append({"mod": mod, "rel": rel, "sha": ev["sha"]})
    doc = {"built": L.now(), "events": len(idx.events), "variants": len(idx.variants),
           "rulings": len(idx.rulings), "purged": len(idx.purged),
           "resources": {r: {"variants": sorted(s), "live": lives.get(r, [])} for r, s in idx.by_res.items()}}
    out.write_text(json.dumps(doc, separators=(",", ":")))
    print(f"index: {len(idx.events)} events, {len(idx.variants)} pictures, {len(idx.by_res)} resources, "
          f"{len(idx.rulings)} rulings, {len(idx.purged)} purged -> {out}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("snapshot"); p.add_argument("--date", default=time.strftime("%Y-%m-%d"))
    p.add_argument("--budget", type=float, default=480)
    p = sp.add_parser("backfill"); p.add_argument("step"); p.add_argument("--budget", type=float, default=480)
    p = sp.add_parser("status"); p.add_argument("query")
    p = sp.add_parser("variants"); p.add_argument("query")
    p = sp.add_parser("install"); p.add_argument("mod"); p.add_argument("rel"); p.add_argument("sha")
    p.add_argument("--ruling"); p.add_argument("--owner-said"); p.add_argument("--reason")
    p.add_argument("--dry-run", action="store_true")
    p = sp.add_parser("purge"); p.add_argument("sha"); p.add_argument("--owner-said", required=True)
    p.add_argument("--release-keep", action="store_true")
    p = sp.add_parser("ingest"); p.add_argument("decisions"); p.add_argument("--dry-run", action="store_true")
    p.add_argument("--redo-jobs", help="the regen jobs queued for this sheet; each must carry his note verbatim as owner_note (req 9)")
    p.add_argument("--defer-redo-jobs", action="store_true", help="redo decisions present, jobs queued later (skips the req-9 check)")
    sp.add_parser("index")
    p = sp.add_parser("backfill-rejections", help="record the bytes behind past owner redo/reject rulings")
    p.add_argument("--dry-run", action="store_true")
    if argv is None:
        argv = sys.argv[1:]
    if argv[:1] == ["guard"]:
        import art_guard
        return art_guard.main(argv[1:])
    a = ap.parse_args(argv)
    if a.cmd == "variants":
        return cmd_status(a, verbose=True)
    return {"snapshot": cmd_snapshot, "backfill": cmd_backfill, "status": cmd_status,
            "install": cmd_install, "purge": cmd_purge, "ingest": cmd_ingest, "index": cmd_index,
            "backfill-rejections": cmd_backfill_rejections}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
