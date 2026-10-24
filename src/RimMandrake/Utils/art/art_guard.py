#!/usr/bin/env python3
"""art_guard.py — refuse texture changes the art ledger did not make (ART_VERSION_WRANGLING_1).

Every PNG added, changed or deleted under src/**/Textures/ must be the end of a chain of
`live` events in the art ledger, starting at the file's previous bytes, each link authorized:

  * `ruling_id` naming an owner keep (trust=ruled) of that very sha;
  * a mechanical reason (`artpipe-collect`, `script:<path>`) whose displaced picture was NOT
    owner-kept (a kept picture moves only on his ruling);
  * the ledger's own bookkeeping reason `backfill-observed` (and, for events before ENFORCE_FROM only,
    `retire-duplicate`; from then on a `script:` tag must also name a writer file in the repo).

And the other direction (2026-10-15 review: 18 FlowWorks installs recorded live on 10-07 never reached git, and a
10-14 re-scan relabelled them back): every slot a pushed `live` event or texture change touches must hold, in the
pushed tree, what the folded ledger says (superseded events are fine), and a `backfill-observed` event may not
overwrite a slot the ledger already recorded. `art.py doctor` lists every disagreement in a tree.

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
# Events stamped at or after this are judged by the 2026-10-15 review rules (backfill may not overwrite a recorded
# slot, …); older events keep the rules they were written under, so `range` over history does not re-judge them.
ENFORCE_FROM = "2026-10-15T19:00:00-0700"
ENFORCE_REASONS_FROM = "2026-10-15T20:00:00-0700"     # fix C (reasons), shipped after fix A


def _enforced(ev: dict) -> bool:
    return (ev.get("ts") or "") >= ENFORCE_FROM


def _key(ev: dict) -> tuple[str, str]:
    return L.mod_key(ev["mod"]), L.rel_key(ev["rel"])


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
    if ev.get("sha") is None and ev.get("said"):
        return None                         # a retire on the owner's typed words (artledger.retire)
    if (ev.get("ts") or "") >= ENFORCE_REASONS_FROM:
        # 2026-10-15 review fix C: `retire-duplicate` is hand-typed (no code writes it) and displaced 121 kept
        # pictures; free text after `script:` hid owner authority in a mechanical tag. From ENFORCE_FROM on, only
        # backfill-observed is bookkeeping, and a mechanical tag must name a writer file in the repo.
        if reason == "backfill-observed":
            return None
        if reason == "retire-duplicate":
            if ev.get("said"):
                return None                 # the owner's typed words on the event
            return ("`retire-duplicate` is not an authority — retire through artledger.retire with "
                    "script:<writer path>, or the owner's words / ruling when the picture is kept")
        why = L.mechanical_refusal(reason)
        if why:
            return f"live event has no ruling and no verifiable reason: {why}"
    elif reason in BOOKKEEPING:
        return None
    if L.is_mechanical_reason(reason):
        if ev.get("prev") and idx.protected(ev["prev"]) and not (
                ev.get("sha") is None and L.held_elsewhere(idx, ev["prev"], (ev.get("mod"), ev.get("rel")))):
            return f"mechanical install ({reason}) displaced owner-kept {ev['prev'][:12]}"
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
        # Among links that land on `old`, the LATEST one explains the transition: an earlier unauthorised retire of the same
        # bytes (restored since) must not shadow a later retire made on the owner's words (2026-10-22, GREENTIDE ants).
        cands.sort(key=lambda e: e.get("ts", ""), reverse=True)
        cands.sort(key=lambda e: e.get("prev") != old)
        e = cands[0]
        tried.add(e["id"])
        why = _authorized(e, idx)
        if why:
            return why
        if e.get("reason") == "backfill-observed" and _enforced(e) and any(
                x is not e and (x.get("ts") or "") < (e.get("ts") or "") for x in evs):
            return ("a backfill observation overwrites a slot the ledger already recorded — a re-scan flags drift "
                    "(art.py doctor), it never relabels")
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
            lives.setdefault(_key(ev), []).append(ev)
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
    names = _git(cwd, "ls-tree", "-r", "--name-only", rev, LEDGER_EVENTS + "/").split()
    events, seen = [], set()
    for n in L.order_shard_names(names):   # archives then live tail, per seat (rotation)
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


def added_events(cwd, base: str, head: str) -> list[dict]:
    """Art-ledger events whose lines base..head ADDS (shards are append-only; a rotation's moved lines cancel)."""
    raw = _git(cwd, "diff", "--no-renames", "--no-ext-diff", "-U0", base, head, "--", LEDGER_EVENTS + "/")
    plus, minus = {}, set()
    for ln in raw.splitlines():
        if ln.startswith(("+++", "---")) or not ln[:1] in ("+", "-"):
            continue
        try:
            ev = json.loads(ln[1:])
        except ValueError:
            continue
        if ln[0] == "+":
            plus[ev.get("id")] = ev
        else:
            minus.add(ev.get("id"))
    return [ev for i, ev in plus.items() if i not in minus]


def tree_sha256(cwd, rev: str, paths: list[str]) -> dict:
    """path -> sha256 of its bytes in `rev`'s tree (None when the tree has no such file)."""
    if not paths:
        return {}
    r = subprocess.run(["git", "-C", str(cwd), "cat-file", "--batch-check=%(objectname) %(objecttype)"],
                       input="".join(f"{rev}:{p}\n" for p in paths), capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError("git cat-file --batch-check failed")
    blob = {}
    for p, line in zip(paths, r.stdout.splitlines()):
        f = line.split()
        blob[p] = f[0] if len(f) == 2 and f[1] == "blob" else None
    shas = _sha256_blobs(cwd, [b for b in blob.values() if b])
    return {p: (shas.get(b) if b else None) for p, b in blob.items()}


def expected_at(idx: L.Index, key: tuple[str, str]):
    """(known, sha) — what the folded ledger says the slot holds: a sha, or None for retired."""
    if key in idx.live:
        return True, idx.live[key].get("sha")
    if key in idx._retired:
        return True, None
    return False, None


def check_tree(cwd, idx: L.Index, rev: str, keys) -> list[tuple[str, str]]:
    """[(path, why)] for every slot whose `rev` tree bytes differ from the folded ledger (the event -> PNG half)."""
    want = {}
    for k in keys:
        known, sha = expected_at(idx, k)
        if known:
            want[f"{k[0]}/Textures/{k[1]}"] = sha
    tree = tree_sha256(cwd, rev, sorted(want))
    out = []
    for path, sha in sorted(want.items()):
        got = tree.get(path)
        if got == sha:
            continue
        if sha is None:
            out.append((path, f"the ledger retired this slot but the pushed tree still holds {got[:12]}"))
        elif got is None:
            out.append((path, f"the ledger records {sha[:12]} live here but the pushed tree has no such file — "
                              f"commit the PNG with its event"))
        else:
            out.append((path, f"the ledger records {sha[:12]} live here but the pushed tree holds {got[:12]}"))
    return out


def check_range(cwd, base: str, head: str) -> list[tuple[str, str, str]]:
    """[(commit, path, why)] for base..head, both directions, ledger read at head:
      PNG -> event: every non-merge commit's texture change ends an authorized `live` chain;
      event -> PNG: every slot a `live` event added in the range (or a texture change in the range, merges
      included) names holds, in head's tree, exactly what the folded ledger says — a superseded event is fine."""
    commits = _git(cwd, "rev-list", "--no-merges", "--reverse", f"{base}..{head}").split()
    per = [(c, commit_changes(cwd, c)) for c in commits]
    new_lives = [e for e in added_events(cwd, base, head) if e.get("type") == "live" and e.get("mod") and e.get("rel")]
    if not any(ch for _c, ch in per) and not new_lives:
        return []
    events = ledger_at(cwd, head)
    out = []
    for c, ch in per:
        for path, why in check(ch, events):
            out.append((c, path, why))
    keys = {_key(e) for e in new_lives}
    for path, _o, _n in range_changes(cwd, base, head):
        sp = L.split_texture_path(path)
        if sp:
            keys.add((L.mod_key(sp[0]), L.rel_key(sp[1])))
    idx = L.Index(events)
    by_key: dict = {}
    for ev in events:
        if ev.get("type") == "live" and ev.get("mod") and ev.get("rel"):
            by_key.setdefault(_key(ev), []).append(ev)
    for e in new_lives:                                   # a re-scan relabelling a recorded slot (10-14 shape)
        if e.get("reason") == "backfill-observed" and _enforced(e) and any(
                x.get("id") != e.get("id") and (x.get("ts") or "") < (e.get("ts") or "") for x in by_key.get(_key(e), [])):
            k = _key(e)
            out.append((head, f"{k[0]}/Textures/{k[1]}",
                        "a backfill observation overwrites a slot the ledger already recorded — a re-scan flags "
                        "drift (art.py doctor), it never relabels"))
    flagged = {p for _c, p, _w in out}
    for path, why in check_tree(cwd, idx, head, keys):
        if path not in flagged:
            out.append((head, path, why))
    return out


def range_changes(cwd, base: str, head: str) -> list[tuple[str, str, str]]:
    """Texture PNG paths whose bytes differ between base and head (merge resolutions included)."""
    raw = _git(cwd, "diff", "--no-renames", "--raw", "-z", base, head, "--", "src/").split("\0")
    rows, i = [], 0
    while i < len(raw) - 1:
        if raw[i].startswith(":"):
            f = raw[i][1:].split()
            if is_texture_png(raw[i + 1]):
                rows.append((raw[i + 1], f[2], f[3]))
            i += 2
        else:
            i += 1
    return rows


def doctor(cwd, rev: str = "HEAD") -> list[dict]:
    """Every slot where the folded ledger and `rev`'s committed tree disagree, plus what the working tree holds
    there (an uncommitted install shows as worktree == ledger). Read-only."""
    cwd = Path(cwd)
    idx = L.Index()
    names = _git(cwd, "ls-tree", "-r", "-z", "--name-only", rev, "--", "src/").split("\0")
    tree_paths = {p for p in names if is_texture_png(p)}
    keys = set(idx.live) | set(idx._retired)
    for p in tree_paths:
        sp = L.split_texture_path(p)
        keys.add((L.mod_key(sp[0]), L.rel_key(sp[1])))
    paths = sorted({f"{m}/Textures/{r}" for m, r in keys} | tree_paths)
    tree = {}
    for i in range(0, len(paths), 2000):
        tree.update(tree_sha256(cwd, rev, paths[i:i + 2000]))
    rows = []
    for m, r in sorted(keys):
        path = f"{m}/Textures/{r}"
        known, want = expected_at(idx, (m, r))
        got = tree.get(path)
        if known and got == want:
            continue
        wt_f = cwd / path
        wt = L.sha256_file(wt_f) if wt_f.is_file() else None
        if not known:
            kind = "TREE_UNRECORDED"
        elif want is None:
            kind = "TREE_RETIRED"
        elif got is None:
            kind = "LIVE_NOT_IN_TREE"
        else:
            kind = "LIVE_DIFFERS"
        ev = idx.live.get((m, r)) or idx._retired.get((m, r)) or {}
        rows.append({"kind": kind, "path": path, "ledger": want, "tree": got, "worktree": wt,
                     "uncommitted_install": bool(want and wt == want),
                     "event": {k: ev.get(k) for k in ("id", "ts", "seat", "reason", "prev")} if ev else None})
    return rows


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
