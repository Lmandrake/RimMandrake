#!/usr/bin/env python3
"""scratch_clone.py — the shared object store and the ONE way to make a throwaway clone.

SEAT_MEMORY_CLONES_DRIVES_1, design/RimMandrake/memory_clones_drives_2026-10-08.md §4 items 1-2,
§7 phase 2; what was built and how to judge it: design/RimMandrake/objstore_trial_2026-10-08.md.
Owner, 2026-10-08: "try it out, but let's wire it to keep data on its operation so we can judge
if it was a good idea later."

    scratch_clone.py clone <purpose> [--name N] [--checkout | --sparse P ...] [--fetch] [--dissociate]
    scratch_clone.py init        create the store (hard-links the mirror's packs: ~0 bytes, instant)
    scratch_clone.py refresh     fetch the mirror's origin/main into the store
    scratch_clone.py sample      periodic record (rm-objstore.timer): store size, borrowers, fsck, df
    scratch_clone.py baseline    time one real full copy of the store, for the time-saved column
    scratch_clone.py report      the verdict table — what the owner reads

The store is /home/mandrake/rm/store.git: a bare repo owned by NO working tree, fed only by
`git fetch` from /home/mandrake/rm/mirror.git. A scratch clone is `git clone --shared` of it, so
its objects/info/alternates names the STORE — never bench or foundry, whose `git gc --prune` is
what could silently corrupt the six borrowers found on 10-08 (headline finding #8).

Why a seat gc cannot hurt a borrower any more, and why the store's own gc cannot either:
  - borrowers point at the store, never at a seat clone;
  - the store sets gc.auto=0, gc.pruneExpire=never, reflogs kept forever with
    core.logAllRefUpdates=always — every tip it ever held stays reachable, so even a manual
    `git gc` there drops nothing a borrower could need;
  - init hard-links the mirror's packs; when the mirror repacks and deletes its names, the
    store's links keep the data.

Telemetry lives outside git in ~/.local/state/rm-objstore/ (XDG_STATE_HOME honoured):
  uses.jsonl       one record per `clone` call, success or failure
  samples.jsonl    one record per `sample` run
  incidents.jsonl  a borrower whose objects stopped resolving (the corruption the store exists to stop)
  baseline.jsonl   measured full-copy times, used to compute time saved

Env overrides (the selftest uses them): RM_OBJSTORE, RM_OBJSTORE_SEED, RM_SCRATCH_ROOT,
RM_OBJSTORE_STATE, RM_OBJSTORE_SCAN (os.pathsep-separated glob patterns), RM_SEAT.
"""
from __future__ import annotations

import argparse
import fcntl
import glob
import json
import os
import random
import shutil
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

RM = Path("/home/mandrake/rm")
ORIGIN_URL = "git@github.com:Lmandrake/RimMandrake.git"
SEED_REF = "refs/remotes/origin/main"   # mirror.git's layout (mirror.py)
STORE_REF = "refs/heads/main"
STORE_CONFIG = {
    "gc.auto": "0",
    "gc.autoPackLimit": "0",
    "gc.pruneExpire": "never",
    "gc.worktreePruneExpire": "never",
    "gc.reflogExpire": "never",
    "gc.reflogExpireUnreachable": "never",
    "core.logAllRefUpdates": "always",
    "objstore.role": "shared object store; borrowers via alternates; never prune (scratch_clone.py)",
}
SEATS = ("bench", "foundry")


def store_path() -> Path:
    return Path(os.environ.get("RM_OBJSTORE", RM / "store.git"))


def seed_path() -> Path:
    return Path(os.environ.get("RM_OBJSTORE_SEED", RM / "mirror.git"))


def scratch_root() -> Path:
    return Path(os.environ.get("RM_SCRATCH_ROOT", RM / "scratch"))


def state_dir() -> Path:
    if os.environ.get("RM_OBJSTORE_STATE"):
        d = Path(os.environ["RM_OBJSTORE_STATE"])
    else:
        d = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state") / "rm-objstore"
    d.mkdir(parents=True, exist_ok=True)
    return d


def scan_patterns() -> list[str]:
    env = os.environ.get("RM_OBJSTORE_SCAN")
    if env:
        return [p for p in env.split(os.pathsep) if p]
    h = str(Path.home())
    return [f"{RM}/*", f"{RM}/scratch/*/*", f"{RM}/_quarantine/*/*", f"{h}/wt/*", f"{h}/.cache/*"]


def seat() -> str:
    if os.environ.get("RM_SEAT"):
        return os.environ["RM_SEAT"]
    try:
        for line in Path("/proc/self/cgroup").read_text().splitlines():
            for part in line.split("/"):
                if part.startswith("claude-seat-"):
                    return part[len("claude-seat-"):].rsplit("-", 1)[0]
    except OSError:
        pass
    return "UNKNOWN"


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def append(name: str, rec: dict) -> None:
    with open(state_dir() / name, "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")


def read_jsonl(name: str) -> list[dict]:
    p = state_dir() / name
    out = []
    if p.exists():
        for line in p.read_text().splitlines():
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def git(*args, cwd=None, check=True, timeout=None) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {(r.stderr or r.stdout).strip()[:400]}")
    return r.stdout.strip()


@contextmanager
def store_lock():
    p = store_path().parent / (store_path().name + ".lock")
    with open(p, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield


def own_bytes(root: Path) -> tuple[int, int]:
    """(bytes only this tree holds, bytes hard-linked with something else). Allocated blocks."""
    own = linked = 0
    for dp, _dn, fn in os.walk(root):
        for n in fn:
            try:
                st = os.lstat(os.path.join(dp, n))
            except OSError:
                continue
            b = st.st_blocks * 512
            if st.st_nlink > 1:
                linked += b
            else:
                own += b
    return own, linked


def store_objects() -> dict:
    """count-objects of the store: what a full clone's .git/objects would hold."""
    kv = {}
    for line in git("--git-dir", str(store_path()), "count-objects", "-v").splitlines():
        k, _, v = line.partition(":")
        kv[k.strip()] = int(v.strip()) if v.strip().isdigit() else v.strip()
    return {"objects": kv.get("count", 0) + kv.get("in-pack", 0),
            "bytes": (kv.get("size", 0) + kv.get("size-pack", 0)) * 1024}


# ---------------------------------------------------------------- store

def init() -> dict:
    st, seed = store_path(), seed_path()
    if (st / "HEAD").exists():
        configure()
        return {"created": False}
    git("init", "-q", "--bare", "-b", "main", str(st))
    configure()
    linked = 0
    sp = seed / "objects" / "pack"
    if sp.is_dir():
        for f in sorted(sp.glob("pack-*")):
            if f.suffix in (".pack", ".idx", ".rev"):
                try:
                    os.link(f, st / "objects" / "pack" / f.name)
                    linked += 1
                except OSError:
                    pass
    # Point the ref at the seed's tip BEFORE fetching: a fetch into a ref-less repo negotiates
    # nothing and re-sends every object (measured 10-08: a 6 GB duplicate next to the links).
    try:
        tip = git("--git-dir", str(seed), "rev-parse", "--verify", SEED_REF)
        git("--git-dir", str(st), "cat-file", "-e", tip + "^{commit}")
        git("--git-dir", str(st), "update-ref", STORE_REF, tip)
    except RuntimeError:
        pass
    refresh(lock=False)
    return {"created": True, "packs_linked": linked}


def configure() -> None:
    for k, v in STORE_CONFIG.items():
        git("--git-dir", str(store_path()), "config", k, v)


def refresh(lock: bool = True) -> dict:
    t0 = time.time()

    def _do():
        git("--git-dir", str(store_path()), "fetch", "-q", "--no-tags", str(seed_path()),
            f"+{SEED_REF}:{STORE_REF}", timeout=600)
    if lock:
        with store_lock():
            _do()
    else:
        _do()
    return {"refresh_s": round(time.time() - t0, 2),
            "head": git("--git-dir", str(store_path()), "rev-parse", STORE_REF)}


# ---------------------------------------------------------------- clone

def clone(purpose: str, name: str | None, checkout: bool, sparse: list[str], fetch: bool,
          dissociate: bool) -> int:
    s = seat()
    name = name or f"{purpose.replace(' ', '-')[:40]}-{time.strftime('%Y%m%d-%H%M%S')}"
    dest = scratch_root() / s / name
    mode = "sparse" if sparse else ("checkout" if checkout else "no-checkout")
    rec = {"ts": now_iso(), "seat": s, "purpose": purpose, "path": str(dest), "mode": mode,
           "dissociate": dissociate, "fetch": fetch, "ok": False, "error": None}
    t0 = time.time()
    try:
        if dest.exists():
            raise RuntimeError(f"{dest} already exists")
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not (store_path() / "HEAD").exists():
            rec["init"] = init()
        try:
            rec.update(refresh())
        except Exception as e:  # a stale store still clones; the clone can --fetch the rest
            rec["refresh_error"] = str(e)[:300]
        so = store_objects()
        t1 = time.time()
        if dissociate:   # independent copy: local clone hard-links packs, no alternates
            git("clone", "-q", "--no-checkout", str(store_path()), str(dest))
        else:
            git("clone", "-q", "--shared", "--no-checkout", str(store_path()), str(dest))
        rec["clone_s"] = round(time.time() - t1, 2)
        git("remote", "set-url", "origin", ORIGIN_URL, cwd=dest)
        git("config", "core.hooksPath", "infrastructure/githooks", cwd=dest)
        if fetch:
            t2 = time.time()
            git("fetch", "-q", "origin", cwd=dest, timeout=900)
            git("update-ref", "refs/heads/main", "refs/remotes/origin/main", cwd=dest)
            rec["fetch_s"] = round(time.time() - t2, 2)
        t3 = time.time()
        if sparse:
            git("sparse-checkout", "set", "--cone", *sparse, cwd=dest)
        if sparse or checkout:
            git("read-tree", "-mu", "HEAD", cwd=dest)
        rec["checkout_s"] = round(time.time() - t3, 2)
        alt = dest / ".git" / "objects" / "info" / "alternates"
        rec["alternates"] = alt.read_text().strip() if alt.exists() else None
        gown, glinked = own_bytes(dest / ".git")
        wt = sum(own_bytes(dest)) - gown - glinked
        rec.update({
            "head": git("rev-parse", "HEAD", cwd=dest),
            "git_dir_own_bytes": gown, "git_dir_hardlinked_bytes": glinked,
            "worktree_bytes": wt,
            "full_clone_objects_bytes": so["bytes"],
            "full_clone_bytes": so["bytes"] + wt,
            "objects_borrowed": 0 if dissociate else so["objects"],
            "ok": True,
        })
        print(dest)
        return 0
    except Exception as e:
        rec["error"] = str(e)[:500]
        print(f"scratch_clone: FAILED: {rec['error']}", file=sys.stderr)
        return 1
    finally:
        rec["wall_s"] = round(time.time() - t0, 2)
        append("uses.jsonl", rec)


# ---------------------------------------------------------------- periodic sample

def find_borrowers() -> list[dict]:
    seen, out = set(), []
    for pat in scan_patterns():
        for d in glob.glob(pat):
            for alt in (Path(d) / ".git/objects/info/alternates", Path(d) / "objects/info/alternates"):
                if alt.is_file() and str(alt) not in seen:
                    seen.add(str(alt))
                    try:
                        targets = [t.strip() for t in alt.read_text().splitlines() if t.strip()]
                    except OSError:
                        continue
                    out.append({"repo": d, "alternates": targets, "kind": classify(targets)})
    return out


def classify(targets: list[str]) -> str:
    st = os.path.realpath(store_path() / "objects")
    real = [os.path.realpath(t) for t in targets]
    if st in real:
        return "store"
    for t in real:
        for s in SEATS:
            if t.startswith(str(RM / s) + "/"):
                return "seat"
    return "other"


def borrower_ok(repo: str, deep: bool) -> tuple[bool, str]:
    try:
        git("-C", repo, "cat-file", "-e", "HEAD^{tree}", timeout=60)
        if deep:
            git("-C", repo, "fsck", "--connectivity-only", "--no-progress", timeout=300)
        return True, ""
    except Exception as e:
        return False, str(e)[:300]


def sample() -> dict:
    rec = {"ts": now_iso()}
    st = store_path()
    rec["store_exists"] = (st / "HEAD").exists()
    if rec["store_exists"]:
        try:
            rec.update(refresh())
        except Exception as e:
            rec["refresh_error"] = str(e)[:300]
        own, linked = own_bytes(st)
        rec.update({"store_own_bytes": own, "store_hardlinked_bytes": linked})
        try:
            rec["store_objects"] = store_objects()["objects"]
        except Exception as e:
            rec["store_objects_error"] = str(e)[:300]
    bs = find_borrowers()
    on_store = [b for b in bs if b["kind"] == "store"]
    rec.update({"borrowers_store": len(on_store),
                "borrowers_seat": len([b for b in bs if b["kind"] == "seat"]),
                "borrowers_other": len([b for b in bs if b["kind"] == "other"]),
                "borrowers_seat_paths": [b["repo"] for b in bs if b["kind"] == "seat"]})
    deep = random.choice(on_store)["repo"] if on_store else None
    bad = []
    t0 = time.time()
    for b in on_store:
        ok, err = borrower_ok(b["repo"], deep=(b["repo"] == deep))
        if not ok:
            bad.append(b["repo"])
            append("incidents.jsonl", {"ts": rec["ts"], "repo": b["repo"], "error": err,
                                       "alternates": b["alternates"], "deep": b["repo"] == deep})
    rec.update({"check_s": round(time.time() - t0, 2), "fsck_sampled": deep, "borrowers_broken": bad})
    vs = os.statvfs(str(RM if RM.exists() else Path.home()))
    rec["disk_free_bytes"] = vs.f_bavail * vs.f_frsize
    append("samples.jsonl", rec)
    return rec


def baseline() -> dict:
    """One real full copy of the store (`--no-local`: objects re-packed and written, as a network
    clone would, minus the network) — a LOWER bound on what a non-borrowing clone costs."""
    dest = scratch_root() / seat() / f"_objstore_baseline_{os.getpid()}"
    t0 = time.time()
    try:
        git("clone", "-q", "--no-local", "--no-checkout", str(store_path()), str(dest), timeout=3600)
        rec = {"ts": now_iso(), "full_clone_s": round(time.time() - t0, 2),
               "full_git_dir_bytes": sum(own_bytes(dest / ".git")), "method": "clone --no-local --no-checkout"}
    finally:
        shutil.rmtree(dest, ignore_errors=True)
    append("baseline.jsonl", rec)
    return rec


# ---------------------------------------------------------------- report

def gb(n) -> str:
    return f"{n / 1e9:.1f} GB"


def report() -> str:
    uses, samples = read_jsonl("uses.jsonl"), read_jsonl("samples.jsonl")
    incidents, base = read_jsonl("incidents.jsonl"), read_jsonl("baseline.jsonl")
    ok = [u for u in uses if u.get("ok")]
    failed = [u for u in uses if not u.get("ok")]
    bsec = base[-1]["full_clone_s"] if base else None
    clone_s = sorted(u.get("clone_s", 0) for u in ok)
    med = clone_s[len(clone_s) // 2] if clone_s else None
    t_saved = sum(max(bsec - u.get("clone_s", 0), 0) for u in ok) if bsec is not None else None
    d_saved = sum(max(u.get("full_clone_objects_bytes", 0) - u.get("git_dir_own_bytes", 0), 0) for u in ok)
    last = samples[-1] if samples else {}
    seats = {}
    for u in uses:
        seats[u.get("seat", "?")] = seats.get(u.get("seat", "?"), 0) + 1
    rows = [
        ("clones made (ok / failed)", f"{len(ok)} / {len(failed)}"),
        ("by seat", ", ".join(f"{k} {v}" for k, v in sorted(seats.items())) or "-"),
        ("median clone time", f"{med:.2f} s" if med is not None else "-"),
        ("full-copy baseline", f"{bsec:.0f} s (lower bound)" if bsec is not None else "UNMEASURED (run baseline)"),
        ("time saved, total", f"{t_saved / 60:.1f} min" if t_saved is not None else "UNMEASURED"),
        ("disk saved at creation, total", gb(d_saved)),
        ("corruption incidents", str(len(incidents))),
        ("samples taken", f"{len(samples)} (last {last.get('ts', '-')})"),
        ("store size (own / hard-linked)", f"{gb(last.get('store_own_bytes', 0))} / {gb(last.get('store_hardlinked_bytes', 0))}" if last else "-"),
        ("borrowers now: store / seat clone / other", f"{last.get('borrowers_store', '-')} / {last.get('borrowers_seat', '-')} / {last.get('borrowers_other', '-')}"),
        ("disk free", gb(last["disk_free_bytes"]) if last.get("disk_free_bytes") else "-"),
    ]
    if incidents:
        verdict = "BAD — a borrower lost objects; read incidents.jsonl"
    elif not ok:
        verdict = "NO DATA — nobody has used it yet"
    elif len(failed) > 0.1 * len(uses):
        verdict = "MIXED — more than 10% of clone calls failed; read uses.jsonl errors"
    else:
        verdict = "GOOD so far — no corruption, failures under 10%"
    w = max(len(r[0]) for r in rows)
    lines = [f"objstore trial ({state_dir()})", ""] + [f"  {k.ljust(w)}  {v}" for k, v in rows]
    if last.get("borrowers_seat"):
        ps = last["borrowers_seat_paths"]
        lines.append(f"  !! {len(ps)} repo(s) still borrow from a seat clone (finding #8): "
                     + ", ".join(ps[:3]) + (" ..." if len(ps) > 3 else ""))
    if failed:
        lines.append(f"  last failure: {failed[-1].get('error')}")
    lines += ["", f"  VERDICT: {verdict}"]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("clone", help="make a throwaway clone under /home/mandrake/rm/scratch/<SEAT>/")
    c.add_argument("purpose", help="what it is for — recorded")
    c.add_argument("--name")
    g = c.add_mutually_exclusive_group()
    g.add_argument("--checkout", action="store_true", help="full working tree (~6 GB)")
    g.add_argument("--sparse", nargs="+", default=[], metavar="PATH", help="cone sparse checkout")
    c.add_argument("--fetch", action="store_true", help="also fetch origin (GitHub) after cloning")
    c.add_argument("--dissociate", action="store_true", help="durable clone: no alternates (hard-linked packs)")
    for n in ("init", "refresh", "sample", "baseline", "report"):
        sub.add_parser(n)
    a = ap.parse_args(argv)
    if a.cmd == "clone":
        return clone(a.purpose, a.name, a.checkout, a.sparse, a.fetch, a.dissociate)
    if a.cmd == "report":
        print(report())
        return 0
    out = {"init": init, "refresh": refresh, "sample": sample, "baseline": baseline}[a.cmd]()
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
