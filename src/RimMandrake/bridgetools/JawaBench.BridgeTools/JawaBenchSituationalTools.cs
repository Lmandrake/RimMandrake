// JawaBenchSituationalTools.cs - NORTHSTAR_COMPANION_GAPS_1: the reads the northstar
// situational envelope (src/RimMandrake/Utils/modcheck/{snapshot,detectors,helpers}.py) could
// only infer before. Spec: design/RimMandrake/northstar_helpers_plan.md §2 "Gaps" (G1, G3) and
// §10 item 10 (G6-G9).
//
//   pawn census  (G1)  - one call: mental state, current job + targets, prey/hunting, break
//                        imminence, needs, lord/duty, for every pawn on the map.
//   pawn roles   (G9)  - colonist/slave/prisoner/guest/lodger/wild/mutant/mech flags, ideo role,
//                        royal title, lord (job, toil, owned pawns), duty + focus, map ids.
//   incident queue peek + selective remove (G6) - the existing clear is all-or-nothing.
//   damage-event ring buffer (G7) - every TakeDamage and every Pawn.Kill, with instigator,
//                        weapon, def, amount, tick.
//   holder / stack lineage (G3+G8) - where a thing is now (holder chain, carrier, rot), and,
//                        when it is gone, the journal of what absorbed / split / ate / destroyed it.
//
// EVERY ENGINE MEMBER BELOW WAS READ OUT OF 1.6 SOURCE VIA rimsage, NOT GUESSED (2026-10-01):
//   RimWorld/IncidentQueue.cs      private List<QueuedIncident> queuedIncidents; NO per-item remove,
//                                  only Clear()/Add() - the selective remove is a reflection write.
//   RimWorld/QueuedIncident.cs     FireTick, FiringIncident, RetryDurationTicks, TriedToFire
//   RimWorld/FiringIncident.cs     def, parms, source (StorytellerComp), sourceQuestPart
//   RimWorld/IncidentParms.cs      target, points, faction, forced, quest
//   Verse/Pawn.cs                  CurJob, CurJobDef, MentalState, MentalStateDef, IsColonist,
//                                  IsFreeColonist, IsPrisoner(OfColony), IsSlave(OfColony), IsMutant,
//                                  IsGhoul, IsAnimal, IsColonyMech, IsColonistPlayerControlled,
//                                  IsCreepJoiner, HostFaction, Ideo, carryTracker,
//                                  Kill(DamageInfo?, Hediff) (override)
//   Verse/AI/MentalState.cs        def, Age, causedByMood, causedByDamage, causedByPawn,
//                                  forceRecoverAfterTicks
//   Verse/AI/Pawn_MindState.cs     mentalBreaker, duty, enemyTarget, meleeThreat,
//                                  lastAttackTargetTick, anyCloseHostilesRecently
//   Verse/AI/MentalBreaker.cs      Break{Minor,Major,Extreme}IsImminent (read mood; guarded below)
//   Verse/AI/Group/LordUtility.cs  GetLord(this Pawn)
//   Verse/AI/Group/Lord.cs         loadID, faction, ownedPawns, Map, CurLordToil, LordJob
//   Verse/AI/PawnDuty.cs           def, focus
//   RimWorld/QuestUtility.cs       IsQuestLodger, IsQuestHelper ; Verse/WildManUtility IsWildMan ;
//   Planet/CaravanUtility          IsCaravanMember ; Planet/WorldPawnsUtility IsWorldPawn
//   RimWorld/Ideo.cs               GetRole(Pawn) ; Pawn_RoyaltyTracker.MostSeniorTitle (def, faction)
//   Verse/Thing.cs                 TakeDamage(DamageInfo) - NON-virtual, so one postfix sees all
//                                  damage; TryAbsorbStack(Thing,bool), SplitOff(int),
//                                  Destroy(DestroyMode) (virtual - overrides reach it via base),
//                                  Ingested(Pawn,float) (non-virtual); holdingOwner, ParentHolder,
//                                  MapHeld, PositionHeld, Destroyed, Spawned
//   Verse/DamageInfo.cs            Def, Amount, Instigator, Weapon, HitPart, IntendedTarget
//   Verse/DamageWorker.cs          DamageResult.totalDamageDealt, deflected, hediffs
//   Verse/ThingOwnerUtility.cs     GetAllThingsRecursively(IThingHolder, List<Thing>, ...) and the
//                                  Map overload; Planet/World.cs is an IThingHolder
//   RimWorld/CompRottable.cs       RotProgress, Stage ; ForbidUtility.IsForbidden(Thing, Faction)
//
// GATING: reads are ungated. jawa/incident_queue_remove is #if JAWA_GM_TOOLS, the same family
// and tier as the already-gated incident-queue clear (it edits what WILL act on the player).
//
// 🔴 THE RECORDERS ARE LAZY, LIKE EVERY HARMONY CONTACT POINT HERE: JawaBenchInit installs them
// on the FIRST jawa/ tool call of a session. Damage, deaths, merges and meals that happened
// before that call are NOT in the buffers. Every read reports `installed` and the oldest
// retained event so absence can never be mistaken for "nothing happened".
//
// THREAD AFFINITY: the patches run on the game thread (that is where damage happens); every tool
// reads the buffers inside ctx.MainThread.InvokeAsync, so reads and writes never interleave.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimBridgeServer.Sdk;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace JawaBench.BridgeTools
{
    /// <summary>Fixed-capacity ring; Total counts every Add so a reader can see what was overwritten.</summary>
    internal sealed class JawaEventRing<T> where T : class
    {
        private readonly T[] _buf;
        private long _total;
        internal JawaEventRing(int capacity) { _buf = new T[capacity]; }
        internal int Capacity => _buf.Length;
        internal long Total => _total;
        internal long Overwritten => Math.Max(0, _total - _buf.Length);
        internal long Add(T item)
        {
            long seq = _total;
            _buf[(int)(seq % _buf.Length)] = item;
            _total = seq + 1;
            return seq;
        }
        internal void Clear()
        {
            Array.Clear(_buf, 0, _buf.Length);
            _total = 0;
        }
        /// <summary>Oldest first.</summary>
        internal List<T> Snapshot()
        {
            var list = new List<T>();
            long start = Math.Max(0, _total - _buf.Length);
            for (long s = start; s < _total; s++)
            {
                var e = _buf[(int)(s % _buf.Length)];
                if (e != null) list.Add(e);
            }
            return list;
        }
    }

    internal sealed class JawaDamageEvent
    {
        public long seq; public int tick; public string kind;   // "damage" | "kill"
        public string victimId; public string victimDef; public bool victimIsPawn; public string victimFaction;
        public bool victimColonist; public bool victimDeadAfter;
        public string damageDef; public float amount; public float totalDealt; public bool deflected;
        public string instigatorId; public string instigatorDef; public string instigatorFaction;
        public string weapon; public string hitPart; public string culpritHediff;
        public List<string> hediffsAdded;
        public int mapUniqueId = -1; public int x = -1; public int z = -1;
    }

    internal sealed class JawaLineageEvent
    {
        public long seq; public int tick; public string kind;   // absorb | split | detach | ingest | destroy
        public string thingId; public string def; public string otherId; public string otherDef;
        public int count; public int stackAfter; public string holder; public string destroyMode;
        public int mapUniqueId = -1; public int x = -1; public int z = -1;
    }

    /// <summary>
    /// Harmony contact point (same discipline as JawaBenchArgGuard / LogAutoOpenSuppress): no
    /// Harmony type outside Install(); every patch body is try/catch so a recorder can never break
    /// damage, death, hauling or eating. A patch that fails to install is listed in InstallErrors
    /// and the tools refuse rather than report an empty log.
    /// </summary>
    internal static class JawaBenchEventRecorder
    {
        internal const int DamageCapacity = 4096;
        internal const int LineageCapacity = 4096;
        internal static readonly JawaEventRing<JawaDamageEvent> Damage = new JawaEventRing<JawaDamageEvent>(DamageCapacity);
        internal static readonly JawaEventRing<JawaLineageEvent> Lineage = new JawaEventRing<JawaLineageEvent>(LineageCapacity);

        internal static bool DamageInstalled, KillInstalled, LineageInstalled;
        internal static readonly List<string> InstallErrors = new List<string>();
        internal static DateTime InstalledUtc;
        internal static int RecordErrors;        // exceptions inside a patch body (counted, never thrown)
        internal static string LastRecordError;

        private static readonly object Gate = new object();
        private static bool _attempted;

        internal static void Install()
        {
            lock (Gate)
            {
                if (_attempted) return;
                _attempted = true;
                InstalledUtc = DateTime.UtcNow;
                Harmony harmony;
                try { harmony = new Harmony("mandrake.jawabench.eventrecorder"); }
                catch (Exception e) { InstallErrors.Add("Harmony ctor: " + e.GetType().Name + ": " + e.Message); return; }

                DamageInstalled = TryPatch(harmony, typeof(Thing), "TakeDamage", new[] { typeof(DamageInfo) },
                    null, nameof(TakeDamagePostfix));
                KillInstalled = TryPatch(harmony, typeof(Pawn), "Kill", new[] { typeof(DamageInfo?), typeof(Hediff) },
                    null, nameof(KillPostfix));
                bool a = TryPatch(harmony, typeof(Thing), "TryAbsorbStack", new[] { typeof(Thing), typeof(bool) },
                    nameof(AbsorbPrefix), nameof(AbsorbPostfix));
                bool s = TryPatch(harmony, typeof(Thing), "SplitOff", new[] { typeof(int) },
                    nameof(SplitPrefix), nameof(SplitPostfix));
                bool i = TryPatch(harmony, typeof(Thing), "Ingested", new[] { typeof(Pawn), typeof(float) },
                    nameof(IngestPrefix), nameof(IngestPostfix));
                bool d = TryPatch(harmony, typeof(Thing), "Destroy", new[] { typeof(DestroyMode) },
                    nameof(DestroyPrefix), null);
                LineageInstalled = a && s && i && d;
                try
                {
                    Log.Message("[JawaBench] event recorder: damage=" + DamageInstalled + " kill=" + KillInstalled +
                                " lineage=" + LineageInstalled +
                                (InstallErrors.Count > 0 ? " ERRORS: " + string.Join("; ", InstallErrors) : ""));
                }
                catch { }
            }
        }

        private static bool TryPatch(Harmony h, Type t, string name, Type[] args, string prefix, string postfix)
        {
            try
            {
                var m = AccessTools.Method(t, name, args);
                if (m == null) { InstallErrors.Add(t.Name + "." + name + " not found"); return false; }
                var self = typeof(JawaBenchEventRecorder);
                h.Patch(m,
                    prefix: prefix == null ? null : new HarmonyMethod(self.GetMethod(prefix, BindingFlags.Static | BindingFlags.NonPublic)),
                    postfix: postfix == null ? null : new HarmonyMethod(self.GetMethod(postfix, BindingFlags.Static | BindingFlags.NonPublic)));
                return true;
            }
            catch (Exception e)
            {
                InstallErrors.Add(t.Name + "." + name + ": " + e.GetType().Name + ": " + e.Message);
                return false;
            }
        }

        private static void NoteError(Exception e)
        {
            RecordErrors++;
            LastRecordError = e.GetType().Name + ": " + e.Message;
        }

        private static int Tick() { try { return Find.TickManager != null ? Find.TickManager.TicksGame : -1; } catch { return -1; } }

        private static bool IsItem(Thing t) => t != null && t.def != null && t.def.category == ThingCategory.Item;

        private static void Place(Thing t, out int mapId, out int x, out int z)
        {
            mapId = -1; x = -1; z = -1;
            try
            {
                var m = t.MapHeld;
                if (m != null) mapId = m.uniqueID;
                var p = t.PositionHeld;
                if (p.IsValid) { x = p.x; z = p.z; }
            }
            catch { }
        }

        internal static string DescribeHolder(IThingHolder h)
        {
            if (h == null) return null;
            var th = h as Thing;
            if (th != null) return "thing:" + th.ThingID;
            var map = h as Map;
            if (map != null) return "map:" + map.uniqueID;
            var carry = h as Pawn_CarryTracker;
            if (carry != null) return "carriedBy:" + (carry.pawn != null ? carry.pawn.ThingID : "?");
            var inv = h as Pawn_InventoryTracker;
            if (inv != null) return "inventoryOf:" + (inv.pawn != null ? inv.pawn.ThingID : "?");
            var eq = h as Pawn_EquipmentTracker;
            if (eq != null) return "equippedBy:" + (eq.pawn != null ? eq.pawn.ThingID : "?");
            var ap = h as Pawn_ApparelTracker;
            if (ap != null) return "wornBy:" + (ap.pawn != null ? ap.pawn.ThingID : "?");
            var comp = h as ThingComp;
            if (comp != null) return "comp:" + comp.GetType().Name + "@" + (comp.parent != null ? comp.parent.ThingID : "?");
            var wo = h as WorldObject;
            if (wo != null) return "worldObject:" + wo.GetUniqueLoadID();
            if (h is World) return "world";
            return "holder:" + h.GetType().Name;
        }

        // ---------------------------------------------------------------- damage + kill

        private static void TakeDamagePostfix(Thing __instance, DamageInfo dinfo, DamageWorker.DamageResult __result)
        {
            try
            {
                if (__instance == null || __instance.def == null) return;
                // Plants and filth burn by the hundred in any fire and would evict every pawn event.
                var cat = __instance.def.category;
                if (cat == ThingCategory.Plant || cat == ThingCategory.Filth || cat == ThingCategory.Mote) return;
                var victimPawn = __instance as Pawn;
                var inst = dinfo.Instigator;
                var e = new JawaDamageEvent
                {
                    tick = Tick(), kind = "damage",
                    victimId = __instance.ThingID, victimDef = __instance.def.defName,
                    victimIsPawn = victimPawn != null,
                    victimFaction = __instance.Faction != null && __instance.Faction.def != null ? __instance.Faction.def.defName : null,
                    victimColonist = victimPawn != null && victimPawn.IsColonist,
                    victimDeadAfter = victimPawn != null ? victimPawn.Dead : __instance.Destroyed,
                    damageDef = dinfo.Def != null ? dinfo.Def.defName : null,
                    amount = dinfo.Amount,
                    totalDealt = __result != null ? __result.totalDamageDealt : 0f,
                    deflected = __result != null && __result.deflected,
                    instigatorId = inst != null ? inst.ThingID : null,
                    instigatorDef = inst != null && inst.def != null ? inst.def.defName : null,
                    instigatorFaction = inst != null && inst.Faction != null && inst.Faction.def != null ? inst.Faction.def.defName : null,
                    weapon = dinfo.Weapon != null ? dinfo.Weapon.defName : null,
                    hitPart = dinfo.HitPart != null && dinfo.HitPart.def != null ? dinfo.HitPart.def.defName : null,
                    hediffsAdded = __result != null && __result.hediffs != null
                        ? __result.hediffs.Where(h => h != null && h.def != null).Select(h => h.def.defName).ToList()
                        : null
                };
                Place(__instance, out e.mapUniqueId, out e.x, out e.z);
                e.seq = Damage.Add(e);
            }
            catch (Exception ex) { NoteError(ex); }
        }

        private static void KillPostfix(Pawn __instance, DamageInfo? dinfo, Hediff exactCulprit)
        {
            try
            {
                if (__instance == null || !__instance.Dead) return;   // Kill can early-out; record only real deaths
                var inst = dinfo.HasValue ? dinfo.Value.Instigator : null;
                var e = new JawaDamageEvent
                {
                    tick = Tick(), kind = "kill",
                    victimId = __instance.ThingID, victimDef = __instance.def != null ? __instance.def.defName : null,
                    victimIsPawn = true,
                    victimFaction = __instance.Faction != null && __instance.Faction.def != null ? __instance.Faction.def.defName : null,
                    victimColonist = __instance.Faction == Faction.OfPlayer && __instance.RaceProps != null && __instance.RaceProps.Humanlike,
                    victimDeadAfter = true,
                    damageDef = dinfo.HasValue && dinfo.Value.Def != null ? dinfo.Value.Def.defName : null,
                    amount = dinfo.HasValue ? dinfo.Value.Amount : 0f,
                    instigatorId = inst != null ? inst.ThingID : null,
                    instigatorDef = inst != null && inst.def != null ? inst.def.defName : null,
                    instigatorFaction = inst != null && inst.Faction != null && inst.Faction.def != null ? inst.Faction.def.defName : null,
                    weapon = dinfo.HasValue && dinfo.Value.Weapon != null ? dinfo.Value.Weapon.defName : null,
                    culpritHediff = exactCulprit != null && exactCulprit.def != null ? exactCulprit.def.defName : null
                };
                Place(__instance, out e.mapUniqueId, out e.x, out e.z);
                e.seq = Damage.Add(e);
            }
            catch (Exception ex) { NoteError(ex); }
        }

        // ---------------------------------------------------------------- lineage

        private static void AddLineage(string kind, Thing t, Thing other, int count, string destroyMode)
        {
            var e = new JawaLineageEvent
            {
                tick = Tick(), kind = kind,
                thingId = t.ThingID, def = t.def != null ? t.def.defName : null,
                otherId = other != null ? other.ThingID : null,
                otherDef = other != null && other.def != null ? other.def.defName : null,
                count = count, stackAfter = t.stackCount,
                holder = DescribeHolder(t.ParentHolder), destroyMode = destroyMode
            };
            Place(t, out e.mapUniqueId, out e.x, out e.z);
            e.seq = Lineage.Add(e);
        }

        private static void AbsorbPrefix(Thing other, out int __state)
        {
            __state = -1;
            try { if (other != null) __state = other.stackCount; } catch (Exception ex) { NoteError(ex); }
        }

        // Recorded from the ABSORBED thing's point of view: thingId = the stack that lost count,
        // otherId = the stack that took it. A full absorb is followed by a destroy event.
        private static void AbsorbPostfix(Thing __instance, Thing other, int __state)
        {
            try
            {
                if (other == null || __instance == null || __state < 0 || !IsItem(other)) return;
                int taken = __state - other.stackCount;
                if (taken <= 0) return;
                AddLineage("absorb", other, __instance, taken, null);
            }
            catch (Exception ex) { NoteError(ex); }
        }

        private static void SplitPrefix(Thing __instance, out int __state)
        {
            __state = -1;
            try { if (__instance != null) __state = __instance.stackCount; } catch (Exception ex) { NoteError(ex); }
        }

        // split  : thingId = source stack, otherId = the NEW thing carrying `count`.
        // detach : the whole stack left its holder/map (count >= stackCount); same id continues.
        private static void SplitPostfix(Thing __instance, int count, Thing __result, int __state)
        {
            try
            {
                if (__instance == null || __result == null || !IsItem(__instance)) return;
                if (ReferenceEquals(__result, __instance)) AddLineage("detach", __instance, null, __state, null);
                else AddLineage("split", __instance, __result, count, null);
            }
            catch (Exception ex) { NoteError(ex); }
        }

        private static void IngestPrefix(Thing __instance, out int __state)
        {
            __state = -1;
            try { if (__instance != null) __state = __instance.stackCount; } catch (Exception ex) { NoteError(ex); }
        }

        private static void IngestPostfix(Thing __instance, Pawn ingester, int __state)
        {
            try
            {
                if (__instance == null || !IsItem(__instance)) return;
                int eaten = __state >= 0 ? __state - __instance.stackCount : 0;
                AddLineage("ingest", __instance, ingester, eaten, null);
            }
            catch (Exception ex) { NoteError(ex); }
        }

        private static void DestroyPrefix(Thing __instance, DestroyMode mode)
        {
            try
            {
                if (__instance == null || __instance.Destroyed || !IsItem(__instance)) return;
                AddLineage("destroy", __instance, null, __instance.stackCount, mode.ToString());
            }
            catch (Exception ex) { NoteError(ex); }
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        // ================================================================
        //  shared row builders
        // ================================================================

        private static object TargetRow(LocalTargetInfo t)
        {
            if (!t.IsValid) return null;
            if (t.HasThing)
            {
                var th = t.Thing;
                return new { thingId = th.ThingID, def = th.def != null ? th.def.defName : null,
                             x = th.PositionHeld.IsValid ? th.PositionHeld.x : -1, z = th.PositionHeld.IsValid ? th.PositionHeld.z : -1 };
            }
            return new { thingId = (string)null, def = (string)null, x = t.Cell.x, z = t.Cell.z };
        }

        private static object LordRow(Pawn p, bool detail)
        {
            var lord = p.GetLord();
            if (lord == null) return null;
            if (!detail)
                return new
                {
                    loadId = lord.loadID,
                    lordJob = lord.LordJob != null ? lord.LordJob.GetType().Name : null,
                    toil = lord.CurLordToil != null ? lord.CurLordToil.GetType().Name : null
                };
            return new
            {
                loadId = lord.loadID,
                lordJob = lord.LordJob != null ? lord.LordJob.GetType().Name : null,
                toil = lord.CurLordToil != null ? lord.CurLordToil.GetType().Name : null,
                faction = lord.faction != null && lord.faction.def != null ? lord.faction.def.defName : null,
                factionName = lord.faction != null ? lord.faction.Name : null,
                ownedPawnCount = lord.ownedPawns != null ? lord.ownedPawns.Count : 0,
                ownedPawns = lord.ownedPawns != null ? lord.ownedPawns.Take(50).Select(o => o.ThingID).ToList() : new List<string>(),
                mapUniqueId = lord.Map != null ? lord.Map.uniqueID : -1
            };
        }

        // Anonymous projections: the bridge serialises anonymous-type PROPERTIES; the recorder's
        // event classes carry public FIELDS, which a property-only serialiser would emit as {}.
        private static object DamageRow(JawaDamageEvent e) => new
        {
            e.seq, e.tick, e.kind, e.victimId, e.victimDef, e.victimIsPawn, e.victimFaction, e.victimColonist,
            e.victimDeadAfter, e.damageDef, e.amount, e.totalDealt, e.deflected, e.instigatorId, e.instigatorDef,
            e.instigatorFaction, e.weapon, e.hitPart, e.culpritHediff, e.hediffsAdded, e.mapUniqueId, e.x, e.z
        };

        private static object LineageRow(JawaLineageEvent e) => new
        {
            e.seq, e.tick, e.kind, e.thingId, e.def, e.otherId, e.otherDef, e.count, e.stackAfter, e.holder,
            e.destroyMode, e.mapUniqueId, e.x, e.z
        };

        private static object DutyRow(Pawn p)
        {
            var d = p.mindState != null ? p.mindState.duty : null;
            if (d == null) return null;
            return new { def = d.def != null ? d.def.defName : null, focus = TargetRow(d.focus) };
        }

        /// <summary>Population shared by census and roles. ids beats faction; unresolved ids FAIL the call.</summary>
        private static bool SelectPawns(Map map, string ids, string faction, bool includeDead, out List<Pawn> pawns, out string err)
        {
            pawns = new List<Pawn>();
            err = null;
            if (!string.IsNullOrWhiteSpace(ids))
            {
                var missing = new List<string>();
                foreach (var tok in ids.Split(',').Select(s => s.Trim()).Where(s => s.Length > 0))
                {
                    string perr;
                    var p = FindPawn(tok, out perr);
                    if (p == null)
                    {
                        // a dead pawn sits in a Corpse, which FindPawn's spawned/held/world passes do not see
                        p = map.listerThings.AllThings.OfType<Corpse>().Select(c => c.InnerPawn)
                               .FirstOrDefault(ip => ip != null && (string.Equals(ip.ThingID, tok, StringComparison.OrdinalIgnoreCase)
                                   || string.Equals("Thing_" + ip.ThingID, tok, StringComparison.OrdinalIgnoreCase)));
                    }
                    if (p == null) missing.Add(tok); else if (!pawns.Contains(p)) pawns.Add(p);
                }
                if (missing.Count > 0) { err = "No pawn matching: " + string.Join(", ", missing) + ". Nothing was read; fix the id list."; return false; }
                return true;
            }

            var playerFaction = Faction.OfPlayer;
            var pool = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
            if (includeDead)
                foreach (var c in map.listerThings.AllThings.OfType<Corpse>())
                    if (c.InnerPawn != null) pool.Add(c.InnerPawn);
            if (string.IsNullOrWhiteSpace(faction)) { pawns = pool; return true; }
            var f = faction.Trim();
            bool known = string.Equals(f, "player", StringComparison.OrdinalIgnoreCase) || string.Equals(f, "hostile", StringComparison.OrdinalIgnoreCase)
                      || string.Equals(f, "nonplayer", StringComparison.OrdinalIgnoreCase) || string.Equals(f, "none", StringComparison.OrdinalIgnoreCase)
                      || DefDatabase<FactionDef>.GetNamedSilentFail(f) != null;
            if (!known) { err = "Unknown faction filter '" + faction + "'. Use player, hostile, nonplayer, none (factionless, e.g. wild animals) or a FactionDef defName."; return false; }
            foreach (var p in pool)
            {
                bool isPlayer = p.Faction == playerFaction;
                bool hostile = p.Faction != null && p.Faction.HostileTo(playerFaction);
                bool keep =
                    string.Equals(f, "player", StringComparison.OrdinalIgnoreCase) ? isPlayer :
                    string.Equals(f, "hostile", StringComparison.OrdinalIgnoreCase) ? hostile :
                    string.Equals(f, "nonplayer", StringComparison.OrdinalIgnoreCase) ? !isPlayer :
                    string.Equals(f, "none", StringComparison.OrdinalIgnoreCase) ? p.Faction == null :
                    (p.Faction != null && p.Faction.def != null && string.Equals(p.Faction.def.defName, f, StringComparison.OrdinalIgnoreCase));
                if (keep) pawns.Add(p);
            }
            return true;
        }

        // ================================================================
        //  G1  pawn census
        // ================================================================

        [Tool(
            "jawa/pawn_census",
            Description =
                "One call, every pawn on the current map: mental state (def, aggro, age, cause), " +
                "current job def + its A/B targets, whether it is hunting prey (PredatorHunt job) and " +
                "the prey id, enemyTarget / meleeThreat ids, mental-break imminence, food/rest/mood/joy " +
                "levels, and a compact lord + duty. Replaces N calls of the per-pawn mental/need/break " +
                "tools. Filter with faction (player/hostile/nonplayer/none/defName) or an explicit id " +
                "list (an id that resolves to nothing FAILS the call - it is never silently dropped). " +
                "A null mentalState means the pawn is in none; a null needs.mood means the pawn HAS no " +
                "mood need (animals), not that it reads zero. Per-pawn read failures are listed in " +
                "readErrors, never swallowed. A factionless predator is NOT hostile - read " +
                "isPredatorHunting/preyId, not a faction flag.",
            ResultDescription =
                "success, count, totalSelected, truncated, ticksGame, readErrors[], pawns[] with id, name, " +
                "kindDef, faction, isPlayer, hostile, isColonist, spawned, dead, downed, x, z, inMentalState, " +
                "mentalState{def, isAggro, ageTicks, causedByMood, causedByDamage, causedByPawn, " +
                "forceRecoverAfterTicks}, breakImminent{minor, major, extreme}, job{def, targetA, targetB} (each target: thingId, def, x, z; thingId null for a cell), " +
                "isPredatorHunting, preyId, enemyTargetId, meleeThreatId, lastAttackTargetTick, " +
                "anyCloseHostilesRecently, needs{food, rest, mood, joy}, lord{loadId, lordJob, toil}, duty{def, focus}.")]
        public static async Task<object> PawnCensus(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Faction filter: player, hostile, nonplayer, none (factionless) or a FactionDef defName. Omit for all.")]
            string faction = null,
            [ToolParameter(Description = "Comma-separated pawn ids (bare or Thing_ prefixed). Overrides faction; may name off-map/held/dead pawns.")]
            string ids = null,
            [ToolParameter(Description = "Include dead pawns lying in corpses on this map. Default false.")]
            bool includeDead = false,
            [ToolParameter(Description = "Cap on returned rows (1-2000). Default 500.")]
            int limit = 500)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                if (limit < 1 || limit > 2000) return Fail("limit must be 1-2000, got " + limit + ".");
                List<Pawn> pawns;
                if (!SelectPawns(map, ids, faction, includeDead, out pawns, out err)) return Fail(err);

                var playerFaction = Faction.OfPlayer;
                var rows = new List<object>();
                var readErrors = new List<object>();
                foreach (var p in pawns)
                {
                    if (rows.Count >= limit) break;
                    try
                    {
                        var ms = p.MentalState;
                        object mental = ms == null ? null : (object)new
                        {
                            def = ms.def != null ? ms.def.defName : null,
                            isAggro = ms.def != null && ms.def.IsAggro,
                            ageTicks = ms.Age,
                            causedByMood = ms.causedByMood,
                            causedByDamage = ms.causedByDamage,
                            causedByPawn = ms.causedByPawn != null ? ms.causedByPawn.ThingID : null,
                            forceRecoverAfterTicks = ms.forceRecoverAfterTicks
                        };

                        object breakImm = null;
                        if (!p.Dead && p.needs != null && p.needs.mood != null && p.mindState != null && p.mindState.mentalBreaker != null)
                        {
                            try
                            {
                                var mb = p.mindState.mentalBreaker;
                                breakImm = new { minor = mb.BreakMinorIsImminent, major = mb.BreakMajorIsImminent, extreme = mb.BreakExtremeIsImminent };
                            }
                            catch (Exception be) { readErrors.Add(new { pawn = p.ThingID, field = "breakImminent", reason = be.GetType().Name + ": " + be.Message }); }
                        }

                        var job = p.CurJob;
                        bool hunting = job != null && job.def == JobDefOf.PredatorHunt;
                        string preyId = hunting && job.targetA.HasThing ? job.targetA.Thing.ThingID : null;

                        object needs = null;
                        if (p.needs != null)
                            needs = new
                            {
                                food = p.needs.food != null ? (float?)p.needs.food.CurLevelPercentage : null,
                                rest = p.needs.rest != null ? (float?)p.needs.rest.CurLevelPercentage : null,
                                mood = p.needs.mood != null ? (float?)p.needs.mood.CurLevelPercentage : null,
                                joy = p.needs.joy != null ? (float?)p.needs.joy.CurLevelPercentage : null
                            };

                        var pos = p.PositionHeld;
                        rows.Add(new
                        {
                            id = p.ThingID,
                            name = p.Name != null ? p.Name.ToStringShort : p.LabelShortCap.ToString(),
                            kindDef = p.kindDef != null ? p.kindDef.defName : null,
                            faction = p.Faction != null && p.Faction.def != null ? p.Faction.def.defName : null,
                            isPlayer = p.Faction == playerFaction,
                            hostile = p.Faction != null && p.Faction.HostileTo(playerFaction),
                            isColonist = p.IsColonist,
                            spawned = p.Spawned,
                            dead = p.Dead,
                            downed = !p.Dead && p.Downed,
                            x = pos.IsValid ? pos.x : -1,
                            z = pos.IsValid ? pos.z : -1,
                            inMentalState = ms != null,
                            mentalState = mental,
                            breakImminent = breakImm,
                            job = job == null ? null : (object)new { def = job.def != null ? job.def.defName : null, targetA = TargetRow(job.targetA), targetB = TargetRow(job.targetB) },
                            isPredatorHunting = hunting,
                            preyId,
                            enemyTargetId = p.mindState != null && p.mindState.enemyTarget != null ? p.mindState.enemyTarget.ThingID : null,
                            meleeThreatId = p.mindState != null && p.mindState.meleeThreat != null ? p.mindState.meleeThreat.ThingID : null,
                            lastAttackTargetTick = p.mindState != null ? p.mindState.lastAttackTargetTick : -1,
                            anyCloseHostilesRecently = p.mindState != null && p.mindState.anyCloseHostilesRecently,
                            needs,
                            lord = LordRow(p, false),
                            duty = DutyRow(p)
                        });
                    }
                    catch (Exception e)
                    {
                        readErrors.Add(new { pawn = p.ThingID, field = "row", reason = e.GetType().Name + ": " + e.Message });
                    }
                }
                return new
                {
                    success = true,
                    count = rows.Count,
                    totalSelected = pawns.Count,
                    truncated = Math.Max(0, pawns.Count - limit),
                    readErrors,
                    pawns = rows,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  G9  pawn roles + lord
        // ================================================================

        [Tool(
            "jawa/pawn_roles",
            Description =
                "Who each pawn IS to the colony, which the faction flag cannot say: isColonist / " +
                "isFreeColonist / isSlave(OfColony) / isPrisoner(OfColony) / guestStatus + hostFaction / " +
                "quest lodger / quest helper / wild man / creep joiner / mutant / ghoul / animal / colony " +
                "mech / player-controlled / caravan member / world pawn, plus ideo role, most senior royal " +
                "title, and the FULL lord (lordJob, toil, faction, owned pawns) and duty (def + focus), " +
                "with the pawn's map uniqueID and index. isPlayer is true for a colony animal - use " +
                "isColonist for 'a colonist'. Same filters as the census; an unresolved id FAILS the call.",
            ResultDescription =
                "success, count, totalSelected, truncated, ticksGame, readErrors[], pawns[] with id, name, " +
                "kindDef, faction, isPlayer, isColonist, isFreeColonist, isSlave, isSlaveOfColony, isPrisoner, " +
                "isPrisonerOfColony, guestStatus, hostFaction, isQuestLodger, isQuestHelper, isWildMan, " +
                "isCreepJoiner, isMutant, isGhoul, isAnimal, isColonyMech, isColonistPlayerControlled, " +
                "isCaravanMember, isWorldPawn, dead, spawned, ideoRole, royalTitle, royalTitleFaction, " +
                "lord{loadId, lordJob, toil, faction, factionName, ownedPawnCount, ownedPawns, mapUniqueId}, " +
                "duty{def, focus}, mapUniqueId, mapIndex.")]
        public static async Task<object> PawnRoles(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Faction filter: player, hostile, nonplayer, none (factionless) or a FactionDef defName. Omit for all.")]
            string faction = null,
            [ToolParameter(Description = "Comma-separated pawn ids (bare or Thing_ prefixed). Overrides faction.")]
            string ids = null,
            [ToolParameter(Description = "Include dead pawns lying in corpses on this map. Default false.")]
            bool includeDead = false,
            [ToolParameter(Description = "Cap on returned rows (1-2000). Default 500.")]
            int limit = 500)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                if (limit < 1 || limit > 2000) return Fail("limit must be 1-2000, got " + limit + ".");
                List<Pawn> pawns;
                if (!SelectPawns(map, ids, faction, includeDead, out pawns, out err)) return Fail(err);

                var playerFaction = Faction.OfPlayer;
                var rows = new List<object>();
                var readErrors = new List<object>();
                foreach (var p in pawns)
                {
                    if (rows.Count >= limit) break;
                    try
                    {
                        string ideoRole = null;
                        try
                        {
                            var ideo = p.Ideo;
                            var role = ideo != null ? ideo.GetRole(p) : null;
                            if (role != null) ideoRole = role.def != null ? role.def.defName : role.GetType().Name;
                        }
                        catch (Exception ie) { readErrors.Add(new { pawn = p.ThingID, field = "ideoRole", reason = ie.GetType().Name + ": " + ie.Message }); }

                        var title = p.royalty != null ? p.royalty.MostSeniorTitle : null;
                        var m = p.MapHeld;
                        rows.Add(new
                        {
                            id = p.ThingID,
                            name = p.Name != null ? p.Name.ToStringShort : p.LabelShortCap.ToString(),
                            kindDef = p.kindDef != null ? p.kindDef.defName : null,
                            faction = p.Faction != null && p.Faction.def != null ? p.Faction.def.defName : null,
                            isPlayer = p.Faction == playerFaction,
                            isColonist = p.IsColonist,
                            isFreeColonist = p.IsFreeColonist,
                            isSlave = p.IsSlave,
                            isSlaveOfColony = p.IsSlaveOfColony,
                            isPrisoner = p.IsPrisoner,
                            isPrisonerOfColony = p.IsPrisonerOfColony,
                            guestStatus = p.guest != null ? p.guest.GuestStatus.ToString() : null,
                            hostFaction = p.HostFaction != null && p.HostFaction.def != null ? p.HostFaction.def.defName : null,
                            isQuestLodger = p.IsQuestLodger(),
                            isQuestHelper = p.IsQuestHelper(),
                            isWildMan = p.IsWildMan(),
                            isCreepJoiner = p.IsCreepJoiner,
                            isMutant = p.IsMutant,
                            isGhoul = p.IsGhoul,
                            isAnimal = p.IsAnimal,
                            isColonyMech = p.IsColonyMech,
                            isColonistPlayerControlled = p.IsColonistPlayerControlled,
                            isCaravanMember = p.IsCaravanMember(),
                            isWorldPawn = p.IsWorldPawn(),
                            dead = p.Dead,
                            spawned = p.Spawned,
                            ideoRole,
                            royalTitle = title != null && title.def != null ? title.def.defName : null,
                            royalTitleFaction = title != null && title.faction != null && title.faction.def != null ? title.faction.def.defName : null,
                            lord = LordRow(p, true),
                            duty = DutyRow(p),
                            mapUniqueId = m != null ? m.uniqueID : -1,
                            mapIndex = m != null ? m.Index : -1
                        });
                    }
                    catch (Exception e)
                    {
                        readErrors.Add(new { pawn = p.ThingID, field = "row", reason = e.GetType().Name + ": " + e.Message });
                    }
                }
                return new
                {
                    success = true,
                    count = rows.Count,
                    totalSelected = pawns.Count,
                    truncated = Math.Max(0, pawns.Count - limit),
                    readErrors,
                    pawns = rows,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  G6  incident queue peek + selective remove
        // ================================================================

        private static List<QueuedIncident> QueueBackingList(out string err)
        {
            err = null;
            if (Current.Game == null || Find.Storyteller == null || Find.Storyteller.incidentQueue == null) { err = "No active game/storyteller."; return null; }
            var f = typeof(IncidentQueue).GetField("queuedIncidents", BindingFlags.Instance | BindingFlags.NonPublic);
            if (f == null) { err = "IncidentQueue.queuedIncidents field not found - the engine renamed it; selective access is impossible, nothing was read."; return null; }
            var list = f.GetValue(Find.Storyteller.incidentQueue) as List<QueuedIncident>;
            if (list == null) { err = "IncidentQueue.queuedIncidents is not a List<QueuedIncident> (" + (f.FieldType.Name) + ")."; return null; }
            return list;
        }

        private static object QueuedRow(QueuedIncident qi, int index, int now)
        {
            var fi = qi.FiringIncident;
            var parms = fi != null ? fi.parms : null;
            string target = null;
            if (parms != null && parms.target != null)
            {
                var tm = parms.target as Map;
                target = tm != null ? "map:" + tm.uniqueID : (parms.target is World ? "world" : parms.target.GetType().Name);
            }
            return new
            {
                index,
                defName = fi != null && fi.def != null ? fi.def.defName : null,
                fireTick = qi.FireTick,
                ticksUntilFire = qi.FireTick - now,
                retryDurationTicks = qi.RetryDurationTicks,
                triedToFire = qi.TriedToFire,
                points = parms != null ? parms.points : -1f,
                faction = parms != null && parms.faction != null && parms.faction.def != null ? parms.faction.def.defName : null,
                forced = parms != null && parms.forced,
                target,
                source = fi != null && fi.source != null ? fi.source.GetType().Name : null,
                fromQuest = fi != null && (fi.sourceQuestPart != null || (parms != null && parms.quest != null))
            };
        }

        [Tool(
            "jawa/incident_queue_peek",
            Description =
                "READ the storyteller's incident queue without changing it: every queued incident with " +
                "def, fireTick, ticks until it fires, retry window, whether it already tried, points, " +
                "faction, target map, source comp and whether a quest queued it. The backing list is " +
                "private (IncidentQueue.queuedIncidents) and read by reflection; if the engine renamed " +
                "it this FAILS rather than reporting an empty queue. NOT covered: quest-scheduled " +
                "incidents that live in a quest's own parts, and map-condition timers - an empty queue " +
                "does not mean nothing is coming.",
            ResultDescription = "success, count, ticksGame, queue[] (index, defName, fireTick, ticksUntilFire, retryDurationTicks, triedToFire, points, faction, forced, target, source, fromQuest).")]
        public static async Task<object> IncidentQueuePeek(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var list = QueueBackingList(out err);
                if (list == null) return Fail(err);
                int now = TicksGameSafe();
                var rows = new List<object>();
                for (int i = 0; i < list.Count; i++) rows.Add(QueuedRow(list[i], i, now));
                return new { success = true, count = rows.Count, queue = rows, ticksGame = now };
            }).ConfigureAwait(false);
        }

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/incident_queue_remove",
            Description =
                "Remove SELECTED entries from the storyteller incident queue - the selective half the " +
                "all-or-nothing queue clear lacks. Select by defName and/or fireTick (both given = both " +
                "must match). DRY RUN BY DEFAULT: pass dryRun=false to remove. A selector that matches " +
                "NOTHING fails (success=false) and lists the queue, so a typo cannot read as 'removed'. " +
                "Writes the private backing list by reflection and READS IT BACK: removedCount is the " +
                "measured drop in queue length, not the number of matches.",
            ResultDescription = "success, dryRun, matchedCount, matched[], removedCount (measured), countBefore, countAfter, remaining[], ticksGame. matched[]/remaining[] rows: index, defName, fireTick, ticksUntilFire, retryDurationTicks, triedToFire, points, faction, forced, target, source, fromQuest.")]
        public static async Task<object> IncidentQueueRemove(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "IncidentDef defName to remove (exact, case-insensitive).")]
            string defName = null,
            [ToolParameter(Description = "Exact fireTick to remove (from the peek). -1 = any.")]
            int fireTick = -1,
            [ToolParameter(Description = "Default true: report what WOULD be removed and change nothing.")]
            bool dryRun = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (string.IsNullOrWhiteSpace(defName) && fireTick < 0)
                    return Fail("Give defName and/or fireTick. To remove everything use the queue clear tool.");
                if (!string.IsNullOrWhiteSpace(defName) && DefDatabase<IncidentDef>.GetNamedSilentFail(defName.Trim()) == null)
                    return Fail("No IncidentDef named '" + defName + "'.");
                string err; var list = QueueBackingList(out err);
                if (list == null) return Fail(err);
                int now = TicksGameSafe();
                Func<QueuedIncident, bool> match = qi =>
                    (string.IsNullOrWhiteSpace(defName) || (qi.FiringIncident != null && qi.FiringIncident.def != null
                        && string.Equals(qi.FiringIncident.def.defName, defName.Trim(), StringComparison.OrdinalIgnoreCase)))
                    && (fireTick < 0 || qi.FireTick == fireTick);
                var matched = new List<object>();
                var hits = new List<QueuedIncident>();
                for (int i = 0; i < list.Count; i++)
                    if (match(list[i])) { hits.Add(list[i]); matched.Add(QueuedRow(list[i], i, now)); }
                if (hits.Count == 0)
                {
                    var queue = new List<object>();
                    for (int i = 0; i < list.Count; i++) queue.Add(QueuedRow(list[i], i, now));
                    return Fail("Nothing in the incident queue matches defName='" + defName + "' fireTick=" + fireTick + ". Nothing was removed.", new { queue });
                }
                int before = list.Count;
                if (!dryRun)
                {
                    foreach (var h in hits) list.Remove(h);
                }
                int after = list.Count;
                var remaining = new List<object>();
                for (int i = 0; i < list.Count; i++) remaining.Add(QueuedRow(list[i], i, now));
                if (!dryRun && before - after != hits.Count)
                    return Fail("Removal read-back mismatch: matched " + hits.Count + " but the queue shrank by " + (before - after) + ".",
                        new { matched, countBefore = before, countAfter = after, remaining });
                return new
                {
                    success = true,
                    dryRun,
                    matchedCount = hits.Count,
                    matched,
                    removedCount = before - after,
                    countBefore = before,
                    countAfter = after,
                    remaining,
                    ticksGame = now
                };
            }).ConfigureAwait(false);
        }
#endif

        // ================================================================
        //  G7  damage-event ring buffer
        // ================================================================

        [Tool(
            "jawa/damage_log",
            Description =
                "Read the companion's damage-event ring buffer: every Thing.TakeDamage (kind 'damage') " +
                "and every real Pawn.Kill (kind 'kill') since the recorder installed, with victim, " +
                "damage def, amount, dealt, instigator (id/def/faction), weapon def, hit part, hediffs " +
                "added, culprit hediff (kills), tick and cell. Answers 'what killed / hurt this pawn' " +
                "directly. 🔴 THE RECORDER INSTALLS ON THE FIRST TOOL CALL OF A SESSION: earlier events " +
                "are not there - read recorderInstalledUtc / oldestRetainedTick before trusting an " +
                "absence. Plant, filth and mote damage is not recorded (fires would evict everything " +
                "else). Capacity is fixed; `overwritten` > 0 means old events are gone and " +
                "`completeSinceSeq` says whether your window survived. action: read (default), status, " +
                "clear. Refuses if the patches did not install.",
            ResultDescription =
                "success, action, installed{damage, kill}, installErrors[], recorderInstalledUtc, capacity, " +
                "totalRecorded, overwritten, oldestRetainedSeq, oldestRetainedTick, completeSinceSeq, " +
                "recordErrors, lastRecordError, matchedCount, returned, truncated, nextSeq, events[] (seq, " +
                "tick, kind, victimId, victimDef, victimIsPawn, victimFaction, victimColonist, " +
                "victimDeadAfter, damageDef, amount, totalDealt, deflected, instigatorId, instigatorDef, " +
                "instigatorFaction, weapon, hitPart, culpritHediff, hediffsAdded, mapUniqueId, x, z), ticksGame.")]
        public static async Task<object> DamageLog(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'read' (default), 'status' (counters only) or 'clear'.")]
            string action = "read",
            [ToolParameter(Description = "Only events with seq > sinceSeq (pass the previous nextSeq - 1). -1 = all retained.")]
            int sinceSeq = -1,
            [ToolParameter(Description = "Only events at tick >= sinceTick. -1 = no tick filter.")]
            int sinceTick = -1,
            [ToolParameter(Description = "Only events whose victim OR instigator id equals this (bare or Thing_ prefixed).")]
            string thingId = null,
            [ToolParameter(Description = "Only events with a pawn victim. Default true.")]
            bool pawnsOnly = true,
            [ToolParameter(Description = "'damage', 'kill' or omit for both.")]
            string kind = null,
            [ToolParameter(Description = "Cap on returned events (1-4096), newest kept. Default 500.")]
            int limit = 500)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var act = (action ?? "read").Trim().ToLowerInvariant();
                if (act != "read" && act != "status" && act != "clear") return Fail("Unknown action '" + action + "'. Use read, status or clear.");
                if (limit < 1 || limit > 4096) return Fail("limit must be 1-4096, got " + limit + ".");
                var k = string.IsNullOrWhiteSpace(kind) ? null : kind.Trim().ToLowerInvariant();
                if (k != null && k != "damage" && k != "kill") return Fail("kind must be 'damage', 'kill' or omitted.");
                var R = typeof(JawaBenchEventRecorder);
                if (!JawaBenchEventRecorder.DamageInstalled && !JawaBenchEventRecorder.KillInstalled)
                    return Fail("The damage recorder is not installed, so this log would read empty while damage happens. Refusing.",
                        new { installErrors = JawaBenchEventRecorder.InstallErrors.ToList(), recorder = R.Name });

                var ring = JawaBenchEventRecorder.Damage;
                if (act == "clear")
                {
                    long dropped = ring.Total;
                    ring.Clear();
                    return new { success = true, action = act, clearedTotal = dropped, totalAfter = ring.Total, ticksGame = TicksGameSafe() };
                }

                var all = ring.Snapshot();
                long oldestSeq = all.Count > 0 ? all[0].seq : ring.Total;
                var id = string.IsNullOrWhiteSpace(thingId) ? null : thingId.Trim();
                if (id != null && id.StartsWith("Thing_", StringComparison.OrdinalIgnoreCase) && id.Length > 6) id = id.Substring(6);

                var hits = act == "status" ? new List<JawaDamageEvent>() : all.Where(e =>
                    e.seq > sinceSeq
                    && (sinceTick < 0 || e.tick >= sinceTick)
                    && (!pawnsOnly || e.victimIsPawn)
                    && (k == null || e.kind == k)
                    && (id == null || string.Equals(e.victimId, id, StringComparison.OrdinalIgnoreCase) || string.Equals(e.instigatorId, id, StringComparison.OrdinalIgnoreCase))).ToList();
                int trunc = Math.Max(0, hits.Count - limit);
                var ret = trunc > 0 ? hits.Skip(trunc).ToList() : hits;

                return new
                {
                    success = true,
                    action = act,
                    installed = new { damage = JawaBenchEventRecorder.DamageInstalled, kill = JawaBenchEventRecorder.KillInstalled },
                    installErrors = JawaBenchEventRecorder.InstallErrors.ToList(),
                    recorderInstalledUtc = JawaBenchEventRecorder.InstalledUtc.ToString("o"),
                    capacity = ring.Capacity,
                    totalRecorded = ring.Total,
                    overwritten = ring.Overwritten,
                    oldestRetainedSeq = oldestSeq,
                    oldestRetainedTick = all.Count > 0 ? all[0].tick : -1,
                    completeSinceSeq = sinceSeq + 1 >= oldestSeq,
                    recordErrors = JawaBenchEventRecorder.RecordErrors,
                    lastRecordError = JawaBenchEventRecorder.LastRecordError,
                    matchedCount = hits.Count,
                    returned = ret.Count,
                    truncated = trunc,
                    nextSeq = ring.Total,
                    events = ret.Select(DamageRow).ToList(),
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  G3 + G8  holder / stack lineage
        // ================================================================

        private static Thing FindThingAnywhere(string bare)
        {
            var buf = new List<Thing>();
            foreach (var m in Find.Maps ?? new List<Map>())
            {
                foreach (var t in m.listerThings.AllThings)
                    if (string.Equals(t.ThingID, bare, StringComparison.OrdinalIgnoreCase)) return t;
                ThingOwnerUtility.GetAllThingsRecursively(m, ThingRequest.ForGroup(ThingRequestGroup.Everything), buf, true, null, false);
                foreach (var t in buf)
                    if (t != null && string.Equals(t.ThingID, bare, StringComparison.OrdinalIgnoreCase)) return t;
            }
            if (Find.World != null)
            {
                ThingOwnerUtility.GetAllThingsRecursively(Find.World, buf, true, null);
                foreach (var t in buf)
                    if (t != null && string.Equals(t.ThingID, bare, StringComparison.OrdinalIgnoreCase)) return t;
            }
            return null;
        }

        [Tool(
            "jawa/thing_lineage",
            Description =
                "Where did this thing go? For each id: if it still exists anywhere (any map, spawned or " +
                "held in any container/pawn, or on the world e.g. in a caravan) - its def, stack, " +
                "spawned/destroyed, cell, map, the FULL holder chain (carriedBy / inventoryOf / " +
                "equippedBy / wornBy / thing / comp / map / world), forbidden, and rot stage/progress. " +
                "Whether or not it exists - the lineage journal's events naming it: 'absorb' (merged " +
                "into otherId), 'split' (otherId was split off it), 'detach' (whole stack left its " +
                "holder), 'ingest' (eaten by pawn otherId), 'destroy' (with DestroyMode). `fate` " +
                "summarises the last event of a thing that no longer exists; 'UNRECORDED' means the " +
                "journal has nothing - it installs on the first tool call of a session and only " +
                "journals ITEM-category things, so check recorderInstalledUtc / overwritten before " +
                "concluding anything. An item id vanishing is not quantity vanishing - follow absorb " +
                "and split to the surviving stack.",
            ResultDescription =
                "success, lineageInstalled, installErrors[], recorderInstalledUtc, journalTotal, journalOverwritten, " +
                "results[] (id, found, def, label, stackCount, spawned, destroyed, mapUniqueId, x, z, holderChain[], " +
                "carriedBy, forbidden, rotStage, rotProgress, fate, events[] (seq, tick, kind, thingId, def, otherId, " +
                "otherDef, count, stackAfter, holder, destroyMode, mapUniqueId, x, z)), ticksGame.")]
        public static async Task<object> ThingLineage(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated thing ids (bare or Thing_ prefixed), max 200. Required.")]
            string ids = null,
            [ToolParameter(Description = "Include the journal events naming each id. Default true.")]
            bool includeEvents = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                if (string.IsNullOrWhiteSpace(ids)) return Fail("Give ids: comma-separated thing ids.");
                var list = ids.Split(',').Select(s => s.Trim()).Where(s => s.Length > 0)
                              .Select(s => s.StartsWith("Thing_", StringComparison.OrdinalIgnoreCase) && s.Length > 6 ? s.Substring(6) : s)
                              .Distinct(StringComparer.OrdinalIgnoreCase).ToList();
                if (list.Count == 0) return Fail("ids held no usable id.");
                if (list.Count > 200) return Fail("At most 200 ids per call, got " + list.Count + ".");

                var journal = JawaBenchEventRecorder.Lineage.Snapshot();
                var results = new List<object>();
                foreach (var id in list)
                {
                    var t = FindThingAnywhere(id);
                    var evs = journal.Where(e => string.Equals(e.thingId, id, StringComparison.OrdinalIgnoreCase)
                                              || string.Equals(e.otherId, id, StringComparison.OrdinalIgnoreCase)).ToList();
                    string fate = null;
                    if (t == null)
                    {
                        var own = evs.Where(e => string.Equals(e.thingId, id, StringComparison.OrdinalIgnoreCase)).ToList();
                        if (own.Count == 0) fate = "UNRECORDED";
                        else
                        {
                            var absorb = own.LastOrDefault(e => e.kind == "absorb");
                            var ingest = own.LastOrDefault(e => e.kind == "ingest");
                            var destroy = own.LastOrDefault(e => e.kind == "destroy");
                            fate = absorb != null && destroy != null && destroy.seq > absorb.seq ? "absorbedInto:" + absorb.otherId
                                 : ingest != null && destroy != null && destroy.seq > ingest.seq ? "eatenBy:" + ingest.otherId
                                 : destroy != null ? "destroyed:" + destroy.destroyMode
                                 : "gone-after:" + own[own.Count - 1].kind;
                        }
                        results.Add(new { id, found = false, fate, events = includeEvents ? evs.Select(LineageRow).ToList() : null });
                        continue;
                    }

                    var chain = new List<string>();
                    string carriedBy = null;
                    IThingHolder h = t.ParentHolder;
                    for (int depth = 0; h != null && depth < 20; depth++)
                    {
                        chain.Add(JawaBenchEventRecorder.DescribeHolder(h));
                        var ct = h as Pawn_CarryTracker;
                        if (ct != null && carriedBy == null && ct.pawn != null) carriedBy = ct.pawn.ThingID;
                        h = h.ParentHolder;
                    }
                    var rot = (t as ThingWithComps) != null ? ((ThingWithComps)t).GetComp<CompRottable>() : null;
                    var pos = t.PositionHeld;
                    var m = t.MapHeld;
                    bool forbidden = false;
                    try { forbidden = t.Spawned && t.IsForbidden(Faction.OfPlayer); } catch { forbidden = false; }
                    results.Add(new
                    {
                        id,
                        found = true,
                        def = t.def != null ? t.def.defName : null,
                        label = t.LabelCap.ToString(),
                        stackCount = t.stackCount,
                        spawned = t.Spawned,
                        destroyed = t.Destroyed,
                        mapUniqueId = m != null ? m.uniqueID : -1,
                        x = pos.IsValid ? pos.x : -1,
                        z = pos.IsValid ? pos.z : -1,
                        holderChain = chain,
                        carriedBy,
                        forbidden,
                        rotStage = rot != null ? rot.Stage.ToString() : null,
                        rotProgress = rot != null ? (float?)rot.RotProgress : null,
                        fate,
                        events = includeEvents ? evs.Select(LineageRow).ToList() : null
                    });
                }
                return new
                {
                    success = true,
                    lineageInstalled = JawaBenchEventRecorder.LineageInstalled,
                    installErrors = JawaBenchEventRecorder.InstallErrors.ToList(),
                    recorderInstalledUtc = JawaBenchEventRecorder.InstalledUtc.ToString("o"),
                    journalTotal = JawaBenchEventRecorder.Lineage.Total,
                    journalOverwritten = JawaBenchEventRecorder.Lineage.Overwritten,
                    results,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
