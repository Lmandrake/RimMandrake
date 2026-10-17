#!/usr/bin/env python3
"""facing_regen_batch.py — run facing_regen.py over every regenerate-class creature picture, resumably
(ROSTER_FACINGS_SHRINK_FRONT_VIEWS_STAND_TALL; owner chose the redraw by card 2026-10-16 and then said
"Can you just please accept the newly redone base standing creatures and move on? ... LEt's just get going.").

    facing_regen_batch.py plan     # write STATE (refuses to overwrite one that exists)
    facing_regen_batch.py run -j 3 # gen -> conform -> lint (judge + feet row) -> register -> canon (SW) -> install
    facing_regen_batch.py status
    facing_regen_batch.py requeue <texPath substring>...   # reset non-installed rows to pending

STATE (Transient/facing_regen_batch_2026-10-16/state.json, committed) holds one record per picture with a
semantic status: pending | in_progress | ready | installed | needs_eyes | retryable_failure | skipped.
Resume runs pending, in_progress (a crash) and retryable_failure (attempts < MAX_ATTEMPTS); never re-runs
installed/needs_eyes/skipped. Install = art.py install --file <candidate> --owner-said <his words>, only when the
lint passes, the canon Must-show grader did not FAIL (Star Wars creatures), and the live picture is unchanged since
plan time (someone else touching it -> needs_eyes). Commits go through ./publish in batches (explicit paths).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "artpipe"))
import facing_regen as R  # noqa: E402
import facing_scale_lint as L  # noqa: E402

BATCH = REPO / "Transient/facing_regen_batch_2026-10-16"
STATE = BATCH / "state.json"
LOG = BATCH / "events.jsonl"
CAND = BATCH / "candidates"                      # in-clone copies art.py install --file needs
WORK = Path("/mnt/d/Luke/dev/_rmscratch/facing_regen_batch")   # raw renders: not in the repo
ROWS = REPO / "Transient/facing_rescale_2026-10-16/lint_after_reseat.json"
TAG = "standtall_b1"
MAX_ATTEMPTS = 2                                 # whole-picture attempts (each = up to GEN_TRIES per facing)
GEN_TRIES = 3
QUOTE = ("Can you just please accept the newly redone base standing creatures and move on? That sheet is causing me "
         "a headache. LEt's just get going.")
PILOT = {"rm_heemin", "rm_krissek", "rm_qorrax", "rm_siidda", "stormsando", "rm_zrrik", "akk", "anooba_f", "borcatu",
         "dewback"}
EXCLUDE_SUBSTR = ("dewback",)                    # separate reconcile awaiting the owner
LOCK = threading.Lock()


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load() -> dict:
    return json.loads(STATE.read_text())


def save(st: dict) -> None:
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, indent=1, sort_keys=True))
    os.replace(tmp, STATE)


def log(rec: dict) -> None:
    rec["at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with LOCK, open(LOG, "a") as fh:
        fh.write(json.dumps(rec) + "\n")


def update(key: str, **kw) -> None:
    with LOCK:
        st = load()
        st["items"][key].update(kw)
        save(st)


def is_sw(row) -> bool:
    return row["def"].startswith("RSW_") or "SW" in row["mod"]


def plan() -> int:
    if STATE.exists():
        sys.exit(f"{STATE} exists; delete it to re-plan")
    rows = {}
    for r in json.loads(ROWS.read_text()):
        rows.setdefault(r["texPath"].lower(), r)
    items = {}
    for k, r in rows.items():
        regen = [f for f, v in (r.get("fixes") or {}).items() if v.get("action") == "regenerate"]
        if not regen:
            continue
        s = R.slug(r).lower()
        rec = {"texPath": r["texPath"], "def": r["def"], "mod": r["mod"], "facings": sorted(regen, reverse=True),
               "sw": is_sw(r), "status": "pending", "attempts": 0, "why": ""}
        if s in PILOT or any(x in k for x in EXCLUDE_SUBSTR):
            rec.update(status="skipped", why="pilot set (installed 17b63dfb21) or Dewback (owner reconcile)")
        elif set(regen) - {"north", "south"}:
            rec.update(status="needs_eyes", why=f"lint asks to regenerate {regen}: east is the anchor, never redrawn")
        elif any("/rm/bench/src/" not in r["files"].get(f, "") for f in regen):
            rec.update(status="needs_eyes", why="live picture is not in this repo (vanilla/donor/workshop path)")
        else:
            rec["live_sha"] = {f: sha(r["files"][f]) for f in regen}
            dirty = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "--"] +
                                   [r["files"][f] for f in regen], capture_output=True, text=True).stdout.strip()
            if dirty:
                rec.update(status="skipped", why="uncommitted edit by another agent at plan time")
        items[k] = rec
    slugs = {}
    for k, v in items.items():
        slugs.setdefault(R.slug(rows[k]).lower(), []).append(k)
    for s, ks in slugs.items():
        if len(ks) > 1:
            for k in ks[1:]:
                items[k].update(status="needs_eyes", why=f"slug {s} collides with {ks[0]} (artpipe job id)")
    BATCH.mkdir(parents=True, exist_ok=True)
    save({"schema": 1, "rows": str(ROWS.relative_to(REPO)), "tag": TAG, "items": items})
    print(status())
    return 0


def requeue(subs: list[str]) -> int:
    """Reset matching non-installed rows to pending (attempts 0) so `run` picks them up again."""
    if not subs:
        sys.exit("requeue needs at least one texPath substring")
    for k, v in load()["items"].items():
        if v["status"] != "installed" and any(s.lower() in k for s in subs):
            update(k, status="pending", attempts=0, why="")
            print("requeued", k)
    return 0


def status() -> str:
    st = load()
    from collections import Counter
    c = Counter(v["status"] for v in st["items"].values())
    n = len(st["items"])
    return f"{n} pictures: " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())) + f" (sum {sum(c.values())} = {n})"


def feet_off(m) -> dict:
    return {f: round(m[f]["bottom"] - m["east"]["bottom"], 4) for f in ("south", "north")
            if f in m and "east" in m and abs(m[f]["bottom"] - m["east"]["bottom"]) > L.FEET_TOL}


SANDBOX_BASE = [0]
STOP = threading.Event()


def sandbox_setup_count(home: Path) -> int:
    n = 0
    for f in (home / ".sandbox").glob("sandbox.*.log"):
        try:
            n += f.read_text(errors="replace").count("sandbox setup required")
        except OSError:
            pass
    return n


def sandbox_guard(home: Path) -> None:
    """A new 'sandbox setup required' in the home's sandbox log = Codex is provisioning (UAC on his screen): stop all."""
    if sandbox_setup_count(home) > SANDBOX_BASE[0]:
        STOP.set()
        log({"event": "STOP", "why": f"sandbox setup required logged in {home}"})
        raise RuntimeError(f"STOP: sandbox setup required in {home}/.sandbox")


def run_one(key: str, row: dict, home: Path) -> None:
    st = load()["items"][key]
    env_home = str(home)
    os.environ  # noqa: B018
    out = WORK / R.slug(row)
    out.mkdir(parents=True, exist_ok=True)
    update(key, status="in_progress", attempts=st["attempts"] + 1, worker=home.name)
    t0 = time.time()
    facings = [f for f in ("north", "south") if f in st["facings"]]
    for f in facings:                                 # a fresh attempt redraws from scratch
        c = out / "candidates" / Path(row["files"][f]).name
        if c.exists():
            c.unlink()
    res = None
    for rnd in range(2):
        todo = facings if rnd == 0 else [x["facing"] for x in res["flags"] if x["facing"] in facings] or facings
        for f in todo:
            ok = False
            for _ in range(GEN_TRIES):
                p = subprocess.run([sys.executable, str(HERE / "facing_regen.py"), "gen", "--row", row["texPath"],
                                    "--facing", f, "--out", str(out), "--rows", str(ROWS), "--timeout", "170"],
                                   capture_output=True, text=True, env=dict(os.environ, FACING_REGEN_CODEX_HOME=env_home))
                sandbox_guard(home)
                if p.returncode == 0:
                    ok = True
                    break
                time.sleep(20)
            if not ok:
                update(key, status="retryable_failure", why=f"codex gen failed {GEN_TRIES}x on {f}: "
                       + (p.stderr or p.stdout)[-200:], seconds=round(time.time() - t0))
                log({"key": key, "event": "gen_fail", "facing": f})
                return
            R.conform(row, f, out)
        res = R.lint_candidate(row, out)
        files = res["files"]
        m = {f: L.measure_file(p) for f, p in files.items() if f in L.FACES}
        m = {f: v for f, v in m.items() if v}
        fo = feet_off(m) if row.get("view") == "elevation" else {}
        fo = {f: v for f, v in fo.items() if f in facings}
        if fo:
            res["verdict"] = "FLAG"
            res["flags"] += [{"facing": f, "key": "feet", "value": v, "band": [-L.FEET_TOL, L.FEET_TOL]} for f, v in fo.items()]
        res["flags"] = [x for x in res["flags"] if x["facing"] in facings or x["key"] in ("ns", "nsw")]
        if not res["flags"]:
            break
    lint = {"ratios": res["ratios"], "flags": res["flags"]}
    if res["flags"]:
        update(key, status="needs_eyes", why="lint: " + "; ".join(f"{x['facing']} {x['key']}={x['value']}" for x in res["flags"]),
               lint=lint, seconds=round(time.time() - t0), work=str(out))
        log({"key": key, "event": "lint_flag"})
        return
    jids = R.register(row, out, TAG)
    canon = {}
    if st["sw"]:
        import canon_check as C
        import common
        for jid in jids:
            if jid.endswith("_east") or not any(jid.endswith("_" + f) for f in facings):
                continue
            r = C.check_one(jid, done=common.DEFAULT_DONE, failed=common.DEFAULT_FAILED, artsrc=common.DEFAULT_ARTSRC,
                            force=True, dry_run=False, home=home)
            sandbox_guard(home)
            c = C.normalize(r.get("check")) or {}
            canon[jid] = {"status": r.get("status"), "verdict": c.get("verdict") or c.get("status"),
                          "score": c.get("score"), "flags": (c.get("flags") or [])[:4], "note": r.get("note", "")}
    bad = {j: v for j, v in canon.items() if v["verdict"] == "FAIL"}
    err = {j: v for j, v in canon.items() if v["status"] == "error"}
    cands = {f: str(out / "candidates" / Path(row["files"][f]).name) for f in facings}
    if bad:
        update(key, status="needs_eyes", why="canon Must-show FAIL: " + "; ".join(
            f"{j.rsplit('_', 1)[1]}: {x['line'][:80]}" for j, v in bad.items() for x in v["flags"][:2]),
               lint=lint, canon=canon, cands=cands, seconds=round(time.time() - t0), work=str(out))
    elif err:
        update(key, status="needs_eyes", why="canon grader did not run: " + "; ".join(v["note"][:120] for v in err.values()),
               lint=lint, canon=canon, cands=cands, seconds=round(time.time() - t0), work=str(out))
    else:
        update(key, status="ready", lint=lint, canon=canon, cands=cands, jobs=jids, seconds=round(time.time() - t0),
               work=str(out))
    log({"key": key, "event": "done", "seconds": round(time.time() - t0)})


def install_ready(rows) -> list[str]:
    """Install every `ready` picture whose live bytes are unchanged since plan. Returns the paths written."""
    st = load()
    written = []
    for key, v in st["items"].items():
        if v["status"] != "ready":
            continue
        row = rows[key]
        changed = [f for f in v["cands"] if sha(row["files"][f]) != v["live_sha"][f]]
        if changed:
            update(key, status="needs_eyes", why=f"live {changed} changed since plan (another agent): not overwritten")
            continue
        inst = {}
        for f, c in v["cands"].items():
            live = Path(row["files"][f])
            mod, rel = str(live).split("/src/", 1)[1].split("/Textures/", 1)
            local = CAND / R.slug(row) / Path(c).name
            local.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(c, local)
            p = subprocess.run([sys.executable, str(HERE / "art.py"), "install", mod, rel, "--file", str(local),
                                "--owner-said", QUOTE], capture_output=True, text=True, cwd=REPO)
            out = (p.stdout or "").strip().splitlines()
            js = next((json.loads(x) for x in reversed(out) if x.startswith("{")), {})
            if js.get("status") != "installed":
                update(key, status="needs_eyes", why=f"art install refused {f}: {(p.stderr or p.stdout)[-200:]}",
                       installed=inst)
                break
            inst[f] = js["new"]
            written.append(str(live.relative_to(REPO)))
        else:
            update(key, status="installed", installed=inst)
            log({"key": key, "event": "installed", "facings": list(inst)})
    return written


def publish(paths: list[str], n: int) -> str:
    st = str(STATE.relative_to(REPO))
    msg = (f"Facings stand tall batch: {n} creatures' redrawn S/N installed via art ledger (owner's words)\n\n"
           "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n"
           "Claude-Session: https://claude.ai/code/session_01FXK6MoYNNZRBtF6RgSvTgY")
    allp = sorted(set(paths)) + [st, str(LOG.relative_to(REPO)), "infrastructure/state/art/events/BENCH.jsonl"]
    subprocess.run(["git", "-C", str(REPO), "pull", "--ff-only", "-q"], capture_output=True)
    p = subprocess.run(["./publish", "-m", msg] + allp, capture_output=True, text=True, cwd=REPO)
    tail = (p.stdout + p.stderr).strip()[-300:]
    for _ in range(10):                     # commit is on HEAD; a refused land is retried bare until it lands
        if "PUBLISHED" in tail or "already on origin" in tail:
            return tail.splitlines()[-1]
        if "intact on HEAD" not in tail and "REFUSED" not in tail:
            break
        time.sleep(60)
        p = subprocess.run(["./publish"], capture_output=True, text=True, cwd=REPO)
        tail = (p.stdout + p.stderr).strip()[-300:]
    return "PUBLISH FAILED: " + tail.replace(chr(10), " ")[-200:]


def run(jobs: int) -> int:
    rows = {}
    for r in json.loads(ROWS.read_text()):
        rows.setdefault(r["texPath"].lower(), r)
    st = load()
    todo = [k for k, v in st["items"].items()
            if v["status"] in ("pending", "in_progress") or (v["status"] == "retryable_failure" and v["attempts"] < MAX_ATTEMPTS)]
    print(f"{len(todo)} to run; {status()}", flush=True)
    # ONE worker on the SHARED home (coordinator 2026-10-16): an isolated per-worker home whose sandbox seed predates
    # the current codex.exe re-runs Codex's Windows sandbox setup -> a UAC dialog on the owner's screen.
    if jobs != 1:
        sys.exit("refused: -j must be 1 (parallel isolated codex homes raise UAC sandbox dialogs)")
    homes = [Path(R.CODEX_HOME)]
    SANDBOX_BASE[0] = sandbox_setup_count(homes[0])
    free = list(homes)
    flock = threading.Lock()
    pending_paths, since = [], [0]

    def work(key):
        if STOP.is_set():
            return
        with flock:
            home = free.pop()
        try:
            run_one(key, rows[key], home)
        except Exception as exc:  # noqa: BLE001 — recorded, never fatal to the batch
            update(key, status="pending" if STOP.is_set() else "retryable_failure", why=f"{type(exc).__name__}: {exc}"[:300])
            log({"key": key, "event": "exception", "err": repr(exc)[:300]})
        finally:
            with flock:
                free.append(home)
        with LOCK:
            since[0] += 1
            n_ready = sum(1 for v in load()["items"].values() if v["status"] == "ready")
        if n_ready >= 20:
            flush_installs()

    ilock = threading.Lock()

    def flush_installs():
        with ilock:
            paths = install_ready(rows)
            if paths:
                n = len({p.rsplit("/", 1)[0] for p in paths})
                r = publish(paths, n)
                log({"event": "publish", "n_paths": len(paths), "result": r})
                print(f"publish {len(paths)} paths: {r}", flush=True)

    with ThreadPoolExecutor(jobs) as ex:
        list(ex.map(work, todo))
    flush_installs()
    print("END " + status(), flush=True)
    return 0


def montage(per_page: int = 24, ppu: int = 110) -> list[str]:
    """Every installed creature's S/E/N side by side at TRUE scale (drawSize x ppu px per tile, same for all), a
    1-tile bar on each page, plus the needs-eyes list as text. -> written paths."""
    from PIL import Image, ImageDraw, ImageFont
    rows = {}
    for r in json.loads(ROWS.read_text()):
        rows.setdefault(r["texPath"].lower(), r)
    st = load()["items"]
    keys = sorted((k for k, v in st.items() if v["status"] == "installed"), key=lambda k: st[k]["def"])
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
    cells = []
    for k in keys:
        r = rows[k]
        dw, dh = r["drawSize"]
        ims = []
        for f in ("south", "east", "north"):
            if f in r["files"]:
                im = Image.open(r["files"][f]).convert("RGBA")
                ims.append(im.resize((max(1, round(dw * ppu)), max(1, round(dh * ppu))), Image.BOX))
        w = sum(i.width for i in ims) + 10 * (len(ims) - 1)
        h = max(i.height for i in ims)
        c = Image.new("RGBA", (max(w, 260), h + 24), (0, 0, 0, 0))
        x = 0
        for i in ims:
            c.alpha_composite(i, (x, 24 + h - i.height))
            x += i.width + 10
        ImageDraw.Draw(c).text((0, 2), f"{r['def']}  ({', '.join(st[k]['installed'])} new)", fill=(30, 20, 10), font=font)
        cells.append(c)
    out = []
    BATCH.mkdir(parents=True, exist_ok=True)
    for old in BATCH.glob("montage_*.png"):
        old.unlink()
    for pi in range(0, len(cells), per_page):
        page = cells[pi:pi + per_page]
        W = 2400
        lines, line, lw = [], [], 0
        for c in page:
            if line and lw + c.width + 30 > W - 40:
                lines.append(line)
                line, lw = [], 0
            line.append(c)
            lw += c.width + 30
        if line:
            lines.append(line)
        H = 70 + sum(max(c.height for c in ln) + 30 for ln in lines)
        img = Image.new("RGBA", (W, H), (214, 196, 160, 255))
        d = ImageDraw.Draw(img)
        d.text((20, 15), f"Facings stand tall batch — installed S / E / N at true scale ({ppu}px = 1 tile); page "
               f"{pi // per_page + 1} of {-(-len(cells) // per_page)}", fill=(30, 20, 10), font=font)
        d.rectangle((W - 40 - ppu, 20, W - 40, 30), fill=(60, 40, 20))
        d.text((W - 40 - ppu, 34), "1 tile", fill=(30, 20, 10), font=font)
        y = 60
        for ln in lines:
            x = 20
            for c in ln:
                img.alpha_composite(c, (x, y))
                x += c.width + 30
            y += max(c.height for c in ln) + 30
        p = BATCH / f"montage_{pi // per_page + 1:02d}.png"
        img.convert("RGB").save(p, optimize=True)
        out.append(str(p))
    ne = [f"- `{v['def']}` ({v['texPath']}): {v['why']}" + (f" — candidates: {', '.join(v['cands'].values())}" if v.get("cands") else "")
          for k, v in sorted(st.items(), key=lambda kv: kv[1]["def"]) if v["status"] in ("needs_eyes", "retryable_failure")]
    (BATCH / "needs_eyes.md").write_text("# Facings stand tall batch — needs eyes\n\n" + "\n".join(ne) + "\n")
    out.append(str(BATCH / "needs_eyes.md"))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "run", "status", "install", "montage", "requeue"])
    ap.add_argument("keys", nargs="*", help="requeue: texPath substrings (lowercase) of rows to reset to pending")
    ap.add_argument("-j", "--jobs", type=int, default=1)
    a = ap.parse_args(argv)
    if a.cmd == "requeue":
        return requeue(a.keys)
    if a.cmd == "plan":
        return plan()
    if a.cmd == "montage":
        print("\n".join(montage()))
        return 0
    if a.cmd == "status":
        print(status())
        return 0
    if a.cmd == "install":
        rows = {}
        for r in json.loads(ROWS.read_text()):
            rows.setdefault(r["texPath"].lower(), r)
        print(install_ready(rows))
        return 0
    return run(a.jobs)


if __name__ == "__main__":
    sys.exit(main())
