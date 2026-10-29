#!/usr/bin/env python3
"""audit_hardflag_file.py - files every Auditor pre-screen hard flag as a defect ticket, no AI
(item AUDITOR_BUILD_HARD_FLAG_FILER_NO_AI; roles/auditor.md "The daily audit" step 1).

A hard flag (audit_prescreen_rules.json `hard_flags`: sha missing / HEAD / unresolvable, evidence path absent) is a
defect found without a re-check, so filing it must not wait on audit capacity (GPT review #6). The Auditor's
pre_launch runs this right after audit_prescreen.py; the Auditor then only confirms the filings landed.

  - Reads prescreen.json. Missing, torn, older than `max_prescreen_age_s`, or not the pre-screen's shape (a row with
    no `hard` list, `hard_flagged` disagreeing with the rows) -> UNMEASURED, exit 2, nothing filed: the Auditor then
    never starts (pre_launch), which is right, since its whole day reads the same file.
  - One ticket per hard-flagged (item, sha): `rimflow file <NAME> --kind defect --caused-by <item>` for the item's
    owning work seat (else `fallback_for`). Its `why` carries the marker `[hardflag ITEM@SHA]`.
  - Idempotent against the LEDGER, not a state file: a `file` event caused_by the item whose why holds the marker
    means it is already filed, by this program or by an Auditor by hand. A new sha on the same item is a new ticket.
  - Writes hardflag_filed.json beside the pre-screen: status OK | PARTIAL, filed / already / failed. A failed filing
    is loud (stderr, status PARTIAL) but exits 0: the Auditor still runs and files the `failed` rows by hand, which
    is the prompt's own fallback. Losing the whole audit to one refused filing would be the worse failure.

The ledger events land in the role seat's shard (RIMFLOW_SEAT, set by role_launch); the Auditor commits and
publishes that shard before it stops (auditor.md "Before you stop").

    python3 src/RimMandrake/rimflow/audit_hardflag_file.py [--prescreen P] [--out P] [--seat S] [--dry-run]
"""
import argparse, datetime, hashlib, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
RULES = os.path.join(HERE, "audit_prescreen_rules.json")
CLI = os.path.join(HERE, "cli.py")
PRESCREEN = "/mnt/d/ClaudeWork/rimmandrake/auditor/prescreen.json"
OUT = os.path.join(os.path.dirname(PRESCREEN), "hardflag_filed.json")


def _model():
    from rimflow import model
    return model


def load_conf(path=RULES):
    with open(path) as f:
        return json.load(f)["hardflag_filer"]


def _epoch(ts):
    return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()


def marker(item, sha):
    return "[hardflag %s@%s]" % (item, sha or "-")


def load_prescreen(path, now, max_age_s):
    """-> the pre-screen doc. Raises OSError / ValueError for anything that is not a fresh, well-formed pre-screen."""
    with open(path) as f:
        d = json.load(f)
    if not isinstance(d, dict) or not isinstance(d.get("ranked"), list) or not d.get("generated"):
        raise ValueError("%s is not a pre-screen (no generated/ranked)" % path)
    age = now - _epoch(d["generated"])
    if age > max_age_s:
        raise ValueError("%s generated %s is %d s old (> max_prescreen_age_s %d): its pre_launch did not rewrite it"
                         % (path, d["generated"], age, max_age_s))
    for r in d["ranked"]:
        if not isinstance(r, dict) or not r.get("item") or not isinstance(r.get("hard"), list):
            raise ValueError("%s has a row with no item or no hard list: %r" % (path, r)[:300])
    rows_hard = sorted(r["item"] for r in d["ranked"] if r["hard"])
    if sorted(d.get("hard_flagged") or []) != rows_hard:
        raise ValueError("%s hard_flagged %r disagrees with its rows %r" % (path, d.get("hard_flagged"), rows_hard))
    return d


def filed_markers(events):
    """(item, marker) for every `file` event already on the ledger that carries a hardflag marker for its caused_by."""
    out = set()
    for e in events:
        if e.get("event") == "file" and e.get("caused_by"):
            why = str(e.get("why") or "")
            if "[hardflag %s@" % e["caused_by"] in why:
                i = why.index("[hardflag %s@" % e["caused_by"])
                out.add((e["caused_by"], why[i:why.index("]", i) + 1]))
    return out


def mint(item, sha, known, prefix):
    """A deterministic, mint-clean name: <prefix>_<4 hex of item@sha>, salted on collision."""
    m = _model()
    for salt in range(50):
        h = hashlib.sha1(("%s@%s#%d" % (item, sha, salt)).encode()).hexdigest()[:4].upper()
        name = "%s_%s" % (prefix, h if any(c.isalpha() for c in h) else "X" + h[1:])
        if not m.mint_problems(name, known):
            return name
    raise RuntimeError("no mintable hard-flag ticket name for %s@%s" % (item, sha))


def plan(doc, events, owners, conf, known_ids):
    """Pure but for mint's name rules. -> (todo, already). todo rows: name, item, sha, flags, for, title, why."""
    done = filed_markers(events)
    known = set(known_ids)
    todo, already = [], []
    for r in doc["ranked"]:
        if not r["hard"]:
            continue
        sha = (r.get("sha") or "").strip()
        mk = marker(r["item"], sha)
        if (r["item"], mk) in done:
            already.append({"item": r["item"], "sha": sha, "hard": r["hard"]})
            continue
        owner = owners.get(r["item"])
        seat = owner if owner in conf["work_seats"] else conf["fallback_for"]
        name = mint(r["item"], sha, known, conf["name_prefix"])
        known.add(name)
        todo.append({"name": name, "item": r["item"], "sha": sha, "hard": r["hard"], "for": seat,
                     "title": ("Auditor hard flag on %s close %s: %s" % (r["item"], sha or "(no sha)",
                                                                         ", ".join(r["hard"])))[:200],
                     "why": "audit hard flag, filed with no AI by audit_hardflag_file.py %s: %s"
                            % (mk, ", ".join(r["hard"])),
                     "caused_by": r["item"]})
    return todo, already


FLAG_MEANS = {
    "sha_missing": "the close records no sha, so no one can see what was shipped",
    "sha_head_literal": "the close records the literal `HEAD`, which names nothing once HEAD moves",
    "sha_unresolvable": "the close's sha does not resolve in this clone (never published, or mistyped)",
    "evidence_path_absent": "a verify event cites an evidence path that does not exist",
}


def prose(t):
    lines = ["## spec",
             "The Auditor's no-AI pre-screen raised hard flag(s) on the close of `%s` (sha `%s`):" % (t["item"],
                                                                                                  t["sha"] or "none"),
             ""]
    lines += ["- `%s`: %s." % (f, FLAG_MEANS.get(f, "see audit_prescreen_rules.json")) for f in t["hard"]]
    lines += ["", "A hard flag is a defect found without a re-check (roles/auditor.md step 1). Correct the record: "
              "find the real published sha (or the evidence) and record it on `%s`." % t["item"], "",
              "## verify", "Re-run `python3 src/RimMandrake/rimflow/audit_prescreen.py --days 7 --out <tmp>`: "
              "the item no longer carries these hard flags, or its corrected record is noted on it.", "",
              "## notes", "Filed by `src/RimMandrake/rimflow/audit_hardflag_file.py` (no AI) %s." % marker(t["item"],
                                                                                                       t["sha"])]
    return "\n".join(lines) + "\n"


def cli_filer(t, seat, conf):
    env = dict(os.environ, RIMFLOW_SEAT=seat)
    r = subprocess.run([sys.executable, CLI, "file", t["name"], "--seat", seat, "--for", t["for"],
                        "--title", t["title"], "--kind", conf["kind"], "--needs", conf["needs"],
                        "--caused-by", t["caused_by"], "--why", t["why"]],
                       env=env, capture_output=True, text=True, timeout=120)
    return r.returncode, (r.stdout + r.stderr).strip()


def write_json(path, d):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w") as f:
        json.dump(d, f, indent=1)
    os.replace(tmp, path)


def main(argv=None, events=None, owners=None, filer=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--prescreen", default=PRESCREEN)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--seat", default=os.environ.get("RIMFLOW_SEAT") or "BENCH")
    ap.add_argument("--dry-run", action="store_true", help="plan and print; file nothing, write no record")
    ap.add_argument("--no-prose", action="store_true", help="do not write items/<NAME>.md (tests)")
    a = ap.parse_args(argv)
    conf = load_conf()
    now = time.time()
    try:
        doc = load_prescreen(a.prescreen, now, conf["max_prescreen_age_s"])
        if events is None:
            events = _model().read()
            if not events:
                raise ValueError("ledger read returned no events")
        if owners is None:
            owners = {i: it.owner for i, it in _model().replay(events).items.items()}
    except (OSError, ValueError) as ex:
        print("UNMEASURED: %s; no hard flag filed" % ex, file=sys.stderr)
        return 2
    known = set(owners) | {e.get("id") for e in events if e.get("id")}
    todo, already = plan(doc, events, owners, conf, known)
    if a.dry_run:
        for t in todo:
            print("WOULD FILE %s for %s caused_by %s: %s" % (t["name"], t["for"], t["item"], t["title"]))
        print("%d to file, %d already filed" % (len(todo), len(already)))
        return 0
    filer = filer or (lambda t, seat: cli_filer(t, seat, conf))
    filed, failed = [], []
    for t in todo:
        path = None
        if not a.no_prose:
            path = _model().item_path(t["name"], for_write=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(prose(t))
        rc, out = filer(t, a.seat)
        if rc == 0:
            filed.append({k: t[k] for k in ("name", "item", "sha", "hard", "for")})
        else:
            if path and os.path.exists(path):
                os.remove(path)
            failed.append(dict({k: t[k] for k in ("name", "item", "sha", "hard", "for")}, error=out[-300:]))
            print("FAILED to file %s on %s: %s" % (t["name"], t["item"], out[-300:]), file=sys.stderr)
    rec = {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
           "prescreen": a.prescreen, "prescreen_generated": doc["generated"],
           "status": "PARTIAL" if failed else "OK", "seat": a.seat,
           "filed": filed, "already": already, "failed": failed}
    write_json(a.out, rec)
    print("hard flags: %d filed, %d already filed, %d FAILED -> %s" % (len(filed), len(already), len(failed), a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
