#!/usr/bin/env python3
"""selftest_artist_role.py - The Artist is registered off, never launches by itself, and its memory cannot drift from the ledger:
every `> CL-nnn:` line in art_style_memory.md is his words verbatim, every CL id it cites exists. Reads only real repo files."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ROLE = os.path.join(HERE, "roles", "artist.md")
MEMORY = os.path.join(ROOT, "design", "RimMandrake", "art_style_memory.md")
LEDGER = os.path.join(ROOT, "infrastructure", "state", "art_eval", "criteria_ledger.jsonl")
SCHEDULE = os.path.join(HERE, "dispatcher_schedule.json")
SKILL = os.path.join(ROOT, ".claude", "skills", "rimworld-art-evaluation", "SKILL.md")

FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def quotes(text):
    """(id, words) of every verbatim line: `> CL-nnn: "words"`."""
    return re.findall(r'^> (CL-\d+): "(.*)"\s*$', text, re.M)


def main():
    sched = json.loads(read(SCHEDULE))
    rows = [r for r in sched["roles"] if r["name"] == "Artist"]
    check("one Artist row", len(rows) == 1, len(rows))
    row = rows[0]
    golive = (sched.get("golive") or {}).get("roles", [])
    check("off, or flipped the way a flip is done", row.get("enabled") is False or "Artist" in golive, row.get("enabled"))
    check("no slot starts it", not row.get("slots") and not row.get("slot_when") and not row.get("runs_local"), row)
    check("instructions point at the role file", row.get("instructions") == "src/RimMandrake/rimflow/roles/artist.md", row.get("instructions"))
    role = read(ROLE)
    check("the role reports to the Conductor", "report to the **Conductor**" in role)
    check("the role never approaches him", "never approach the owner" in role)
    check("the role names its memory", "design/RimMandrake/art_style_memory.md" in role)
    check("the skill points at the role", "roles/artist.md" in read(SKILL))

    ledger = [json.loads(l) for l in read(LEDGER).splitlines() if l.strip()]
    ids = {r["id"] for r in ledger}
    memory = read(MEMORY)
    cited = set(re.findall(r"CL-\d{3}", memory))
    check("memory cites ledger entries", len(cited) >= 10, len(cited))    # an empty scan proves nothing
    check("every cited id exists", cited <= ids, sorted(cited - ids))
    said = quotes(memory)
    check("memory quotes him", len(said) >= 5, len(said))                 # likewise
    words = {r["id"]: (r.get("owner_said") or "") + " " + (r.get("missed") or "") for r in ledger if r.get("event") == "add"}
    bad = [i for i, q in said if q not in words.get(i, "")]
    check("every quote is verbatim", not bad, bad)
    check("the instrument sees a bent quote", "NOT a star trek creature" not in words["CL-019"]
          and quotes('> CL-019: "x"\n') == [("CL-019", "x")])
    last = re.search(r"\*\*Studied through:\*\* (CL-\d+)", memory)
    check("memory says how far it has studied", bool(last) and last.group(1) in ids, last)

    print("selftest_artist_role: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
