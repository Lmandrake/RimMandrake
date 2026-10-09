#!/usr/bin/env python3
"""artpipe_state.py — operate on the artpipe state dir (outside git since 2026-10-02).

    python3 artpipe_state.py where                      # resolved state dir + per-dir counts
    python3 artpipe_state.py find korrum Brindeth       # prior art/rulings for a subject, before queuing
    python3 artpipe_state.py collect <job_id> --to src/<Mod>/Textures/.../X_east.png [--dry-run]
    python3 artpipe_state.py collect --from-jobs        # every done job carrying "install_to" not yet collected
    python3 artpipe_state.py migrate --from /mnt/d/Luke/dev/RimMandrake/infrastructure/artpipe [--dry-run]

`collect` is how finished art reaches `src/`: the daemon never writes into a
clone (it leaves `<state>/_artsrc/<id>/<id>.png` + `done/<id>.manifest.json`);
a seat runs collect IN ITS OWN CLONE, which installs the PNG at the repo-relative
destination through the art ledger (`artledger.install_file`, reason `artpipe-collect`:
the displaced picture is archived first, and an owner-kept one is never replaced), appends a line to `<state>/collected.jsonl`, and prints the paths
to commit. A job JSON may name its destination in an optional `install_to`
field (repo-relative); otherwise pass `--to`.

`migrate` COPIES an old queue (never deletes from the source) and is safe to
re-run: a job already further along in the destination is left alone, a job
further along in the source replaces the destination's earlier-stage copy
(done/failed > active > pending), and append-only jsonl logs are unioned by
line. Plan: `design/RimMandrake/git_migration_phase5_artpipe_2026-10-02.md`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state_dir  # noqa: E402

STAGE_RANK = {"pending": 0, "active": 1, "done": 2, "failed": 2}
UNION_JSONL = ("registry.jsonl", "throughput.jsonl")
PLAIN_DIRS = ("_artsrc", "_withdrawn", "logs")
SEARCH_DIRS = ("pending", "active", "done", "failed", "_withdrawn")
SEARCH_FILES = ("registry.jsonl", "art_status.json")
# The PRE-MIGRATION artpipe tree (the old Rimworld repo). Its _artsrc holds ~2241
# renders that never moved to the state dir; r31 found wireable art there that
# `find` could not see. Searched by `find` unless --no-legacy.
LEGACY_ROOTS = (Path("/mnt/d/Luke/dev/RimMandrake/infrastructure/artpipe"),)


# ---------------------------------------------------------------- where

def cmd_where(args) -> int:
    root = args.state
    print(f"state dir: {root}  (${state_dir.ENV_VAR}={os.environ.get(state_dir.ENV_VAR, '') or 'unset'})")
    if not root.is_dir():
        print("  MISSING — nothing here to count (an absent dir is not an empty queue)")
        return 1
    for d in (*state_dir.QUEUE_DIRS, *PLAIN_DIRS):
        p = root / d
        if not p.is_dir():
            print(f"  {d:<11} MISSING")
            continue
        jobs = sum(1 for f in p.iterdir() if f.suffix == ".json" and not f.name.endswith(".manifest.json"))
        print(f"  {d:<11} {jobs:>6} job json   {sum(1 for _ in p.iterdir()):>6} entries")
    for f in (*UNION_JSONL, "art_status.json", "collected.jsonl"):
        p = root / f
        print(f"  {f:<17} " + (f"{p.stat().st_size} bytes" if p.is_file() else "absent"))
    return 0


# ---------------------------------------------------------------- find

def _resolver(root: Path):
    """(subject module, World over THIS state dir), or None when the resolver cannot load (said, not silent)."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "art"))
        import subject as S
        return S, S.World(artpipe_root=root)
    except Exception as e:                       # noqa: BLE001 — a find must still print its raw hits
        print(f"resolver unavailable ({e.__class__.__name__}: {e}) — raw text hits only")
        return None


def _print_resolved(resolver, term: str, limit: int) -> None:
    """ART_SUBJECT_RESOLVER_1: what subject.py says the term IS and which finished art/canon belongs to it,
    each hit with its confidence. The raw substring scan below it is the older, noisier view."""
    S, w = resolver
    a, c = S.resolve_art(term, w), S.resolve_canon(term, w)
    nb = sum(1 for x in a["columns"] if x["confidence"] == "bound")
    print(f"{term}: resolves to {a['subject']}"
          + (f" (originals {', '.join(a['originals'])})" if a["originals"] else "")
          + f" — {nb} bound, {len(a['columns']) - nb} name-matched; canon "
          + (f"{c['slug']} [{c['match']}, {c['confidence']}]" if c["slug"] else "none"))
    for x in a["columns"][:limit]:
        print(f"  {x['confidence']:12} {x['kind']:6} {x['ref'][:44]:44} {x['evidence']}")
    if len(a["columns"]) > limit:
        print(f"  … {len(a['columns']) - limit} more resolved")
    if not a["columns"]:
        print(f"  none — {S.describe_none(a['searched'])}")


def cmd_find(args) -> int:
    root = state_dir.require(args.state)
    terms = [t.lower() for t in args.terms]
    hits: dict[str, list[str]] = {t: [] for t in terms}
    scanned = 0
    for d in SEARCH_DIRS:
        p = root / d
        if not p.is_dir():
            continue
        for f in p.iterdir():
            scanned += 1
            name = f.name.lower()
            body = None
            for t in terms:
                if t in name:
                    hits[t].append(f"{d}/{f.name}")
                elif not args.names_only and f.suffix == ".json":
                    if body is None:
                        try:
                            body = f.read_text(errors="replace").lower()
                        except OSError:
                            body = ""
                    if t in body:
                        hits[t].append(f"{d}/{f.name} (content)")
    artsrc = root / "_artsrc"
    if artsrc.is_dir():
        for sub in artsrc.iterdir():
            scanned += 1
            for t in terms:
                if t in sub.name.lower():
                    hits[t].append(f"_artsrc/{sub.name}/")
    for fn in SEARCH_FILES:
        p = root / fn
        if not p.is_file():
            continue
        n = {t: 0 for t in terms}
        with p.open(errors="replace") as fh:
            for line in fh:
                low = line.lower()
                for t in terms:
                    if t in low:
                        n[t] += 1
        for t in terms:
            if n[t]:
                hits[t].append(f"{fn}: {n[t]} line(s)")
    legacy_scanned = []
    for lroot in ([] if args.no_legacy else (args.legacy or list(LEGACY_ROOTS))):
        lroot = Path(lroot)
        if not lroot.is_dir():
            print(f"legacy root {lroot}: MISSING (not searched)")
            continue
        legacy_scanned.append(lroot)
        for d in ("_artsrc", *SEARCH_DIRS):
            p = lroot / d
            if not p.is_dir():
                continue
            for f in p.iterdir():
                scanned += 1
                for t in terms:
                    if t in f.name.lower():
                        hits[t].append(f"LEGACY {lroot}/{d}/{f.name}" + ("/" if f.is_dir() else ""))
    print(f"searched {scanned} entries under {root}"
          + "".join(f" + legacy {r}" for r in legacy_scanned))
    resolver = None if args.no_resolve else _resolver(root)
    for t in args.terms:
        if resolver is not None:
            _print_resolved(resolver, t, args.limit)
    for t in terms:
        print(f"{t}: {len(hits[t])} raw text hit(s) (substring of names/bodies; may include false hits)")
        for h in hits[t][: args.limit]:
            print(f"  {h}")
        if len(hits[t]) > args.limit:
            print(f"  … {len(hits[t]) - args.limit} more")
    print("also check Transient/*.decisions.json in the repo for owner rulings on that art")
    return 0


# ---------------------------------------------------------------- collect

def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _collected(root: Path) -> set[tuple[str, str]]:
    p = root / "collected.jsonl"
    out = set()
    if p.is_file():
        for line in p.read_text().splitlines():
            try:
                r = json.loads(line)
                out.add((r["job_id"], r["dest"]))
            except (ValueError, KeyError):
                continue
    return out


def _artledger(repo: Path):
    """artledger bound to `repo`'s src/ and ledger (another clone, or a selftest fixture)."""
    os.environ.setdefault("ART_SRC_ROOT", str(repo / "src"))
    os.environ.setdefault("ART_LEDGER_DIR", str(repo / "infrastructure" / "state" / "art"))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "art"))
    import artledger
    return artledger


def collect_one(root: Path, repo: Path, job_id: str, dest_rel: str, dry_run: bool,
                allow_failed: bool = False) -> Path:
    dest_rel = dest_rel.lstrip("/")
    dest = (repo / dest_rel).resolve()
    if not str(dest).startswith(str((repo / "src").resolve()) + os.sep):
        raise SystemExit(f"collect: {dest_rel} is not under this clone's src/ — refusing")
    png = root / "_artsrc" / job_id / f"{job_id}.png"
    if not png.is_file():
        raise SystemExit(f"collect: no output PNG for {job_id} at {png}")
    if not (root / "done" / f"{job_id}.manifest.json").is_file() and not allow_failed:
        raise SystemExit(f"collect: {job_id} has no done/ manifest (failed or unfinished) — "
                         f"pass --allow-failed to take it anyway")
    if dry_run:
        return dest
    L = _artledger(repo)
    try:                     # the art ledger is the only writer into Textures (ART_VERSION_WRANGLING_1)
        L.install_file(dest, png, reason="artpipe-collect", provenance={"kind": "artpipe", "job": job_id})
    except L.Refused as e:
        raise SystemExit(f"collect: {job_id} -> {dest_rel} REFUSED by the art ledger: {e}")
    rec = {"job_id": job_id, "dest": dest_rel, "sha256": _sha256(dest),
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "clone": str(repo),
           "host": socket.gethostname()}
    with (root / "collected.jsonl").open("a") as fh:
        fh.write(json.dumps(rec) + "\n")
    return dest


def cmd_collect(args) -> int:
    root = state_dir.require(args.state)
    repo = args.repo.resolve()
    pairs: list[tuple[str, str]] = []
    if args.from_jobs:
        done = _collected(root)
        for f in sorted((root / "done").glob("*.json")):
            if f.name.endswith(".manifest.json"):
                continue
            try:
                job = json.loads(f.read_text())
            except (OSError, ValueError):
                continue
            dest = job.get("install_to")
            if dest and (job["id"], dest) not in done:
                pairs.append((job["id"], dest))
    else:
        if not args.job_id or not args.to:
            raise SystemExit("collect: give <job_id> --to <repo-relative path>, or --from-jobs")
        pairs.append((args.job_id, args.to))
    written = [collect_one(root, repo, j, d, args.dry_run, args.allow_failed) for j, d in pairs]
    verb = "would copy" if args.dry_run else "collected"
    print(f"{verb} {len(written)} file(s); commit with explicit paths (the art-ledger shard too):")
    for p in written:
        print(f"  {p.relative_to(repo)}")
    if written and not args.dry_run:
        print(f"  infrastructure/state/art/events/{_artledger(repo).seat()}.jsonl")
    return 0


# ---------------------------------------------------------------- migrate

def _same(a: Path, b: Path) -> bool:
    sa, sb = a.stat(), b.stat()
    return sa.st_size == sb.st_size and int(sa.st_mtime) == int(sb.st_mtime)


def _copy(src: Path, dst: Path, dry: bool, stats: dict, key: str) -> None:
    try:
        if dst.exists() and _same(src, dst):
            return
    except FileNotFoundError:
        return
    if not dry:
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(src, dst)
        except FileNotFoundError:  # a live daemon moved it mid-walk; the next run picks it up
            stats["vanished_mid_copy"] = stats.get("vanished_mid_copy", 0) + 1
            return
    stats[key] = stats.get(key, 0) + 1


def _where_is(root: Path, name: str) -> tuple[str, int] | None:
    best = None
    for d, r in STAGE_RANK.items():
        if (root / d / name).exists() and (best is None or r > best[1]):
            best = (d, r)
    return best


def migrate(src: Path, dst: Path, dry: bool) -> dict:
    stats: dict = {}
    # queue dirs: stage precedence, never regress a job
    for d, rank in STAGE_RANK.items():
        sd = src / d
        if not sd.is_dir():
            continue
        if not dry:
            (dst / d).mkdir(parents=True, exist_ok=True)
        for f in sd.iterdir():
            if not f.is_file():
                continue
            if f.name.endswith(".manifest.json") or not f.name.endswith(".json"):
                _copy(f, dst / d / f.name, dry, stats, f"{d}/other")
                continue
            here = _where_is(dst, f.name)
            if here is not None and here[1] > rank:
                stats["kept_further_along"] = stats.get("kept_further_along", 0) + 1
                continue
            _copy(f, dst / d / f.name, dry, stats, f"{d}/jobs")
            if here is not None and here[1] < rank:
                stats["advanced"] = stats.get("advanced", 0) + 1
                if not dry:
                    (dst / here[0] / f.name).unlink(missing_ok=True)
    # plain trees
    for d in PLAIN_DIRS:
        sd = src / d
        if not sd.is_dir():
            continue
        for dirpath, _dirs, files in os.walk(sd):
            for fn in files:
                s = Path(dirpath) / fn
                _copy(s, dst / s.relative_to(src), dry, stats, d)
    # top-level files
    for f in src.iterdir():
        if not f.is_file():
            continue
        if f.name in UNION_JSONL:
            t = dst / f.name
            have = set(t.read_text(errors="replace").splitlines()) if t.exists() else set()
            new = [ln for ln in f.read_text(errors="replace").splitlines() if ln and ln not in have]
            if new:
                stats[f.name] = len(new)
                if not dry:
                    with t.open("a") as fh:
                        fh.writelines(ln + "\n" for ln in new)
        elif f.name.endswith(".lock"):
            continue
        elif f.name.startswith("daemon_run_") or f.name.startswith("art_status."):
            t = dst / f.name
            if not t.exists() or f.stat().st_mtime > t.stat().st_mtime:
                _copy(f, t, dry, stats, "top")
    return stats


def cmd_migrate(args) -> int:
    src = args.src.resolve()
    if not (src / "done").is_dir():
        raise SystemExit(f"migrate: {src} has no done/ — not an artpipe queue")
    dst = args.state
    if dst.resolve() == src:
        raise SystemExit("migrate: source and state dir are the same")
    stats = migrate(src, dst, args.dry_run)
    print(("DRY RUN " if args.dry_run else "") + f"migrate {src} -> {dst}")
    for k in sorted(stats):
        print(f"  {k}: {stats[k]}")
    if not stats:
        print("  nothing to do (already in sync)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--state", type=Path, default=state_dir.STATE_ROOT,
                    help=f"state dir (default: resolved, now {state_dir.STATE_ROOT})")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("where")
    f = sub.add_parser("find")
    f.add_argument("terms", nargs="+")
    f.add_argument("--names-only", action="store_true", help="skip reading job JSON bodies")
    f.add_argument("--limit", type=int, default=15)
    f.add_argument("--legacy", type=Path, action="append",
                   help="pre-migration artpipe root to also search by name (default: LEGACY_ROOTS)")
    f.add_argument("--no-legacy", action="store_true")
    f.add_argument("--no-resolve", action="store_true", help="skip the subject.py resolution; raw substring hits only")
    c = sub.add_parser("collect")
    c.add_argument("job_id", nargs="?")
    c.add_argument("--to", help="repo-relative destination under src/")
    c.add_argument("--from-jobs", action="store_true")
    c.add_argument("--repo", type=Path, default=state_dir.REPO_ROOT,
                   help="the clone to copy into (default: the clone this script lives in)")
    c.add_argument("--allow-failed", action="store_true")
    c.add_argument("--dry-run", action="store_true")
    m = sub.add_parser("migrate")
    m.add_argument("--from", dest="src", type=Path, required=True)
    m.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    return {"where": cmd_where, "find": cmd_find, "collect": cmd_collect,
            "migrate": cmd_migrate}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
