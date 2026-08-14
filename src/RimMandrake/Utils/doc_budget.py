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
  infrastructure/agents/*.md       120   an identity is read every session. Every line is a tax
                          on all five seats, every time.
  AGENT_*_state.md  150   a handoff. If a successor must read 900 lines to resume,
                          it is not a handoff, it is an archive.
  CLAUDE.md         300   auto-loaded into EVERY session of every seat. The most
                          expensive lines in the repo.
  agents_def.md     200   shared rules.
  traps-*.md        700   append-only by nature; the index is what stays short.
  NEXT_RELOAD.md    400   a queue for ONE event. Accumulation here is the symptom.
  CLOSED.md         150   one line per item.
  STRUCTURE.md      300   the manifest.
  V1_SCOPE.md       300   the scope line and the burn-down.
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
    ("infrastructure/state/queue/*.md", 150),
    ("infrastructure/agents/*.md", 120),
    ("infrastructure/state/AGENT_*_state.md", 150),
    ("CLAUDE.md", 300),
    ("infrastructure/agents_def.md", 200),          # was 500; dissolved to 158, budget dropped
    ("skills/*/references/traps*.md", 700),
    # ⚠️ The governing files are governed too. DOC_BUDGET.md sets these rules and
    # sat outside them until 2026-08-13 — the self-exemption its own "a written
    # instruction rots" section warns about, inside the file carrying the warning.
    ("infrastructure/DOC_BUDGET.md", 200),
    ("infrastructure/STRUCTURE.md", 300),
    ("infrastructure/state/V1_SCOPE.md", 300),
    # Waiting on the owner. Growth past 120 means rows are not being cleared into
    # CLOSED.md — the exact rot this file was created to stop.
    ("infrastructure/state/OWNER_DECISIONS.md", 120),
    ("infrastructure/state/CLOSED.md", 150),              # one line per item; archive the oldest if it fills
    # NEXT_RELOAD.md is a queue for ONE event. It should be harvested and cleared
    # after each load, so accumulation here is the symptom, not the content.
    ("infrastructure/state/NEXT_RELOAD.md", 400),
    # 🔴 The two biggest state files matched NO glob until 2026-08-13 and were
    # therefore never measured: TODO.md (965) and TODO_v2.md (1,168) — 3,078
    # unmeasured lines, MORE than the entire measured excess across every other
    # file combined. A budget tool that silently omits its largest subject is
    # reporting on the wrong tier; found by a doc-budget sweep, not by the tool.
    # Budgets are deliberately generous: these are being retired, not trimmed,
    # and a budget that fails on day one gets ignored rather than obeyed.
    ("infrastructure/state/TODO.md", 400),
    ("infrastructure/state/TODO_v2.md", 600),
]

# Lines that record HOW WE LEARNED something rather than WHAT IS TRUE. They earn
# their place in a commit message; in a doc they are the thing that accumulates.
PROVENANCE = re.compile(
    r'2026-\d\d-\d\d|`[0-9a-f]{7,40}`|MEASURED|CORRECTED|RETRACTED|superseded|'
    r'~~|✅ *(DONE|CLOSED)|previously (said|claimed)|used to (say|read)',
    re.I)


def scan():
    rows, over = [], 0
    for pattern, budget in BUDGETS:
        for path in sorted(glob.glob(pattern)):
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
    print(f"{'file':<34}{'lines':>7}{'budget':>8}{'prov/100':>10}  status")
    for path, n, budget, prov in rows:
        density = 100 * prov / n if n else 0
        flag = "OVER" if n > budget else "ok"
        bar = f"+{n - budget}" if n > budget else ""
        print(f"{path:<34}{n:>7}{budget:>8}{density:>9.1f}  {flag} {bar}")

    md = glob.glob("**/*.md", recursive=True)
    md = [p for p in md if ".git" not in p]
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

    if over:
        print(f"\n{over} file(s) over budget. Closed items belong in CLOSED.md as "
              f"ONE LINE each; provenance belongs in the commit message.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
