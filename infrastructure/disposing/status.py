#!/usr/bin/env python3
"""status.py — one command for "what is the state of this project".

The owner was reconstructing that from five queue files, a burn-down table and
whatever an agent said last. This reads the same sources and prints the answer.

    python3 src/RimMandrake/Utils/status.py            # the whole picture
    python3 src/RimMandrake/Utils/status.py --seat OPS # one seat, expanded
    python3 src/RimMandrake/Utils/status.py --brief    # the top block only

Sources, all parsed and none hardcoded:

  V1_SCOPE.md       the burn-down table, located and read BY ITS HEADERS
  infrastructure/state/queue/<SEAT>.md   ### headings = items; ✅/CLOSED/DONE/~~ = closed
  OWNER_DECISIONS.md if present; else the queues' owner sections
  NEXT_RELOAD.md    open ## sections = things waiting on a game load
  src/RimMandrake/Utils/doc_budget.py  count over budget, never the whole table
  git log --since=midnight

⚠️ A confidently wrong status is worse than an obviously incomplete one. Any
source that is missing or unparseable prints `?` and a note naming the file.
Never substitute a guess for a number.
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent

# A heading is closed if it carries one of these. Same vocabulary the queues use.
CLOSED = re.compile(r'✅|~~|\bCLOSED\b|\bDONE\b')
# Items the owner must rule on. Section headers and item headings both.
OWNER = re.compile(r'NEEDS YOU|needs? (an |the )?owner|owner decision|'
                   r"owner'?s call", re.I)
# ⭐ or a bare v1 mention, but [v2] wins — a v2 tag is never a v1 row.
V1 = re.compile(r'⭐|\bv1\b', re.I)
V2 = re.compile(r'\[v2\]', re.I)

NOTES = []          # one line per unreadable source; printed under the report
SEAT_ALIAS = {"WORLD": "OPS"}   # renamed 2026-08-13; the burn-down still says WORLD


def read(rel):
    """Text, or None plus a note. Never raises — this tool always exits 0."""
    p = ROOT / rel
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        NOTES.append(f"unreadable: {rel}")
        return None


def trunc(s, n):
    s = re.sub(r'[*`]', '', s).strip()      # keep _ — it is in every defName
    return s if len(s) <= n else s[:n - 1] + "…"


# ---------------------------------------------------------------- queues

def parse_queue(seat):
    """-> dict(open=[titles], v1=[titles], owner=[titles]) or None."""
    text = read(f"infrastructure/state/queue/{seat}.md")
    if text is None:
        return None
    sec = ""
    out = {"open": [], "v1": [], "owner": []}
    for line in text.splitlines():
        if line.startswith("## ") and not line.startswith("###"):
            sec = line[3:]
            continue
        if line.startswith("### "):
            head = line[4:]
            if CLOSED.search(head) or CLOSED.search(sec) or \
                    re.match(r'\s*closed\b', sec, re.I):
                continue
            out["open"].append(head)
            if V1.search(head) and not V2.search(head):
                out["v1"].append(head)
            if OWNER.search(head) or OWNER.search(sec):
                out["owner"].append(head)
            continue
        # Owner sections sometimes hold a numbered list instead of ### items.
        if OWNER.search(sec) and re.match(r'\d+\.\s+\S', line):
            out["owner"].append(re.sub(r'^\d+\.\s+', '', line))
    return out


def parse_owner_file(text):
    """OWNER_DECISIONS.md holds a table under `## Open`, one row per ask.

    Rows come from the column whose header names the ask; ### headings count
    too, in case the file's shape changes under us. Sections outside `Open`
    (the rule, the checked-and-not-listed list) are skipped.
    """
    items, sec, hdr, ask = [], "", None, None
    for line in text.splitlines():
        if line.startswith("## ") and not line.startswith("###"):
            sec, hdr = line[3:], None
            continue
        if not re.search(r'\bopen\b', sec, re.I):
            continue
        if line.startswith("### ") and not CLOSED.search(line):
            items.append(line[4:])
        elif line.startswith("|"):
            c = cells(line)
            if set("".join(c)) <= set("-: "):
                continue
            if hdr is None:                      # first row of a table = header
                hdr = [re.sub(r'[*`]', '', x).lower() for x in c]
                ask = find_col(hdr, "ask", "decision", "question") or \
                    (1 if len(hdr) > 1 else 0)
                continue
            if ask < len(c) and c[ask] and not CLOSED.search(c[ask]):
                items.append(c[ask])
    return items


def owner_items(queues):
    """OWNER_DECISIONS.md if it exists; else the queues' owner sections."""
    if (ROOT / "infrastructure/state/OWNER_DECISIONS.md").exists():
        text = read("infrastructure/state/OWNER_DECISIONS.md")
        if text is not None:
            items = parse_owner_file(text)
            if not items:
                NOTES.append("OWNER_DECISIONS.md: no open rows parsed")
            return items, "infrastructure/state/OWNER_DECISIONS.md"
    items = []
    for seat, q in queues.items():
        if q:
            items += [f"{seat}: {t}" for t in q["owner"]]
    return items, "queues"


# ---------------------------------------------------------------- v1 table

def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def find_col(hdr, *words):
    for i, h in enumerate(hdr):
        if any(w in h for w in words):
            return i
    return None


def parse_v1():
    """The burn-down, located by its headers so a new column cannot shift it."""
    text = read("infrastructure/state/V1_SCOPE.md")
    if text is None:
        return None
    lines = text.splitlines()
    start = None
    for i, l in enumerate(lines):
        if l.startswith("|") and "verified" in l.lower() and "built" in l.lower():
            start = i
            break
    if start is None:
        NOTES.append("no burn-down table found in V1_SCOPE.md")
        return None
    hdr = [re.sub(r'[*`]', '', c).lower() for c in cells(lines[start])]
    ci = {k: find_col(hdr, *w) for k, w in {
        "row": ("v1 row", "row"), "built": ("built",), "ver": ("verified",),
        "owner": ("owner",), "load": ("load",), "off": ("offline",)}.items()}
    rows = []
    for l in lines[start + 1:]:
        if not l.startswith("|"):
            break
        c = cells(l)
        if set("".join(c)) <= set("-: "):
            continue
        def get(k):
            i = ci[k]
            return c[i] if i is not None and i < len(c) else None
        rows.append({k: get(k) for k in ci})
    return rows or None


def is_verified(row):
    return bool(row["ver"] and re.search(r'🟩|✅', row["ver"]))


def needs_load(row):
    """Prefer an explicit 'needs a load' column; fall back to 'offline?'.

    The load column is glyph-led: 🟢/no = closable offline, 🔴/⚠️ = wants the
    game, ✅ = the load already happened. Negatives are tested first because
    "🟢 NO — closable offline" also contains words a positive test would catch.
    """
    v = row.get("load")
    if v:
        if re.search(r'🟢|⬜|\bno\b|offline', v, re.I):
            return False
        if re.search(r'🔴|⚠️|\byes\b|load|game|live', v, re.I):
            return True
        if "✅" in v:
            return False                      # already spent
    off = row.get("off")
    if off is not None:
        return "✅" not in off
    return None            # unknown -> counted nowhere, reported as ?


def v1_stats(rows):
    if not rows:
        return dict(n="?", ver="?", off="?", load="?")
    ver = sum(1 for r in rows if is_verified(r))
    todo = [r for r in rows if not is_verified(r)]
    load = [r for r in todo if needs_load(r) is True]
    off = [r for r in todo if needs_load(r) is False]
    unk = len(todo) - len(load) - len(off)
    if unk:
        NOTES.append(f"V1_SCOPE.md: {unk} row(s) with no load/offline marker")
    return dict(n=len(rows), ver=ver, off=len(off), load=len(load))


def v1_by_seat(rows, seat):
    if not rows:
        return None
    out = []
    for r in rows:
        o = (r["owner"] or "").strip("*` ").upper()
        if SEAT_ALIAS.get(o, o) == seat:
            out.append(r)
    return out


# ---------------------------------------------------------------- misc

def next_reload_open():
    text = read("infrastructure/state/NEXT_RELOAD.md")
    if text is None:
        return "?"
    return sum(1 for l in text.splitlines()
               if l.startswith("## ") and not CLOSED.search(l))


_BUDGET = None


def budget():
    """(count over, {path: overage}). doc_budget globs relative to the root.

    Cached: the report asks for it once per seat and scan() re-reads the repo.
    """
    global _BUDGET
    if _BUDGET is not None:
        return _BUDGET
    try:
        sys.path.insert(0, str(ROOT / "src" / "RimMandrake" / "Utils"))
        import doc_budget
        cwd = os.getcwd()
        os.chdir(ROOT)
        try:
            rows, over = doc_budget.scan()
        finally:
            os.chdir(cwd)
        _BUDGET = (over, {p: n - b for p, n, b, _ in rows if n > b})
    except Exception as e:
        NOTES.append(f"doc_budget.py failed: {type(e).__name__}")
        _BUDGET = ("?", {})
    return _BUDGET


def commits_today():
    try:
        out = subprocess.run(["git", "log", "--since=midnight", "--oneline"],
                             cwd=ROOT, capture_output=True, text=True,
                             timeout=15)
        if out.returncode:
            raise RuntimeError
        return len([l for l in out.stdout.splitlines() if l.strip()])
    except Exception:
        NOTES.append("git log failed")
        return "?"


# ---------------------------------------------------------------- report

def seats():
    d = sorted(p.stem for p in (ROOT / "infrastructure" / "state" / "queue").glob("*.md")) \
        if (ROOT / "infrastructure" / "state" / "queue").is_dir() else []
    if not d:
        NOTES.append("no infrastructure/state/queue/*.md found")
    return d


def top_block(queues, rows, owners, src):
    st = v1_stats(rows)
    print(f"◆ PROJECT STATUS · {commits_today()} commits today")
    first = trunc(owners[0], 40) if owners else "—"
    # A present-but-unparsed decisions file must not report a confident 0.
    n = len(owners) if owners or src == "queues" else "?"
    print(f"🟡 NEEDS OWNER  {n:>3} open  →  {first}")
    print(f"⭐ v1           {st['ver']}/{st['n']} verified · "
          f"{st['off']} closable offline · {st['load']} need a load")
    over, _ = budget()
    print(f"🔴 blocked      {next_reload_open():>3} on a game load"
          f"  ·  {over} docs over budget")


def seat_line(seat, q, rows):
    if q is None:
        return f"  {seat:<8} {'?':>3} open   infrastructure/state/queue/{seat}.md unreadable"
    v1 = v1_by_seat(rows, seat)
    if v1 is None:
        v1s = "v1 ?"
    else:
        v1s = f"v1 {sum(1 for r in v1 if is_verified(r))}/{len(v1)}" if v1 \
            else "v1 —"
    _, overs = budget()
    ov = overs.get(f"infrastructure/state/queue/{seat}.md")
    return (f"  {seat:<8} {len(q['open']):>3} open   {v1s:<10}"
            f"{'queue OVER +%d' % ov if ov else 'queue ok'}")


def main():
    ap = argparse.ArgumentParser(description="project state in one screen")
    ap.add_argument("--seat", help="one seat only, expanded")
    ap.add_argument("--brief", action="store_true", help="top block only")
    args = ap.parse_args()

    names = seats()
    rows = parse_v1()

    if args.seat:
        seat = args.seat.upper()
        seat = SEAT_ALIAS.get(seat, seat)
        if names and seat not in names:
            print(f"◆ {seat} · no infrastructure/state/queue/{seat}.md · seats: {' '.join(names)}")
            return 0
        q = parse_queue(seat)
        print(f"◆ {seat} · {len(q['open']) if q else '?'} open items")
        for t in (q["owner"] if q else [])[:3]:
            print(f"🟡 {trunc(t, 66)}")
        shown = set(q["owner"] if q else [])
        for t in [t for t in (q["v1"] if q else []) if t not in shown][:3]:
            print(f"⭐ {trunc(t, 66)}")
        for r in (v1_by_seat(rows, seat) or []):
            mark = "🟩" if is_verified(r) else "⬜"
            print(f"{mark} v1 row {trunc(r['row'] or '?', 45)}")
        rest = [t for t in (q["open"] if q else [])
                if t not in q["owner"] and t not in q["v1"]]
        for t in rest[:8]:
            print(f"·  {trunc(t, 66)}")
        if len(rest) > 8:
            print(f"·  … {len(rest) - 8} more")
        _, overs = budget()
        ov = overs.get(f"infrastructure/state/queue/{seat}.md")
        if ov:
            print(f"📏 infrastructure/state/queue/{seat}.md is {ov} lines over budget")
        for n in NOTES:
            print(f"⚠️ {n}")
        return 0

    queues = {s: parse_queue(s) for s in names}
    owners, src = owner_items(queues)
    top_block(queues, rows, owners, src)
    if args.brief:
        for n in NOTES[:2]:
            print(f"⚠️ {n}")
        return 0

    print()
    for s in names:
        print(seat_line(s, queues[s], rows))
    if rows:
        todo = [r for r in rows if not is_verified(r)]
        if todo:
            print()
            print("⭐ next v1 rows, unverified:")
            for r in todo[:3]:
                tag = "load" if needs_load(r) is True else "offline"
                print(f"   {trunc(r['row'] or '?', 46):<47}{tag}")
    for n in NOTES:
        print(f"⚠️ {n}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:          # informational tool: never fail the caller
        print(f"⚠️ status.py: {type(e).__name__}: {e}")
        sys.exit(0)
