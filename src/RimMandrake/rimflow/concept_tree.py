#!/usr/bin/env python3
"""concept_tree.py - the Concept agent's tree: writer, door lint (Gate A) and the gate Relentless refuses a mod on.

Format: design/RimMandrake/relentless_tree_schema_2026-11-01.md. Meaning: concept_agent_design_2026-11-01.md §5-§8, §11.

  write    <dir> --draft d.json [--dry-walk]   stamp hashes, check the shape, write tree.json (clears any signature)
  lint     <dir>                               Gate A: sheet + tree + floor. Exit 0 PASS, 1 REFUSED
  gate     <dir>                               lint plus: not a dry walk, root VALIDATED at its hash, Arbiter signature on
                                               this tree hash, every waiver found in OWNER.jsonl
  sign     <dir> --by Arbiter                  the coverage signature. Refuses a dry walk and a lint failure
  askcheck <dir> "question"                    does this question re-raise a waiver? Exit 1 when it may
  hash     <dir>                               tree_hash

Gate B, the Cold Reader exam, is not here: this program checks form, and a perfectly formed tree can be wrong. The
Arbiter's signature comes after the exam (stage 5), or after `exam_waived` in his words.

What a program cannot do, said plainly: "names an observer" is a word list, the pruning check proves a citation is
present and not that it is good, and askcheck cannot catch a rewording, so a fresh reviewer reads the question log too.
"""
import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
FLOOR_FILE = "concept_floor.json"
OWNER_SHARD = "infrastructure/state/ledger/events/OWNER.jsonl"
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
SLUG = re.compile(r"^[a-z][a-z0-9_]*$")
OBSERVER = re.compile(r"\b(player|colonist|colonists|viewer|observer|pawn|pawns|he|you|screen|log|reader|tester|the save)\b",
                      re.I)
CONSTRAINT = re.compile(r"^\s*(at most|at least|under|over|no more than|<=?|>=?)?\s*\d+(\.\d+)?\s*(ms|s|min|mb|gb|kb|tps|fps|%|"
                        r"per [a-z]+|[a-z]+/[a-z]+)(?![A-Za-z0-9]).*\bon\s+\S+", re.I)
WALK_NEEDS = {"reload": r"\breload(s|ed|ing)?\b", "repeat": r"\brepeat", "second order": r"\b(second|another|different|other|opposite|reverse|reversed)\s+order\b|\border\s+reversed\b|\breverse\s+the\s+order\b"}
TOOL_ROOT = "tool"
STOP = set("the a an of to in on and or it is at for by this that with how what does do not be are was you your his he "
           "me my i we as if".split())


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

SECTIONS = ("his words", "does", "does not", "waived", "open", "delegated", "pruning")
TAG = re.compile(r"^\s*[-*+]\s*\[(leaf|floor|waived|advisory|core)(?::([A-Za-z0-9_]+))?\]\s*(.*)$")


def parse_sheet(path):
    """-> {section: [raw non-empty lines]}. Headings are `## <name>`; a heading may carry a parenthesis after the name."""
    out, cur = {}, None
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^##\s+([^#(]+?)\s*(\(.*\))?\s*$", line)
            if m:
                cur = m.group(1).strip().lower()
                out.setdefault(cur, [])
            elif cur is not None and line.strip():
                out[cur].append(line.rstrip("\n"))
    return out


def sheet_errors(sheet, tree, floor=None):
    errs = []
    for s in SECTIONS:
        if s not in sheet:
            errs.append("sheet: no `## %s` section" % s)
    if not sheet.get("his words"):
        errs.append("sheet: `his words` is empty")
    leaves = {x.get("id"): x for x in tree.get("leaves") or [] if isinstance(x, dict)}
    waived = {w.get("id") for w in tree.get("waived") or [] if isinstance(w, dict)}
    floor_ids = {ln["id"] for ln in (floor or load_floor()[0])["lines"]}
    named = set()
    for sec, allowed in (("does", ("leaf", "floor", "waived", "advisory")), ("does not", ("leaf", "floor", "waived"))):
        for line in sheet.get(sec, []):
            if not re.match(r"^\s*[-*+](\s|\[)", line):
                continue
            m = TAG.match(line)
            if not m or m.group(1) not in allowed:
                errs.append("sheet: `%s` line maps to nothing (%s): %s" % (sec, "|".join(allowed), line.strip()[:80]))
                continue
            tag, ref = m.group(1), m.group(2)
            if tag == "leaf":
                if ref not in leaves:
                    errs.append("sheet: `%s` line names no such leaf: %s" % (sec, ref))
                else:
                    named.add(ref)
                    if sec == "does not" and not leaves[ref].get("cannot_show"):
                        errs.append("sheet: `does not` leaf %s has no cannot_show" % ref)
            elif tag == "floor" and ref not in floor_ids:
                errs.append("sheet: no floor line %s" % ref)
            elif tag == "waived" and ref not in waived:
                errs.append("sheet: no waiver %s" % ref)
    for line in sheet.get("open", []):
        m = TAG.match(line)
        if m and m.group(1) == "core":
            errs.append("sheet: a core line is still open: %s" % m.group(3)[:80])
    for lid, leaf in leaves.items():
        structural = leaf.get("leaf_kind") in ("walk", "instrument")
        if lid not in named and not structural and leaf.get("by") != "setter_sweep":
            errs.append("orphan leaf: %s is on no `does`/`does not` line" % lid)
    pruned = {}
    for line in sheet.get("pruning", []):
        m = re.match(r"^\s*-\s*`?([a-z][a-z0-9_]*)`?\s*:\s*(.*)$", line)
        if m:
            pruned[m.group(1)] = m.group(2).strip()
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
    for k in LEAF_REQ:
        if x.get(k) in (None, "", []):
            e("%s missing" % k)
    for k in ("experience", "scenario", "red", "tier_proposed", "owner_part", "oracle_proposed", "cannot_show"):
        if x.get(k) is not None and not isinstance(x[k], str):
            e("%s must be text" % k)
    for k in x:
        if k not in LEAF_REQ and k not in LEAF_OPT:
            e("field %s is not the tree's (Setter's go in binding.json, budget in budget.json)" % k)
    if not SLUG.match(str(lid)):
        e("id is not a slug")
    if x.get("by") not in ("concept", "filer", "setter_sweep"):
        e("by %r" % x.get("by"))
    if x.get("by") == "setter_sweep" and kind != "tool":
        e("a setter_sweep leaf belongs to a tooling goal only")
    if x.get("leaf_kind") not in LEAF_KINDS:
        e("leaf_kind %r" % x.get("leaf_kind"))
    if x.get("clause_kind") not in ("change", "preserve"):
        e("clause_kind %r" % x.get("clause_kind"))
    text = str(x.get("experience") or "")
    if x.get("leaf_kind") == "constraint":
        if not CONSTRAINT.match(text):
            e("a constraint reads `<limit> <unit> on <test machine>`, got: %s" % text[:60])
    elif text and not OBSERVER.search(text):
        e("experience names no observer: %s" % text[:60])
    if not isinstance(x.get("false_pass"), list) or not all(
            isinstance(w, str) and w.strip() for w in x.get("false_pass") or [""]):
        e("false_pass must list named wrong worlds")
    tier = x.get("tier_proposed")
    if tier and tier not in tiers:
        e("tier_proposed %r not in %s" % (tier, ", ".join(tiers)))
    if tier and tier != "offline" and not str(x.get("tier_reason") or "").strip():
        e("tier %s needs tier_reason" % tier)
    if not (str(x.get("oracle_proposed") or "").strip() or str(x.get("cannot_show") or "").strip()):
        e("no oracle_proposed and no cannot_show")
    op = str(x.get("owner_part") or "")
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
            if r not in root_ids:
                e("root id %s is not in the north star" % r)
    words = " ".join(str(x.get(k) or "") for k in ("experience", "scenario"))
    if not x.get("cannot_show") and re.search(r"\b(worldgen|world generation|world gen)\b", words, re.I):
        e("needs worldgen: refused by standing ruling")
    if tier and tier != "offline" and re.search(r"\b(flight|flyer|flying|takes? off)\b", words, re.I):
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
    if not str(tree.get("subject") or "").strip():
        errs.append("subject missing")
    au = str(tree.get("authored_by") or "")
    if not (au == "concept" or au.startswith("filer:")):
        errs.append("authored_by %r" % au)
    if tree.get("root_state") not in ("VALIDATED", "DRAFT", "none"):
        errs.append("root_state %r" % tree.get("root_state"))
    fl = tree.get("floor") or {}
    if fl.get("ref") != FLOOR_FILE:
        errs.append("floor.ref %r" % fl.get("ref"))
    if fl.get("hash") != floor_hash:
        errs.append("floor.hash is not the current floor's")
    by_id = {ln["id"]: ln for ln in floor["lines"]}
    dry = tree.get("dry_walk") is True
    for o in fl.get("off") or []:
        ln = by_id.get(o.get("line"))
        if ln is None:
            errs.append("floor.off: no line %r" % o.get("line"))
        elif not ln["waivable"]:
            errs.append("floor.off: %s cannot be turned off here" % o.get("line"))
        if not (str(o.get("words") or "").strip() and str(o.get("ref") or "").strip()):
            errs.append("floor.off %s: needs his words and a ref" % o.get("line"))
    ex = tree.get("exam_waived")
    if ex is not None and not (isinstance(ex, dict) and str(ex.get("words") or "").strip() and ex.get("ref")):
        errs.append("exam_waived needs his words and a ref")
    seen_w = set()
    for w in tree.get("waived") or []:
        if not all(str(w.get(k) or "").strip() for k in ("id", "scope", "date", "ref")):
            errs.append("waiver %s: id, scope, date, ref all required" % w.get("id"))
        if w.get("id") in seen_w:
            errs.append("waiver id twice: %s" % w.get("id"))
        seen_w.add(w.get("id"))
        real = re.match(r"^OWNER:\d+$", str(w.get("ref") or ""))
        if not dry and not real:
            errs.append("waiver %s: ref must be OWNER:<tsn>, his event" % w.get("id"))
        if dry and not (w.get("stand_in") is True and str(w.get("ref") or "").startswith("dry_walk:")):
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
    ids = [x.get("id") for x in leaves]
    for d in sorted({i for i in ids if ids.count(i) > 1}, key=str):
        errs.append("leaf id twice: %s" % d)
    instruments = {x.get("id") for x in leaves if x.get("leaf_kind") == "instrument"}
    for x in leaves:
        errs += leaf_errors(x, kind, floor["tiers"], root_ids)
        ni = x.get("needs_instrument")
        if ni and ni not in instruments:
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
        s = str(x.get("scenario") or "")
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
    path = os.path.join(repo, str(ref or "").split("#")[0])
    if not ref or not os.path.isfile(path):
        return "none", None, set(), "root_ref names no file: %r" % (ref,)
    sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
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
    with open(os.path.join(d, "tree.json"), encoding="utf-8") as f:
        return json.load(f)


def lint(d, repo=REPO, floor_file=None):
    """Gate A. -> (errors, flags)."""
    floor, fh = load_floor(floor_file)
    try:
        tree = load(d)
    except FileNotFoundError:
        return ["no tree.json in %s" % d], flags(floor)
    except ValueError as e:
        return ["tree.json does not parse: %s" % e], flags(floor)
    if not isinstance(tree, dict):
        return ["tree.json is not an object"], flags(floor)
    sheet, errs = None, []
    if tree.get("kind") == "mod":
        sp = os.path.join(d, "sheet.md")
        if not os.path.isfile(sp):
            errs.append("no sheet.md")
        else:
            sheet = parse_sheet(sp)
            errs += sheet_errors(sheet, tree, floor)
            if tree.get("dry_walk") is True:
                with open(sp, encoding="utf-8") as f:
                    if "DRY WALK" not in f.readline():
                        errs.append("a dry walk's sheet starts with a DRY WALK line")
    errs += shape_errors(tree, root_ids_for(repo, tree, sheet), floor, fh)
    in_dry = DRY_DIR in os.path.normpath(os.path.abspath(d)).casefold().split(os.sep)
    if (tree.get("dry_walk") is True) != in_dry:
        errs.append("a dry walk lives under %s/ and nothing else does" % DRY_DIR)
    return errs, flags(floor)


def owner_events(repo):
    out = {}
    try:
        with open(os.path.join(repo, OWNER_SHARD), encoding="utf-8") as f:
            for line in f:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if ev.get("tsn"):
                    out[str(ev["tsn"])] = ev
    except OSError:
        pass
    return out


def squash(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def in_words(scope, text):
    """Whole words only: "art" is not in "start", and an empty scope is in nothing."""
    s = squash(scope)
    return bool(s) and " %s " % s in " %s " % squash(text)


def his_words_problem(ev, ref, words):
    """Why `words` are not on the owner event `ref`, or None. A per-ruling event's words are its text."""
    m = re.match(r"^OWNER:(\d+)$", str(ref or ""))
    e = ev.get(m.group(1)) if m else None
    if e is None:
        return "ref finds no event in OWNER.jsonl"
    said = str(e.get("ownerSaid") or "")
    if isinstance(e.get("perRuling"), str) and e["perRuling"].strip():
        said += " " + str(e.get("text") or "")
    return None if in_words(words, said) else "not his words on that event"


def sheet_hash(d):
    """A signature covers what he reads, so it binds the sheet too. Line ends do not count; a tool tree has no sheet."""
    try:
        with open(os.path.join(d, "sheet.md"), "rb") as f:
            return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()
    except OSError:
        return None


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
    cov = tree.get("coverage") or {}
    if cov.get("signed_by") != "Arbiter":
        errs.append("no Arbiter coverage signature")
    elif cov.get("tree_hash") != tree_hash(tree):
        errs.append("the signature is on another tree hash")
    elif tree.get("kind") == "mod" and cov.get("sheet_hash") != sheet_hash(d):
        errs.append("the signature is on another sheet")
    ev = owner_events(repo)
    for w in tree.get("waived") or []:
        why = his_words_problem(ev, w.get("ref"), w.get("scope"))
        if why:
            errs.append("waiver %s: %s" % (w.get("id"), why))
    for o in (tree.get("floor") or {}).get("off") or []:
        why = his_words_problem(ev, o.get("ref"), o.get("words"))
        if why:
            errs.append("floor.off %s: %s" % (o.get("line"), why))
    ex = tree.get("exam_waived")
    if ex:
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


TREE_CITE = re.compile(r"design/concepts/[A-Za-z0-9_./-]+/tree\.json", re.I)


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

def build(draft, repo=REPO, dry=False, sheet=None):
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
    for x in draft.get("leaves") or []:
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
    tree = build(draft, repo, dry, sheet)
    floor, fh = load_floor()
    errs = shape_errors(tree, root_ids_for(repo, tree, sheet), floor, fh)
    if errs:
        return errs
    os.makedirs(d, exist_ok=True)
    tmp = os.path.join(d, ".tree.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=1, ensure_ascii=False, sort_keys=False)
        f.write("\n")
    os.replace(tmp, os.path.join(d, "tree.json"))
    return []


def sign(d, by, repo=REPO, at=None):
    if by != "Arbiter":
        return ["only the Arbiter signs coverage"]
    errs, _fl = lint(d, repo)
    tree = load(d) if os.path.isfile(os.path.join(d, "tree.json")) else {}
    if tree.get("dry_walk") is True:
        errs = errs + ["a dry walk is never signed"]
    if errs:
        return errs
    import time
    tree["coverage"] = {"signed_by": "Arbiter", "at": at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "tree_hash": tree_hash(tree), "sheet_hash": sheet_hash(d)}
    with open(os.path.join(d, "tree.json"), "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=1, ensure_ascii=False)
        f.write("\n")
    return []


def askcheck(tree, question):
    """Waivers a question may re-raise. A word overlap: it catches a repeat, never a rewording."""
    q = set(squash(question).split()) - STOP
    hits = []
    for w in tree.get("waived") or []:
        s = set(squash(w.get("scope")).split()) - STOP
        if s and len(q & s) >= min(len(s), max(2, (len(s) + 1) // 2)):
            hits.append(w.get("id"))
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
        if name == "askcheck":
            p.add_argument("question")
    a = ap.parse_args(argv)
    if a.cmd == "write":
        with open(a.draft, encoding="utf-8") as f:
            draft = json.load(f)
        errs = write(a.dir, draft, dry=a.dry_walk)
        return report(errs, flags(load_floor()[0]), "write")
    if a.cmd == "lint":
        return report(*lint(a.dir), "lint (Gate A)")
    if a.cmd == "gate":
        return report(*gate(a.dir), "gate")
    if a.cmd == "sign":
        return report(sign(a.dir, a.by), [], "sign")
    tree = load(a.dir)
    if a.cmd == "hash":
        print(tree_hash(tree))
        return 0
    hits = askcheck(tree, a.question)
    print("MAY RE-RAISE %s" % ", ".join(hits) if hits else "clear")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
