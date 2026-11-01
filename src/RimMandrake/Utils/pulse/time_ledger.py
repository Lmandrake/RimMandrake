#!/usr/bin/env python3
"""time_ledger.py — RW1: where a worker's hours went (WORKER_TIME_LEDGER_BUILD_WHERE_HOURS_WENT). Read-only.

Each relentless run's wall time, first record to last, is charged from its tool records to RW1's six categories:
    selftest  live  build  reading  editing  waiting   (+ `other`: unclassified tools, `model`: thinking between tools)
    python3 src/RimMandrake/Utils/pulse/time_ledger.py write [--days 7] [--out <path>]   the ledger the mission page reads
    python3 src/RimMandrake/Utils/pulse/time_ledger.py show [--days 7]                   per run, as text
    python3 src/RimMandrake/Utils/pulse/time_ledger.py replay --labels <file.json>       S2: missed waste, wrongful stops

Reuse, so RW1 and RW2 can never disagree about what a tool call was:
  * circling.classify  (the RW2 tick's own classifier) names each tool call's kind;
  * agents_timeline.scan / BUSY_GAP name a run's working stretches: time no tool covers and no record falls within
    BUSY_GAP of is "open, waiting" there and `waiting` here; inside a stretch it is the model thinking -> `model`.
Overlapping tools (parallel calls, subagents) split the overlap evenly, so a run's categories sum to its wall time.
A tool with no result is charged to its transcript's last record (killed, or still running at the read).

Runs: every item in the relentless store (RELENTLESS_ROOT) with a clone; its transcripts are the clone's Claude project
folder (RM_TIME_PROJECTS, default ~/.claude/projects), subagent transcripts included. Gen g owns the wall time from its
attempts.jsonl `start` row to the next one; all of an item's transcripts are swept together inside that window, so
parent and subagent time is charged once and a transcript crossing a restart is split at it.
Mods: a run is charged IN FULL to every mod the mission page says its item concerns (mission_page._concerns), so a mod's
hours are exactly the work its mission page lists, and mod totals do not sum to run totals (`attribution: inclusive`).
A run concerning no mod stays in `runs` only.

Output (RM_TIME_LEDGER, else <pulse state>/time_ledger.json; the only file this writes):
    {"at", "since", "mods": {<Mod>: {"at", "hours": {cat: h}, "runs": [run ids]}}, "runs": {<item>#g<gen>: {...}},
     "unmeasured": [...]}
Waste (S2) is read with relentless_rules.json `circling`: a run spending over test_share_limit of its working time
(wall minus waiting) in selftests, for at least test_share_min minutes, is flagged. A flag on a run labelled fine is a
wrongful stop; a waste-labelled run with no flag is missed waste. Seat windows (BENCH, FOUNDRY) are not runs: UNMEASURED.
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True   # read-only: not even a __pycache__ for the modules it imports

import argparse  # noqa: E402
import glob  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import time  # noqa: E402
import types  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "rimflow"))
import agents_timeline as at   # noqa: E402
import circling               # noqa: E402
import pulse_core as pc       # noqa: E402

CATEGORIES = ("selftest", "live", "build", "reading", "editing", "waiting")
KINDS = CATEGORIES + ("other", "model")
RULES = HERE.parents[1] / "rimflow" / "relentless_rules.json"
ITEM = "WORKER_TIME_LEDGER_BUILD_WHERE_HOURS_WENT"
FIXTURE = HERE / "time_ledger_replay"     # S2: hand-labelled real runs, frozen (freeze), replayed by the selftest


def out_path() -> Path:
    return Path(os.environ.get("RM_TIME_LEDGER") or pc.STATE_DIR / "time_ledger.json")


def projects_dir() -> Path:
    return Path(os.environ.get("RM_TIME_PROJECTS") or Path.home() / ".claude" / "projects")


def relentless_root() -> Path:
    return Path(os.environ.get("RELENTLESS_ROOT") or "/home/mandrake/rm/relentless")


def circling_rules(path=None) -> dict:
    with open(path or os.environ.get("RELENTLESS_RULES") or RULES, encoding="utf-8") as f:
        return json.load(f)["circling"]


def tools_of(path: Path) -> list[dict]:
    """[{id, t0, t1, kind, target}] for one transcript, one row per tool_use id (a repeated record is the same call),
    t1 None while it has no result. Kinds are circling.classify's, so a kind here is the RW2 tick's kind; circling's
    own tool_rows is not used because it drops the id and leaves an unclosed twin for a repeated record."""
    rows, order = {}, []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return []
    for line in lines:
        try:
            d = json.loads(line)
        except ValueError:          # the live end of a transcript may be half a line
            continue
        if not isinstance(d, dict):
            continue
        m = d.get("message")
        c = m.get("content") if isinstance(m, dict) else None
        t = circling._ts(d.get("timestamp"))
        if not isinstance(c, list) or t is None:
            continue
        for b in c:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use":
                key = b.get("id") or ("anon", str(path), len(order))   # no id: never merged with anything
                if key in rows:
                    continue
                kind, target = circling.classify(b.get("name"), b.get("input"))
                rows[key] = {"id": key, "t0": t, "t1": None, "kind": kind, "target": target}
                order.append(key)
            elif b.get("type") == "tool_result" and b.get("tool_use_id") in rows:
                r = rows[b["tool_use_id"]]
                r["t1"] = t if r["t1"] is None else r["t1"]
    return sorted((rows[k] for k in order), key=lambda x: x["t0"])


def view(path: Path) -> dict | None:
    """One transcript -> {first, last, segs, tools}; a tool with no result runs to this file's last record. None when
    it holds no timed record."""
    st = at.scan(path)
    if st.get("err") or st.get("first") is None:
        return None
    lo, hi = st["first"], st["last"]
    tools = [dict(t, src=str(path), open=t["t1"] is None, t1=hi if t["t1"] is None else min(max(t["t1"], t["t0"]), hi))
             for t in tools_of(path) if lo <= t["t0"] <= hi]
    return {"path": str(path), "first": lo, "last": hi, "segs": [(a, b) for a, b in st["segs"]], "tools": tools}


def merge(segs):
    out = []
    for a, b in sorted(segs):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [tuple(s) for s in out]


def dedupe(tools):
    """One call per tool_use id across all of a run's files: a resumed session's copied history repeats the same ids
    in another file and counts once; distinct ids are distinct calls, parallel or identical, and all stay. Of a call's
    copies the closed one wins (a copy cut off before its result would stretch to its own file's end), else the
    longest observed."""
    best = {}
    for t in tools:
        k = t.get("id") or id(t)
        b = best.get(k)
        if b is None or (b["open"] and not t["open"]) or (b["open"] == t["open"] and t["t1"] > b["t1"]):
            best[k] = t
    return sorted(best.values(), key=lambda t: t["t0"])


def sweep(lo: float, hi: float, segs, tools) -> dict:
    """Charge [lo, hi] once: overlapping tools split each slice evenly; a slice no tool covers is `model` inside a
    working stretch and `waiting` outside one. The categories sum to hi - lo."""
    segs = merge((max(a, lo), min(b, hi)) for a, b in segs if b > lo and a < hi)
    tools = [dict(t, t0=max(t["t0"], lo), t1=min(t["t1"], hi)) for t in tools if t["t1"] > lo and t["t0"] < hi]
    secs = dict.fromkeys(KINDS, 0.0)
    cuts = sorted({lo, hi} | {t["t0"] for t in tools} | {t["t1"] for t in tools} | {x for s in segs for x in s})
    for a, b in zip(cuts, cuts[1:]):
        if b <= a:
            continue
        live = [t["kind"] for t in tools if t["t0"] <= a and t["t1"] >= b]
        if live:
            for k in live:
                secs[k if k in secs else "other"] += (b - a) / len(live)
            continue
        inside = sum(max(0.0, min(b, s1) - max(a, s0)) for s0, s1 in segs)
        secs["model"] += inside
        secs["waiting"] += (b - a) - inside
    return secs


def charge(path: Path) -> dict | None:
    """One transcript alone -> {first, last, secs, tools}. None when it holds no timed record."""
    v = view(path)
    if v is None:
        return None
    tools = dedupe(v["tools"])
    return {"first": v["first"], "last": v["last"], "secs": sweep(v["first"], v["last"], v["segs"], tools),
            "tools": tools}


def mangle(clone: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", clone or "")


def _epoch(s):
    try:
        return pc.iso_to_epoch(str(s))
    except Exception:  # noqa: BLE001 - a torn stamp is a row skipped
        return None


def starts_of(item_dir: Path) -> list[tuple[float, int]]:
    out = []
    try:
        lines = (item_dir / "attempts.jsonl").read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return out
    for ln in lines:
        try:
            d = json.loads(ln)
        except ValueError:
            continue
        t = _epoch(d.get("at")) if isinstance(d, dict) and d.get("start") else None
        if t is not None and isinstance(d.get("gen"), int):
            out.append((t, d["gen"]))
    return sorted(out, key=lambda x: x[0])   # stable: of tied rows the later one owns what follows


FIRST_SLACK = 120.0   # a first transcript may stamp just before the first start row (clock skew); later gens get none


def windows(starts) -> list[tuple[int, float, float]]:
    """[(gen, w0, w1)]: gen i owns [start_i, start_{i+1}). Measured on 124 real transcripts (2026-11-01): every one
    begins 3..55 s AFTER its own start row and ends before the next, so a later row never claims earlier work."""
    out = []
    for i, (s, g) in enumerate(starts):
        w1 = starts[i + 1][0] if i + 1 < len(starts) else float("inf")
        if out and out[-1][0] == g:      # the same gen started twice in a row: one window, its gap is still its own
            out[-1] = (g, out[-1][1], w1)
        else:
            out.append((g, s - FIRST_SLACK if i == 0 else s, w1))
    return out


def transcripts(clone: str) -> list[Path]:
    d = glob.escape(str(projects_dir() / mangle(clone)))   # a literal [ in the root is a path, not a pattern
    return [Path(p) for p in sorted(glob.glob(d + "/*.jsonl") + glob.glob(d + "/*/subagents/*.jsonl"))]


def _mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except OSError:   # removed since the listing: it has nothing to charge
        return float("-inf")


def collect_runs(since: float, root: Path | None = None, until: float = float("inf")) -> tuple[dict, list]:
    """-> ({run id: {item, gen, first, last, secs, files, tools}}, unmeasured). Per item, every transcript (parent and
    subagents) is swept together, once, inside each gen's window and [since, until]: wall time is charged exactly once,
    a transcript spanning a restart is split at it, and a gap between transcripts is waiting, never lost."""
    root = root or relentless_root()
    items = root / "store" / "items"
    runs, unm = {}, []
    try:
        names = sorted(os.listdir(items))
    except OSError as e:
        return {}, [f"relentless store not read: {e}"]
    clones = {}
    for item in names:
        try:
            st = json.loads((items / item / "state.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        clone = st.get("clone") if isinstance(st, dict) else None
        if clone:
            clones[item] = clone
    owners = {}
    for item, clone in clones.items():
        owners.setdefault(mangle(clone), []).append(item)
    for item, clone in sorted(clones.items()):
        if len(owners[mangle(clone)]) > 1:
            unm.append(f"{item}: transcript folder {mangle(clone)} is shared with {owners[mangle(clone)]}: not charged")
            continue
        paths = transcripts(clone)
        if not any(_mtime(p) >= since for p in paths):
            continue   # nothing written since the cutoff (mtime >= last record, so no record after it either)
        views = [v for v in (view(p) for p in paths) if v]   # all of an active item's: earlier ones bound its windows
        if not views:
            continue
        wins = windows(starts_of(items / item))
        if not wins:
            unm.append(f"{item}: {len(views)} transcript(s) but no attempt start row")
            continue
        early = [v for v in views if v["first"] < wins[0][1]]
        if early:
            unm.append(f"{item}: {len(early)} transcript(s) begin before the first attempt start row; that part uncharged")
        segs = merge(s for v in views for s in v["segs"])
        tools = dedupe(t for v in views for t in v["tools"])
        for g, w0, w1 in wins:
            mine = [v for v in views if v["first"] < w1 and v["last"] >= w0]   # a record AT a start is that gen's
            if not mine:
                continue
            lo = max(w0, since, min(v["first"] for v in mine))
            hi = min(w1, until, max(v["last"] for v in mine))
            if hi <= lo:
                continue
            r = runs.setdefault(f"{item}#g{g}", {"item": item, "gen": g, "first": lo, "last": hi,
                                                 "secs": dict.fromkeys(KINDS, 0.0), "files": [], "tools": []})
            r["first"], r["last"] = min(r["first"], lo), max(r["last"], hi)   # a gen resumed after another gen: windows summed, first/last only their envelope
            for k, s in sweep(lo, hi, segs, tools).items():
                r["secs"][k] += s
            r["files"] += [v["path"] for v in mine if v["path"] not in r["files"]]
            r["tools"] += [t for t in tools if t["t1"] > lo and t["t0"] < hi]
    return runs, unm


def verdict(secs: dict, c: dict) -> dict:
    """S2's reading of one run. Working time is wall minus waiting: a run parked on a sleep is not a testing run."""
    work = sum(v for k, v in secs.items() if k != "waiting")
    share = secs["selftest"] / work if work > 0 else 0.0
    waste = secs["selftest"] >= c["test_share_min"] * 60 and share > c["test_share_limit"]
    return {"selftest_share": round(share, 3), "selftest_min": round(secs["selftest"] / 60, 1), "waste": waste}


def mods_of(item_ids, root=None) -> tuple[dict, str | None]:
    """{item: [Mod]} by the mission page's own rule. -> ({}, why) when the ledger or the mod list could not be read."""
    import mission_page as mp
    root = root or mp._root()
    mods = sorted({p.parents[1].name for p in root.glob("src/*/*/About/About.xml")})
    if not mods:
        return {}, f"no mod with an About.xml under {root}/src"
    try:
        seam = os.environ.get("RM_MISSION_LEDGER")
        events = [json.loads(ln) for ln in open(seam, encoding="utf-8") if ln.strip()] if seam else pc.read_ledger()
        world = pc._model().replay(events)
    except Exception as e:  # noqa: BLE001 - attribution unread is said, never an empty mod list that reads as "no hours"
        return {}, f"ledger not read: {type(e).__name__}: {str(e)[:120]}"
    out = {}
    for iid in item_ids:
        it = world.items.get(iid) or types.SimpleNamespace(title="")
        out[iid] = [m for m in mods if mp._concerns(iid, it, m, root, mp._lane(m, root))]
    return out, None


def hours_of(secs: dict) -> dict:
    """Seconds -> exported hours; 6 decimals, so a one-second slice is never rounded to nothing."""
    return {k: round(v / 3600, 6) for k, v in secs.items()}


def build(days: float = 7.0, now: float | None = None) -> dict:
    now = time.time() if now is None else now
    since = now - days * 86400
    c = circling_rules()
    runs, unm = collect_runs(since, until=now)
    attr, why = mods_of(sorted({r["item"] for r in runs.values()}))
    if why:
        unm.append(f"mod attribution: {why}")
    unm.append("seat windows (BENCH, FOUNDRY, HESTIA) are not runs: their hours are not charged in v1")
    mods, out_runs = {}, {}
    for rid, r in sorted(runs.items()):
        hours = hours_of(r["secs"])
        out_runs[rid] = {"item": r["item"], "gen": r["gen"], "first": r["first"], "last": r["last"], "hours": hours,
                         "mods": attr.get(r["item"], []), "transcripts": len(r["files"]), **verdict(r["secs"], c)}
        for m in attr.get(r["item"], []):
            rec = mods.setdefault(m, {"at": now, "hours": dict.fromkeys(KINDS, 0.0), "runs": []})
            for k, v in r["secs"].items():
                rec["hours"][k] += v
            rec["runs"].append(rid)
    for rec in mods.values():
        rec["hours"] = hours_of(rec["hours"])
    return {"at": now, "since": since, "item": ITEM, "attribution": "inclusive", "mods": mods, "runs": out_runs,
            "unmeasured": unm}


def write(d: dict, path: Path | None = None) -> Path:
    path = path or out_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(d, indent=1, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)
    return path


def replay(labels: list, runs: dict, c: dict) -> dict:
    """labels: [{run: "<item>#g<gen>", label: waste|fine, why}]. A run missing from the ledger, or labelled both ways, is
    UNMEASURED, never clean. Listed twice counts once. `gate` is whether stopping on the flag would be allowed."""
    out = {"waste": 0, "fine": 0, "missed": 0, "wrongful": 0, "unmeasured": [], "runs": []}
    said = {}
    for row in labels:
        said.setdefault(row["run"], set()).add(row["label"])
    for rid in dict.fromkeys(row["run"] for row in labels):
        lab = said[rid]
        if len(lab) > 1 or not lab <= {"waste", "fine"}:
            out["unmeasured"].append(f"{rid}: labelled {sorted(lab)}")
            continue
        r = runs.get(rid)
        if r is None:
            out["unmeasured"].append(f"{rid}: no transcript in the ledger")
            continue
        label = lab.pop()
        flag = verdict(r["secs"], c)
        out[label] += 1
        out["missed"] += label == "waste" and not flag["waste"]
        out["wrongful"] += label == "fine" and flag["waste"]
        out["runs"].append(dict(flag, run=rid, label=label))
    out["measured"] = out["waste"] + out["fine"]
    out["wrongful_rate"] = round(out["wrongful"] / out["fine"], 3) if out["fine"] else None
    out["may_stop"] = bool(out["measured"] >= c["replay_min_runs"] and out["fine"] and out["waste"]
                           and out["wrongful"] / out["fine"] < c["false_stop_limit"] and not out["missed"])
    return out


def _strip(d: dict) -> dict | None:
    """A transcript record cut to what this ledger and agents_timeline.scan read: type, stamp, tool calls (name, the
    input fields circling.classify reads) and tool results (their id only). Prose, results and thinking are dropped."""
    if not isinstance(d, dict) or d.get("type") not in ("user", "assistant", "system", "queue-operation"):
        return None
    out = {"type": d["type"], "timestamp": d.get("timestamp")}
    m = d.get("message")
    blocks = []
    for b in (m.get("content") if isinstance(m, dict) and isinstance(m.get("content"), list) else []):
        if isinstance(b, dict) and b.get("type") == "tool_use":
            inp = b.get("input") if isinstance(b.get("input"), dict) else {}
            keep = {"Bash": ("command",), "Read": ("file_path", "offset")}.get(b.get("name"), ())
            blocks.append({"type": "tool_use", "id": b.get("id"), "name": b.get("name"),
                           "input": {k: inp[k] for k in keep if k in inp}})
        elif isinstance(b, dict) and b.get("type") == "tool_result":
            blocks.append({"type": "tool_result", "tool_use_id": b.get("tool_use_id")})
    out["message"] = {"role": d["type"], "content": blocks}
    return out


def freeze(labels: list, fixture: Path, since: float) -> int:
    """Copy the labelled runs' store rows and stripped transcripts into `fixture`, so S2 replays the same real runs
    after the live transcripts age out. Every transcript of a labelled item is copied whole, as collect_runs reads them
    all (`since` is not a filter: a run frozen in part, or without the closed copy of a call, would replay as a
    different run). An item whose transcript folder another item shares is refused: live it is UNMEASURED, frozen alone
    it would read as charged. Refuses a fixture overlapping the live trees or already holding a frozen store. Reads the
    live store; writes only under `fixture`."""
    want = {}
    for row in labels:
        item, _, g = row["run"].rpartition("#g")
        want.setdefault(item, set()).add(int(g))
    src = relentless_root() / "store" / "items"
    fx, live = Path(fixture).resolve(), [relentless_root().resolve(), projects_dir().resolve()]
    for x in live:
        if fx == x or fx in x.parents or x in fx.parents:
            raise ValueError(f"fixture {fx} overlaps the live {x}: freeze writes only into a separate tree")
    for sub in ("relentless", "projects"):
        if (fx / sub).exists():
            raise ValueError(f"{fx / sub} exists: a freeze starts empty (remove it to re-freeze), so nothing stale stays")
    folders = {}
    for d in (src.iterdir() if src.is_dir() else []):
        try:
            c = json.loads((d / "state.json").read_text(encoding="utf-8")).get("clone")
        except (OSError, ValueError, AttributeError):
            continue
        if c:
            folders.setdefault(mangle(c), []).append(d.name)
    n = 0
    for item in sorted(want):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", item) or item in (".", ".."):
            raise ValueError(f"label run {item!r}: an item id is a plain name, never a path")
        st = json.loads((src / item / "state.json").read_text(encoding="utf-8"))
        if len(folders.get(mangle(st["clone"]), [])) > 1:
            raise ValueError(f"label run {item!r}: transcript folder shared with {folders[mangle(st['clone'])]}")
        dst = fixture / "relentless" / "store" / "items" / item
        dst.mkdir(parents=True, exist_ok=True)
        (dst / "state.json").write_text(json.dumps({"item": item, "clone": st["clone"]}, indent=1), encoding="utf-8")
        starts = (src / item / "attempts.jsonl").read_text(encoding="utf-8", errors="replace").splitlines()
        rows = []
        for x in starts:
            try:
                rows.append(json.loads(x))
            except ValueError:   # a torn row: starts_of skips it too
                continue
        (dst / "attempts.jsonl").write_text("".join(json.dumps({k: r[k] for k in ("at", "gen", "start")}) + "\n"
                                                    for r in rows if isinstance(r, dict) and r.get("start")
                                                    and isinstance(r.get("gen"), int) and "at" in r),   # as starts_of
                                            encoding="utf-8")
        pd = projects_dir() / mangle(st["clone"])
        for p in transcripts(st["clone"]):
            if view(p) is None:
                continue
            out = fixture / "projects" / mangle(st["clone"]) / Path(p).relative_to(pd)
            out.parent.mkdir(parents=True, exist_ok=True)
            recs = []
            for ln in Path(p).read_text(encoding="utf-8", errors="replace").splitlines():
                try:
                    r = _strip(json.loads(ln))
                except ValueError:
                    continue
                if r:
                    recs.append(json.dumps(r, sort_keys=True))
            out.write_text("\n".join(recs) + "\n", encoding="utf-8")
            n += 1
    return n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("write", "show", "replay", "freeze"):
        p = sub.add_parser(name)
        p.add_argument("--days", type=float, default=7.0)
        if name == "write":
            p.add_argument("--out")
        if name in ("replay", "freeze"):
            p.add_argument("--labels", help="default: <fixture>/labels.json")
            p.add_argument("--fixture", help="a frozen store: replay reads it, freeze writes it", default=str(FIXTURE))
    a = ap.parse_args(argv)
    if a.cmd in ("replay", "freeze"):
        with open(a.labels or Path(a.fixture) / "labels.json", encoding="utf-8") as f:
            labels = json.load(f)
        if a.cmd == "freeze":
            n = freeze(labels, Path(a.fixture), time.time() - a.days * 86400)
            print("FROZE", n, "transcripts into", a.fixture)
            return 0
        os.environ["RELENTLESS_ROOT"] = str(Path(a.fixture) / "relentless")
        os.environ["RM_TIME_PROJECTS"] = str(Path(a.fixture) / "projects")
        runs, unm = collect_runs(0)
        v = replay(labels, runs, circling_rules())
        print(json.dumps(dict(v, ledger_unmeasured=unm), indent=1))
        return 0
    d = build(a.days)
    if a.cmd == "write":
        print("WROTE", write(d, Path(a.out) if a.out else None), len(d["runs"]), "runs", len(d["mods"]), "mods")
        return 0
    for rid, r in d["runs"].items():
        h = r["hours"]
        print(f"{rid:60} " + " ".join(f"{k[:5]}={h[k]:.2f}" for k in KINDS) + f"  share={r['selftest_share']}"
              + (" FLAG:waste" if r["waste"] else "") + f"  mods={','.join(r['mods']) or '-'}")
    for m, rec in sorted(d["mods"].items()):
        print(f"MOD {m}: " + " ".join(f"{k}={v:.2f}" for k, v in rec["hours"].items()))
    for u in d["unmeasured"]:
        print("UNMEASURED", u)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
