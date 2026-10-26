#!/usr/bin/env python3
"""selftest_coldstorage.py -- build and run the C# selftest of the cold storage engine (mandrake.rm.coldstorage).

    python3 src/RimMandrake/ColdStorage/selftest_coldstorage.py   (exit 0 = clean)

Source/SelfTest/Program.cs compiles the REAL Source/Kernel/ColdStorageKernel.cs and checks it against the shipped
Assembly-CSharp's GenTemperature.RotRateAtTemperature: rot per tick for each unit type, the temperature an item
on a unit reads, and every engine switch off giving vanilla rot at room temperature
(COLD_STORAGE_ENGINE_BUILD_CLIMATE_COMP). dotnet.exe is Windows-native, so the project is staged on D: by
Utils/winbuild.stage_build and run with `dotnet run --no-build`. No dotnet.exe -> exit 2, UNMEASURED.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
CSPROJ = os.path.join(HERE, "Source", "SelfTest", "RimMandrakeColdStorage.SelfTest.csproj")
DOTNET = ("/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe")


def static_checks():
    """Source-level pins the C# selftest cannot see. Returns a list of failure strings."""
    import re
    import xml.etree.ElementTree as ET
    fails = []
    # A class holding a static Texture2D/Material loaded at class init must be [StaticConstructorOnStartup], else
    # its cctor may run off the main thread (map load/gen are async long events) and DevMode warns every startup.
    src = os.path.join(HERE, "Source")
    for dirpath, dirnames, files in os.walk(src):
        dirnames[:] = [d for d in dirnames if d not in ("SelfTest", "obj", "bin")]
        for f in files:
            if not f.endswith(".cs"):
                continue
            path = os.path.join(dirpath, f)
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            if re.search(r"static\s+readonly\s+(Texture2D|Material)\b", text) and "[StaticConstructorOnStartup]" not in text:
                fails.append("%s: static Texture2D/Material field without [StaticConstructorOnStartup]" % os.path.relpath(path, HERE))
    # LWM.DeepStorage.Properties is a CompProperties (LWM's own Deep_Storage.xml puts it under <comps>);
    # under <modExtensions> it is a load error and the unit gets no deep storage.
    lwm = os.path.join(HERE, "Patches", "ColdStorage_LWMDeepStorage.xml")
    root = ET.parse(lwm).getroot()
    found = 0
    for parent in root.iter():
        for li in parent.findall("li"):
            if li.get("Class") == "LWM.DeepStorage.Properties":
                found += 1
                if parent.tag != "comps":
                    fails.append("%s: LWM.DeepStorage.Properties under <%s>, must be <comps>" % (os.path.basename(lwm), parent.tag))
    if found == 0:
        fails.append("%s: no LWM.DeepStorage.Properties found (instrument blind?)" % os.path.basename(lwm))
    fails += seal_static_checks(ET, re)
    fails += stasis_unlock_checks(ET)
    fails += encase_static_checks(ET, re)
    return fails


def stasis_unlock_checks(ET):
    """COLD_STORAGE_STASIS_BUILD_RAKATAN_CHAMBERS: the chambers' unlock path is wired into systems that already exist,
    so its pins are cross-file: the Rakatan research sits in the Wrecked Machines ShipRelated restoration family, the
    Research Reinvented Analyse opportunity studies the broken grades, every grade of every line joins the Wrecked
    Machines ladder under the mod names the game matches, the Kludged/Refurbished/Original fallback rot factors follow
    the owner's grade ruling (strength 0.2/0.75/1), and the RUT V6 vault places the chambers as loot."""
    fails = []
    src = os.path.join(ROOT, "src")
    rsw = os.path.join(src, "RimStarWars", "Cuisine")
    wm = os.path.join(src, "RimMandrake", "WreckedMachines")
    rut = os.path.join(src, "RimUtinni", "StructureInjectionsRUT", "Defs", "VaultDungeons")

    def defs_by_name(path):
        out = {}
        for el in ET.parse(path).getroot():
            dn = el.findtext("defName")
            if dn:
                out[dn] = el
        return out

    def all_defnames(root_dir):
        names = set()
        for dirpath, _, files in os.walk(os.path.join(root_dir, "Defs")):
            for f in files:
                if f.endswith(".xml"):
                    names |= set(defs_by_name(os.path.join(dirpath, f)))
        return names

    def mod_name(mod_dir):
        return ET.parse(os.path.join(mod_dir, "About", "About.xml")).getroot().findtext("name")

    rsw_defs = defs_by_name(os.path.join(rsw, "Defs", "RSW_RakatanStasis.xml"))
    lockers = defs_by_name(os.path.join(HERE, "Defs", "ColdStorage_StasisLockers.xml"))
    rsw_all, wm_all = all_defnames(rsw), all_defnames(wm)
    grades = ("Wrecked", "Kludged", "Refurbished", "Original")
    lines = {"RM_AncientStasisLocker": lockers, "RSW_RakatanStasisCasket": rsw_defs, "RSW_RakatanStasisVault": rsw_defs}
    if len(rsw_defs) < 9 or len(lockers) < 4:
        fails.append("stasis unlock: read %d Rakatan / %d locker defs (instrument blind?)" % (len(rsw_defs), len(lockers)))
        return fails

    # 1. research: ShipRelated, after the cryo store and Wrecked Machines' restoration research
    proj = rsw_defs.get("RSW_RakatanStasis")
    if proj is None:
        fails.append("stasis unlock: no ResearchProjectDef RSW_RakatanStasis")
    else:
        if "ShipRelated" not in [li.text for li in proj.findall("tags/li")]:
            fails.append("stasis unlock: RSW_RakatanStasis lacks the ShipRelated tag")
        pre = {li.text: li.get("MayRequire") for li in proj.findall("prerequisites/li")}
        if "RSW_CryoStorage" not in pre or "RSW_CryoStorage" not in rsw_all:
            fails.append("stasis unlock: RSW_RakatanStasis must follow RSW_CryoStorage (a Cuisine def)")
        if pre.get("RM_WM_PowerCellRestoration") != "mandrake.rm.wreckedmachines" or "RM_WM_PowerCellRestoration" not in wm_all:
            fails.append("stasis unlock: RSW_RakatanStasis must follow RM_WM_PowerCellRestoration, MayRequire wreckedmachines")
    # 2. Research Reinvented Analyse opportunity on the broken grades
    opp = rsw_defs.get("RSW_AnalyseRakatanStasisChamber")
    if opp is None:
        fails.append("stasis unlock: no Analyse opportunity RSW_AnalyseRakatanStasisChamber")
    else:
        things = {li.text for li in opp.findall("things/li")}
        want = {"RSW_RakatanStasis%s_%s" % (k, g) for k in ("Casket", "Vault") for g in ("Wrecked", "Kludged")}
        if opp.findtext("project") != "RSW_RakatanStasis" or opp.findtext("opportunityType") != "Analyse" or things != want:
            fails.append("stasis unlock: Analyse opportunity must study %s for RSW_RakatanStasis" % sorted(want))
        if "petetimessix.researchreinvented" not in (opp.get("MayRequire") or ""):
            fails.append("stasis unlock: Analyse opportunity must MayRequire Research Reinvented")
    # 3. fallback strengths follow the grade ruling; every grade of every line exists
    want_rot = {"Kludged": 0.8, "Refurbished": 0.25, "Original": 0.0}
    for line, defs in lines.items():
        for g in grades:
            d = defs.get("%s_%s" % (line, g))
            if d is None:
                fails.append("stasis unlock: missing %s_%s" % (line, g))
                continue
            if g in want_rot:
                rot = d.findtext("comps/li/stasisRotFactor")
                if rot is None or abs(float(rot) - want_rot[g]) > 1e-6:
                    fails.append("stasis unlock: %s_%s stasisRotFactor %s, ruling says %s" % (line, g, rot, want_rot[g]))
    # 4. Wrecked Machines ladder: every grade gets its WreckedMachineGrade under the right line; FindMod names match
    for patch, mods in ((os.path.join(HERE, "Patches", "ColdStorage_WreckedMachinesLadder.xml"), [wm]),
                        (os.path.join(rsw, "Patches", "RSW_RakatanStasisLadder.xml"), [wm, HERE])):
        root = ET.parse(patch).getroot()
        named = {li.text for m in root.iter("mods") for li in m}
        for mdir in mods:
            if mod_name(mdir) not in named:
                fails.append("stasis unlock: %s FindMod never names %r" % (os.path.basename(patch), mod_name(mdir)))
        exts = {}
        for op in root.iter("li"):
            if op.get("Class") == "PatchOperationAddModExtension":
                ext = op.find("value/li")
                dn = (op.findtext("xpath") or "").split('defName="')[-1].split('"')[0]
                exts[dn] = (ext.findtext("grade"), ext.findtext("line"))
        rsw_patch = os.path.basename(patch).startswith("RSW_")
        for line in lines:
            if line.startswith("RSW_") != rsw_patch:
                continue
            for g in grades:
                if exts.get("%s_%s" % (line, g)) != (g, line):
                    fails.append("stasis unlock: %s gives %s_%s no WreckedMachineGrade(%s, %s)"
                                 % (os.path.basename(patch), line, g, g, line))
    # 5. RUT V6 vault places the chambers as loot, MayRequire'd on both of their mods
    syms = defs_by_name(os.path.join(rut, "SymbolDefs_Vaults.xml"))
    layout = open(os.path.join(rut, "StructureLayoutDefs_Vaults.xml"), encoding="utf-8").read()
    v6 = layout[layout.find("RUT_VaultType3_FrozenRakata"):]
    placed = 0
    for name, el in syms.items():
        thing = el.findtext("thing") or ""
        if not thing.startswith("RSW_RakatanStasis"):
            continue
        placed += 1
        if thing not in rsw_defs:
            fails.append("stasis unlock: %s spawns %s, which is no Rakatan chamber def" % (name, thing))
        if set((el.get("MayRequire") or "").split(",")) != {"mandrake.rsw.cuisine", "mandrake.rm.coldstorage"}:
            fails.append("stasis unlock: %s must MayRequire cuisine and coldstorage" % name)
        if v6.count(name) != 1:
            fails.append("stasis unlock: %s placed %d times in the V6 vault, want 1" % (name, v6.count(name)))
    if placed < 2:
        fails.append("stasis unlock: only %d Rakatan chamber symbols in the RUT vault symbols" % placed)
    return fails


def seal_static_checks(ET, re):
    """COLD_STORAGE_SEALS_BUILD_RESIN_SAND_BRINE / COLD_STORAGE_TARSEAL_BUILD_SUMP_VAT pins. An external "Type:field"
    setting that names no public static field reads as unreadable, and GateOpen then treats it as ON: a typo would
    silently ignore the player's switch. The Sump's tar defs ride Cold Storage parents, so each must be MayRequire'd."""
    fails = []
    mods = os.path.dirname(HERE)
    files = [os.path.join(HERE, "Defs", "Seals", f) for f in sorted(os.listdir(os.path.join(HERE, "Defs", "Seals")))]
    tar = os.path.join(mods, "TheSump", "Defs", "ThingDefs_Buildings", "RM_TarSealing.xml")
    files.append(tar)
    refs = 0
    for path in files:
        root = ET.parse(path).getroot()
        for tag in ("settingField", "chanceSettingField"):
            for el in root.iter(tag):
                refs += 1
                typ, _, field = (el.text or "").strip().rpartition(":")
                cls = typ.rpartition(".")[2]
                src = None
                for d in (HERE, os.path.join(mods, "TheSump")):
                    for dp, dn, fs in os.walk(os.path.join(d, "Source")):
                        dn[:] = [x for x in dn if x not in ("SelfTest", "obj", "bin")]
                        for f in fs:
                            if f.endswith(".cs"):
                                t = open(os.path.join(dp, f), encoding="utf-8").read()
                                if re.search(r"class\s+%s\b" % re.escape(cls), t):
                                    src = t
                if src is None or not re.search(r"public\s+static\s+\w+\s+%s\s*=" % re.escape(field), src):
                    fails.append("%s: %s %r names no public static field" % (os.path.basename(path), tag, el.text))
        if path == tar:
            for d in root:
                if d.get("MayRequire") != "mandrake.rm.coldstorage":
                    fails.append("RM_TarSealing.xml: %s %s lacks MayRequire mandrake.rm.coldstorage" % (d.tag, d.findtext("defName")))
            # A crafting station heats only while worked: a CompHeatPusher on a consumeFuelOnlyWhenUsed firebox heats
            # 24/7. Building_WorkTable_HeatPush pushes heatPerTickWhileWorking from UsedThisTick only.
            vat = [d for d in root if d.findtext("defName") == "RM_TarSealingVat"]
            if len(vat) != 1:
                fails.append("RM_TarSealing.xml: RM_TarSealingVat not found (instrument blind?)")
            else:
                v = vat[0]
                if any("HeatPusher" in (li.get("Class") or "") for li in v.iter("li")):
                    fails.append("RM_TarSealingVat: has a CompHeatPusher (heats while idle)")
                if v.findtext("thingClass") != "Building_WorkTable_HeatPush" or not v.findtext("building/heatPerTickWhileWorking"):
                    fails.append("RM_TarSealingVat: must be Building_WorkTable_HeatPush with heatPerTickWhileWorking")
    if refs < 5:
        fails.append("seal settings refs: only %d found (instrument blind?)" % refs)
    # RecipeDef.AvailableNow only filters the add-bill list; WorkGiver_DoBill runs any bill whose ShouldDoNow is true,
    # so a method switch must also pause existing bills or a station built before the switch keeps working.
    hp = open(os.path.join(HERE, "Source", "HarmonyPatches.cs"), encoding="utf-8").read()
    m = re.search(r"\[HarmonyPatch\(typeof\(Bill_Production\),\s*nameof\(Bill_Production\.ShouldDoNow\)\)\][\s\S]*?\n    }\n", hp)
    if not m or "ColdStorageGates.RecipeOpen" not in m.group(0):
        fails.append("HarmonyPatches.cs: no Bill_Production.ShouldDoNow postfix gating on ColdStorageGates.RecipeOpen "
                     "(a switched-off method's existing bills keep running)")
    fails += duplicate_comp_checks(ET, files)
    fails += food_kind_checks(ET, files)
    return fails


ENCASE_WORKER = "RimMandrake.ColdStorage.RecipeWorker_Encase"
CUISINE_SETTINGS = "RimMandrake.StarWars.Cuisine.RSW_CuisineSettings"


def encase_static_checks(ET, re):
    """COLD_STORAGE_CARBONFREEZE_BUILD_FOOD_PRESS pins on Star Wars Cuisine's Defs/RSW_CarbonFreezing.xml.
    An encase or release recipe that runs vanilla's RecipeWorker DESTROYS the food it just put in the pack (vanilla
    consumes every ingredient), so each must name RecipeWorker_Encase. A pack that stacks merges two packs' contents
    into one label, so CompEncased needs stackLimit 1. Every def rides Cold Storage classes or parents, so each is
    MayRequire'd on it. Every gate and the shock-chance slider name a real public static field of the Cuisine
    settings (an unreadable one reads as ON / the XML default and silently ignores the player)."""
    fails = []
    mods = os.path.dirname(HERE)
    path = os.path.join(mods, "..", "RimStarWars", "Cuisine", "Defs", "RSW_CarbonFreezing.xml")
    root = ET.parse(path).getroot()
    named = {d.get("Name"): d for d in root if d.get("Name")}

    def lookup(d, xp):
        while d is not None:
            v = d.find(xp)
            if v is not None:
                return v
            d = named.get(d.get("ParentName"))
        return None

    settings_src = os.path.join(mods, "..", "RimStarWars", "Cuisine", "Source", "Cuisine", "CuisineSettings.cs")
    src = open(settings_src, encoding="utf-8").read()
    packs, encase, release, gated, refs = set(), 0, 0, 0, 0
    for d in root:
        name = d.findtext("defName") or d.get("Name") or "?"
        if "mandrake.rm.coldstorage" not in (d.get("MayRequire") or "").split(","):
            fails.append("RSW_CarbonFreezing.xml: %s %s lacks MayRequire mandrake.rm.coldstorage" % (d.tag, name))
        if d.tag == "ThingDef" and d.get("Abstract") != "True":
            if any(li.get("Class") == "RimMandrake.ColdStorage.CompProperties_Encased" for li in lookup(d, "comps") or []):
                packs.add(name)
                if (lookup(d, "stackLimit").text if lookup(d, "stackLimit") is not None else "") != "1":
                    fails.append("%s: has CompEncased but stackLimit is not 1" % name)
        for tag in ("settingField", "shockChanceSettingField"):
            for el in d.iter(tag):
                refs += 1
                typ, _, field = (el.text or "").strip().rpartition(":")
                want = "bool" if tag == "settingField" else "float"
                if typ != CUISINE_SETTINGS or not re.search(r"public\s+static\s+%s\s+%s\s*=" % (want, re.escape(field)), src):
                    fails.append("%s: %s %r names no public static %s of %s" % (name, tag, el.text, want, CUISINE_SETTINGS))
    for d in root:
        if d.tag != "RecipeDef" or d.get("Abstract") == "True":
            continue
        name = d.findtext("defName")
        users = [li.text for li in (lookup(d, "recipeUsers") or [])]
        exts = lookup(d, "modExtensions")
        classes = [li.get("Class") for li in (exts if exts is not None else [])]
        if "RSW_CarbonFreezingPress" in users:
            if "RimMandrake.ColdStorage.ColdStorageGateExtension" not in classes:
                fails.append("%s: a press recipe without the carbonPressEnabled gate" % name)
            else:
                gated += 1
        ext = [li for li in (exts if exts is not None else []) if li.get("Class") == "RimMandrake.ColdStorage.ColdStorageEncaseExtension"]
        if not ext:
            continue
        worker = lookup(d, "workerClass")
        if worker is None or worker.text != ENCASE_WORKER:
            fails.append("%s: encase extension but workerClass is not %s (vanilla consumes the encased food)" % (name, ENCASE_WORKER))
        mode = ext[0].findtext("mode") or "Encase"
        if mode == "Encase":
            encase += 1
            prods = [p.tag for p in (d.find("products") or [])]
            if len(prods) != 1 or prods[0] not in packs:
                fails.append("%s: an encase recipe must make exactly one pack with CompEncased, makes %s" % (name, prods))
        else:
            release += 1
            taken = {li.text for li in d.iter("li") if li.text in packs}
            if taken != packs:
                fails.append("%s: the thaw recipe must take every pack; missing %s" % (name, sorted(packs - taken)))
    press = [d for d in root if d.findtext("defName") == "RSW_CarbonFreezingPress"]
    if len(press) != 1 or not any(li.get("Class") == "RimMandrake.ColdStorage.ColdStorageGateExtension" for li in press[0].iter("li")):
        fails.append("RSW_CarbonFreezingPress: missing, or without the carbonPressEnabled gate")
    if len(packs) != 4 or encase != 4 or release != 1 or gated < 7 or refs < 8:
        fails.append("carbon freeze check: packs=%d encase=%d release=%d gated=%d refs=%d, want 4/4/1/>=7/>=8 (instrument blind?)"
                     % (len(packs), encase, release, gated, refs))
    # Every key Encasing.cs translates is in Cold Storage's English keyed file.
    keyed = open(os.path.join(HERE, "Languages", "English", "Keyed", "ColdStorage.xml"), encoding="utf-8").read()
    enc = open(os.path.join(HERE, "Source", "Encasing.cs"), encoding="utf-8").read()
    for key in sorted(set(re.findall(r'"(RM_ColdStorage_\w+)"\.Translate', enc))):
        if "<%s>" % key not in keyed:
            fails.append("Encasing.cs: key %s missing from Keyed/ColdStorage.xml" % key)
    return fails


# RimWorld.FoodKind (decomp rw16 FoodKind.cs) has exactly these members; any other text is a red parse error at load
# and the field stays Any. FoodUtility.GetFoodKind(ThingDef) rates an animal product (egg) Any, never Meat.
FOOD_KINDS = ("Meat", "NonMeat", "Any")


def food_kind_checks(ET, files):
    """Every CompProperties_Ingredients.noIngredientsFoodKind names a real FoodKind; an egg good is Any, as vanilla
    rates eggs, so an ingredient-less one does not upset a vegetarian."""
    fails, seen = [], 0
    for path in files:
        for d in ET.parse(path).getroot():
            name = d.findtext("defName") or "?"
            for el in d.iter("noIngredientsFoodKind"):
                seen += 1
                kind = (el.text or "").strip()
                if kind not in FOOD_KINDS:
                    fails.append("%s: %s noIngredientsFoodKind %r is not a FoodKind %s"
                                 % (os.path.basename(path), name, kind, FOOD_KINDS))
                elif "Egg" in name and kind != "Any":
                    fails.append("%s: %s is an egg good but noIngredientsFoodKind %s (vanilla eggs are Any)"
                                 % (os.path.basename(path), name, kind))
    if seen < 20:
        fails.append("food kind check: only %d noIngredientsFoodKind found (instrument blind?)" % seen)
    return fails


def duplicate_comp_checks(ET, files):
    """XML inheritance APPENDS <li> list items (Verse.XmlInheritance), so a child that re-declares a comp its parent
    already has gets two of it: two CompIngredients write two <ingredients> save nodes, show the ingredients twice and
    the parent's noIngredientsFoodKind wins. Resolve Name parents across the seal files; one comp class per def."""
    fails = []
    named, concrete = {}, []
    for path in files:
        for d in ET.parse(path).getroot():
            if d.tag != "ThingDef":
                continue
            if d.get("Name"):
                named[d.get("Name")] = d
            if d.get("Abstract") != "True":
                concrete.append((os.path.basename(path), d))
    checked = 0
    for fname, d in concrete:
        classes, node = [], d
        while node is not None:
            comps = node.find("comps")
            if comps is not None:
                classes += [li.get("Class") for li in comps.findall("li") if li.get("Class")]
                if comps.get("Inherit") == "False":
                    break
            node = named.get(node.get("ParentName"))
        checked += 1
        dup = sorted({c for c in classes if classes.count(c) > 1})
        if dup:
            fails.append("%s: %s has duplicate comps %s (parent and child both declare it)" % (fname, d.findtext("defName"), dup))
    if checked < 20:
        fails.append("duplicate comp check: only %d concrete seal ThingDefs found (instrument blind?)" % checked)
    return fails


def main():
    fails = static_checks()
    for f in fails:
        print("FAIL static: " + f)
    print("coldstorage static checks: %d failed" % len(fails))
    dotnet = next((c for c in DOTNET if os.path.exists(c)), None)
    if dotnet is None:
        print("UNMEASURED: dotnet.exe not found; the C# selftest needs the Windows-side .NET SDK")
        return 2
    import winbuild
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="SelfTest_coldstorage")
    if rc:
        print("selftest build FAILED")
        return rc
    r = subprocess.run([dotnet, "run", "--project", winbuild.staged_win(rec, CSPROJ), "-c", "Release", "--no-build"],
                       capture_output=True, text=True)
    sys.stdout.write(r.stdout.replace("\r\n", "\n"))
    if r.stderr.strip():
        sys.stderr.write(r.stderr)
    return r.returncode or (1 if fails else 0)


if __name__ == "__main__":
    sys.exit(main())
