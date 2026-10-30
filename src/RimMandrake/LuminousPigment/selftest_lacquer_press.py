#!/usr/bin/env python3
"""Offline selftest for LACQUER_PRESS_REWIRE_BILL_PLUS_RIGHT_CLICK (owner ruling 2026-10-16, by card
"Bill + right-click the press"): lacquering is a press bill plus a right-click on the press, never a pawn gizmo.

    python3 src/RimMandrake/LuminousPigment/selftest_lacquer_press.py

No game. It pins the contract between Defs/RecipeDefs/RM_LacquerAtPress.xml and the C# that reads it, the part
a live round trip cannot see until the settings or the def drift:
  1. two recipes, RM_LacquerApparel (Apparel) and RM_LacquerWeapon (Weapons), each used by RM_DeepfirePress, each
     with workerClass RecipeWorker_LacquerItem (a class that exists in Source/) and no <products> (the item itself
     comes back);
  2. ingredient [0] is the item slot (count 1) and ingredient [1] is RM_Deepfire, because SetLacquerRecipeCost
     writes ingredients[1]; the XML count equals the costApparel/costWeapon default, and both names are passed
     to SetLacquerRecipeCost;
  3. the press def exists, is the PressDefName the C# matches, and has CompPowerTrader (else "no power" can never
     show);
  4. the right-click provider is a FloatMenuOptionProvider, names the unpowered reason, and the pawn gizmo is gone.
Each check runs against mutated copies too (MUTANTS): every mutant must turn at least one check red.
What it cannot prove: that the float menu appears in game and that the unpowered option is greyed. Those stay
live criteria on the item.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
RECIPES = os.path.join(HERE, "Defs", "RecipeDefs", "RM_LacquerAtPress.xml")
PRESS = os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_DeepfirePress.xml")
WANT = {"RM_LacquerApparel": ("Apparel", "costApparel"), "RM_LacquerWeapon": ("Weapons", "costWeapon")}


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def load():
    cs = {n: read(os.path.join(SRC, n)) for n in sorted(os.listdir(SRC)) if n.endswith(".cs")}
    return {"recipes": read(RECIPES), "press": read(PRESS), "cs": cs}


def checks(art):
    """Return a list of (name, ok, detail). Pure: reads only `art`."""
    out = []

    def c(name, ok, detail=""):
        out.append((name, bool(ok), detail))

    code = {n: strip_comments(t) for n, t in art["cs"].items()}     # a commented-out line must not satisfy a check
    allcs = "\n".join(code.values())
    mod = code.get("LuminousPigmentMod.cs", "")
    press_cs = code.get("LacquerAtPress.cs", "")
    try:
        root = ET.fromstring(art["recipes"])
    except ET.ParseError as e:
        c("recipes XML parses", False, str(e))
        return out
    recipes = {r.findtext("defName"): r for r in root.findall("RecipeDef")}
    c("exactly the two lacquer recipes", sorted(recipes) == sorted(WANT), sorted(recipes))
    worker_cls = re.search(r"class\s+(\w+)\s*:\s*RecipeWorker\b", press_cs)
    ns = re.search(r"^namespace\s+([\w.]+)", press_cs, re.M)
    worker_full = "%s.%s" % (ns.group(1), worker_cls.group(1)) if ns and worker_cls else None
    for name, (cat, setting) in WANT.items():
        r = recipes.get(name)
        if r is None:
            continue
        users = [li.text for li in r.findall("recipeUsers/li")]
        c(name + ": used by the press only", users == ["RM_DeepfirePress"], users)
        wc = (r.findtext("workerClass") or "").strip()
        c(name + ": workerClass is the RecipeWorker in LacquerAtPress.cs (namespace-qualified)",
          worker_full is not None and wc == worker_full, (wc, worker_full))
        c(name + ": no <products> (the item itself is the product)", r.find("products") is None)
        ings = r.findall("ingredients/li")
        c(name + ": two ingredients", len(ings) == 2, len(ings))
        if len(ings) == 2:
            item_f = shape(ings[0].find("filter"))
            c(name + ": ingredient [0] is the %s item, count 1" % cat,
              item_f == {"categories": [cat]} and ings[0].findtext("count") == "1", (item_f, ings[0].findtext("count")))
            fire_f = shape(ings[1].find("filter"))
            c(name + ": ingredient [1] is RM_Deepfire (SetLacquerRecipeCost writes ingredients[1])",
              fire_f == {"thingDefs": ["RM_Deepfire"]}, fire_f)
            m = re.search(r"public static int %s\s*=\s*(\d+)\s*;" % setting, mod)
            c(name + ": XML deepfire count equals the %s default" % setting,
              m is not None and ings[1].findtext("count") == m.group(1),
              (ings[1].findtext("count"), m and m.group(1)))
        for fname in ("fixedIngredientFilter", "defaultIngredientFilter"):
            got = shape(r.find(fname))
            c(name + ": %s is exactly the item class and deepfire (no exclusions, no extras)" % fname,
              got == {"categories": [cat], "thingDefs": ["RM_Deepfire"]}, got)
        c(name + ": startup writes its cost from %s" % setting,
          re.search(r'SetLacquerRecipeCost\("%s",\s*LuminousPigmentSettings\.%s\)' % (name, setting), mod) is not None)
    c("SetLacquerRecipeCost writes the clamped setting into ingredients[1]",
      re.search(r"r\.ingredients\[1\]\.SetBaseCount\(\s*System\.Math\.Max\(\s*1\s*,\s*cost\s*\)\s*\)\s*;", mod) is not None)

    try:
        proot = ET.fromstring(art["press"])
    except ET.ParseError as e:
        c("press XML parses", False, str(e))
        return out
    pdefs = [t for t in proot.iter("ThingDef") if t.findtext("defName") == "RM_DeepfirePress"]
    c("press def RM_DeepfirePress exists", len(pdefs) == 1, len(pdefs))
    c("C# PressDefName is RM_DeepfirePress", 'PressDefName = "RM_DeepfirePress"' in allcs)
    if pdefs:
        comps = [li.findtext("compClass") for li in pdefs[0].findall("comps/li")
                 if li.get("Class") == "CompProperties_Power"]
        c("press has CompPowerTrader (the unpowered reason can show)", comps == ["CompPowerTrader"], comps)

    c("right-click provider is a FloatMenuOptionProvider",
      re.search(r"class\s+FloatMenuOptionProvider_LacquerAtPress\s*:\s*FloatMenuOptionProvider\b", press_cs) is not None)
    c("right-click names the unpowered reason", '"The deepfire press has no power."' in press_cs)
    gate = re.search(r'if\s*\(\s*!\s*LacquerWornItemUtility\.StationUsable\(clickedThing\)\s*\)\s*'
                     r'why\s*=\s*"The deepfire press has no power\.";\s*else if\b', press_cs)
    c("right-click: an UNpowered press sets the reason, and only the else branches make the job",
      gate is not None and gate.start() < press_cs.find("MakeJob(pawn, item, clickedThing"))
    # No code in this mod patches Pawn.GetGizmos or builds a Command at all (measured 2026-10-30), so any such
    # construct is the gizmo coming back under whatever name. If a later feature needs one, narrow this check.
    gizmo = re.search(r"GetGizmos|new\s+Command\w*|:\s*Command\w*\b", allcs)
    c("pawn gizmo is gone (no Pawn.GetGizmos patch, no Command built)", gizmo is None, gizmo and gizmo.group(0))
    return out


def strip_comments(cs):
    """C# without // and /* */ comments (string literals kept; none in these files holds a comment marker)."""
    out, i, n = [], 0, len(cs)
    while i < n:
        if cs[i] == '"':
            j = i + 1
            while j < n and cs[j] != '"':
                j += 2 if cs[j] == "\\" else 1
            out.append(cs[i:j + 1])
            i = j + 1
        elif cs.startswith("//", i):
            j = cs.find("\n", i)
            i = n if j < 0 else j
        elif cs.startswith("/*", i):
            j = cs.find("*/", i + 2)
            i = n if j < 0 else j + 2
        else:
            out.append(cs[i])
            i += 1
    return "".join(out)


def shape(f):
    """A ThingFilter element as {child tag: [li texts]}; any child (exclusions, specialFilters, ...) shows up."""
    if f is None:
        return None
    return {ch.tag: [li.text for li in ch.findall("li")] for ch in f}


def mutate(art, key, old, new, csname=None):
    m = {"recipes": art["recipes"], "press": art["press"], "cs": dict(art["cs"])}
    if csname:
        if old not in m["cs"][csname]:
            raise AssertionError("mutant anchor missing in %s: %r" % (csname, old))
        m["cs"][csname] = m["cs"][csname].replace(old, new, 1)
    else:
        if old not in m[key]:
            raise AssertionError("mutant anchor missing in %s: %r" % (key, old))
        m[key] = m[key].replace(old, new, 1)
    return m


def swap_ingredients(xml):
    """Put the deepfire li before the item li in the first recipe."""
    root = ET.fromstring(xml)
    ings = root.find("RecipeDef/ingredients")
    first, second = list(ings)
    ings.remove(first)
    ings.append(first)
    assert list(ings) == [second, first]
    return ET.tostring(root, encoding="unicode")


def main():
    art = load()
    fails = 0
    for name, ok, detail in checks(art):
        print("%s  %s %s" % ("ok  " if ok else "FAIL", name, "" if ok else detail))
        fails += not ok
    mutants = [
        ("ingredient order swapped", dict(art, recipes=swap_ingredients(art["recipes"]))),
        ("weapon recipe moved off the press", mutate(art, "recipes", "<li>RM_DeepfirePress</li>\n    </recipeUsers>\n  </RecipeDef>\n\n</Defs>",
                                                     "<li>TableMachining</li>\n    </recipeUsers>\n  </RecipeDef>\n\n</Defs>")),
        ("XML cost drifts from costApparel default", mutate(art, "recipes", "<count>3</count>", "<count>4</count>")),
        ("products added", mutate(art, "recipes", "<recipeUsers>", "<products><RM_Deepfire>1</RM_Deepfire></products><recipeUsers>")),
        ("workerClass renamed", mutate(art, "recipes", "RecipeWorker_LacquerItem<", "RecipeWorker_Lacquer<")),
        ("workerClass namespace wrong", mutate(art, "recipes", "RimMandrake.LuminousPigment.RecipeWorker_LacquerItem",
                                               "DoesNotExist.RecipeWorker_LacquerItem")),
        ("fixed filter excludes apparel", mutate(art, "recipes", "</fixedIngredientFilter>",
                                                 "<disallowedCategories><li>Apparel</li></disallowedCategories></fixedIngredientFilter>")),
        ("item filter gains an extra def", mutate(art, "recipes", "<li>Apparel</li>\n          </categories>\n        </filter>",
                                                  "<li>Apparel</li>\n          </categories>\n          <thingDefs><li>Steel</li></thingDefs>\n        </filter>")),
        ("cost setter ignores the setting", mutate(art, "cs", "SetBaseCount(System.Math.Max(1, cost))", "SetBaseCount(1)",
                                                   "LuminousPigmentMod.cs")),
        ("unpowered gate negation dropped", mutate(art, "cs", "if (!LacquerWornItemUtility.StationUsable(clickedThing))",
                                                   "if (LacquerWornItemUtility.StationUsable(clickedThing))", "LacquerAtPress.cs")),
        ("press loses power comp", mutate(art, "press", "CompPowerTrader", "CompGlower")),
        ("unpowered reason removed", mutate(art, "cs", '"The deepfire press has no power."', '"x"', "LacquerAtPress.cs")),
        ("cost setter writes ingredients[0]", mutate(art, "cs", "r.ingredients[1].SetBaseCount", "r.ingredients[0].SetBaseCount",
                                                     "LuminousPigmentMod.cs")),
        ("gizmo back under a new name", mutate(art, "cs", "public class RecipeWorker_LacquerItem",
                              "[HarmonyPatch(typeof(Pawn), nameof(Pawn.GetGizmos))]\n    public static class Patch_PawnButtons\n"
                              "    {\n        static IEnumerable<Gizmo> Postfix(IEnumerable<Gizmo> v, Pawn __instance)\n"
                              "        {\n            foreach (Gizmo g in v) yield return g;\n"
                              "            yield return new Command_Action { defaultLabel = \"Coat\", action = () => { } };\n"
                              "        }\n    }\n    public class RecipeWorker_LacquerItem", "LacquerAtPress.cs")),
        ("apparel cost call commented out", mutate(art, "cs", 'SetLacquerRecipeCost("RM_LacquerApparel"',
                                                   '// SetLacquerRecipeCost("RM_LacquerApparel"', "LuminousPigmentMod.cs")),
        ("weapon cost call commented out", mutate(art, "cs", 'SetLacquerRecipeCost("RM_LacquerWeapon"',
                                                  '/* */ // SetLacquerRecipeCost("RM_LacquerWeapon"', "LuminousPigmentMod.cs")),
        ("unpowered gate commented out", mutate(art, "cs", 'if (!LacquerWornItemUtility.StationUsable(clickedThing)) why',
                                                '/* if (!LacquerWornItemUtility.StationUsable(clickedThing)) why */ if (false) why',
                                                "LacquerAtPress.cs")),
    ]
    for label, m in mutants:
        red = [n for n, ok, _ in checks(m) if not ok]
        print("%s  mutant red: %s %s" % ("ok  " if red else "FAIL", label, red[:2] if red else "(no check caught it)"))
        fails += not red
    print("\n%s" % ("ALL OK" if not fails else "FAILED: %d" % fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
