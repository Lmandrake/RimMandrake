#!/usr/bin/env python3
"""guiding_prose.py - guiding prose (a text that tells an agent how to act) is checked when it is written.

Owner, 2026-11-23: "No more searching across whole documents to figure out what something means. Rules have to be
exceptionally clear to be powerful or they can't bind to the moment they pertain to." Page and measurements:
design/specs/2026-11-23-guiding-prose-check/. Item RIMMANDRAKE_CHECK_GUIDING_PROSE_AT_WRITE_NO_SEARCHING_FOR_MEANING.

    guiding_prose.py check FILE... [--base REV]   the sentences that each file adds over REV (no --base: every sentence).
                                                  exit 0 no fault, 1 a fault, 3 could not look
    guiding_prose.py brief FILE                   a brief before its launch; the same exits
    guiding_prose.py diff REV [--base REV]        what the publish door reads for a commit or a range
    guiding_prose.py unfindable --file F --line N --term T --question Q
                                                  a meaning that nobody finds: one ledger item with the question
    guiding_prose.py recheck                      do both doors still return a planted fault? writes recheck.json
    guiding_prose.py calibrate                    the reader's planted cases (refusal_contract.py runs this)

It runs by itself at the end of `./publish` and of `detached_helper.py launch`, after the landing or the start. It
refuses nothing and changes no exit code there: it returns each fault with its repair to the writer, in the same run. A
sentence that the old text already held is never read. Each run is one row in runs.jsonl (RM_GUIDING_PROSE_DIR, else
guiding_prose/ in the Dispatcher's state dir). RM_GUIDING_PROSE_READER=0 turns the model reader off; it also stays off when no agent reads
the output (no CLAUDECODE). RM_GUIDING_PROSE_CUT=publish|launch cuts a door (the recheck then reads it as dead).
"""
import argparse
import bisect
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RIMFLOW = os.path.join(TOP, "src", "RimMandrake", "rimflow")
LINT_DIR = os.path.join(TOP, "design", "specs", "2026-11-19-plain-english-rule-docs")
CONFIG = os.path.join(HERE, "guiding_prose.json")
CONFIG_REL = "src/RimMandrake/Utils/guiding_prose.json"
READER_BRIEF = os.path.join(HERE, "guiding_prose_reader.md")
FAMILY = "guiding_prose_reader"
ITEM_OF_THIS_CHECK = "RIMMANDRAKE_CHECK_GUIDING_PROSE_AT_WRITE_NO_SEARCHING_FOR_MEANING"
BRIEF_PATH = "(brief)"
# Opus: Sonnet did not flag "the D/F primitive" on the owner's own line (measured 2026-11-23, boundary page).
READER_MODEL = "opus"
# A hang guard. Danger: a model call that never returns keeps the writer's ./publish open after the landing. Evidence: a
# real call took 4 to 13 s on 61 to 434 sentences (2026-11-23); this is far above that.
# budget: danger=a model call that never returns keeps the writer's ./publish open after the landing; longest=13s (real calls of
# budget: 4 to 13 s on 61 to 434 sentences, 2026-11-23)
READER_TIMEOUT_S = 300
# ASD-STE100: a procedural sentence has at most 20 words (clarify.MAX_SENTENCE_WORDS), a descriptive one at most 25.
# Danger: several ideas in one sentence, which a reader at that line must take apart. Evidence: the census of 2026-11-19
# (4,247 long sentences); at 20 for both, the descriptive sentences of 21 to 25 words that a hand read called plain
# were about half of the hits (2026-11-23).
MAX_DESCRIPTIVE_WORDS = 25
GIT_TIMEOUT_S = 60          # a hang guard on local git reads (a stuck drvfs read), which take well under 1 s
# budget: danger=a hung throwaway landing or launch holds the recheck; longest=5s (each took 2 to 5 s)
DOOR_TIMEOUT_S = 180        # a hang guard on the recheck's throwaway landing and launch (each takes 2-5 s)
CLAUDE = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")  # systemd's PATH lacks ~/.local/bin


class CouldNotLook(Exception):
    """The check could not read its input or load its lint: the cause. Never zero faults."""


def now_s():
    return int(time.time())


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise CouldNotLook("cannot read %s (%s)" % (path, e))


def config():
    return load_json(CONFIG)


def lint():
    """-> (rule_doc_lint, clarify): the lint that exists. Loaded at the first use: a missing one is CouldNotLook."""
    for d in (LINT_DIR, RIMFLOW, HERE):
        if d not in sys.path:
            sys.path.insert(0, d)
    try:
        import rule_doc_lint as RL
        if not os.path.isfile(os.path.join(RL.CLARIFY_DIR, "clarify.py")):
            raise CouldNotLook("the STE lint clarify.py is not in %s" % RL.CLARIFY_DIR)
        return RL, RL.load_clarify()
    except ImportError as e:
        raise CouldNotLook("the lint cannot be loaded (%s)" % e)
    except SystemExit:
        raise CouldNotLook("the STE lint (clarify.py) cannot be loaded")


def is_guiding(path, cfg=None):
    cfg = cfg or config()
    p = path.replace(os.sep, "/")
    return p not in cfg["left_out"] and any(
        g.count("/") == p.count("/") and fnmatch.fnmatchcase(p, g) for g in cfg["files"])


# ---- reading the sentences -----------------------------------------------------------------------------------------
# An owner quote and card text are exempt word for word. The mark is the quote mark: *"..."*, "..." or “...”, over line
# breaks, never over a blank line. So is every sentence under the heading that card_repair writes into a brief.
CODE = re.compile(r"`(?:[^`\n]|\n(?!\s*\n))+`")
QUOTE = re.compile(r'\*"(?:[^\n]|\n(?!\s*\n))*?"\*|"(?:[^"\n]|\n(?!\s*\n))*?"|“(?:[^“”\n]|\n(?!\s*\n))*?”')
CARD_HEADING = "what the card said"
SPLIT = re.compile(r"(?<=[.!?])\s{3,}|(?<=[.!?])(?<!e\.g\.)(?<!i\.e\.)(?<!vs\.)(?<!No\.)\s+(?=[A-Z(*“\"`0-9\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50])")
COMMAND_LINE = re.compile(r"\s{2,}(?:\$ |python3? |\./[a-z]|git |bash |rimflow |systemctl )")     # an indented code line
ITEM = re.compile(r"\s*(?:[-*] |\d+\. |> ?)")


def _blank(fill):
    """A mask of equal length (offsets stay true): one token, its line breaks kept, its last stop kept as its last sign."""
    def sub(m):
        s = m.group(0)
        out = [c if c == "\n" else fill for c in s]
        out[0] = fill.upper()
        stop = re.search(r"([.!?])[\"”*)]*$", s)
        if stop and len(out) > 1:
            out[-1] = stop.group(1)
        return "".join(out)
    return sub


def masked(text):
    return QUOTE.sub(_blank("q"), CODE.sub(_blank("x"), text))


def sentences(text):
    """-> [{l0, l1, raw, mask, head}] for each prose sentence. Headings, tables, fenced blocks and front matter are not."""
    raw, mk = text.split("\n"), masked(text).split("\n")
    fm = re.match(r"(?s)\A---\n.*?\n---\n", text)
    skip = fm.group(0).count("\n") if fm else 0
    out, cur, head, fence = [], [], "", False

    def flush():
        if not cur:
            return
        buf_r, buf_m, starts = "", "", []
        for n, r, m in cur:
            if buf_m:
                buf_r, buf_m = buf_r + " ", buf_m + " "
            starts.append((len(buf_m), n))
            buf_r, buf_m = buf_r + r, buf_m + m
        plain = buf_m.replace("**", "  ").replace("__", "  ")
        at = [o for o, _ in starts]
        pos, cuts = 0, []
        for s in SPLIT.finditer(plain):
            cuts.append((pos, s.start()))
            pos = s.end()
        cuts.append((pos, len(plain)))
        for a, b in cuts:
            if plain[a:b].strip():
                line = [starts[bisect.bisect_right(at, p) - 1][1] for p in (a, max(a, b - 1))]
                out.append({"l0": line[0], "l1": line[1], "raw": buf_r[a:b].strip(), "mask": plain[a:b].strip(),
                            "pad": len(plain[a:b]) - len(plain[a:b].lstrip()), "head": head})
        del cur[:]
    for n, m in enumerate(mk, 1):
        if n <= skip:
            continue
        r = raw[n - 1]
        if r.lstrip().startswith("```"):
            fence = not fence
            flush()
        elif fence:
            continue
        elif COMMAND_LINE.match(r):
            flush()
        elif re.match(r"\s*#{1,6} ", m):
            flush()
            head = r.strip().lstrip("# ").strip()
        elif not m.strip() or m.lstrip().startswith("|"):
            flush()
        elif head.lower().startswith(CARD_HEADING):
            continue
        else:
            it = ITEM.match(m)
            if it and not (m.lstrip().startswith(">") and cur and raw[n - 2].lstrip().startswith(">")):
                flush()
            cut = it.end() if it else len(m) - len(m.lstrip())
            cur.append((n, r[cut:].rstrip(), m[cut:].rstrip()))
    flush()
    return out


def squash(s):
    return re.sub(r"[\s*_]+", "", s)


def changed_sentences(new, olds):
    """The sentences of `new` that no old text holds. Reads no diff: a re-wrapped or moved sentence is old text."""
    seen = {squash(s["raw"]) for t in olds for s in sentences(t)}
    return [s for s in sentences(new) if squash(s["raw"]) not in seen]


def chunks(text):
    """-> [(first line, last line, level, [(line no, line)])], cut at each heading outside a fence."""
    out, cur, level, fence = [], [], 0, False
    for n, l in enumerate(text.split("\n"), 1):
        if l.lstrip().startswith("```"):
            fence = not fence
        h = None if fence else re.match(r"(#{1,6}) ", l)
        if h and cur:
            out.append((cur[0][0], cur[-1][0], level, cur))
            cur = []
        if h:
            level = len(h.group(1))
        cur.append((n, l))
    if cur:
        out.append((cur[0][0], cur[-1][0], level, cur))
    return out


def section_index(cs, line):
    for i, c in enumerate(cs):
        if c[0] <= line <= c[1]:
            return i
    return len(cs) - 1


def section_text(cs, i, whole=False):
    """The section of chunk i: its own lines, and the opening of each section that it lies under."""
    if whole:
        return "\n".join(l for c in cs for _, l in c[3])
    take, level = [i], cs[i][2]
    for j in range(i - 1, -1, -1):
        if cs[j][2] and cs[j][2] < level:
            take.insert(0, j)
            level = cs[j][2]
    return "\n".join(l for j in take for _, l in cs[j][3])


# ---- what a program decides ----------------------------------------------------------------------------------------
PRONOUN = re.compile(
    r"^(?:(?:So|Then|But|And|Also|Thus|Otherwise|Here|Now),? )?"
    r"(?:(?:(?:^|(?<= ))(?:It|They|(?<= )it|(?<= )they))(?= [a-z])(?! (?:is|was|takes|costs|makes) (?:not )?(?:\w+ ){1,2}(?:to|that)\b)"
    r"|(?:This|That|These|Those|(?<= )(?:this|that|these|those))(?= (?:(?:also|never|always|only|still|now|not) )?(?:is|are|was|were|has|have|"
    r"had|does|do|did|can|will|must|may|goes|reads|runs|means|makes|keeps|needs|stays|fires|binds|holds|covers|applies|"
    r"works|fails|returns|writes|gives|takes|lets|stops|happens|matters)\b))(?: [a-z]+)?")
SHOULD = re.compile(r"(?<!\w)should\b", re.I)
SHOULD_ASKED = re.compile(r"\b(?:what|which|who|how|whether|where|when|why)\b[^.;:]{0,40}$", re.I)
DUTY = re.compile(r"\b(?:must|shall|has to|have to|needs? to|is to|are to)(?: not| never)? be (?:\w+ly )?"
                  r"(?:\w+ed|written|made|done|given|taken|shown|kept|left|read|put|set|sent|built|found|run|held|told|"
                  r"drawn|chosen|rerun|redone|rewritten)\b", re.I)
WHEN = re.compile(r"\b(?:if|when|while|whenever|until|unless|whether|that|which|who|after|before|once|each|every|any)\b"
                  r"[^.;:]*$", re.I)
STATE = re.compile(
    r"\b(?:is|are)(?: still| now| currently)? (?:in progress|under ?way|ongoing|being (?:built|written|moved|migrated|"
    r"converted))\b|\bcurrently\b|\bat the moment\b(?=[ ,.;]*(?:$|[.,;]))|\bas of (?:today|now|this writing)\b"
    r"|\b(?:today|right now|so far),? (?:\w+ ){0,2}\d+ (?:of|/|out of) \d+"
    r"|\b\d+ (?:of|out of) (?:the )?\d+ [^.;:]{0,40}\b(?:today|so far|right now)\b"
    r"|\b(?:is|are) not (?:yet )?(?:built|finished|landed|wired|done)(?: yet)?(?=[ ,.;]*(?:$|[.,;]))", re.I)
DATED = re.compile(r"\b20\d\d-\d\d(?:-\d\d)?\b")
NO_OBJECT = re.compile(r"^(?:Revert|Undo|Restore|Rebuild|Escalate|Reopen|Release|Drop|Cut|Remove|Delete|Repeat|Rerun) "
                       r"(?:if|when|unless|once|after|before|whenever)\b")
ELSEWHERE = re.compile(r"\b(?:see above|as above|the above|see below|the latter|the former)\b(?! (?:[a-z]+ )?[a-z]+s?\b"
                       r"(?<!is)(?<!are)(?<!was)(?<!has))", re.I)
SLASH = re.compile(r"(?<![\w/.~-])[A-Z]{1,2}/[A-Z]{1,2}(?![\w/])")
CODED = re.compile(r"(?<![\w/.#=+-])(?:[A-Z]{1,2}-?\d{1,3}[a-z]?|WP-\d+)(?![\w/%°-])")
CODED_OK = re.compile(r"^(?:P\d{2}|V\d|H[1-6]|A4|B\d{2}|S3|T\d|X\d|Q[1-4]|F\d{1,2}|C\d|GB\d*|UTF-?8|A/B|I/O|UI/UX|N/A|R/W|"
                      r"L/R|W/L|Y/N|E2E|PR|ID|SD|M\.?2|v\d)$")
PATHS = re.compile(r"^(?:\./)?(?:src|design|infrastructure|skills|\.claude|world)/[A-Za-z0-9_./-]+$")
GONE = re.compile(r"\b(?:gone|delet\w*|remov\w*|retired?|renam\w*|moved?|archiv\w*|history|never existed|no such|absent|"
                  r"does not exist|creat\w*|former\w*|old|output|untracked|writes?|written|generat\w*|will be|new)\b", re.I)
ITEM_ID = re.compile(r"(?<![\w/])(RIMM(?:ANDRAKE|ASTER)(?:_[A-Z0-9]+){3,})(?![\w*<…])(?!\.\.)")


def glossary(top=TOP):
    path = os.path.join(top, config()["glossary"])
    if not os.path.isfile(path):
        path = os.path.join(TOP, config()["glossary"])
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        raise CouldNotLook("cannot read the glossary (%s)" % e)


def retired_names(lex):
    """-> [(name, what to write instead)] from the glossary's `## Retired names` table."""
    m = re.search(r"(?ms)^## Retired names\n(.*?)(?=^## |\Z)", lex)
    return re.findall(r"(?m)^\| \*\*(.+?)\*\* \| (.+?) \|$", m.group(1)) if m else []


class Tree:
    """What exists: the paths of the checkout (or of HEAD, in a sparse clone) and the items of the ledger."""
    def __init__(self, top):
        self.top, self._items, self._seen = top, None, {}

    def path(self, p):
        if p not in self._seen:
            ok = os.path.exists(os.path.join(self.top, p))
            if not ok:
                r = subprocess.run(["git", "cat-file", "-e", "HEAD:" + p], cwd=self.top, capture_output=True, timeout=GIT_TIMEOUT_S)
                ok = r.returncode == 0
            self._seen[p] = ok
        return self._seen[p]

    def item(self, i):
        """True | False | None (no ledger here: cannot look)."""
        if self._items is None:
            d = os.path.join(self.top, "infrastructure", "state", "ledger", "events")
            ids = set()
            for f in sorted(os.listdir(d)) if os.path.isdir(d) else ():
                if f.endswith(".jsonl"):
                    with open(os.path.join(d, f), encoding="utf-8", errors="replace") as fh:
                        ids.update(re.findall(r"RIMM(?:ANDRAKE|ASTER)_[A-Z0-9_]+", fh.read()))
            self._items = ids
        return (i in self._items) if self._items else None


PART = r"[:;](?:\s|$)| [—–-] |, (?=(?:and|but|or|so|then|because|which|while|not)\b)"


def words_of(s, C):
    """The word counts of one sentence's parts: a quote and a code span are one word each, and words in parentheses are not
    counted (evidence). A colon, a semicolon, a dash and a comma before a joining word end a part; after a colon, so does
    each comma (a list). The repaired line of de63778138e0 is 28 words in two marked parts, and it reads plainly."""
    s = re.sub(r"\([^()]*\)", " ", s)
    s = re.sub(r"(?:Q|X)[qx\s]*[qx.!?]", " W ", s)
    head, colon, tail = s.partition(": ")
    parts = re.split(PART, head) + (re.split(PART + r"|, ", tail) if colon else [])
    return [len(C.WORD.findall(p)) for p in parts]


def program_faults(path, text, sents, tree, lex, door="publish"):
    RL, C = lint()
    cs, out, retired = chunks(text), [], retired_names(lex)
    brief = door in ("launch", "brief")

    def add(s, kind, term, repair):
        out.append({"file": path, "line": s["l0"], "kind": kind, "term": term.strip(), "repair": repair, "by": "program",
                    "sentence": s["raw"]})
    for s in sents:
        t, raw = s["mask"], s["raw"]
        here = "this sentence, or the first line of its section (%s)" % (("“%s”" % s["head"]) if s["head"] else path)
        sec = masked(section_text(cs, section_index(cs, s["l0"]), whole=brief))
        n = max(words_of(t, C) or [0])
        most = C.MAX_SENTENCE_WORDS if C.IMPERATIVE_HEAD.match(t) else MAX_DESCRIPTIVE_WORDS
        if n > most:
            add(s, "long-sentence", "%d words" % n, "split it: one idea, at most %d words" % most)
        heads = [c for c in re.split(r";\s", t) if C.IMPERATIVE_HEAD.match(c) and not re.match(r"\s*(?:never|do not|don't|avoid)\b", c, re.I)]
        if len(heads) > 1:
            add(s, "two-commands", "; ".join(h.strip()[:30] for h in heads), "write one sentence for each command")
        m = PRONOUN.match(t.lstrip("*_ \U0001F534\U0001F511⚠️⛔⭐"))
        if m:
            add(s, "pronoun", m.group(0), "write the noun that the sentence is about in place of the pronoun")
        for m in SHOULD.finditer(t):
            if not SHOULD_ASKED.search(t[:m.start()]):
                add(s, "should", m.group(0), "write the plain command, or write that the act is optional")
        m = DUTY.search(t)
        if m and not SHOULD_ASKED.search(t[:m.start()]) and not re.match(r"[^.;:]*\bby (?!hand\b|default\b|itself\b|name\b)", t[m.end():]):
            add(s, "duty-no-actor", m.group(0), "name who does the act, and make that actor the subject")
        m = STATE.search(t)
        if m and not DATED.search(t) and not WHEN.search(t[:m.start()]):
            add(s, "state", m.group(0), "point at what holds the state (an item id with `rimflow show <ID>`, a file, a command); state in prose goes false")
        m = NO_OBJECT.match(t)
        if m:
            add(s, "no-object", m.group(0), "name what the verb acts on")
        m = ELSEWHERE.search(t)
        if m:
            add(s, "look-elsewhere", m.group(0), "name the thing itself, or its path and § heading")
        for m in list(SLASH.finditer(t)) + list(CODED.finditer(t)):
            tok = m.group(0)
            d = re.compile(r"(?<![\w/])%s(?:\s*\(|\s*=|:|\s+[—–-] |\s+(?:is|are|means|names|stands for)\b)|\(%s\)|\*\*%s\*\*" % ((re.escape(tok),) * 3))
            if not CODED_OK.match(tok) and not d.search(sec) and not d.search(lex):
                add(s, "coded-name", tok, "say in plain words what %s is, in %s" % (tok, here))
        for name, instead in retired:
            m = re.search(r"\b%s\b" % re.escape(name), t, re.I)
            if m and not re.search(r"\bretired\b", t, re.I):
                add(s, "retired-name", m.group(0), "a retired name. %s" % instead)
        if not GONE.search(t):
            for span in re.findall(r"`([^`]+)`", raw):
                p = re.sub(r":\d+$", "", span.strip())
                if not PATHS.match(p):
                    continue
                q = p[2:] if p.startswith("./") else p
                q = q.rstrip("/").rstrip(".")
                if tree.path(q) or (brief and tree.path(os.path.dirname(q))):      # a brief names files that its run makes
                    continue
                closed = q.replace("state/items/", "state/items/closed/")
                add(s, "dead-path", span, "the path does not exist; write %s" % (
                    "`%s`" % closed if closed != q and tree.path(closed) else "the path that does, or say that the file is gone"))
        for i in ITEM_ID.findall(raw):
            if tree.item(i) is False:
                add(s, "dead-item", i, "the ledger holds no such item; write the id that it holds, or file it first")
    return out


# ---- what a model reads --------------------------------------------------------------------------------------------
def opening(text):
    """The file's title and first lines: at most 12, and none past its first section heading."""
    out = []
    for l in text.split("\n")[:12]:
        if out and l.startswith("## "):
            break
        out.append(l)
    return "\n".join(out)


def reader_prompt(path, text, sents, lex, whole=False):
    cs, by = chunks(text), {}
    for n, s in enumerate(sents, 1):
        by.setdefault(0 if whole else section_index(cs, s["l0"]), []).append("[%d] %s" % (n, s["raw"]))
    body = "\n\n".join("=== SECTION (context) ===\n%s\n=== SENTENCES TO CHECK ===\n%s" % (
        section_text(cs, i, whole), "\n".join(l)) for i, l in sorted(by.items()))
    with open(READER_BRIEF, encoding="utf-8") as f:
        p = f.read()
    return p.replace("{LEXICON}", lex).replace("{PATH}", path).replace("{OPENING}", opening(text)) \
            .replace("{BODY}", body)


def ask_model(prompt):
    """-> the model's answer text. One fresh call, no tools, no settings, an empty folder: it reads only the prompt."""
    with tempfile.TemporaryDirectory(prefix="rm-gprose-") as d:
        r = subprocess.run([CLAUDE, "-p", "--model", READER_MODEL, "--tools", "", "--setting-sources", "", "--strict-mcp-config",
                            "--no-session-persistence", "--output-format", "json", "--system-prompt",
                            "You check rule text for terms that a reader cannot resolve. You answer with one JSON object."],
                           input=prompt, capture_output=True, text=True, cwd=d, timeout=READER_TIMEOUT_S)
    if r.returncode != 0:
        raise OSError("claude exit %s: %s" % (r.returncode, (r.stderr or r.stdout).strip()))
    d = json.loads(r.stdout)
    if d.get("is_error"):
        raise OSError("claude: %s" % str(d.get("result")))
    return str(d.get("result") or "")


def reader_status():
    lint()      # puts rimflow on the path
    import refusal_contract as RC
    return RC.status(FAMILY)


def read_faults(path, text, sents, lex, ask, whole=False):
    """-> (faults, dropped, None) or (None, 0, why): what the model found on these sentences, bound to the line."""
    try:
        ans = ask(reader_prompt(path, text, sents, lex, whole))
        m = re.search(r"(?s)\{.*\}", ans or "")
        if not m:
            return None, 0, "the answer holds no JSON (%r)" % (ans or "")[:80]
        rows = json.loads(m.group(0)).get("faults")
        if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
            return None, 0, "the answer's `faults` is not a list of rows"
    except subprocess.TimeoutExpired:
        return None, 0, "no answer in %d s" % READER_TIMEOUT_S
    except (OSError, ValueError, AttributeError) as e:
        return None, 0, "%s: %s" % (type(e).__name__, str(e))
    out, dropped = [], 0
    for r in rows:
        n, term = r.get("n"), str(r.get("term") or "").strip()
        s = sents[n - 1] if isinstance(n, int) and 0 < n <= len(sents) else None
        bare = squash(re.sub(r"[`\"“”]", "", term))
        if not s or not bare or bare not in squash(re.sub(r"[`\"“”]", "", s["raw"])) \
                or r.get("kind") not in ("undefined", "synonym", "no-object"):
            dropped += 1
            continue
        out.append({"file": path, "line": s["l0"], "kind": r["kind"], "term": term, "by": "reader", "sentence": s["raw"],
                    "repair": "%s Say it in %s." % (str(r.get("why") or "").strip(), str(r.get("define_at") or "this sentence").strip().rstrip("."))})
    return out, dropped, None


def reader_wanted(env=None):
    env = os.environ if env is None else env
    return env.get("RM_GUIDING_PROSE_READER", "1") != "0" and bool(env.get("CLAUDECODE"))


# ---- one check -----------------------------------------------------------------------------------------------------
def check_text(path, text, olds, top=TOP, door="publish"):
    """The program half for one text -> {"faults", "sentences"}."""
    sents = changed_sentences(text, olds)
    return {"faults": program_faults(path, text, sents, Tree(top), glossary(top), door) if sents else [], "sentences": len(sents)}


def check_files(top, news, olds, door="publish", reader=None, status=None, sents_by=None):
    """news, olds: {path: text}. A sentence that any old text holds is old. `reader`: prompt -> answer, None = none.
    -> {"faults", "shown", "sentences", "files", "reader": {"status", "dropped"}}."""
    tree, lex, faults, shown, jobs, total = Tree(top), glossary(top), [], [], [], 0
    for p, text in sorted(news.items()):
        sents = (sents_by or {}).get(p)
        if sents is None:
            sents = changed_sentences(text, list(olds.values()))
        total += len(sents)
        if sents:
            faults += program_faults(p, text, sents, tree, lex, door)
            jobs.append((p, text, sents))
    rd = {"status": "not run", "dropped": 0, "calibration": None}
    if reader and jobs:
        rd["calibration"] = (status or reader_status)()
        with ThreadPoolExecutor(max_workers=4) as ex:
            got = list(ex.map(lambda j: read_faults(j[0], j[1], j[2], lex, reader, whole=door in ("launch", "brief")), jobs))
        bad = [why for f, _, why in got if f is None]
        rd["status"] = ("UNMEASURED: " + "; ".join(bad)) if bad else "read"
        rd["dropped"] = sum(d for _, d, _ in got)
        mine = [x for f, _, _ in got for x in (f or [])]
        mine = [x for x in mine if not any(x["file"] == y["file"] and x["line"] == y["line"] and (y["term"].lower() in x["term"].lower()
                                           or x["term"].lower() in y["term"].lower()) for y in faults)]
        if rd["calibration"] == "CALIBRATED":     # only a calibrated brief sends anything back (standing_rulings.md)
            faults += mine
        else:
            shown = mine
    order = lambda f: (f["file"], f["line"])      # noqa: E731
    return {"faults": sorted(faults, key=order), "shown": sorted(shown, key=order), "sentences": total,
            "files": sorted(news), "reader": rd, "door": door}


def line_of(f):
    return "  %s:%s [%s] %r in: %s\n      REPAIR: %s" % (f["file"], f["line"], f["kind"], f["term"], f["sentence"][:110], f["repair"])  # cut-ok: terminal display


def render(res, principal=None):
    """The text a writer reads; "" when there is nothing to say."""
    out, rd = [], res["reader"]
    done = "The brief is sent and the run has started." if res.get("door") == "launch" else "The landing is complete."
    if res["faults"]:
        head = "%d fault(s) in %d new sentence(s) of %s. Nothing was refused." % (
            len(res["faults"]), res["sentences"], ", ".join(res["files"]))
        out.append("GUIDING PROSE: " + (("NOTE (form, recorded for the %s): " % principal) if principal else "") + head + " " +
                   (done if res.get("door") in ("launch", "publish") else ""))
        out += [line_of(f) for f in res["faults"]]
        out.append("REPAIR in this run: %s A meaning that you cannot find: python3 src/RimMandrake/Utils/guiding_prose.py "
                   "unfindable --file F --line N --term T --question Q" % (
                       "correct the brief file; when a fault hides an act, write the correction as a note on the item."
                       if res.get("door") == "launch" else "edit those lines and go again."))
    if res["shown"]:
        out.append("GUIDING PROSE: shown only, the reader's brief is not calibrated (%s):" % rd["calibration"])
        out += [line_of(f) for f in res["shown"]]
    if rd["status"].startswith("UNMEASURED"):
        out.append("GUIDING PROSE: the model reader is %s. The program half ran." % rd["status"])
    return "\n".join(out)


def data_dir():
    d = os.environ.get("RM_GUIDING_PROSE_DIR")
    if not d:
        if RIMFLOW not in sys.path:
            sys.path.insert(0, RIMFLOW)
        import doorbell
        d = os.path.join(doorbell.state_dir(), "guiding_prose")
    os.makedirs(d, exist_ok=True)
    return d


def record(door, res, env=None, **more):
    """One row per run. A row that cannot be written never stops the writer; the row says what was read."""
    env = os.environ if env is None else env
    try:
        lint()
        import principal as P
        who = P.who(env)
    except Exception:  # noqa: BLE001  the mark is a note on a record, never a gate
        who = None
    row = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "t": now_s(), "door": door, "principal": who,
           "unit": env.get("RM_ROLE_UNIT") or None, "files": res["files"], "sentences": res["sentences"],
           "faults": res["faults"], "shown": res["shown"], "reader": res["reader"]}
    row.update(more)
    with open(os.path.join(data_dir(), "runs.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    return row


def rows():
    """Every run record. No file is a measured none (no run has recorded yet); a file that cannot be read raises."""
    p = os.path.join(data_dir(), "runs.jsonl")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


# ---- the two doors -------------------------------------------------------------------------------------------------
def git(top, *a):
    r = subprocess.run(["git", *a], cwd=top, capture_output=True, text=True, errors="replace", timeout=GIT_TIMEOUT_S)
    if r.returncode != 0:
        raise CouldNotLook("git %s failed: %s" % (" ".join(a[:2]), r.stderr.strip()))
    return r.stdout


def blob(top, rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)], cwd=top, capture_output=True, text=True, errors="replace",
                       timeout=GIT_TIMEOUT_S)
    return r.stdout if r.returncode == 0 else None


def range_texts(top, base, head):
    """-> ({path: new}, {path: old}) of the guiding prose that base..head changes. A left path's old text is an old text."""
    cfg = config()
    names = [p for p in git(top, "diff", "--name-only", "--no-renames", "-z", base, head).split("\0") if p and is_guiding(p, cfg)]
    news = {p: blob(top, head, p) for p in names}
    olds = {p: blob(top, base, p) for p in names}
    return {p: t for p, t in news.items() if t is not None}, {p: t for p, t in olds.items() if t is not None}


def after_publish(top, base, head, landed):
    """What ./publish prints after a landing: "" when it touched no guiding prose or no fault was found. Never raises."""
    if os.environ.get("RM_GUIDING_PROSE_CUT") == "publish":
        return ""
    if not (os.path.isfile(os.path.join(top, CONFIG_REL)) or os.environ.get("RM_GUIDING_PROSE_DIR")):
        return ""           # another repo, or a test's throwaway clone: not this project's guiding prose
    try:
        news, olds = range_texts(top, base, head)
        if not news:
            return ""
        n = int(git(top, "rev-list", "--count", "%s..%s" % (base, head)).strip() or 1)
        res = check_files(top, news, olds, "publish", ask_model if reader_wanted() else None)
        row = record("publish", res, landed=git(top, "rev-list", "-n", str(max(1, n)), landed).split())
        return render(res, row["principal"])
    except Exception as e:  # noqa: BLE001  the landing is done: a broken check says so and stops nothing
        return "GUIDING PROSE: UNMEASURED, the check did not run (%s: %s). The landing is complete." % (type(e).__name__, str(e)[:240])  # cut-ok: terminal display


def _sent_path():
    return os.path.join(data_dir(), "sent_brief_sentences.txt")


def _key(s):
    return hashlib.sha1(squash(s["raw"]).encode("utf-8")).hexdigest()[:16]


def check_brief(brief, door="launch", env=None, reader=None):
    """A brief's sentences that no earlier launch sent -> the check's result."""
    try:
        with open(_sent_path(), encoding="utf-8") as f:
            sent = set(f.read().split())
    except FileNotFoundError:
        sent = set()
    sents = [s for s in sentences(brief) if _key(s) not in sent]
    return check_files(TOP, {BRIEF_PATH: brief}, {}, door, reader or (ask_model if reader_wanted(env) else None),
                       sents_by={BRIEF_PATH: sents})


def after_launch(brief, item=None):
    """What `launch` adds to its text once the run has started. Never raises."""
    if os.environ.get("RM_GUIDING_PROSE_CUT") == "launch":
        return ""
    try:
        res = check_brief(brief)
        row = record("launch", res, item=item)
        with open(_sent_path(), "a", encoding="utf-8") as f:
            f.write("".join(_key(s) + "\n" for s in sentences(brief)))
        return render(res, row["principal"])
    except Exception as e:  # noqa: BLE001  the run has started: a broken check says so and stops nothing
        return "GUIDING PROSE: UNMEASURED, the check did not run (%s: %s). The run has started." % (type(e).__name__, str(e)[:240])  # cut-ok: terminal display


# ---- the one list of meanings that nobody finds --------------------------------------------------------------------
def _cli(argv):
    r = subprocess.run([sys.executable, os.path.join(RIMFLOW, "cli.py")] + argv, cwd=TOP, capture_output=True, text=True, timeout=21600)  # hang guard: a rimflow write that publishes takes 30-120 s # budget: class=publish
    return r.returncode, (r.stdout + r.stderr).strip()


def list_id(path, term):
    """The ledger name of one question: RIMMANDRAKE_DEFINE_<TERM>_IN_<FILE>_MEANING_NOT_FOUND, at most 64 characters (9 words)."""
    def w(t, n, k):
        return "_".join(re.findall(r"[A-Z0-9]+", t.upper())[:k])[:n].strip("_") or "TERM"
    stem = os.path.basename(os.path.dirname(path)) if os.path.basename(path) == "SKILL.md" else os.path.splitext(os.path.basename(path))[0]
    return "RIMMANDRAKE_DEFINE_%s_IN_%s_NOT_FOUND" % (w(term, 16, 2), w(stem, 14, 2))


def unfindable(path, line, term, question, runner=_cli, tree=None):
    """One question on the one list (the rimflow ledger): filed once for a term in a file, a note after that."""
    if not (question or "").strip() or not (term or "").strip():
        return 2, "unfindable: give the term and the exact question; an entry with no question can be answered by nobody"
    text = "UNFINDABLE MEANING %s:%s term %r. QUESTION: %s" % (path, line, term, " ".join(question.split()))
    i, seat = list_id(path, term), os.environ.get("RIMFLOW_SEAT") or os.environ.get("AGENT_SEAT") or "BENCH"
    if (tree or Tree(TOP)).item(i):
        argv = ["note", i, "--text", text]
    else:
        argv = ["file", i, "--for", "BENCH", "--kind", "owed", "--needs", "offline", "--title", text, "--caused-by", ITEM_OF_THIS_CHECK]
    rc, out = runner(argv + ["--seat", seat, "--why", "guiding_prose.py unfindable", "--publish"])
    return rc, "%s: %s" % (i, out.splitlines()[-1] if out else "")


# ---- does it still run? --------------------------------------------------------------------------------------------
PLANT = "# Planted\n\n- Give the item to the belt.\n"


def _publish_door(env):
    """A real publish.py landing of a planted rule file in a throwaway remote. -> "ok" or the cause."""
    with tempfile.TemporaryDirectory(prefix="rm-gprose-recheck-") as d:
        c, rel = os.path.join(d, "c"), "design/RimMandrake/debug_process.md"
        for cmd in (["init", "-q", "--bare", "-b", "main", "o.git"], ["clone", "-q", "o.git", "c"]):
            git(d, *cmd)
        for k, v in (("user.name", "recheck"), ("user.email", "recheck@example.invalid"), ("core.hooksPath", "/dev/null")):
            git(c, "config", k, v)
        os.makedirs(os.path.join(c, os.path.dirname(rel)))
        for body, msg in (("# Planted\n", "base"), (PLANT, None)):
            with open(os.path.join(c, rel), "w", encoding="utf-8") as f:
                f.write(body)
            if msg:
                git(c, "add", rel)
                git(c, "commit", "-qm", msg)
                git(c, "push", "-q", "origin", "HEAD:main")
        r = subprocess.run([sys.executable, os.path.join(HERE, "publish.py"), "-m", "planted", rel], cwd=c, capture_output=True,
                           text=True, env=env, timeout=DOOR_TIMEOUT_S)
        if r.returncode != 0 or "PUBLISHED " not in r.stdout:
            return "the planted landing did not land (exit %s: %s)" % (r.returncode, (r.stdout + r.stderr).strip())
        return "ok" if "retired-name" in r.stdout else "./publish landed a planted fault and returned nothing"


def _launch_door(env):
    """detached_helper.py's own main with the start itself replaced. -> "ok" or the cause."""
    code = ("import sys; sys.path.insert(0, %r); import detached_helper as D; D.launch = D.OWN_LAUNCH = lambda *a, **k: (0, 'started');"
            "sys.exit(D.main(['launch', '--seat', 'BENCH', '--item', 'PLANT_A_LAUNCH_RECHECK', '--budget-usd', '0', '--brief', %r]))"
            % (RIMFLOW, PLANT))
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, timeout=DOOR_TIMEOUT_S, cwd=TOP)
    if r.returncode != 0 or "started" not in r.stdout:
        return "the planted launch did not start (exit %s: %s)" % (r.returncode, (r.stdout + r.stderr).strip())
    return "ok" if "retired-name" in r.stdout else "a launch sent a planted fault and returned nothing"


def uncovered(top, since, rows):
    """-> [{"sha", "files", "subject"}]: each commit on origin/main since `since` that changed guiding prose and is in no
    run record (a landing that was not ./publish)."""
    cfg, out, have = config(), [], {s for r in rows for s in r.get("landed") or []}
    for rec in git(top, "log", "--since=@%d" % since, "--no-merges", "--format=%x01%H%x02%s", "--name-only", "origin/main").split("\x01")[1:]:
        head, _, names = rec.partition("\n")
        sha, _, subject = head.partition("\x02")
        files = sorted(p for p in names.split("\n") if p.strip() and is_guiding(p.strip(), cfg))
        if files and sha not in have:
            out.append({"sha": sha, "files": files, "subject": subject})
    return out


def recheck(write=True, coverage=True, env=None):
    with tempfile.TemporaryDirectory(prefix="rm-gprose-rows-") as d:
        e = dict(os.environ, RM_GUIDING_PROSE_DIR=d, RM_GUIDING_PROSE_READER="0", **(env or {}))
        e.pop("RM_PUBLISH_SKIP_TREE_CHECKS", None)
        res = {}
        for name, fn in (("publish_door", _publish_door), ("launch_door", _launch_door)):
            try:
                res[name] = fn(e)
            except (CouldNotLook, OSError, subprocess.SubprocessError) as x:
                res[name] = "could not look: %s: %s" % (type(x).__name__, str(x))
    res["cause"] = "; ".join("%s: %s" % (k, v) for k, v in res.items() if v != "ok")
    res["ok"] = not res["cause"]
    if coverage:
        try:
            rs = rows()
            first = min([r["t"] for r in rs if r.get("door") == "publish"] or [now_s()])
            res["landings_with_no_record"] = uncovered(TOP, max(first, now_s() - 2 * 86400), rs)
            res["runs"] = len(rs)
            res["faults_returned"] = sum(len(r.get("faults") or []) for r in rs)
        except (CouldNotLook, OSError, subprocess.SubprocessError, ValueError) as x:
            res["landings_with_no_record"] = "could not look: %s" % x
        res["reader"] = reader_status()
    res["at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if write:
        p = os.path.join(data_dir(), "recheck.json")
        with open(p + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1)
        if res["ok"]:
            os.replace(p + ".tmp", p)           # the promise's reading moves only while both doors live
        else:
            os.replace(p + ".tmp", os.path.join(data_dir(), "recheck_failed.json"))
    return res


# ---- the reader's planted cases ------------------------------------------------------------------------------------
def calibrate():
    import guiding_prose_calibration as GC
    return GC.main()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("check")
    a.add_argument("files", nargs="+")
    a.add_argument("--base")
    a = sub.add_parser("brief")
    a.add_argument("file")
    a = sub.add_parser("diff")
    a.add_argument("rev")
    a.add_argument("--base")
    a = sub.add_parser("unfindable")
    for k in ("--file", "--line", "--term", "--question"):
        a.add_argument(k, required=True)
    sub.add_parser("recheck")
    sub.add_parser("calibrate")
    args = ap.parse_args(argv)
    if args.cmd == "unfindable":
        rc, text = unfindable(args.file, args.line, args.term, args.question)
        print(text)
        return rc
    if args.cmd == "recheck":
        res = recheck()
        print(json.dumps(res, indent=1))
        return 0 if res["ok"] else 1
    if args.cmd == "calibrate":
        return calibrate()
    try:
        ask = ask_model if reader_wanted() else None
        if args.cmd == "diff":
            base = args.base or args.rev + "~1"
            news, olds = range_texts(TOP, base, args.rev)
            res = check_files(TOP, news, olds, "check", ask)
        elif args.cmd == "brief":
            with open(args.file, encoding="utf-8") as f:
                res = check_brief(f.read(), "brief")
        else:
            news, olds = {}, {}
            for p in args.files:
                with open(p, encoding="utf-8") as f:
                    news[os.path.relpath(os.path.abspath(p), TOP) if os.path.abspath(p).startswith(TOP) else p] = f.read()
                if args.base:
                    old = blob(TOP, args.base, os.path.relpath(os.path.abspath(p), TOP))
                    if old is not None:         # a file that the base does not hold is all new
                        olds[p] = old
            res = check_files(TOP, news, olds, "check", ask)
    except (CouldNotLook, OSError, UnicodeDecodeError) as e:
        print("GUIDING PROSE: UNMEASURED: %s" % e)
        return 3
    text = render(res)
    print(text or "GUIDING PROSE: no fault in %d new sentence(s); reader %s" % (res["sentences"], res["reader"]["status"]))
    return 1 if res["faults"] else 3 if res["reader"]["status"].startswith("UNMEASURED") else 0


if __name__ == "__main__":
    sys.exit(main())
