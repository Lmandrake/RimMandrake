// JawaBenchTapFixtureTools.cs - RIMMANDRAKE_BUILD_TAP_CERTIFICATE_CANARY_RUNS_OFF_STAGE.
//
// Two TEST-profile tools that the live tap certificate (prove_tap_certificate.py) needs as ACTS inside one
// jawa/run_until run, where no stock tool reaches the engine route:
//   jawa/scene_gate   arm / release / state of a JawaBenchGates gate (incident, quest, mental), so a fixture can show
//                     a gate's "allowed" and "held" rows by the real engine call the gate sits on.
//   jawa/tap_fixture  four small engine calls: unpatch one jawabench.* Harmony owner from one method (the blind plant),
//                     add an existing quest again (QuestManager.Add, the "already there" route), FireUtility.TryAttachFire
//                     with an instigator, GenExplosion.DoExplosion with an instigator or none.
// Both are generic: neither names a mod, and the unpatch refuses any owner that is not ours ("jawabench.").
// The unpatch adds no Harmony site (it removes one); the cast hook comes back at the next run with a cast
// (JawaBenchCast.Join calls EnsurePatched).
//
// THREAD AFFINITY: everything runs inside ctx.MainThread.

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimWorld;
using RimBridgeServer.Sdk;
using Verse;
using Verse.AI;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
#if JAWA_GM_TOOLS
        [Tool(
            "jawa/scene_gate",
            Description =
                "Arm, release or read one scene gate (JawaBenchGates: incident, quest, mental). arm: allow is a comma list of " +
                "names (incident def, quest root def, mental state def); a name listed N times lets N calls through, every other " +
                "call of that kind is held and leaves a gate row in the scene trace. release: kind empty releases every gate. " +
                "state: the gates' summary. Main thread. TEST only.",
            ResultDescription = "success, action, kind, armed (refusal text when not), summary, ticksGame.")]
        public static async Task<object> SceneGate(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "arm | release | state.")] string action = "state",
            [ToolParameter(Description = "incident | quest | mental (release: empty = all).")] string kind = "",
            [ToolParameter(Description = "arm: comma list of names let through; empty = hold every call.")] string allow = "",
            [ToolParameter(Description = "release: why, for the gate's own record.")] string why = "released by jawa/scene_gate")
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                string a = (action ?? "").Trim().ToLowerInvariant();
                long t = Find.TickManager != null ? Find.TickManager.TicksGame : -1;
                if (a == "arm")
                {
                    if (string.IsNullOrEmpty(kind)) return Fail("arm needs kind (incident, quest, mental)");
                    string refused = JawaBenchGates.Arm(kind, allow ?? "");
                    if (refused != null) return Fail(refused, new { kind, allow });
                    return new { success = true, action = a, kind, allow, summary = JawaBenchGates.Summary(), ticksGame = t };
                }
                if (a == "release")
                {
                    JawaBenchGates.Release(string.IsNullOrEmpty(kind) ? null : kind, why ?? "released by jawa/scene_gate");
                    return new { success = true, action = a, kind, summary = JawaBenchGates.Summary(), ticksGame = t };
                }
                if (a == "state") return new { success = true, action = a, summary = JawaBenchGates.Summary(), ticksGame = t };
                return Fail("action must be arm, release or state, not '" + action + "'");
            });
        }

        [Tool(
            "jawa/tap_fixture",
            Description =
                "Five engine calls for a tap fixture. unpatch: remove Harmony owner 'owner' (must start 'jawabench.') from every " +
                "declared method 'methodName' of typeName that it patches. quest_add_again: Find.QuestManager.Add of a quest that " +
                "is already there (questId, -1 = the newest). fire_attach: FireUtility.TryAttachFire(thing, size, instigator). " +
                "explode: GenExplosion.DoExplosion(cell, current map, radius, damType, instigator or null). reserve_unforced: " +
                "ReservationManager.Reserve(pawnId, an Equip job that is NOT player-forced, thingId, errorOnFailed false), released " +
                "again if made. Main thread. TEST only.",
            ResultDescription = "success, action, what was done (unpatched methods, quest id, fire, explosion), ticksGame.")]
        public static async Task<object> TapFixture(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "unpatch | quest_add_again | fire_attach | explode | reserve_unforced.")] string action,
            [ToolParameter(Description = "unpatch: Type.FullName, exact (e.g. Verse.AI.ReservationManager).")] string typeName = "",
            [ToolParameter(Description = "unpatch: method name.")] string methodName = "",
            [ToolParameter(Description = "unpatch: the Harmony owner id; must start 'jawabench.'.")] string owner = "",
            [ToolParameter(Description = "quest_add_again: quest id; -1 = the newest quest.")] int questId = -1,
            [ToolParameter(Description = "fire_attach: the thing set alight (ThingID or id number).")] string thingId = "",
            [ToolParameter(Description = "fire_attach / explode: the instigator (ThingID or id number); empty = none.")] string instigatorId = "",
            [ToolParameter(Description = "explode: the centre cell 'x,z'.")] string cell = "",
            [ToolParameter(Description = "explode: radius.")] float radius = 1.9f,
            [ToolParameter(Description = "explode: DamageDef defName.")] string damType = "Smoke",
            [ToolParameter(Description = "fire_attach: fire size.")] float size = 0.5f,
            [ToolParameter(Description = "reserve_unforced: the claimant pawn (ThingID or id number); thingId is the target.")] string pawnId = "")
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                string a = (action ?? "").Trim().ToLowerInvariant();
                long t = Find.TickManager != null ? Find.TickManager.TicksGame : -1;
                Thing instigator = null;
                if (!string.IsNullOrEmpty(instigatorId))
                {
                    instigator = StaticCallResolveThing(instigatorId, out _);
                    if (instigator == null) return Fail("instigator not found: " + instigatorId);
                }

                if (a == "unpatch")
                {
                    if (string.IsNullOrEmpty(owner) || !owner.StartsWith("jawabench.", StringComparison.Ordinal))
                        return Fail("unpatch removes only our own owners (jawabench.*), not '" + owner + "'");
                    Type ty = ResolveLiveType(typeName, out _, out _);
                    if (ty == null) return Fail("Type not found: " + typeName);
                    var done = new List<string>();
                    var h = new Harmony(owner);
                    foreach (var m in ty.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly))
                    {
                        if (m.Name != methodName) continue;
                        var info = Harmony.GetPatchInfo(m);
                        if (info == null || !info.Owners.Contains(owner)) continue;
                        h.Unpatch(m, HarmonyPatchType.All, owner);
                        var after = Harmony.GetPatchInfo(m);
                        bool gone = after == null || !after.Owners.Contains(owner);
                        done.Add(m.DeclaringType.Name + "." + m.Name + "(" + string.Join(",", m.GetParameters().Select(p => p.ParameterType.Name)) + ")" + (gone ? "" : " STILL PATCHED"));
                    }
                    if (done.Count == 0) return Fail("owner " + owner + " patches no method " + typeName + "." + methodName);
                    return new { success = done.All(d => !d.EndsWith("STILL PATCHED", StringComparison.Ordinal)), action = a, owner, unpatched = done, ticksGame = t };
                }

                if (a == "quest_add_again")
                {
                    var qm = Find.QuestManager;
                    if (qm == null) return Fail("no quest manager");
                    var list = qm.QuestsListForReading;
                    Quest q = questId < 0 ? (list.Count > 0 ? list[list.Count - 1] : null) : list.FirstOrDefault(x => x.id == questId);
                    if (q == null) return Fail("quest not found: " + questId);
                    int before = list.Count;
                    qm.Add(q);
                    return new { success = true, action = a, questId = q.id, root = q.root != null ? q.root.defName : null, countBefore = before, countAfter = qm.QuestsListForReading.Count, ticksGame = t };
                }

                if (a == "fire_attach")
                {
                    Thing target = StaticCallResolveThing(thingId, out _);
                    if (target == null) return Fail("thing not found: " + thingId);
                    if (!target.Spawned) return Fail("thing is not spawned: " + thingId);
                    FireUtility.TryAttachFire(target, size, instigator);
                    return new { success = true, action = a, thing = target.ThingID, instigator = instigator != null ? instigator.ThingID : null, burning = target.IsBurning(), ticksGame = t };
                }

                if (a == "explode")
                {
                    Map map = Find.CurrentMap;
                    if (map == null) return Fail("no current map");
                    string[] xz = (cell ?? "").Split(',');
                    if (xz.Length != 2 || !int.TryParse(xz[0].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out int x)
                        || !int.TryParse(xz[1].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out int z))
                        return Fail("cell must be 'x,z', not '" + cell + "'");
                    var c = new IntVec3(x, 0, z);
                    if (!c.InBounds(map)) return Fail("cell out of bounds: " + cell);
                    var def = DefDatabase<DamageDef>.GetNamedSilentFail(damType ?? "");
                    if (def == null) return Fail("DamageDef not found: " + damType);
                    GenExplosion.DoExplosion(c, map, radius, def, instigator);
                    return new { success = true, action = a, cell = x + "," + z, radius, damType = def.defName, instigator = instigator != null ? instigator.ThingID : null, ticksGame = t };
                }

                if (a == "reserve_unforced")
                {
                    // Why unforced: a player-forced job's Reserve takes the target from a holder and ends the holder's job
                    // (measured live on ArchBig 2026-11-25: every jawa/ordered_job Equip on a held gun was made, and the
                    // holder's Equip ended InterruptForced inside the second Reserve). jawa/ordered_job always forces, so
                    // the refusal branch of Reserve is reached only by a job that is not forced, as the think tree's are.
                    var claimant = StaticCallResolveThing(pawnId, out _) as Pawn;
                    if (claimant == null || !claimant.Spawned) return Fail("pawnId is no spawned pawn: " + pawnId);
                    Thing target = StaticCallResolveThing(thingId, out _);
                    if (target == null || !target.Spawned) return Fail("thing not found or not spawned: " + thingId);
                    if (target.Map != claimant.Map) return Fail("the pawn and the thing are on different maps");
                    var job = JobMaker.MakeJob(JobDefOf.Equip, target);
                    job.playerForced = false;
                    var rm = claimant.Map.reservationManager;
                    bool made = rm.Reserve(claimant, job, target, errorOnFailed: false);
                    if (made) rm.Release(target, claimant, job);
                    return new { success = true, action = a, pawn = claimant.ThingID, thing = target.ThingID, made, released = made, ticksGame = t };
                }

                return Fail("action must be unpatch, quest_add_again, fire_attach, explode or reserve_unforced, not '" + action + "'");
            });
        }
#endif
    }
}
