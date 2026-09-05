// JawaBenchTypeInspect.cs - name the mod whose init-time code (not a Harmony patch) is
// responsible for behaviour that has no XML and no vendored/decompiled source explanation.
//
// WILD_ANIMALS_PADDED_LISTS_1
// ============================
// jawa/harmony_patches enumerated every patched method anywhere near the def-load / XML-
// inheritance / def-generation pipeline (BiomeDef, DefGenerator, GenDefDatabase,
// DirectXmlLoader.DefFromNode, ShortHashGiver, all of LoadedModManager) and none of them can
// write 1024 raw BiomeDef.wildAnimals records. That pass's own conclusion: the mechanism is
// very likely NOT a Harmony patch at all - ordinary reflection
// (typeof(BiomeDef).GetField("wildAnimals", ...).SetValue(...)) from a
// [StaticConstructorOnStartup] class or a Mod-derived subclass's constructor (RimWorld calls
// both after defs finish loading) would never show up in Harmony's patch table. This file is
// the enumerator for those two categories that jawa/harmony_patches cannot see.
//
// EVERY SIGNATURE READ FROM 1.6 SOURCE, NOT REMEMBERED:
//   - Verse/GenTypes.cs: AllTypesWithAttribute<TAttr>() and the AllSubclassesNonAbstract()
//     extension method, both iterating the same GenTypes.AllTypes list Root.cs itself uses.
//   - Verse/StaticConstructorOnStartup.cs: the attribute class itself.
//   - Verse/Mod.cs: the abstract base every mod's settings/init class derives from.
//   - Verse/LoadedModManager.cs: RunningModsListForReading, and ModContentPack.assemblies.
//     loadedAssemblies - the same per-mod assembly LIST jawa/mod_inventory reads. This file's
//     own join direction is different and riskier: it flattens every mod's assemblies into one
//     REVERSE (assembly name -> mod) dictionary, which has a last-writer-wins collision surface
//     jawa/mod_inventory's forward per-mod list does not (see ambiguousAssemblies below).
//
// THREAD AFFINITY: LoadedModManager.RunningModsListForReading is touched here (not just pure
// reflection over already-resolved MethodBase objects the way jawa/harmony_patches is), so
// this follows jawa/mod_inventory's more conservative precedent and stays inside
// ctx.MainThread.InvokeAsync rather than jawa/harmony_patches' narrower exception.
//
// ⛔ NO jawa/ PREFIXES IN PROSE ANYWHERE IN THIS FILE'S DESCRIPTIONS other than an EXACT,
// REAL tool name. build.py scans the assembly for jawa/... literals and a partial mention
// becomes a phantom tool name.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private sealed class StartupTypeRow
        {
            public string TypeName;
            public string Kind;
            public string AssemblyName;
            public string ModName;
            public string ModPackageId;
            public int? ModLoadOrder;
        }

        [Tool(
            "jawa/startup_types",
            Description =
                "READ ONLY. Lists every type carrying [StaticConstructorOnStartup] and/or every " +
                "non-abstract subclass of Verse.Mod, across the WHOLE PROCESS, each joined to the " +
                "running mod that owns its declaring assembly (same assembly/mod join " +
                "jawa/mod_inventory uses). Both categories run init-time code after defs finish " +
                "loading via ordinary reflection, with no Harmony involvement - use this when " +
                "jawa/harmony_patches comes back clean on every method near the def-load pipeline " +
                "and the remaining suspect is a static ctor or a Mod subclass's constructor doing " +
                "a GetField/SetValue pass. Excludes the base game's own Assembly-CSharp by default " +
                "(953+ vanilla entries, all irrelevant to a mod-caused mutation) - set " +
                "excludeVanilla=false to include them. ⛔ Cannot see what a constructor actually " +
                "DOES, only that it exists and which mod owns it - correlate against a decompile " +
                "or a targeted field/property read once a suspect is named.",
            ResultDescription =
                "success, kind, filter, excludeVanilla, count, types[] each {typeName, kind " +
                "('StaticCtor' or 'ModSubclass'), assemblyName, modName, modPackageId, modLoadOrder}. " +
                "modName/modPackageId are null when the assembly does not match any running mod's " +
                "loadedAssemblies (dynamically-generated or reflection-emitted assembly) - " +
                "ambiguousAssemblies[] names any assembly short name TWO OR MORE running mods loaded, " +
                "where the reported owner is only the first in load order (real but rare: two mods " +
                "shipping a same-named DLL). modAssemblyErrors[] surfaces any exception reading a mod's " +
                "own assembly list, so a missing mod attribution can be told apart from a genuine " +
                "dynamic assembly. note is set instead of an empty count meaning nothing matched.")]
        public static async Task<object> StartupTypes(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Which category to list: 'staticctor' ([StaticConstructorOnStartup] types only), " +
                "'modsubclass' (non-abstract Verse.Mod subclasses only), or 'both' (default).")]
            string kind = "both",
            [ToolParameter(Description =
                "Keep only rows whose type full name, assembly name, mod name or mod packageId " +
                "contains this (case-insensitive). Empty returns all matching rows.")]
            string filter = null,
            [ToolParameter(Description =
                "Exclude rows whose declaring assembly is 'Assembly-CSharp' (the base game itself). " +
                "Default true - the vanilla list is large (953+ StaticConstructorOnStartup sites) " +
                "and never the culprit for a mod-introduced def mutation.")]
            bool excludeVanilla = true)
        {
            cancellationToken.ThrowIfCancellationRequested();

            var normalizedKind = (kind ?? "both").Trim().ToLowerInvariant();
            var wantStaticCtor = normalizedKind == "staticctor" || normalizedKind == "both";
            var wantModSubclass = normalizedKind == "modsubclass" || normalizedKind == "both";
            if (!wantStaticCtor && !wantModSubclass)
                return Fail("kind must be 'staticctor', 'modsubclass' or 'both' - got '" + kind + "'.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();

                var runningMods = LoadedModManager.RunningModsListForReading;
                if (runningMods == null) return Fail("LoadedModManager.RunningModsListForReading is null.");

                // assembly short name -> (mod name, packageId, loadOrder). Unlike jawa/mod_inventory's
                // forward per-mod list, this flattens every mod into one reverse dictionary, which CAN
                // collide if two running mods ship a same-named assembly. First mod in load order wins
                // (deterministic), and every losing name is reported in ambiguousAssemblies below rather
                // than silently mis-attributing that assembly's types to the wrong mod.
                var assemblyToMod = new Dictionary<string, (string name, string packageId, int loadOrder)>(
                    StringComparer.OrdinalIgnoreCase);
                var ambiguousAssemblies = new List<string>();
                var modAssemblyErrors = new List<string>();
                foreach (var mod in runningMods)
                {
                    List<System.Reflection.Assembly> asms;
                    try { asms = mod.assemblies?.loadedAssemblies; }
                    catch (Exception ex)
                    {
                        asms = null;
                        modAssemblyErrors.Add((mod.Name ?? mod.PackageId ?? "?") + ": " + ex.GetType().Name + ": " + ex.Message);
                    }
                    if (asms == null) continue;
                    foreach (var asm in asms)
                    {
                        string asmName;
                        try { asmName = asm?.GetName()?.Name; }
                        catch (Exception ex)
                        {
                            modAssemblyErrors.Add((mod.Name ?? mod.PackageId ?? "?") + " assembly GetName(): " + ex.GetType().Name + ": " + ex.Message);
                            continue;
                        }
                        if (string.IsNullOrEmpty(asmName)) continue;
                        if (assemblyToMod.ContainsKey(asmName))
                            ambiguousAssemblies.Add(asmName);
                        else
                            assemblyToMod[asmName] = (mod.Name, mod.PackageId, mod.loadOrder);
                    }
                }

                List<Type> staticCtorTypes = new List<Type>();
                string staticCtorError = null;
                if (wantStaticCtor)
                {
                    try { staticCtorTypes = GenTypes.AllTypesWithAttribute<StaticConstructorOnStartup>(); }
                    catch (Exception ex) { staticCtorError = ex.GetType().Name + ": " + ex.Message; }
                }

                List<Type> modSubclassTypes = new List<Type>();
                string modSubclassError = null;
                if (wantModSubclass)
                {
                    try { modSubclassTypes = typeof(Mod).AllSubclassesNonAbstract(); }
                    catch (Exception ex) { modSubclassError = ex.GetType().Name + ": " + ex.Message; }
                }

                StartupTypeRow RowFor(Type t, string rowKind)
                {
                    string asmName;
                    try { asmName = t.Assembly?.GetName()?.Name; } catch { asmName = null; }
                    // Filtered by excludeVanilla BEFORE this runs (see below) - only non-vanilla types
                    // (or all types, if excludeVanilla=false) ever reach RowFor's dictionary lookup.
                    assemblyToMod.TryGetValue(asmName ?? "", out var owner);
                    string typeName;
                    try { typeName = t.FullName ?? t.Name; } catch { typeName = t.Name ?? "?"; }
                    return new StartupTypeRow
                    {
                        TypeName = typeName,
                        Kind = rowKind,
                        AssemblyName = asmName,
                        ModName = owner.name,
                        ModPackageId = owner.packageId,
                        ModLoadOrder = owner.packageId != null ? (int?)owner.loadOrder : null
                    };
                }

                bool IsVanilla(Type t)
                {
                    string asmName;
                    try { asmName = t.Assembly?.GetName()?.Name; } catch { return false; }
                    return string.Equals(asmName, "Assembly-CSharp", StringComparison.OrdinalIgnoreCase);
                }

                // Filter BEFORE RowFor, not after - excludeVanilla defaults to true and the vanilla set
                // is 953+ types; building a row (dictionary lookup + allocation) for every one of them
                // only to discard it on every single call would be pure waste.
                if (excludeVanilla)
                {
                    staticCtorTypes = staticCtorTypes.Where(t => !IsVanilla(t)).ToList();
                    modSubclassTypes = modSubclassTypes.Where(t => !IsVanilla(t)).ToList();
                }

                IEnumerable<StartupTypeRow> rows = staticCtorTypes.Select(t => RowFor(t, "StaticCtor"))
                    .Concat(modSubclassTypes.Select(t => RowFor(t, "ModSubclass")));

                if (!string.IsNullOrWhiteSpace(filter))
                {
                    var f = filter.Trim();
                    bool Contains(string s) => !string.IsNullOrEmpty(s) && s.IndexOf(f, StringComparison.OrdinalIgnoreCase) >= 0;
                    rows = rows.Where(r => Contains(r.TypeName) || Contains(r.AssemblyName)
                        || Contains(r.ModName) || Contains(r.ModPackageId));
                }

                var list = rows.Select(r => (object)new
                {
                    typeName = r.TypeName,
                    kind = r.Kind,
                    assemblyName = r.AssemblyName,
                    modName = r.ModName,
                    modPackageId = r.ModPackageId,
                    modLoadOrder = r.ModLoadOrder
                }).ToList();

                return new
                {
                    success = true,
                    kind = normalizedKind,
                    filter,
                    excludeVanilla,
                    count = list.Count,
                    types = list,
                    ambiguousAssemblies,
                    modAssemblyErrors,
                    staticCtorError,
                    modSubclassError,
                    ticksGame = TicksGameSafe(),
                    note = list.Count == 0
                        ? "No row matched. Either nothing of this kind is loaded, or 'filter'/'kind' did not match - check spelling."
                        : null
                };
            }).ConfigureAwait(false);
        }
    }
}
