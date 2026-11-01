#!/usr/bin/env python3
"""One machine-written page per mod (C7, MI1 in design/RimMandrake/operating_requirements_2026-11-01.md;
MISSION_PAGE_BUILD_READ_ONLY_STATE): finish line with each row's status and proof age, what is running and for how
long, days since the reading advanced, time ledger, open decisions. Phone width.

    /mission, /mission/<Mod>, /mission/<Mod>.json     served by brief.page, loopback and tailnet
    python3 src/RimMandrake/Utils/pulse/mission_page.py <Mod> [--out <path>] [--json]

Read-only: the routes write nothing, the CLI writes only --out (stdout without it). Every reading is taken at request
time; a page is never a stored claim.

A row's status is a reading, never a statement:
    PROVEN      a row of the mod's recorded result claims this bar (its id, or `shows=`), all PASS, at today's mod hash
    FAIL        such a row failed, at today's mod hash
    STALE       the mod changed since the run that holds the row: old proof is no proof
    UNMEASURED  anything else. No run, no result file, no row claiming the bar, a SKIP, an invalid or reused row, a
                torn entry. Missing evidence is never read as done.
`MET` needs a VALIDATED north star with at least one bar, every bar PROVEN, and a GREEN entry at today's hash with
step 4 PASS or not owed. A mod with no bars reads UNMEASURED however green its modcheck entry is.

Inputs: <root>/design/validation_walks, infrastructure/state/modcheck_status.json, the ledger, relentless's store
(RELENTLESS_ROOT), plan_advance.json (RM_OPS_WATCH_DIR) and the time ledger. The time ledger's producer is
WORKER_TIME_LEDGER_BUILD_WHERE_HOURS_WENT; until it lands that section reads UNMEASURED. This page reads the file it is to
write, RM_TIME_LEDGER or <pulse state>/time_ledger.json: {"mods": {<Mod>: {"at": <epoch>, "hours": {<category>: <h>}}}}.
RM_MISSION_ROOT and RM_MISSION_LEDGER (one jsonl) are fixture seams.
"""
import sys

if __name__ == "__main__":       # the CLI's promise: a __pycache__ is a write that is not the page. Not the daemon's flag to flip.
    sys.dont_write_bytecode = True
import argparse           # noqa: E402
import html               # noqa: E402
import importlib.util     # noqa: E402
import json               # noqa: E402
import math               # noqa: E402
import os                 # noqa: E402
import re                 # noqa: E402
import time               # noqa: E402
from pathlib import Path  # noqa: E402
from types import SimpleNamespace  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import brief              # noqa: E402
import pulse_core as pc   # noqa: E402

MODCHECK = HERE.parent / "modcheck"
CATEGORIES = ("selftest", "live", "build", "reading", "editing", "waiting")     # RW1's six
TIME_ITEM = "WORKER_TIME_LEDGER_BUILD_WHERE_HOURS_WENT"
MOD_RE = r"[A-Za-z][A-Za-z0-9_]{1,63}"
FUTURE_SLACK = 300
UNM = "UNMEASURED"


def _root():
    return Path(os.environ.get("RM_MISSION_ROOT") or HERE.parents[3])


def _private(name):
    """A modcheck module under a private name: `status` and `northstar` are too generic for sys.modules here."""
    full = "_mission_" + name
    if full not in sys.modules:
        spec = importlib.util.spec_from_file_location(full, MODCHECK / (name + ".py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[full] = mod
        keep, sys.dont_write_bytecode = sys.dont_write_bytecode, True      # a route writes nothing, a .pyc included
        try:
            spec.loader.exec_module(mod)
        finally:
            sys.dont_write_bytecode = keep
    return sys.modules[full]


def _num(v):
    try:
        return not isinstance(v, bool) and isinstance(v, (int, float)) and math.isfinite(v)
    except OverflowError:       # a JSON integer past float range
        return False


def _when(t, now):
    """Seconds since `t`, or None for a time that cannot be one: a future stamp is a torn stamp, not a young one."""
    return now - t if _num(t) and 0 < t <= now + FUTURE_SLACK else None


def age_words(s):
    if s is None:
        return UNM
    s = max(s, 0)
    return f"{int(s // 60)} min" if s < 5400 else (f"{s / 3600:.0f} h" if s < 172800 else f"{s / 86400:.0f} d")


def mod_dir_of(mod, root):
    for p in sorted(root.glob(f"src/*/{mod}/About/About.xml")):
        return p.parents[1]
    return None


def walk_of(mod, root):
    return _private("northstar").find_walk(str(root), mod)


def _status_entry(mod, root):
    """-> (entry or None, why). A torn file or entry is `why`, never an empty registry that reads as 'never run'."""
    p = root / "infrastructure" / "state" / "modcheck_status.json"
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "no modcheck_status.json"
    except (OSError, ValueError, RecursionError) as e:
        return None, f"modcheck_status.json unreadable: {str(e)[:100]}"
    if not isinstance(doc, dict):
        return None, "modcheck_status.json is not an object"
    if mod not in doc:
        return None, "never run"
    e = doc[mod]
    if not isinstance(e, dict) or not isinstance(e.get("status"), str):
        return None, "its modcheck entry is torn"
    return e, ""


def _result_doc(mod, entry, root):
    """-> (the run's result, why). Results under Transient/ live only in the clone that wrote them (untracked)."""
    rel = ((entry.get("source") or {}).get("result") if isinstance(entry.get("source"), dict) else None)
    if not isinstance(rel, str) or not rel:
        return None, "the run recorded no result file"
    if os.path.isabs(rel) or ".." in rel.replace("\\", "/").split("/"):
        return None, f"result path {rel[:80]} is outside the repo"
    roots = [root] + ([] if os.environ.get("RM_MISSION_ROOT") else list(pc.CLONES))
    for r in roots:
        try:
            doc = json.loads((Path(r) / rel).read_text(encoding="utf-8"))
        except FileNotFoundError:
            continue
        except (OSError, ValueError, RecursionError) as e:
            return None, f"result file unreadable: {str(e)[:100]}"
        if not isinstance(doc, dict) or doc.get("mod") != mod:
            return None, "result file is not this mod's"
        if doc.get("aborted"):
            return None, "that run aborted"
        if not doc.get("mod_hash") or doc["mod_hash"] != entry.get("hash"):    # no hash proves nothing about this build
            return None, "result file does not carry the recorded run's mod hash"
        return doc, ""
    return None, f"result file gone: {rel[:100]}"


def _rows_of(doc):
    out = []
    for key in ("rows", "bars", "components"):
        if isinstance(doc.get(key), list):
            out += doc[key]
    for ch in doc.get("chains") if isinstance(doc.get("chains"), list) else []:
        if isinstance(ch, dict) and isinstance(ch.get("components"), list):
            out += ch["components"]
    return [r for r in out if isinstance(r, dict)]


def _claims(bar, rows):
    hit = []
    for r in rows:
        rid = str(r.get("id") or r.get("name") or "")
        shows = r.get("shows") if isinstance(r.get("shows"), list) else []
        if rid == bar or rid.endswith("." + bar) or bar in shows:
            hit.append(r)
    return hit


def _bar_status(claims, hash_moved, run_seen):
    """-> (status, why) for one bar."""
    if not run_seen:
        return UNM, "no recorded run"
    if not claims:
        return UNM, "no row of the last run claims this bar"
    if hash_moved:
        return "STALE", "the mod changed after this run"
    words = [str(r.get("status") or r.get("verdict") or "") for r in claims]
    if any(w == "FAIL" for w in words):
        return "FAIL", ""
    bad = [r for r in claims if r.get("validity") == "invalid" or str(r.get("freshness") or "").startswith("reused@")]
    if bad:
        return UNM, "invalid or reused row"
    if words and all(w == "PASS" for w in words):
        return "PROVEN", ""
    return UNM, "row reads " + ", ".join(sorted(set(w or "nothing" for w in words)))


def finish_line(mod, root, now):
    ns_mod, st_mod = _private("northstar"), _private("status")
    walk = walk_of(mod, root)
    ns = ns_mod.parse(walk) if walk else None
    bars = ([(b, "must show", ns["must_show_text"].get(b, "")) for b in ns["must_show"]]
            + [(b, "cannot show", ns["cannot_show_text"].get(b, "")) for b in ns["cannot_show"]]) if ns else []
    entry, why = _status_entry(mod, root)
    mdir = mod_dir_of(mod, root)
    run_age = _when(entry.get("ts"), now) if entry else None
    run_seen = entry is not None and run_age is not None
    if entry is not None and not run_seen:
        why = "its run has no usable time"
    # no mod folder means no hash to compare: treated as moved, so a row can never read PROVEN on it
    moved = run_seen and (mdir is None or st_mod.mod_hash(str(mdir)) != entry.get("hash"))
    step4 = st_mod.step4_live(entry, str(mdir)) if run_seen and mdir else None
    doc, doc_why = (_result_doc(mod, entry, root) if run_seen else (None, why))
    rows = _rows_of(doc) if doc else []
    out = []
    for bar, polarity, text in bars:
        claims = _claims(bar, rows)
        st, w = _bar_status(claims, moved, run_seen)
        if st == UNM and not claims:
            w = why if not run_seen else (doc_why or w)
        age = ("proof " + age_words(run_age) if claims and run_seen
               else ("no proof; last run " + age_words(run_age) if run_seen else "no proof; " + (why or "never run")))
        out.append({"id": bar, "polarity": polarity, "text": text, "status": st, "why": w, "age": age, "age_s": run_age if claims else None})
    if not out:
        out.append({"id": "(no finish line written)", "polarity": "", "text": "", "status": UNM,
                    "why": "the walk has no bars" if ns else "this mod has no validation walk",
                    "age": "no proof; " + ("last run " + age_words(run_age) if run_seen else (why or "never run")), "age_s": None})
    proven = sum(r["status"] == "PROVEN" for r in out)
    state = ns["state"] if ns else None
    green = run_seen and entry.get("status") == "GREEN" and not moved and step4 in (None, "PASS")
    if not bars:
        verdict = UNM
    elif state == ns_mod.VALIDATED and proven == len(bars) and green:
        verdict = "MET"
    else:
        verdict = "NOT MET"
    return {"verdict": verdict, "proven": proven, "bars": len(bars), "north_star": state,
            "north_star_why": (ns or {}).get("reason") or "", "walk": os.path.relpath(walk, root) if walk else None,
            "modcheck": {"status": (entry or {}).get("status") or UNM, "why": why, "stale": bool(moved), "step4": step4,
                         "age": age_words(run_age) if run_seen else UNM},
            "rows": out}


def _concerns(iid, item, mod):
    """The brief's reading of an item's goal, row set aside: a spec that only mentions this mod names another goal."""
    bare = SimpleNamespace(row=None, title=item.title)
    return brief.goal_of(iid, bare, brief.item_words(iid), {**brief.packages(), mod.lower(): mod}) == mod


def ledger_view(mod, now):
    """-> (running, decisions, why). `why` set means the ledger was not read: both lists say nothing."""
    try:
        seam = os.environ.get("RM_MISSION_LEDGER")
        if seam:
            with open(seam, encoding="utf-8") as f:
                events = [json.loads(ln) for ln in f if ln.strip()]
        else:
            events = pc.read_ledger()
        world = pc._model().replay(events)
    except Exception as e:      # noqa: BLE001 - any failure of the reader is a section that reads UNMEASURED
        return [], [], f"ledger not read: {type(e).__name__}: {str(e)[:120]}"
    first, started = {}, {}
    for ev in events:
        iid, t = ev.get("id"), brief._tsec(ev)
        if iid and t:
            first.setdefault(iid, t)
            if ev.get("event") == "start":
                started[iid] = t
    running, decisions = [], []
    for iid, it in world.items.items():
        if not it.open or not _concerns(iid, it, mod):
            continue
        if it.state == "doing":
            run = {"id": iid, "title": it.title or "", "seat": it.owner or "?",
                   "for": age_words(_when(started.get(iid), now)), "worker": _worker(iid, now)}
            running.append(run)
        if it.needs == "owner" or it.blocked_on == "OWNER":
            decisions.append({"id": iid, "title": it.title or "", "state": it.state,
                              "waiting": age_words(_when(first.get(iid), now))})
    return running, decisions, ""


def _worker(iid, now):
    """Relentless's own record of the run, beside the ledger's word: its last heartbeat. None when it runs none."""
    p = Path(os.environ.get("RELENTLESS_ROOT") or "/home/mandrake/rm/relentless") / "store" / "items" / iid / "state.json"
    try:
        st = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(st, dict):
        return None
    return {"status": str(st.get("status") or "?"), "gen": st.get("gen"), "beat": age_words(_when(st.get("last_beat"), now))}


def advance_view(mod, root, now):
    """MI1: days since this mod's finish-line reading last rose, as ops_watch keeps it. Reads, never writes it."""
    try:
        listed = json.loads((root / "infrastructure" / "state" / "priority_list.json").read_text(encoding="utf-8"))
        entries = [e for e in listed["entries"] if isinstance(e, dict) and e.get("reading") == {"mod": mod}]
    except FileNotFoundError:
        return {"status": UNM, "why": "no priority list"}
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as e:
        return {"status": UNM, "why": f"priority list unreadable: {str(e)[:80]}"}
    if not entries:
        return {"status": UNM, "why": "this mod is not on the priority list"}
    p = Path(os.environ.get("RM_OPS_WATCH_DIR", "/mnt/d/ClaudeWork/rimmandrake/ops_watch")) / "plan_advance.json"
    try:
        kept = json.loads(p.read_text(encoding="utf-8"))
        rose = [_when(v.get("rose_t"), now) for v in kept.values() if isinstance(v, dict) and v.get("spec") == {"mod": mod}]
    except (OSError, ValueError, AttributeError, RecursionError) as e:
        return {"status": UNM, "why": f"plan_advance.json unreadable: {str(e)[:80]}"}
    rose = [r for r in rose if r is not None]
    if not rose:
        return {"status": UNM, "why": "ops_watch holds no reading for it yet"}
    return {"status": "READ", "days": round(min(rose) / 86400.0, 1)}


def time_view(mod, now):
    p = Path(os.environ.get("RM_TIME_LEDGER") or pc.STATE_DIR / "time_ledger.json")
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))["mods"][mod]
        age, hours = _when(rec.get("at"), now), rec["hours"]
    except FileNotFoundError:
        return {"status": UNM, "why": f"no time ledger on disk ({TIME_ITEM})"}
    except KeyError:
        return {"status": UNM, "why": "the time ledger has no record of this mod"}
    except (OSError, ValueError, TypeError, AttributeError, RecursionError) as e:
        return {"status": UNM, "why": f"time ledger torn: {str(e)[:80]}"}
    if age is None or not isinstance(hours, dict):
        return {"status": UNM, "why": "time ledger record torn"}
    return {"status": "READ", "age": age_words(age),
            "hours": {c: round(hours[c], 1) if _num(hours.get(c)) else UNM for c in CATEGORIES}}


def known(mod, root):
    entry, why = _status_entry(mod, root)
    return bool(mod_dir_of(mod, root) or walk_of(mod, root) or entry or why not in ("never run", "no modcheck_status.json"))


def collect(mod, now=None):
    now = time.time() if now is None else now
    root = _root()
    running, decisions, ledger_why = ledger_view(mod, now)
    try:
        finish = finish_line(mod, root, now)
    except Exception as e:      # noqa: BLE001 - a malformed record is a page that says so, never a 500
        why = f"finish line not read: {type(e).__name__}: {str(e)[:120]}"
        finish = {"verdict": UNM, "proven": 0, "bars": 0, "north_star": None, "north_star_why": "", "walk": None,
                  "modcheck": {"status": UNM, "why": why, "stale": False, "step4": None, "age": UNM},
                  "rows": [{"id": "(finish line not read)", "polarity": "", "text": "", "status": UNM, "why": why, "age": "no proof", "age_s": None}]}
    return {"mod": mod, "at": now, "finish": finish, "running": running, "decisions": decisions,
            "ledger_why": ledger_why, "advance": advance_view(mod, root, now), "time": time_view(mod, now)}


# ---------------------------------------------------------------- render: lists, never a table, so a phone never scrolls sideways
STYLE = """.PROVEN{color:#8fc27a}.FAIL{color:var(--red)}.STALE,.UNMEASURED{color:var(--mustard)}
.v{font-size:22px;font-weight:700;margin:10px 0 0}.st{white-space:normal}"""


def _link(iid, base):
    e = html.escape
    return f"<a href='{e(base)}/item/{e(iid)}'>{e(iid)}</a>" if base is not None else e(iid)


def render(d, base=""):
    """`base` None drops the links: a page written to a file has no server behind it."""
    e, f = html.escape, d["finish"]
    mc = f["modcheck"]
    head = f"{f['proven']} of {f['bars']} bars proven at today's mod hash"
    ns = f"north star {f['north_star']}" if f["north_star"] else "no north star"
    bars = "".join(
        f"<li><span class='st {e(r['status'])}'>{e(r['status'])}</span> <b>{e(r['id'])}</b> "
        f"<div class=m>{e(r['polarity'])} · {e(r['age'])}{' · ' + e(r['why']) if r['why'] else ''}</div>"
        f"{'<div class=m>' + e(r['text'][:200]) + '</div>' if r['text'] else ''}</li>" for r in f["rows"])
    if d["ledger_why"]:
        run = dec = f"<p class='st UNMEASURED'>UNMEASURED: {e(d['ledger_why'])}</p>"
    else:
        run = "".join(
            f"<li>{_link(r['id'], base)} <span class=m>{e(r['seat'])}, {e(r['for'])}"
            + (f"; worker {e(r['worker']['status'])} gen {e(str(r['worker']['gen']))}, last beat {e(r['worker']['beat'])}" if r["worker"] else "")
            + f"</span><div class=m>{e(r['title'][:120])}</div></li>" for r in d["running"])
        run = f"<ul>{run}</ul>" if run else "<p class=none>Nothing the ledger holds as doing for this mod.</p>"
        dec = "".join(f"<li>{_link(r['id'], base)} <span class=m>{e(r['state'])}, waiting {e(r['waiting'])}</span>"
                      f"<div class=m>{e(r['title'][:120])}</div></li>" for r in d["decisions"])
        dec = f"<ul>{dec}</ul>" if dec else "<p class=none>No open item of this mod needs the owner.</p>"
    adv = d["advance"]
    adv_html = (f"<p>{adv['days']} days since the reading rose</p>" if adv["status"] == "READ"
                else f"<p class='st UNMEASURED'>UNMEASURED: {e(adv['why'])}</p>")
    t = d["time"]
    if t["status"] == "READ":
        tm = "<ul>" + "".join(f"<li>{e(c)}: {e(str(h))}{' h' if h != UNM else ''}</li>" for c, h in t["hours"].items()) + "</ul>"
        tm += f"<p class=m>as of {e(t['age'])} ago</p>"
    else:
        tm = f"<p class='st UNMEASURED'>UNMEASURED: {e(t['why'])}</p>"
    return (f"<!doctype html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>{e(d['mod'])} mission</title><style>{brief.CSS}{STYLE}</style></head><body><main>"
            + (f"<a href='{e(base)}/mission'>← missions</a>" if base is not None else "")
            + f"<h2>{e(d['mod'])}</h2><div class='v {'PROVEN' if f['verdict'] == 'MET' else 'UNMEASURED'}'>{e(f['verdict'])}</div>"
            f"<div class=m>{e(head)} · {e(ns)} · modcheck {e(mc['status'])}{' (stale)' if mc['stale'] else ''}, "
            f"{e(mc['age'])} old{' · step 4 ' + e(mc['step4']) if mc['step4'] else ''}</div>"
            f"<h2>Running now</h2>{run}<h2>Open decisions</h2>{dec}<h2>Reading advance</h2>{adv_html}"
            f"<h2>Time ledger</h2>{tm}<h2>Finish line</h2><ul>{bars}</ul>"   # last: 83 bars must not bury the rest on a phone
            f"<div class=foot>Read {e(time.strftime('%Y-%m-%d %H:%M', time.localtime(d['at'])))}. Machine-written, read-only.</div>"
            f"</main></body></html>")


def render_index():
    root, e = _root(), html.escape
    mods = sorted({p.stem for p in root.glob("design/validation_walks/*/*.md")})
    rows = "".join(f"<li><a href='/mission/{e(m)}'>{e(m)}</a></li>" for m in mods)
    return (f"<!doctype html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>Missions</title><style>{brief.CSS}</style></head><body><main><a href='/brief'>← brief</a>"
            f"<h2>Missions</h2><ul>{rows}</ul></main></body></html>")


def page(path, now=None):
    """-> (code, content type, body), the routes brief.page hands over. Writes nothing."""
    if path.rstrip("/") == "/mission":
        return 200, "text/html; charset=utf-8", render_index().encode()
    m = re.fullmatch(rf"/mission/({MOD_RE})(\.json)?", path)
    if not m or not known(m.group(1), _root()):
        return 404, "text/plain", b"no such mod\n"
    d = collect(m.group(1), now)
    if m.group(2):
        return 200, "application/json", json.dumps(d).encode()
    return 200, "text/html; charset=utf-8", render(d).encode()


def main(argv=None):
    ap = argparse.ArgumentParser(description="one read-only mission page")
    ap.add_argument("mod")
    ap.add_argument("--out", help="write the page here, and nothing else anywhere; stdout without it")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if not re.fullmatch(MOD_RE, a.mod) or not known(a.mod, _root()):
        print(f"no such mod: {a.mod}", file=sys.stderr)
        return 2
    d = collect(a.mod)
    body = json.dumps(d, indent=1) if a.json else render(d, base=None)
    if not a.out:
        print(body)
        return 0
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(body)
    print(f"{a.out}: {d['finish']['verdict']}, {d['finish']['proven']} of {d['finish']['bars']} bars proven")
    return 0


if __name__ == "__main__":
    sys.exit(main())
