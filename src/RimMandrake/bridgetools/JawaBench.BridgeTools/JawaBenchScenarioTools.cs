// JawaBenchScenarioTools.cs — read and (GM-gated) mutate the RUNNING scenario.
//
// Written 2026-08-29 for EMPIRE_PURSUIT_SCENPART_INSTALL_1: the owner ruled a
// runtime insert of ScenPart_RuthlessPursuingMechanoids into Find.Scenario.parts.
// Scenario.parts is a private List<ScenPart>; the only public surface is
// AllParts. Everything here goes through reflection ONCE, cached, and every
// mutation reads the list back as its evidence.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimWorld;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private static FieldInfo _scenarioPartsField;

        private static List<ScenPart> ScenarioPartsList(Scenario s)
        {
            if (_scenarioPartsField == null)
                _scenarioPartsField = typeof(Scenario).GetField(
                    "parts", BindingFlags.Instance | BindingFlags.NonPublic);
            return _scenarioPartsField?.GetValue(s) as List<ScenPart>;
        }

        private static object DescribePart(ScenPart p)
        {
            var fields = new Dictionary<string, object>();
            foreach (var f in p.GetType().GetFields(
                         BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic))
            {
                if (f.Name == "def") continue;
                object v;
                try { v = f.GetValue(p); } catch { continue; }
                if (v == null) { fields[f.Name] = null; continue; }
                if (v is Def d) fields[f.Name] = d.defName;
                else if (v.GetType().IsPrimitive || v is string || v.GetType().IsEnum)
                    fields[f.Name] = v.ToString();
            }
            return new
            {
                className = p.GetType().FullName,
                def = p.def != null ? p.def.defName : null,
                summary = fields,
            };
        }

        [Tool(
            "jawa/scenario_parts_get",
            Description =
                "Read the RUNNING game's scenario: name and every ScenPart with its class, " +
                "def and scalar/Def-valued fields (read via reflection - the raw fields, not " +
                "a summary string). Read-only and safe on a live game.",
            ResultDescription = "success, scenarioName, parts[] {className, def, summary}.")]
        public static async Task<object> ScenarioPartsGet(
            IRimBridgeContext ctx, CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.Game == null || Find.Scenario == null)
                    return Fail("No game / scenario is loaded.");
                var list = ScenarioPartsList(Find.Scenario);
                if (list == null) return Fail("Could not reflect Scenario.parts.");
                return (object)new
                {
                    success = true,
                    scenarioName = Find.Scenario.name,
                    partCount = list.Count,
                    parts = list.Select(DescribePart).ToList(),
                    ticksGame = TicksGameSafe(),
                };
            });
        }

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/scenario_part_add",
            Description =
                "Append a ScenPart to the RUNNING scenario by class name, set its fields, and " +
                "read the whole parts list back as evidence. The part starts working immediately " +
                "and is scribed into the next save. Defaults to dryRun=true - pass dryRun=false " +
                "to mutate. REFUSES: an unknown class, an unknown ScenPartDef, an unknown field " +
                "name, an unconvertible value, or a part of the same class already present " +
                "(pass allowDuplicate=true to override). ⚠ Removing a part has no tool; that is " +
                "a savegame edit by design.",
            ResultDescription =
                "success, added {className, def, summary}, partCount, parts[] read back.")]
        public static async Task<object> ScenarioPartAdd(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "Full class name, e.g. 'RimMandrake.Utinni.EmpirePursuit.ScenPart_RuthlessPursuingMechanoids'.")]
            string className = null,
            [ToolParameter(Description = "ScenPartDef defName to assign to the part's def field.")]
            string defName = null,
            [ToolParameter(Description = "Fields to set, as 'name=value' joined by ';' (e.g. 'pursuitFactionDef=Empire;canDoNormalRaid=true;firstRaidDelayHours=156'). Def-typed fields take a defName; bools true/false; numbers plain.")]
            string fields = null,
            [ToolParameter(Description = "Allow a second part of the same class. Default false.")]
            bool allowDuplicate = false,
            [ToolParameter(Description = "Lifecycle calls to run after adding, ';'-joined, in order, from: PostWorldGenerate, PostGameStart, PostMapGenerate (runs once per current map). A part added MID-GAME never gets these from the engine, and most parts arm their state there - ScenPart_RuthlessPursuingMechanoids needs 'PostWorldGenerate;PostMapGenerate' or its timer dicts stay empty and it never fires. Default: none.")]
            string initCalls = null,
            [ToolParameter(Description = "Report what would happen without mutating. Default TRUE.")]
            bool dryRun = true)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.Game == null || Find.Scenario == null)
                    return Fail("No game / scenario is loaded.");
                if (string.IsNullOrEmpty(className)) return Fail("className is required.");

                Type partType = GenTypes.GetTypeInAnyAssembly(className);
                if (partType == null || !typeof(ScenPart).IsAssignableFrom(partType))
                    return Fail("No ScenPart class named '" + className + "' in any loaded assembly.");

                var list = ScenarioPartsList(Find.Scenario);
                if (list == null) return Fail("Could not reflect Scenario.parts.");
                if (!allowDuplicate && list.Any(p => p.GetType() == partType))
                    return Fail("A " + partType.Name + " is already in the scenario. " +
                                "Pass allowDuplicate=true to add another.",
                                new { existing = list.Where(p => p.GetType() == partType)
                                                     .Select(DescribePart).ToList() });

                ScenPartDef def = null;
                if (!string.IsNullOrEmpty(defName))
                {
                    def = DefDatabase<ScenPartDef>.GetNamedSilentFail(defName);
                    if (def == null)
                        return Fail("No ScenPartDef named '" + defName + "'.",
                                    DefSuggestions<ScenPartDef>(defName));
                }

                var part = (ScenPart)Activator.CreateInstance(partType);
                part.def = def;

                var applied = new Dictionary<string, object>();
                if (!string.IsNullOrEmpty(fields))
                {
                    foreach (var pair in fields.Split(';'))
                    {
                        if (string.IsNullOrWhiteSpace(pair)) continue;
                        int eq = pair.IndexOf('=');
                        if (eq <= 0) return Fail("Field spec '" + pair + "' is not name=value.");
                        string fname = pair.Substring(0, eq).Trim();
                        string fval = pair.Substring(eq + 1).Trim();
                        FieldInfo fi = partType.GetField(
                            fname, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
                        if (fi == null)
                            return Fail("Class " + partType.Name + " has no field '" + fname +
                                        "'. Fields: " + string.Join(", ",
                                            partType.GetFields(BindingFlags.Instance |
                                                BindingFlags.Public | BindingFlags.NonPublic)
                                            .Select(f => f.Name).Where(n => n != "def")));
                        object converted;
                        try
                        {
                            if (typeof(Def).IsAssignableFrom(fi.FieldType))
                            {
                                converted = GenDefDatabase.GetDefSilentFail(fi.FieldType, fval, false);
                                if (converted == null)
                                    return Fail("No " + fi.FieldType.Name + " named '" + fval +
                                                "' for field " + fname + ".");
                            }
                            else if (fi.FieldType.IsEnum)
                                converted = Enum.Parse(fi.FieldType, fval, true);
                            else
                                converted = Convert.ChangeType(
                                    fval, fi.FieldType,
                                    System.Globalization.CultureInfo.InvariantCulture);
                        }
                        catch (Exception e)
                        {
                            return Fail("Could not convert '" + fval + "' for field " + fname +
                                        " (" + fi.FieldType.Name + "): " + e.Message);
                        }
                        fi.SetValue(part, converted);
                        applied[fname] = fval;
                    }
                }

                if (dryRun)
                    return (object)new
                    {
                        success = true, dryRun = true,
                        wouldAdd = DescribePart(part), fieldsApplied = applied,
                        note = "DRY RUN - nothing was added. Pass dryRun=false to mutate.",
                        ticksGame = TicksGameSafe(),
                    };

                var wantedInits = (initCalls ?? "").Split(';')
                    .Select(s => s.Trim()).Where(s => s.Length > 0).ToList();
                var unknown = wantedInits
                    .Where(s => s != "PostWorldGenerate" && s != "PostGameStart"
                             && s != "PostMapGenerate").ToList();
                if (unknown.Any())
                    return Fail("Unknown initCalls: " + string.Join(", ", unknown) +
                                ". Allowed: PostWorldGenerate, PostGameStart, PostMapGenerate. " +
                                "Nothing was added.");

                list.Add(part);

                var initRan = new List<string>();
                foreach (var callName in wantedInits)
                {
                    switch (callName)
                    {
                        case "PostWorldGenerate":
                            part.PostWorldGenerate(); initRan.Add("PostWorldGenerate"); break;
                        case "PostGameStart":
                            part.PostGameStart(); initRan.Add("PostGameStart"); break;
                        case "PostMapGenerate":
                            foreach (Map m in Find.Maps)
                            {
                                part.PostMapGenerate(m);
                                initRan.Add("PostMapGenerate(" + m.uniqueID + ")");
                            }
                            break;
                    }
                }

                var readBack = ScenarioPartsList(Find.Scenario);
                return (object)new
                {
                    success = true, dryRun = false,
                    added = DescribePart(part), fieldsApplied = applied, initRan,
                    partCount = readBack.Count,
                    parts = readBack.Select(DescribePart).ToList(),
                    note = "Part appended and PostAdded() called. It scribes into the next save; " +
                           "verify by saving and grepping the .rws for the class name.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }
#endif // JAWA_GM_TOOLS
    }
}
