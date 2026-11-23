#!/usr/bin/env python3
"""rule_doc_lint: the measuring tool of the plain-English rewrite (item RIMMANDRAKE_REWRITE_RULE_DOCS_PLAIN_ENGLISH_LOSE_NOTHING).

    rule_doc_lint.py lint FILE...            one line per file: STE lint per 100 words, long sentences, flagged lines
    rule_doc_lint.py lint FILE --show        also print each long sentence and each flagged line
    rule_doc_lint.py census [--json OUT]     the census table over the candidate set (CLASSES below), with readers
    rule_doc_lint.py keep OLD NEW [--also F...]   every code span, number, quote and NAMED_ID of OLD is in NEW or an --also file
    rule_doc_lint.py selftest                planted cases: the lint, the flags and `keep` must see them

`keep` is the second no-loss check. The first is `checkable.py compare` of the crystallize skill. `checkable.py` does
not see a number with no unit ("45 minutes", "1127-line") or a short code span (`RM_Greatbole`). `keep` sees those. OLD
may be `git:<rev>:<path>`. `keep` compares text with all white space removed, so a re-wrapped line is not a loss. `keep` counts each number:
the new text must hold a number as many times as the old text.
Neither check reads prose: a rule with no number, name or code span needs a reader. Exit 1 lists each lost span.

The STE lint is `ste_lint` of the clear-findings skill (~/.claude/skills/clear-findings/tools/clarify.py). This tool
feeds it one bullet, heading or paragraph at a time, because its sentence splitter joins markdown bullets (the drain of
2026-11-19 measured 94 false long sentences that way). Code fences and table rows are not linted.

The STE figure measures obedience to the STE spec. It does not measure clarity (clear-findings SKILL.md). The flag
count is mechanical too. A flagged line is a line to READ, not a verdict:
  pronoun   a sentence opens with It/This/That/They/These/Those and then a verb: the sentence names no subject
  bare-id   a short coded id (D31, WP-15, G21, Q11a) with no title beside it
  shout     an emphasis emoji, or a run of 3+ ALL-CAPS words
  above     "see above", "as above", "the above", "the latter", "the former": the reader must hunt for the subject
Exit codes: 0 answered; 2 caller error; 3 the lint module could not be loaded (nothing is printed that reads as a score).
"""
import fnmatch
import json
import os
import re
import subprocess
import sys
from collections import Counter

CLARIFY_DIR = os.environ.get("CLEAR_FINDINGS_TOOLS") or os.path.expanduser("~/.claude/skills/clear-findings/tools")


def load_clarify():
    sys.path.insert(0, CLARIFY_DIR)
    try:
        import clarify
    except Exception as e:  # the instrument is absent: say so, score nothing
        sys.stderr.write("UNMEASURED: cannot import clarify.py from %s (%s). Set CLEAR_FINDINGS_TOOLS.\n" % (CLARIFY_DIR, e))
        sys.exit(3)
    return clarify


EMOJI = re.compile("[\U0001F534\U0001F511⛔⚠⭐\U0001F6D1✅❌\U0001F4B0\U0001F50D⚖]")
CAPS_RUN = re.compile(r"(?:\b[A-Z]{3,}\b[ ,:;-]+){2,}\b[A-Z]{3,}\b")
PRONOUN = re.compile(r"(?:^|(?<=[.!?:;] ))(?:It|This|That|They|These|Those)\s+"
                     r"(?:is|are|was|were|has|have|had|does|do|did|can|will|must|may|goes|reads|runs|means|makes|"
                     r"keeps|needs|stays|fires|binds|holds|covers|applies|works|fails|returns|writes|gives|takes)\b")
BARE_ID = re.compile(r"(?<![\w/`.-])(?:[A-Z]{1,2}-?\d{1,3}[a-z]?|WP-\d+|LODE-\d+)(?![\w/-])")
BARE_ID_OK = re.compile(r"^(?:P\d{2}|V\d|H[1-6]|A4|B12|S3|T\d|X\d|Q[1-4]|D:)$")   # upstream names, headings, a drive
ABOVE = re.compile(r"\b(?:see above|as above|the above|the latter|the former|see below)\b", re.I)
SPAN = re.compile(r"`[^`]*`|\*\"[^\"]*\"\*|\"[^\"]*\"|“[^”]*”")       # code spans and quotes are not our prose


def units_of(text):
    """-> [(line_no, unit text, kind)] ; kind is 'prose' (linted) or 'table' (flag scan only)."""
    text = re.sub(r"(?s)\A---\n.*?\n---\n", lambda m: "\n" * m.group(0).count("\n"), text)   # YAML front matter
    out, cur, start, fence = [], [], 0, False
    def flush():
        if cur:
            out.append((start, " ".join(cur), "prose"))
        del cur[:]
    for n, l in enumerate(text.splitlines(), 1):
        if l.lstrip().startswith("```"):
            fence = not fence
            flush()
            continue
        if fence:
            continue
        if l.lstrip().startswith("|"):
            flush()
            if not re.match(r"^\s*\|[\s|:-]+\|?\s*$", l):
                out.append((n, l.strip(), "table"))
            continue
        if not l.strip():
            flush()
            continue
        m = re.match(r"\s*(#+|[-*] |\d+\. |> ?)", l)
        if m:
            flush()
            body = l[m.end():].strip()
            if m.group(1).startswith("#"):
                out.append((n, body, "prose"))
            else:
                start = n
                cur.append(body)
        else:
            if not cur:
                start = n
            cur.append(l.strip())
    flush()
    return [u for u in out if u[1].strip()]


def flags_of(unit):
    bare = SPAN.sub(" ", unit)
    f = []
    if PRONOUN.search(bare):
        f.append("pronoun")
    if any(not BARE_ID_OK.match(m.group(0)) for m in BARE_ID.finditer(bare)):
        f.append("bare-id")
    if EMOJI.search(unit) or CAPS_RUN.search(bare):
        f.append("shout")
    if ABOVE.search(bare):
        f.append("above")
    return f


def measure(text, C):
    V, words, sents, long_s, flagged = [], 0, 0, [], []
    us = units_of(text)
    for n, u, kind in us:
        fl = flags_of(u)
        if fl:
            flagged.append((n, fl, u))
        if kind != "prose":
            continue
        L = C.ste_lint(u)
        V += L["violations"]
        words += L["words"]
        sents += L["sentences"]
        ss = C.sentences(u)
        for v in L["violations"]:
            if v["rule"].startswith("sentence over"):
                long_s.append((n, ss[v["sentence"]]))
    return {"units": len(us), "sentences": sents, "words": words, "violations": len(V),
            "per100": round(100.0 * len(V) / words, 2) if words else None,   # None = no prose to lint, not zero
            "long": len(long_s), "flagged": len(flagged), "rules": dict(Counter(v["rule"] for v in V)),
            "flag_kinds": dict(Counter(k for _, fl, _ in flagged for k in fl)),
            "_long": long_s, "_flagged": flagged}


def line_of(path, m):
    p = "UNMEASURED (no prose)" if m["per100"] is None else "%.2f per 100 words" % m["per100"]
    return "%s: %d words, STE %s (%d violations), %d sentences over 20 words, %d flagged lines %s" % (
        path, m["words"], p, m["violations"], m["long"], m["flagged"], m["flag_kinds"] or "")


# ---- keep: the second no-loss check ---------------------------------------------------------------------------------
KEEP = [("code span", re.compile(r"`([^`]+)`")),
        ("number", re.compile(r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)(?![\d])")),
        ("quote", re.compile(r"[\"“]([^\"“”\n]{12,})[\"”]")),
        ("named id", re.compile(r"\b([A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+)\b"))]


def read_any(spec):
    if spec.startswith("git:"):
        _, rev, path = spec.split(":", 2)
        r = subprocess.run(["git", "show", "%s:%s" % (rev, path)], capture_output=True, text=True)
        if r.returncode != 0:
            sys.stderr.write("UNMEASURED: cannot read %s (%s)\n" % (spec, r.stderr.strip()[:160]))
            sys.exit(3)
        return r.stdout
    try:
        with open(spec, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError as e:
        sys.stderr.write("UNMEASURED: cannot read %s (%s)\n" % (spec, e))
        sys.exit(3)


def paragraphs(text):
    """The text outside fenced blocks, split at blank lines. A code span may wrap a line but never crosses a blank line."""
    out, cur, fenced = [], [], False
    for l in text.split("\n"):
        if l.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if l.strip():
            cur.append(l)
        elif cur:
            out.append("\n".join(cur))
            cur = []
    if cur:
        out.append("\n".join(cur))
    return out


def squash(s):
    return re.sub(r"\s+", "", s)


def keep(old, new_texts):
    """-> (count of spans in old, [(kind, span)] lost). A code span, quote or id is lost when no new text holds it.
    A number is counted: it is lost when the new texts hold it fewer times than old does ("at most 4 subjects" ->
    "a few subjects" is a loss even when another 4 stays in the file)."""
    hay = squash("\n".join(new_texts))
    seen, lost = set(), []
    for kind, rx in KEEP:
        if kind == "number":
            want = Counter(m.group(1).rstrip(",") for m in rx.finditer(old))
            have = Counter(m.group(1).rstrip(",") for m in rx.finditer("\n".join(new_texts)))
            for span, n in sorted(want.items()):
                seen.add((kind, span))
                if have[span] < n:
                    lost.append((kind, "%s (%d in the old text, %d in the new)" % (span, n, have[span])))
            continue
        # A quote is read with each code span masked by a line break: a `"` inside one code span and a `"` inside the
        # next one are not a quote. A code span is checked whole, as a code span.
        if kind == "quote":
            srcs = [re.sub(r"`[^`]+`", "\n", p) for p in paragraphs(old)]
        elif kind == "code span":
            srcs = paragraphs(old)
        else:
            srcs = [old]
        for m in (m for src in srcs for m in rx.finditer(src)):
            span = m.group(1).strip()
            if not span or (kind, span) in seen:
                continue
            seen.add((kind, span))
            if squash(span) not in hay:
                lost.append((kind, span))
    return len(seen), lost


# ---- census ------------------------------------------------------------------------------------------------------
# class -> globs. A file belongs to the first class that matches it.
CLASSES = [
    ("root", ["CLAUDE.md", "PURPOSE.md"]),
    ("agent-def", [".claude/agents/*.md", ".claude/rm_agent_shared_block.md", ".claude/rm_positive_steps.md",
                   ".claude/commands/*.md"]),
    ("seat", ["infrastructure/agents/*.md"]),
    ("role", ["src/RimMandrake/rimflow/roles/*.md"]),
    ("ruling", ["design/RimMandrake/standing_rulings.md", "design/RimMandrake/biome_rulings.md",
                "design/RimMandrake/delegation_policy.md", "design/RimMandrake/debug_process.md",
                "design/RimMandrake/GIT_WORKFLOW.md", "design/RimMandrake/CLAUDE.history.md",
                "infrastructure/GAME_STATE_WORKFLOW.md", "design/specs/2026-11-13-maturation-pipeline.md"]),
    ("brief", ["design/RimMandrake/art_judge_brief.md", "design/RimMandrake/scene_look_judge_brief.md",
               "design/RimStarWars/canon_references/AGENT_BRIEF.md", "design/RimMandrake/gpt_reviews/PROMPT.md",
               "design/RimStarWars/canon_references/gpt_review/PROMPT.md",
               "skills/rimworld-art-evaluation/references/prompts/*.md"]),
    ("facts", ["infrastructure/state/facts/*.md"]),
    ("skill", ["skills/*/SKILL.md", "skills/README.md", "skills/BY_WORK.md"]),
    ("infra-doc", ["infrastructure/*.md", "README.md", "LEXICON.md"]),
]
# who may cite a file, grouped; a hit is evidence of a reader
READER_SETS = [
    ("code", ["*.py", "*.sh", "*.json", "*.service", "*.timer", "publish", "pipe", "game", "bridge", "mirror", "sync"]),
    ("CLAUDE.md", ["CLAUDE.md"]),
    ("roles+agents", ["src/RimMandrake/rimflow/roles/*.md", ".claude/agents/*.md", "infrastructure/agents/*.md",
                      ".claude/*.md"]),
    ("skills", ["skills/*.md", "skills/*/SKILL.md"]),
]
GREP_SKIP = (":!conversations/", ":!infrastructure/state/ledger/", ":!infrastructure/state/handoffs/",
             ":!infrastructure/state/items/", ":!infrastructure/state/runs/", ":!design/concepts/",
             ":!design/RimMandrake/designer_codex_2026-11-09/", ":!infrastructure/state/delegated/",
             ":!src/RimMandrake/Utils/hook_latency_corpus.json")


def git(*a):
    r = subprocess.run(("git",) + a, capture_output=True, text=True)
    if r.returncode not in (0, 1):
        sys.stderr.write("git %s failed: %s\n" % (" ".join(a[:3]), r.stderr[:200]))
        sys.exit(3)
    return r.stdout.splitlines()


def needle(path):
    """What a citing file would write. A skill is cited by folder; a generic basename needs its folder."""
    base = os.path.basename(path)
    if base == "SKILL.md":
        return os.path.basename(os.path.dirname(path))
    if base in ("README.md", "CLAUDE.md", "PROMPT.md", "POLICY.md", "preamble.md", "operations.md", "AGENTS.md",
                "CHARTER.md"):
        return path if "/" in path else base
    return base


def readers(path):
    out = {}
    for name, globs in READER_SETS:
        hits = [h for h in git("grep", "-I", "-l", "-F", needle(path), "--", *globs, *GREP_SKIP) if h != path]
        if name == "code":
            hits = [h for h in hits if "selftest" not in h and "/acceptance/" not in h]
        out[name] = hits
    return out


def census(C):
    tracked = git("ls-files")
    rows, seen = [], set()
    for cls, globs in CLASSES:
        for p in tracked:
            if p in seen or not any(fnmatch.fnmatchcase(p, g) and p.count("/") == g.count("/") for g in globs):
                continue
            seen.add(p)
            with open(p, encoding="utf-8", errors="replace") as f:
                text = f.read()
            m = measure(text, C)
            last = (git("log", "-1", "--format=%cs", "--", p) or ["unknown"])[0]
            rd = readers(p)
            rows.append({"path": p, "class": cls, "bytes": len(text.encode("utf-8")), "last_commit": last,
                         "registered": os.path.islink(os.path.join(".claude/skills", needle(p))) if cls == "skill" and p.endswith("SKILL.md") else None,
                         "readers": {k: len(v) for k, v in rd.items()}, "reader_examples": {k: v[:3] for k, v in rd.items()},
                         **{k: v for k, v in m.items() if not k.startswith("_")}})
    return rows


def selftest(C):
    bad = ("# Rules\n\n- It is the mechanism that the boundary reads when the misdiagnosis was made, and it should be "
           "considered carefully by every agent that is running before the tick has been started again.\n"
           "- See D31 for the rest.\n- \U0001F534 NEVER EVER DO THAT.\n- Do the same as above.\n")
    good = "# Rules\n\n- Run the test before you commit.\n- The tick starts the game.\n| a | b |\n|---|---|\n| x | y |\n"
    mb, mg = measure(bad, C), measure(good, C)
    checks = [("bad text has a long sentence", mb["long"] >= 1), ("bad text has violations", mb["violations"] >= 3),
              ("pronoun flag", "pronoun" in mb["flag_kinds"]), ("bare-id flag", "bare-id" in mb["flag_kinds"]),
              ("shout flag", "shout" in mb["flag_kinds"]), ("above flag", "above" in mb["flag_kinds"]),
              ("good text is clean", mg["violations"] == 0 and mg["flagged"] == 0 and mg["long"] == 0),
              ("good text was read", mg["words"] >= 8),
              ("no prose is UNMEASURED, not zero", measure("```\ncode\n```\n", C)["per100"] is None)]
    old = 'Take a stale hold after 45 minutes. Use `rimflow bridge take`. He said "do not hold the game for me". See FOO_BAR_1.'
    n, lost = keep(old, [old.replace("45 minutes", "a while")])
    checks.append(("keep sees a lost number", [k for k, _ in lost] == ["number"] and lost[0][1].startswith("45 ")))
    checks.append(("keep sees one lost copy of a single digit", [k for k, _ in keep("at most 4 subjects; 4 clones", ["a few subjects; 4 clones"])[1]] == ["number"]))
    checks.append(("keep sees a lost code span", ("code span", "rimflow bridge take") in keep(old, [old.replace("`rimflow bridge take`", "the take verb")])[1]))
    checks.append(("keep sees a changed quote", any(k == "quote" for k, _ in keep(old, [old.replace("for me", "for him")])[1])))
    checks.append(("keep sees a lost id", ("named id", "FOO_BAR_1") in keep(old, ["nothing"])[1]))
    checks.append(("keep passes a re-wrapped copy", keep(old, [old.replace(" ", "\n  ")])[1] == [] and n >= 4))
    checks.append(("keep finds a span that moved to an --also file", keep(old, ["short", old])[1] == []))
    # a `"` inside one code span and a `"` inside the next are not a quote (rm-testpilot.md, 2026-11-19)
    two = 'Parse it (`ET.parse(p).find("activeMods")`), never grep it. On SteveDesktop drive by `ssh "$STEVE_WSL"`.'
    split = 'Parse it (`ET.parse(p).find("activeMods")`).\n- Never grep it.\n- On SteveDesktop drive by `ssh "$STEVE_WSL"`.'
    checks.append(("keep reads no quote across two code spans", keep(two, [split])[1] == []))
    checks.append(("keep still sees a lost code span that holds a quote mark",
                   ("code span", 'ssh "$STEVE_WSL"') in keep(two, [split.replace('`ssh "$STEVE_WSL"`', "ssh")])[1]))
    for name, ok in checks:
        print("%s  %s" % ("PASS" if ok else "FAIL", name))
    return 0 if all(ok for _, ok in checks) else 1


def main(argv):
    if len(argv) < 2 or argv[1] not in ("lint", "census", "selftest", "keep"):
        sys.stderr.write(__doc__)
        return 2
    if argv[1] == "keep":
        also = argv[argv.index("--also") + 1:] if "--also" in argv else []
        pos = argv[2:argv.index("--also")] if "--also" in argv else argv[2:]
        if len(pos) != 2:
            sys.stderr.write("keep needs OLD and NEW\n")
            return 2
        n, lost = keep(read_any(pos[0]), [read_any(pos[1])] + [read_any(a) for a in also])
        for kind, span in lost:
            print("LOST %s: %s" % (kind, span[:200]))
        print("KEEP %s: %d spans in %s, %d not found in %s%s" % (
            "FAILED" if lost else "OK", n, pos[0], len(lost), pos[1], (" or %d other file(s)" % len(also)) if also else ""))
        return 1 if lost else 0
    C = load_clarify()
    if argv[1] == "selftest":
        return selftest(C)
    if argv[1] == "lint":
        files = [a for a in argv[2:] if not a.startswith("--")]
        if not files:
            sys.stderr.write("lint needs at least one FILE\n")
            return 2
        for p in files:
            try:
                with open(p, encoding="utf-8", errors="replace") as f:
                    m = measure(f.read(), C)
            except OSError as e:
                sys.stderr.write("UNMEASURED: cannot read %s (%s)\n" % (p, e))
                return 3
            print(line_of(p, m))
            if "--show" in argv:
                for n, s in m["_long"]:
                    print("  LONG %d: %s" % (n, s[:240]))
                for n, fl, u in m["_flagged"]:
                    print("  FLAG %d %s: %s" % (n, ",".join(fl), u[:200]))
        return 0
    rows = census(C)
    if "--json" in argv:
        with open(argv[argv.index("--json") + 1], "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=1)
    for r in rows:
        print("%-10s %-70s %7d  STE %-6s long %-3d flag %-3d readers %s" % (
            r["class"], r["path"], r["bytes"], r["per100"], r["long"], r["flagged"], r["readers"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
