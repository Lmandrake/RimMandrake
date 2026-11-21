#!/usr/bin/env python3
"""The lose-nothing check of the rule-file compression (item RIMMANDRAKE_CRYSTALLIZE_RULE_FILES_DOUBLED_IN_EIGHT_DAYS).

    selftest_rule_files_lose_nothing.py             planted cases on built-in fixtures: is the instrument alive?
    selftest_rule_files_lose_nothing.py check       the real check: base commit of the map against the working tree
    selftest_rule_files_lose_nothing.py planted     plant four losses in a copy of the real result; each must FAIL
    selftest_rule_files_lose_nothing.py skeleton [FILE...]   print map rows (file, section, lines) to fill in
    selftest_rule_files_lose_nothing.py changed     list the sections whose text differs from the base

The rule files are the root CLAUDE.md, design/RimMandrake/standing_rulings.md, infrastructure/agents/CHARTER.md and
src/RimMandrake/rimflow/roles/*.md. The map is design/specs/2026-11-21-crystallize-rule-files/map.md plus any file in
map_parts/ beside it. Its header holds `base: <sha>`. A map row is `| file | section | lines | class | after |`.

`check` fails when:
  ROW      a section of a base rule file has no map row, or a row has no class or no `after` text;
  SENTENCE a sentence of the base is no longer present word for word, and the row of its section says `unchanged`
           (a changed or deleted rule that the map does not account for);
  SPAN     a code span, NAMED_ID or number-with-its-next-word of the base is in no file afterwards, and no row of a
           `## Deleted spans` table names it;
  QUOTE    a quote of 4 words or more in the base is in no file afterwards, word for word. A quote is never excused
           by the Deleted spans table unless that row says `not his words`;
  POINTER  a `§ title` citation anywhere in the repo named a section of a rule file at the base and names none now;
           or a rule file now cites a path or a `§ title` that does not exist and that the base did not cite;
  LONGER   a rule file has more lines than at the base (plus the lines that commits listed under `foreign:` added).

"Afterwards" is: the rule files, design/RimMandrake/CLAUDE.history.md, and each existing file that a map row names
in its `after` cell. The check does not read meaning: a reworded rule passes when its spans stay. A fresh reader
guards meaning. Records of the past (the ledger, conversations, handoffs, closed items) are not scanned for pointers.

Exit: 0 PASS; 1 FAIL (each loss is listed); 3 UNMEASURED: could not look (git failed, the map is absent or has no
base). Exit 3 is not a pass.
"""
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SPEC = "design/specs/2026-11-21-crystallize-rule-files"
FIXED = ["CLAUDE.md", "design/RimMandrake/standing_rulings.md", "infrastructure/agents/CHARTER.md"]
ROLES = "src/RimMandrake/rimflow/roles/"
HISTORY = "design/RimMandrake/CLAUDE.history.md"
SKIP = ("conversations/", "infrastructure/state/ledger/", "infrastructure/state/handoffs/",
        "infrastructure/state/items/closed/", "Transient/", "journal/", SPEC + "/")
TOP = "(top)"


class CouldNotLook(Exception):
    pass


def git(*a):
    r = subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        raise CouldNotLook("git %s: %s" % (" ".join(a[:3]), r.stderr.strip()[:200]))
    return r.stdout


def squash(s):
    return re.sub(r"\s+", "", s)


# ---- sections ---------------------------------------------------------------------------------------------------
def sections(text):
    """[(title, body, line count)] in order. A heading inside a code fence is not a heading."""
    out, title, cur, fenced = [], TOP, [], False
    for l in text.split("\n"):
        if l.lstrip().startswith("```"):
            fenced = not fenced
        m = None if fenced else re.match(r"#{1,6}\s+(.*\S)\s*$", l)
        if m:
            out.append((title, "\n".join(cur), len(cur) + (title != TOP)))
            title, cur = m.group(1), []
        else:
            cur.append(l)
    out.append((title, "\n".join(cur), len(cur) + (title != TOP)))
    return [(t, b, n) for t, b, n in out if t != TOP or b.strip()]


def units(body):
    """The sentences of a section: one per sentence of a paragraph or bullet, one per table row or fenced line."""
    out, para, fenced = [], [], False

    def flush():
        if para:
            text = " ".join(x.strip() for x in para)
            out.extend(s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z`\"“(\[*])", text))
            para[:] = []
    for l in body.split("\n"):
        s = l.strip()
        if s.startswith("```"):
            flush()
            fenced = not fenced
        elif fenced or s.startswith("|"):
            flush()
            if s and not re.fullmatch(r"[|\-: ]+", s):
                out.append(s)
        elif not s:
            flush()
        elif re.match(r"(?:[-*+]|\d+[.)])\s", s):
            flush()
            para.append(re.sub(r"^(?:[-*+]|\d+[.)])\s+", "", s))
        else:
            para.append(s)
    flush()
    return [u for u in out if len(re.findall(r"\w+", u)) >= 4]


# ---- spans ------------------------------------------------------------------------------------------------------
CODE = re.compile(r"`([^`\n]+(?:\n[^`\n]+)?)`")
NAMED = re.compile(r"\b([A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+)\b")
NUMBER = re.compile(r"(?<![\w.`/-])(\d[\d,]*(?:\.\d+)?%?(?:[ -][A-Za-z]{2,})?)")
QUOTE = re.compile(r"[\"“]([^\"“”]{12,600})[\"”]")


def prose(text):
    """Paragraphs outside code fences, each joined to one line."""
    out, cur, fenced = [], [], False
    for l in text.split("\n"):
        if l.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced and l.strip():
            cur.append(l.strip())
        elif cur:
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def spans(text):
    """{(kind, span)} of a text. A quote is read with code spans masked, and must hold 4 words."""
    out = set()
    for p in prose(text):
        for m in CODE.finditer(p):
            out.add(("code", m.group(1).strip()))
        bare = CODE.sub(" ` ", p)
        for m in QUOTE.finditer(bare):
            q = m.group(1).strip()
            if len(q.split()) >= 4 and "`" not in q and not q[0].isspace():
                out.add(("quote", q))
        for m in NUMBER.finditer(bare):
            if re.search(r"[A-Za-z]", m.group(1)):
                out.add(("number", m.group(1)))
    for m in NAMED.finditer(text):
        out.add(("id", m.group(1)))
    return out


# ---- the map ----------------------------------------------------------------------------------------------------
def cells(line):
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def read_map(texts):
    """-> (base sha, foreign shas, {(file, section): [(class, after)]}, {span: why})."""
    base, foreign, rows, gone = None, [], {}, {}
    for text in texts:
        in_gone = False
        for l in text.split("\n"):
            m = re.match(r"\s*base:\s*`?([0-9a-f]{7,40})`?", l)
            if m and not base:
                base = m.group(1)
            m = re.match(r"\s*foreign:\s*(.*)", l)
            if m:
                foreign += re.findall(r"[0-9a-f]{7,40}", m.group(1))
            if l.startswith("#"):
                in_gone = "deleted spans" in l.lower()
            if not l.lstrip().startswith("|") or re.fullmatch(r"[|\-: ]+", l.strip()):
                continue
            c = cells(l)
            if in_gone and len(c) >= 2 and c[0].lower() != "span":
                gone[squash(c[0].strip("`"))] = c[-1]
            elif not in_gone and len(c) >= 5 and c[0].lower() != "file":
                rows.setdefault((c[0].strip("`"), c[1]), []).append((c[3], c[4]))
    return base, foreign, rows, gone


def rule_files_at(rev):
    names = git("ls-tree", "-r", "--name-only", rev, "--", ROLES).split()
    return FIXED + sorted(n for n in names if n.endswith(".md"))


def load():
    """-> state dict read from git and the working tree."""
    paths = [os.path.join(ROOT, SPEC, "map.md")] + sorted(glob.glob(os.path.join(ROOT, SPEC, "map_parts", "*.md")))
    texts = [open(p, encoding="utf-8").read() for p in paths if os.path.exists(p)]
    if not texts:
        raise CouldNotLook("no map at %s/map.md" % SPEC)
    base, foreign, rows, gone = read_map(texts)
    if not base:
        raise CouldNotLook("the map has no `base: <sha>` line")
    files = rule_files_at(base)
    old = {f: git("show", "%s:%s" % (base, f)) for f in files}
    new = {}
    for f in sorted(set(files) | set(FIXED) | set(
            os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, ROLES, "*.md")))):
        p = os.path.join(ROOT, f)
        new[f] = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    extra = {}
    dests = {HISTORY} | set(re.findall(r"`([\w./~-]+\.\w+)`", "\n".join(a for v in rows.values() for _, a in v)))
    for d in sorted(dests):
        p = os.path.join(ROOT, d)
        if d not in new and os.path.isfile(p):
            extra[d] = open(p, encoding="utf-8", errors="replace").read()
    allow = {}
    for sha in foreign:
        for l in git("show", "--numstat", "--format=", sha, "--", *files).splitlines():
            a, d, f = l.split("\t")
            allow[f] = allow.get(f, 0) + int(a) - int(d)
    cites = []
    listed = git("grep", "-l", "-I", "§", "--", "*.md", "*.py", "*.json", "*.sh", "*.txt").split("\n")
    for f in listed:
        if f and not f.startswith(SKIP) and f not in new:
            cites.append((f, open(os.path.join(ROOT, f), encoding="utf-8", errors="replace").read()))
    return {"old": old, "new": new, "extra": extra, "rows": rows, "gone": gone, "allow": allow, "cites": cites,
            "base": base}


# ---- pointers ---------------------------------------------------------------------------------------------------
def words(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).split()


def target_of(before, names):
    """The rule file that the text before a `§` names last, or None."""
    best = None
    for m in re.finditer(r"[\w./~-]*\w\.md", before):
        t = m.group(0)
        hit = None
        if t.endswith("CLAUDE.history.md") or t.startswith("~") or ".claude/CLAUDE.md" in t:
            hit = None
        else:
            for n in names:
                if t == n or n.endswith("/" + t) or (os.path.basename(n) == t and n.startswith(ROLES)) \
                        or (t == os.path.basename(n) and n in FIXED):
                    hit = n
        best = hit
    return best


def citations(text, names):
    """[(target file, citation text)] for each `§` of a text that follows the name of a rule file."""
    out = []
    for p in re.split(r"\n\s*\n", text):
        p = " ".join(x.strip().lstrip("#").strip() for x in p.split("\n"))
        for m in re.finditer("§", p):
            t = target_of(p[:m.start()], names)
            if t:
                out.append((t, p[m.end():m.end() + 160].strip()))
    return out


def resolves(cit, heads):
    """How many words of the citation open a heading, and whether that is a full pointer."""
    cw = words(cit)
    best, full = 0, False
    for h in heads:
        hw = words(h)
        k = 0
        while k < len(hw) and k < len(cw) and hw[k] == cw[k]:
            k += 1
        if k == 0:
            continue
        ends = k == len(hw) or k >= 3
        if not ends:
            m = re.match(r"\W*" + r"\W+".join(re.escape(w) for w in cw[:k]), cit.lower())
            ends = bool(m) and (m.end() >= len(cit) or cit[m.end()] in ".,;:)]\"”*`")
        if (ends, k) > (full, best):
            full, best = ends, k
    return best, full


def heads_of(texts):
    return {f: [t for t, _, _ in sections(x)] for f, x in texts.items()}


def path_like(span):
    return re.fullmatch(r"(?:src|design|infrastructure|skills|world|observed|\.claude)/[\w./-]+", span)


# ---- the check --------------------------------------------------------------------------------------------------
def check(st):
    """-> [(kind, text)] losses."""
    old, new, rows, gone = st["old"], st["new"], st["rows"], st["gone"]
    after = dict(new)
    after.update(st["extra"])
    hay = squash("\n".join(after.values()))
    quote_hay = re.sub(r"\s+", " ", "\n".join(after.values()))
    lost = []
    for f, text in old.items():
        seen = {}
        for title, body, _ in sections(text):
            n = seen[title] = seen.get(title, 0) + 1
            mine = rows.get((f, title), [])
            if len(mine) < n:
                lost.append(("ROW", "%s § %s: no map row" % (f, title)))
                continue
            cls, aft = mine[n - 1]
            if not cls or not aft or cls == "?":
                lost.append(("ROW", "%s § %s: the row has no class or no `after` text" % (f, title)))
            if aft.lower().startswith("unchanged"):
                for u in units(body):
                    if squash(u) not in hay:
                        lost.append(("SENTENCE", "%s § %s: row says unchanged, but this is gone: %s" % (f, title, u[:110])))
        for kind, span in sorted(spans(text)):
            if kind == "quote":
                if re.sub(r"\s+", " ", span) not in quote_hay and "not his words" not in gone.get(squash(span), ""):
                    lost.append(("QUOTE", "%s: “%s”" % (f, span[:140])))
            elif squash(span) not in hay and squash(span) not in gone:
                lost.append(("SPAN", "%s: %s `%s`" % (f, kind, span[:120])))
        if f in new and new[f].count("\n") > text.count("\n") + st["allow"].get(f, 0):
            lost.append(("LONGER", "%s: %d lines at the base, %d now" % (f, text.count("\n"), new[f].count("\n"))))
    names = list(old)
    hb, ha = heads_of(old), heads_of(new)
    for src, text in list(st["cites"]) + list(new.items()):
        was = {(t, c[:40]) for t, c in citations(old.get(src, ""), names) if not resolves(c, hb.get(t, []))[1]}
        for t, cit in citations(text, names):
            kb, fb = resolves(cit, hb.get(t, []))
            ka, fa = resolves(cit, ha.get(t, []))
            if fb and (not fa or ka < kb):
                lost.append(("POINTER", "%s cites %s §%s: that section title is gone" % (src, t, cit[:60])))
            elif not fb and not fa and src in new and (t, cit[:40]) not in was:
                lost.append(("POINTER", "%s cites %s §%s: no such section (a new citation)" % (src, t, cit[:60])))
    old_paths = {s for x in old.values() for k, s in spans(x) if k == "code"}
    for f, text in new.items():
        for kind, span in sorted(spans(text)):
            if kind == "code" and path_like(span) and span not in old_paths \
                    and not os.path.exists(os.path.join(ROOT, span)):
                lost.append(("POINTER", "%s cites the path `%s`: it does not exist (a new citation)" % (f, span)))
    return lost


def report(lost, label):
    kinds = {}
    for k, _ in lost:
        kinds[k] = kinds.get(k, 0) + 1
    for k, t in lost:
        print("  %-8s %s" % (k, t))
    print("%s: %s" % (label, "PASS, 0 losses" if not lost else "FAIL, %d losses %s" % (len(lost), kinds)))
    return 1 if lost else 0


# ---- planted losses ---------------------------------------------------------------------------------------------
def plant(st):
    """Four copies of a state, each with one loss. -> [(name, state, the kind that must fire)]."""
    import copy
    out = []
    # 1. a rule deleted, with no map row for its section.
    s = copy.deepcopy(st)
    f, title, body = next((f, t, b) for f in sorted(s["old"]) for t, b, _ in sections(s["old"][f])
                          if units(b) and any(squash(u) in squash(s["new"].get(f, "")) for u in units(b)))
    u = next(u for u in units(body) if squash(u) in squash(s["new"][f]))
    for g in list(s["new"]) + list(s["extra"]):
        d = s["new"] if g in s["new"] else s["extra"]
        d[g] = re.sub(r"\s+".join(re.escape(w) for w in u.split()), "", d[g])
    s["rows"].pop((f, title), None)
    out.append(("a deleted rule with no map row (%s § %s)" % (f, title), s, "ROW"))
    # 1b. the same deletion, with the row kept and marked unchanged.
    s2 = copy.deepcopy(s)
    s2["rows"][(f, title)] = [("KEEP", "unchanged")] * 9
    out.append(("a deleted rule in a section whose row says unchanged", s2, "SENTENCE"))
    # 2. a reworded quote.
    s = copy.deepcopy(st)
    q = next((q for f in sorted(s["old"]) for k, q in sorted(spans(s["old"][f])) if k == "quote"), None)
    if q:
        w = q.split()
        pat = re.compile(r"\s+".join(re.escape(x) for x in w))
        for d in (s["new"], s["extra"]):
            for g in d:
                d[g] = pat.sub(" ".join(w[:-2] + ["REWORDED"]), d[g])
        out.append(("a reworded quote (“%s”)" % q[:50], s, "QUOTE"))
    # 3. a broken pointer: rename a cited section title.
    s = copy.deepcopy(st)
    hb = heads_of(s["old"])
    for src, text in list(s["cites"]) + list(s["new"].items()):
        hit = next(((t, c) for t, c in citations(text, list(s["old"])) if resolves(c, hb.get(t, []))[1]
                    and resolves(c, heads_of(s["new"]).get(t, []))[1]), None)
        if hit:
            t, c = hit
            k = resolves(c, heads_of(s["new"])[t])[0]
            for h in heads_of(s["new"])[t]:
                if words(h)[:k] == words(c)[:k]:
                    s["new"][t] = s["new"][t].replace(h, "Renamed " + h)
            out.append(("a broken pointer (%s cites %s §%s)" % (src, t, c[:40]), s, "POINTER"))
            break
    # 4. a longer rule file.
    s = copy.deepcopy(st)
    f = sorted(s["old"])[0]
    s["new"][f] = s["old"][f] + "\nA new line.\n"
    s["rows"] = {k: [(c, "MERGE into itself")] * len(v) for k, v in s["rows"].items() for c, _ in v[:1]}
    out.append(("a rule file longer than at the base (%s)" % f, s, "LONGER"))
    return out


def run_planted(st, label):
    bad = 0
    for name, s, kind in plant(st):
        fired = {k for k, _ in check(s)}
        ok = kind in fired
        bad += not ok
        print("  %s  planted: %s -> %s" % ("ok  " if ok else "MISS", name, "FAIL %s" % kind if ok else "NOT CAUGHT"))
    print("%s: %s" % (label, "every planted loss was caught" if not bad else "%d planted losses NOT CAUGHT" % bad))
    return 1 if bad else 0


FIX_OLD = {"CLAUDE.md": "# Root\n\n## Git\n\n- Never use `git add -A`. The pool holds 16 clones.\n- He said \"keep the"
           " bridge free for me\" on that day.\n\n## Other\n\n- Read `infrastructure/agents/CHARTER.md` §Stop rule"
           " first.\n",
           "infrastructure/agents/CHARTER.md": "# Charter\n\n## Stop rule\n\n- Stop when RM_STOP_NOW is set, at once.\n",
           "design/RimMandrake/standing_rulings.md": "# Rulings\n\n## Git\n\n- The full text of the git rule is here.\n"}


def fixture():
    rows = {(f, t): [("KEEP", "unchanged")] for f, x in FIX_OLD.items() for t, _, _ in sections(x)}
    return {"old": dict(FIX_OLD), "new": dict(FIX_OLD), "extra": {}, "rows": rows, "gone": {}, "allow": {},
            "cites": [("x.py", "# see CHARTER.md §Stop rule.\n")], "base": "fixture"}


def selftest():
    st = fixture()
    clean = check(st)
    print("  %s  the untouched fixture -> %s" % ("ok  " if not clean else "MISS", "PASS" if not clean else clean))
    bad = bool(clean) + run_planted(st, "fixture")
    s = fixture()                       # a span that the map excuses stays green; a moved quote stays green
    s["new"]["CLAUDE.md"] = s["new"]["CLAUDE.md"].replace("Never use `git add -A`. ", "").replace(
        "- He said \"keep the bridge free for me\" on that day.\n", "")
    s["extra"]["design/RimMandrake/CLAUDE.history.md"] = "He said \"keep the bridge\nfree for me\" on that day.\n"
    s["rows"][("CLAUDE.md", "Git")] = [("TOOL DOES IT + MOVE", "the hook refuses; quote in history")]
    s["gone"][squash("git add -A")] = "block_blanket_git_stage.py refuses it"
    green = check(s)
    print("  %s  an excused span and a moved, re-wrapped quote -> %s" % ("ok  " if not green else "MISS",
                                                                      "PASS" if not green else green))
    bad += bool(green)
    print("selftest_rule_files_lose_nothing: %s" % ("PASS" if not bad else "FAIL"))
    return 1 if bad else 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "selftest"
    try:
        if cmd == "selftest":
            return selftest()
        if cmd == "skeleton":
            rev = "HEAD"
            for f in argv[2:] or rule_files_at(rev):
                for t, _, n in sections(git("show", "%s:%s" % (rev, f))):
                    print("| `%s` | %s | %d | ? | ? |" % (f, t.replace("|", "\\|"), n))
            return 0
        st = load()
        if cmd == "changed":
            for f, text in st["old"].items():
                hay = squash(st["new"].get(f, ""))
                for t, b, n in sections(text):
                    miss = sum(1 for u in units(b) if squash(u) not in hay)
                    if miss:
                        print("%s § %s: %d of %d sentences differ" % (f, t, miss, len(units(b))))
            return 0
        if cmd == "check":
            n = {f: (st["old"][f].count("\n"), st["new"][f].count("\n")) for f in st["old"]}
            print("lines: %d at the base %s, %d now" % (sum(a for a, _ in n.values()), st["base"][:10],
                                                        sum(b for _, b in n.values())))
            return report(check(st), "lose-nothing check")
        if cmd == "planted":
            return run_planted(st, "planted losses on the real result")
    except CouldNotLook as e:
        print("UNMEASURED: could not look: %s" % e)
        return 3
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
