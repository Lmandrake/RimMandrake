#!/usr/bin/env python3
"""Belt findings of 2026-10-22, fixed offline by fixer H (no game). Each check reads FlowWorks source and fails on the
pre-fix code; each carries a planted regression that must fail (can-fail).

RAILING_MATERIAL_FIX_MADE_OF_NOTHING: RM_SuspensionRailing is madeFromStuff, but PlaceRailing made it with stuff=null on both
  paths (god mode ThingMaker.MakeThing(rail); player GenConstruct.PlaceBlueprintForBuild(rail, ..., null, ...)) -> Player.log
  'madeFromStuff but stuff=null. Assigning default.' once per railing. Both paths must pass a material.
SETTINGS_SEARCH_FIX_LABELS_NOT_FOUND: Mod Settings search matched a section by title and field names only, so 'Liquid crosses'
  found nothing although the Water engine section draws "Liquid crosses between the pieces of a huge network". The rows' drawn
  labels are recorded per section (RM_SettingsSearchIndex) and a search hits them.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
FAILS = []


def check(name, ok, detail=""):
    print("  %-5s %s %s" % ("ok" if ok else "FAIL", name, detail if not ok else ""))
    if not ok:
        FAILS.append(name)


def read(rel):
    return open(os.path.join(SRC, rel), encoding="utf-8").read()


def body_of(src, sig):
    i = src.index(sig)
    j = src.index("{", i)
    d = 0
    for k in range(j, len(src)):
        d += {"{": 1, "}": -1}.get(src[k], 0)
        if d == 0:
            return src[j:k + 1]
    raise ValueError(sig)


def args_of(call_src, start):
    """Top-level comma-split arguments of the call whose '(' is at or after start."""
    j = call_src.index("(", start)
    d, cur, out = 0, "", []
    for ch in call_src[j:]:
        if ch == "(":
            d += 1
            if d == 1:
                continue
        elif ch == ")":
            d -= 1
            if d == 0:
                out.append(cur.strip())
                return out
        if ch == "," and d == 1:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    raise ValueError("unclosed call")


# ── RAILING_MATERIAL_FIX_MADE_OF_NOTHING ────────────────────────────────────────────────────────────────────────────
def railing_problems(body):
    probs = []
    for m in re.finditer(r"ThingMaker\.MakeThing\(", body):
        a = args_of(body, m.start())
        if len(a) < 2 or a[1] in ("null", ""):
            probs.append("MakeThing without stuff: " + ", ".join(a))
    n = 0
    for m in re.finditer(r"GenConstruct\.PlaceBlueprintForBuild\(", body):
        n += 1
        a = args_of(body, m.start())
        if len(a) < 6 or a[5] == "null":
            probs.append("PlaceBlueprintForBuild stuff arg null: " + ", ".join(a))
    if n == 0:
        probs.append("no PlaceBlueprintForBuild (player path) found")
    return probs


def check_railing():
    src = read("Pits/Suspension/RM_MapComponent_SuspensionBridges.cs")
    body = body_of(src, "private void PlaceRailing(IntVec3 c)")
    p = railing_problems(body)
    check("railing: both paths pass a material", not p, "; ".join(p))
    helper = body_of(src, "public static ThingDef RailingStuffFor(")
    check("railing: material falls back to GenStuff.DefaultStuffFor", "GenStuff.DefaultStuffFor(rail)" in helper)
    old = body.replace("ThingMaker.MakeThing(rail, stuff)", "ThingMaker.MakeThing(rail)")
    check("railing: can-fail on god-mode stuff=null", bool(railing_problems(old)))
    old2 = re.sub(r"(Faction\.OfPlayer, )stuff(, null, RM_SuspensionLooks)", r"\1null\2", body)
    check("railing: can-fail on player-path stuff=null", old2 != body and bool(railing_problems(old2)))


# ── SETTINGS_SEARCH_FIX_LABELS_NOT_FOUND ───────────────────────────────────────────────────────────────────────────
def matches(label, query):
    """SettingsKitCore.Matches: case-insensitive substring of the trimmed query (blank query matches)."""
    q = (query or "").strip().lower()
    return not q or q in (label or "").lower()


def section_labels(body, title):
    """Labels a Section body draws with list.CheckboxLabeled / short list.Label, read from source (string literals only)."""
    i = body.index('Section(list, "%s"' % title)
    j = body.index("{", body.index("\n", i))   # the block opening on the line after the if (...)
    d = 0
    for k in range(j, len(body)):
        d += {"{": 1, "}": -1}.get(body[k], 0)
        if d == 0:
            break
    sec = body[j:k]
    out = re.findall(r'list\.CheckboxLabeled\("((?:[^"\\]|\\.)*)"', sec)
    out += [m for m in re.findall(r'list\.Label\("((?:[^"\\]|\\.)*)"\)', sec) if len(m) <= 90]
    return out


def gate_hits(gate_src, title, names, labels, query):
    """The search rule the Section gate implements: old = title/names only; new = also the drawn labels."""
    hit = matches(title, query) or any(matches(n, query) for n in names)
    if "SectionHits(title, names, searchQuery)" in gate_src:
        hit = hit or any(matches(l, query) for l in labels)
    return hit


def check_settings_search():
    src = read("RimMandrakeFlowWorksMod.cs")
    gate = body_of(src, "private static bool Section(")
    block = body_of(src, "private static void Block(")
    body = body_of(src, "public void DoWindowContents(Rect inRect)")
    title = "Water engine: flow and levelling"
    m = re.search(r'Section\(list, "%s", new\[\] \{([^}]*)\}' % re.escape(title), body)
    check("search: the Water engine section is drawn by Section", bool(m))
    names = re.findall(r'"(\w+)"', m.group(1)) if m else []
    labels = section_labels(body, title)
    row = "Liquid crosses between the pieces of a huge network"
    check("search: sanity, the section draws the row", row in labels, labels[:4])
    for q in ("Liquid crosses", "crosses between", "huge network", "pieces"):
        check("search: '%s' finds the section" % q, gate_hits(gate, title, names, labels, q))
    check("search: can-fail, 'zzqx' finds nothing", not gate_hits(gate, title, names, labels, "zzqx"))
    check("search: Section records its body", "RM_SettingsSearchIndex.Begin(list, title)" in gate)
    check("search: Block records and matches its body", "RM_SettingsSearchIndex.Begin(list, header)" in block
          and "SectionHits(header, null, searchQuery)" in block)
    idx = read("RM_SettingsSearchIndex.cs")
    for meth in ("CheckboxLabeled", "Label"):
        check("search: a %s prefix records labels" % meth,
              bool(re.search(r"HarmonyPatch\(typeof\(Listing_Standard\), nameof\(Listing_Standard\.%s\)" % meth, idx)))
    csproj = read("RimMandrake_FlowWorks.csproj")
    check("search: the index file is compiled", 'Compile Include="RM_SettingsSearchIndex.cs"' in csproj)
    old_gate = gate.replace("SectionHits(title, names, searchQuery)", "OLDRULE")
    check("search: can-fail, the old title/names rule misses 'Liquid crosses'",
          not gate_hits(old_gate, title, names, labels, "Liquid crosses"))


def main():
    print("selftest_flowworks_belt_fixes_h")
    check_railing()
    check_settings_search()
    if FAILS:
        print("FAIL (%d): %s" % (len(FAILS), ", ".join(FAILS)))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
