#!/usr/bin/env python3
"""lessons.py — the lessons inbox, one file per lesson (git plan Phase 5, 2026-10-02).

    python3 src/RimMandrake/Utils/lessons.py add "<the lesson, one paragraph>" [--seat BENCH] [--slug words] [--home <skill|doc path|NONE>]
    python3 src/RimMandrake/Utils/lessons.py render          # -> infrastructure/state/LESSONS_INBOX.md (gitignored view)
    python3 src/RimMandrake/Utils/lessons.py list            # count + newest paths
    python3 src/RimMandrake/Utils/lessons.py stats           # counts by seat/age/home; oldest undrained

Each lesson is `infrastructure/state/lessons/<utc>-<seat>-<slug>.md`, holding the
lesson text only. Filing is CREATING a file, so two windows filing at once never
touch the same path and never conflict; curation (folding a lesson into its
owning skill) is DELETING the file — which a one-file inbox under `merge=union`
would have silently resurrected (git plan §2.5).

`infrastructure/state/lessons/README.md` is the inbox's standing header, not a
lesson. `LESSONS_INBOX.md` is a gitignored rendered view (listed in .gitignore, not
tracked): rebuilt by `render` on demand; never edit it — an edit there is lost on
the next render. A lesson's last line may be `home: <skill|doc path|NONE>`, its
proposed durable home.
"""
import argparse
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("LESSONS_ROOT") or os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DIR = os.path.join(ROOT, "infrastructure", "state", "lessons")
VIEW = os.path.join(ROOT, "infrastructure", "state", "LESSONS_INBOX.md")
README = "README.md"


def seat_of(explicit=None):
    for v in (explicit, os.environ.get("RIMFLOW_SEAT"), os.environ.get("AGENT_SEAT")):
        if v and re.fullmatch(r"[A-Za-z0-9_]+", v.strip()):
            return v.strip().upper()
    return "UNSEATED"


def slugify(text, n=6):
    words = re.findall(r"[a-z0-9]+", text.lower())
    words = [w for w in words if w not in ("the", "a", "an", "and", "of", "to", "is", "in", "on")]
    return "-".join(words[:n]) or "lesson"


def lesson_files():
    try:
        names = sorted(n for n in os.listdir(DIR) if n.endswith(".md") and n != README)
    except FileNotFoundError:
        return []
    return [os.path.join(DIR, n) for n in names]


STOP = set("the a an and of to is in on for it be as at by or this that with are was not but from if so do "
           "we you use used when then than its into only any all can has have".split())


def content_words(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2 and w not in STOP}


def similar(text, limit=3, threshold=0.35):
    """Up to `limit` (score, path, first line) of existing lessons most like `text` (Jaccard on first line)."""
    mine = content_words(text.splitlines()[0] if text.strip() else "")
    out = []
    if not mine:
        return out
    for fp in lesson_files():
        try:
            with open(fp, encoding="utf-8") as f:
                first = f.readline().strip()
        except OSError:
            continue
        theirs = content_words(first)
        if not theirs:
            continue
        score = len(mine & theirs) / len(mine | theirs)
        if score >= threshold:
            out.append((score, fp, first))
    out.sort(key=lambda t: -t[0])
    return out[:limit]


def parse_name(path):
    """(utc epoch, seat) from `<utc>-<SEAT>-<slug>.md`; (None, None) if unparseable."""
    m = re.match(r"(\d{8}T\d{6})Z-([A-Za-z0-9_]+?)-", os.path.basename(path))
    if not m:
        return None, None
    import calendar
    return calendar.timegm(time.strptime(m.group(1), "%Y%m%dT%H%M%S")), m.group(2)


def home_of(path):
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().strip().splitlines()
    except OSError:
        return None
    if lines and lines[-1].startswith("home:"):
        return lines[-1][5:].strip() or None
    return None


def stats(now=None):
    now = now or time.time()
    files = lesson_files()
    seats, buckets, homes = {}, {"<7d": 0, "7-14d": 0, "14-30d": 0, ">30d": 0, "unparsed": 0}, {}
    with_home = 0
    oldest = None
    for fp in files:
        t, seat = parse_name(fp)
        if t is None:
            buckets["unparsed"] += 1
        else:
            seats[seat] = seats.get(seat, 0) + 1
            age = (now - t) / 86400.0
            k = "<7d" if age < 7 else "7-14d" if age < 14 else "14-30d" if age < 30 else ">30d"
            buckets[k] += 1
            if oldest is None or age > oldest[0]:
                oldest = (age, os.path.basename(fp))
        h = home_of(fp)
        if h:
            with_home += 1
            homes[h] = homes.get(h, 0) + 1
    return {"total": len(files), "seats": seats, "buckets": buckets, "with_home": with_home,
            "without_home": len(files) - with_home, "homes": homes, "oldest": oldest}


def print_stats(st):
    if st["oldest"]:
        print("oldest undrained: %d days (%s)" % (int(st["oldest"][0]), st["oldest"][1]))
    else:
        print("oldest undrained: none")
    print("total: %d" % st["total"])
    print("by seat: " + (", ".join("%s=%d" % kv for kv in sorted(st["seats"].items())) or "-"))
    print("by age: " + ", ".join("%s=%d" % kv for kv in st["buckets"].items()))
    print("with home: %d, without home: %d" % (st["with_home"], st["without_home"]))
    if st["homes"]:
        print("by home: " + ", ".join("%s=%d" % kv for kv in sorted(st["homes"].items())))


def add(text, seat=None, slug=None, utc=None, home=None):
    text = text.strip()
    if not text:
        sys.exit("FAIL: empty lesson.")
    if not home:
        print("WARN: no --home given: say which skill/doc should own this lesson, or --home NONE",
              file=sys.stderr)
    dups = similar(text)
    if dups:
        print("possible duplicates:")
        for score, fp, first in dups:
            print("  %.2f %s  %s" % (score, os.path.relpath(fp, ROOT), first[:100]))
    os.makedirs(DIR, exist_ok=True)
    utc = utc or time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    base = "%s-%s-%s" % (utc, seat_of(seat), slugify(slug or text))
    path = os.path.join(DIR, base + ".md")
    i = 2
    while os.path.exists(path):
        path = os.path.join(DIR, "%s-%d.md" % (base, i))
        i += 1
    # O_EXCL: never overwrite another window's lesson.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text + "\n")
        if home:
            f.write("home: %s\n" % home.strip())
    return path


def render():
    parts = []
    try:
        with open(os.path.join(DIR, README), encoding="utf-8") as f:
            parts.append(f.read().rstrip() + "\n")
    except FileNotFoundError:
        parts.append("# Lessons inbox\n")
    parts.append("\n<!-- GENERATED by src/RimMandrake/Utils/lessons.py render — do not edit; "
                 "file a lesson with `lessons.py add`. -->\n\n")
    files = lesson_files()
    for fp in files:
        with open(fp, encoding="utf-8") as f:
            body = f.read().strip()
        first, *rest = body.splitlines() or [""]
        parts.append("- " + first + "\n")
        for line in rest:
            parts.append("  " + line + "\n" if line.strip() else "\n")
        parts.append("  <sub>`%s`</sub>\n" % os.path.relpath(fp, ROOT))
    tmp = VIEW + ".tmp.%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("".join(parts))
    os.replace(tmp, VIEW)
    return VIEW, len(files)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add", help="file one lesson as its own file")
    a.add_argument("text")
    a.add_argument("--seat")
    a.add_argument("--slug", help="a few words for the filename (default: from the text)")
    a.add_argument("--home", help="proposed durable home: a skill, a doc path, or NONE")
    sub.add_parser("render", help="rebuild the gitignored (untracked) LESSONS_INBOX.md view")
    sub.add_parser("stats", help="counts by seat, age, home; oldest undrained lesson")
    sub.add_parser("list", help="count lessons and show the newest")
    args = ap.parse_args()
    if args.cmd == "add":
        p = add(args.text, args.seat, args.slug, home=args.home)
        print(os.path.relpath(p, ROOT))
        print("commit it: git commit %s -m 'lesson: …'" % os.path.relpath(p, ROOT))
    elif args.cmd == "render":
        p, n = render()
        print("%s  (%d lessons)" % (p, n))
    elif args.cmd == "stats":
        print_stats(stats())
    elif args.cmd == "list":
        fs = lesson_files()
        print("%d lessons in %s" % (len(fs), os.path.relpath(DIR, ROOT)))
        for fp in fs[-10:]:
            print("  " + os.path.relpath(fp, ROOT))


if __name__ == "__main__":
    main()
