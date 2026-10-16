// JawaBenchLiquidLookTools.cs - live tuning of a FlowWorks liquid's surface look
// (TAR_LOOK_TUNE_THICK_AND_SLOW, 2026-10-16: the owner tunes tar's canal surface by WATCHING it,
// one tweak at a time, with no restart per tweak).
//
//   liquid_look_get   every field of one liquid's live look + what each of its terrains draws
//   liquid_look_set   set fields, re-apply, and the next frame draws the new look
//   liquid_look_dump  the live look as the <surfaceLook> XML block and the generator table entry
//
// COUPLING: strictly by reflection, like every FlowWorks tool file - the companion must register
// on a mod list WITHOUT FlowWorks. Every member read from src/RimMandrake/FlowWorks/Source/RM_LiquidLooks.cs
// (RM_LiquidLookProof, public static): Resolve(string) -> string, Values(string) ->
// Dictionary<string,string>, Tune(string, string) -> string, Xml(string) -> string,
// GeneratorEntry(string) -> string, Terrains(string) -> List<string>. The look's field names
// come from RM_LiquidSurfaceLook's public instance fields (RM_LiquidSurface.cs).
// Tune itself re-applies the look to every terrain wearing it, drops the overlay's cached
// materials (RM_LiquidSurface.ForgetLook) and regenerates every map's terrain meshes
// (RM_LiquidLooks.RefreshMaps), so no separate commit tool is needed.
//
// THREAD AFFINITY: everything inside ctx.MainThread.InvokeAsync (Tune rebuilds materials and meshes).

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private const string LlProofTypeName = "RimMandrake.FlowWorks.RM_LiquidLookProof";
        private const string LlLookTypeName = "RimMandrake.FlowWorks.RM_LiquidSurfaceLook";

        /// <summary>The proof type and the resolved defName, or a loud error.</summary>
        private static Type LlResolve(string liquid, out string defName, out string error)
        {
            defName = null;
            error = null;
            Type proof = GenTypes.GetTypeInAnyAssembly(LlProofTypeName);
            if (proof == null)
            {
                error = LlProofTypeName + " not found: FlowWorks is not loaded, or its DLL predates TAR_LOOK_TUNE_THICK_AND_SLOW.";
                return null;
            }
            MethodInfo resolve = proof.GetMethod("Resolve", FwStatic, null, new[] { typeof(string) }, null);
            if (resolve == null)
            {
                error = LlProofTypeName + ".Resolve(string) missing: the deployed FlowWorks DLL predates TAR_LOOK_TUNE_THICK_AND_SLOW; deploy it with the game closed.";
                return null;
            }
            if (string.IsNullOrEmpty(liquid))
            {
                error = "liquid is required (a LiquidDef/FluidDef defName, or a short name such as tar).";
                return null;
            }
            defName = resolve.Invoke(null, new object[] { liquid }) as string;
            if (defName == null)
            {
                error = "No LiquidDef or FluidDef matches '" + liquid + "' (tried the defName, RM_Liquid_<name>, RM_Fluid_<name> and LiquidDef labels).";
                return null;
            }
            return proof;
        }

        private static object LlCall(Type proof, string method, List<string> missing, params object[] args)
        {
            MethodInfo m = proof.GetMethod(method, FwStatic, null, args.Select(a => typeof(string)).ToArray(), null);
            if (m == null) { missing.Add(proof.Name + "." + method); return null; }
            return m.Invoke(null, args);
        }

        private static object LlSetting(string name)
        {
            Type s = GenTypes.GetTypeInAnyAssembly(FwSettingsTypeName);
            return s?.GetField(name, FwStatic)?.GetValue(null);
        }

        [Tool(
            "jawa/liquid_look_get",
            Description =
                "Read one FlowWorks liquid's LIVE surface look (RM_LiquidSurfaceLook) - every field, as the running game " +
                "holds it after any live tuning, NOT the XML on disk. liquid: a LiquidDef or FluidDef defName " +
                "(RM_Liquid_Tar, RM_Fluid_Oil) or a short name (tar). A FluidDef with no look of its own reports its " +
                "LiquidDef row's look (the same object: tuning one tunes both). Also reports each terrain wearing the " +
                "look and what it actually draws (shader, colour, texture, water-depth ripple pass or null), and the Mod " +
                "Settings liquidLooksEnabled / liquidSurfaceMotionEnabled - with liquidSurfaceMotionEnabled off no overlay " +
                "is drawn whatever the look says. Read-only.",
            ResultDescription =
                "success, liquid, defName, values{field: text} (null = unset string), terrains[] (one line per terrain), " +
                "liquidLooksEnabled, liquidSurfaceMotionEnabled, ticksGame.")]
        public static async Task<object> LiquidLookGet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "LiquidDef/FluidDef defName, or a short name such as tar.")]
            string liquid = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Type proof = LlResolve(liquid, out string defName, out string error);
                if (proof == null) return Fail(error);
                var missing = new List<string>();
                var values = LlCall(proof, "Values", missing, defName) as Dictionary<string, string>;
                var terrains = LlCall(proof, "Terrains", missing, defName) as List<string>;
                if (missing.Count > 0) return Fail("FlowWorks members missing (stale DLL?): " + string.Join(", ", missing));
                if (values == null) return Fail(defName + " has no surface look (nothing to read; liquid_look_set creates one).");
                return (object)new
                {
                    success = true, liquid, defName, values, terrains,
                    liquidLooksEnabled = LlSetting("liquidLooksEnabled"),
                    liquidSurfaceMotionEnabled = LlSetting("liquidSurfaceMotionEnabled"),
                    ticksGame = TicksGameSafe()
                };
            });
        }

        [Tool(
            "jawa/liquid_look_set",
            Description =
                "Set fields of one FlowWorks liquid's surface look LIVE and re-apply it: the next frame draws the new look " +
                "on every map (terrain materials rebuilt, terrain meshes regenerated, overlay materials and ripple textures " +
                "dropped), no restart. CHANGES ONLY THE RUNNING GAME - nothing is written to disk; when it looks right, " +
                "call liquid_look_dump and paste its output into the generator table (generate_liquid_suite.py " +
                "SURFACE_LOOKS) and the registry XML, or the tuning is lost at the next load. spec: 'field=value;field=value'. " +
                "Fields: shader (Solid | Water | Flow), texture (a texture path, White, or empty = the terrain's own), mask, " +
                "tint / highlight / bubbleColor / seeThroughTint as (r,g,b), depthDarken, rippleDensity / rippleIntensity " +
                "(the vanilla water ripple pass; -1 = vanilla; on a Solid look the ripple pass is drawn only when either " +
                "is >= 0), flowSpeed / flowAmplitude / flowFrequency / brightness / spotScale / spotSpeed / spotMin / spotMax " +
                "(Flow shader only, -1 = shader default), overlay (true/false: the drifting glint film), strength, scale, " +
                "speed, sharpness, stretch, sheen (overlay only), wake, bubbles, splashes, fleck, fleckChance, seeThrough. " +
                "Unknown field names are REFUSED and not passed on; a value that fails to parse is reported in " +
                "tuneComplaints and leaves that field unchanged. Applies even with the liquidLooksEnabled Mod Setting off.",
            ResultDescription =
                "success (false if anything was refused or failed to parse - the rest still applied), defName, applied " +
                "(terrains re-applied; 0 means the look reached no terrain), refused[] {field, reason}, tuneComplaints, " +
                "readBack{field: live text after the set}, ticksGame.")]
        public static async Task<object> LiquidLookSet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "LiquidDef/FluidDef defName, or a short name such as tar.")]
            string liquid = null,
            [ToolParameter(Description = "'field=value;field=value', e.g. 'rippleDensity=0.6;tint=(0.2,0.2,0.2)'.")]
            string spec = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Type proof = LlResolve(liquid, out string defName, out string error);
                if (proof == null) return Fail(error);
                Type lookType = GenTypes.GetTypeInAnyAssembly(LlLookTypeName);
                if (lookType == null) return Fail(LlLookTypeName + " not found.");
                if (string.IsNullOrWhiteSpace(spec)) return Fail("spec is empty: nothing to set ('field=value;field=value').");
                var fields = new HashSet<string>(lookType.GetFields(BindingFlags.Public | BindingFlags.Instance).Select(f => f.Name));
                var refused = new List<object>();
                var keep = new List<string>();
                var asked = new List<string>();
                foreach (string raw in spec.Split(';'))
                {
                    string part = raw.Trim();
                    if (part.Length == 0) continue;
                    int eq = part.IndexOf('=');
                    if (eq <= 0) { refused.Add(new { field = part, reason = "not field=value" }); continue; }
                    string k = part.Substring(0, eq).Trim();
                    if (!fields.Contains(k)) { refused.Add(new { field = k, reason = "no such look field" }); continue; }
                    keep.Add(k + "=" + part.Substring(eq + 1).Trim());
                    asked.Add(k);
                }
                if (keep.Count == 0) return Fail("Nothing to set: every entry was refused.", new { refused });
                var missing = new List<string>();
                string tune = LlCall(proof, "Tune", missing, defName, string.Join(";", keep)) as string;
                var values = LlCall(proof, "Values", missing, defName) as Dictionary<string, string>;
                if (missing.Count > 0) return Fail("FlowWorks members missing (stale DLL?): " + string.Join(", ", missing));
                // Tune returns "applied N[ bad:...] | describe"
                int applied = -1;
                string complaints = "";
                if (tune != null && tune.StartsWith("applied "))
                {
                    string head = tune.Split('|')[0].Trim();
                    string[] w = head.Split(new[] { ' ' }, 3);
                    int.TryParse(w[1], out applied);
                    int bad = head.IndexOf(" bad:", StringComparison.Ordinal);
                    if (bad >= 0) complaints = head.Substring(bad + 5);
                }
                else
                {
                    return Fail("Tune did not apply: " + tune);
                }
                var readBack = new Dictionary<string, string>();
                foreach (string k in asked)
                    readBack[k] = values != null && values.TryGetValue(k, out string v) ? v : "(unread)";
                return (object)new
                {
                    success = refused.Count == 0 && complaints.Length == 0 && applied > 0,
                    defName, applied, refused, tuneComplaints = complaints, readBack,
                    note = applied == 0 ? "the look reached no terrain: no FlowWorks terrain wears this liquid's look" : null,
                    ticksGame = TicksGameSafe()
                };
            });
        }

        [Tool(
            "jawa/liquid_look_dump",
            Description =
                "One FlowWorks liquid's LIVE surface look as text to paste back into source once it looks right: xml is the " +
                "<surfaceLook> block (fields that differ from RM_LiquidSurfaceLook's defaults, in the generator's field " +
                "order) for RM_LiquidDefRegistry.xml (or a FluidDef look patch); generatorEntry is the same look as a dict " +
                "for SURFACE_LOOKS / FLUID_SURFACE_LOOKS in FlowWorks/Tools/generate_liquid_suite.py. THE REGISTRY XML IS " +
                "GENERATED - put the look in the generator table and regenerate, or a regenerate reverts it. Read-only.",
            ResultDescription = "success, defName, xml, generatorEntry, ticksGame.")]
        public static async Task<object> LiquidLookDump(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "LiquidDef/FluidDef defName, or a short name such as tar.")]
            string liquid = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Type proof = LlResolve(liquid, out string defName, out string error);
                if (proof == null) return Fail(error);
                var missing = new List<string>();
                string xml = LlCall(proof, "Xml", missing, defName) as string;
                string entry = LlCall(proof, "GeneratorEntry", missing, defName) as string;
                if (missing.Count > 0) return Fail("FlowWorks members missing (stale DLL?): " + string.Join(", ", missing));
                if (xml == null) return Fail(defName + " has no surface look.");
                return (object)new { success = true, defName, xml, generatorEntry = entry, ticksGame = TicksGameSafe() };
            });
        }
    }
}
