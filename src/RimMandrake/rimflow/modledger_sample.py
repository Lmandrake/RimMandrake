#!/usr/bin/env python3
"""modledger_sample.py — draw a seeded sample of one mod's ticket-mined ledger entries for a judge that did not mine.

    python3 src/RimMandrake/rimflow/modledger_sample.py --mod GimmeSomeSlack --seed 20261116 --out <path>

Population: the BACKFILL events citing an `item:` ref (ticket-mined), in ledger read order. Each sampled entry carries
its ticket's sources (item file when one exists, the rimflow shard lines on the ticket) and every OTHER entry mined
from the same ticket, so the judge can rule MISSED on the set, not only on the line. The judge's pass rule is the
item's: >= 18 of 20 FAITHFUL and 0 WRONG (design/specs/2026-11-15-mod-ledger-entry-standard.md rule 10 and §5).
"""
import argparse
import json
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modledger as M                                            # noqa: E402


def draw(root, mod, seed, n=20):
    evs = [e for e in M.read(root, mod) if e.get("_shard") == "BACKFILL"]
    pop = [e for e in evs if any(str(r).startswith("item:") for r in e.get("evidence") or [])]
    picks = sorted(random.Random(seed).sample(range(len(pop)), min(n, len(pop))))
    by_ticket = {}
    for e in pop:
        for r in e["evidence"]:
            if r.startswith("item:"):
                by_ticket.setdefault(r[5:], []).append(e)
    out = []
    for i in picks:
        e = pop[i]
        tickets = [r[5:] for r in e["evidence"] if r.startswith("item:")]
        paths = []
        for t in tickets:
            for p in ("infrastructure/state/items/%s.md" % t, "infrastructure/state/items/closed/%s.md" % t):
                if os.path.exists(os.path.join(root, p)):
                    paths.append(p)
        siblings = [{"id": s["id"], "kind": s["kind"], "subject": s["subject"], "body": s["body"]}
                    for t in tickets for s in by_ticket.get(t, []) if s["id"] != e["id"]]
        out.append({"index": i, "id": e["id"], "kind": e["kind"], "subject": e["subject"], "body": e["body"],
                    "evidence": e["evidence"], "code_sha": e.get("code_sha"), "authority": e.get("authority"),
                    "source_tickets": tickets, "source_ticket_paths": paths,
                    "rimflow": ["python3 src/RimMandrake/rimflow/cli.py show %s" % t for t in tickets],
                    "same_ticket_entries": siblings})
    return pop, out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mod", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--root", default=None)
    o = ap.parse_args(argv)
    root = o.root or M.default_root()
    pop, samples = draw(root, o.mod, o.seed, o.n)
    sha = subprocess.run(["git", "-C", root, "rev-parse", "--short=12", "HEAD"], capture_output=True,
                         text=True, timeout=60).stdout.strip()
    doc = {"mod": o.mod, "round": 2, "ledger": "design/concepts/%s/ledger/BACKFILL.jsonl" % o.mod, "ledger_sha": sha,
           "population": "BACKFILL events citing an item: ref (ticket-mined), in ledger read order",
           "population_size": len(pop), "seed": o.seed,
           "draw": "random.Random(%d).sample(range(population_size), %d), sorted" % (o.seed, len(samples)),
           "miner": "modledger_backfill.py with the per-ticket reading (modledger_reader.py) after "
                    "RIMMANDRAKE_FIX_MINER_JUDGE_FAILED_SLACK_EIGHT_OF_TWENTY; judge it with a reader that did not mine",
           "pass_rule": ">= 18 FAITHFUL and 0 WRONG of 20; rule per entry FAITHFUL / WRONG / NARRATION / MISSED",
           "reference": "design/specs/2026-11-15-mod-ledger-entry-standard.md rule 10 and §5; the round-1 verdicts "
                        "mining_samples/<Mod>.judge.json name the failure shapes",
           "samples": samples}
    with open(o.out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print("sample %s: %d of %d ticket-mined entries, seed %d -> %s" % (o.mod, len(samples), len(pop), o.seed, o.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
