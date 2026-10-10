// SUPERDEEP_TARGET_VALIDATOR_1 / GLOW_TANK_SEED_LIVE_SOW_1 (FOUNDRY bridge helper 2026-10-09):
// two reads the bridge could not do - which enemy a NON-colonist's own target finder picks right now, and
// putting fuel into a CompRefuelable (plus reading named fields off the thing) without a hauling colonist.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimWorld;
using RimBridgeServer.Sdk;
using Verse;
using Verse.AI;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/attack_target_probe",
            Description =
                "Ask the game's own AttackTargetFinder.BestAttackTarget which target THIS pawn (any faction, not only " +
                "colonists) would pick right now, with the same scan flags JobGiver_AIFightEnemy uses " +
                "(NeedLOSToPawns | NeedReachableIfCantHitFromMyPos | NeedThreat | NeedAutoTargetable) and maxDist. " +
                "Every installed Harmony patch on the finder runs (that is the point: it exercises a mod's target " +
                "validator). Also reports the pawn's CURRENT job, its targetA, mindState.enemyTarget, the primary " +
                "weapon and whether its verb is ranged. Read-only: nothing is assigned. A pawn with no verb or a " +
                "melee-only verb still runs the finder, so check primaryVerbRanged before reading 'idles'.",
            ResultDescription =
                "success, pawn, position, picked{id,def,x,z} or null, curJob, curJobTargetA, enemyTarget, primary, " +
                "primaryVerbRanged, ticksGame.")]
        public static async Task<object> AttackTargetProbe(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name (any faction).")] string pawn = null,
            [ToolParameter(Description = "Search radius, cells. Default 60.", DefaultValue = 60f)] float maxDist = 60f)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; Pawn p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (!p.Spawned) return Fail("Pawn " + p.ThingID + " is not spawned.");
                TargetScanFlags flags = TargetScanFlags.NeedLOSToPawns | TargetScanFlags.NeedReachableIfCantHitFromMyPos
                    | TargetScanFlags.NeedThreat | TargetScanFlags.NeedAutoTargetable;
                Thing picked;
                try { picked = AttackTargetFinder.BestAttackTarget(p, flags, null, 0f, maxDist)?.Thing; }
                catch (Exception ex) { return Fail("BestAttackTarget threw: " + ex.Message); }
                Verb verb = p.TryGetAttackVerb(null, false);
                object Desc(LocalTargetInfo t) => !t.IsValid ? null : t.HasThing
                    ? (object)new { id = t.Thing.ThingID, def = t.Thing.def.defName, x = t.Thing.Position.x, z = t.Thing.Position.z }
                    : new { id = (string)null, def = (string)null, x = t.Cell.x, z = t.Cell.z };
                return (object)new
                {
                    success = true,
                    pawn = p.ThingID,
                    faction = p.Faction?.Name,
                    position = new { x = p.Position.x, z = p.Position.z },
                    picked = picked == null ? null : new { id = picked.ThingID, def = picked.def.defName, x = picked.Position.x, z = picked.Position.z },
                    curJob = p.CurJobDef?.defName,
                    curJobTargetA = p.CurJob != null ? Desc(p.CurJob.targetA) : null,
                    enemyTarget = p.mindState?.enemyTarget == null ? null : Desc(p.mindState.enemyTarget),
                    primary = p.equipment?.Primary?.def.defName,
                    primaryVerbRanged = verb != null && !verb.IsMeleeAttack,
                    ticksGame = TicksGameSafe()
                };
            });
        }

        [Tool(
            "jawa/thing_refuel",
            Description =
                "Read or ADD fuel on one thing's CompRefuelable (by thing id), and optionally read named instance " +
                "fields of the thing itself by reflection (public or private, e.g. 'established'). amount > 0 calls " +
                "CompRefuelable.Refuel(amount) - the engine's own path, clamped to fuelCapacity, no hauler and no " +
                "fuel item consumed; amount = 0 only reads. Refuses a thing without CompRefuelable. A field name " +
                "that does not exist is listed in missing[], never silently dropped.",
            ResultDescription = "success, thing, def, fuelBefore, fuelAfter, capacity, hasFuel, fields{name:text}, missing[], ticksGame.")]
        public static async Task<object> ThingRefuel(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingID (e.g. RM_GlowTank1234) or the bare id number.")] string thingId,
            [ToolParameter(Description = "Fuel to add; 0 = read only.", DefaultValue = 0f)] float amount = 0f,
            [ToolParameter(Description = "Comma-separated instance field names to read off the thing.", DefaultValue = "")] string fields = "")
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                string id = (thingId ?? "").Trim();
                if (id.StartsWith("Thing_", StringComparison.OrdinalIgnoreCase)) id = id.Substring(6);
                int num; bool isNum = int.TryParse(id, out num);
                Thing t = map.listerThings.AllThings.FirstOrDefault(x => isNum ? x.thingIDNumber == num : x.ThingID == id);
                if (t == null) return Fail("No thing '" + thingId + "' on the current map.");
                CompRefuelable fuel = (t as ThingWithComps)?.GetComp<CompRefuelable>();
                if (fuel == null) return Fail(t.ThingID + " has no CompRefuelable.");
                float before = fuel.Fuel;
                if (amount > 0f) fuel.Refuel(amount);
                var vals = new Dictionary<string, string>();
                var missing = new List<string>();
                foreach (string raw in (fields ?? "").Split(','))
                {
                    string f = raw.Trim();
                    if (f.Length == 0) continue;
                    FieldInfo fi = null;
                    for (Type ty = t.GetType(); ty != null && fi == null; ty = ty.BaseType)
                        fi = ty.GetField(f, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
                    if (fi == null) { missing.Add(f); continue; }
                    vals[f] = Convert.ToString(fi.GetValue(t), System.Globalization.CultureInfo.InvariantCulture);
                }
                return (object)new
                {
                    success = true,
                    thing = t.ThingID,
                    def = t.def.defName,
                    fuelBefore = before,
                    fuelAfter = fuel.Fuel,
                    capacity = fuel.Props.fuelCapacity,
                    hasFuel = fuel.HasFuel,
                    fields = vals,
                    missing,
                    ticksGame = TicksGameSafe()
                };
            });
        }
    }
}
