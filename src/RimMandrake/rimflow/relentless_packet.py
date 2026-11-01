#!/usr/bin/env python3
"""The packet: what a Marker is told about a candidate, with no room for advocacy. RA_S02_PACKET_ENFORCE_NO_ADVOCACY.

Design section 8 of design/RimMandrake/relentless_agent_design_2026-11-01.md. JSON with no free field. The supervisor
fills goal, proof, range and oracle_diff; Build authors only exists, how_to_check and unverified. Lint is schema, then a
forbidden-word list, both free of AI. REPORT-ONLY for now: the supervisor journals what lint says and changes nothing.

    relentless_packet.py scan [--out rows.json]     lint every real finish receipt's evidence, as an `unverified` clause
"""
import argparse
import glob
import json
import os
import re
import sys

SUPERVISOR = ("goal", "proof", "range", "oracle_diff")
BUILDER = ("exists", "how_to_check", "unverified")
FIELDS = SUPERVISOR + BUILDER
CLAUSE_MAX = 200
HOW_KEYS = {"command", "expected"}
# History says how it went; advocacy says how to read it. A Marker needs neither. Whole words, on Build's text only.
HISTORY = ("previously", "earlier", "prior", "before this", "last attempt", "last time", "first attempt", "second attempt",
           "this attempt", "retried", "reworked", "redesign", "redesigned", "blind check", "the checker",
           "the marker", "the last worker", "previous worker", "gen \\d+", "was rejected", "was failing", "this time",
           "now passes", "now green")
ADVOCACY = ("because", "clearly", "obviously", "plainly", "correctly", "properly", "robust", "robustly", "thorough",
            "thoroughly", "carefully", "fully", "trivially", "guaranteed", "bulletproof", "no issues", "no problems",
            "as requested", "as asked", "should pass", "safe to", "trust", "rest assured", "honest", "honestly",
            "genuinely", "definitely", "certainly", "really")
WORD_RX = re.compile(r"\b(%s)\b" % "|".join(HISTORY + ADVOCACY), re.I)


def build(st, rec, goal, range_, oracle_diff, authored=None):
    """The packet of a candidate. Only the three authored fields can come from Build; anything else it sent is dropped
    here, and lint() would refuse it anyway."""
    a = authored or {}
    return {"goal": goal, "proof": st["contract"]["proof"], "range": range_, "oracle_diff": oracle_diff,
            "exists": a.get("exists", []), "how_to_check": a.get("how_to_check", []), "unverified": a.get("unverified", [])}


def words(text):
    """The forbidden words in a string, lowercase, in order. Backticked code and paths are the tree's words, not Build's."""
    bare = re.sub(r"`[^`]*`", " ", text or "")
    return [m.group(1).lower() for m in WORD_RX.finditer(bare)]


def _strings(p):
    for x in p.get("exists") or []:
        yield "exists", x
    for x in p.get("unverified") or []:
        yield "unverified", x


def lint(p, st=None):
    """-> reasons, empty when the packet may go to a Marker. `st`: refuse a proof that is not the contract's."""
    if not isinstance(p, dict):
        return ["schema: a packet is an object"]
    out = ["schema: free field %s" % k for k in sorted(set(p) - set(FIELDS))]
    out += ["schema: no %s" % k for k in FIELDS if k not in p]
    if st is not None and p.get("proof") != (st.get("contract") or {}).get("proof"):
        out.append("schema: proof differs from the contract")
    for k in ("exists", "unverified"):
        if k in p and (not isinstance(p[k], list) or not all(isinstance(x, str) for x in p[k])):
            out.append("schema: %s is a flat list of strings" % k)
    how = p.get("how_to_check")
    if "how_to_check" in p:
        if not isinstance(how, list) or not how:
            out.append("schema: how_to_check is a non-empty list")
            how = []
        for i, h in enumerate(how):
            if not isinstance(h, dict) or set(h) != HOW_KEYS or not all(isinstance(v, str) and v.strip() for v in h.values()):
                out.append("schema: how_to_check %d is a command and an expected output, nothing else" % i)
    if any(o.startswith("schema") for o in out):      # order: the word list reads only a packet of the right shape
        return out
    for k, x in _strings(p):
        if k == "unverified" and len(x) > CLAUSE_MAX:
            out.append("unverified: over %d characters: %s" % (CLAUSE_MAX, x[:60]))
        for w in words(x):
            out.append("word: %s in %s: %s" % (w, k, x[:80]))
    for h in how:
        for w in words(h["expected"]):
            out.append("word: %s in how_to_check: %s" % (w, h["expected"][:80]))
    return out


def report(rec):
    """Report-only reading of a receipt: its evidence prose is the free text a packet will end, so read it as a clause."""
    return sorted(set(words(rec.get("evidence") or "")))


def receipts(root):
    for path in sorted(glob.glob(os.path.join(root, "store", "items", "*", "receipts", "*"))):
        try:
            with open(path, encoding="utf-8") as f:
                yield path, json.load(f)
        except (OSError, ValueError):
            continue


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("verb", choices=["scan"])
    p.add_argument("--root", default=os.environ.get("RELENTLESS_ROOT") or "/home/mandrake/rm/relentless")
    p.add_argument("--out")
    a = p.parse_args(argv)
    rows = [{"item": rec.get("item"), "gen": rec.get("gen"), "hits": report(rec), "evidence": rec.get("evidence") or ""}
            for _, rec in receipts(a.root)]
    hit = [r for r in rows if r["hits"]]
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=1)
    print("%d receipts, %d with forbidden words" % (len(rows), len(hit)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
