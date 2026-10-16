#!/usr/bin/env python3
"""art — the art ledger CLI (ART_VERSION_WRANGLING_1).

    art.py snapshot  [--budget S]           Phase 0: every src/**/Textures PNG -> the art store,
                                            plus a committed sha manifest. Resumable.
    art.py backfill  <step|all> [--budget S] Phase 1 imports: disk | git | artpipe | donor |
                                            canon | rulings  (idempotent: deterministic ids)
    art.py status    <subject|texPath>      live picture(s), protections, rulings, flags
    art.py variants  <subject|texPath>      every known picture of it, with provenance
    art.py put       <png>...                put files into the art store (regular files inside this clone,
                                            no symlinks); prints each sha
    art.py install   <mod> <rel> (<sha> | --file PNG) (--ruling ID | --owner-said "..." | --reason TAG) [--dry-run]
                                            mod: SWBestiary | RimStarWars/SWBestiary | src/RimStarWars/SWBestiary;
                                            rel: with or without a leading Textures/.
                                            TAG: artpipe-collect | script:<writer path>; a mechanical
                                            install is refused over an owner-kept picture
    art.py guard     range A..B | worktree [paths]   texture changes the ledger did not make; a push range is
                                            also checked event -> PNG (the committed tree holds what the ledger says)
    art.py doctor    [--rev REV] [--out FILE]   every slot where the folded ledger and REV's committed tree
                                            (default HEAD) disagree, with the worktree bytes; read-only
    art.py purge     <sha> --owner-said "..." [--release-keep]   reject+purge (owner only); a kept picture is
                                            refused unless --release-keep names his words for releasing it
    art.py unpurge   <sha> --owner-said "..."   reverse the latest purge of that picture on his newer, explicit
                                            words (owner only; append-only `unpurge` event, history kept). Restores
                                            no bytes (put them first) and no keep; a mechanical install stays refused
    art.py kept-purged [--out FILE]         pictures purged while an owner keep on them is still active —
                                            REPORTED for his reconciliation, never auto-released
    art.py ingest    <decisions.json>       owner sheet decisions -> ruling/purge events
    art.py index                            write the gitignored projection index.json
    art.py enact     <decisions.json> [--apply] [--hold S]... [--mark-done ROW]... [--no-deploy]
                                            a ruled sheet in ONE pass: ingest, install picks, queue redraws,
                                            purge ✕ (never protected ones), cut rows, deploy touched mods (enact.py)
    art.py rotate    <SEAT> (--before ISO | --keep-mb N) [--apply]
                                            move a byte-exact PREFIX of events/<SEAT>.jsonl into write-once
                                            events/archive/<SEAT>.<NNNN>.<from>_<to>.jsonl; dry run by default.
                                            Readers fold archives then the live tail, so the fold is unchanged.

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
        rc = rc or (3 if r.get("budget_reached") else 1 if r.get("drift") else 0)
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
              f"purged {sum(1 for s in shas if idx.is_purged(s))}"
              + (f", unpurged by the owner {n_un}" if (n_un := sum(1 for s in shas if s in idx.unpurged)) else ""))
        if verbose:
            for s in sorted(shas, key=lambda s: min(v.get("date", "") for v in idx.variants[s])):
                vs = idx.variants[s]
                tag = "LIVE " if s in live_shas else ("PURGED " if idx.is_purged(s) else
                                                      "UNPURGED " if s in idx.unpurged else "")
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


def cmd_put(a):
    rc = 0
    for f in a.files:
        try:
            print(f"{L.put_file_checked(f)}  {f}")
        except L.Refused as e:
            print(f"REFUSED: {e}")
            rc = 2
    return rc


def cmd_install(a):
    try:
        if bool(a.sha) == bool(a.file):
            raise L.Refused("give exactly one of <sha> or --file <png>")
        sha = a.sha
        if a.file:
            sha = L.put_file_checked(a.file)
            if a.dry_run:
                print(f"put {a.file} -> {sha}")
        r = L.install(a.mod, a.rel, sha, ruling_id=a.ruling, owner_said=a.owner_said, reason=a.reason,
                      dry_run=a.dry_run)
    except L.Refused as e:
        print(f"REFUSED: {e}")
        return 2
    print(json.dumps(r))
    if not a.dry_run:          # the install-side hook: name every sheet this install just made stale (they refuse to serve)
        import sheet_freshness as FR
        res = L.parse_texfile(L.rel_key(a.rel))["res"]
        FR.after_install([res, res.rpartition("/")[0]])
    return 0


def cmd_doctor(a):
    import subprocess
    import art_guard as G
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    rows = G.doctor(root or L.REPO_ROOT, a.rev)
    by = {}
    for r in rows:
        by[r["kind"]] = by.get(r["kind"], 0) + 1
    unc = sum(1 for r in rows if r["uncommitted_install"])
    print(f"doctor ({a.rev}): {len(rows)} slot(s) where ledger and committed tree disagree"
          + (": " + ", ".join(f"{k} {n}" for k, n in sorted(by.items())) if rows else "")
          + (f"; {unc} of them are installs sitting uncommitted in this clone's worktree" if unc else ""))
    if a.out:
        Path(a.out).write_text(json.dumps(rows, indent=1))
        print(f"  rows -> {a.out}")
    else:
        for r in rows[:40]:
            print(f"  {r['kind']:<17} {r['path']}  ledger={str(r['ledger'])[:12]} tree={str(r['tree'])[:12]} "
                  f"worktree={str(r['worktree'])[:12]}")
        if len(rows) > 40:
            print(f"  … {len(rows) - 40} more (--out FILE for all)")
    un = L.Index().unpurged
    if un:
        nob = [s for s in un if not L.store_has(s)]
        print(f"unpurged by the owner: {len(un)} picture(s)" + (f"; {len(nob)} have no bytes in the store (put them "
              f"before installing): {', '.join(s[:12] for s in nob[:8])}" if nob else ""))
    return 1 if rows else 0


def cmd_kept_purged(a):
    idx = L.Index()
    rows = idx.kept_but_purged()
    gone = sum(1 for r in rows if not r["bytes_in_store"])
    print(f"kept-purged: {len(rows)} purged picture(s) still carry an active owner keep; {gone} have no bytes in the store")
    if not a.out:
        for r in rows[:30]:
            print(f"  {r['sha'][:12]} purged {(r['purge'].get('ts') or '')[:16]}  keeps: "
                  + "; ".join(f"{(k.get('ts') or '')[:16]} {Path(k.get('via') or '').name or 'words'}" for k in r["keeps"][:2]))
        return 1 if rows else 0
    out = Path(a.out)
    lines = ["# Kept but purged — art ledger, " + L.now()[:10], "",
             "Pictures the owner purged (bytes deleted from the art store) while an owner `keep` on them is still active, "
             "so the projection claims a protection that cannot be installed. **Reported for his decision; nothing was "
             "released or deleted.** Regenerate: `python3 src/RimMandrake/Utils/art/art.py kept-purged --out <file>`.", "",
             f"**{len(rows)} pictures; {gone} have no bytes left in the store; "
             f"{sum(1 for r in rows if any((k.get('ts') or '') < (r['purge'].get('ts') or '') for k in r['keeps']))} were kept "
             f"before the purge, {sum(1 for r in rows if all((k.get('ts') or '') >= (r['purge'].get('ts') or '') for k in r['keeps']))} "
             f"only after it.**", "",
             "| sha | bytes in store | live at | purged (ts · via · his words) | active keep(s) (ts · via · words) |",
             "|---|---|---|---|---|"]

    def cell(x):
        return str(x or "").replace("|", "/").replace("\n", " ")[:90]
    for r in rows:
        pv = r["purge"]
        ks = "<br>".join(f"{(k.get('ts') or k.get('at') or '')[:16]} · {cell(Path(k.get('via') or '').name)} · {cell(k.get('said'))}"
                         for k in r["keeps"])
        lines.append(f"| `{r['sha'][:16]}` | {'yes' if r['bytes_in_store'] else 'NO'} | {cell(', '.join(r['live_at']))} | "
                     f"{(pv.get('ts') or '')[:16]} · {cell(Path(pv.get('via') or '').name)} · {cell(pv.get('said'))} | {ks} |")
    out.write_text("\n".join(lines) + "\n")
    print(f"  report -> {out}")
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


def cmd_unpurge(a):
    idx = L.Index()
    full = [s for s in idx.purge_history if s.startswith(a.sha)]
    if len(full) != 1:
        print(f"REFUSED: {a.sha} matches {len(full)} purged pictures")
        return 2
    try:
        r = L.unpurge(full[0], owner_said=a.owner_said)
    except L.Refused as e:
        print(f"REFUSED: {e}")
        return 2
    print(json.dumps(r))
    if not r["bytes_in_store"]:
        print(f"  note: no bytes in the store for {full[0][:12]} — put the PNG there before installing it")
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


def cmd_rotate(a):
    """Move a byte-exact prefix of a seat's live shard into write-once archive files."""
    if a.before is None and a.keep_mb is None:
        print("rotate: give --before <ISO ts> or --keep-mb <N>", file=sys.stderr)
        return 2
    keep = None if a.keep_mb is None else int(a.keep_mb * 1024 * 1024)
    plan = L.rotate_plan(a.seat, before=a.before, keep_bytes=keep)
    before = L.read_events() if a.apply else None
    print(f"rotate {a.seat}: {plan['orig_bytes']:,} B / {plan['orig_lines']:,} lines -> "
          f"move {plan['moved_lines']:,} lines, keep {len(plan['tail']):,} B / {plan['tail_lines']:,} lines live; "
          f"pure_move={plan['pure_move']}")
    for ar in plan["archives"]:
        print(f"  archive/{ar['name']}  {len(ar['bytes']):,} B  {ar['lines']:,} lines")
    if not plan["archives"]:
        print("  nothing to move")
        return 0
    if not a.apply:
        print("  dry run — pass --apply to write")
        return 0
    paths = L.rotate_apply(plan)
    after = L.read_events()
    if after != before:
        print("rotate: FOLD CHANGED after apply — this must never happen; inspect before committing", file=sys.stderr)
        return 1
    print(f"  applied; fold identical ({len(after):,} events). Commit these paths together:")
    for p in paths:
        print(f"    {p}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("snapshot"); p.add_argument("--date", default=time.strftime("%Y-%m-%d"))
    p.add_argument("--budget", type=float, default=480)
    p = sp.add_parser("backfill"); p.add_argument("step"); p.add_argument("--budget", type=float, default=480)
    p = sp.add_parser("status"); p.add_argument("query")
    p = sp.add_parser("variants"); p.add_argument("query")
    p = sp.add_parser("put"); p.add_argument("files", nargs="+")
    p = sp.add_parser("install"); p.add_argument("mod"); p.add_argument("rel"); p.add_argument("sha", nargs="?")
    p.add_argument("--file", help="a PNG inside this clone: put it in the store, then install its sha")
    p.add_argument("--ruling"); p.add_argument("--owner-said"); p.add_argument("--reason")
    p.add_argument("--dry-run", action="store_true")
    p = sp.add_parser("purge"); p.add_argument("sha"); p.add_argument("--owner-said", required=True)
    p.add_argument("--release-keep", action="store_true")
    p = sp.add_parser("unpurge"); p.add_argument("sha"); p.add_argument("--owner-said", default="")
    p = sp.add_parser("ingest"); p.add_argument("decisions"); p.add_argument("--dry-run", action="store_true")
    p.add_argument("--redo-jobs", help="the regen jobs queued for this sheet; each must carry his note verbatim as owner_note (req 9)")
    p.add_argument("--defer-redo-jobs", action="store_true", help="redo decisions present, jobs queued later (skips the req-9 check)")
    sp.add_parser("index")
    p = sp.add_parser("kept-purged"); p.add_argument("--out")
    p = sp.add_parser("doctor"); p.add_argument("--rev", default="HEAD"); p.add_argument("--out")
    p = sp.add_parser("backfill-rejections", help="record the bytes behind past owner redo/reject rulings")
    p.add_argument("--dry-run", action="store_true")
    p = sp.add_parser("rotate", help="move old events of a seat's live shard into write-once archive files")
    p.add_argument("seat"); p.add_argument("--before", help="move the prefix with ts < this ISO timestamp")
    p.add_argument("--keep-mb", type=float, help="move the shortest prefix leaving <= N MB live")
    p.add_argument("--apply", action="store_true", help="write (default: dry run)")
    if argv is None:
        argv = sys.argv[1:]
    if argv[:1] == ["enact"]:
        import enact
        return enact.main(argv[1:])
    if argv[:1] == ["guard"]:
        import art_guard
        return art_guard.main(argv[1:])
    a = ap.parse_args(argv)
    if a.cmd == "variants":
        return cmd_status(a, verbose=True)
    return {"snapshot": cmd_snapshot, "backfill": cmd_backfill, "status": cmd_status,
            "install": cmd_install, "put": cmd_put, "doctor": cmd_doctor, "kept-purged": cmd_kept_purged, "purge": cmd_purge, "unpurge": cmd_unpurge, "ingest": cmd_ingest, "index": cmd_index,
            "backfill-rejections": cmd_backfill_rejections, "rotate": cmd_rotate}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
