#!/usr/bin/env python3
"""ops_health: Operations' ONE health verdict for the system (PIPELINE_BUDGET_ENFORCE_HEAL_THYSELF).

The owner, 2026-11-03: "Yes relentless fixes itself first." · "Relentless fixes operations or conductor or designer or
any other part of the system before continuing content creation yes." · "I don't want relentless to own assessing
system health. I want it to ask "the system" for its health assessment, and that belongs to the operations component."
Card 2026-11-03 (no verdict): "System work immediately but existing non system work continues. If all system tickets
are already being worked non system work can be selected." Ruling text: design/RimMandrake/standing_rulings.md
"Relentless fixes the system first"; design: build_system_practices_2026-11-03.md idea 5.

ops_watch.run() calls publish() every pass; it writes $RM_OPS_WATCH_DIR/health.json:
  {schema, as_of, t, state: healthy|degraded|unmeasured, inputs, repair, budget: {<sli>: {...}}, spent: [<sli>],
   spent_scope: {<sli>: integrity|all|game|system}, drifted: [<sli>], system_items: [ids, best first],
   content_paused: bool, why}
  SLI      a point ops_watch already measured, bad when it crosses its line (rules "health" block, `slis`). UNMEASURED is
           not bad and not good: it is said, and spends nothing.
  UNIT     every SLI names the unit its line was written against. A point that says another unit has changed meaning under
           the SLI: it reads UNMEASURED and the SLI is listed in `drifted` (alarm SLI_DRIFT), never a confident number. An
           SLI moved to a new key keeps its past through `was` [{key, unit}], read only for passes the new key is absent from.
  BUDGET   per SLI, the hours it read bad in the last window_h, a gap between passes counted at most max_gap_h. Spent at
           allowed_bad_h ("When any SLI is over budget for 24 h, Relentless staffs only pipeline items until it recovers").
  STATE    degraded while any SLI's budget is spent, else healthy. Degraded pauses NEW content only as far as the spent
           SLIs' `scope` reaches (SCOPES; Relentless reads spent_scope); running work continues.
           UNMEASURED when the health rules are unusable: no budget was read, so the verdict says nothing about health and
           never reads as healthy (OPS_HEALTH_FIX_BROKEN_RULES_READ_HEALTHY; it once gave b={} -> healthy). Relentless reads
           it as a shared resource impaired (all new content waits while a system item waits for a place, card
           2026-11-05 "Pause only what it touches") and puts `repair` (open REPAIR_ALARM items, ops_watch's health.unmeasured alarm) first.
  INPUTS   every verdict names what it was made from: rules_sha256 (canonical JSON of the rules ops_watch passed), the
           collector's git sha (the clone this file runs from), the ledger watermark (events, last ts/tsn; None = no
           ledger this pass). Same inputs -> byte-identical verdict, so a strange verdict is explained by re-running it.
  INCIDENT an SLI with `incident: true` (infra_share, churn_items, returned_tokens_pct) is listed in `incident.bad` the pass it
           reads bad, budget or no budget: ops_watch turns that into ONE fixed alarm item (health.incident_slis,
           OPS_CHURN_MEASURE_RETURNS_ARE_NOT_PROGRESS: 47 items churned a night while infra_share sat bad 7.75 h of its 24).
  RECUR    a system item whose fix died once already (live_repeats) leads the list, marked as owing a class guard test until
           `rimflow guard` records one (model.guard_owed; `rimflow close` refuses without it). recurring_unguarded: every alarm
           kind that came back with no guard, open or closed (alarm_census.recurring).
  SYSTEM   open items that are about the system itself (Relentless, Operations, Conductor, Designer, Dispatcher, timers,
           tests, tools), not game content: a word of its SUBJECT from system_words, or an id prefix from system_prefixes,
           and no game mod or content_words word in its id. The subject is the part before the intent word (a twist is a joke
           about how it went, and names tools in passing); a system_words_lead word counts only as the subject's first word
           (HOSE_NET_SELFTEST is a mod's test, SELFTEST_CLOCK is the suite's). Order: alarm items (system_prefixes) first,
           raised, then oldest.

Relentless never computes any of this: it calls read_verdict(); with no fresh verdict it asks system_ids() (this file,
Operations' classifier) for the open system items and puts them first at once, and says so in its reading.

    python3 src/RimMandrake/Utils/ops_health.py show          the published verdict, and whether it is fresh
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

RIMFLOW = str(Path(__file__).resolve().parent.parent / "rimflow")
SCHEMA = "rm.ops_health/1"
HOUR = 3600.0
FILE = "health.json"
STATES = ("healthy", "degraded", "unmeasured")
# What a spent SLI pauses (DEGRADED_PAUSE_FIX_STOPS_ONLY_WHAT_BROKE; owner card 2026-11-05 "Pause only what it touches"):
# integrity/all = a shared resource every run uses, all new content waits; game = content whose lane is the live game;
# system = no content lane depends on it, only places are reserved for the system items. No scope = all, said.
SCOPES = ("integrity", "all", "game", "system")
REPAIR_ALARM = "OPS_HEALTH_RULES_DIAGNOSE"     # ops_watch_rules.json: the alarm on health.unmeasured; its minted ids start so
DEFAULTS = {
    "max_age_min": 45, "window_h": 48, "allowed_bad_h": 24, "max_gap_h": 1.0,
    "slis": [],
    "system_prefixes": ["OPS_"],
    "system_words": [],
    "system_words_lead": [],
    "guard_exempt_kinds": [],
    "content_kinds": ["mod", "art"],
    "content_words": [],
    "system_rank": [],      # Operations' hand order, best first; always system, wherever the words put it
    "not_system": [],       # the classifier's known false friends (a mod's "pool", "ledger", "budget")
}
OPS = {"<": lambda a, b: a < b, "<=": lambda a, b: a <= b, ">": lambda a, b: a > b, ">=": lambda a, b: a >= b}
WORD = re.compile(r"[^A-Za-z0-9]+")


def ops_dir() -> Path:
    return Path(os.environ.get("RM_OPS_WATCH_DIR", "/mnt/d/ClaudeWork/rimmandrake/ops_watch"))


def conf(rules):
    c = dict(DEFAULTS)
    c.update((rules or {}).get("health") or {})
    return c


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v and v not in (float("inf"), float("-inf"))


def bad_of(point, sli):
    """True/False when the point is MEASURED and numeric; None when the instrument could not see."""
    if not isinstance(point, dict) or point.get("m") != "MEASURED" or not is_num(point.get("v")):
        return None
    return bool(OPS[sli["op"]](point["v"], sli["x"]))


def reading_of(points, sli):
    """The point this SLI reads in one pass's {key: point}. Its own key with the unit it was written against; a MEASURED point
    in another unit -> UNMEASURED, marked drifted; its own key absent -> a `was` key, only in that key's old unit."""
    p = points.get(sli["key"])
    if isinstance(p, dict):
        if p.get("m") != "MEASURED" or p.get("unit") == sli["unit"]:
            return p
        return {"m": "UNMEASURED", "v": None, "drifted": True,
                "why": "%s now says %r; this SLI's line was written against %r" % (sli["key"], p.get("unit"), sli["unit"])}
    for w in sli.get("was") or ():
        q = points.get(w["key"])
        if isinstance(q, dict) and q.get("unit") == w["unit"]:
            return q
    return p


def sli_problems(c):
    out = []
    for s in c.get("slis") or []:
        if not isinstance(s, dict) or not s.get("name") or not s.get("key") or s.get("op") not in OPS or not is_num(s.get("x")) \
                or not s.get("unit") or not isinstance(s.get("was") or [], list) or not all(
                    isinstance(w, dict) and w.get("key") and w.get("unit") for w in s.get("was") or []):
            out.append("health sli needs name, key, unit, op in %s, a numeric x and was [{key, unit}]: %r" % (sorted(OPS), s))
        elif not isinstance(s.get("incident", False), bool):
            out.append("health sli %s: incident must be true or false" % s["name"])
        elif s.get("scope", "all") not in SCOPES:
            out.append("health sli %s: scope must be one of %s" % (s["name"], ", ".join(SCOPES)))
    for k in ("max_age_min", "window_h", "allowed_bad_h", "max_gap_h"):
        if not is_num(c.get(k)) or c[k] <= 0:
            out.append("health.%s must be a positive number" % k)
    return out


def bad_hours(samples, sli, now, window_h, max_gap_h):
    """samples: [(t, point)] in any order. -> (hours bad in the window, hours measured in it). A sample holds until the
    next one, at most max_gap_h: a watcher that stopped measuring spends no budget and earns none."""
    lo = now - window_h * HOUR
    pts = sorted(((t, p) for t, p in samples if is_num(t) and t <= now), key=lambda x: x[0])    # never compare two points on a tied t
    bad = seen = 0.0
    for n, (t, p) in enumerate(pts):
        end = min(pts[n + 1][0] if n + 1 < len(pts) else now, t + max_gap_h * HOUR, now)
        start = max(t, lo)
        if end <= start:
            continue
        b = bad_of(p, sli)
        if b is None:
            continue
        seen += end - start
        if b:
            bad += end - start
    return bad / HOUR, seen / HOUR


def budget(points, history, c, now):
    """points: this pass's {key: point}; history: {family: [series records]}. -> {sli name: reading}."""
    out = {}
    for s in c.get("slis") or []:
        fam = s["key"].split(".")[0]
        samples = [(r.get("t"), reading_of(r.get("points") or {}, s)) for r in history.get(fam) or []
                   if isinstance(r, dict)]
        cur = reading_of(points, s)
        samples.append((now, cur))
        bad_h, seen_h = bad_hours(samples, s, now, c["window_h"], c["max_gap_h"])
        now_bad = bad_of(cur, s)
        out[s["name"]] = {"key": s["key"], "line": "%s %s" % (s["op"], s["x"]),
                          "v": cur.get("v") if isinstance(cur, dict) else None,
                          "now": "UNMEASURED" if now_bad is None else ("bad" if now_bad else "ok"),
                          "bad_h": round(bad_h, 2), "measured_h": round(seen_h, 2),
                          "allowed_bad_h": c["allowed_bad_h"], "window_h": c["window_h"],
                          "spent": bad_h >= c["allowed_bad_h"]}
        if now_bad is None:
            out[s["name"]]["why"] = (cur or {}).get("why") if isinstance(cur, dict) else "no reading this pass"
            if isinstance(cur, dict) and cur.get("drifted"):
                out[s["name"]]["drifted"] = True
    for name, why in (c.get("unmeasured_slis") or {}).items():     # an SLI the design names and no instrument has yet
        out[name] = {"now": "UNMEASURED", "why": why, "spent": False}
    return out


def mod_names(root):
    """Lowercase folder names of every game mod in a clone: a folder with an About/About.xml under src/<tier>/."""
    names = set()
    src = Path(root) / "src"
    try:
        for tier in src.iterdir():
            if not tier.is_dir():
                continue
            for mod in tier.iterdir():
                if (mod / "About" / "About.xml").is_file():
                    names.add(mod.name.lower())
    except OSError:
        pass
    return names


def words_of(item_id, title):
    w = [x.lower() for x in WORD.split("%s %s" % (item_id or "", title or "")) if x]
    return set(w) | {a + b for a, b in zip(w, w[1:])}


def subject_words(iid):
    """The id's subject, lower case: what stands before the intent word (model.parse_name); a legacy id has no hinge, so all of
    it but the trailing number."""
    if RIMFLOW not in sys.path:
        sys.path.insert(0, RIMFLOW)
    import model
    p = model.parse_name(iid)
    return [w.lower() for w in (p[0] if p else re.sub(r"_\d+$", "", iid).split("_"))]


def owes_guard(it):
    """model.guard_owed: one rule, counted in deaths (a first sighting is none), wherever it is asked."""
    if RIMFLOW not in sys.path:
        sys.path.insert(0, RIMFLOW)
    import model
    return model.guard_owed(it)


def unguarded(world, c):
    """Recurring alarm kinds with no guard (alarm_census.recurring), or None when the alarm log cannot be read."""
    if RIMFLOW not in sys.path:
        sys.path.insert(0, RIMFLOW)
    import alarm_census as AC
    try:
        rows = AC.read_log(str(ops_dir() / "alarms_log.jsonl"))
    except OSError:
        return None
    return AC.recurring(rows, world.items, c["guard_exempt_kinds"])


def rank_of(iid, c):
    """The item's place on Operations' hand order, or None. An entry ending in * is a family (new reds rank as they appear)."""
    for n, e in enumerate(c["system_rank"]):
        if iid == e or (e.endswith("*") and iid.startswith(e[:-1])):
            return n
    return None


def is_system(item, c, mods):
    """Operations' classifier: an open item about the system itself, never one that names a game mod."""
    iid = getattr(item, "id", "") or ""
    if iid in c["system_rank"]:         # named by hand, exactly, beats everything below
        return True
    if iid in c["not_system"]:          # an exact not_system id beats a family glob (SELFTEST_* never claims one)
        return False
    if rank_of(iid, c) is not None:     # a family glob beats every word below, either way
        return True
    if (getattr(item, "kind", None) or "") in c["content_kinds"]:
        return False
    words = words_of(iid, "")       # the id, never the title: titles of content items name tools in passing
    if words & mods or words & {w.lower() for w in c["content_words"]}:
        return False
    if any(iid.startswith(p) for p in c["system_prefixes"]):
        return True
    subject = subject_words(iid)
    strong = {w.lower() for w in c["system_words"]}
    lead = {w.lower() for w in c["system_words_lead"]}
    return bool(subject) and (subject[0] in strong | lead or bool(words_of("_".join(subject), "") & (strong - lead)))


def system_items(world, rules, root):
    """Open system items, best first: Operations' hand order (system_rank), then a fix that already died once (live_repeats:
    the class came back, it owes a guard test), then alarm items (system_prefixes), raised, then oldest."""
    c = conf(rules)
    mods = mod_names(root)
    items = [it for it in world.items.values() if getattr(it, "open", False) and is_system(it, c, mods)]
    last = len(c["system_rank"])
    items.sort(key=lambda it: (last if rank_of(it.id, c) is None else rank_of(it.id, c), not (getattr(it, "live_repeats", 0) or 0), not any(it.id.startswith(p) for p in c["system_prefixes"]),
                               not getattr(it, "raised", None), getattr(it, "created_at", None) or "", it.id))
    return items


def system_ids(world, rules, root):
    return [it.id for it in system_items(world, rules, root)]


def incident(b, c):
    """-> {bad: [sli], cause, unmeasured: [sli]} over the incident SLIs, from this pass's budget readings."""
    names = [s["name"] for s in c.get("slis") or [] if isinstance(s, dict) and s.get("incident") is True]
    bad = [n for n in names if (b.get(n) or {}).get("now") == "bad"]
    return {"slis": names, "bad": bad, "unmeasured": [n for n in names if (b.get(n) or {}).get("now") not in ("bad", "ok")],
            "cause": "; ".join("%s %s (line %s)" % (n, b[n].get("v"), b[n].get("line")) for n in bad) or "none"}


def rules_sha256(rules):
    """sha256 of the rules as canonical JSON: the same object read from any clone hashes the same."""
    return hashlib.sha256(json.dumps(rules, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def collector_sha():
    """The git HEAD of the clone this file runs from (the collector's code), or None when git cannot say."""
    try:
        r = subprocess.run(["git", "-C", str(Path(__file__).resolve().parent), "rev-parse", "HEAD"],
                           capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    sha = r.stdout.strip()
    return sha if r.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}", sha) else None


def ledger_mark(events):
    """The ledger watermark of an event list: {events, last_ts, last_tsn}; None when there was no ledger."""
    if events is None:
        return None
    ts = [str(e.get("ts") or "") for e in events if isinstance(e, dict)]
    tsn = [e["tsn"] for e in events if isinstance(e, dict) and isinstance(e.get("tsn"), int) and not isinstance(e.get("tsn"), bool)]
    return {"events": len(events), "last_ts": max(ts) if ts else None, "last_tsn": max(tsn) if tsn else None}


def verdict(points, history, world, rules, root, now, stamp=None):
    """stamp: {collector_sha, ledger} as the caller measured them (ops_watch passes the ledger mark); a missing key is
    measured here (collector_sha) or None (ledger)."""
    c = conf(rules)
    probs = sli_problems(c)
    b = budget(points, history, c, now) if not probs else {}
    spent = sorted(k for k, v in b.items() if v.get("spent"))
    scope_of = {s["name"]: s.get("scope", "all") for s in c.get("slis") or [] if isinstance(s, dict) and s.get("name")}
    spent_scope = {k: scope_of.get(k, "all") for k in spent}
    drifted = sorted(k for k, v in b.items() if v.get("drifted"))
    state = "unmeasured" if probs else "degraded" if spent else "healthy"
    stamp = dict(stamp or {})
    inputs = {"rules_sha256": rules_sha256(rules),
              "collector_sha": stamp["collector_sha"] if "collector_sha" in stamp else collector_sha(),
              "ledger": stamp.get("ledger")}
    items = system_items(world, rules, root) if world is not None else None
    ids = [it.id for it in items] if items is not None else None
    # design idea 5: a twice-seen alarm closes only with a class fix, a guard test that fails on the whole class
    recurring = [{"id": it.id, "outages": it.live_repeats, "owes": "a guard test for the class, shown failing on this instance"}
                 for it in items or () if owes_guard(it)]
    why = ("error budget spent: " + ", ".join("%s %sh bad of %sh" % (k, b[k]["bad_h"], c["allowed_bad_h"]) for k in spent)
           if spent else "every SLI inside its budget")
    if drifted:
        why += "; meaning changed under: " + ", ".join(drifted)
    if probs:
        why = "UNMEASURED: health rules unusable, no budget read, this is no health reading: " + "; ".join(probs)
    if ids is None:
        why += "; no ledger this pass: system_items unknown"
    repair = [i for i in ids or () if i.startswith(REPAIR_ALARM)] if probs else []
    return {"schema": SCHEMA, "as_of": iso(now), "t": now, "state": state, "inputs": inputs, "repair": repair, "budget": b, "spent": spent, "spent_scope": spent_scope, "drifted": drifted,
            "system_items": ids, "recurring": recurring, "incident": incident(b, c), "recurring_unguarded": unguarded(world, c) if world is not None else None, "content_paused": state == "degraded", "max_age_min": c["max_age_min"], "why": why}


def publish(points, history, world, rules, root, now, path=None, stamp=None):
    v = verdict(points, history, world, rules, root, now, stamp)
    p = Path(path) if path else ops_dir() / FILE
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(v, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, p)
    return v


def read_verdict(now=None, path=None, max_age_min=None):
    """-> (verdict or None, why). None when the file is missing, unreadable, foreign or older than its own max age."""
    now = time.time() if now is None else now
    p = Path(path) if path else ops_dir() / FILE
    try:
        v = json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "no health verdict at %s" % p
    except (OSError, ValueError) as e:
        return None, "health verdict unreadable: %s: %s" % (type(e).__name__, str(e)[:120])
    if not isinstance(v, dict) or v.get("schema") != SCHEMA or not is_num(v.get("t")) \
            or v.get("state") not in STATES or not isinstance(v.get("system_items"), (list, type(None))):
        return None, "health verdict malformed at %s" % p
    age = max_age_min if max_age_min is not None else v.get("max_age_min") if is_num(v.get("max_age_min")) else DEFAULTS["max_age_min"]
    if now - v["t"] > age * 60:
        return None, "health verdict stale: as_of %s, %.0f min old (max %s)" % (v.get("as_of"), (now - v["t"]) / 60, age)
    return v, "fresh: %s as of %s" % (v["state"], v.get("as_of"))


def main(argv=None):
    a = argv if argv is not None else sys.argv[1:]
    if a[:1] != ["show"]:
        print(__doc__.strip().splitlines()[-1].strip())
        return 2
    v, why = read_verdict()
    print(why)
    if v:
        print("state %s; spent %s; drifted %s; %d system items first" % (v["state"], v["spent"] or "none", v.get("drifted") or "none", len(v["system_items"] or ())))
        inp = v.get("inputs") or {}
        try:
            with open(Path(__file__).resolve().parent / "ops_watch_rules.json", encoding="utf-8") as f:
                here = rules_sha256(json.load(f))
        except (OSError, ValueError) as e:
            here = "UNMEASURED (%s)" % type(e).__name__
        print("inputs: rules %s (%s this clone's rules), collector %s, ledger %s" % (
            str(inp.get("rules_sha256"))[:12], "SAME AS" if inp.get("rules_sha256") == here else "DIFFERS FROM",
            inp.get("collector_sha"), inp.get("ledger")))
    return 0 if v else 1


if __name__ == "__main__":
    sys.exit(main())
