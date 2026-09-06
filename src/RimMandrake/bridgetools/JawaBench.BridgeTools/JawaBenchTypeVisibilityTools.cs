// JawaBenchTypeVisibilityTools.cs - is a given type actually IN GenTypes.AllTypes, and if
// not, exactly why.
//
// FLUID_CANAL_DEBUG_SURFACE_1. FluidCanals' [DebugAction]s never appear in the dev menu,
// while the same mod's defs resolve fine and its assembly loads with no logged error. The
// item's own round-2 investigation established that these are two INDEPENDENT paths and
// ran out of things reading could settle:
//
//   * Def / custom-DefType resolution goes through GenTypes.GetTypeInAnyAssembly, which on
//     a cache miss iterates AllActiveAssemblies FRESH on every call. So "FluidDef resolves"
//     says nothing about AllTypes.
//   * The debug-action scan (LudeonTK/DebugTabMenu_Actions.InitActions) is the only consumer
//     that walks GenTypes.AllTypes - a lazily-built, cached List<Type>.
//
// 🔑 THE MECHANISM THIS TOOL EXISTS TO DECIDE, read out of Verse/GenTypes.cs. When an
// assembly's GetTypes() throws ReflectionTypeLoadException, AllTypes falls back to:
//
//     array = ex.Types.Where(x => x != null && x.TypeInitializer != null).ToArray();
//
// ⛔ `x.TypeInitializer != null` silently DROPS every surviving type that has no static
// constructor - and a `static class` whose only members are consts and methods has no
// .cctor at all. FluidCanalsDebugActions is exactly that shape. So one unresolvable
// reference anywhere in the assembly can delete the debug-action class from AllTypes while
// leaving every type that happens to own a static field. That is a per-type drop with no
// load-order dependency, which matches the symptom the item measured (moving the mod from
// position 19 to 14 changed nothing).
//
// It logs "Exception getting types in assembly ..." when it happens - but that line names
// whichever assembly threw, and the repro session's log is gone, so the question is open.
//
// WHAT THIS ANSWERS, IN ONE CALL: whether the assembly is in AllActiveAssemblies at all,
// whether its GetTypes() throws (and what the loader exceptions actually say), whether the
// type is in AllTypes, and whether its TypeInitializer is null - i.e. whether it is exactly
// the kind of type that fallback path discards. It also counts the [DebugAction] methods on
// it, so "the class is there but carries no actions" is distinguishable from "the class is
// gone".
//
// ⚠️ It reports rather than concludes. `typeInAllTypes=false` with `getTypesThrew=true` and
// `typeInitializerNull=true` is the confirmation; any other combination refutes this theory
// and the next probe goes elsewhere.
//
// THREAD AFFINITY: reflection over loaded types only - no Map, Pawn or Thing - so this does
// not hop the main thread, for the same reason jawa/debug_actions does not.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using LudeonTK;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/type_visibility",
            Description =
                "Report whether a type is present in GenTypes.AllTypes - the cached list the " +
                "dev-menu debug-action scan walks - and if it is missing, why. Answers the " +
                "question a def lookup CANNOT: def resolution uses a different code path " +
                "(GetTypeInAnyAssembly, fresh every call), so a def resolving proves nothing " +
                "about AllTypes. Names the assembly, says whether its GetTypes() throws and what " +
                "the loader exceptions are, and reports TypeInitializer - because AllTypes' " +
                "recovery path keeps only types WITH a static constructor, silently dropping any " +
                "static class that has none. Executes nothing.",
            ResultDescription =
                "success, typeName, found flags (assemblyFound / typeInAllTypes / " +
                "typeInAssemblyGetTypes / typeInitializerNull), owningMod, assemblyName, " +
                "getTypesThrew, loaderExceptions[] (first few messages), debugActionMethods[] on " +
                "the type, allTypesCount, and verdict - a plain sentence naming which of the " +
                "known mechanisms the readings are consistent with, or 'inconclusive'.")]
        public static async Task<object> TypeVisibility(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Full type name, e.g. RimMandrake.FluidCanals.FluidCanalsDebugActions. Matched " +
                "case-insensitively against Type.FullName, and as a suffix so the bare class " +
                "name also works when it is unambiguous.")]
            string typeName = null,
            [ToolParameter(Description =
                "How many loader-exception messages to include when GetTypes() throws. These are " +
                "the actual missing-reference names and are the point of the call.", DefaultValue = 8)]
            int maxLoaderExceptions = 8)
        {
            cancellationToken.ThrowIfCancellationRequested();
            await Task.CompletedTask;

            if (string.IsNullOrWhiteSpace(typeName))
                return Fail("typeName is required, e.g. RimMandrake.FluidCanals.FluidCanalsDebugActions.");

            var wanted = typeName.Trim();
            if (maxLoaderExceptions < 0) maxLoaderExceptions = 0;
            if (maxLoaderExceptions > 50) maxLoaderExceptions = 50;

            // --- 1. is it in AllTypes? This is the reading that actually decides the symptom.
            List<Type> allTypes;
            try { allTypes = GenTypes.AllTypes.ToList(); }
            catch (Exception e) { return Fail("Could not enumerate GenTypes.AllTypes: " + e.GetType().Name + ": " + e.Message); }

            Type inAllTypes = FindType(allTypes, wanted);

            // --- 2. walk the mods' own assemblies. Deliberately NOT AllActiveAssemblies (it is
            // private): RunningMods is the same source it enumerates, and going through the mod
            // list lets the answer name WHICH mod owns the assembly.
            string owningMod = null, assemblyName = null;
            bool assemblyFound = false, getTypesThrew = false, typeInAssemblyGetTypes = false;
            string getTypesException = null;
            var loaderMessages = new List<string>();
            Type fromAssembly = null;

            foreach (var mod in LoadedModManager.RunningMods)
            {
                if (mod?.assemblies?.loadedAssemblies == null) continue;
                foreach (var asm in mod.assemblies.loadedAssemblies)
                {
                    if (asm == null) continue;

                    Type[] types = null;
                    bool threw = false;
                    var msgs = new List<string>();
                    try
                    {
                        types = asm.GetTypes();
                    }
                    catch (ReflectionTypeLoadException rex)
                    {
                        threw = true;
                        // The loader exceptions carry the actual missing reference names. This is
                        // the whole reason the tool exists - the vanilla Log.Error line prints the
                        // exception's ToString(), which the log may have rolled past or never kept.
                        try
                        {
                            if (rex.LoaderExceptions != null)
                                foreach (var le in rex.LoaderExceptions.Where(x => x != null).Take(maxLoaderExceptions))
                                    msgs.Add(le.GetType().Name + ": " + le.Message);
                        }
                        catch { }
                        try { types = rex.Types?.Where(t => t != null).ToArray(); }
                        catch { types = null; }
                    }
                    catch (Exception e)
                    {
                        threw = true;
                        msgs.Add(e.GetType().Name + ": " + e.Message);
                    }

                    var hit = types == null ? null : FindType(types, wanted);
                    if (hit == null) continue;

                    assemblyFound = true;
                    fromAssembly = hit;
                    owningMod = mod.Name;
                    assemblyName = SafeAsmName(asm);
                    getTypesThrew = threw;
                    typeInAssemblyGetTypes = true;
                    if (threw) getTypesException = "ReflectionTypeLoadException";
                    loaderMessages = msgs;
                    break;
                }
                if (assemblyFound) break;
            }

            var target = inAllTypes ?? fromAssembly;
            bool typeInitializerNull = false;
            if (target != null)
            {
                try { typeInitializerNull = target.TypeInitializer == null; }
                catch { typeInitializerNull = false; }
            }

            // --- 3. what debug actions does it carry? Distinguishes "class gone" from
            // "class present, attributes not seen".
            var actions = new List<object>();
            if (target != null)
            {
                MethodInfo[] methods = null;
                try { methods = target.GetMethods(BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic); }
                catch { }
                if (methods != null)
                {
                    foreach (var m in methods)
                    {
                        DebugActionAttribute attr = null;
                        try { attr = m.GetCustomAttribute<DebugActionAttribute>(); }
                        catch { }
                        if (attr == null) continue;
                        actions.Add(new
                        {
                            method = m.Name,
                            name = attr.name,
                            category = attr.category,
                            actionType = attr.actionType.ToString(),
                            allowedGameStates = attr.allowedGameStates.ToString(),
                        });
                    }
                }
            }

            string verdict;
            if (target == null)
                verdict = "NOT FOUND anywhere - the type is in no running mod's loaded assembly. " +
                          "Check the name, and check the assembly actually deployed.";
            else if (inAllTypes != null)
                verdict = "PRESENT in AllTypes. If its debug actions still do not appear, AllTypes " +
                          "is not the cause and the next probe belongs on the menu builder or the " +
                          "attribute itself - " + actions.Count + " [DebugAction] method(s) seen here.";
            else if (getTypesThrew && typeInitializerNull)
                verdict = "CONFIRMS the AllTypes recovery-path drop: the assembly's GetTypes() " +
                          "throws, and this type has NO static constructor, so AllTypes' " +
                          "`x.TypeInitializer != null` filter discards it. Fix either end - resolve " +
                          "the loader exception below, or give the type a static constructor.";
            else if (getTypesThrew)
                verdict = "The assembly's GetTypes() throws, but this type HAS a static constructor, " +
                          "so the TypeInitializer filter is not what dropped it. Something else " +
                          "excluded it from AllTypes - read the loader exceptions and look again.";
            else
                verdict = "Inconclusive: the type is in the assembly, GetTypes() does not throw, and " +
                          "yet it is absent from AllTypes. That should not happen - suspect a stale " +
                          "allTypesCached built before this assembly loaded.";

            return new
            {
                success = true,
                typeName = wanted,
                resolvedName = target?.FullName,
                assemblyFound,
                typeInAllTypes = inAllTypes != null,
                typeInAssemblyGetTypes,
                typeInitializerNull,
                owningMod,
                assemblyName,
                getTypesThrew,
                getTypesException,
                loaderExceptions = loaderMessages,
                debugActionMethods = actions,
                allTypesCount = allTypes.Count,
                verdict,
            };
        }

        /// <summary>Exact FullName first, then a dotted-suffix match, so a bare class name works
        /// when it is unambiguous. Suffix is matched on ".Name" rather than plain EndsWith, or
        /// "Tools" would match "MapTools".</summary>
        private static Type FindType(IEnumerable<Type> types, string wanted)
        {
            Type suffixHit = null;
            var dotted = "." + wanted;
            foreach (var t in types)
            {
                string full;
                try { full = t?.FullName; } catch { continue; }
                if (full == null) continue;
                if (string.Equals(full, wanted, StringComparison.OrdinalIgnoreCase)) return t;
                if (suffixHit == null && full.EndsWith(dotted, StringComparison.OrdinalIgnoreCase)) suffixHit = t;
            }
            return suffixHit;
        }

        private static string SafeAsmName(Assembly asm)
        {
            try { return asm.GetName().Name; }
            catch { try { return asm.ToString(); } catch { return "<unnameable>"; } }
        }
    }
}
