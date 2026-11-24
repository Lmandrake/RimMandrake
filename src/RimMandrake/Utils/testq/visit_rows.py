"""testq/visit_rows.py - a finished job of an in-game visit becomes rows of that visit's rows.jsonl, by program
(RIMMANDRAKE_COUNT_LANE_RESULTS_WHERE_VISITS_DECIDE; page design/specs/2026-11-24-stage-six-checks-to-steve/boundary.md;
tests selftest_stage6_checks.py; the contract: design/specs/2026-11-23-stevedesktop-work-to-code/acceptance/
count_visit_rows_accept.py).

  rows_of(rec, table, identity) -> [row], one per check that the job decided whole
  write(visit_dir, rows) -> how many were new; a row of the same (job, test) is never written twice
  ingest(rec, root) -> {"visit_rows": n, ...} | {"visit_rows": 0, "why": ...}; never raises for a bad record

PASS reads SUCCESS; FAIL reads UNRESOLVED until someone classes it; all else reads COULD NOT LOOK, which speaks for nobody
and never replaces a row (live_kinds.later). A row with no readable identity reads COULD NOT LOOK: which build it ran on
is unknown. The build match decides later whether a row counts."""
import fcntl
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.abspath(os.path.join(HERE, "..", "..", "rimflow"))
NO_LOOK = "COULD NOT LOOK"
ID_FIELDS = ("mod_sha", "mod_hash", "game_build", "active_mods", "deployed_folder", "tier", "full_list")
REQUIRED = ("mod_sha", "mod_hash", "game_build", "active_mods")


def _rf(name):
    if RIMFLOW not in sys.path:
        sys.path.append(RIMFLOW)
    return __import__(name)


def game_of(rec):
    """-> Steve1 | Steve2 | the host as written. A record that names no host ran on Steve1 (the lane before Steve2)."""
    res = rec.get("result") or {}
    key = str(res.get("host") or rec.get("host") or "stevedesktop").lower()
    return {"stevedesktop": "Steve1", "stevedesktop.a": "Steve1", "stevedesktop.b": "Steve2"}.get(key, key)


def _reading(hits):
    v = [str(r.get("verdict") or "").upper() for r in hits]
    if "FAIL" in v:
        return "FAIL"
    return "PASS" if v and all(x == "PASS" for x in v) else NO_LOOK


def rows_of(rec, table, identity):
    res, job = rec.get("result") or {}, rec.get("job") or {}
    sel = job.get("selector") if isinstance(job.get("selector"), dict) else {}
    rows = [r for r in res.get("rows") or [] if isinstance(r, dict)]
    facts = ((res.get("checks") or {}).get("rows") or {}) if isinstance(res.get("checks"), dict) else {}
    lacks = [k for k in REQUIRED if not (identity or {}).get(k)]
    out = []
    for t in sorted(table):
        spec = table[t] if isinstance(table[t], dict) else {}
        if t in (sel.get("checks") or []):
            hits = [r for r in rows if r.get("chain") == "checks" and r.get("row") == t]
        else:
            ch = (spec.get("testq") or {}).get("chains") if isinstance(spec.get("testq"), dict) else None
            if not ch or not set(ch) <= set(sel.get("chains") or []):
                continue
            by = [[r for r in rows if r.get("chain") == c] for c in ch]
            hits = [r for b in by for r in b] if all(by) else None
            if hits is None and res.get("outcome") == "DONE":
                continue            # a chain of it has no row: the check was not decided whole
            hits = hits or []
        if res.get("outcome") != "DONE":
            v, det = NO_LOOK, "the job ended %s/%s: %s" % (res.get("outcome"), res.get("cause"), str(res.get("note"))[:300])
        else:
            v = _reading(hits)
            show = [r for r in hits if str(r.get("verdict")).upper() != "PASS"] if v != "PASS" else hits
            det = "; ".join("%s %s%s" % (r.get("row"), r.get("verdict"), ": " + str(r["detail"])[:300] if r.get("detail") else "")
                            for r in show)[:1200] or "the job has no row of this check"
        if lacks and v != NO_LOOK:
            v, det = NO_LOOK, "%s, so this reading counts nothing: it read %s" % (
                "the build identity could not be read (%s)" % ", ".join(lacks) if t in (sel.get("checks") or []) else
                "a chain job runs on modcheck's own mod list, which is no tier's list (the visit's driver runs this check)", det)
        x = facts.get(t) or {}
        row = {"test": t, "verdict": v, "outcome": {"PASS": "SUCCESS", "FAIL": "UNRESOLVED"}.get(v, NO_LOOK), "forbidden": [],
               "game": game_of(rec), "job": job.get("id"), "attempt": res.get("attempt"), "detail": det,
               "command": x.get("command") or "testq %s" % (",".join(sel.get("checks") or sel.get("chains") or [])),
               "held": x.get("held") or [], "site_checked": bool(x.get("site")), "by": "testq/visit_rows.py"}
        if x.get("site"):
            row["site"] = x["site"]
        row.update({k: identity[k] for k in ID_FIELDS if (identity or {}).get(k) is not None})
        out.append(row)
    return out


def write(visit_dir, rows):
    """Append the new rows, under a lock file of the visit's own."""
    os.makedirs(visit_dir, exist_ok=True)
    path = os.path.join(visit_dir, "rows.jsonl")
    with open(path, "a+", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        text = f.read()
        have = set()
        for ln in text.splitlines():
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            if isinstance(r, dict):
                have.add((r.get("job"), r.get("test")))
        new = [r for r in rows if (r.get("job"), r.get("test")) not in have]
        if new:
            f.write(("\n" if text and not text.endswith("\n") else "") + "".join(json.dumps(r, sort_keys=True) + "\n"
                                                                               for r in new))
    return len(new)


def open_visit(root, mod, visit):
    """-> (visit, None) when VISIT is the mod's open one, else (None, why)."""
    M = _rf("maturation")
    rec = M.load(root, mod)
    if not rec or rec.get("stage") != "in_game":
        return None, "%s is not in in-game acceptance now" % mod
    n = max(1, len(M.ingame_openings(rec)))
    if n != visit:
        return None, "the job was sent for visit %s; visit %d is open now" % (visit, n)
    return n, None


def identity_of(res):
    """-> the identity a checks job recorded, or None: a chain job runs on modcheck's own composed list, no tier's list,
    so its rows could never match a tier and must never replace one that does."""
    d = (res.get("checks") or {}).get("identity") if isinstance(res.get("checks"), dict) else None
    return d if isinstance(d, dict) and not d.get("why") else None


def tier_lists():
    """-> build_match's tier lister on this machine (one scan of the installed mods)."""
    return _rf("build_match").tier_lister({})


def matched(identity, tiers):
    """-> (identity, None) when its mod list is its tier's as an Archmagi install builds it, else (None, why). The build
    match counts no other list, and a later row that cannot count would hide an earlier one that does (2026-11-24:
    SteveDesktop lacked Cherry Picker, so each tier there was one mod short)."""
    if not identity:
        return None, "no identity could be read"
    BM = _rf("build_match")
    if not identity.get("tier"):
        return None, "the run names no tier"
    ref, why = tiers(identity["tier"])
    if ref is None:
        return None, "tier %s gives no list here: %s" % (identity["tier"], why)
    if BM.same_list(identity.get("active_mods"), ref):
        return identity, None
    game, said = BM.other_tier_match(identity["tier"], identity.get("active_mods"), tiers)
    if game:
        return identity, None
    return None, "its mod list is not tier %s's: %s%s" % (identity["tier"], BM._first_diff(identity.get("active_mods"), ref), said)


def ingest(rec, root):
    job, res = rec.get("job") or {}, rec.get("result") or {}
    if job.get("visit") is None:
        return None
    mod = job.get("mod")
    n, why = open_visit(root, mod, job["visit"])
    if n is None:
        return {"visit_rows": 0, "why": why}
    if res.get("outcome") != "DONE":    # no check ran: 197 rows of one stale-companion job said so, once each (2026-11-24)
        return {"visit_rows": 0, "no_look": "the job ended %s/%s before its checks ran" % (res.get("outcome"), res.get("cause"))}
    p = os.path.join(root, "design", "concepts", mod, "version", "test_table.json")
    with open(p, encoding="utf-8") as f:
        table = {k: t for k, t in (json.load(f).get("tests") or {}).items() if isinstance(t, dict) and str(t.get("stage")) == "6"}
    ident, why = identity_of(res), None
    if ident:
        ident, why = matched(ident, tier_lists())
    rows = rows_of(rec, table, ident)
    if why:
        for r in rows:
            if r["verdict"] == NO_LOOK:
                r["detail"] = ("%s | %s" % (why, r["detail"]))[:1500]
    rel = "design/concepts/%s/version/in_game/visit_%d" % (mod, n)
    return {"visit_rows": write(os.path.join(root, rel), rows) if rows else 0, "path": rel + "/rows.jsonl", "no_look": why,
            "verdicts": {v: sum(1 for r in rows if r["verdict"] == v) for v in sorted({r["verdict"] for r in rows})}}
