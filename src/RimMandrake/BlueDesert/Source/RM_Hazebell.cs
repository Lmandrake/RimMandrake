// BLUEDESERT_GPT_ENRICHMENT_1 §3 — the Carbon Garden: hydrocarbon flora only (owner, typed on the card
// 2026-09-30: "Only hydrocarbon plants please."). Vetting and the delegated design calls:
// design/Jawa/worldbuilding/biomes/bluedesert_carbon_garden_2026-09-30.md.
//
// RM_Plant_Hazebell: the hazebell (the pitch's "Ninefold Censer", renamed: `Ninefold` is our mod) opens while
// the RM_Haze weather falls and for hazebellOpenHours after it ends, and breathes out a pale puff while open.
// Plants tick only TickLong (2000 ticks), so the comp decides there; plants are PRINTED into the section mesh,
// so a change of state dirties the cell's Things mesh or the new graphic never shows.
//
// RM_CarbonGardenGate: with carbonGardenEnabled off, the three are removed from RM_BlueDesert's wildPlants at
// startup (the RM_BlueDesertFloraGate pattern; takes effect on the next launch).
//
// Gate: masterEnabled && hazebellBloomEnabled (the bloom); carbonGardenEnabled (the roster).

using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.BlueDesert
{
    public class CompProperties_HazeBloom : CompProperties
    {
        public string openTexPath;
        public string hazeWeather = "RM_Haze";

        public CompProperties_HazeBloom()
        {
            compClass = typeof(RM_CompHazeBloom);
        }
    }

    public class RM_CompHazeBloom : ThingComp
    {
        private int lastHazeTick = -1;
        private bool open;

        public CompProperties_HazeBloom Props => (CompProperties_HazeBloom)props;
        public bool Open => open;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lastHazeTick, "lastHazeTick", -1);
            Scribe_Values.Look(ref open, "open", false);
        }

        public override void CompTickLong()
        {
            base.CompTickLong();
            Map map = parent.Map;
            if (map == null)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            WeatherDef cur = map.weatherManager?.curWeather;
            bool hazeNow = cur != null && cur.defName == Props.hazeWeather;
            if (hazeNow)
            {
                lastHazeTick = now;
            }
            bool want = RM_BlueKernel.HazebellOpen(RM_BlueDesertSettings.masterEnabled && RM_BlueDesertSettings.hazebellBloomEnabled,
                hazeNow, lastHazeTick, now, RM_BlueDesertSettings.hazebellOpenHours);
            if (want != open)
            {
                open = want;
                map.mapDrawer.MapMeshDirty(parent.Position, MapMeshFlagDefOf.Things);
            }
            if (open)
            {
                FleckMaker.ThrowAirPuffUp(parent.DrawPos, map);
            }
        }

        public override string CompInspectStringExtra()
        {
            return open ? "Open: breathing out the Haze." : null;
        }
    }

    public class RM_Plant_Hazebell : Plant
    {
        private Graphic openGraphic;

        public override Graphic Graphic
        {
            get
            {
                RM_CompHazeBloom bloom = GetComp<RM_CompHazeBloom>();
                if (bloom == null || !bloom.Open || LeaflessNow || bloom.Props.openTexPath.NullOrEmpty())
                {
                    return base.Graphic;
                }
                if (openGraphic == null)
                {
                    openGraphic = GraphicDatabase.Get<Graphic_Single>(bloom.Props.openTexPath, def.graphicData.shaderType?.Shader ?? ShaderDatabase.CutoutPlant,
                        def.graphicData.drawSize, def.graphicData.color);
                }
                return openGraphic;
            }
        }
    }

    [StaticConstructorOnStartup]
    public static class RM_CarbonGardenGate
    {
        public static readonly string[] Garden = { "RM_Milelace", "RM_Hazebell", "RM_Longglass" };

        static RM_CarbonGardenGate()
        {
            if (RM_BlueDesertSettings.carbonGardenEnabled)
            {
                return;
            }
            BiomeDef biome = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_BlueDesert");
            biome?.wildPlants.RemoveAll(r => r.plant != null && System.Array.IndexOf(Garden, r.plant.defName) >= 0);
        }
    }
}
