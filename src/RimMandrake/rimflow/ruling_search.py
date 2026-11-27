#!/usr/bin/env python3
"""ruling_search.py - search the rule trees for lines that may say the opposite of a new owner ruling.

Item RIMMANDRAKE_BUILD_RULING_SEARCH_540_GREPS_FOR_OPPOSITES (script candidate 3 of
design/specs/2026-11-26-script-candidates/one_page.md); page design/specs/2026-11-27-ruling-search/boundary.md;
selftest selftest_ruling_search.py. It sits beside ruling_fast.py (which records his words and places the rule).

    python3 src/RimMandrake/rimflow/ruling_search.py "<his words>" [--root DIR] [--top N | --all] [--min-terms K]

It takes the content words of his words (stop words and words under 4 letters dropped; a simple stem, so "holds" and
"hold" meet), reads five trees under --root (default: this repo) and prints, per tree, the lines that hold at least
--min-terms of them: file:line, how many terms, the negation words on the line, and the negation words on the line
before and after ("near"). The model judges whether a line really says the opposite. This program does not.

Trees: CLAUDE.md; design/RimMandrake/standing_rulings.md; src/RimMandrake/rimflow/roles/ (*.md, *.txt);
skills/ (*.md, *.txt); design/specs/*/boundary.md.
Each tree reads one of: its hits; `none (looked)` with how many files and lines were read; `COULD NOT LOOK (<cause>)`
with the path (a missing root, a root with no file, a file that cannot be read or decoded). Never blank.
Exit 0: a hit in some tree. 1: none in any tree, all looked. 3: some tree (or file) could not be looked at, whatever else
was found (the others are still printed). 2: a call with no key term.
"""
import argparse
import glob
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TOP_DEFAULT = 8      # budget: lines shown per tree. danger=a hit below the cut is not seen; the footer says so and --all shows all.
MIN_WORD = 4         # budget: shortest key word. danger=a short content word ("map", "def") is not searched; add a longer one.
SNIP = 150           # budget: characters of a hit line printed. danger=the clause that negates sits past the cut; the file:line points to it.

STOP = set("""about above after again against also because been before being below between both cannot could does doing down
during each either else ever every from further have having here herself himself into itself just more most much must
need once only other ours ourselves over same shall should some such than that their theirs them themselves then there
these they this those through under until upon very want were what when where which while whom whose will with would
your yours yourself yourselves""".split())
# a negation or a limit: the words that turn a line against a ruling. Longest forms first.
NEG_RE = re.compile(r"\b(?:do not|does not|did not|must not|may not|should not|cannot|can't|don't|doesn't|won't|never|"
                    r"not|none|nothing|nobody|no|nor|without|only|refuse[sd]?|refusal|stop(?:s|ped)?|retired|dead|"
                    r"banned?|forbid(?:s|den)?|unless|instead|deleted?|sleeps?)\b", re.I)
TEXT_EXT = (".md", ".txt")


def stem(w):
    w = w.lower()
    if w.endswith("ies") and len(w) > 4:
        w = w[:-3] + "y"
    elif w.endswith("sses"):
        w = w[:-2]
    elif w.endswith("ing") and len(w) > 5:
        w = w[:-3]
    elif w.endswith("ed") and len(w) > 4:
        w = w[:-2]
    elif w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        w = w[:-1]
    if w.endswith("e") and len(w) > 4:
        w = w[:-1]
    return w


def words(text):
    return re.findall(r"[a-z]+", text.lower())


def key_terms(said):
    """(terms in order, dropped words). A term is a stem of a word of MIN_WORD letters or more that is no stop word."""
    terms, dropped = [], []
    for w in words(said):
        if len(w) < MIN_WORD or w in STOP:
            dropped.append(w)
            continue
        s = stem(w)
        if s not in terms:
            terms.append(s)
    return terms, dropped


def trees(root):
    """[(name, kind, path-or-pattern)]: kind 'file', 'dir' or 'glob'."""
    j = lambda *a: os.path.join(root, *a)   # noqa: E731
    return [("CLAUDE.md", "file", j("CLAUDE.md")),
            ("standing_rulings", "file", j("design", "RimMandrake", "standing_rulings.md")),
            ("roles", "dir", j("src", "RimMandrake", "rimflow", "roles")),
            ("skills", "dir", j("skills")),
            ("boundary", "glob", j("design", "specs", "*", "boundary.md"))]


def list_files(kind, path):
    """(files, cause). cause is None when the root could be listed and held at least one file."""
    if kind == "file":
        return ([path], None) if os.path.isfile(path) else ([], "missing: %s" % path)
    if kind == "dir":
        if not os.path.isdir(path):
            return [], "missing: %s" % path
        fs = []
        for d, _dirs, names in os.walk(path):
            fs += [os.path.join(d, n) for n in names if n.endswith(TEXT_EXT)]
        return (sorted(fs), None) if fs else ([], "no .md or .txt file under %s" % path)
    base = os.path.dirname(os.path.dirname(path))
    if not os.path.isdir(base):
        return [], "missing: %s" % base
    fs = sorted(glob.glob(path))
    return (fs, None) if fs else ([], "no file matches %s" % path)


def read(path):
    """(lines, cause)."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().splitlines(), None
    except UnicodeDecodeError as e:
        return None, "decode error in %s: %s" % (path, e.reason)
    except OSError as e:
        return None, "%s: %s" % (path, e.strerror or type(e).__name__)


def negs(text):
    out = []
    for m in NEG_RE.finditer(text):
        w = m.group(0).lower()
        if w not in out:
            out.append(w)
    return out


def scan(root, name, kind, path, terms, min_terms):
    """One tree: dict(name, hits, files, lines, cant). hits: (nterms, hasneg, relpath, lineno, own, near, text)."""
    res = {"name": name, "hits": [], "files": 0, "lines": 0, "cant": []}
    files, cause = list_files(kind, path)
    if cause:
        res["cant"].append(cause)
        return res
    tset = set(terms)
    for fp in files:
        lines, cause = read(fp)
        if cause:
            res["cant"].append(cause)
            continue
        res["files"] += 1
        res["lines"] += len(lines)
        rel = os.path.relpath(fp, root)
        for i, ln in enumerate(lines):
            n = len(tset & {stem(w) for w in words(ln)})
            if n < min_terms:
                continue
            own = negs(ln)
            near = []
            for j in (i - 1, i + 1):
                if 0 <= j < len(lines):
                    near += [w for w in negs(lines[j]) if w not in near]
            res["hits"].append((n, bool(own or near), rel, i + 1, own, near, ln.strip()))
    res["hits"].sort(key=lambda h: (-h[0], not h[1], h[2], h[3]))
    return res


def render(res, nterms, top):
    out = []
    h = res["hits"]
    head = "== %s" % res["name"]
    if h:
        shown = h if top is None else h[:top]
        out.append("%s: %d hit line(s) (read %d file(s), %d lines)" % (head, len(h), res["files"], res["lines"]))
        for n, _neg, rel, no, own, near, text in shown:
            neg = "neg: %s" % (", ".join(own) if own else "(none)")
            if near:
                neg += " | near: %s" % ", ".join(near)
            out.append("  %s:%d [%d/%d terms] %s :: %s" % (rel, no, n, nterms, neg,
                                                          text if len(text) <= SNIP else text[:SNIP] + "..."))
        if len(shown) < len(h):
            out.append("  ... %d more hit line(s) not shown: --all shows every one (the cut hides lines; it ends no work)"
                       % (len(h) - len(shown)))
    elif not res["cant"]:
        out.append("%s: none (looked) - read %d file(s), %d lines; no line holds enough terms"
                   % (head, res["files"], res["lines"]))
    else:
        out.append("%s: no hit in the part that could be read (read %d file(s), %d lines)" % (head, res["files"], res["lines"]))
    for c in res["cant"]:
        out.append("  COULD NOT LOOK (%s)" % c)
    return out


def main(argv=None, out=None):
    out = out or sys.stdout
    ap = argparse.ArgumentParser(description="lines in the rule trees that may say the opposite of a new ruling")
    ap.add_argument("said", nargs="+", help="his words")
    ap.add_argument("--root", default=REPO, help="the repo root that holds the five trees (default: this repo)")
    ap.add_argument("--top", type=int, default=TOP_DEFAULT, help="lines shown per tree (default %d)" % TOP_DEFAULT)
    ap.add_argument("--all", action="store_true", help="show every hit line")
    ap.add_argument("--min-terms", type=int, default=None, help="terms a line must hold (default 2, or 1 if only 1 term)")
    o = ap.parse_args(argv)
    said = " ".join(o.said)
    terms, dropped = key_terms(said)
    if not terms:
        print("ruling_search: no key term in %r (stop words and words under %d letters are dropped)" % (said, MIN_WORD),
              file=out)
        return 2
    mt = o.min_terms or (2 if len(terms) >= 2 else 1)
    lines = ["ruling_search: terms (stems): %s; need %d per line; dropped: %s" % (", ".join(terms), mt,
                                                                                  ", ".join(dropped) or "none"),
             "his words carry: %s. The lines below MAY say the opposite; the model judges." % (", ".join(negs(said)) or "no negation word")]
    results = [scan(o.root, n, k, p, terms, mt) for n, k, p in trees(o.root)]
    for r in results:
        lines += render(r, len(terms), None if o.all else o.top)
    hit = sum(1 for r in results if r["hits"])
    cant = [r["name"] for r in results if r["cant"]]
    lines.append("SUMMARY: %d tree(s) with hits; looked, no hit: %s; could not look: %s"
                 % (hit, ", ".join(r["name"] for r in results if not r["hits"] and not r["cant"]) or "-",
                    ", ".join(cant) or "-"))
    print("\n".join(lines), file=out)
    return 3 if cant else (0 if hit else 1)


if __name__ == "__main__":
    sys.exit(main())
