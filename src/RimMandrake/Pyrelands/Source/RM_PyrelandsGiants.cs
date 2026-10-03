using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Pyrelands
{
    // PYRELANDS_ULLAI_GIANT_BUILD_1 (design/Jawa/worldbuilding/biomes/pyrelands_bedazzle_review_2026-10-01.md §3,
    // ruled by card: both). The ullai herd that follows the burn, and the furnace-beast grown into a giant.

    /// <summary>On a race: graze where it burned about lagDays ago (MapComponent_BurnLine's history), on ash.</summary>
    public class RM_FollowBurnExtension : DefModExtension
    {
        public float lagDays = 2f;
        public float radius = 10f;
        public float chancePerCheck = 0.04f;
        public float settleRadius = 6f;
        public List<TerrainDef> terrains = new List<TerrainDef>();
    }

    /// <summary>
    /// Wild herds only (a tamed herd stays where its keepers put it). Ash terrain never reverts, so a bare terrain
    /// target would read every burn ever; the burn-line's record says which black is two days old. With no record
    /// yet (a new map, no fire), the herd still drifts onto the nearest ash.
    /// </summary>
    public class RM_JobGiver_FollowBurn : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!RM_PyrelandsSettings.pyrelandsEnabled || !RM_PyrelandsSettings.ullaiEnabled)
            {
                return null;
            }
            RM_FollowBurnExtension ext = pawn.def.GetModExtension<RM_FollowBurnExtension>();
            if (ext == null || pawn.Map == null || pawn.Faction != null || pawn.Downed || !Rand.Chance(ext.chancePerCheck))
            {
                return null;
            }
            Map map = pawn.Map;
            IntVec3 anchor = MapComponent_BurnLine.For(map)?.BurnCenterAgo(Mathf.RoundToInt(ext.lagDays * GenDate.TicksPerDay))
                             ?? IntVec3.Invalid;
            bool OnAsh(IntVec3 c) => c.InBounds(map) && ext.terrains.Contains(c.GetTerrain(map));
            if (anchor.IsValid && OnAsh(pawn.Position) && pawn.Position.InHorDistOf(anchor, ext.settleRadius + ext.radius))
            {
                return null;   // already grazing the right black
            }
            if (!anchor.IsValid && OnAsh(pawn.Position))
            {
                return null;
            }
            IntVec3 from = anchor.IsValid ? anchor : pawn.Position;
            float r = anchor.IsValid ? ext.radius : 25f;
            if (!CellFinder.TryFindRandomCellNear(from, map, Mathf.RoundToInt(r),
                    c => OnAsh(c) && c.Standable(map) && pawn.CanReach(c, PathEndMode.OnCell, Danger.Some), out IntVec3 target))
            {
                return null;
            }
            Job job = JobMaker.MakeJob(JobDefOf.GotoWander, target);
            job.locomotionUrgency = LocomotionUrgency.Walk;
            return job;
        }
    }

    /// <summary>
    /// The ullai and giant settings take effect at startup (restart): the giant's numbers live in XML, and the
    /// classic furnace-beast (bs 3.2, 0.08, groups 3~7, the original sprite) is restored here when the giant is off.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class RM_PyrelandsGiants
    {
        static RM_PyrelandsGiants()
        {
            BiomeDef pyrelands = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_Pyrelands");
            PawnKindDef ullai = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Ullai");
            if (ullai != null)
            {
                if (!RM_PyrelandsSettings.ullaiEnabled)
                {
                    SetCommonality(pyrelands, ullai, 0f);
                }
                else if (!Mathf.Approximately(RM_PyrelandsSettings.ullaiHerdSizeMultiplier, 1f))
                {
                    IntRange g = ullai.wildGroupSize;
                    ullai.wildGroupSize = new IntRange(
                        Mathf.Max(1, Mathf.RoundToInt(g.min * RM_PyrelandsSettings.ullaiHerdSizeMultiplier)),
                        Mathf.Max(1, Mathf.RoundToInt(g.max * RM_PyrelandsSettings.ullaiHerdSizeMultiplier)));
                }
            }

            PawnKindDef beast = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_FurnaceBeast");
            if (beast != null && !RM_PyrelandsSettings.furnaceBeastGiant)
            {
                RestoreClassicFurnaceBeast(beast, pyrelands);
            }
        }

        private static void SetCommonality(BiomeDef biome, PawnKindDef kind, float value)
        {
            if (biome == null)
            {
                return;
            }
            var records = Traverse.Create(biome).Field("wildAnimals").GetValue<List<BiomeAnimalRecord>>();
            if (records == null)
            {
                return;
            }
            foreach (BiomeAnimalRecord r in records)
            {
                if (r.animal == kind)
                {
                    r.commonality = value;
                }
            }
            Traverse.Create(biome).Field("cachedAnimalCommonalities").SetValue(null);
        }

        private static void RestoreClassicFurnaceBeast(PawnKindDef kind, BiomeDef pyrelands)
        {
            ThingDef race = kind.race;
            race.race.baseBodySize = PyrelandsTuning.FurnaceClassicBodySize;
            race.race.baseHealthScale = 2.8f;
            kind.combatPower = 220f;
            kind.wildGroupSize = new IntRange(3, 7);
            float[] classicDraw = { 1.6f, 2.4f, 3.2f };
            for (int i = 0; i < kind.lifeStages.Count && i < classicDraw.Length; i++)
            {
                GraphicData g = kind.lifeStages[i].bodyGraphicData;
                if (g == null)
                {
                    continue;
                }
                g.texPath = "Things/Pawn/Animal/Pyrelands/FurnaceBeast/FurnaceBeast";
                g.drawSize = new Vector2(classicDraw[i], classicDraw[i]);
                Traverse.Create(g).Field("cachedGraphic").SetValue(null);
            }
            SetCommonality(pyrelands, kind, 0.08f);
        }
    }
}
