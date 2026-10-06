#!/usr/bin/env python3
"""art_guard.py — refuse texture changes the art ledger did not make (ART_VERSION_WRANGLING_1).

Every PNG added, changed or deleted under src/**/Textures/ must be the end of a chain of
`live` events in the art ledger, starting at the file's previous bytes, each link authorized:

  * `ruling_id` naming an owner keep (trust=ruled) of that very sha;
  * a mechanical reason (`artpipe-collect`, `script:<path>`) whose displaced picture was NOT
    owner-kept (a kept picture moves only on his ruling);
  * the ledger's own bookkeeping reasons (`backfill-observed`, `retire-duplicate`).

So a raw `cp`/`Image.save` into Textures + commit is refused, and a hand-appended `live` line
whose `prev` skips a transition is refused too. The way to make a change legal is
`art.py install` (or a writer calling `artledger.install_bytes`), which writes the event.

Used by `.claude/hooks/block_unledgered_texture.py` (PreToolUse on commit/publish/push) and
by `infrastructure/githooks/pre-push` (via that hook's `--git-pre-push`). CLI for by-hand use:

    art_guard.py range <base>..<head>      check each non-merge commit in the range
    art_guard.py worktree [<path>...]      check uncommitted PNG changes (default: all of src/)
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artledger as L  # noqa: E402

LEDGER_EVENTS = "infrastructure/state/art/events"
BOOKKEEPING = {"backfill-observed", "retire-duplicate"}


def is_texture_png(path: str) -> bool:
    p = path.replace("\\", "/")
    return p.startswith("src/") and "/Textures/" in p and p.lower().endswith(".png")


def _git(cwd, *args, input=None, text=True) -> str:
    r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=text,
                       input=input, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:3])}: {r.stderr.strip()[:300]}")
    return r.stdout


# ───────────────────────────────────────────────────────────── the rule ──

def _authorized(ev: dict, idx: L.Index) -> str | None:
    """None if this live event is an authorized transition, else the reason it is not."""
    reason = ev.get("reason") or ""
    if ev.get("ruling_id"):
        r = next((r for r in idx.rulings if r["id"] == ev["ruling_id"]), None)
        if not r:
            return f"names ruling {ev['ruling_id']} which is not in the ledger"
        tg = r.get("target") or {}
        if ev.get("sha") not in (tg.get("shas") or []) + ([tg["sha"]] if tg.get("sha") else []):
            return f"ruling {ev['ruling_id']} does not name {str(ev.get('sha'))[:12]}"
        if r.get("by") != "owner" or r.get("trust") not in L.TRUST_PROTECTS \
                or L.normalise_verdict(r.get("verdict")) != "keep":
            return f"ruling {ev['ruling_id']} is not an owner keep with real provenance"
        return None
    if reason in BOOKKEEPING:
        return None
    if ev.get("sha") is None and ev.get("said"):
        return None                         # a retire on the owner's typed words (artledger.retire)
    if L.is_mechanical_reason(reason):
        if ev.get("prev") and idx.protected(ev["prev"]):
            return f"mechanical install ({reason}) displaced owner-kept {ev['prev'][:12]}"
        if ev.get("sha") is None and not ev.get("said") and ev.get("prev") and idx.protected(ev["prev"]):
            return "retired an owner-kept picture without his words"
        return None
    return f"live event has no ruling and no recognised reason ({reason!r})"


def check_change(idx: L.Index, lives: dict, path: str, old: str | None, new: str | None) -> str | None:
    """None if the ledger explains old -> new at `path`, else a one-line reason."""
    if old == new:
        return None
    sp = L.split_texture_path(path)
    if not sp:
        return None
    evs = lives.get(sp, [])
    if not evs:
        return "no art-ledger record for this file"
    cur, depth = new, 0
    tried = set()
    while depth < 64:
        cands = [e for e in evs if e.get("sha") == cur and e["id"] not in tried]
        if cur is None:
            cands = [e for e in cands if e.get("prev") == old] or cands
        if not cands:
            return (f"ledger has no `live` event for these bytes ({(cur or 'deletion')[:12]})"
                    if depth == 0 else
                    f"ledger chain breaks at {str(cur)[:12]} — a transition was skipped")
        # prefer the link that lands on `old` directly
        cands.sort(key=lambda e: (e.get("prev") != old, e.get("ts", "")))
        e = cands[0]
        tried.add(e["id"])
        why = _authorized(e, idx)
        if why:
            return why
        if e.get("prev") == old:
            return None
        if e.get("prev") is None and e.get("reason") == "backfill-observed" and old is not None:
            return "only a backfill observation records these bytes; the change from the committed picture is unrecorded"
        cur = e.get("prev")
        depth += 1
    return "ledger chain too long or cyclic"


def check(changes, events: list[dict]) -> list[tuple[str, str]]:
    """changes: [(path, old_sha256|None, new_sha256|None)]. Returns [(path, why)]."""
    idx = L.Index(events)
    lives: dict = {}
    for ev in idx.events:
        if ev.get("type") == "live":
            lives.setdefault((ev["mod"], ev["rel"]), []).append(ev)
    out = []
    for path, old, new in changes:
        why = check_change(idx, lives, path, old, new)
        if why:
            out.append((path, why))
    return out


# ──────────────────────────────────────────────────────── change sources ──

def _sha256_blobs(cwd, blob_ids: list[str]) -> dict:
    """git blob id -> sha256 of its bytes, one `cat-file --batch` for all."""
    ids = sorted({b for b in blob_ids if b and set(b) != {"0"}})
    if not ids:
        return {}
    r = subprocess.run(["git", "-C", str(cwd), "cat-file", "--batch"], input=("\n".join(ids) + "\n").encode(),
                       capture_output=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError("git cat-file --batch failed")
    out, buf, i = {}, r.stdout, 0
    for bid in ids:
        nl = buf.index(b"\n", i)
        hdr = buf[i:nl].decode().split()
        if len(hdr) < 3 or hdr[1] != "blob":
            raise RuntimeError(f"blob {bid} unreadable: {hdr}")
        size = int(hdr[2])
        out[bid] = hashlib.sha256(buf[nl + 1:nl + 1 + size]).hexdigest()
        i = nl + 1 + size + 1
    return out


def commit_changes(cwd, commit: str) -> list[tuple[str, str | None, str | None]]:
    """Texture PNG changes a non-merge commit makes against its first parent."""
    parents = _git(cwd, "rev-list", "--parents", "-n", "1", commit).split()[1:]
    args = ["diff-tree", "-r", "--no-renames", "-z", "--raw"]
    args += [parents[0], commit] if parents else ["--root", commit]
    raw = _git(cwd, *args).split("\0")
    rows = []
    i = 0
    while i < len(raw) - 1:
        meta = raw[i]
        if not meta.startswith(":"):
            i += 1
            continue
        path = raw[i + 1]
        i += 2
        f = meta[1:].split()
        if is_texture_png(path):
            rows.append((path, f[2], f[3]))
    shas = _sha256_blobs(cwd, [r[1] for r in rows] + [r[2] for r in rows])
    return [(p, shas.get(a), shas.get(b)) for p, a, b in rows]


def ledger_at(cwd, rev: str) -> list[dict]:
    """Every art-ledger event as committed at `rev` (the union of its shards)."""
    names = _git(cwd, "ls-tree", "--name-only", rev, LEDGER_EVENTS + "/").split()
    events, seen = [], set()
    for n in names:
        if not n.endswith(".jsonl"):
            continue
        for k, line in enumerate(_git(cwd, "show", f"{rev}:{n}").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except ValueError:
                raise ValueError(f"{n}@{rev[:10]}:{k}: unparseable art-ledger line") from None
            if ev.get("id") in seen:
                continue
            seen.add(ev.get("id"))
            events.append(ev)
    return events


def check_range(cwd, base: str, head: str) -> list[tuple[str, str, str]]:
    """[(commit, path, why)] for every non-merge commit in base..head. Ledger read at head."""
    commits = _git(cwd, "rev-list", "--no-merges", "--reverse", f"{base}..{head}").split()
    per = [(c, commit_changes(cwd, c)) for c in commits]
    if not any(ch for _c, ch in per):
        return []
    events = ledger_at(cwd, head)
    out = []
    for c, ch in per:
        for path, why in check(ch, events):
            out.append((c, path, why))
    return out


def worktree_changes(cwd, paths: list[str] | None = None) -> list[tuple[str, str | None, str | None]]:
    """Uncommitted texture PNG changes (vs HEAD) under `paths` (default src/)."""
    root = Path(_git(cwd, "rev-parse", "--show-toplevel").strip())
    out = _git(cwd, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--no-renames",
               "--", *(paths or ["src/"]))
    rows = []
    for ent in out.split("\0"):
        if len(ent) < 4:
            continue
        path = ent[3:]
        if not is_texture_png(path):
            continue
        old = None
        try:
            bid = _git(root, "rev-parse", "-q", "--verify", f"HEAD:{path}").strip()
            old = _sha256_blobs(root, [bid]).get(bid)
        except RuntimeError:
            old = None
        f = root / path
        new = L.sha256_file(f) if f.is_file() else None
        rows.append((path, old, new))
    return rows


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in ("range", "worktree"):
        print(__doc__)
        return 2
    cwd = Path.cwd()
    if argv[0] == "range":
        base, head = argv[1].split("..", 1)
        bad = check_range(cwd, base, head or "HEAD")
        for c, p, why in bad:
            print(f"UNLEDGERED {c[:10]} {p}: {why}")
    else:
        ch = worktree_changes(cwd, argv[1:] or None)
        bad = [("worktree", p, why) for p, why in check(ch, L.read_events())]
        for _c, p, why in bad:
            print(f"UNLEDGERED {p}: {why}")
    print(f"art guard: {len(bad)} unledgered texture change(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
