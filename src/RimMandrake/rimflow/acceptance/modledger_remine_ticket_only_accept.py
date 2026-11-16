#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_REMINE_SLACK_TICKET_ONLY_ITEMS_HOLD_REFUTED_CAUSES: the Gimme Some Slack ledger,
re-mined under ticket-only mining (dc8d51c60c), holds the refuted causes that live in tickets with no item file, and
its packet stays in budget by its line rule, never by dropping an open finding, a refuted cause or his answer.

    python3 src/RimMandrake/rimflow/acceptance/modledger_remine_ticket_only_accept.py [GimmeSomeSlack]   # PASS 7/7

THE CONTRACT: (1) the ledger mines tickets that have no item file (finding.open citing item:<id>, no
infrastructure/state/items/[closed/]<id>.md); (2) at least one cause.refuted cites such a ticket (0 at filing,
62c18af00dbd); (3) the two causes the first backfill named as left out ('D7 refuted', 'False theory: the pool fix')
are in it; (4) the packet is within packet_budget_tokens, not OVER BUDGET; (5) every open finding, refuted cause and
answer subject is printed in the packet (the never-dropped classes); (6) modledger_backfill_accept.py <Mod> passes;
(7) the judge sample exists (its `samples`): 20 entries, each a ticket-only one in the ledger, with its seed.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import modledger as M                                            # noqa: E402

ROOT = M.REPO_ROOT
SAMPLE = "/mnt/d/ClaudeWork/rimmandrake/conductor/mining_samples/%s_ticket_only.json"
res = []


def check(name, ok, detail=""):
    res.append(ok)
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))


def no_file(iid):
    d = os.path.join(ROOT, "infrastructure", "state", "items")
    return not os.path.exists(os.path.join(d, iid + ".md")) and not os.path.exists(os.path.join(d, "closed",
                                                                                                iid + ".md"))


def items_of(e):
    return [r[5:] for r in e.get("evidence") or [] if isinstance(r, str) and r.startswith("item:")]


mod = (sys.argv[1:] or ["GimmeSomeSlack"])[0]
evs = M.read(ROOT, mod)
bf = [e for e in evs if e.get("writer") == "BACKFILL"]
only = [e for e in bf if any(no_file(i) for i in items_of(e))]
opened = {i for e in only if e.get("kind") == "finding.open" for i in items_of(e) if no_file(i)}
check("%s: tickets with no item file are mined (finding.open)" % mod, len(opened) > 0, len(opened))
refuted = [e for e in only if e.get("kind") == "cause.refuted"]
check("%s: a refuted cause cites a ticket-only item" % mod, len(refuted) > 0, len(refuted))
texts = [json.dumps(e.get("body") or {}, ensure_ascii=False) for e in bf if e.get("kind") == "cause.refuted"]
want = {"D7 refuted": "D7 refuted", "False theory: the pool fix": "the pool fix"}
miss = [k for k, w in want.items() if not any(w.lower() in t.lower() for t in texts)]
check("%s: the causes the first backfill left out are in" % mod, not miss, miss)
text, info = M.packet(ROOT, mod)
check("%s: the packet is within budget" % mod, not info["over_budget"] and info["tokens"] <= info["budget"],
      (info["tokens"], info["budget"]))
st = M.reduce(evs)
must = [k for k, f in st["findings"].items() if f["status"] not in M.CLOSED["finding"]] + \
    [k for k, c in st["causes"].items() if c["status"] == "refuted"] + list(st["answers"])
# a subject leads its line; the line rule may name a finding without its 'finding:' (the packet's header says so)
heads = {l.split()[1].rstrip(":") for l in text.split("\n") if l.startswith("- ") and len(l.split()) > 1}
gone = [k for k in must if k not in heads and k.split(":", 1)[-1] not in heads]
check("%s: every open finding, refuted cause and answer is printed (%d)" % (mod, len(must)), not gone, gone[:5])
r = subprocess.run([sys.executable, os.path.join(HERE, "modledger_backfill_accept.py"), mod], capture_output=True, timeout=600,
                   text=True)
last = (r.stdout.strip().splitlines() or [""])[-1]
check("%s: modledger_backfill_accept.py passes" % mod, r.returncode == 0 and last.startswith("PASS"), last)
try:
    s = json.load(open(SAMPLE % mod, encoding="utf-8"))
except (OSError, ValueError) as x:
    s = {"_err": str(x)}
ents = s.get("samples") or []
ids = {e.get("id") for e in evs}
bad = [e.get("id") for e in ents if not any(no_file(i) for i in items_of(e)) or e.get("id") not in ids]
check("%s: the judge sample holds 20 ticket-only entries and its seed" % mod,
      len(ents) == 20 and not bad and "seed" in s, s.get("_err") or (len(ents), bad[:3]))
print("%s %d/%d" % ("PASS" if all(res) else "FAIL", sum(res), len(res)))
sys.exit(0 if all(res) else 1)
