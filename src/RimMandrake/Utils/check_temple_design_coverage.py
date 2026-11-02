#!/usr/bin/env python3
"""Check that the temple design doc covers what its item asked for, not just its citations.

Item TEMPLE_RUINS_DESIGN_SEVERAL_FAITHS asked for "ruined temples in several Star
Wars-esque faith themes as world mutators, plus Inhabited temples with living
religious residents". check_design_citations.py proves the machinery the doc names
exists; it reads only the '## Cited machinery' table, so deleting both coverage
sections left it green. This tool reads the two coverage sections themselves:

  RUINS   the '## <n>. The ruined ...' section must say the ruins are a
          `TileMutatorDef`, and its table (a header column naming StyleCategoryDef)
          must hold >= 4 rows, each a tier-prefixed (RSW_/RUT_/RM_) mutator defName
          with its own tier-prefixed StyleCategoryDef kit and a faith cell; defNames,
          kits and faith cells must each be >= 4 distinct (several faiths, not one
          faith four times).
  LIVING  the '## <n>. The living ...' section must name `WorldObject_Inhabited`,
          and hold >= 1 table row whose mutator is a tier-prefixed defName, whose cast
          roster code CODE has src/RimMandrake/Inhabited/Defs/CastRosters/
          CastRoster_CODE.xml carrying <faction>CODE</faction>, and whose faith is an
          <ideoName> in a src XML file that also names that row's faction label: a
          faith a living faction really holds.

Exit 0: covered. Exit 1: a clause fails (each failure is printed). Exit 2: usage or
src unreadable (sanity probe: The Salvation must be found as an <ideoName>).
--selftest <doc> applies each mutant the blind checker could name to the doc in
memory and requires every one to go red and the unmutated doc to stay green.

Usage: python3 src/RimMandrake/Utils/check_temple_design_coverage.py [--selftest] <doc.md>
"""
import contextlib
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "src")
ROSTERS = os.path.join(SRC, "RimMandrake", "Inhabited", "Defs", "CastRosters")
DEFNAME = re.compile(r"`((?:RSW|RUT|RM)_[A-Za-z0-9_]+)`")
CODE = re.compile(r"`([A-Z][A-Z0-9_]+)`")
IDEO = re.compile(r"<ideoName>\s*([^<]+?)\s*</ideoName>")
MIN_RUINS = 4


def sections(text):
    """Return {lowercased heading: body} for every '## ' section."""
    out, head, buf = {}, None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if head is not None:
                out[head] = "\n".join(buf)
            head, buf = line[3:].strip().lower(), []
        elif head is not None:
            buf.append(line)
    if head is not None:
        out[head] = "\n".join(buf)
    return out


def find_section(secs, word):
    for head, body in secs.items():
        if re.match(r"\d+\.\s+the\s+" + word, head):
            return body
    return None


def table(body):
    """Return (header cells, [row cells]) of the first markdown table in body."""
    lines = [ln.strip() for ln in body.splitlines() if ln.strip().startswith("|")]
    if len(lines) < 3:
        return None, []
    split = lambda ln: [c.strip() for c in ln.strip("|").split("|")]
    rows = [split(ln) for ln in lines[2:] if not set(ln) <= set("|-: ")]
    return split(lines[0]), rows


def norm_faith(s):
    s = re.sub(r"[`*_]", "", s).strip().lower()
    return re.sub(r"^the\s+", "", s)


def ideo_index():
    """Return {normalised faith: [file text]} for every <ideoName> under src/."""
    idx = {}
    for dirpath, dirnames, filenames in os.walk(SRC):
        dirnames[:] = [d for d in dirnames if d not in (".git", "bin", "obj")]
        for fn in filenames:
            if not fn.endswith(".xml"):
                continue
            try:
                with open(os.path.join(dirpath, fn), encoding="utf-8", errors="replace") as fh:
                    txt = fh.read()
            except OSError:
                continue
            for m in IDEO.finditer(txt):
                idx.setdefault(norm_faith(m.group(1)), []).append(txt)
    return idx


def check_ruins(secs):
    fails = []
    body = find_section(secs, "ruined")
    if body is None:
        return ["RUINS: no '## <n>. The ruined ...' section"]
    if "`TileMutatorDef`" not in body:
        fails.append("RUINS: section never says the ruins are a `TileMutatorDef`")
    head, rows = table(body)
    if not head:
        return fails + ["RUINS: no table in the ruins section"]
    kit_col = next((i for i, h in enumerate(head) if "StyleCategoryDef" in h), None)
    faith_col = next((i for i, h in enumerate(head) if "faith" in h.lower()), None)
    if kit_col is None or faith_col is None:
        return fails + ["RUINS: table lacks a StyleCategoryDef kit column or a faith column"]
    names, kits, faiths = [], [], []
    for r in rows:
        if len(r) <= max(kit_col, faith_col):
            continue
        m, k = DEFNAME.fullmatch(r[0]), DEFNAME.search(r[kit_col])
        if not m:
            continue
        if not k:
            fails.append(f"RUINS: {m.group(1)} has no tier-prefixed StyleCategoryDef kit")
            continue
        if len(r[faith_col]) < 10:
            fails.append(f"RUINS: {m.group(1)} has no faith described")
            continue
        names.append(m.group(1)); kits.append(k.group(1)); faiths.append(r[faith_col].lower())
    for what, vals in (("mutator defNames", names), ("StyleCategoryDef kits", kits),
                       ("faith themes", faiths)):
        if len(set(vals)) < MIN_RUINS:
            fails.append(f"RUINS: {len(set(vals))} distinct {what} with a kit (need >= {MIN_RUINS})")
    if not fails:
        print(f"ok   RUINS: {len(names)} ruined-temple mutators, {len(set(kits))} kits: "
              + ", ".join(f"{n}->{k}" for n, k in zip(names, kits)))
    return fails


def check_living(secs, idx):
    body = find_section(secs, "living")
    if body is None:
        return ["LIVING: no '## <n>. The living ...' section"]
    fails = []
    if "`WorldObject_Inhabited`" not in body:
        fails.append("LIVING: section never names `WorldObject_Inhabited`")
    head, rows = table(body)
    if not head:
        return fails + ["LIVING: no table in the living section"]
    fac_col = next((i for i, h in enumerate(head) if "faction" in h.lower()), None)
    faith_col = next((i for i, h in enumerate(head) if "faith" in h.lower()), None)
    if fac_col is None or faith_col is None:
        return fails + ["LIVING: table lacks a faction or a faith column"]
    good = []
    for r in rows:
        if len(r) <= max(fac_col, faith_col):
            continue
        m, c = DEFNAME.fullmatch(r[0]), CODE.search(r[fac_col])
        if not m or not c:
            continue
        code, label = c.group(1), r[fac_col].split("(")[0].strip().lower()
        roster = os.path.join(ROSTERS, f"CastRoster_{code}.xml")
        try:
            with open(roster, encoding="utf-8") as fh:
                has_cast = f"<faction>{code}</faction>" in fh.read()
        except OSError:
            has_cast = False
        if not has_cast:
            fails.append(f"LIVING: {m.group(1)}: no cast roster CastRoster_{code}.xml for {code}")
            continue
        files = idx.get(norm_faith(r[faith_col]), [])
        if not files:
            fails.append(f"LIVING: {m.group(1)}: faith '{r[faith_col]}' is no <ideoName> in src")
            continue
        words = [w for w in re.findall(r"[a-z]+", label) if len(w) > 3]
        if not words or not any(all(w in t.lower() for w in words) for t in files):
            fails.append(f"LIVING: {m.group(1)}: faith '{r[faith_col]}' is not held by '{label}'")
            continue
        good.append(f"{m.group(1)}->{code}/{norm_faith(r[faith_col])}")
    if not good:
        fails.append("LIVING: no inhabited temple row whose faith a living faction holds")
    elif not fails:
        print(f"ok   LIVING: {len(good)} inhabited temples: " + ", ".join(good))
    return fails


def check(text, idx):
    secs = sections(text)
    return check_ruins(secs) + check_living(secs, idx)


def mutants(text):
    """(name, mutated text) per clause; each must go red."""
    def cut(a, b):
        i, j = text.find(a), text.find(b)
        return text[:i] + text[j:] if 0 <= i < j else None
    secs = sections(text)
    ruins = find_section(secs, "ruined") or ""
    rlines = [ln for ln in ruins.splitlines() if DEFNAME.match(ln.strip("| ").strip())]
    living = find_section(secs, "living") or ""
    llines = [ln for ln in living.splitlines() if ln.startswith("| `RUT_Inhabited")]
    # Kit is the 5th cell of a ruins row; a reshaped table yields no kits, and the
    # kit mutants then come out unapplied, which the selftest reports as a failure.
    kits = [k.group(0) for k in (DEFNAME.search(ln.split("|")[5]) for ln in rlines
                                 if len(ln.split("|")) > 6) if k] or ["`none`"]
    out = [
        ("both coverage sections deleted (the checker's own mutant)",
         cut("## 2. The ruined", "## Cited machinery")),
        ("ruins section deleted", cut("## 2. The ruined", "## 3. The living")),
        ("living section deleted", cut("## 3. The living", "## 4.")),
        ("ruins table cut to 3 rows",
         text.replace("\n".join(rlines), "\n".join(rlines[:3]))),
        ("every kit cell stripped of its StyleCategoryDef",
         _sub_all(text, [(k, "vanilla") for k in kits])),
        ("all kits collapsed to one", _sub_all(text, [(k, kits[0]) for k in kits[1:]])),
        ("TileMutatorDef dropped from the ruins section",
         text.replace(ruins, ruins.replace("`TileMutatorDef`", "`ThingDef`"))),
        ("every faith swapped for one no faction holds",
         _faith_swap(text, llines, "the Whills")),
        ("every cast roster code swapped for one that does not exist",
         _sub_all(text, [(ln, re.sub(r"\(`[A-Z]+`\)", "(`NOSUCHFACTION`)", ln)) for ln in llines])),
        ("faiths rotated so no faction holds its own",
         _rotate_faith(text, llines)),
        ("WorldObject_Inhabited dropped from the living section",
         text.replace(living, living.replace("`WorldObject_Inhabited`", "a marker"))),
    ]
    return out


def _sub_all(text, pairs):
    for a, b in pairs:
        text = text.replace(a, b)
    return text


def _faith_swap(text, llines, faith):
    for ln in llines:
        cells = ln.split("|")
        cells[3] = f" {faith} "
        text = text.replace(ln, "|".join(cells))
    return text


def _rotate_faith(text, llines):
    faiths = [ln.split("|")[3] for ln in llines]
    for ln, f in zip(llines, faiths[1:] + faiths[:1]):
        cells = ln.split("|")
        cells[3] = f
        text = text.replace(ln, "|".join(cells))
    return text


def main(argv):
    selftest = "--selftest" in argv
    args = [a for a in argv[1:] if a != "--selftest"]
    if len(args) != 1:
        print(__doc__.strip().splitlines()[-1])
        return 2
    with open(args[0], encoding="utf-8") as fh:
        text = fh.read()
    idx = ideo_index()
    if "salvation" not in idx:
        print(f"UNREADABLE: sanity probe failed: no <ideoName>The Salvation under {SRC}")
        return 2
    fails = check(text, idx)
    for f in fails:
        print("FAIL " + f)
    if not selftest:
        return 1 if fails else 0
    if fails:
        print("SELFTEST FAIL: the unmutated doc is red")
        return 1
    bad = 0
    for name, mutated in mutants(text):
        if mutated is None or mutated == text:
            print(f"SELFTEST FAIL: mutant '{name}' could not be applied")
            bad += 1
            continue
        with contextlib.redirect_stdout(io.StringIO()):
            red = bool(check(mutated, idx))
        print(f"{'red ' if red else 'GREEN'} mutant: {name}")
        bad += not red
    print(f"selftest: {'PASS' if not bad else 'FAIL'} ({bad} mutants survived or unapplied)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
