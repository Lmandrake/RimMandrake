// JawaBenchHarmonyInspect.cs - name the mod whose Harmony patch is responsible for
// behaviour that has no XML and no vendored/decompiled source explanation.
//
// WILD_ANIMALS_PADDED_LISTS_1
// ============================
// Every one of 81 biomes' `wildAnimals` list holds exactly 1024 records in a capture,
// including biomes a BiomeCast patch replaced with ~29-record lists - a load-time
// mutation to the live def, not a dump-time artifact (DefDumper reads raw reflection
// and computes nothing). An exhaustive grep of every vendored/decompiled .cs file that
// mentions BiomeDef found nothing that writes to wildAnimals. That investigation's own
// conclusion: "naming the exact assembly needs a live Harmony patch inventory... no
// bridge tool exists for this today." This file is that tool.
//
// 🔑 ISOLATED HARMONY CONTACT POINT #2 IN THIS COMPANION
// ========================================================
// JawaBenchArgGuard.cs was written under the rule "all Harmony contact isolated to one
// file" so an absent 0Harmony fails only that file's own call, inside a try/catch,
// rather than risking the whole companion's type load. That rule survives as "each file
// that touches HarmonyLib is independently isolated and independently guarded" rather
// than "exactly one file may ever touch it" - a second file follows the identical
// discipline: no Harmony type appears in a static field initializer or a class-level
// static ctor, only inside methods, and every call into HarmonyLib is wrapped in its own
// try/catch that reports failure as data instead of throwing. See JawaBenchArgGuard.cs
// for contact point #1.
//
// Unlike ArgGuard this tool INSTALLS NOTHING - it only calls Harmony's own static
// introspection (GetAllPatchedMethods / GetPatchInfo), which walks Harmony's existing
// patch registry and touches no other mod's code. There is no Install() step and
// nothing for JawaBenchInit.cs to call eagerly; the first invocation IS the guard.
//
// ⛔ NO jawa/ PREFIXES IN PROSE ANYWHERE IN THIS FILE'S DESCRIPTIONS other than an
// EXACT, REAL tool name. build.py scans the assembly for jawa/... literals and a
// partial mention (e.g. "the jawa/world_* family") becomes a phantom tool name.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/harmony_patches",
            Description =
                "READ ONLY. Lists every Harmony patch currently active on methods of the named " +
                "TYPE, across the WHOLE PROCESS - not just this companion's own patches. For each " +
                "matching method: every Prefix/Postfix/Transpiler/Finalizer, each patch's Harmony " +
                "owner id and the ASSEMBLY its patch method is compiled into (which usually names " +
                "the mod). Use when a def's raw field holds a value the XML and the vendored/" +
                "decompiled source subset cannot explain - a Harmony transpiler or postfix is the " +
                "remaining suspect, and this is the only way to name it without a decompiler. " +
                "⛔ Cannot see a patch's SOURCE, only its declaring assembly and method name - " +
                "correlate the assembly to a mod via jawa/mod_inventory or the workshop id in the " +
                "path. 🔑 A second isolated Harmony contact point, same discipline as " +
                "jawa/bridge_arg_report's JawaBenchArgGuard.cs - see that file for why an absent " +
                "0Harmony fails only this call.",
            ResultDescription =
                "success, typeName, methodName, methodCount, methods[] each {method, " +
                "declaringType, prefixCount/postfixCount/transpilerCount/finalizerCount, " +
                "prefixes/postfixes/transpilers/finalizers[] of {owner, priority, patchMethod, " +
                "patchAssembly}}. harmonyError is set instead of throwing if HarmonyLib itself is " +
                "unreachable - that means THIS INSTRUMENT IS BLIND, not that nothing is patched.")]
        public static async Task<object> HarmonyPatches(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Type to inspect - simple name (e.g. 'BiomeDef') or full name (e.g. " +
                "'RimWorld.BiomeDef'). Matches either, case-insensitive. Required: the " +
                "appdomain-wide patched-method list can be in the thousands and dumping it " +
                "unfiltered is not useful.")]
            string typeName,
            [ToolParameter(Description =
                "Optional method name filter, exact and case-sensitive, e.g. " +
                "'CommonalityOfAnimal'. Empty returns every patched method on the type.")]
            string methodName = null)
        {
            cancellationToken.ThrowIfCancellationRequested();

            if (string.IsNullOrWhiteSpace(typeName))
                return Fail("typeName is required - the appdomain-wide patched-method list is too " +
                            "large to return unfiltered.");

            // 🔑 Deliberately NOT inside MainThread.InvokeAsync. This reads Harmony's own
            // static patch registry via reflection over MethodBase objects already resolved
            // at patch time - it touches no Map, no Pawn, no Unity object, exactly the same
            // reasoning jawa/bridge_arg_report gives for skipping the hop.
            List<MethodBase> patched;
            try
            {
                patched = HarmonyLib.Harmony.GetAllPatchedMethods().ToList();
            }
            catch (Exception ex)
            {
                return Fail("HarmonyLib introspection failed: " + ex.GetType().Name + ": " + ex.Message,
                    new { harmonyError = true });
            }

            var matches = patched
                .Where(m => m?.DeclaringType != null &&
                            (string.Equals(m.DeclaringType.Name, typeName, StringComparison.OrdinalIgnoreCase) ||
                             string.Equals(m.DeclaringType.FullName, typeName, StringComparison.OrdinalIgnoreCase)))
                .Where(m => string.IsNullOrEmpty(methodName) ||
                            string.Equals(m.Name, methodName, StringComparison.Ordinal))
                .ToList();

            var methods = matches.Select(m =>
            {
                HarmonyLib.Patches info = null;
                string patchInfoError = null;
                try { info = HarmonyLib.Harmony.GetPatchInfo(m); }
                catch (Exception ex) { patchInfoError = ex.GetType().Name + ": " + ex.Message; }

                List<object> Rows(IEnumerable<HarmonyLib.Patch> arr) =>
                    (arr ?? Enumerable.Empty<HarmonyLib.Patch>()).Select(p => (object)new
                    {
                        owner = p.owner,
                        priority = p.priority,
                        patchMethod = p.PatchMethod != null
                            ? (p.PatchMethod.DeclaringType?.FullName + "." + p.PatchMethod.Name)
                            : null,
                        patchAssembly = p.PatchMethod?.DeclaringType?.Assembly?.GetName().Name
                    }).ToList();

                var prefixes = Rows(info?.Prefixes);
                var postfixes = Rows(info?.Postfixes);
                var transpilers = Rows(info?.Transpilers);
                var finalizers = Rows(info?.Finalizers);

                return (object)new
                {
                    method = m.Name,
                    declaringType = m.DeclaringType.FullName,
                    patchInfoError,
                    prefixCount = prefixes.Count,
                    postfixCount = postfixes.Count,
                    transpilerCount = transpilers.Count,
                    finalizerCount = finalizers.Count,
                    prefixes,
                    postfixes,
                    transpilers,
                    finalizers
                };
            }).ToList();

            return await Task.FromResult<object>(new
            {
                success = true,
                typeName,
                methodName,
                methodCount = methods.Count,
                methods,
                ticksGame = TicksGameSafe(),
                note = methods.Count == 0
                    ? "No patched method matched this type name. Either nothing patches it, or " +
                      "the type name did not resolve - check spelling and that the type is loaded."
                    : null
            }).ConfigureAwait(false);
        }
    }
}
