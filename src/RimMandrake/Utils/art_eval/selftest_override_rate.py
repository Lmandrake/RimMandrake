#!/usr/bin/env python3
"""Selftest for override_rate.py (A4: pipeline-passed pictures the owner rejected or redid).

Fixture events fold through the REAL artledger.Index, so the join is tested against the ledger's own projection;
the last case runs the instrument on the repo's real ledgers and requires its sanity probes to pass."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "art"))
import artledger as A  # noqa: E402
import override_rate as O  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


SHEET = "Transient/biome_ffar/x_sheet_2026-11-01.decisions.json"
N = [0]


def sha(tag: str) -> str:
    return (tag.encode().hex() * 64)[:64]


def rec(subject, tag, decision, at, template="creature"):
    return {"subject": subject, "template": template, "decision": decision, "at": at,
            "source_sha256": {"south": sha(tag + "s"), "east": sha(tag + "e"), "scale": sha(tag + "panel")}}


def ruling(tag, verdict, ts, by="owner", trust="ruled", via=SHEET, **kw):
    N[0] += 1
    return dict({"type": "ruling", "id": f"r{N[0]}", "by": by, "trust": trust, "verdict": verdict, "ts": ts, "via": via,
                 "target": {"sha": sha(tag + "s")}}, **kw)


def run(records, events, shadow=()):
    idx = A.Index(events=list(events))
    return O.measure(records=records, idx=idx, shadow_rows=list(shadow)) + (idx,)


T0, T1, T2, T3 = "2026-11-01T10:00:00-07:00", "2026-11-01T12:00:00-07:00", "2026-11-02T09:00:00-08:00", "2026-11-03T09:00:00-08:00"


def by_subject(pics):
    return {p["subject"]: p for p in pics}


def main() -> int:
    recs = [
        ("r1", rec("RM_Keep", "a", "ACCEPT", T0)),          # sheet keep after: agreement
        ("r1", rec("RM_Redo", "b", "ACCEPT", T0)),          # sheet redo after: override
        ("r1", rec("RM_Early", "c", "ACCEPT", T1)),         # keep BEFORE the decision: not an answer to it
        ("r1", rec("RM_Blanket", "d", "ACCEPT", T0)),       # keep under a blanket card: standing, not a look
        ("r1", rec("RM_Named__RM_Named_n", "e", "ACCEPT", T0)),   # card naming the subject: a look
        ("r1", rec("RM_Flip", "f", "ACCEPT", T0)),          # keep then purge: latest wins -> override
        ("r1", rec("RM_Release", "g", "ACCEPT", T0)),       # release alone says nothing
        ("r1", rec("RM_Prefill", "h", "ACCEPT", T0)),       # prefill / agent rulings are not his answer
        ("r1", rec("RM_Twice", "i", "ACCEPT", T0)),         # judged twice, one picture; window opens at the first
        ("r2", rec("RM_Twice", "i", "ACCEPT", T2)),
        ("r1", rec("RM_Regen", "j", "REGEN", T0)),          # regenerated, then he kept it: the converse
        ("r1", rec("RM_Shadow", "k", "ACCEPT", T0)),        # only a shadow answer: should_regen -> override
        ("r1", rec("RM_ShadowRegen", "l", "REGEN", T0)),    # shadow 'keep' on a REGEN = he agrees it was bad
        ("regress_x", rec("RM_Regress", "m", "ACCEPT", T0)),   # regression runs are not production
        ("r1", rec("RM_Plant", "n", "ACCEPT", T0, template="plant")),   # passed, never ruled
        ("r1", {"subject": "RM_NoSha", "template": "creature", "decision": "ACCEPT", "at": T0}),
        ("r1", rec("RM_Unpurge", "o", "ACCEPT", T0)),       # purge then his unpurge: keep
        ("r1", rec("RM_Late", "q", "ACCEPT", T2)),          # shadow answer older than the decision: no answer
        ("r1", dict(rec("RM_ShareA", "u", "ACCEPT", T0), source_sha256={"south": sha("us"), "north": sha("shared")})),
        ("r1", dict(rec("RM_ShareB", "v", "ACCEPT", T0), source_sha256={"south": sha("vs"), "north": sha("shared")})),
    ]
    ev = [
        ruling("a", "keep", T2),
        ruling("b", "redo", T2),
        ruling("c", "keep", T0),
        ruling("d", "keep", T2, via="art install (by card)", by_card="2026-10-26 card → Art audit across all creatures"),
        ruling("e", "keep", T2, via="art install (by card)", by_card="Named: keep the new picture? → Keep"),
        ruling("f", "keep", T1),
        {"type": "purge", "id": "p1", "by": "owner", "sha": sha("fe"), "ts": T2, "via": SHEET},
        ruling("g", "release", T2, releases="zzz"),
        ruling("h", "redo", T2, trust="prefill"), ruling("h", "redo", T2, by="agent"),
        ruling("i", "keep", T1),
        ruling("j", "keep", T2),
        ruling("m", "redo", T2),
        {"type": "purge", "id": "p2", "by": "owner", "sha": sha("os"), "ts": T1, "via": SHEET},
        {"type": "unpurge", "id": "u2", "by": "owner", "sha": sha("os"), "ts": T2, "follows": "p2", "said": "bring it back"},
        dict(ruling("x", "redo", T2), target={"sha": sha("shared")}),
    ]
    shadow = [{"at": T2, "run": "r1", "subject": "RM_Shadow", "template": "creature", "pipeline_decision": "ACCEPT",
               "owner_answer": "should_regen", "override": True},
              {"at": T2, "run": "r1", "subject": "RM_ShadowRegen", "template": "creature", "pipeline_decision": "REGEN",
               "owner_answer": "keep", "override": False},
              {"at": T1, "run": "r1", "subject": "RM_Late", "template": "creature", "pipeline_decision": "ACCEPT",
               "owner_answer": "should_regen", "override": True}]
    s, pics, idx = run(recs, ev, shadow)
    p = by_subject(pics)
    check("keep after the decision = agreement", p["RM_Keep"]["answer"] == "keep")
    check("redo after the decision = override", p["RM_Redo"]["answer"] == "reject")
    check("a keep before the decision is no answer to it", p["RM_Early"]["answer"] is None)
    check("blanket-card keep is standing authority, not a look",
          p["RM_Blanket"]["answer"] is None and p["RM_Blanket"]["standing_only"])
    check("card naming the subject is a look", p["RM_Named__RM_Named_n"]["answer"] == "keep")
    check("latest act wins (keep then purge = override)", p["RM_Flip"]["answer"] == "reject")
    check("release alone is no answer", p["RM_Release"]["answer"] is None)
    check("prefill and agent rulings are ignored", p["RM_Prefill"]["answer"] is None)
    check("one picture judged twice is one picture", sum(1 for x in pics if x["subject"] == "RM_Twice") == 1)
    check("its window opens at the first of the trailing ACCEPTs", p["RM_Twice"]["answer"] == "keep")
    check("regenerated then kept = regen_kept", p["RM_Regen"]["answer"] == "keep")
    check("shadow should_regen on a pass = override", p["RM_Shadow"]["answer"] == "reject")
    check("shadow keep on a REGEN = he wanted it gone", p["RM_ShadowRegen"]["answer"] == "reject")
    check("regress_ runs are not production", "RM_Regress" not in p)
    check("an owner unpurge after a purge reads keep", p["RM_Unpurge"]["answer"] == "keep")
    check("a shadow answer older than the decision is no answer", p["RM_Late"]["answer"] is None)
    check("an act on a sha two pictures share answers neither",
          p["RM_ShareA"]["answer"] is None and p["RM_ShareB"]["answer"] is None)
    check("a record without source shas has no identity", "RM_NoSha" not in p)
    a = s["all"]
    # passed: Keep Redo Early Blanket Named Flip Release Prefill Twice Shadow Plant Unpurge Late ShareA ShareB = 15
    # ruled: Keep Redo Named Flip Twice Shadow Unpurge = 7; overridden: Redo Flip Shadow = 3
    check("passed count", a["passed"] == 15, a)
    check("ruled count", a["ruled"] == 7, a)
    check("overridden count", a["overridden"] == 3, a)
    check("rate = overridden / ruled", a["rate"] == round(3 / 7, 4), a)
    check("standing_only counted apart", a["standing_only"] == 1, a)
    check("regen and regen_kept", (a["regen"], a["regen_ruled"], a["regen_kept"]) == (2, 2, 1), a)
    check("an unruled template reads UNMEASURED, never 0",
          s["by_template"]["plant"]["rate"] is None and s["by_template"]["plant"]["rate_reading"].startswith("UNMEASURED"))
    check("overridden list matches the count", len(s["overridden"]) == 3)
    check("probes pass on a seeing fixture", O.check(s, pics, idx) == [], O.check(s, pics, idx))

    s0, p0, i0 = run([], [])
    check("blind fixture: probes fail", len(O.check(s0, p0, i0)) >= 2, O.check(s0, p0, i0))
    check("blind fixture: rate UNMEASURED", s0["all"]["rate"] is None)

    s1, p1, i1 = run([("r1", rec("RM_Z", "z", "ACCEPT", T0))], [ruling("q", "keep", T2)])
    check("join keys that never meet: probe fails",
          any("do not meet" in b for b in O.check(s1, p1, i1)), O.check(s1, p1, i1))

    # the real ledgers: the instrument must see (pipeline side, owner side, keys meeting)
    idx = A.Index()
    sr, pr = O.measure(idx=idx)
    bad = O.check(sr, pr, idx)
    check("real ledgers: sanity probes pass", not bad, bad)
    check("real ledgers: some passed picture is owner-ruled", sr["all"]["ruled"] > 0, sr["all"])

    print(f"{'OK' if not FAILS else 'FAILED'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
