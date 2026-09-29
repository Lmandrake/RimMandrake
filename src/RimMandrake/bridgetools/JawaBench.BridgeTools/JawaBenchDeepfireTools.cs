// JawaBenchDeepfireTools.cs - DEEPFIRE_PAINT_LIVE_VERIFY_1 spec §10 step 5's own
// live quicktest needs two things the bridge cannot currently do at all: read
// map.glowGrid.GroundGlowAt (Verse/GlowGrid.cs, public, vanilla - no reflection
// needed) and reach RimMandrake.LuminousPigment.CompDeepfire, a foreign
// assembly the companion has never referenced on purpose (same reasoning as
// JawaBenchPipeTools.cs/JawaBenchVehicleTools.cs: a hard reference would stop
// the companion loading whenever LuminousPigment is absent from the mod
// list). CompDeepfire is reached the same way those files reach VEF/Vehicle
// Framework types: reflection by type name, resolved once, reported honestly
// (present:false, not an error, when the type or the comp is absent).
//
// GATING: ungated. Nothing here acts on the player or fires an incident; it
// reads glow state and drives one mod's own comp on things the caller already
// named. Same tier as jawa/set_thing_props.
//
// THREAD AFFINITY: everything that touches game state is inside
// ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private const string DeepfireCompTypeName = "RimMandrake.LuminousPigment.CompDeepfire";
        private const string DeepfireDesignationDefName = "RM_ApplyDeepfireDesignation";

        private static object FindDeepfireComp(Thing t, out string err)
        {
            err = null;
            if (t == null) { err = "No such thing."; return null; }
            var tc = t as ThingWithComps;
            if (tc == null) { err = "Thing is not a ThingWithComps."; return null; }
            foreach (var comp in tc.AllComps)
            {
                if (comp.GetType().FullName == DeepfireCompTypeName) return comp;
            }
            err = "No CompDeepfire on this thing (LuminousPigment not loaded, or this def was not injected).";
            return null;
        }

        [Tool(
            "deepfire/glow_at",
            Description =
                "Read Verse/GlowGrid.GroundGlowAt for a cell on the current map - the exact " +
                "field DEEPFIRE_PAINT_LIVE_VERIFY_1's proofs read (GameGlowLitThreshold is " +
                "0.3f). Vanilla API, no reflection, works with LuminousPigment absent. Also " +
                "reads VisualGlowAt so a caller can see the actual RGB the grid renders, not " +
                "just the scalar brightness.",
            ResultDescription = "success, groundGlow (float), visual {r,g,b,a} 0-255.")]
        public static async Task<object> DeepfireGlowAt(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Cell X.")] int x = 0,
            [ToolParameter(Description = "Cell Z.")] int z = 0)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                IntVec3 cell = new IntVec3(x, 0, z);
                if (!cell.InBounds(map)) return Fail("Cell out of bounds.");

                float ground = map.glowGrid.GroundGlowAt(cell);
                Color32 vis = map.glowGrid.VisualGlowAt(map.cellIndices.CellToIndex(cell));
                return (object)new
                {
                    success = true,
                    groundGlow = ground,
                    visual = new { r = (int)vis.r, g = (int)vis.g, b = (int)vis.b, a = (int)vis.a },
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "deepfire/comp_coats",
            Description =
                "Read RimMandrake.LuminousPigment.CompDeepfire.coats off a thing by reflection " +
                "(LuminousPigment is a soft dependency - this tool is present:false, not an " +
                "error, when the mod is absent or the def carries no CompDeepfire).",
            ResultDescription = "success, present (bool), coats (int), canAddCoat (bool).")]
        public static async Task<object> DeepfireCompCoats(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Thing id (as jawa/list_things reports it).")] string thing = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                var t = FindLiveThingById(thing, out var terr);
                if (t == null) return Fail(terr);
                var comp = FindDeepfireComp(t, out var cerr);
                if (comp == null) return (object)new { success = true, present = false, reason = cerr };

                var coatsField = comp.GetType().GetField("coats", BindingFlags.Public | BindingFlags.Instance);
                int coats = coatsField != null ? (int)coatsField.GetValue(comp) : -1;
                var canAddProp = comp.GetType().GetProperty("CanAddCoat", BindingFlags.Public | BindingFlags.Instance);
                bool canAdd = canAddProp != null && (bool)canAddProp.GetValue(comp);

                return (object)new { success = true, present = true, coats, canAddCoat = canAdd };
            });
        }

        [Tool(
            "deepfire/add_coat",
            Description =
                "Call RimMandrake.LuminousPigment.CompDeepfire.AddCoat() directly by " +
                "reflection - the exact method RM_JobDriver_ApplyDeepfire calls on toil " +
                "completion. Used to drive coats 2/3 and the fourth-refused case without " +
                "re-running the fetch/walk/toil pawn job each time; coat 1 should still be " +
                "proven through the real designation -> WorkGiver -> JobDriver path via " +
                "deepfire/designate.",
            ResultDescription = "success, present (bool), coatsBefore, coatsAfter.")]
        public static async Task<object> DeepfireAddCoat(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Thing id.")] string thing = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                var t = FindLiveThingById(thing, out var terr);
                if (t == null) return Fail(terr);
                var comp = FindDeepfireComp(t, out var cerr);
                if (comp == null) return (object)new { success = true, present = false, reason = cerr };

                var coatsField = comp.GetType().GetField("coats", BindingFlags.Public | BindingFlags.Instance);
                int before = coatsField != null ? (int)coatsField.GetValue(comp) : -1;
                var m = comp.GetType().GetMethod("AddCoat", BindingFlags.Public | BindingFlags.Instance);
                if (m == null) return Fail("CompDeepfire.AddCoat method not found (shape changed).");
                m.Invoke(comp, null);
                int after = coatsField != null ? (int)coatsField.GetValue(comp) : -1;

                return (object)new { success = true, present = true, coatsBefore = before, coatsAfter = after };
            });
        }

        [Tool(
            "deepfire/remove_coats",
            Description =
                "Call RimMandrake.LuminousPigment.CompDeepfire.RemoveAllCoats() directly by " +
                "reflection - the same method RM_Designator_RemoveDeepfire calls.",
            ResultDescription = "success, present (bool), coatsBefore, coatsAfter.")]
        public static async Task<object> DeepfireRemoveCoats(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Thing id.")] string thing = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                var t = FindLiveThingById(thing, out var terr);
                if (t == null) return Fail(terr);
                var comp = FindDeepfireComp(t, out var cerr);
                if (comp == null) return (object)new { success = true, present = false, reason = cerr };

                var coatsField = comp.GetType().GetField("coats", BindingFlags.Public | BindingFlags.Instance);
                int before = coatsField != null ? (int)coatsField.GetValue(comp) : -1;
                var m = comp.GetType().GetMethod("RemoveAllCoats", BindingFlags.Public | BindingFlags.Instance);
                if (m == null) return Fail("CompDeepfire.RemoveAllCoats method not found (shape changed).");
                m.Invoke(comp, null);
                int after = coatsField != null ? (int)coatsField.GetValue(comp) : -1;

                return (object)new { success = true, present = true, coatsBefore = before, coatsAfter = after };
            });
        }

        [Tool(
            "deepfire/designate",
            Description =
                "Add the RM_ApplyDeepfireDesignation designation on a thing, exactly as " +
                "RM_Designator_Deepfire's DesignateThing does - proves the real " +
                "WorkGiver_ApplyDeepfireConstruction/Crafting -> JobDriver_ApplyDeepfire path " +
                "end to end once a colonist and nearby RM_Deepfire exist and time runs. " +
                "Vanilla DesignationManager API, no reflection.",
            ResultDescription = "success, alreadyDesignated (bool).")]
        public static async Task<object> DeepfireDesignate(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Thing id.")] string thing = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                var t = FindLiveThingById(thing, out var terr);
                if (t == null) return Fail(terr);
                Map map = t.Map;
                if (map == null) return Fail("Thing is not spawned on a map.");

                DesignationDef def = DefDatabase<DesignationDef>.GetNamedSilentFail(DeepfireDesignationDefName);
                if (def == null) return Fail("DesignationDef " + DeepfireDesignationDefName + " not found (LuminousPigment not loaded).");

                if (map.designationManager.DesignationOn(t, def) != null)
                {
                    return (object)new { success = true, alreadyDesignated = true };
                }
                map.designationManager.AddDesignation(new Designation(t, def));
                return (object)new { success = true, alreadyDesignated = false };
            });
        }

        [Tool(
            "deepfire/paint_building",
            Description =
                "Call Verse/Building.ChangePaint(ColorDef) - the exact vanilla method " +
                "Designator_PaintBuilding's own JobDriver_PaintBuilding calls - so a live " +
                "quicktest can prove CompDeepfire.Notify_ColorChanged (fired by " +
                "ThingWithComps.Notify_ColorChanged, which ChangePaint triggers) actually " +
                "re-colours an already-lit Deepfire proxy. Vanilla API, no reflection.",
            ResultDescription = "success, colorDef, drawColor {r,g,b,a} after the change.")]
        public static async Task<object> DeepfirePaintBuilding(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Thing id.")] string thing = null,
            [ToolParameter(Description = "ColorDef defName, e.g. Blue.")] string colorDef = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                var t = FindLiveThingById(thing, out var terr);
                if (t == null) return Fail(terr);
                var building = t as Building;
                if (building == null) return Fail("Thing is not a Building.");
                ColorDef cd = DefDatabase<ColorDef>.GetNamedSilentFail(colorDef);
                if (cd == null) return Fail("ColorDef '" + colorDef + "' not found.");

                building.ChangePaint(cd);
                Color dc = building.DrawColor;
                return (object)new { success = true, colorDef = cd.defName, drawColor = new { r = dc.r, g = dc.g, b = dc.b, a = dc.a } };
            });
        }

        [Tool(
            "deepfire/force_apply_job",
            Description =
                "Force a specific pawn to start the REAL RM_JobDriver_ApplyDeepfire job on a " +
                "thing right now, bypassing JobGiver_Work's think-tree priority scan entirely " +
                "(built via WorkGiver_ApplyDeepfireConstruction/Crafting.JobOnThing by " +
                "reflection, then pawn.jobs.StartJob with InterruptForced) - proves the actual " +
                "fetch/carry/toil/AddCoat job pipeline end to end without depending on the " +
                "pawn's own AI ever choosing to pick up the (real, player-visible) designation. " +
                "The designation should still be added first via deepfire/designate, exactly as " +
                "a player's click would, so this only skips WHO gets assigned the job, not " +
                "whether the job/designation system itself is wired correctly.",
            ResultDescription = "success, jobDefName, reportString.")]
        public static async Task<object> DeepfireForceApplyJob(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id (as jawa/list_pawns or rimworld/list_colonists reports it).")] string pawn = null,
            [ToolParameter(Description = "Target thing id.")] string thing = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                var p = FindPawn(pawn, out var perr);
                if (p == null) return Fail(perr);
                var t = FindLiveThingById(thing, out var terr);
                if (t == null) return Fail(terr);

                Type conType = HarmonyLibTypeByName("RimMandrake.LuminousPigment.WorkGiver_ApplyDeepfireConstruction");
                Type craType = HarmonyLibTypeByName("RimMandrake.LuminousPigment.WorkGiver_ApplyDeepfireCrafting");
                if (conType == null) return Fail("WorkGiver_ApplyDeepfireConstruction not found.");
                Type giverType = t.def.category == ThingCategory.Building ? conType : craType;
                object giver = Activator.CreateInstance(giverType);
                MethodInfo jobOnThing = giverType.GetMethod("JobOnThing", BindingFlags.Public | BindingFlags.Instance);
                object jobObj;
                try { jobObj = jobOnThing.Invoke(giver, new object[] { p, t, true }); }
                catch (TargetInvocationException tie) { return Fail("JobOnThing threw: " + tie.InnerException); }
                if (jobObj == null) return Fail("JobOnThing returned null (no reachable Deepfire, or target ineligible).");

                Job job = (Job)jobObj;
                p.jobs.StartJob(job, JobCondition.InterruptForced);
                return (object)new { success = true, jobDefName = job.def.defName, reportString = job.GetReport(p) };
            });
        }

        [Tool(
            "deepfire/debug_workgiver",
            Description =
                "Diagnostic: for every free colonist on the current map, report WorkTypeDef " +
                "enable state/priority for Construction and Crafting, and call " +
                "WorkGiver_ApplyDeepfireConstruction/Crafting.HasJobOnThing(pawn, thing, false) " +
                "by reflection against the named thing, reading back JobFailReason.Reason on a " +
                "false. Diagnoses why a designated thing's job never gets picked up without " +
                "guessing. Read-only.",
            ResultDescription = "success, pawns[] {name, constructionActive, constructionPriority, craftingActive, craftingPriority, hasJobConstruction, hasJobCrafting, failReason}.")]
        public static async Task<object> DeepfireDebugWorkGiver(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Thing id to test against.")] string thing = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                var t = FindLiveThingById(thing, out var terr);
                if (t == null) return Fail(terr);
                Map map = t.Map;
                if (map == null) return Fail("Thing not spawned.");

                Type conType = HarmonyLibTypeByName("RimMandrake.LuminousPigment.WorkGiver_ApplyDeepfireConstruction");
                Type craType = HarmonyLibTypeByName("RimMandrake.LuminousPigment.WorkGiver_ApplyDeepfireCrafting");
                if (conType == null || craType == null)
                {
                    return Fail("WorkGiver types not found (LuminousPigment not loaded or shape changed).");
                }
                object conGiver = Activator.CreateInstance(conType);
                object craGiver = Activator.CreateInstance(craType);
                MethodInfo conHas = conType.GetMethod("HasJobOnThing", BindingFlags.Public | BindingFlags.Instance);
                MethodInfo craHas = craType.GetMethod("HasJobOnThing", BindingFlags.Public | BindingFlags.Instance);

                var results = new List<object>();
                foreach (Pawn p in map.mapPawns.FreeColonists)
                {
                    bool conActive = p.workSettings != null && p.workSettings.WorkIsActive(WorkTypeDefOf.Construction);
                    int conPrio = p.workSettings != null ? p.workSettings.GetPriority(WorkTypeDefOf.Construction) : -1;
                    var craftingDef = DefDatabase<WorkTypeDef>.GetNamedSilentFail("Crafting");
                    bool craActive = craftingDef != null && p.workSettings != null && p.workSettings.WorkIsActive(craftingDef);
                    int craPrio = craftingDef != null && p.workSettings != null ? p.workSettings.GetPriority(craftingDef) : -1;

                    JobFailReason.Clear();
                    bool hasCon = false;
                    try { hasCon = (bool)conHas.Invoke(conGiver, new object[] { p, t, false }); }
                    catch (Exception ex) { results.Add(new { name = p.Name.ToStringShort, error = ex.ToString() }); continue; }
                    string reasonCon = JobFailReason.Reason;

                    JobFailReason.Clear();
                    bool hasCra = false;
                    try { hasCra = (bool)craHas.Invoke(craGiver, new object[] { p, t, false }); }
                    catch (Exception) { /* leave false */ }
                    string reasonCra = JobFailReason.Reason;

                    results.Add(new
                    {
                        name = p.Name.ToStringShort,
                        drafted = p.Drafted,
                        downed = p.Downed,
                        curJob = p.CurJobDef?.defName,
                        constructionActive = conActive,
                        constructionPriority = conPrio,
                        craftingActive = craActive,
                        craftingPriority = craPrio,
                        hasJobConstruction = hasCon,
                        failReasonConstruction = reasonCon,
                        hasJobCrafting = hasCra,
                        failReasonCrafting = reasonCra,
                    });
                }

                return (object)new { success = true, pawns = results };
            });
        }

        private static Type HarmonyLibTypeByName(string fullName)
        {
            foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
            {
                var t = asm.GetType(fullName, false);
                if (t != null) return t;
            }
            return null;
        }
    }
}
