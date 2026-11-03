#!/usr/bin/env python3
"""Offline proof for SCALDHIDE_R1_DESIGN_NEW_CREATURE: the creature designed from Scaldhide render C.

Exits 0 only when every check holds:
  1. render C's three facings, committed under design/Jawa/worldbuilding/biomes/contagion_rawshade_art/,
     carry the hashes the item names (and the artpipe source agrees, when this machine can reach it);
  2. the design doc names RM_Rawshade and carries Name, Description and Behaviour sections;
  3. "Rawshade" appears in src/ only as the defName RM_Rawshade (no collision with another def);
  4. the judge record's last round is KEEP on all four artifacts;
  5. the build follow-on item RAWSHADE_BUILD_SKIRT_COMES_DOWN is filed on the ledger.

Known limits, accepted (review rounds 1-4): names spelled with XML character references and headings that sit only
inside code fences are not seen; neither is written by any tool or person in this repo. Round 7 adds: Defs files
with an XML namespace (RimWorld defs never carry one) and a later unrelated numeric table in the judge record.
"""
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
DOC = os.path.join(REPO, "design/Jawa/worldbuilding/biomes/contagion_rawshade_2026-11-02.md")
JUDGE = os.path.join(REPO, "design/Jawa/worldbuilding/biomes/contagion_rawshade_2026-11-02.judge.md")
LEDGER = os.path.join(REPO, "infrastructure/state/ledger/events")
ART_COPY = os.path.join(REPO, "design/Jawa/worldbuilding/biomes/contagion_rawshade_art")
ART_ROOT = os.environ.get("RM_ARTSRC", "/mnt/d/ClaudeWork/rimmandrake/artpipe/_artsrc")
ART = {"south": "a84db7fbaa9d", "east": "dc94663f97a2", "north": "69a6e7907900"}
BUILD_ITEM = "RAWSHADE_BUILD_SKIRT_COMES_DOWN"
OWN_NAMES = {"RM_Rawshade", "Corpse_RM_Rawshade"}


def _art_bad(root, nested, seen):
    """Hash each facing under root; nested = the artpipe layout (one folder per facing).
    Facings actually hashed are appended to seen."""
    bad = []
    for facing, want in ART.items():
        name = "arteval_RM_Scaldhide_r1_%s" % facing
        p = os.path.join(root, name, name + ".png") if nested else os.path.join(root, name + ".png")
        try:
            with open(p, "rb") as f:
                got = hashlib.sha256(f.read()).hexdigest()[:12]
        except FileNotFoundError:
            if nested:  # artpipe purged a facing: nothing to compare, not a mismatch
                continue
            bad.append("%s missing" % facing)
            continue
        except OSError as e:
            bad.append("%s unreadable (%s)" % (facing, e.__class__.__name__))
            continue
        seen.append(facing)
        if got != want:
            bad.append("%s sha %s != %s" % (facing, got, want))
    return bad


def check_art():
    """The committed copies are the proof (reachable from any export); the artpipe source,
    when this machine can see it, must still hold the same bytes."""
    if not os.path.isdir(ART_COPY):
        return False, "art copy dir %s missing" % ART_COPY
    bad = _art_bad(ART_COPY, False, [])
    if bad:
        return False, "art (committed copy): " + "; ".join(bad)
    note = "artpipe source not reachable here, committed copy only"
    if os.path.isdir(ART_ROOT):
        seen = []
        src_bad = _art_bad(ART_ROOT, True, seen)
        if src_bad:
            return False, "art (artpipe source): " + "; ".join(src_bad)
        note = "artpipe source agrees on %d of 3 facings present" % len(seen)
    return True, "art: 3 facings match (%s)" % note


def check_doc():
    if not os.path.isfile(DOC):
        return False, "doc missing"
    s = open(DOC, encoding="utf-8").read()
    missing = [h for h in ("Name", "Description", "Behaviour") if not re.search(r"^## %s(\s[^\n]*)?$" % h, s, re.M)]
    if not re.search(r"(?<![\w.-])RM_Rawshade(?![\w-]|\.\w)", s):
        missing.append("RM_Rawshade")
    return (not missing), "doc: " + ("name/description/behaviour present" if not missing else "missing " + ", ".join(missing))


def _raise(err):
    raise err


def check_collision():
    """Every token containing "Rawshade" in src/ *.xml/*.cs must be one of the def's own names, and
    every parsed defName containing "Rawshade" must be an own name, and each def type (parsed XML,
    comments excluded) may declare each own name at most once."""
    hits, decls = [], {}
    try:
        for root, dirs, files in os.walk(os.path.join(REPO, "src"), onerror=_raise):
            dirs[:] = [d for d in dirs if d not in (".git", "bin", "obj")]
            for fn in files:
                if not fn.lower().endswith((".xml", ".cs")):
                    continue
                p = os.path.join(root, fn)
                rel = os.path.relpath(p, REPO)
                with open(p, encoding="utf-8", errors="replace") as f:
                    s = f.read()
                for m in re.finditer(r"[\w-]*Rawshade[\w-]*", s):  # "-" is legal in a defName
                    if m.group(0) not in OWN_NAMES:
                        hits.append("%s:%s" % (rel, m.group(0)))
                if fn.lower().endswith(".xml") and "Rawshade" in s:
                    try:
                        root_el = ET.fromstring(s)
                    except ET.ParseError as e:
                        hits.append("%s unparsable (%s)" % (rel, e))
                        continue
                    for el in root_el.iter():
                        dn = (el.findtext("defName") or "").strip()
                        if "Rawshade" not in dn:
                            continue
                        if dn not in OWN_NAMES:
                            hits.append("%s:defName %s" % (rel, dn))
                        else:
                            decls.setdefault((el.tag, dn), []).append(rel)
    except OSError as e:
        return False, "collision: cannot read src/ (%s)" % e
    for (tag, dn), where in sorted(decls.items()):
        if len(where) > 1:
            hits.append("%s %s declared %d times in %s" % (tag, dn, len(where), sorted(set(where))))
    return (not hits), "collision: " + ("none" if not hits else ", ".join(hits[:5]))


def check_judge():
    if not os.path.isfile(JUDGE):
        return False, "judge record missing"
    rows = [l for l in open(JUDGE, encoding="utf-8") if re.match(r"\s*\|\s*\d+\s*\|", l)]
    if not rows:
        return False, "judge record has no round rows"
    cells = [c.strip() for c in rows[-1].strip().strip("|").split("|")]
    ok = cells[1:5] == ["KEEP"] * 4
    return ok, "judge: last round %s -> %s" % (cells[0], "/".join(cells[1:5]))


def check_item():
    if not os.path.isdir(LEDGER):
        return False, "ledger dir missing"
    for fn in os.listdir(LEDGER):
        if not fn.endswith(".jsonl"):
            continue
        for line in open(os.path.join(LEDGER, fn), encoding="utf-8", errors="replace"):
            if BUILD_ITEM not in line:
                continue
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            if isinstance(ev, dict) and ev.get("id") == BUILD_ITEM and ev.get("verb", ev.get("event")) == "file":
                return True, "build item filed (%s)" % fn
    return False, "build item %s not filed" % BUILD_ITEM


def main():
    failed = unmeasured = False
    for fn in (check_art, check_doc, check_collision, check_judge, check_item):
        try:
            ok, msg = fn()
        except (OSError, ValueError) as e:
            ok, msg = False, "%s crashed: %s" % (fn.__name__, e)
        print(("PASS " if ok else "UNMEASURED " if ok is None else "FAIL ") + msg)
        failed = failed or ok is False
        unmeasured = unmeasured or ok is None
    # An unmeasured check is not a pass: exit 2 so a caller cannot read it as proof.
    print("RESULT", "FAIL" if failed else "UNMEASURED" if unmeasured else "PASS")
    return 1 if failed else 2 if unmeasured else 0


if __name__ == "__main__":
    sys.exit(main())
