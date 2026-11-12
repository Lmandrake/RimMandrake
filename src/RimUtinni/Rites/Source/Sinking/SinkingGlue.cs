// SUMP_SINKING_RITE_BUILD_1: the Verse side of the Sinking. Gathers facts, asks Kernel/SinkingKernel.cs, and applies what
// it decides. Soft dependencies (no About.xml dependency, reached by reflection, absent = that effect does nothing):
//   EnvironmentalHazards  RimMandrake.EnvironmentalHazards.RM_LotteryTableDef / RM_CompWorkedLottery / RM_CompBeastWakeRelay
//   RimProperty           RimMandrake.Property.GameComponent_PropertyLedger.ClearForeignClaimsWhere
//   EmpirePursuit         RuthlessPursuingMechanoids.ScenPart_RuthlessPursuingMechanoids (mapRaidTimers / mapWarningTimers)
//   BeskarArmorer         RimMandrake.Utinni.BeskarArmorer.RM_HeatEvents (read by the proof only; the rite never writes Heat)
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.Rites
{
    public static class SinkingGlue
    {
        public const string HoldOffDef = "RUT_ImperialHoldOff";
        public const string RaidLullDef = "RUT_TarLull_Raids";
        public const string BeastLullDef = "RM_TarLull_Beast";
        public const string BulgeDef = "RM_BeastBulge";

        public static SinkingConfig Config()
        {
            return new SinkingConfig
            {
                riteEnabled = RM_NinefoldSettings.sinkingEnabled,
                holdOffEnabled = RM_NinefoldSettings.sinkingHoldOffEnabled,
                raidLullEnabled = RM_NinefoldSettings.sinkingRaidLullEnabled,
                ownershipEraseEnabled = RM_NinefoldSettings.sinkingOwnershipEraseEnabled,
                beastLullEnabled = RM_NinefoldSettings.sinkingBeastLullEnabled,
                trapFizzleEnabled = RM_NinefoldSettings.sinkingTrapFizzleEnabled,
                valueFloor = RM_NinefoldSettings.sinkingValueFloor,
                holdOffMultiplier = RM_NinefoldSettings.sinkingHoldOffMultiplier,
                normalHoldOffDays = RM_NinefoldSettings.sinkingNormalHoldOffDays,
                raidLullDays = RM_NinefoldSettings.sinkingRaidLullDays,
                raidLullStrength = RM_NinefoldSettings.sinkingRaidLullStrength,
                beastLullDays = RM_NinefoldSettings.sinkingBeastLullDays,
                trapCount = RM_NinefoldSettings.sinkingTrapCount,
                ownershipExclusions = RM_NinefoldSettings.sinkingOwnershipExclusions,
            };
        }

        // ---------------------------------------------------------------- facts

        private static HashSet<string> lotteryFinds;

        /// <summary>Every thingDef named by a row of any RM_LotteryTableDef (EnvironmentalHazards), read once.</summary>
        public static bool IsLotteryFind(ThingDef def)
        {
            if (def == null) return false;
            if (lotteryFinds == null)
            {
                lotteryFinds = new HashSet<string>();
                Type tableT = AccessTools.TypeByName("RimMandrake.EnvironmentalHazards.RM_LotteryTableDef");
                FieldInfo strataF = tableT == null ? null : AccessTools.Field(tableT, "strata");
                if (strataF != null)
                {
                    foreach (Def table in GenDefDatabase.GetAllDefsInDatabaseForDef(tableT))
                        foreach (object stratum in (strataF.GetValue(table) as IEnumerable) ?? new object[0])
                        {
                            if (stratum == null) continue;
                            FieldInfo rowsF = AccessTools.Field(stratum.GetType(), "rows");
                            foreach (object row in (rowsF?.GetValue(stratum) as IEnumerable) ?? new object[0])
                            {
                                if (row == null) continue;
                                if (AccessTools.Field(row.GetType(), "thingDef")?.GetValue(row) is ThingDef td)
                                    lotteryFinds.Add(td.defName);
                            }
                        }
                }
            }
            return lotteryFinds.Contains(def.defName);
        }

        public static SinkingOfferingFacts Facts(Thing t)
        {
            return new SinkingOfferingFacts
            {
                defName = t?.def?.defName,
                isPawn = t is Pawn,
                isCorpse = t is Corpse,
                inLotteryTable = t != null && IsLotteryFind(t.def),
                marketValue = t == null ? 0f : t.MarketValue * t.stackCount,
            };
        }

        public static SinkingPlan PlanFor(Thing t)
        {
            return SinkingKernel.Plan(Facts(t), Config(), OfferingUtility.ValueAtSmall, OfferingUtility.ValueAtLarge,
                                      EventMagnitude.Small, EventMagnitude.Large);
        }

        // ---------------------------------------------------------------- conditions

        public static GameCondition Condition(Map map, string defName)
        {
            GameConditionDef def = DefDatabase<GameConditionDef>.GetNamedSilentFail(defName);
            return def == null || map?.gameConditionManager == null ? null : map.gameConditionManager.GetActiveCondition(def);
        }

        public static bool Active(Map map, string defName) { return Condition(map, defName) != null; }

        public static int TicksLeft(Map map, string defName)
        {
            GameCondition c = Condition(map, defName);
            return c == null ? -1 : (c.Permanent ? int.MaxValue : c.TicksLeft);
        }

        /// <summary>Starts the condition for <paramref name="ticks"/>, or resets a running one to that many ticks left.</summary>
        public static void StartCondition(Map map, string defName, int ticks)
        {
            GameConditionDef def = DefDatabase<GameConditionDef>.GetNamedSilentFail(defName);
            if (def == null || map?.gameConditionManager == null || ticks <= 0) return;
            GameCondition existing = map.gameConditionManager.GetActiveCondition(def);
            if (existing != null) { existing.Duration = existing.TicksPassed + ticks; return; }
            map.gameConditionManager.RegisterCondition(GameConditionMaker.MakeCondition(def, ticks));
        }

        // ---------------------------------------------------------------- the Empire

        public static bool IsImperial(Faction f)
        {
            if (f == null) return false;
            if (f.def != null && f.def.defName == "Empire") return true;
            Faction pursuit = PursuitFaction();
            return pursuit != null && pursuit == f;
        }

        private static object PursuitPart()
        {
            Type partT = AccessTools.TypeByName("RuthlessPursuingMechanoids.ScenPart_RuthlessPursuingMechanoids");
            if (partT == null || Find.Scenario == null) return null;
            return Find.Scenario.AllParts.FirstOrDefault(p => p != null && partT.IsInstanceOfType(p));
        }

        private static Faction PursuitFaction()
        {
            object part = PursuitPart();
            return part == null ? null : AccessTools.Field(part.GetType(), "PursuitFaction")?.GetValue(part) as Faction;
        }

        /// <summary>The EmpirePursuit ladder's next raid and warning ticks on <paramref name="map"/> (absolute), or -1.</summary>
        public static bool ReadImperialTimers(Map map, out int raid, out int warning)
        {
            raid = warning = -1;
            object part = PursuitPart();
            if (part == null || map == null) return false;
            var raids = AccessTools.Field(part.GetType(), "mapRaidTimers")?.GetValue(part) as Dictionary<Map, int>;
            var warns = AccessTools.Field(part.GetType(), "mapWarningTimers")?.GetValue(part) as Dictionary<Map, int>;
            if (raids == null || !raids.TryGetValue(map, out raid)) { raid = -1; return false; }
            if (warns == null || !warns.TryGetValue(map, out warning)) warning = -1;
            return true;
        }

        /// <summary>Moves the next scheduled Imperial raid (and its warning) on the map out by the multiplier. Returns a
        /// line for the letter/probe, or null when no Imperial incident is scheduled.</summary>
        public static string MoveImperialTimers(Map map, float multiplier)
        {
            object part = PursuitPart();
            if (part == null || map == null) return null;
            var raids = AccessTools.Field(part.GetType(), "mapRaidTimers")?.GetValue(part) as Dictionary<Map, int>;
            var warns = AccessTools.Field(part.GetType(), "mapWarningTimers")?.GetValue(part) as Dictionary<Map, int>;
            if (raids == null || !raids.TryGetValue(map, out int raid)) return null;
            int now = Find.TickManager.TicksGame;
            int moved = SinkingKernel.MoveOut(now, raid, multiplier);
            raids[map] = moved;
            if (warns != null && warns.TryGetValue(map, out int warn))
                warns[map] = SinkingKernel.MoveOutWarning(now, warn, moved, multiplier);
            return "imperial raid tick " + raid + " -> " + moved;
        }

        // ---------------------------------------------------------------- the beasts

        public static bool WakeAllowed(Map map, SinkingWakeCause cause)
        {
            return SinkingKernel.WakeAllowed(cause, Active(map, BeastLullDef), RM_NinefoldSettings.sinkingBeastLullEnabled);
        }

        // ---------------------------------------------------------------- ownership

        public static string CategoryOf(Thing t)
        {
            if (t is Pawn p)
            {
                if (p.RaceProps == null) return "Item";
                if (p.RaceProps.Humanlike) return "Humanlike";
                if (p.RaceProps.IsMechanoid) return "Mech";
                return "Animal";
            }
            if (t is Building) return "Building";
            return "Item";
        }

        public static bool ColonyOwned(Thing t)
        {
            if (t is Pawn || t is Building) return t.Faction == Faction.OfPlayer;
            // an item carried, worn or wielded is its carrier's; a loose item on the colony's map is the colony's
            Pawn carrier = (t.ParentHolder as Pawn_InventoryTracker)?.pawn ?? (t.ParentHolder as Pawn_EquipmentTracker)?.pawn
                           ?? (t.ParentHolder as Pawn_ApparelTracker)?.pawn ?? (t.ParentHolder as Pawn_CarryTracker)?.pawn;
            if (carrier != null) return carrier.Faction == Faction.OfPlayer;
            return t.Spawned || (t.ParentHolder is Thing box && box.Faction == Faction.OfPlayer);
        }

        /// <summary>Wipes every foreign claim on the colony's things on <paramref name="map"/> through the RimProperty API.
        /// Returns one line per wiped claim (thing label and whose claim), or null when RimProperty is not loaded.</summary>
        public static List<string> EraseOwnership(Map map)
        {
            Type ledgerT = AccessTools.TypeByName("RimMandrake.Property.GameComponent_PropertyLedger");
            Type refT = AccessTools.TypeByName("RimMandrake.Property.ClaimantRef");
            if (ledgerT == null || refT == null || map == null) return null;
            object ledger = AccessTools.Method(ledgerT, "Get")?.Invoke(null, null);
            MethodInfo clear = AccessTools.Method(ledgerT, "ClearForeignClaimsWhere");
            object keep = AccessTools.Method(refT, "OfCommons")?.Invoke(null, new object[] { Faction.OfPlayer });
            if (ledger == null || clear == null || keep == null) return null;
            HashSet<string> excl = SinkingKernel.ParseExclusions(RM_NinefoldSettings.sinkingOwnershipExclusions);
            Func<Thing, bool> filter = t => t != null && !t.Destroyed
                && SinkingKernel.EraseCandidate(CategoryOf(t), ColonyOwned(t), t.MapHeld == map, excl);
            var lines = new List<string>();
            foreach (object w in (clear.Invoke(ledger, new object[] { filter, keep }) as IEnumerable) ?? new object[0])
            {
                Thing thing = AccessTools.Field(w.GetType(), "Thing")?.GetValue(w) as Thing;
                object claimant = AccessTools.Field(w.GetType(), "Claimant")?.GetValue(w);
                object basis = AccessTools.Field(w.GetType(), "Basis")?.GetValue(w);
                lines.Add((thing?.LabelCap ?? "something") + ": " + claimant + "'s claim (" + basis + ") wiped");
            }
            return lines;
        }

        // ---------------------------------------------------------------- the rite itself

        /// <summary>Ishko deltas the last Sinking applied, as "God>reason>amount" (the proof read).</summary>
        public static readonly List<string> LastDeltas = new List<string>();
        public static string LastLetterText;
        public static string LastSummary;

        /// <summary>Everything a Sinking does to <paramref name="offering"/> on <paramref name="map"/>, applied in one place
        /// for the outcome worker and the proof. Refusals change nothing and return the reason.</summary>
        public static SinkingPlan Apply(Map map, Thing offering, out string text, ref LookTargets look)
        {
            var sb = new StringBuilder();
            SinkingPlan plan = PlanFor(offering);
            if (!plan.accepted || map == null || offering == null || offering.Destroyed)
            {
                text = plan.reason;
                LastSummary = "REFUSED " + plan.kind + ": " + plan.reason;
                return plan;
            }
            IntVec3 at = offering.PositionHeld;
            string label = offering.LabelCap;

            // the sign: a slow bubble as the offering sinks, then it is gone
            Vector3 v = at.ToVector3Shifted();
            for (int i = 0; i < 4; i++) FleckMaker.ThrowSmoke(v + new Vector3(Rand.Range(-0.3f, 0.3f), 0f, Rand.Range(-0.3f, 0.3f)), map, 0.6f + 0.2f * i);
            FleckMaker.ThrowAirPuffUp(v, map);
            if (offering.Spawned) offering.DeSpawn();
            offering.Destroy(DestroyMode.Vanish);
            sb.Append(label).Append(" sank into the tar. A slow bubble rose where it went down, and broke.");

            // Ishko, tagged "The Sinking"
            LastDeltas.Clear();
            var prior = GameComponent_Ninefold.DeltaWatcher;
            GameComponent_Ninefold.DeltaWatcher = (g, amt, why) =>
            {
                prior?.Invoke(g, amt, why);
                if (why == SinkingKernel.DeltaTag) LastDeltas.Add(g + ">" + why + ">" + amt.ToString("0.###"));
            };
            try { GameComponent_Ninefold.Instance?.ApplyDelta(God.Ishko, plan.ishkoDelta, SinkingKernel.DeltaTag); }
            finally { GameComponent_Ninefold.DeltaWatcher = prior; }

            if (plan.holdOff)
            {
                StartCondition(map, HoldOffDef, plan.holdOffTicks);
                string moved = MoveImperialTimers(map, plan.holdOffMultiplier);
                sb.Append("\n\nThe Empire's eye slides off this ground for a while (").Append((plan.holdOffTicks / 60000f).ToString("0.#"))
                  .Append(" days). Their next probe comes later than it would have.");
                if (moved != null) Log.Message("[Sinking] " + moved);
            }
            if (plan.raidLull)
            {
                StartCondition(map, RaidLullDef, plan.raidLullTicks);
                sb.Append("\n\nThe smell of the tar hangs over the colony. Raiders think twice (").Append((plan.raidLullTicks / 60000f).ToString("0.#")).Append(" days).");
            }
            if (plan.rider == SinkingRider.BeastLull)
            {
                StartCondition(map, BeastLullDef, plan.beastLullTicks);
                sb.Append("\n\nPitch given back to the pitch. The bulges lie still (").Append((plan.beastLullTicks / 60000f).ToString("0.#")).Append(" days): building, digging and pumping will not wake what sleeps in them. An explosion still will.");
            }
            if (plan.rider == SinkingRider.TrapFizzle)
            {
                MapComponent_SinkingTraps.For(map)?.Set(plan.trapCount);
                sb.Append("\n\nThe depth has its find back. The next ").Append(plan.trapCount).Append(" traps in the dig will fizzle.");
            }
            if (plan.ownershipErase)
            {
                List<string> wiped = EraseOwnership(map);
                if (wiped != null && wiped.Count > 0)
                {
                    sb.Append("\n\nThe tar keeps no ledger. Whatever was taken is now simply ours:");
                    foreach (string w in wiped) sb.Append("\n  - ").Append(w);
                }
                else if (wiped != null)
                {
                    sb.Append("\n\nNo foreign claim stood on the colony's things.");
                }
            }
            text = sb.ToString();
            LastLetterText = text;
            LastSummary = plan.Signature();
            look = new LookTargets(new TargetInfo(at, map));
            return plan;
        }
    }
}
