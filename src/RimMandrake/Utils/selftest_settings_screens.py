#!/usr/bin/env python3
"""MOD_OPTIONS_RETROFIT_1 offline check for the SettingsKit settings screens retrofitted onto a mod's own Mod file.

For each mod listed in MODS below: every setting the settings class Scribes sits inside exactly one named Group(...) block whose
names array lists it (so it collapses, searches and resets with its group); every control drawn in a block is listed by it;
groups are brace-balanced and do not swallow the next group; the group scope tags equal the AUDITED scopes recorded here (the
audit is per setting, against its read site: a worldgen step is NewMapsOnly, a Gale-onset or storyteller-roll read is
NextPulse, a tick/job/patch read is Now); the SettingsKit files are in the csproj; the shippedDefaults snapshot exists.
Then plants one defect at a time per mod and requires the check to fail on each.

Add a mod by adding one entry to MODS.     python3 src/RimMandrake/Utils/selftest_settings_screens.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# folder, mod .cs, csproj, expected groups: title -> scope (the audited scopes)
# folder: (mod .cs, csproj, expected groups, extra setting names the screen resets that are not Scribe_Values fields)
MODS = {
    "GimmeSomeSlack#Cables": ("GimmeSomeSlackMod.cs", "RimMandrake_GimmeSomeSlack.csproj", {
        "Messy cords and default style": "Now",
        "Slack, loops and tangles": "Now",
        "Breaks and sparks": "Now",
        "Wind sway": "Now",
        "Far zoom and debug": "Now",
    }, ()),
    "GimmeSomeSlack#Aerial": ("Aerial/AerialSettings.cs", "RimMandrake_GimmeSomeSlack.csproj", {
        "Overhead power lines": "Now",
        "Wire sway": "Now",
        "Damage, shock and alerts": "Now",
        "Power-tap clamps": "Now",
    }, ()),
    "GimmeSomeSlack#Hose": ("Hose/HoseSettings.cs", "RimMandrake_GimmeSomeSlack.csproj", {
        "Flexible hoses": "Now",
        "Hose length and shape": "Now",
        "Colonists carrying hoses": "Now",
        "Look and FlowWorks": "Now",
    }, ()),
    "Graffiti": ("RM_GraffitiMod.cs", "Graffiti.csproj", {
        "Painting": "Now",
        "Viewer reactions": "Now",
        "Raiders": "Now",
        "Cleaning": "Now",
    }, ()),
    "LeaningScrub": ("RM_LeaningScrubMod.cs", "RM_LeaningScrub.csproj", {
        "Mod and venomvine passability": "Now",
        "The Stall and the Gale": "Now",
        "Gale raid weighting": "NextPulse",
        "Twitcher venomvine": "Now",
        "Smother-craft": "Now",
        "The Lean (wind heading)": "Now",
        "Venomvine rooms and the runway bloom": "Now",
        "Sweetline trees": "Now",
        "Sweetline trees on new maps": "NewMapsOnly",
        "Vissler arms and fire-stamping giants": "Now",
        "Venomvine forms": "Now",
        "Forms that act when the Gale starts": "NextPulse",
    }, ()),
    "LanternDeeps": ("LanternDeepsMod.cs", "RM_LanternDeeps.csproj", {
        "Entrances: cave mouth and ruined mineshaft": "NewMapsOnly",
        "Darkness inside a Deep": "Now",
        "Newly generated Deeps: crystal, dead and galuush": "NewMapsOnly",
        "Flora and deposits": "Now",
        "Shard-minds, Orun-Ghal and the Answering": "Now",
        "Methane, the Creep and Cleavers": "Now",
        "Aurora, roofs and cave fauna": "Now",
        "Entrance biomes (world generation)": "NewMapsOnly",
    }, ("entranceBiomes",)),
    "Greentide": ("RM_GreentideMod.cs", "RM_Greentide.csproj", {
        "Churnmud and the mire": "Now",
        "Jungle density": "NewMapsOnly",
        "World-map movement": "Now",
        "Cross-biome opt-in (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "The Frenzy": "Now",
        "Jungle grenades": "Now",
        "Canopy swarm (the krannock)": "Now",
        "Stellock lace": "Now",
        "The shoal (the illisk)": "Now",
        "The false bank (the vurrak)": "Now",
        "The canopy-breaker (the thurrock)": "Now",
        "The Roil (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Greatbole fruitfall and harvest ladder": "Now",
        "Greatbole seeds and servants": "NextGameStart",
    }, ()),
    "Miasma": ("RM_MiasmaMod.cs", "RM_Miasma.csproj", {
        "Biome rarity (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Warden mother young": "Now",
        "Predators and pollination": "Now",
        "Flotsam in the root-lines": "Now",
        "Attar: still, glaze and balm": "Now",
        "Decay cells and the rotting bed": "Now",
        "The mother's price": "Now",
    }, ()),
    "Abyss": ("RM_AbyssMod.cs", "RM_Abyss.csproj", {
        "Biome rarity (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Gharreks, sorters and krizzaks": "Now",
        "Sorter dens on new maps": "NewMapsOnly",
        "Summs and ombrathias": "Now",
        "Ishvariths and light": "Now",
        "The Dark": "Now",
        "Etchfall": "Now",
        "The hidden ship": "Now",
        "Wickwood lamp crops": "NextGameStart",
        "Fold-lamps": "Now",
        "Heat-folding discovery": "NextGameStart",
        "Sound": "Now",
        "Cryptid signs": "Now",
        "Brood lair switch": "Now",
        "Brood lair details (fixed at map generation)": "NewMapsOnly",
        "Stolen egg and bonded summ": "Now",
    }, ()),
    "Contagion": ("RM_ContagionMod.cs", "RM_Contagion.csproj", {
        "Biome rarity (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Genome growing and the Unfinished": "Now",
        "The Burn": "Now",
        "Burn frequency": "NextPulse",
        "The Coalescence": "Now",
        "Draftprints": "Now",
        "Helix contract pay": "NextPulse",
        "Helix devices": "Now",
    }, ()),
    "Cauldron": ("RM_CauldronMod.cs", "RM_Cauldron.csproj", {
        "Biome rarity (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Metal in the trees": "Now",
        "Vent bloom exposure": "Now",
        "Vexxiss behaviour": "Now",
        "Nettle shorelines": "Now",
        "Ground vents (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Vents and what hangs on them": "Now",
        "Vent silence length": "NextPulse",
        "Dewfall": "Now",
        "Flora expansion and fexxil venom": "NextGameStart",
        "Vexxith acid-proofing": "Now",
        "Acid-proof vexxith door": "NextGameStart",
    }, ()),
    "Pyrelands": ("RM_PyrelandsMod.cs", "FireEcologyHook.csproj", {
        "Mod enabled": "Now",
        "Fulgurite, loose ash and scorch-fruit": "Now",
        "Ash accumulation (Ash Fall / Cinderfall weather)": "Now",
        "Plant art and wild flora": "Now",
        "Scorched ruins (new maps)": "NewMapsOnly",
        "Biome placement (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Absorbed mechanics (mandrake.rut.pyrelandsmechanics)": "Now",
        "Furnace-beast herds at world start (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Giants and recipe costs (restart)": "NextGameStart",
        "Burrowers": "Now",
        "Lightning breakers and sand shovelling": "Now",
        "Cross-biome ash accumulation": "Now",
    }, ()),
    "GelatinousSlime": ("SlimeMod.cs", "RM_GelatinousSlime.csproj", {
        "The gene archive": "Now",
        "Biome rarity (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Flavour": "Now",
        "Slimification and fields": "Now",
        "Ruined farms (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Joining Water ring": "Now",
        "Visitors": "Now",
        "Creatures and the slime pit": "Now",
        "Titanoslime chunks and the archive vat": "Now",
        "The titanoslime": "Now",
        "Titanoslime rarity (WORLDGEN-AFFECTING)": "NewMapsOnly",
    }, ()),
    "TheRot": ("RM_TheRotMod.cs", "RM_TheRot.csproj", {
        "The Rot enabled": "Now",
        "Sheen, rot, heat and spores": "Now",
        "Wild spawns and kin bonds (restart)": "NextGameStart",
        "Giant: the hwelgrue": "Now",
        "Ship: the swallowed navigator": "Now",
        "Technology: the gut-mother and the unjoining draught": "Now",
        "Cross-biome opt-in": "Now",
    }, ()),
    "TheForge": ("RM_TheForgeMod.cs", "RM_TheForge.csproj", {
        "The Forge enabled": "Now",
        "Weather pulse and grand cycle": "Now",
        "Keelwork and spunstone study": "Now",
        "Spunstone door and hull (restart)": "NextGameStart",
        "Voices and the dhuvvox": "Now",
        "White plume fronts": "Now",
        "Vapour columns and sky creatures": "Now",
        "The dhokkur": "Now",
        "Not wired yet (these change nothing)": "Now",
    }, ()),
    "ShipVermin": ("RM_ShipVerminMod.cs", "RM_ShipVermin.csproj", {
        "Alert and fuel mites": "Now",
        "Wreck-anchored vermin nests": "Now",
        "Species a wreck nest may produce": "Now",
    }, ()),
    "Wasteland": ("RM_WastelandMod.cs", "RM_Wasteland.csproj", {
        "Wasteland master switch": "Now",
        "Storms": "Now",
        "Ambient dose and radiothermal heat": "Now",
        "Processor animals": "Now",
        "Grippers": "Now",
        "The Middenshell": "Now",
        "Waste casks and the sealed cask bay": "Now",
        "Rite of Tipping": "Now",
        "Not wired yet (these change nothing)": "Now",
    }, ()),
}

# (field, key) pairs where the Scribe key was renamed on purpose when the field's meaning changed (old saved values must not load)
DELIBERATE_KEY_RENAMES = {("scorchFruitChance", "scorchFruitChancePerCell")}


def check(cs, csproj, expected, extra=()):
    errs = []
    scribed = set(re.findall(r'Scribe_Values\.Look\(ref (\w+), "(\w+)"', cs))
    for field, key in scribed:
        if field != key and (field, key) not in DELIBERATE_KEY_RENAMES:
            errs.append(f"scribe key {key!r} != field {field!r}")
    scribed = {f for f, _ in scribed} | set(extra)
    a = cs.index("public void DoWindowContents")
    body = cs[a:cs.index("list.End();", a)]
    groups = []   # (title, scope, names, text)
    for m in re.finditer(r'if \(Group\(list, "([^"]+)", [\w.]*SettingScope\.(\w+), new\[\] \{ ([^}]*) \}(?:, "(\[[a-z ]+\])")?\)', body):
        names = re.findall(r'"(\w+)"', m.group(3))
        i = body.index("{", m.end())          # the block's opening brace (the line after the if(...))
        depth, j = 0, i
        while j < len(body):
            depth += body[j] == "{"
            depth -= body[j] == "}"
            j += 1
            if depth == 0:
                break
        else:
            errs.append(f"group {m.group(1)!r}: unbalanced braces")
        if "if (Group(" in body[i:j]:
            errs.append(f"group {m.group(1)!r}: swallows the next group (a closing brace is missing)")
        scope = {"[next game start]": "NextGameStart"}.get(m.group(4), m.group(2))   # a tag override is the audited label
        groups.append((m.group(1), scope, names, body[i:j]))
    got = {t: s for t, s, _, _ in groups}
    if len(groups) != len(expected):
        errs.append(f"{len(groups)} groups found, expected {len(expected)}")
    for t, s in expected.items():
        if t not in got:
            errs.append(f"group {t!r} missing")
        elif got[t] != s:
            errs.append(f"group {t!r} scope tag {got[t]} but the audited scope is {s}")
    seen = {}
    for title, _, names, text in groups:
        for n in names:
            if n in seen:
                errs.append(f"{n} listed in two groups: {seen[n]!r} and {title!r}")
            seen[n] = title
            if n not in scribed:
                errs.append(f"group {title!r} names {n}, which is not a Scribed setting")
        drawn = set(re.findall(r'ref (\w+)\b', text)) | set(re.findall(r'(\w+) = (?:\(int\)|Mathf\.\w+\()?list\.Slider', text))
        for d in drawn - set(names):
            errs.append(f"group {title!r} draws {d} but does not list it (it would not reset)")
    for f in scribed:
        if f not in seen:
            errs.append(f"setting {f} is in no group (no reset, not searchable)")
    for kit in ("SettingsKitCore.cs", "SettingsKitDrawer.cs"):
        if kit not in csproj:
            errs.append(f"csproj lacks the {kit} Compile Include")
    if "private static readonly Dictionary<string, object> shippedDefaults" not in cs:
        errs.append("no shippedDefaults snapshot for per-group reset")
    if "SettingsKitDrawer.SearchBox" not in cs:
        errs.append("no search box")
    return errs, groups


def run_mod(name, cs_name, pj_name, expected, extra):
    src = os.path.join(ROOT, name.split("#")[0], "Source")
    cs = open(os.path.join(src, cs_name), encoding="utf-8").read()
    pj = open(os.path.join(src, pj_name), encoding="utf-8").read()
    bad = total = 0
    e, groups = check(cs, pj, expected, extra)
    total += 1
    print(("ok   " if not e else "FAIL ") + f"{name}: real screen, every setting grouped, resettable, scopes as audited" + ("" if not e else " | " + "; ".join(e[:4])))
    bad += bool(e)
    g0, g1 = groups[0], groups[1]
    last0 = g0[2][-1]
    scope_swap = next(((t, s) for t, s in expected.items() if s not in ("Now", "NextGameStart")), None)
    plants = [
        ("a name dropped from its group array", lambda c, p: (c.replace(f', "{last0}" }}', ' }', 1) if f', "{last0}" }}' in c else c.replace(f'"{last0}" }}', ' }', 1), p), "no group"),
        ("a setting in two groups", lambda c, p: (c.replace(f'"{g1[0]}", RimMandrake.Shared.SettingScope.{g1[1]}, new[] {{ ', f'"{g1[0]}", RimMandrake.Shared.SettingScope.{g1[1]}, new[] {{ "{g0[2][0]}", ', 1), p), "two groups"),
        ("group names a non-setting", lambda c, p: (c.replace(f'"{last0}" }}', '"notASettingAtAll" }', 1), p), "not a Scribed setting"),
        ("a Group's closing brace lost", lambda c, p: (c.replace('                list.GapLine();\n            }\n', '                list.GapLine();\n', 1), p), "swallows"),
        ("kit dropped from the csproj", lambda c, p: (c, p.replace("SettingsKitDrawer.cs", "SettingsKitDrawr.cs")), "SettingsKitDrawer.cs"),
        ("snapshot removed", lambda c, p: (c.replace("shippedDefaults = SnapshotDefaults()", "shippedDefaultz = SnapshotDefaults()"), p), "shippedDefaults"),
    ]
    if scope_swap:
        t, s = scope_swap
        plants.append(("a scope tag flipped to a dishonest one", lambda c, p: (c.replace(f'"{t}", RimMandrake.Shared.SettingScope.{s}', f'"{t}", RimMandrake.Shared.SettingScope.Now', 1), p), "audited scope"))
    if "NextGameStart" in expected.values():
        plants.append(("a next-game-start tag overridden to [now]", lambda c, p: (c.replace('"[next game start]"))', '"[now]"))', 1), p), "audited scope"))
    for label, f, want in plants:
        c2, p2 = f(cs, pj)
        total += 1
        if (c2, p2) == (cs, pj):
            print(f"FAIL {name}: {label}: pattern not found")
            bad += 1
            continue
        try:
            e, _ = check(c2, p2, expected, extra)
        except Exception as ex:   # a broken file must still be a failure, not a crash
            e = [f"exception {ex}"]
        hit = any(want in x for x in e)
        print(("ok   " if hit else "FAIL ") + f"{name}: {label}" + ("" if hit else f" | wanted {want!r}, got {e[:2]}"))
        bad += not hit
    return bad, total


def main():
    bad = total = 0
    for name, (cs_name, pj_name, expected, extra) in MODS.items():
        b, t = run_mod(name, cs_name, pj_name, expected, extra)
        bad += b
        total += t
    print(f"settings screens selftest: {total - bad}/{total} ok")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
