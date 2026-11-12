// SUMP_SINKING_RITE_BUILD_1: proof reads for validation.py (jawa/static_call) and a dev action to grant the rite (§1, the
// inscription, is out of scope: until it lands, the precept is added to the player's primary ideo here). Every method
// returns one line starting PASS / FAIL / INFO; none of them is reached in normal play.
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text;
using HarmonyLib;
using LudeonTK;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.Rites
{
    public static class SinkingProbe
    {
        public const string PreceptDefName = "RUT_Ritual_Sinking";

        [DebugAction("RimMandrake", "Grant the Sinking (Ishko) to the player ideo", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        public static void GrantRiteAction() { Messages.Message(GrantRite(), MessageTypeDefOf.NeutralEvent, false); }

        public static string GrantRite()
        {
            PreceptDef pd = DefDatabase<PreceptDef>.GetNamedSilentFail(PreceptDefName);
            Ideo ideo = Faction.OfPlayer?.ideos?.PrimaryIdeo;
            if (pd == null) return "FAIL no PreceptDef " + PreceptDefName + " (Ideology not active?)";
            if (ideo == null) return "FAIL the player faction has no primary ideo";
            if (ideo.PreceptsListForReading.Any(p => p.def == pd)) return "PASS already granted to " + ideo.name;
            ideo.AddPrecept(PreceptMaker.MakePrecept(pd), true, null, pd.ritualPatternBase);
            return ideo.PreceptsListForReading.Any(p => p.def == pd) ? "PASS granted to " + ideo.name : "FAIL AddPrecept did not stick";
        }

        /// <summary>Runs the full Sinking on <paramref name="offering"/> exactly as the outcome worker does.</summary>
        public static string Sink(Map map, Thing offering)
        {
            if (offering == null) return "FAIL no offering";
            string id = offering.ThingID;
            LookTargets look = null;
            SinkingPlan plan = SinkingGlue.Apply(map, offering, out string text, ref look);
            if (!plan.accepted) return "INFO refused " + plan.kind + ": " + plan.reason;
            return (offering.Destroyed ? "PASS " : "FAIL ") + id + " destroyed=" + offering.Destroyed + " plan=" + plan.Signature();
        }

        public static string Refusal(Thing t)
        {
            string why = RUT_RitualObligationTargetWorker_SinkingOffering.RefusalReason(t);
            return why == null ? "INFO accepted " + t?.ThingID : "PASS refused " + t?.ThingID + ": " + why;
        }

        public static string Conditions(Map map)
        {
            var sb = new StringBuilder("INFO");
            foreach (string d in new[] { SinkingGlue.HoldOffDef, SinkingGlue.RaidLullDef, SinkingGlue.BeastLullDef })
            {
                int left = SinkingGlue.TicksLeft(map, d);
                sb.Append(' ').Append(d).Append('=').Append(left < 0 ? "none" : (left / 60000f).ToString("0.##") + "d");
            }
            return sb.ToString();
        }

        public static string ProbeWake(Map map, string cause)
        {
            if (!Enum.TryParse(cause, true, out SinkingWakeCause c)) return "FAIL unknown cause " + cause;
            return "INFO wake " + c + " allowed=" + SinkingGlue.WakeAllowed(map, c) + " lull=" + SinkingGlue.Active(map, SinkingGlue.BeastLullDef);
        }

        /// <summary>A small explosion on the first RM_BeastBulge: the lull must not stop damage from waking it.</summary>
        public static string ExplodeAtBulge(Map map)
        {
            Thing bulge = map?.listerThings.AllThings.FirstOrDefault(t => t.def.defName == SinkingGlue.BulgeDef);
            if (bulge == null) return "FAIL no " + SinkingGlue.BulgeDef + " on the map";
            CompCanBeDormant d = bulge.TryGetComp<CompCanBeDormant>();
            bool before = d?.Awake ?? false;
            GenExplosion.DoExplosion(bulge.Position, map, 1.9f, DamageDefOf.Bomb, null, damAmount: 5);
            bool after = d?.Awake ?? bulge.Destroyed;
            return (after ? "PASS" : "FAIL") + " bulge awake " + before + " -> " + after + " lull=" + SinkingGlue.Active(map, SinkingGlue.BeastLullDef);
        }

        public static string TrapCounter(Map map)
        {
            return "INFO traps=" + (MapComponent_SinkingTraps.For(map)?.Remaining ?? -1) + " fizzled=" + Patch_Sinking_TrapFizzle.Fizzled;
        }

        /// <summary>One trap roll on every RM_CompWorkedLottery on the map (through the patched ArmTrap), then their armed flags.</summary>
        public static string ForceTrapRoll(Map map)
        {
            Type lotT = AccessTools.TypeByName("RimMandrake.EnvironmentalHazards.RM_CompWorkedLottery");
            MethodInfo arm = lotT == null ? null : AccessTools.Method(lotT, "ArmTrap");
            PropertyInfo armed = lotT == null ? null : AccessTools.Property(lotT, "TrapArmed");
            if (arm == null || armed == null || map == null) return "FAIL RM_CompWorkedLottery not loaded";
            var comps = new List<ThingComp>();
            foreach (Thing t in map.listerThings.AllThings)
                if (t is ThingWithComps tw) comps.AddRange(tw.AllComps.Where(c => lotT.IsInstanceOfType(c)));
            if (comps.Count == 0) return "FAIL no dig shaft (RM_CompWorkedLottery) on the map";
            foreach (ThingComp c in comps) arm.Invoke(c, null);
            int armedN = comps.Count(c => (bool)armed.GetValue(c));
            return "INFO shafts=" + comps.Count + " armed=" + armedN + " traps=" + (MapComponent_SinkingTraps.For(map)?.Remaining ?? -1);
        }

        /// <summary>Disarms every armed lottery trap (skill gate 0) so a test leaves no fuse burning.</summary>
        public static string ClearTraps(Map map)
        {
            Type lotT = AccessTools.TypeByName("RimMandrake.EnvironmentalHazards.RM_CompWorkedLottery");
            FieldInfo fuse = lotT == null ? null : AccessTools.Field(lotT, "trapFuseTicksRemaining");
            if (fuse == null || map == null) return "FAIL RM_CompWorkedLottery not loaded";
            int n = 0;
            foreach (Thing t in map.listerThings.AllThings)
                if (t is ThingWithComps tw)
                    foreach (ThingComp c in tw.AllComps.Where(c => lotT.IsInstanceOfType(c)))
                        if ((int)fuse.GetValue(c) >= 0) { fuse.SetValue(c, -1); n++; }
            return "INFO cleared " + n;
        }

        public static string ImperialTimers(Map map)
        {
            if (!SinkingGlue.ReadImperialTimers(map, out int raid, out int warn)) return "INFO no EmpirePursuit timer on this map";
            return "INFO now=" + Find.TickManager.TicksGame + " raid=" + raid + " warning=" + warn;
        }

        /// <summary>Sum and count of BeskarArmorer Heat events (read only; the Sinking must leave it unchanged).</summary>
        public static string HeatSum()
        {
            Type heatT = AccessTools.TypeByName("RimMandrake.Utinni.BeskarArmorer.RM_HeatEvents");
            if (heatT == null || Current.Game == null) return "INFO BeskarArmorer not loaded";
            GameComponent comp = Current.Game.components.FirstOrDefault(c => heatT.IsInstanceOfType(c));
            IList events = comp == null ? null : AccessTools.Field(heatT, "events")?.GetValue(comp) as IList;
            if (events == null) return "INFO no heat ledger";
            int sum = 0;
            foreach (object e in events) sum += (int)(AccessTools.Field(e.GetType(), "amount")?.GetValue(e) ?? 0);
            return "INFO heatEvents=" + events.Count + " sum=" + sum;
        }

        /// <summary>A seeded non-Imperial raid roll: the chance multiplier the storyteller gate uses, and whether it fires.</summary>
        public static string RaidRoll(Map map, int seed)
        {
            float mult = SinkingKernel.RaidChanceMultiplier(SinkingGlue.Config(), SinkingGlue.Active(map, SinkingGlue.RaidLullDef));
            Rand.PushState(seed);
            float roll;
            try { roll = Rand.Value; } finally { Rand.PopState(); }
            return "INFO seed=" + seed + " roll=" + roll.ToString("0.####") + " mult=" + mult.ToString("0.###")
                   + " fires=" + SinkingKernel.RaidRollFires(roll, mult) + " refused=" + Patch_Sinking_TryFire.LullRefused;
        }

        public static string IshkoDeltas()
        {
            return "INFO count=" + SinkingGlue.LastDeltas.Count + (SinkingGlue.LastDeltas.Count > 0 ? " " + string.Join(";", SinkingGlue.LastDeltas) : "");
        }

        /// <summary>Puts a Stolen claim by a foreign faction (and the colony's own commons claim) on <paramref name="t"/>.</summary>
        public static string SeedForeignClaim(Thing t)
        {
            Type ledgerT = AccessTools.TypeByName("RimMandrake.Property.GameComponent_PropertyLedger");
            Type refT = AccessTools.TypeByName("RimMandrake.Property.ClaimantRef");
            Type recT = AccessTools.TypeByName("RimMandrake.Property.ClaimRecord");
            Type basisT = AccessTools.TypeByName("RimMandrake.Property.ClaimBasis");
            if (ledgerT == null || refT == null || recT == null || basisT == null || t == null) return "FAIL RimProperty not loaded";
            object ledger = AccessTools.Method(ledgerT, "Get").Invoke(null, null);
            Faction foreign = Find.FactionManager.AllFactions.FirstOrDefault(f => !f.IsPlayer && !f.Hidden && !f.temporary);
            if (ledger == null || foreign == null) return "FAIL no ledger or no foreign faction";
            MethodInfo commons = AccessTools.Method(refT, "OfCommons");
            MethodInfo record = AccessTools.Method(ledgerT, "RecordClaim");
            int now = Find.TickManager.TicksGame;
            object stolen = Enum.Parse(basisT, "Stolen");
            object colonyBasis = Enum.Parse(basisT, "Purchased");
            record.Invoke(ledger, new object[] { t, Activator.CreateInstance(recT, commons.Invoke(null, new object[] { foreign }), 1f, stolen, now) });
            record.Invoke(ledger, new object[] { t, Activator.CreateInstance(recT, commons.Invoke(null, new object[] { Faction.OfPlayer }), 1f, colonyBasis, now) });
            return "INFO seeded " + t.ThingID + " foreign=" + foreign.Name + " " + ClaimsOf(t);
        }

        public static string ClaimsOf(Thing t)
        {
            Type ledgerT = AccessTools.TypeByName("RimMandrake.Property.GameComponent_PropertyLedger");
            if (ledgerT == null || t == null) return "FAIL RimProperty not loaded";
            object ledger = AccessTools.Method(ledgerT, "Get").Invoke(null, null);
            var args = new object[] { t, null };
            if (ledger == null || !(bool)AccessTools.Method(ledgerT, "TryGetRecords").Invoke(ledger, args)) return "claims=0";
            var parts = new List<string>();
            foreach (object r in (IEnumerable)args[1])
                parts.Add(AccessTools.Property(r.GetType(), "Claimant")?.GetValue(r) + "/" + AccessTools.Field(r.GetType(), "Basis")?.GetValue(r));
            return "claims=" + parts.Count + " [" + string.Join("; ", parts) + "]";
        }

        /// <summary>Spawns <paramref name="count"/> of <paramref name="defName"/> near the map centre; "INFO id=... value=...".</summary>
        public static string SpawnOffering(Map map, string defName, int count)
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (map == null || def == null) return "FAIL no map or no ThingDef " + defName;
            Thing t = ThingMaker.MakeThing(def, def.MadeFromStuff ? GenStuff.DefaultStuffFor(def) : null);
            t.stackCount = Math.Max(1, Math.Min(count, def.stackLimit));
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 12, c => c.Standable(map) && c.GetFirstItem(map) == null, out IntVec3 at))
                return "FAIL no free cell";
            GenSpawn.Spawn(t, at, map);
            // The offering must lie at the tar's edge (kernel RefusedAwayFromTar): when none is in reach, pour a cell of
            // the mere's shallow tar beside it so the chain tests the rite, not the map.
            string tar = "found";
            if (!SinkingGlue.NearTar(t))
            {
                TerrainDef shallow = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_TarShallow");
                if (shallow == null) return "FAIL no tar in reach and no TerrainDef RM_TarShallow id=" + t.ThingID;
                IntVec3 pour = IntVec3.Invalid;
                foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(t))
                    if (c.InBounds(map) && c.GetEdifice(map) == null && c.GetFirstItem(map) == null) { pour = c; break; }
                if (!pour.IsValid) return "FAIL no cell beside the offering to pour tar id=" + t.ThingID;
                map.terrainGrid.SetTerrain(pour, shallow);
                tar = "spawned@" + pour.x + "," + pour.z;
                if (!SinkingGlue.NearTar(t)) return "FAIL poured tar but NearTar still false id=" + t.ThingID;
            }
            return "INFO id=" + t.ThingID + " value=" + (t.MarketValue * t.stackCount).ToString("0") + " tar=" + tar;
        }

        /// <summary>Spawns the offering on a cell with no tar terrain or tar building within the radius, for the refusal
        /// leg of the chain; "INFO id=... value=... tar=none".</summary>
        public static string SpawnOfferingAwayFromTar(Map map, string defName, int count)
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (map == null || def == null) return "FAIL no map or no ThingDef " + defName;
            Thing t = ThingMaker.MakeThing(def, def.MadeFromStuff ? GenStuff.DefaultStuffFor(def) : null);
            t.stackCount = Math.Max(1, Math.Min(count, def.stackLimit));
            int r = SinkingKernel.TarRadius(SinkingGlue.Config());
            bool clear(IntVec3 c)
            {
                if (!c.Standable(map) || c.GetFirstItem(map) != null) return false;
                foreach (IntVec3 n in GenRadial.RadialCellsAround(c, r + 1, true))
                {
                    if (!n.InBounds(map)) continue;
                    if (SinkingKernel.IsTarTerrain(map.terrainGrid.TerrainAt(n)?.defName)) return false;
                    foreach (Thing h in map.thingGrid.ThingsListAtFast(n)) if (SinkingKernel.IsTarBuilding(h?.def?.defName)) return false;
                }
                return true;
            }
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 40, clear, out IntVec3 at)) return "FAIL no cell away from tar";
            GenSpawn.Spawn(t, at, map);
            if (SinkingGlue.NearTar(t)) { t.Destroy(DestroyMode.Vanish); return "FAIL spawned away from tar but NearTar true"; }
            return "INFO id=" + t.ThingID + " value=" + (t.MarketValue * t.stackCount).ToString("0") + " tar=none";
        }

        /// <summary>Makes a throwaway pawn ("pawn") or its corpse ("corpse"), asks the filter, and removes it again.</summary>
        public static string RefuseKind(Map map, string kind)
        {
            if (map == null) return "FAIL no map";
            Pawn p = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 12, c => c.Standable(map), out IntVec3 at)) return "FAIL no free cell";
            GenSpawn.Spawn(p, at, map);
            Thing target = p;
            if (kind == "corpse") { p.Kill(null); target = p.Corpse; }
            string why = target == null ? null : RUT_RitualObligationTargetWorker_SinkingOffering.RefusalReason(target);
            string res = (why != null ? "PASS refused " : "FAIL accepted ") + kind + (why != null ? ": " + why : "");
            if (target != null && !target.Destroyed) target.Destroy(DestroyMode.Vanish);
            if (!p.Destroyed && !p.Discarded) p.Destroy(DestroyMode.Vanish);
            return res;
        }

        public static string FirstColonist(Map map)
        {
            Pawn p = map?.mapPawns.FreeColonistsSpawned.FirstOrDefault();
            return p == null ? "FAIL no free colonist" : "INFO id=" + p.ThingID;
        }

        /// <summary>Hediffs across every free colonist on the map (the Sinking must add none).</summary>
        public static string HediffTotal(Map map)
        {
            if (map == null) return "FAIL no map";
            int n = 0;
            foreach (Pawn p in map.mapPawns.FreeColonistsSpawned) n += p.health?.hediffSet?.hediffs.Count ?? 0;
            return "INFO hediffs=" + n;
        }

        /// <summary>Ends the Sinking's three conditions and empties the trap counter, so each live case starts clean.</summary>
        public static string Reset(Map map)
        {
            if (map?.gameConditionManager == null) return "FAIL no map";
            int ended = 0;
            foreach (string d in new[] { SinkingGlue.HoldOffDef, SinkingGlue.RaidLullDef, SinkingGlue.BeastLullDef })
            {
                GameCondition c = SinkingGlue.Condition(map, d);
                if (c != null) { c.End(); ended++; }
            }
            MapComponent_SinkingTraps.For(map)?.Set(0);
            SinkingGlue.LastDeltas.Clear();
            SinkingGlue.LastLetterText = null;
            return "INFO reset ended=" + ended;
        }

        public static string LastLetter() => "INFO " + (SinkingGlue.LastLetterText ?? "(none)").Replace("\n", " | ");

        public static string HediffCount(Pawn p)
        {
            return p?.health?.hediffSet == null ? "FAIL no pawn" : "INFO " + p.ThingID + " hediffs=" + p.health.hediffSet.hediffs.Count;
        }
    }
}
