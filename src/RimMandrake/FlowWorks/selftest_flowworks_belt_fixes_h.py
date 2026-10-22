#!/usr/bin/env python3
"""Belt findings of 2026-10-22, fixed offline by fixer H (no game). Each check reads FlowWorks source and fails on the
pre-fix code; each carries a planted regression that must fail (can-fail).

RAILING_MATERIAL_FIX_MADE_OF_NOTHING: RM_SuspensionRailing is madeFromStuff, but PlaceRailing made it with stuff=null on both
  paths (god mode ThingMaker.MakeThing(rail); player GenConstruct.PlaceBlueprintForBuild(rail, ..., null, ...)) -> Player.log
  'madeFromStuff but stuff=null. Assigning default.' once per railing. Both paths must pass a material.
SETTINGS_SEARCH_FIX_LABELS_NOT_FOUND: Mod Settings search matched a section by title and field names only, so 'Liquid crosses'
  found nothing although the Water engine section draws "Liquid crosses between the pieces of a huge network". The rows' drawn
  labels are recorded per section (RM_SettingsSearchIndex) and a search hits them.
SUSPENSION_BUTTONS_DIAGNOSE_STILL_SHOWING: with "Suspension bridges can be built" off, every RM_Suspension* build button must
  hide. MOD half: the tower was vanilla's generated designator (no Visible override) and stayed. HARNESS half: the proof read
  rimworld/list_architect_designators 'visible' (rules membership, never Designator.Visible); it now reads ProofButtons.
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


# ── SUSPENSION_BUTTONS_DIAGNOSE_STILL_SHOWING ──────────────────────────────────────────────────────────────────────
def mod_file(*parts):
    return open(os.path.join(HERE, *parts), encoding="utf-8").read()


def buttons_problems(defs_xml, patch_xml, des_cs):
    """Every RM_Suspension* def with a designationCategory must be built only through a special designator whose Visible
    reads suspensionBridgesBuildable (a vanilla generated button ignores the setting)."""
    probs = []
    gated = {}
    for m in re.finditer(r"public (?:abstract )?class (\w+) : (\w+)", des_cs):
        gated[m.group(1)] = m.group(2)
    body_of_cls = {}
    for name in gated:
        i = des_cs.index("class %s :" % name)
        j = des_cs.find("\n\tpublic ", i + 1)
        body_of_cls[name] = des_cs[i:j if j > 0 else len(des_cs)]

    def visible_gated(cls):
        seen = set()
        while cls in gated and cls not in seen:
            seen.add(cls)
            if "suspensionBridgesBuildable && base.Visible" in body_of_cls[cls]:
                return True
            cls = gated[cls]
        return False

    registered = re.findall(r"<li>RimMandrake\.FlowWorks\.Pits\.(\w+)</li>", patch_xml)
    placed = {}
    for cls in registered:
        m = re.search(r"class %s : \w+\s*\{\s*public %s\(\) : base\(DefDatabase<ThingDef>\.GetNamed\(\"(\w+)\"\)" % (cls, cls), des_cs)
        if m:
            placed[m.group(1)] = cls
    for m in re.finditer(r"<ThingDef[^>]*>(.*?)</ThingDef>", defs_xml, re.S):
        d = m.group(1)
        name = re.search(r"<defName>(\w+)</defName>", d)
        if not name or "<designationCategory>" not in d:
            continue
        n = name.group(1)
        if "<canGenerateDefaultDesignator>false</canGenerateDefaultDesignator>" not in d:
            probs.append(n + ": vanilla generated button (ignores the setting)")
        elif n in placed and not visible_gated(placed[n]):
            probs.append(n + ": special designator %s not gated on the setting" % placed[n])
    return probs


def check_buttons():
    defs_xml = mod_file("Defs", "Pits", "ThingDefs", "RM_SuspensionBridges.xml")
    patch_xml = mod_file("Patches", "Pits", "RM_SuspensionBridges.xml")
    des_cs = read("Pits/Suspension/Designator_SuspensionBridge.cs")
    p = buttons_problems(defs_xml, patch_xml, des_cs)
    check("buttons: every suspension button hides with bridges off", not p, "; ".join(p))
    check("buttons: sanity, the tower is a gated special designator",
          "Designator_SuspensionTower" in patch_xml and "class Designator_SuspensionTower : Designator_Build" in des_cs)
    old_defs = defs_xml.replace("    <canGenerateDefaultDesignator>false</canGenerateDefaultDesignator>   <!-- Designator_SuspensionTower", "    <!-- Designator_SuspensionTower")
    check("buttons: can-fail, a vanilla tower button is caught",
          old_defs != defs_xml and any("RM_SuspensionTower" in x for x in buttons_problems(old_defs, patch_xml, des_cs)))
    old_des = des_cs.replace("public override bool Visible => RM_SuspensionSettings.suspensionBridgesBuildable && base.Visible;\n\t}\n\n\t/// <summary>A deck square",
                             "\n\t}\n\n\t/// <summary>A deck square")
    check("buttons: can-fail, an ungated tower designator is caught",
          old_des != des_cs and any("RM_SuspensionTower" in x for x in buttons_problems(defs_xml, patch_xml, old_des)))
    proofs = read("Pits/Suspension/RM_SuspensionProofs.cs")
    hook = body_of(proofs, "public static string ProofButtons(")
    check("buttons: ProofButtons reads Designator.Visible the way the gizmo grid does",
          "root.Visible && d.Visible" in hook and "ResolvedAllowedDesignators" in hook)
    live = mod_file("northstar", "suspension_settings_live.py")
    check("buttons: the live row grades ProofButtons, not the bridge list",
          'proof("ProofButtons"' in live and '"bridgeListOff": list_off' in live
          and '"visibleOff": off' not in live)


def main():
    print("selftest_flowworks_belt_fixes_h")
    check_railing()
    check_settings_search()
    check_buttons()
    if FAILS:
        print("FAIL (%d): %s" % (len(FAILS), ", ".join(FAILS)))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
