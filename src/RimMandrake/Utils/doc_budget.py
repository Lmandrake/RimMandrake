#!/usr/bin/env python3
"""doc_budget.py — make documentation bloat VISIBLE, because nobody was measuring it.

The repo grew to 61,523 markdown lines across 284 files — about 1.06M tokens if
read whole, more than a full context window — and added a NET 5,555 lines in one
day. No seat was doing anything wrong by its own rules. Every file was individually
justified. Nothing measured the total, so nothing pushed back.

This does. Run it; it prints what is over budget and exits 1 if anything is.

    python3 src/RimMandrake/Utils/doc_budget.py            # report
    python3 src/RimMandrake/Utils/doc_budget.py --today    # also show today's net growth

BUDGETS are per FILE CLASS, not per file, because the right length depends on
what a document is for:

  infrastructure/state/queue/*.md        150   a queue is a list of open work. If it needs 400 lines,
                          the closed items were never removed.
  queue/BUILD.md    500   the exception, and it is per-file: BUILD's queue carries
                          ~30 items as full spec/verify/criteria contracts, which
                          is content, not accumulation. Per-file entries sit ABOVE
                          their class glob in BUDGETS; first match wins.
  infrastructure/agents/*.md       150   an identity is injected at every session start — but into
                          ONE seat, not five. Was 120 on the stated premise "a tax
                          on all five seats, every time", which is false: that is
                          CLAUDE.md's and agents_def.md's cost, not this file's.
                          Raised 2026-08-14 when each seat gained a skills table,
                          which is per-seat routing and lives nowhere else.
  AGENT_*_state.md  150   a handoff. If a successor must read 900 lines to resume,
                          it is not a handoff, it is an archive.
  CLAUDE.md         300   auto-loaded into EVERY session of every seat. The most
                          expensive lines in the repo.
  traps-*.md        700   append-only by nature; the index is what stays short.
  NEXT_RELOAD.md    400   a queue for ONE event. Accumulation here is the symptom.
  STRUCTURE.md      300   the manifest.
  OWNER_DECISIONS.md 120  what is waiting on the owner. If it grows past this it
                          is not being drained, which is the whole failure it
                          exists to prevent.
  DOC_BUDGET.md     200   ⚠️ THIS FILE'S OWN RULES ARE GOVERNED BY THEM.

Design docs and rosters stay unbudgeted: their length is content, not accumulation.

  infrastructure/output/           none  audits, options papers, one-off analyses. A report's
                          length IS its content, so no per-class budget applies.
                          The patterns above are rooted at the repo top, so a
                          file stops counting against its class once moved here.
  infrastructure/disposing/        none  same, for files on their way out.

⚠️ **The repo-total line globs `**/*.md` recursively, so it counts BOTH.** That is
deliberate for `infrastructure/output/`: those files are live in the tree and any seat may read
them, so their lines are real weight. It is NOT right for `infrastructure/disposing/`, whose
doctrine is "treat as absent" — an open question flagged in `infrastructure/disposing/README.md`
and left alone here rather than changed as a side effect.

⚠️ **A governing file must govern itself.** DOC_BUDGET.md set every budget above
and sat outside all of them until 2026-08-13 — the self-exemption its own "a
written instruction rots" section warns about, in the file carrying the warning.
Keep this table and BUDGETS below in sync; a doc and a tool that disagree are
worse than either alone.
"""
import argparse
import glob
import os
import re
import subprocess
import sys

BUDGETS = [
    # 🔴 First match wins, so per-FILE overrides go above their class glob.
    # queue/BUILD.md holds ~30 items, each a full spec/verify/criteria contract.
    # 150 is a budget for a list of titles, not for executable contracts, and a
    # budget that cannot be met gets ignored rather than obeyed.
    ("infrastructure/state/queue/BUILD.md", 500),
    # 🔴 ARCHIVES AND THE INBOX ARE NOT QUEUE VIEWS — corrected 2026-08-22.
    # These three were charged against the 150 written for a rendered list of titles, so
    # the report showed them 3,600 lines OVER, every run, unfixably. ⛔ That is the exact
    # failure this file's own docstring names: unactionable OVER lines train everyone to
    # ignore the output. Their length is a function of HOW MUCH WORK HAS BEEN DONE and
    # of what the owner has been told — not of rot — and truncating them destroys record.
    # 🔑 The numbers are deliberately loose. They exist to catch a runaway, not to shape
    # the file; when one is hit, ask whether the OLDEST half belongs in git history only.
    ("infrastructure/state/queue/DECIDE_ARCHIVE.md", 2500),
    ("infrastructure/state/queue/CHECK_CLOSED.md", 2500),
    ("infrastructure/state/queue/HUMAN.md", 2000),
    ("infrastructure/state/queue/*.md", 150),
    # ⚠️ POLICY.md is not a per-seat identity, and the 150 was never meant for it. It is
    # the SHARED contract that all four seats load, so its per-line cost is 4x a seat
    # file's — which argues for a tighter budget, not a looser one. What earns 320 is
    # the opposite lever: on 2026-08-20 it shed 74 lines that were verbatim duplication
    # with CLAUDE.md and absorbed the whole rimflow contract, the 90% context ritual and
    # the stop conditions, for a NET +11. Four copies of that text would be ~1,200 lines.
    # 🔑 The real lever here is moving per-seat detail OUT into the four seat files, not
    # compressing prose. A budget that cannot be met gets ignored rather than obeyed.
    ("infrastructure/agents/POLICY.md", 320),
    ("infrastructure/agents/*.md", 150),   # was 120; premise was wrong, see docstring
    ("CLAUDE.md", 300),
    ("infrastructure/state/V1_CHAIN.md", 400),
    ("skills/*/references/traps*.md", 700),
    # ⚠️ The governing files are governed too. DOC_BUDGET.md sets these rules and
    # sat outside them until 2026-08-13 — the self-exemption its own "a written
    # instruction rots" section warns about, inside the file carrying the warning.
    ("infrastructure/DOC_BUDGET.md", 200),
    ("infrastructure/STRUCTURE.md", 300),
    # Waiting on the owner. Growth past 120 means rows are not being drained —
    # the exact rot this file was created to stop.
    ("infrastructure/state/OWNER_DECISIONS.md", 120),
    # NEXT_RELOAD.md is a queue for ONE event. It should be harvested and cleared
    # after each load, so accumulation here is the symptom, not the content.
    ("infrastructure/state/NEXT_RELOAD.md", 400),
    # 🔴 Added 2026-08-20. Until today this file measured NOTHING directly under
    # infrastructure/state/ except the three per-file entries above, so 2,596 lines
    # were invisible to the budget — including the 939-line EXPECTED_FAILURES and the
    # 486-line WORLDGEN_FACTION_CHECKLIST, the two biggest run sheets in the repo.
    # A budget tool with a hand-maintained allowlist measures whatever someone
    # remembered to add, which is not the same as measuring the repo.
    # ⚠️ `state/*.md` does NOT match `state/preserved/*.md`, so 905 lines of rescued
    # briefings were unmeasured entirely — invisible to the very tool that exists to
    # notice accumulation. Archives, so the budget is loose; it exists to catch growth
    # in a directory that should never grow again.
    # ⚠️ EXPECTED_FAILURES is a PER-LOAD LEDGER, not a document. Each load adds a
    # signature block written before it and a Results table filled after; six blocks so
    # far, five closed. Its length tracks LOADS RUN, not rot, and truncating it destroys
    # the baselines later loads are graded against — `score_inhabited_load.py` parses §4
    # directly. Charged at 250 it read +1254 OVER every run, which is the unactionable
    # noise this file's docstring warns trains everyone to ignore the output.
    # 🔑 The real lever is ARCHIVING closed blocks (§1, §3, §6) to observed/, not
    # compressing prose. When this budget is hit, do that rather than cutting.
    ("infrastructure/state/EXPECTED_FAILURES_next_load.md", 1800),
    ("infrastructure/state/preserved/*.md", 1000),
    ("infrastructure/state/*.md", 250),
]

# Append-only work logs. Their length is a function of how much work exists, not of
# rot, so they are reported SEPARATELY — mixing them in made every run show six
# unactionable OVER lines and trained everyone to ignore the output.
QUEUE_CLASSES = ("infrastructure/state/queue/",)

# Lines that record HOW WE LEARNED something rather than WHAT IS TRUE. They earn
# their place in a commit message; in a doc they are the thing that accumulates.
PROVENANCE = re.compile(
    r'2026-\d\d-\d\d|`[0-9a-f]{7,40}`|MEASURED|CORRECTED|RETRACTED|superseded|'
    r'~~|✅ *(DONE|CLOSED)|previously (said|claimed)|used to (say|read)',
    re.I)


def scan():
    rows, over, seen = [], 0, set()
    for pattern, budget in BUDGETS:
        for path in sorted(glob.glob(pattern)):
            if path in seen:      # first match wins: a per-file entry beats its class glob
                continue
            seen.add(path)
            with open(path, encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
            n = len(lines)
            prov = sum(1 for l in lines if PROVENANCE.search(l))
            rows.append((path, n, budget, prov))
            if n > budget:
                over += 1
    return rows, over


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", action="store_true", help="also show net growth today")
    args = ap.parse_args()

    rows, over = scan()

    def show(title, subset):
        if not subset:
            return
        print(f"\n{title}")
        print(f"{'file':<44}{'lines':>7}{'budget':>8}{'prov/100':>10}  status")
        for path, n, budget, prov in subset:
            density = 100 * prov / n if n else 0
            flag = "OVER" if n > budget else "ok"
            bar = f"+{n - budget}" if n > budget else ""
            print(f"{path:<44}{n:>7}{budget:>8}{density:>9.1f}  {flag} {bar}")

    docs = [r for r in rows if not r[0].startswith(QUEUE_CLASSES)]
    queues = [r for r in rows if r[0].startswith(QUEUE_CLASSES)]
    show("DOCS — an OVER here is rot, and actionable", docs)
    show("QUEUES — append-only; length tracks open work, not rot", queues)
    print(f"\nactionable overruns: {sum(1 for p, n, b, _ in docs if n > b)}"
          f"  (queues over: {sum(1 for p, n, b, _ in queues if n > b)}, not counted)")

    md = glob.glob("**/*.md", recursive=True)
    # ⚠️ disposing/ is quarantine — nothing there may be cited, so counting it in the
    # repo total made the corpus look bigger than the corpus a seat can actually read.
    md = [p for p in md
          if ".git" not in p
          and not p.startswith(("infrastructure/disposing/", "vendor/", "research/"))]
    total = sum(sum(1 for _ in open(p, encoding="utf-8", errors="replace"))
                for p in md)
    print(f"\nrepo total: {len(md)} markdown files, {total:,} lines "
          f"(~{total * 11 // 1000}k tokens if read whole)")

    if args.today:
        try:
            out = subprocess.run(
                ["git", "log", "--since=midnight", "--numstat", "--format=", "--", "*.md"],
                capture_output=True, text=True, timeout=30).stdout
            add = sub = 0
            for line in out.splitlines():
                parts = line.split("\t")
                if len(parts) == 3 and parts[0].isdigit():
                    add += int(parts[0]); sub += int(parts[1])
            print(f"today: +{add:,} / -{sub:,} = net {add - sub:+,} lines")
        except Exception:
            pass

    doc_over = sum(1 for p_, n, b, _ in docs if n > b)
    if doc_over:
        print(f"\n{doc_over} DOC(s) over budget. Delete the body of anything closed; "
              f"provenance belongs in the commit message.")
        return 1
    # 🔑 A queue over budget is not a failure and must not fail the exit code — that
    # is what trained everyone to ignore this tool. It is reported, never enforced.
    return 0


if __name__ == "__main__":
    sys.exit(main())
