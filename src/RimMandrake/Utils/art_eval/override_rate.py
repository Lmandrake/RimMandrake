#!/usr/bin/env python3
"""A4 override rate: the share of pictures the art-eval pipeline PASSED that the owner then rejected or redid.

Measure A4 of design/RimMandrake/work_allocation_framework_2026-10-26.md §3.1 (item ART_OVERRIDE_MEASURE_AGENT_VS_OWNER);
it feeds the shadow-sheet trust rule (skill `rimworld-art-evaluation`: under 10% before a template is trusted).

    python3 override_rate.py              # table: per template passed / ruled / overridden / rate
    python3 override_rate.py --json       # the same as one JSON object (plus every overridden picture)
    python3 override_rate.py --check      # sanity probes on the real ledgers; exit 0 when the instrument can see

The join. A judged picture is a decision record in infrastructure/state/art_eval/runs/<run>/decisions.jsonl (production
runs only: not --test, not regress_/race_), identified by its facing source shas (round_series.picture_key). The same
picture judged in several runs is ONE picture: its pipeline verdict is the latest record, and the owner's window opens
at the first record of the trailing run of that verdict. The owner's answer is the LATEST of his acts on any of those
shas inside the window, read from the art ledger (artledger.Index):
  * ruling by=owner trust=ruled  — keep = agreement; redo / reject / purge = override;
  * rejected event (by owner)    — override;  * purge event (by owner) — override (he threw the bytes out);
  * only his LOOKS count (is_look): a sheet answer, his typed words, or a card naming the subject. Acts under a
    blanket card are standing authority, not a look, and are reported apart as `standing_only`;
  * an act on a sha two pictures share (a reused live facing) answers neither; an owner unpurge is a keep;
  * `release` rulings ride a purge (they unprotect a keep) and say nothing on their own: ignored;
  * prefill / legacy-unresolved / flawed-sheet / agent rulings are not his answer: ignored.
His explicit shadow-sheet answers (shadow_log.jsonl, keyed run + subject, no sha) fill pictures the ledger has no
signal for. A passed picture he never ruled on is UNRULED, never agreement (silence is not agreement): the rate is
overridden / ruled, and with nothing ruled it is UNMEASURED, never 0.
The converse (pictures the pipeline regenerated that he then kept) is reported beside it as `regen_kept`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "art"))
import policy as P  # noqa: E402
import round_series as RSR  # noqa: E402

STATE = P.ROOT / "infrastructure/state/art_eval"
PASS = "ACCEPT"
REGEN = ("REGEN", "ESCALATE")
NEGATIVE_VERDICTS = {"redo", "reject", "purge"}
SHADOW_OVERRIDE = {"should_regen", "other", "revert"}
TARGET = 0.10   # the shadow-sheet trust bar the framework row names (under 10%)


def _norm(v) -> str:
    import artledger as A
    return A.normalise_verdict(v)


def subject_names(subject: str) -> set:
    """The names a card would call this subject by: `RM_Irqit__RM_Irqit_RM_Irqit_n` -> {'rm_irqit', 'irqit'}."""
    base = (subject or "").split("__")[0]
    out = {base.lower()}
    for pre in ("RM_", "RSW_", "RUT_", "AA_"):
        if base.startswith(pre):
            out.add(base[len(pre):].lower())
    return {n for n in out if len(n) >= 4}


def is_look(ev: dict, auth: dict, subject: str) -> bool:
    """True when the act shows he LOOKED at this picture: a review-sheet answer (via a .decisions.json), his own typed
    words on it, or a card that names the subject. An act under a blanket card ('2026-10-26 card -> Art audit across
    all creatures', 'Rescale') is the pipeline's own decision installed under standing authority: counting it as his
    agreement would make the pipeline grade itself (it made A4 read 1.4%, 46 of 73 agreements circular, 2026-11-05)."""
    if str(ev.get("via") or "").endswith(".decisions.json"):
        return True
    if auth.get("said"):   # authority() already applies any provenance_fix; the raw field would bypass it
        return True
    card = str(auth.get("by_card") or "").lower()
    return bool(card) and any(n in card for n in subject_names(subject))


def owner_acts(idx, sha: str, subject: str = "") -> list:
    """[(instant, 'keep'|'reject', what, look)] — the owner's acts on these bytes, from the art ledger index; `look`
    says whether the act is his look at the picture (is_look) or standing authority only."""
    out = []

    def add(e, ans, what):
        out.append((P._instant(e.get("ts")), ans, what, is_look(e, idx.authority(e), subject)))
    for e in idx.rulings_by_sha.get(sha, []):
        if e.get("by") != "owner" or e.get("trust") != "ruled":
            continue
        v = _norm(e.get("verdict"))
        if v == "keep":
            add(e, "keep", f"ruling keep {e.get('id')}")
        elif v in NEGATIVE_VERDICTS:
            add(e, "reject", f"ruling {v} {e.get('id')}")
    for e in idx.rejected.get(sha, []):
        if e.get("by") == "owner":
            add(e, "reject", f"rejected {e.get('id')}")
    for e in idx.purge_history.get(sha, []):
        if e.get("type") == "purge" and e.get("by") == "owner":
            add(e, "reject", f"purge {e.get('id')}")
        elif e.get("type") == "unpurge" and e.get("by") == "owner":   # his later words brought the bytes back
            add(e, "keep", f"unpurge {e.get('id')}")
    return out


def pictures(records) -> list:
    """One entry per judged picture: {key, template, subject, run, decision, since, record}. `records` is
    [(run, record)] (round_series.production_decisions); records without source shas have no identity and are skipped."""
    groups = {}
    for run, r in records:
        if run.startswith(("regress_", "race_")):
            continue
        k = RSR.picture_key(r)
        if k is None:
            continue
        groups.setdefault(k, []).append((P._instant(r.get("at")), run, r))
    out = []
    for k, rows in groups.items():
        rows.sort(key=lambda x: x[0])
        last = rows[-1][2].get("decision")
        i = len(rows) - 1
        while i > 0 and rows[i - 1][2].get("decision") == last:
            i -= 1
        t, run, r = rows[-1]
        out.append({"key": k, "template": r.get("template") or "?", "subject": r.get("subject"), "run": run,
                    "runs": sorted({x[1] for x in rows}), "decision": last, "since": rows[i][0], "record": r})
    return out


def join(pics: list, idx, shadow_rows: list) -> list:
    """Each picture with the owner's latest answer after `since`: answer keep|reject|None (what he wants for the
    PICTURE, whatever the pipeline decided), plus its source."""
    by_run_subject = {}
    for p in pics:
        for run in p["runs"]:
            by_run_subject.setdefault((run, p["subject"]), []).append(p)
    # a sha in two pictures (a render that reused the live north) cannot say which picture he answered: an act on it
    # would count for both, so only shas unique to one picture carry an answer
    holders = {}
    for p in pics:
        for s in p["key"]:
            holders.setdefault(s, set()).add(p["key"])
    for p in pics:
        own = [s for s in p["key"] if len(holders[s]) == 1]
        acts = [a for s in own for a in owner_acts(idx, s, p["subject"]) if a[0] > p["since"]]
        looks = [a for a in acts if a[3]]
        p["standing_only"] = bool(acts) and not looks
        if looks:
            t, ans, what, _ = max(looks, key=lambda a: (a[0], a[1] == "reject"))
            p.update(answer=ans, answered_at=t.isoformat(), via=what, source="art_ledger")
        else:
            p.update(answer=None, answered_at=None, via=None, source=None)
    for s in sorted(shadow_rows, key=lambda s: P._instant(s.get("at"))):
        for p in by_run_subject.get((s.get("run"), s.get("subject")), []):
            if p["source"] == "art_ledger" or p["decision"] != s.get("pipeline_decision") \
                    or P._instant(s.get("at")) <= p["since"]:
                continue
            a = s.get("owner_answer")
            # a shadow answer is about the pipeline's DECISION; turn it into what he wants for the PICTURE
            if p["decision"] == PASS:
                ans = "reject" if a in SHADOW_OVERRIDE else "keep" if a == "keep" else None
            else:
                ans = "keep" if a == "should_accept" else "reject" if a == "keep" else None
            if ans:
                p.update(answer=ans, answered_at=s.get("at"), via=f"shadow_log {a}", source="shadow_log")
    return pics


def summarise(pics: list) -> dict:
    def cell(ps):
        passed = [p for p in ps if p["decision"] == PASS]
        ruled = [p for p in passed if p["answer"] in ("keep", "reject")]
        over = [p for p in ruled if p["answer"] == "reject"]
        regen = [p for p in ps if p["decision"] in REGEN]
        regen_ruled = [p for p in regen if p["answer"] in ("keep", "reject")]
        # a regenerated picture he KEPT is the converse override (the pipeline threw out art he wanted)
        regen_kept = [p for p in regen_ruled if p["answer"] == "keep"]
        rate = round(len(over) / len(ruled), 4) if ruled else None
        return {"passed": len(passed), "ruled": len(ruled), "unruled": len(passed) - len(ruled),
                "standing_only": sum(1 for p in passed if p["answer"] is None and p.get("standing_only")),
                "overridden": len(over), "rate": rate,
                "rate_reading": f"{rate:.1%}" if rate is not None else "UNMEASURED: no passed picture carries an owner ruling",
                "under_target": None if rate is None else rate < TARGET,
                "regen": len(regen), "regen_ruled": len(regen_ruled), "regen_kept": len(regen_kept)}
    out = {"as_of": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "target": TARGET,
           "all": cell(pics), "by_template": {}}
    for t in sorted({p["template"] for p in pics}):
        out["by_template"][t] = cell([p for p in pics if p["template"] == t])
    out["overridden"] = [{"subject": p["subject"], "template": p["template"], "runs": p["runs"],
                          "answered_at": p["answered_at"], "via": p["via"]}
                         for p in pics if p["decision"] == PASS and p["answer"] == "reject"]
    return out


def load_shadow(path: Path = STATE / "shadow_log.jsonl") -> list:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()] if path.is_file() else []


def measure(records=None, idx=None, shadow_rows=None) -> tuple[dict, list]:
    if idx is None:
        import artledger as A
        idx = A.Index()
    pics = pictures(RSR.production_decisions() if records is None else records)
    pics = join(pics, idx, load_shadow() if shadow_rows is None else shadow_rows)
    return summarise(pics), pics


def check(summary: dict, pics: list, idx) -> list:
    """Sanity probes (instrument_traps.md: a zero is a query bug until the instrument is shown able to see).
    Returns the failures; empty = the reading stands."""
    bad = []
    if not pics:
        bad.append("no production decision carries source shas: the pipeline side is blind")
    seen = sum(1 for p in pics if any(s in idx.variants or s in idx.rulings_by_sha for s in p["key"]))
    if pics and not seen:
        bad.append(f"none of {len(pics)} judged pictures' shas is known to the art ledger: the join keys do not meet")
    owner_ruled = sum(1 for r in idx.rulings if r.get("by") == "owner" and r.get("trust") == "ruled")
    if not owner_ruled:
        bad.append("the art ledger holds no owner-ruled ruling: the owner side is blind")
    for name, c in [("all", summary["all"])] + list(summary["by_template"].items()):
        if not (c["overridden"] <= c["ruled"] <= c["passed"]):
            bad.append(f"{name}: overridden {c['overridden']} <= ruled {c['ruled']} <= passed {c['passed']} broken")
    if summary["all"]["overridden"] != len(summary["overridden"]):
        bad.append("overridden count disagrees with the overridden list")
    return bad


def table(s: dict) -> str:
    rows = [f"A4 override rate (as of {s['as_of']}; target under {s['target']:.0%}; rate = overridden / ruled)",
            f"{'template':<10} {'passed':>6} {'ruled':>6} {'unruled':>7} {'standing':>8} {'overridden':>10}  rate         regen  regen_kept/ruled"]
    for name, c in [("ALL", s["all"])] + list(s["by_template"].items()):
        rate = c["rate_reading"] if c["rate"] is not None else "UNMEASURED"
        rows.append(f"{name:<10} {c['passed']:>6} {c['ruled']:>6} {c['unruled']:>7} {c['standing_only']:>8} {c['overridden']:>10}  {rate:<12} "
                    f"{c['regen']:>5}  {c['regen_kept']}/{c['regen_ruled']}")
    for o in s["overridden"]:
        rows.append(f"  overridden: {o['subject']} ({o['template']}) {o['via']} at {o['answered_at']}")
    return "\n".join(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true", help="sanity probes; exit 1 when the instrument cannot see")
    a = ap.parse_args(argv)
    import artledger as A
    idx = A.Index()
    s, pics = measure(idx=idx)
    print(json.dumps(s, indent=1) if a.json else table(s))
    if a.check:
        bad = check(s, pics, idx)
        for b in bad:
            print(f"CHECK FAIL: {b}", file=sys.stderr)
        print("CHECK " + ("FAIL" if bad else f"OK: {len(pics)} judged pictures joined; A4 = {s['all']['rate_reading']}"))
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
