using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.LanternDeeps
{
    // ════════════════════════════════════════════════════════════════════
    // LANTERNDEEPS_HYDROCARBON_WAVE1_BUILD_1 (split from LANTERNDEEPS_HYDROCARBON_FAUNA_BUILD_1; the
    // XML-only wave the parent names: drifter, candler, galuush, chiller, shoal). Concepts:
    // design/Jawa/worldbuilding/biomes/rosters/lantern_deeps_repopulation_proposals.md §2, §3, §9,
    // §10, §12, ruled in by the owner ("Yes all 7 and ensure hydrocarbon"). Three small seams the
    // proposals' "XML only" lines turned out to need, each measured against decompiled 1.6:
    //
    //  1. RM_DeathActionWorker_HotKill: a methane body that ignites only when killed hot. Vanilla
    //     CompExplosive.explodeOnKilled fires from PostDestroy(KillFinalize), which a dying PAWN
    //     never reaches (it becomes a corpse, it is not destroyed), and requiredDamageTypeToExplode
    //     names ONE damage type. So: a death action (the boomalope's own hook) that reads the
    //     killing wound — the newest injury — and detonates unless it was a cold, edged/blunt one.
    //     "Killed by a blade it collapses into a harmless sac; killed by fire, a spark, a hot
    //     bullet... it detonates."
    //  2. RM_CompMobileGlow: vanilla CompGlower registers at a fixed cell; a drifting glower must
    //     re-register as it moves (CompTick, since a pawn never runs CompTickRare).
    //  3. RM_CompHeatPusherGated: the chiller's cold is vanilla CompHeatPusher (CompTick pushes
    //     every 60 ticks, which a pawn does run), behind its Mod Settings switch.
    //  Plus RM_GenStep_Galuush: one galuush per Deep at most, by chance, hung in the biggest
    //  open chamber, never from the wildAnimals roster ("one per Deep at most, and many Deeps
    //  have none").
    // ════════════════════════════════════════════════════════════════════

    public class RM_DeathActionProperties_HotKill : DeathActionProperties
    {
        public float radius = 2.9f;
        public DamageDef damageDef;
        public float chanceToStartFire = 0.5f;
        // Injuries that count as a COLD kill: no ignition.
        public List<HediffDef> coldInjuries = new List<HediffDef>();
        public string ignitionMessageKey = "RM_HotKillIgnition";
        // LANTERNDEEPS_AURORA_COLLAPSE_BUILD_1: the galuush brings its chamber's roof down (through the Deep's
        // collapse warnings when those are on). 0 = no roof fall.
        public float collapseRoofRadius = 0f;

        public RM_DeathActionProperties_HotKill()
        {
            workerClass = typeof(RM_DeathActionWorker_HotKill);
        }
    }

    public class RM_DeathActionWorker_HotKill : DeathActionWorker
    {
        private RM_DeathActionProperties_HotKill Props => (RM_DeathActionProperties_HotKill)props;

        public override bool DangerousInMelee => false; // a blade kill is the safe one

        public override void PawnDied(Corpse corpse, Lord prevLord)
        {
            if (!LanternDeepsSettings.hydrocarbonIgnitionEnabled || corpse == null || corpse.MapHeld == null)
            {
                return;
            }
            Pawn pawn = corpse.InnerPawn;
            if (!KilledHot(pawn, Props.coldInjuries))
            {
                return;
            }
            Messages.Message(Props.ignitionMessageKey.Translate(pawn.LabelShort), new TargetInfo(corpse.PositionHeld, corpse.MapHeld),
                MessageTypeDefOf.NegativeEvent);
            GenExplosion.DoExplosion(corpse.PositionHeld, corpse.MapHeld, Props.radius, Props.damageDef ?? DamageDefOf.Flame, pawn,
                chanceToStartFire: Props.chanceToStartFire);
            if (Props.collapseRoofRadius > 0f && LanternDeepsSettings.galuushRoofFallEnabled)
            {
                Map map = corpse.MapHeld;
                foreach (IntVec3 c in GenRadial.RadialCellsAround(corpse.PositionHeld, Props.collapseRoofRadius, true))
                {
                    if (c.InBounds(map) && c.Roofed(map) && c.GetRoof(map).canCollapse)
                    {
                        map.GetComponent<RM_MapComponent_DeepCollapse>()?.MarkForced(c);
                        map.roofCollapseBuffer.MarkToCollapse(c);
                    }
                }
            }
        }

        // The killing wound is the newest injury. No injury at all (starvation, cold) = no ignition.
        public static bool KilledHot(Pawn pawn, List<HediffDef> coldInjuries)
        {
            Hediff_Injury last = pawn?.health?.hediffSet?.hediffs?.OfType<Hediff_Injury>()
                .OrderByDescending(h => h.tickAdded).FirstOrDefault();
            return last != null && (coldInjuries == null || !coldInjuries.Contains(last.def));
        }
    }

    public class RM_CompProperties_MobileGlow : CompProperties
    {
        public int interval = 30;

        public RM_CompProperties_MobileGlow()
        {
            compClass = typeof(RM_CompMobileGlow);
        }
    }

    public class RM_CompMobileGlow : ThingComp
    {
        private IntVec3 last = IntVec3.Invalid;

        public override void CompTick()
        {
            if (!parent.Spawned || !parent.IsHashIntervalTick(((RM_CompProperties_MobileGlow)props).interval))
            {
                return;
            }
            if (parent.Position == last)
            {
                return;
            }
            last = parent.Position;
            parent.TryGetComp<CompGlower>()?.ForceRegister(parent.Map);
        }
    }

    public class RM_CompHeatPusherGated : CompHeatPusher
    {
        public override bool ShouldPushHeatNow => LanternDeepsSettings.chillerColdEnabled && base.ShouldPushHeatNow;
    }

    public class RM_GenStep_Galuush : GenStep
    {
        public PawnKindDef kind;
        public float chance = 0.5f;
        public float minOpenRadius = 4.9f;

        public override int SeedPart => 340917771;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (LanternDeepsSettings.galuushEnabled && Rand.Chance(chance))
            {
                Place(map, kind, minOpenRadius);
            }
        }

        // The roomiest standable cell: most standable cells within the radius.
        public static string Place(Map map, PawnKindDef kind, float minOpenRadius)
        {
            if (kind == null)
            {
                return "no kind";
            }
            IntVec3 best = IntVec3.Invalid;
            int bestOpen = -1;
            for (int i = 0; i < 300; i++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                if (!c.Standable(map) || c.DistanceToEdge(map) < 8)
                {
                    continue;
                }
                int open = GenRadial.RadialCellsAround(c, minOpenRadius, true).Count(x => x.InBounds(map) && x.Standable(map));
                if (open > bestOpen)
                {
                    bestOpen = open;
                    best = c;
                }
            }
            if (!best.IsValid)
            {
                return "no cell";
            }
            Pawn p = PawnGenerator.GeneratePawn(kind);
            GenSpawn.Spawn(p, best, map);
            return "placed galuush at " + best + " open=" + bestOpen;
        }
    }

    // jawa/static_call proofs (validation.py, hydrocarbon_wave1).
    public static class RM_HydrocarbonProof
    {
        public static string ProofGaluush(string unused)
        {
            Map map = Find.CurrentMap;
            return map == null ? "no map" : RM_GenStep_Galuush.Place(map, DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Galuush"), 4.9f);
        }

        // "cold|hot": spawn a drifter at the map centre-ish, kill it with a cut or a burn, report
        // whether the death action judged the kill hot.
        public static string ProofDrifterKill(string mode)
        {
            Map map = Find.CurrentMap;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Drifter");
            if (map == null || kind == null)
            {
                return "no map or kind";
            }
            if (!CellFinder.TryFindRandomCell(map, c => c.Standable(map), out IntVec3 cell))
            {
                return "no cell";
            }
            Pawn p = PawnGenerator.GeneratePawn(kind);
            GenSpawn.Spawn(p, cell, map);
            DamageDef dd = mode == "hot" ? DamageDefOf.Burn : DamageDefOf.Cut;
            for (int i = 0; i < 40 && !p.Dead; i++)
            {
                p.TakeDamage(new DamageInfo(dd, 8f));
            }
            RM_DeathActionProperties_HotKill props = p.RaceProps.deathAction as RM_DeathActionProperties_HotKill;
            bool hot = RM_DeathActionWorker_HotKill.KilledHot(p, props?.coldInjuries);
            return "dead=" + p.Dead + " killedHot=" + hot + " at " + cell;
        }
    }
}
