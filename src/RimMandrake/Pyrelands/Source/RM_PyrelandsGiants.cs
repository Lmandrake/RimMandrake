using System.Linq;
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
            if (!PyrelandsMechanicsGate.On || !RM_PyrelandsSettings.ullaiEnabled)
            {
                return null;
            }
            RM_FollowBurnExtension ext = pawn.def.GetModExtension<RM_FollowBurnExtension>();
            if (ext == null || pawn.Map == null || pawn.Faction != null || pawn.Downed || !Rand.Chance(ext.chancePerCheck))
            {
                return null;
            }
            return JobFor(pawn, ext, out _, out _);
        }

        /// <summary>The giver after its chance roll: the GotoWander job toward the anchor (or the nearest ash), or null when the
        /// pawn stays. Shared by TryGiveJob and the test probe so the probe reads the giver's own decision.</summary>
        internal static Job JobFor(Pawn pawn, RM_FollowBurnExtension ext, out IntVec3 anchor, out RM_FollowBurnAction action)
        {
            Map map = pawn.Map;
            anchor = MapComponent_BurnLine.For(map)?.BurnCenterAgo(Mathf.RoundToInt(ext.lagDays * GenDate.TicksPerDay))
                     ?? IntVec3.Invalid;
            bool OnAsh(IntVec3 c) => c.InBounds(map) && ext.terrains.Contains(c.GetTerrain(map));
            float dist = anchor.IsValid ? (pawn.Position - anchor).LengthHorizontal : 0f;
            action = RM_BurnKernel.FollowBurnDecision(anchor.IsValid, OnAsh(pawn.Position), dist, ext.settleRadius, ext.radius);
            if (action == RM_FollowBurnAction.Stay)
            {
                return null;   // already grazing the right black (or, with no record yet, on ash)
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

        /// <summary>Test probe (jawa/static_call; PYRE_HERD_DRIVE_BUILD_TWO_DAYS_LATER). Every wild, standing pawn of `raceDefName` on the
        /// current map: the giver's decision with the chance roll set aside, their centroid, and the anchor. issue=true also starts
        /// each GotoWander the giver would give (the chance roll is the one part this skips: its cadence is INFERRED, 0.04 a check).
        /// -> "n=;cx=;cz=;anchor=x,z|invalid;stay=;goAnchor=;goAsh=;noCell=;issued="</summary>
        public static string ProbeHerd(string raceDefName, bool issue)
        {
            Map map = Find.CurrentMap;
            ThingDef race = DefDatabase<ThingDef>.GetNamedSilentFail(raceDefName ?? "");
            RM_FollowBurnExtension ext = race?.GetModExtension<RM_FollowBurnExtension>();
            if (map == null || ext == null)
            {
                return "error=no map, or " + raceDefName + " has no RM_FollowBurnExtension";
            }
            int n = 0, sx = 0, sz = 0, stay = 0, goAnchor = 0, goAsh = 0, noCell = 0, issued = 0;
            IntVec3 anchor = IntVec3.Invalid;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned.ToList())
            {
                if (p.def != race || p.Faction != null || p.Downed || p.Dead)
                {
                    continue;
                }
                n++; sx += p.Position.x; sz += p.Position.z;
                Job job = JobFor(p, ext, out anchor, out RM_FollowBurnAction act);
                if (act == RM_FollowBurnAction.Stay) stay++;
                else if (act == RM_FollowBurnAction.GoAnchor) goAnchor++;
                else goAsh++;
                if (act != RM_FollowBurnAction.Stay && job == null) noCell++;
                if (issue && job != null)
                {
                    p.jobs.StartJob(job, JobCondition.InterruptForced);
                    issued++;
                }
            }
            return string.Format(System.Globalization.CultureInfo.InvariantCulture,
                "n={0};cx={1:0.0};cz={2:0.0};anchor={3};stay={4};goAnchor={5};goAsh={6};noCell={7};issued={8}",
                n, n > 0 ? (float)sx / n : -1f, n > 0 ? (float)sz / n : -1f,
                anchor.IsValid ? anchor.x + "," + anchor.z : "invalid", stay, goAnchor, goAsh, noCell, issued);
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
