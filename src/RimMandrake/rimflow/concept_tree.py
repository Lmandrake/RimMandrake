#!/usr/bin/env python3
"""concept_tree.py - The Designer's tree (the Concept agent, renamed by card 2026-11-01; `authored_by: concept` stays, it is schema data): writer, door lint (Gate A) and the gate Relentless refuses a mod on.

Format: design/RimMandrake/relentless_tree_schema_2026-11-01.md. Meaning: concept_agent_design_2026-11-01.md §5-§8, §11.

  write    <dir> --draft d.json [--dry-walk]   stamp hashes, check the shape, write tree.json (clears any signature)
  lint     <dir>                               Gate A: sheet + tree + floor. Exit 0 PASS, 1 REFUSED
  gate     <dir>                               lint plus: not a dry walk, root VALIDATED at its hash, the coverage judge's
                                               signature on this tree hash AND as its ledger event, every waiver in OWNER.jsonl
  sign     <dir> --by CoverageJudge [--item ID] the coverage signature: a `rimflow note` on the concept's item (stage.json
                                               `item`, or --item) from inside a coverage judge run (coverage_judge.py), then
                                               the stamp in tree.json. Refuses a dry walk, a lint failure, and any other writer
  askcheck <dir> "question"                    does this question re-raise a waiver? Exit 1 when it may; with no
                                               tree.json yet it prints HISTORY_NOT_CHECKED (exit 0), never "clear"
  hash     <dir>                               tree_hash

Gate B, the Cold Reader exam, is not here: this program checks form, and a perfectly formed tree can be wrong. The
coverage judge's signature comes after the exam (stage 5), or after `exam_waived` in his words. The judge is a fresh
Opus run that did not make the tree (coverage_judge.py; the role launcher starts it before a Designer stage-5 run).
The Arbiter role that used to sign is retired (owner 2026-11-05, CONCEPT_LOCK_UNBLOCK_SIGNER_NEVER_CALLED); a signature
it already recorded (`Arbiter`, rm-role-arbiter-<n>) is still accepted by the gate, never written again.

The coverage stamp in tree.json is a copy any writer can forge, so the gate also wants the ledger event
(CONCEPT_COVERAGE_HARDEN_SIGNED_ON_LEDGER): a `note` whose role_unit is a coverage judge run (rm-coverage-judge-<n>) and
whose text names this concept, tree hash and sheet hash. The ledger is append-only and committed, so a forged signature
is an attributable line in git, not a silent edit; RM_ROLE_UNIT is still an environment variable, and a writer who sets
it by hand forges this too.

What a program cannot do, said plainly: "names an observer" is a word list, the pruning check proves a citation is
present and not that it is good, and askcheck cannot catch a rewording, so a fresh reviewer reads the question log too.
"""
import argparse
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
FLOOR_FILE = "concept_floor.json"
OWNER_SHARD = "infrastructure/state/ledger/events/OWNER.jsonl"
LEDGER_DIR = "infrastructure/state/ledger"
SIGNER = "CoverageJudge"
JUDGE_UNIT = re.compile(r"rm-coverage-judge-[0-9]+")     # coverage_judge.py's unit name; always fullmatch
# the retired Arbiter's signatures already on the ledger (FlowWorks, 2026-11-05) stay valid; nothing writes one again
LEGACY_SIGNERS = {"Arbiter": re.compile(r"rm-role-arbiter-[0-9]+")}
SIGNER_UNITS = dict(LEGACY_SIGNERS, **{SIGNER: JUDGE_UNIT})
SIGN_MARK = "coverage-signed"
DRY_DIR = "_dry_walk"       # a dry walk lives only here, so nobody takes it for a real concept
SCHEMA = 1

TOP_KEYS = {"schema_version", "subject", "kind", "authored_by", "root_ref", "root_state", "root_hash", "coverage", "floor",
            "exam_waived", "waived", "advisory", "leaves", "dry_walk"}
DRAFT_KEYS = {"subject", "kind", "root_ref", "floor_off", "exam_waived", "waived", "advisory", "leaves"}
LEAF_REQ = ("id", "by", "root", "leaf_kind", "clause_kind", "experience", "scenario", "false_pass", "red", "tier_proposed",
            "owner_part")
LEAF_OPT = ("bundle", "scenario_informed_by", "needs_instrument", "oracle_proposed", "tier_reason", "cannot_show",
            "wall_expect_h")
LEAF_KINDS = ("experience", "constraint", "instrument", "walk")
SLUG = re.compile(r"[a-z][a-z0-9_]*")     # always fullmatch: `$` would let a trailing newline through
OBSERVER = re.compile(r"\b(player|colonist|colonists|viewer|observer|pawn|pawns|he|you|screen|log|reader|tester|the save)\b",
                      re.I)
CONSTRAINT = re.compile(r"^\s*(at most|at least|under|over|no more than|<=?|>=?)?\s*\d+(\.\d+)?\s*(ms|s|min|mb|gb|kb|tps|fps|%|"
                        r"per [a-z]+|[a-z]+/[a-z]+)(?![A-Za-z0-9]).*\bon\s+\S+", re.I)
WALK_NEEDS = {"reload": r"\breload(s|ed|ing)?\b", "repeat": r"\brepeat(s|ed|ing)?\b", "second order": r"\b(second|another|different|other|opposite|reverse|reversed)\s+order\b|\border\s+reversed\b|\breverse\s+the\s+order\b"}
TOOL_ROOT = "tool"
# a `red` that names no broken version (relentless_improvement_loop_2026-11-03.md: "a test that catches no nameable broken
# version is decoration"): the whole field, lowercased and stripped of punctuation, is one of these. Always fullmatch.
NO_RED = re.compile(r"(none|n ?a|nil|null|tbd|tba|todo|unknown|nothing|no(ne)? broken version|not applicable|"
                    r"cannot name one|can ?not be named|unnameable|nameless|same|see above|ditto|\?+)")
STOP = set("the a an of to in on and or it is at for by this that with how what does do not be are was you your his he "
           "me my i we as if".split())


def txt(v):
    """The one blank-field rule every check uses: text is a str with something in it after strip. Anything else - None,
    a number, a list, a dict, whitespace - is blank, so a field that must be text can never pass by being another type."""
    return v.strip() if isinstance(v, str) else ""


def lst(v):
    """A list field read as a list; anything else reads as empty (and is refused where the list is required)."""
    return v if isinstance(v, list) else []


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(obj):
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()


def tree_hash(tree):
    return sha({k: v for k, v in tree.items() if k != "coverage"})


def leaf_hash(leaf):
    return sha(leaf)


def floor_path():
    return os.path.join(HERE, FLOOR_FILE)


def load_floor(path=None):
    with open(path or floor_path(), encoding="utf-8") as f:
        floor = json.load(f)
    return floor, sha(floor)


def flags(floor):
    """What every report carries until he answers: never a pass, never a refusal."""
    return ["FLAG %s: %s" % (ln["id"], ln.get("flag") or "open") for ln in floor["lines"] if ln["class"] == "open_owner"]


# ---------------------------------------------------------------- sheet

CORE = re.compile(r"\[\s*core\b[^\]]*\]", re.I)      # `[core]`, `[ Core ]`, `[core:x]`: any spelling a reader sees as core


def visible(line):
    """Roughly what a Markdown viewer shows: entities decoded, compatibility forms folded, invisible format characters
    and emphasis/escape marks dropped. Used where a tag must be seen as the reader sees it, never to rewrite the sheet."""
    s = unicodedata.normalize("NFKC", html.unescape(line))
    return re.sub(r"[*_~`\\]", "", "".join(c for c in s if unicodedata.category(c) != "Cf"))


# Markup that renders as other text: inline HTML, an entity, an inline or reference link (or its definition), a bracket
# opened inside a bracket. A sheet is plain, so
# a line holding any of these is refused anywhere, headings included, rather than rendered and guessed at.
_NOT_PLAIN = re.compile(r"<[A-Za-z/!?]|&#?[A-Za-z0-9]+;|\]\(|\]\[|^\s*\[[^\]]*\]:|\[[^\]]*\[")


def not_plain(line):
    """NOT_PLAIN on the line as written and as rendered (fullwidth brackets fold to `[` only after NFKC), plus the
    allow-list that ends the hunt for spellings: rendered, every bracket pair is balanced, never nested, and holds only
    ASCII letters, digits, spaces and `:-`. So a reader can only see `[core]` where `visible()` holds `[core]` too."""
    if _NOT_PLAIN.search(line) or _NOT_PLAIN.search(visible(line)):
        return True
    v = visible(line)
    if v.count("[") != v.count("]"):
        return True
    groups = re.findall(r"\[([^\[\]]*)\]", v)
    return len(groups) != v.count("[") or any(not re.fullmatch(r"[A-Za-z0-9 :-]*", g) for g in groups)
UNREAD = "\0unread headings"      # parse_sheet's own key, never a heading name
SECTIONS = ("his words", "does", "does not", "waived", "open", "delegated", "pruning")
OPTIONAL_SECTIONS = ("later",)      # "Not now": v2, not in the tree. A dry walk adds `root` (its stand-in north star)
BULLET = r"^\s*(?:[-*+]|[0-9]+[.)])"      # an unordered or an ordered Markdown bullet
TAG = re.compile(BULLET + r"\s*\[(leaf|floor|waived|advisory|core)(?::([A-Za-z0-9_]+))?\]\s*(.*)$")


def parse_sheet(path):
    """-> {section: [raw non-empty lines]}. Headings are `## <name>`; a heading may carry a parenthesis after the name.
    The sheet is plain bullets, so a line this parser could read differently from a Markdown viewer is refused, never
    guessed at (UNREAD): a code fence of any indent (Markdown would hide or show headings inside it), a setext underline
    or rule line, inline HTML, an entity, a link or a nested bracket (NOT_PLAIN), a bracket tag holding a non-ASCII character, any heading-like line that is not `## <name>` (the `# ` title before the first section
    excepted), or a heading holding a `[` tag.
    Lines before the first heading are
    kept under "" so that no line escapes a check."""
    out, cur = {"": []}, ""
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^##\s+([^#(]+?)\s*(\(.*\))?\s*$", line)
            if m and ("[" in visible(line) or not_plain(line)):    # a heading's note is dropped: no tag may hide there
                out.setdefault(UNREAD, []).append(line.rstrip("\n"))
            if m:
                cur = m.group(1).strip().lower()
                out.setdefault(cur, [])
            elif line.strip():
                if (re.match(r"^\s*(`{3,}|~{3,})", line)                     # a code fence
                        or re.match(r"^\s{0,3}(=+|-{2,})\s*$", line)              # a setext underline (or a rule)
                        or not_plain(line)                                  # HTML, entity, link, nested bracket
                        or any(ord(c) > 127 for b in re.findall(r"\[[^\]]*\]", visible(line)) for c in b)  # homoglyph tag
                        or (re.match(r"^\s{0,3}#{1,6}(\s|$)", line) and not (cur == "" and re.match(r"^# \S", line)))):
                    out.setdefault(UNREAD, []).append(line.rstrip("\n"))
                out[cur].append(line.rstrip("\n"))
    return out


def sheet_errors(sheet, tree, floor=None):
    errs = []
    for s in SECTIONS:
        if s not in sheet:
            errs.append("sheet: no `## %s` section" % s)
    known = ("",) + SECTIONS + OPTIONAL_SECTIONS + (("root",) if tree.get("dry_walk") is True else ())
    for line in sheet.get(UNREAD, []):
        errs.append("sheet: not plain bullets (a fence, rule, HTML, entity, link, nested bracket, a non-ASCII or heading tag, "
                    "or a heading other than "
                    "`## <section>` and the `# ` title): %s" % line.strip()[:80])
    for s in sheet:     # an unknown section is unchecked text: a [core] question could sit there unseen
        if s == UNREAD:
            continue
        if s not in known:
            errs.append("sheet: `## %s` is no section of the sheet" % s)
        elif s != "open":
            for line in sheet[s]:
                if CORE.search(visible(line)):
                    errs.append("sheet: a [core] line outside `## open`: %s" % line.strip()[:80])
    if not sheet.get("his words"):
        errs.append("sheet: `his words` is empty")
    leaves = {x.get("id"): x for x in lst(tree.get("leaves")) if isinstance(x, dict) and isinstance(x.get("id"), str)}
    waived = {w.get("id") for w in lst(tree.get("waived")) if isinstance(w, dict) and isinstance(w.get("id"), str)}
    floor_ids = {ln["id"] for ln in (floor or load_floor()[0])["lines"]}
    named = set()
    for sec, allowed in (("does", ("leaf", "floor", "waived", "advisory")), ("does not", ("leaf", "floor", "waived"))):
        for line in sheet.get(sec, []):
            if not re.match(BULLET + r"(\s|\[)", line):    # every promise maps: prose here would be an unmapped one
                errs.append("sheet: `%s` holds a line that is not a bullet: %s" % (sec, line.strip()[:80]))
                continue
            m = TAG.match(line)
            if not m or m.group(1) not in allowed:
                errs.append("sheet: `%s` line maps to nothing (%s): %s" % (sec, "|".join(allowed), line.strip()[:80]))
                continue
            tag, ref = m.group(1), m.group(2)
            if not txt(m.group(3)):
                errs.append("sheet: `%s` line says nothing after its tag: %s" % (sec, line.strip()[:80]))
            if tag == "leaf":
                if ref not in leaves:
                    errs.append("sheet: `%s` line names no such leaf: %s" % (sec, ref))
                else:
                    named.add(ref)
                    if sec == "does not" and not txt(leaves[ref].get("cannot_show")):
                        errs.append("sheet: `does not` leaf %s has no cannot_show" % ref)
            elif tag == "floor" and ref not in floor_ids:
                errs.append("sheet: no floor line %s" % ref)
            elif tag == "waived" and ref not in waived:
                errs.append("sheet: no waiver %s" % ref)
    for line in sheet.get("open", []):     # fails shut: `[core]` anywhere on an open line blocks, whatever the bullet
        if CORE.search(visible(line)):
            errs.append("sheet: a core line is still open: %s" % line.strip()[:80])
    for lid, leaf in leaves.items():
        structural = leaf.get("leaf_kind") in ("walk", "instrument")
        if lid not in named and not structural and leaf.get("by") != "setter_sweep":
            errs.append("orphan leaf: %s is on no `does`/`does not` line" % lid)
    pruned = {}
    for line in sheet.get("pruning", []):
        m = re.match(BULLET + r"\s*`?([a-z][a-z0-9_]*)`?\s*:\s*(.*)$", line)
        if m:
            pruned[m.group(1)] = txt(m.group(2))
    for lid, leaf in leaves.items():
        if leaf.get("leaf_kind") != "instrument" and not pruned.get(lid):
            errs.append("pruning: leaf %s has no answer to \"would you reject the mod on this alone?\"" % lid)
    for lid in pruned:
        if lid not in leaves:
            errs.append("pruning: names no such leaf: %s" % lid)
    return errs


# ---------------------------------------------------------------- tree

def leaf_errors(x, kind, tiers, root_ids):
    lid = x.get("id", "?")
    errs = []
    e = lambda why: errs.append("leaf %s: %s" % (lid, why))     # noqa: E731
    texts = ("experience", "scenario", "red", "tier_proposed", "owner_part", "oracle_proposed", "cannot_show",
             "needs_instrument", "tier_reason", "by", "leaf_kind", "clause_kind")
    for k in LEAF_REQ:
        v = x.get(k)
        if v is None or (isinstance(v, (str, list, dict)) and not (txt(v) if isinstance(v, str) else v)):
            e("%s missing" % k)
    for k in texts:
        if x.get(k) is not None and not isinstance(x[k], str):
            e("%s must be text" % k)
    if not isinstance(x.get("scenario_informed_by", []), list):
        e("scenario_informed_by is a list")
    for k in x:
        if k not in LEAF_REQ and k not in LEAF_OPT:
            e("field %s is not the tree's (Setter's go in binding.json, budget in budget.json)" % k)
    if not (isinstance(lid, str) and SLUG.fullmatch(lid)):
        e("id is not a slug")
    if x.get("by") not in ("concept", "filer", "setter_sweep"):
        e("by %r" % x.get("by"))
    if x.get("by") == "setter_sweep" and kind != "tool":
        e("a setter_sweep leaf belongs to a tooling goal only")
    if x.get("by") == "setter_sweep" and x.get("clause_kind") != "preserve":
        e("a setter_sweep leaf only preserves (the Setter adds no change)")
    if x.get("leaf_kind") not in LEAF_KINDS:
        e("leaf_kind %r" % x.get("leaf_kind"))
    if x.get("clause_kind") not in ("change", "preserve"):
        e("clause_kind %r" % x.get("clause_kind"))
    text = txt(x.get("experience"))
    if x.get("leaf_kind") == "constraint":
        if not CONSTRAINT.match(text):
            e("a constraint reads `<limit> <unit> on <test machine>`, got: %s" % text[:60])
    elif text and not OBSERVER.search(text):
        e("experience names no observer: %s" % text[:60])
    red = re.sub(r"[^a-z0-9? ]+", " ", txt(x.get("red")).lower()).strip()
    if txt(x.get("red")) and (not red or NO_RED.fullmatch(re.sub(r"\s+", " ", red))):
        e("red names no broken version (%r): a leaf that catches none is decoration, cut it" % txt(x.get("red"))[:40])
    elif red and red == re.sub(r"[^a-z0-9? ]+", " ", txt(x.get("experience")).lower()).strip():
        e("red repeats the experience: name the broken mod it catches, not the working one")
    if not lst(x.get("false_pass")) or not all(txt(w) for w in x["false_pass"]):
        e("false_pass must list named wrong worlds")
    tier = x.get("tier_proposed")
    if tier and tier not in tiers:
        e("tier_proposed %r not in %s" % (tier, ", ".join(tiers)))
    if tier and tier != "offline" and not txt(x.get("tier_reason")):
        e("tier %s needs tier_reason" % tier)
    if not (txt(x.get("oracle_proposed")) or txt(x.get("cannot_show"))):
        e("no oracle_proposed and no cannot_show")
    op = txt(x.get("owner_part"))
    if op and op != "no" and not re.match(r"^yes:\s*\S", op):
        e("owner_part is `no` or `yes: <what he looks at>`")
    roots = x.get("root")
    if not isinstance(roots, list):
        e("root is a list of ids")
    elif kind == "tool":
        if roots != [TOOL_ROOT]:
            e("a tooling leaf's root is [\"tool\"]")
    else:
        for r in roots:
            if not isinstance(r, str) or r not in root_ids:
                e("root id %s is not in the north star" % r)
    words = " ".join(txt(x.get(k)) for k in ("experience", "scenario"))
    if not txt(x.get("cannot_show")) and re.search(r"\b(worldgen|world generation|world gen)\b", words, re.I):
        e("needs worldgen: refused by standing ruling")
    if tier and tier != "offline" and not re.match(r"^yes:\s*\S", op) and re.search(r"\b(flight|flyer|flying|takes? off)\b", words, re.I):
        e("a flyer's flight is never live-tested without him: refused by standing ruling")
    return errs


def shape_errors(tree, root_ids, floor, floor_hash):
    errs = []
    for k in tree:
        if k not in TOP_KEYS:
            errs.append("field %s is not in the schema" % k)
    if tree.get("schema_version") != SCHEMA:
        errs.append("schema_version %r" % tree.get("schema_version"))
    kind = tree.get("kind")
    if kind not in ("mod", "tool"):
        errs.append("kind %r" % kind)
    if not txt(tree.get("subject")):
        errs.append("subject missing")
    au = tree.get("authored_by")
    if not (au == "concept" or (isinstance(au, str) and re.fullmatch(r"filer:\s*\S.*", au, re.S))):
        errs.append("authored_by %r" % au)
    if tree.get("root_state") not in ("VALIDATED", "DRAFT", "none"):
        errs.append("root_state %r" % tree.get("root_state"))
    fl = tree.get("floor") if tree.get("floor") is not None else {}
    if not isinstance(fl, dict):
        return errs + ["floor is not an object"]
    if fl.get("off") is not None and not (isinstance(fl["off"], list) and all(isinstance(o, dict) for o in fl["off"])):
        return errs + ["floor.off is a list of objects"]
    if tree.get("waived") is not None and not (isinstance(tree["waived"], list)
                                               and all(isinstance(w, dict) for w in tree["waived"])):
        return errs + ["waived is a list of objects"]
    adv = tree.get("advisory")
    if adv is not None and not (isinstance(adv, list) and all(txt(a) for a in adv)):
        errs.append("advisory is a list of non-blank lines")
    if fl.get("ref") != FLOOR_FILE:
        errs.append("floor.ref %r" % fl.get("ref"))
    if fl.get("hash") != floor_hash:
        errs.append("floor.hash is not the current floor's")
    by_id = {ln["id"]: ln for ln in floor["lines"]}
    dry = tree.get("dry_walk") is True
    for o in lst(fl.get("off")):
        ln = by_id.get(o.get("line")) if isinstance(o.get("line"), str) else None
        if ln is None:
            errs.append("floor.off: no line %r" % o.get("line"))
        elif not ln["waivable"]:
            errs.append("floor.off: %s cannot be turned off here" % o.get("line"))
        if not (txt(o.get("words")) and txt(o.get("ref"))):
            errs.append("floor.off %s: needs his words and a ref (a Conductor per-ruling event is a valid ref)" % o.get("line"))
    ex = tree.get("exam_waived")
    if ex is not None and not (isinstance(ex, dict) and txt(ex.get("words")) and txt(ex.get("ref"))):
        errs.append("exam_waived needs his words and a ref (a Conductor per-ruling event is a valid ref)")
    if not all(isinstance(w.get("id"), str) for w in lst(tree.get("waived"))):
        return errs + ["a waiver id is text"]
    seen_w = set()
    for w in lst(tree.get("waived")):
        if not all(txt(w.get(k)) for k in ("id", "scope", "date", "ref")):
            errs.append("waiver %s: id, scope, date, ref all required" % w.get("id"))
        if w.get("id") in seen_w:
            errs.append("waiver id twice: %s" % w.get("id"))
        seen_w.add(w.get("id"))
        real = isinstance(w.get("ref"), str) and re.fullmatch(r"OWNER:[0-9]+", w["ref"])
        if not dry and not real:
            errs.append("waiver %s: ref must be OWNER:<tsn>, his event" % w.get("id"))
        if dry and not (w.get("stand_in") is True and isinstance(w.get("ref"), str)
                        and re.fullmatch(r"dry_walk:\S+", w["ref"])):
            errs.append("waiver %s: on a dry walk it is marked stand_in, ref dry_walk:<round>" % w.get("id"))
        if not dry and "stand_in" in w:
            errs.append("waiver %s: a stand_in line in a real tree" % w.get("id"))
    if "dry_walk" in tree and not dry:
        errs.append("dry_walk is true or absent")
    leaves = tree.get("leaves")
    if not isinstance(leaves, list) or not leaves:
        return errs + ["no leaves"]
    if not all(isinstance(x, dict) for x in leaves):
        return errs + ["a leaf is not an object"]
    if not all(isinstance(x.get("id"), str) for x in leaves):
        return errs + ["a leaf id is text"]
    ids = [x.get("id") for x in leaves]
    for d in sorted({i for i in ids if ids.count(i) > 1}, key=str):
        errs.append("leaf id twice: %s" % d)
    instruments = {x.get("id") for x in leaves if x.get("leaf_kind") == "instrument"}
    for x in leaves:
        errs += leaf_errors(x, kind, floor["tiers"], root_ids)
        ni = x.get("needs_instrument")
        if ni and isinstance(ni, str) and ni not in instruments:
            errs.append("leaf %s: needs_instrument %s is no instrument leaf" % (x.get("id"), ni))
        if x.get("id") in seen_w:
            errs.append("leaf %s shares an id with a waiver: a waived line gets no leaf" % x.get("id"))
    walks = [x for x in leaves if x.get("leaf_kind") == "walk"]
    covered = {r for x in leaves if isinstance(x.get("root"), list) for r in x["root"] if isinstance(r, str)}
    for r in sorted(root_ids - covered):
        errs.append("north star line %s is on no leaf" % r)
    if kind == "mod" and len(walks) != 1:
        errs.append("a mod has exactly one walk leaf, found %d" % len(walks))
    if kind == "tool" and walks:
        errs.append("a tooling goal has no walk leaf")
    for x in walks:
        s = txt(x.get("scenario"))
        for name, rx in WALK_NEEDS.items():
            if not re.search(rx, s, re.I):
                errs.append("walk leaf: scenario lacks the %s" % name)
    for x in leaves:
        if x.get("leaf_kind") == "instrument" and not any(y.get("needs_instrument") == x.get("id") for y in leaves):
            errs.append("orphan instrument leaf: nothing depends on %s" % x.get("id"))
    return errs


# ---------------------------------------------------------------- the root

def walk_root(repo, ref):
    """-> (state, current hash, ids, why) for a `<path>#north-star` reference, through modcheck's own parser."""
    rel = txt(ref).split("#")[0]
    path = os.path.join(repo, rel)
    if not rel or not os.path.isfile(path):
        return "none", None, set(), "root_ref names no file: %r" % (ref,)
    if not os.path.realpath(path).startswith(os.path.realpath(repo) + os.sep):
        return "none", None, set(), "root_ref leaves the repo: %r" % (ref,)
    utils = os.path.normpath(os.path.join(HERE, "..", "Utils"))
    if utils not in sys.path:
        sys.path.insert(0, utils)
    from modcheck import northstar as NS
    p = NS.parse(path)
    return p["state"], p["current_hash"] or None, set(p["must_show"]) | set(p["cannot_show"]), p.get("reason")


def root_ids_for(repo, tree, sheet):
    if tree.get("kind") == "tool":
        return set()
    if tree.get("dry_walk") is True:     # no walk file is written for a stand-in: its root is the sheet's, labelled
        ids = set()
        for line in (sheet or {}).get("root", []):
            m = re.match(r"^\s*-\s*`?([a-z][a-z0-9_]*)`?\s*:", line)
            if m:
                ids.add(m.group(1))
        return ids
    return walk_root(repo, tree.get("root_ref"))[2]


# ---------------------------------------------------------------- the two gates

def load(d):
    """tree.json, parsed. ValueError (bad UTF-8, bad JSON, or text no hash can encode, e.g. a lone surrogate) for the
    caller to report as "does not parse"; FileNotFoundError when there is none."""
    with open(os.path.join(d, "tree.json"), encoding="utf-8") as f:
        try:
            tree = json.load(f)
            canon(tree).encode("utf-8")
        except RecursionError:
            raise ValueError("nested too deep") from None
    return tree


def lint(d, repo=REPO, floor_file=None):
    """Gate A. -> (errors, flags)."""
    floor, fh = load_floor(floor_file)
    try:
        tree = load(d)
    except FileNotFoundError:
        return ["no tree.json in %s" % d], flags(floor)
    except ValueError as e:
        return ["tree.json does not parse: %s" % e], flags(floor)
    except OSError as e:
        return ["tree.json cannot be read: %s" % e], flags(floor)
    if not isinstance(tree, dict):
        return ["tree.json is not an object"], flags(floor)
    sheet, errs = None, []
    if tree.get("kind") == "mod":
        sp = os.path.join(d, "sheet.md")
        if not os.path.isfile(sp):
            errs.append("no sheet.md")
        else:
            try:
                sheet = parse_sheet(sp)
                with open(sp, encoding="utf-8") as f:
                    first = f.readline()
            except (OSError, ValueError) as e:
                return errs + ["sheet.md cannot be read: %s" % e], flags(floor)
            errs += sheet_errors(sheet, tree, floor)
            if tree.get("dry_walk") is True and "DRY WALK" not in first:
                errs.append("a dry walk's sheet starts with a DRY WALK line")
    errs += shape_errors(tree, root_ids_for(repo, tree, sheet), floor, fh)
    in_dry = DRY_DIR in os.path.normpath(os.path.abspath(d)).casefold().split(os.sep)
    if (tree.get("dry_walk") is True) != in_dry:
        errs.append("a dry walk lives under %s/ and nothing else does" % DRY_DIR)
    return errs, flags(floor)


_ORIGIN_SHARD = {}


def origin_shard(repo):
    """OWNER.jsonl as origin/main has it in `repo`'s git, as text, or None (not a clone's top level, no origin/main,
    or git failed). DESIGNER_TURNS_FIX_LEFT_ON_THE_DOORSTEP: the Dispatcher judged a Designer run-now from ~/rm/dispatch
    while that clone was behind origin, and refused WAITING_OWNER with his answer already published. An owner event on
    origin is his word whether or not this working tree has pulled it yet. Cached per clone, keyed on origin/main's sha."""
    try:
        r = subprocess.run(["git", "-C", repo, "rev-parse", "--show-toplevel", "origin/main"], capture_output=True,
                           text=True, timeout=20)
        top, sha = (r.stdout.split() + ["", ""])[:2] if r.returncode == 0 else ("", "")
        if not sha or os.path.realpath(top) != os.path.realpath(repo):   # a temp dir inside another clone is not it
            return None
        key = os.path.realpath(repo)
        if (_ORIGIN_SHARD.get(key) or ("",))[0] != sha:          # one entry per clone: its latest origin/main only
            g = subprocess.run(["git", "-C", repo, "show", "%s:%s" % (sha, OWNER_SHARD)], capture_output=True,
                               timeout=60)
            _ORIGIN_SHARD[key] = (sha, g.stdout.decode("utf-8", "replace") if g.returncode == 0 else None)
        return _ORIGIN_SHARD[key][1]
    except (OSError, subprocess.SubprocessError):
        return None


def owner_lines(*repos):
    """-> every OWNER.jsonl line any of `repos` holds, in its working tree or on its origin/main, each once (the shard
    is append-only, so the union is the truest copy), or None when no copy is readable at all."""
    seen, out, read = set(), [], False
    for repo in dict.fromkeys(r for r in repos if r):
        texts = []
        try:
            with open(os.path.join(repo, OWNER_SHARD), encoding="utf-8", errors="replace") as f:
                texts.append(f.read())
        except OSError:
            pass
        texts.append(origin_shard(repo))
        for t in texts:
            if t is None:
                continue
            read = True
            for ln in t.splitlines():
                if ln.strip() and ln not in seen:
                    seen.add(ln)
                    out.append(ln)
    return out if read else None


def owner_events(repo, *more):
    out = {}
    for line in owner_lines(repo, *more) or []:       # a bad byte spoils its line only
        try:
            ev = json.loads(line)
        except (ValueError, RecursionError):
            continue
        if isinstance(ev, dict) and ev.get("tsn"):
            out[str(ev["tsn"])] = ev
    return out


def squash(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def in_words(scope, text):
    """Whole words only: "art" is not in "start", and an empty scope is in nothing."""
    s = squash(scope)
    return bool(s) and " %s " % s in " %s " % squash(text)


def his_words_problem(ev, ref, words):
    """Why `words` are not on the owner event `ref`, or None. A per-ruling event's words are its text."""
    m = re.fullmatch(r"OWNER:([0-9]+)", ref) if isinstance(ref, str) else None
    e = ev.get(m.group(1)) if m else None
    if e is None:
        return "ref finds no event in OWNER.jsonl"
    said = str(e.get("ownerSaid") or "")
    if isinstance(e.get("perRuling"), str) and e["perRuling"].strip():
        said += " " + str(e.get("text") or "")
    if not txt(words):
        return "no words to find on that event"
    return None if in_words(words, said) else "not his words on that event"


def sheet_hash(d):
    """A signature covers what he reads, so it binds the sheet too. Line ends do not count; a tool tree has no sheet."""
    try:
        with open(os.path.join(d, "sheet.md"), "rb") as f:
            return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()
    except OSError:
        return None


def concept_rel(d, repo):
    return os.path.relpath(os.path.realpath(d), os.path.realpath(repo)).replace(os.sep, "/")


def signature_text(d, repo, tree):
    """The one line the signer's ledger note says; the gate wants it byte for byte."""
    return "%s concept=%s tree=%s sheet=%s" % (SIGN_MARK, concept_rel(d, repo), tree_hash(tree), sheet_hash(d) or "none")


def ledger_files(repo):
    """The files model.read() merges: the frozen events.jsonl and the per-seat shards (and rolled months) in events/.
    Nothing else under the ledger dir counts, so a stray ledger/scratch.jsonl signs nothing (GPT review 2026-11-04)."""
    root = os.path.join(repo, LEDGER_DIR)
    shards = os.path.join(root, "events")
    try:
        names = sorted(n for n in os.listdir(shards) if n.endswith(".jsonl"))
    except OSError:
        names = []
    return [os.path.join(root, "events.jsonl")] + [os.path.join(shards, n) for n in names]


def ledger_signatures(repo):
    """Every coverage-signed note on the ledger. A bad line spoils itself only."""
    out = []
    for p in ledger_files(repo):
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                for line in f:
                    if SIGN_MARK not in line:
                        continue
                    try:
                        ev = json.loads(line)
                    except (ValueError, RecursionError):
                        continue
                    if isinstance(ev, dict) and ev.get("event") == "note" and \
                            str(ev.get("text") or "").startswith(SIGN_MARK + " "):
                        out.append(ev)
        except OSError:
            continue
    return out


def ledger_signature_problem(d, repo, tree, signer=SIGNER):
    """Why the ledger holds no `signer` signature for this tree and sheet, or None."""
    want, alls = signature_text(d, repo, tree), ledger_signatures(repo)
    evs = [e for e in alls if str(e.get("text")) == want]
    if not evs:
        here = [e for e in alls if (" concept=%s " % concept_rel(d, repo)) in str(e.get("text"))]
        return "the ledger signature is on another tree or sheet" if here else "no coverage signature on the ledger"
    unit_re = SIGNER_UNITS.get(signer, JUDGE_UNIT)
    if not any(isinstance(e.get("role_unit"), str) and unit_re.fullmatch(e["role_unit"]) for e in evs):
        return "the ledger signature was not written by a %s run (role_unit %s)" % (signer, 
            ", ".join(sorted({str(e.get("role_unit")) for e in evs})))
    return None


def coverage_problem(d, repo, tree):
    """Why this tree carries no valid coverage signature (stamp and ledger event), or None."""
    cov = tree.get("coverage") if isinstance(tree.get("coverage"), dict) else {}
    if cov.get("signed_by") not in SIGNER_UNITS:
        return "no coverage signature"
    if cov.get("tree_hash") != tree_hash(tree):
        return "the signature is on another tree hash"
    if tree.get("kind") == "mod" and cov.get("sheet_hash") != sheet_hash(d):
        return "the signature is on another sheet"
    return ledger_signature_problem(d, repo, tree, cov["signed_by"])


def gate(d, repo=REPO, floor_file=None):
    """What Relentless asks. -> (refusals, flags). Lint plus what only a finished, signed, real tree has."""
    errs, fl = lint(d, repo, floor_file)
    if errs and errs[0].startswith(("no tree.json", "tree.json")):
        return errs, fl
    tree = load(d)
    if tree.get("dry_walk") is True:
        errs.append("a dry walk is never handed to a worker")
    if tree.get("kind") == "mod":
        state, cur, _ids, why = walk_root(repo, tree.get("root_ref"))
        if state != "VALIDATED":
            errs.append("root is not VALIDATED: %s" % (why or state))
        elif tree.get("root_hash") != cur or tree.get("root_state") != "VALIDATED":
            errs.append("tree cites a root hash that is not the walk's")
    why = coverage_problem(d, repo, tree)
    if why:
        errs.append(why)
    ev = owner_events(repo)
    for w in [w for w in lst(tree.get("waived")) if isinstance(w, dict)]:
        why = his_words_problem(ev, w.get("ref"), w.get("scope"))
        if why:
            errs.append("waiver %s: %s" % (w.get("id"), why))
    fl2 = tree.get("floor") if isinstance(tree.get("floor"), dict) else {}
    for o in [o for o in lst(fl2.get("off")) if isinstance(o, dict)]:
        why = his_words_problem(ev, o.get("ref"), o.get("words"))
        if why:
            errs.append("floor.off %s: %s" % (o.get("line"), why))
    ex = tree.get("exam_waived")
    if isinstance(ex, dict) and ex:
        why = his_words_problem(ev, ex.get("ref"), ex.get("words"))
        if why:
            errs.append("exam_waived: %s" % why)
    return errs, fl


def item_file_text(repo, item):
    """The item's body. A mod whose body cannot be read cites no tree, so it is refused: this door fails shut."""
    try:
        with open(os.path.join(repo, "infrastructure/state/items", item + ".md"), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


# A cite is a whole token: it starts after whitespace or opening punctuation and ends at whitespace, closing punctuation or
# a sentence's full stop, so `tree.json.bak`, `tree.json~` and `x/design/concepts/...` are not cites of a tree.
TREE_CITE = re.compile(r"(?<![^\s`'\"(\[<])design/concepts/[A-Za-z0-9_./-]+/tree\.json(?=$|[\s`'\")\]>,;:]|\.(?:\s|$))",
                       re.I | re.M)


def relentless_refusal(repo, item, kind, text):
    """Why Relentless may not take this item, or None. A mod, or anything citing a concept tree, needs a passing gate.
    Every other item passes untouched: the tooling half of intake is RA_S05_INTAKE_ENFORCE_TREE_FIRST's."""
    cites = sorted(set(TREE_CITE.findall(text or "")))
    if kind != "mod" and not cites:
        return None
    if not cites:
        return "%s is a mod with no tree: `## verify` cites no design/concepts/<Mod>/tree.json" % item
    errs = []
    for cite in cites:     # every citation: one good tree in a comment does not vouch for the rest
        d = os.path.join(repo, os.path.dirname(cite))
        # realpath: a symlink or junction leaves as surely as `..` does; a cite in another case fails shut on Linux
        if not os.path.realpath(d).startswith(os.path.realpath(os.path.join(repo, "design/concepts")) + os.sep):
            errs.append("%s: leaves design/concepts" % cite)
            continue
        try:
            errs += gate(d, repo)[0]
            if kind == "mod" and load(d).get("kind") != "mod":
                errs.append("%s is not a mod's tree" % cite)
        except Exception as e:  # noqa: BLE001  a gate that cannot read refuses: this door fails shut
            errs.append("unreadable: %s: %s" % (type(e).__name__, e))
    if errs:
        return "%s: tree not well defined (%d): %s" % (item, len(errs), "; ".join(errs[:4]))
    return None


# ---------------------------------------------------------------- writer

def build(draft, repo=REPO, dry=False):
    """A draft that is not a JSON object, or carries a key the draft does not have, raises ValueError."""
    if not isinstance(draft, dict):
        raise ValueError("draft: not a JSON object")
    canon(draft).encode("utf-8")     # a lone surrogate raises here, before any file is touched
    bad = sorted(set(draft) - DRAFT_KEYS)
    if bad:
        raise ValueError("draft: unknown keys %s" % ", ".join(bad))
    floor, fh = load_floor()
    state, cur, _ids, _why = ("none", None, None, None) if dry or draft.get("kind") == "tool" \
        else walk_root(repo, draft.get("root_ref"))
    tree = {"schema_version": SCHEMA, "subject": draft.get("subject"), "kind": draft.get("kind"), "authored_by": "concept",
            "root_ref": draft.get("root_ref"), "root_state": state, "root_hash": cur if state == "VALIDATED" else None,
            "coverage": None, "floor": {"ref": FLOOR_FILE, "hash": fh, "off": draft.get("floor_off") or []},
            "exam_waived": draft.get("exam_waived"), "waived": draft.get("waived") or [],
            "advisory": draft.get("advisory") or [], "leaves": []}
    if dry:
        tree["dry_walk"] = True
    raw = draft.get("leaves")
    if not isinstance(raw, list):     # shape_errors says "no leaves"
        return tree
    for x in raw:
        if not isinstance(x, dict):   # carried as is: shape_errors says "a leaf is not an object"
            tree["leaves"].append(x)
            continue
        leaf = {k: x.get(k) for k in LEAF_OPT}
        leaf.update(x)
        leaf.setdefault("by", "concept")
        leaf.setdefault("clause_kind", "change")
        leaf.setdefault("owner_part", "no")
        leaf["scenario_informed_by"] = leaf.get("scenario_informed_by") or []
        tree["leaves"].append(leaf)
    return tree


def write(d, draft, repo=REPO, dry=False):
    """-> errors. Nothing is written while the shape is wrong; a rewrite always voids the signature."""
    sp = os.path.join(d, "sheet.md")
    sheet = parse_sheet(sp) if os.path.isfile(sp) else None
    tree = build(draft, repo, dry)
    floor, fh = load_floor()
    errs = shape_errors(tree, root_ids_for(repo, tree, sheet), floor, fh)
    if errs:
        return errs
    os.makedirs(d, exist_ok=True)
    put(d, tree)
    return []


def put(d, tree):
    """tree.json is replaced whole or not at all."""
    tmp = os.path.join(d, ".tree.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=1, ensure_ascii=False, sort_keys=False)
        f.write("\n")
    os.replace(tmp, os.path.join(d, "tree.json"))


def stage_item(d):
    """The concept's ledger item, from designer_stage's stage.json, or None."""
    try:
        with open(os.path.join(d, "stage.json"), encoding="utf-8") as f:
            st = json.load(f)
    except (OSError, ValueError, RecursionError):
        return None
    it = st.get("item") if isinstance(st, dict) else None
    return it if isinstance(it, str) and it.strip() else None


def rimflow_note(repo, item, text):
    """The ledger write, through rimflow (the only writer). -> error text or None."""
    import subprocess
    cli = os.path.join(repo, "src/RimMandrake/rimflow/cli.py")
    try:
        r = subprocess.run([sys.executable, cli, "note", item, "--text", text], cwd=repo, capture_output=True,
                           text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return "rimflow note failed: %s" % e
    if r.returncode != 0:
        return "rimflow note refused (exit %d): %s" % (r.returncode, (r.stderr or r.stdout).strip()[-300:])
    return None


def sign(d, by, repo=REPO, at=None, item=None, emit=None):
    """The ledger event first, then the stamp: a failed ledger write leaves tree.json unsigned."""
    if by != SIGNER:
        return ["only the coverage judge (%s) signs coverage" % SIGNER]
    unit = os.environ.get("RM_ROLE_UNIT", "")
    if not JUDGE_UNIT.fullmatch(unit):
        return ["sign runs inside a coverage judge run (RM_ROLE_UNIT rm-coverage-judge-<n>), not %r" % unit[:60]]
    errs, _fl = lint(d, repo)
    if errs:
        return errs
    tree = load(d)
    if tree.get("dry_walk") is True:
        return ["a dry walk is never signed"]
    item = item or stage_item(d)
    if not item:
        return ["no item to sign on: stage.json names none and no --item was given"]
    import time
    tree["coverage"] = {"signed_by": SIGNER, "at": at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "tree_hash": tree_hash(tree), "sheet_hash": sheet_hash(d), "ledger_item": item}
    why = (emit or rimflow_note)(repo, item, signature_text(d, repo, tree))
    if why:
        return [why]
    put(d, tree)
    return []


def askcheck(tree, question):
    """Waivers a question may re-raise. A word overlap: it catches a repeat, never a rewording."""
    q = set(squash(question).split()) - STOP
    hits = []
    for w in [w for w in lst(tree.get("waived")) if isinstance(w, dict)]:
        s = set(squash(txt(w.get("scope"))).split()) - STOP
        if s and len(q & s) >= min(len(s), max(2, (len(s) + 1) // 2)):
            hits.append(str(w.get("id")))
    return hits


def report(errs, fl, name):
    for x in fl:
        print(x)
    for e in errs:
        print("  - %s" % e)
    print("%s: %s" % (name, "PASS" if not errs else "REFUSED (%d)" % len(errs)))
    return 0 if not errs else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("write", "lint", "gate", "sign", "askcheck", "hash"):
        p = sub.add_parser(name)
        p.add_argument("dir")
        if name == "write":
            p.add_argument("--draft", required=True)
            p.add_argument("--dry-walk", action="store_true")
        if name == "sign":
            p.add_argument("--by", required=True)
            p.add_argument("--item")
        if name == "askcheck":
            p.add_argument("question")
    a = ap.parse_args(argv)
    if a.cmd == "write":
        try:
            with open(a.draft, encoding="utf-8") as f:
                draft = json.load(f)
            errs = write(a.dir, draft, dry=a.dry_walk)
        except RecursionError:
            errs = ["draft %s: nested too deep" % a.draft]
        except (OSError, ValueError) as e:
            errs = ["draft %s: %s" % (a.draft, e)]
        return report(errs, flags(load_floor()[0]), "write")
    if a.cmd == "lint":
        return report(*lint(a.dir), "lint (Gate A)")
    if a.cmd == "gate":
        return report(*gate(a.dir), "gate")
    if a.cmd == "sign":
        return report(sign(a.dir, a.by, item=a.item), [], "sign")
    try:
        tree = load(a.dir)
    except FileNotFoundError:
        tree = None     # Stage 1, where asks are made, has no tree yet: no waivers to re-raise
    except ValueError as e:
        return report(["tree.json does not parse: %s" % e], [], a.cmd)
    except OSError as e:
        return report(["tree.json cannot be read: %s" % e], [], a.cmd)
    if tree is not None and not isinstance(tree, dict):
        return report(["tree.json is not an object"], [], a.cmd)
    if a.cmd == "hash":
        if tree is None:
            return report(["no tree.json in %s" % a.dir], [], "hash")
        print(tree_hash(tree))
        return 0
    if tree is None:
        # no tree, no waivers: nothing was checked, which is not the same as clear (GPT review 2026-11-03 §2.3)
        print("HISTORY_NOT_CHECKED: no tree.json yet; read log.md and record.json for a repeat yourself")
        return 0
    hits = askcheck(tree, a.question)
    print("MAY RE-RAISE %s" % ", ".join(hits) if hits else "clear")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
