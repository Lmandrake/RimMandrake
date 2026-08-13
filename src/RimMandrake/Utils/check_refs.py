#!/usr/bin/env python3
"""check_refs.py — every "see X" in a doc is a machine-checkable claim. Check them.

Documents here cite each other constantly, and nothing verified the citations. In
one day: STRUCTURE.md pointed at a state file that does not exist, TODO.md cited a
worked example that never existed, infrastructure/state/queue/OPS.md cited line numbers in a file that
had shrunk by 400 lines, and a rule number moved to another file. All four are
mechanical checks. Same argument as src/RimMandrake/Utils/doc_budget.py: mechanical beats
disciplined.

    python3 src/RimMandrake/Utils/check_refs.py             # short report, exit 1 if BROKEN
    python3 src/RimMandrake/Utils/check_refs.py --all       # every finding
    python3 src/RimMandrake/Utils/check_refs.py --markdown  # infrastructure/output/REF_AUDIT.md body

WHAT IS CHECKED, over tracked *.md (minus .git, infrastructure/disposing/, infrastructure/output/,
vendor/mod_sources/):

  paths    repo-relative, bare basenames, Windows absolute, legacy file:///
  commits  7-40 hex in backticks, via git cat-file
  lines    foo.md:123 and "line 123" -- target file must have that many lines
  rules    "rule 6b", "§3a" -- the number must appear in the file named nearby
  skills   skills/<name>/ must be a real directory

TWO VERDICTS, and the split is the whole design:

  BROKEN      resolved with confidence, and the target is not there.
  UNVERIFIED  could not be resolved with confidence -- a path outside the repo,
              a command line, a bare script name, a game-side filename, or a
              sentence that is ABOUT the file being gone or not built yet.

A third bucket is counted but never listed: claims with nothing to resolve
against, such as a bare "§4" with no file named near it. There are hundreds.
Printing them would bury the twenty that matter.

False positives are the failure mode. A linter that cries wolf gets ignored,
which is worse than no linter, so every ambiguity resolves downward. There is
deliberately no --fix: this tool reports, humans edit.
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

# Scanned-file exclusions. Resolution still sees these trees; we just do not
# audit the prose inside them.
# infrastructure/output/ holds audits and options papers, which quote broken and superseded
# references on purpose -- the same reason infrastructure/disposing/ is skipped.
SKIP_SCAN = ("infrastructure/disposing/", "infrastructure/output/",
             "vendor/mod_sources/", ".git/")
# The report quotes broken references by design; auditing it would be a loop.
# Redundant while it lives under infrastructure/output/, kept so a move back stays safe.
SKIP_FILES = {"infrastructure/output/REF_AUDIT.md", "REF_AUDIT.md"}

# Extensions that make a token a path claim rather than prose. Only a bare
# `*.md` miss is BROKEN: a bare script or asset name is as often a tool living
# outside this tree (get-pip.py, image_gen.py) as a citation of one inside it.
EXTS = {"md", "py", "sh", "xml", "json", "cs", "log", "txt", "csv", "png",
        "jpg", "rws", "dll", "ps1", "yaml", "yml", "toml", "zip", "pdf",
        "skill", "patch", "cfg", "bat", "svg", "wav", "ogg"}

# RimWorld structural names. These name a KIND of file, at hundreds of paths
# outside this repo, so they are never a citation of one specific file.
GENERIC = {
    "About.xml", "ModsConfig.xml", "LoadFolders.xml", "Player.log",
    "Prefs.xml", "KeyPrefs.xml", "SKILL.md", "README.md", "CLAUDE.md",
    "settings.json", "settings.local.json", "package.json",
    "manifest.xml", "manifest.json", "index.md", "notes.md",
}
GENERIC_DIRS = {"Defs", "Patches", "Textures", "Sounds", "Languages",
                "Assemblies", "About", "Source", "Utils", "skills", "queue",
                "agents", "mods", "custom_patches", "runtime", "worldbuilding"}

# A line that is a command, not prose. Paths in it are usually illustrative.
CMD = re.compile(r"^\s*(?:[$#>]|python3?\b|git\b|bash\b|sh\b|ls\b|cd\b|grep\b|"
                 r"cat\b|stat\b|cp\b|mv\b|rm\b|find\b|sed\b|awk\b|echo\b|"
                 r"curl\b|wc\b|\./)")

FENCE = re.compile(r"^\s*(?:```|~~~)")
BACKTICK = re.compile(r"`([^`\n]{2,120})`")
URL_FILE = re.compile(r"file:///([^\s`\"'<>\]|]+)")
WIN_ABS = re.compile(r"\b([A-Za-z]:[\\/][^\s`\"'<>\])|]+)")
BARE_PATH = re.compile(r"(?<![\w/`.])([A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)+"
                       r"\.(?:" + "|".join(sorted(EXTS)) + r"))\b")
HASH = re.compile(r"`([0-9a-f]{7,40})`")
LINECITE = re.compile(r"([A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)*"
                      r"\.(?:md|py|xml|cs|json|sh|txt)):(\d+)(?:-(\d+))?")
PROSE_LINE = re.compile(r"\blines?\s+(\d+)\b", re.I)
RULE = re.compile(r"(?:§{1,2}\s?|\b(?:interaction\s+)?rules?\s+)"
                  r"(\d+(?:\.\d+)?[A-Za-z]?)", re.I)
MDNAME = re.compile(r"([A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)*\.md)")
SKILLREF = re.compile(r"^skills/([A-Za-z0-9_.\-]+)")
PLACEHOLDER = re.compile(r"[<>{}*?|%$]")

# Two sentence shapes make a dangling name CORRECT, and flagging them is the
# loudest kind of crying wolf: prose about a file that is gone on purpose, and
# prose about a file that does not exist YET.
SOFT_CONTEXT = re.compile(
    r"\b(delet|remov|missing|gone|never exist|never been|does not exist|"
    r"doesn't exist|no longer|retire|stale|supersed|dissolv|renam|fold(ed)? into|"
    r"moved to|was moved|formerly|previously|used to|when this was written|"
    r"absent|dangling|broken|purge|dead|"
    r"propos|candidate|planned|not yet|to be (written|added|built|created)|"
    r"would|should (be|live|carry|hold)|will (be|live|carry|hold)|keep a|creat)",
    re.I)

# How far from a rule number a filename may sit and still be its attribution.
RULE_NEAR = 40
# Above this, "§N" is a section/line marker in a long doc, not a numbered rule.
RULE_MAX = 100


def sh(args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True).stdout


class Repo:
    """Filesystem knowledge, built lazily -- the full walk costs ~18s on this mount."""

    def __init__(self):
        self.tracked = set(sh(["git", "ls-files"]).split("\n")) - {""}
        self.tracked |= set(
            sh(["git", "ls-files", "--others", "--exclude-standard"]).split("\n")) - {""}
        self.index = {}
        for p in self.tracked:
            self.index.setdefault(os.path.basename(p), []).append(p)
        self.walked = False
        self.lines = {}
        self.roots = {n for n in os.listdir(ROOT)
                      if os.path.isdir(os.path.join(ROOT, n))}

    def deep(self):
        if self.walked:
            return
        self.walked = True
        for r, d, fs in os.walk(ROOT):
            d[:] = [x for x in d if x not in (".git", "__pycache__", "node_modules")]
            rel = os.path.relpath(r, ROOT)
            for f in fs:
                p = f if rel == "." else os.path.join(rel, f).replace("\\", "/")
                hits = self.index.setdefault(f, [])
                if p not in hits:       # tracked files are already indexed
                    hits.append(p)

    def exists(self, rel):
        return os.path.exists(os.path.join(ROOT, rel))

    def find_basename(self, name):
        hits = self.index.get(name)
        if hits:
            return hits
        self.deep()
        return self.index.get(name, [])

    def find_ci(self, name):
        """`rimmaster.md` when the file is runtime/RimMaster.md. Resolves on
        Windows, not here, and not on GitHub -- worth naming exactly."""
        self.deep()
        low = name.lower()
        for k, v in self.index.items():
            if k.lower() == low:
                return v
        return []

    def suffix_of_real(self, tok):
        """`Jawa_Patches/Patches/x.xml` is a real file cited by its tail, not a
        dangling one. Abbreviating a long path is normal prose, not an error."""
        tail = "/" + tok
        for p in self.find_basename(os.path.basename(tok)):
            if p == tok or p.endswith(tail):
                return True
        return False

    def linecount(self, rel):
        if rel not in self.lines:
            try:
                with open(os.path.join(ROOT, rel), "rb") as fh:
                    self.lines[rel] = fh.read().count(b"\n") + 1
            except OSError:
                self.lines[rel] = None
        return self.lines[rel]


def unquote(s):
    return re.sub(r"%([0-9A-Fa-f]{2})", lambda m: chr(int(m.group(1), 16)), s)


def win_to_posix(p):
    """D:\\Luke\\... or D:/Luke/... -> a path this machine can stat."""
    p = unquote(p).replace("\\", "/")
    m = re.match(r"^([A-Za-z]):/(.*)$", p)
    if not m:
        return None
    drive, rest = m.group(1).lower(), m.group(2)
    return "/mnt/%s/%s" % (drive, rest)


def clean(tok):
    tok = tok.strip().rstrip(".,;:!")
    tok = tok.split("#")[0]
    while tok.endswith(")") and tok.count("(") < tok.count(")"):
        tok = tok[:-1]
    return tok


class Audit:
    def __init__(self, repo):
        self.repo = repo
        self.findings = []          # (owner, lineno, kind, text, status, why)
        self.seen = set()
        self.checked = {}           # kind -> how many claims were resolvable
        self.skipped = {}           # why -> how many were not even addressable

    def tally(self, kind):
        self.checked[kind] = self.checked.get(kind, 0) + 1

    def skip(self, why):
        self.skipped[why] = self.skipped.get(why, 0) + 1

    def add(self, owner, ln, kind, text, status, why):
        key = (owner, kind, text, why)
        if key in self.seen:
            return
        self.seen.add(key)
        self.findings.append((owner, ln, kind, text, status, why))

    # ---- paths ----------------------------------------------------------
    def path(self, owner, ln, tok, cmdline, soft=False):
        tok = clean(tok)
        if not tok or PLACEHOLDER.search(tok) or tok.startswith(("http", "www.")):
            return
        if tok.startswith(("~", "/", "./", "../")) or "…" in tok or "..." in tok:
            return              # home-relative, posix-absolute or elided: not ours
        base = os.path.basename(tok.rstrip("/"))
        if base.startswith("."):
            return              # ".md", ".gitignore" -- an extension, not a file

        # absolute / drive-qualified
        if re.match(r"^[A-Za-z]:[\\/]", tok) or tok.startswith("file:///"):
            raw = tok[len("file:///"):] if tok.startswith("file:///") else tok
            posix = win_to_posix(raw)
            if not posix:
                return
            inside = posix.lower().startswith(ROOT.lower() + "/")
            self.tally("path")
            if os.path.exists(posix):
                return
            if inside and not soft:
                self.add(owner, ln, "path", tok, "BROKEN", "no such file in repo")
            else:
                self.add(owner, ln, "path", tok, "UNVERIFIED",
                         "outside the repo; machine-specific"
                         if not inside else "may be illustrative")
            return

        if tok.endswith("/"):
            d = tok.rstrip("/")
            self.tally("path")
            if self.repo.exists(d) or self.repo.suffix_of_real(d):
                return
            if "/" not in d or d.split("/")[0] not in self.repo.roots:
                return          # bare or foreign folder name: unresolvable, not wrong
            self.add(owner, ln, "path", tok,
                     "UNVERIFIED" if soft else "BROKEN", "directory not found")
            return

        ext = tok.rsplit(".", 1)[-1].lower() if "." in base else ""
        if ext not in EXTS:
            return
        if base in GENERIC and "/" not in tok:
            return
        self.tally("path")

        if "/" in tok:
            if self.repo.exists(tok) or self.repo.suffix_of_real(tok):
                return
            here = os.path.dirname(owner)
            if here and self.repo.exists(os.path.normpath(os.path.join(here, tok))):
                return
            if tok.split("/")[0] not in self.repo.roots:
                return          # a tail of some other tree; nothing to resolve against
            if cmdline or soft:
                self.add(owner, ln, "path", tok, "UNVERIFIED",
                         "may be illustrative")
                return
            self.add(owner, ln, "path", tok, "BROKEN", "no such file")
            return

        # bare basename
        if self.repo.find_basename(base):
            return
        ci = self.repo.find_ci(base) if ext == "md" else []
        if len(ci) == 1:
            self.add(owner, ln, "path", tok,
                     "UNVERIFIED" if soft else "BROKEN",
                     "case mismatch; file is %s" % ci[0])
            return
        if cmdline or soft:
            self.add(owner, ln, "path", tok, "UNVERIFIED", "may be illustrative")
        elif ext == "md":
            self.add(owner, ln, "path", tok, "BROKEN", "no file of this name in repo")
        else:
            # A bare script or asset name is as often a tool that lives outside
            # this tree as a citation of one inside it.
            self.add(owner, ln, "path", tok, "UNVERIFIED",
                     "not in repo; may live outside it")

    # ---- commits --------------------------------------------------------
    def commits(self, pending):
        if not pending:
            return
        shas = sorted({s for (_, _, s) in pending})
        inp = "".join("%s^{commit}\n" % s for s in shas)
        out = subprocess.run(["git", "cat-file", "--batch-check"], cwd=ROOT,
                             input=inp, capture_output=True, text=True).stdout
        bad = set()
        for sha, line in zip(shas, out.strip().split("\n")):
            if "missing" in line or "ambiguous" in line:
                bad.add(sha)
        self.checked["commit"] = len(shas)
        for owner, ln, sha in pending:
            if sha in bad:
                self.add(owner, ln, "commit", sha, "BROKEN", "unknown to git")

    # ---- line citations -------------------------------------------------
    def linecite(self, owner, ln, target, num):
        base = os.path.basename(target)
        if base in GENERIC and "/" not in target:
            return
        rel = target if self.repo.exists(target) else None
        if rel is None:
            hits = self.repo.find_basename(base)
            if len(hits) != 1:
                return          # unresolved or ambiguous target -- the path
            rel = hits[0]       # check already owns the "missing file" verdict
        n = self.repo.linecount(rel)
        if n is None:
            return
        self.tally("line")
        if num > n:
            self.add(owner, ln, "line", "%s:%d" % (target, num), "BROKEN",
                     "file has %d lines" % n)

    # ---- rules ----------------------------------------------------------
    def rule(self, owner, ln, num, line, pos, soft=False):
        """Attribution decides confidence. A filename immediately LEFT of the rule
        number is the citation ("agents_def.md rule 9"); one to the right is a
        table cell or the next clause, so a miss there is only UNVERIFIED."""
        left = MDNAME.findall(line[max(0, pos - RULE_NEAR):pos])
        right = MDNAME.findall(line[pos:pos + RULE_NEAR])
        target, side = (left[-1], "L") if left else \
                       ((right[0], "R") if right else (None, None))
        if target is None:
            # 400+ of these. Itemising an unaddressable claim IS crying wolf,
            # so they are counted and named in one line, not listed.
            self.skip("rule/section number with no file named within "
                      "%d chars" % RULE_NEAR)
            return
        rel = target if self.repo.exists(target) else None
        if rel is None:
            hits = self.repo.find_basename(os.path.basename(target))
            if len(hits) != 1:
                return          # the path check already owns "target missing"
            rel = hits[0]
        try:
            with open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace") as fh:
                body = fh.read()
        except OSError:
            return
        label = "%s %s" % (target, num)
        self.tally("rule")

        if float(re.sub(r"[A-Za-z]", "", num)) >= RULE_MAX:
            # Three digits is a section/line marker in a long doc, not a rule.
            n = self.repo.linecount(rel)
            if n is not None and int(float(re.sub(r"[A-Za-z]", "", num))) > n:
                self.add(owner, ln, "rule", label,
                         "UNVERIFIED" if soft or side == "R" else "BROKEN",
                         "section marker past end of file (%d lines)" % n)
            return

        if re.search(r"(?<![\d.])%s(?![\d])" % re.escape(num), body):
            return
        self.add(owner, ln, "rule", label,
                 "UNVERIFIED" if soft or side == "R" else "BROKEN",
                 "%s never mentions %s" % (target, num))

    # ---- skills ---------------------------------------------------------
    def skill(self, owner, ln, name, soft=False):
        if PLACEHOLDER.search(name) or name.startswith("."):
            return
        self.tally("skill")
        if os.path.exists(os.path.join(ROOT, "skills", name)):
            return
        self.add(owner, ln, "skill", "skills/%s" % name,
                 "UNVERIFIED" if soft else "BROKEN", "no such skill directory")


def scan(audit, repo, rel):
    try:
        with open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace") as fh:
            lines = fh.read().split("\n")
    except OSError:
        return []
    pending_hashes = []
    fenced = False
    for i, line in enumerate(lines, 1):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        cmdline = bool(CMD.match(line))
        soft = bool(SOFT_CONTEXT.search(line))

        for m in URL_FILE.finditer(line):
            audit.path(rel, i, "file:///" + m.group(1), cmdline, soft)
        for m in WIN_ABS.finditer(line):
            audit.path(rel, i, m.group(1), cmdline, soft)

        ticks = [m.group(1) for m in BACKTICK.finditer(line)]
        for t in ticks:
            t = t.strip()
            if " " in t or "\t" in t:
                continue
            if LINECITE.fullmatch(clean(t)):
                continue
            audit.path(rel, i, t, cmdline, soft)
            sm = SKILLREF.match(clean(t))
            if sm:
                audit.skill(rel, i, sm.group(1), soft)
        stripped = BACKTICK.sub(" ", line)
        for m in BARE_PATH.finditer(stripped):
            audit.path(rel, i, m.group(1), cmdline, soft)

        for m in HASH.finditer(line):
            s = m.group(1)
            if not re.search(r"[0-9]", s) or not re.search(r"[a-f]", s):
                continue        # workshop IDs are decimal; "defaced" has no digit
            if len(s) > 12 and len(s) != 40:
                continue
            pending_hashes.append((rel, i, s))

        for m in LINECITE.finditer(line):
            audit.linecite(rel, i, m.group(1), int(m.group(2)))
        for m in PROSE_LINE.finditer(line):
            names = MDNAME.findall(line[:m.start()])
            if names:
                audit.linecite(rel, i, names[-1], int(m.group(1)))

        for m in RULE.finditer(line):
            audit.rule(rel, i, m.group(1), line, m.start(), soft)
    return pending_hashes


def collect():
    repo = Repo()
    audit = Audit(repo)
    docs = [p for p in sorted(repo.tracked)
            if p.endswith(".md") and not p.startswith(SKIP_SCAN)
            and p not in SKIP_FILES]
    hashes = []
    for d in docs:
        hashes += scan(audit, repo, d)
    audit.commits(hashes)
    return audit, len(docs)


def group(findings, status):
    out = {}
    for f in findings:
        if f[4] == status:
            out.setdefault(f[0], []).append(f)
    return out


BUDGET = 26          # default output stays readable in one screen


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--all", action="store_true", help="every finding, not a summary")
    ap.add_argument("--markdown", action="store_true",
                    help="emit infrastructure/output/REF_AUDIT.md body")
    args = ap.parse_args()

    audit, ndocs = collect()
    broken = group(audit.findings, "BROKEN")
    unver = group(audit.findings, "UNVERIFIED")
    nb = sum(len(v) for v in broken.values())
    nu = sum(len(v) for v in unver.values())
    checked = ", ".join("%d %s" % (n, k)
                        for k, n in sorted(audit.checked.items()))

    if args.markdown:
        out = ["# REF_AUDIT", "",
               "Generated: `python3 Utils\\check_refs.py --markdown > "
               "output\\REF_AUDIT.md`. Do not hand-edit; fix the citation and "
               "rerun.", "",
               "**%d BROKEN, %d UNVERIFIED** across %d tracked `*.md`."
               % (nb, nu, ndocs), "",
               "BROKEN — resolved, target absent. Fix these.  ",
               "UNVERIFIED — not resolvable with confidence (outside the repo, "
               "a command line, a game-side name). Not defects by default.", "",
               "Claims resolved: %s." % checked, ""]
        for why, n in sorted(audit.skipped.items()):
            out += ["Not addressable, so not listed: %d occurrences of a %s."
                    % (n, why), ""]
        for title, grp, n in (("BROKEN", broken, nb), ("UNVERIFIED", unver, nu)):
            out += ["## %s (%d)" % (title, n), ""]
            if not grp:
                out += ["None.", ""]
                continue
            for owner in sorted(grp):
                out += ["### `%s`" % owner.replace("/", "\\"), ""]
                for _, ln, kind, text, _, why in sorted(grp[owner],
                                                        key=lambda f: f[1]):
                    out.append("- L%d %s `%s` — %s" % (ln, kind, text, why))
                out.append("")
        print("\n".join(out))
        return 1 if nb else 0

    lines = ["check_refs: %d BROKEN, %d UNVERIFIED across %d docs (%s)"
             % (nb, nu, ndocs, checked)]
    order = [("BROKEN", broken)] + ([("UNVERIFIED", unver)] if args.all else [])
    total = nb + (nu if args.all else 0)
    shown = 0
    stop = False
    for title, grp in order:
        for owner in sorted(grp):
            head = owner if title == "BROKEN" else owner + "  [unverified]"
            block = ["  L%-4d %-6s %s — %s" % (f[1], f[2], f[3], f[5])
                     for f in sorted(grp[owner], key=lambda f: f[1])]
            if not args.all and len(lines) + 1 + len(block) > BUDGET:
                stop = True
                break
            lines.append(head)
            lines += block
            shown += len(block)
        if stop:
            break
    if stop:
        lines.append("  ... +%d more (--all)" % (total - shown))
    if not nb:
        lines.append("No broken references.")
    if nu and not args.all:
        lines.append("%d UNVERIFIED not shown; --all or --markdown." % nu)
    print("\n".join(lines))
    return 1 if nb else 0


if __name__ == "__main__":
    sys.exit(main())
