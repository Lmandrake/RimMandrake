using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Pyrelands
{
    // ════════════════════════════════════════════════════════════════════
    // THREE-STAGE GROWTH ART FOR A WILD PLANT — QUICKGRASS_GROWTH_STAGES_1.
    //
    // Owner, 2026-09-14: quickgrass should read as "just starting,
    // half-grown, and then tall lush grass grown high".
    //
    // WHY THIS IS NOT XML. Vanilla has exactly one growth-keyed art swap,
    // `immatureGraphicPath`, and it is two-stage AND gated on
    // `!HarvestableNow` (decompiled Plant.cs:490). `HarvestableNow` is
    // `def.plant.Harvestable && growth > harvestMinGrowth`, and
    // `Harvestable` is false for anything with no `harvestedThingDef` —
    // quickgrass has none, so `!HarvestableNow` is true for its ENTIRE
    // life and the immature graphic would never be dropped. Two stages
    // short of three, and stuck on the wrong one. There is no second
    // field, so this is tier (c).
    //
    // WHY A `thingClass`, NOT A HARMONY PATCH. `Plant.Graphic` is a
    // virtual property. Overriding it in a subclass costs nothing at
    // startup, cannot conflict with another mod's patch, and leaves every
    // plant in the game that is not ours running vanilla code.
    //
    // Reusable by design, not hardcoded to quickgrass: the paths and the
    // two thresholds ride a DefModExtension, so any plant in any biome kit
    // can opt in with XML alone.
    // ════════════════════════════════════════════════════════════════════

    // TRIGGERED BY: <modExtensions><li Class="RimMandrake.Pyrelands.PlantGrowthStages">
    // on a ThingDef whose thingClass is Plant_GrowthStaged.
    //
    // Each path is a FOLDER, exactly like `graphicData/texPath` is for
    // Graphic_Random: Graphic_Collection.Init calls
    // ContentFinder<Texture2D>.GetAllInFolder(path) and makes one
    // subgraphic per file under it (decompiled Graphic_Collection.cs).
    // That is why the sprout and half art sit in their own folders — four
    // PNGs in one folder would be ONE eight-way-random graphic mixing the
    // stages, not two two-way ones.
    public class PlantGrowthStages : DefModExtension
    {
        public string sproutGraphicPath;
        public string halfGraphicPath;

        // Clean thirds. Below the first, the sprout art; below the second,
        // the half-grown art; at or above it, the def's own tall art.
        public float sproutMaxGrowth = 0.33f;
        public float halfMaxGrowth = 0.66f;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (sproutGraphicPath.NullOrEmpty() && halfGraphicPath.NullOrEmpty())
            {
                yield return "PlantGrowthStages has neither sproutGraphicPath nor halfGraphicPath — "
                           + "the extension does nothing.";
            }
            if (halfMaxGrowth <= sproutMaxGrowth)
            {
                yield return "PlantGrowthStages halfMaxGrowth (" + halfMaxGrowth
                           + ") must be greater than sproutMaxGrowth (" + sproutMaxGrowth
                           + ") or the half-grown stage can never be reached.";
            }
        }
    }

    // Graphics MUST be built on the main thread, and RimWorld's own
    // PlantProperties.PostLoadSpecial does it inside
    // LongEventHandler.ExecuteWhenFinished for exactly that reason
    // (decompiled PlantProperties.cs:257). Same pattern, same
    // GraphicDatabase.Get overload, same arguments — so a staged graphic
    // is built identically to the leafless/immature ones it sits beside.
    [StaticConstructorOnStartup]
    public static class PlantGrowthStageGraphics
    {
        internal const int StageSprout = 0;
        internal const int StageHalf = 1;
        internal const int StageTall = 2;

        // ThingDef -> { sprout, half }. Either entry may be null: a def
        // that supplies only one path simply keeps its own art for the
        // other stage.
        private static readonly Dictionary<ThingDef, Graphic[]> Cache =
            new Dictionary<ThingDef, Graphic[]>();

        static PlantGrowthStageGraphics()
        {
            LongEventHandler.ExecuteWhenFinished(ResolveAll);
        }

        private static void ResolveAll()
        {
            try
            {
                List<ThingDef> all = DefDatabase<ThingDef>.AllDefsListForReading;
                for (int i = 0; i < all.Count; i++)
                {
                    ThingDef d = all[i];
                    PlantGrowthStages ext = d.GetModExtension<PlantGrowthStages>();
                    if (ext == null)
                    {
                        continue;
                    }
                    if (d.graphicData == null || d.graphic == null)
                    {
                        Log.Error("[RimMandrake.Pyrelands] growth-stage art: " + d.defName
                                  + " carries PlantGrowthStages but has no resolved graphicData — "
                                  + "stage art NOT in effect for it.");
                        continue;
                    }
                    Cache[d] = new[]
                    {
                        Build(d, ext.sproutGraphicPath),
                        Build(d, ext.halfGraphicPath),
                    };
                }
                Log.Message("[RimMandrake.Pyrelands] growth-stage art: armed for "
                            + Cache.Count + " plant def(s)");
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Pyrelands] growth-stage art: resolve FAILED, "
                          + "staged plants fall back to their own art — " + e.Message);
            }
        }

        private static Graphic Build(ThingDef d, string path)
        {
            if (path.NullOrEmpty())
            {
                return null;
            }
            return GraphicDatabase.Get(d.graphicData.graphicClass, path, d.graphic.Shader,
                                       d.graphicData.drawSize, d.graphicData.color,
                                       d.graphicData.colorTwo);
        }

        // Null for the tall stage, for a def with no extension, or for a
        // stage whose path was not supplied — every caller falls back to
        // the def's own graphic on null.
        internal static Graphic For(ThingDef d, int stage)
        {
            if (d == null || stage < StageSprout || stage > StageHalf)
            {
                return null;
            }
            Graphic[] staged;
            if (!Cache.TryGetValue(d, out staged) || staged == null)
            {
                return null;
            }
            return staged[stage];
        }
    }

    // TRIGGERED BY: <thingClass>RimMandrake.Pyrelands.Plant_GrowthStaged</thingClass>.
    public class Plant_GrowthStaged : Plant
    {
        // Not saved: it only exists to decide whether the map mesh needs
        // reprinting, and a freshly loaded plant reprints anyway.
        private int lastStage = -1;

        private int CurrentStage(PlantGrowthStages ext)
        {
            float g = Growth;
            if (g < ext.sproutMaxGrowth)
            {
                return PlantGrowthStageGraphics.StageSprout;
            }
            if (g < ext.halfMaxGrowth)
            {
                return PlantGrowthStageGraphics.StageHalf;
            }
            return PlantGrowthStageGraphics.StageTall;
        }

        public override Graphic Graphic
        {
            get
            {
                // Every rung of vanilla's own chain (decompiled
                // Plant.cs:470) wins first, in its exact order and with its
                // exact conditions — sowing, polluted, leafless-immature,
                // leafless, immature. Only the LAST rung, where vanilla
                // would hand back the def's own graphic, is substituted.
                // leaflessGraphicPath behaviour is therefore untouched.
                if (LifeStage == PlantLifeStage.Sowing)
                {
                    return base.Graphic;
                }
                if (def.plant.pollutedGraphic != null && base.PositionHeld.IsPolluted(base.MapHeld))
                {
                    return base.Graphic;
                }
                if (def.plant.leaflessImmatureGraphic != null && LeaflessNow && !HarvestableNow)
                {
                    return base.Graphic;
                }
                if (def.plant.leaflessGraphic != null && LeaflessNow && (!sown || !HarvestableNow))
                {
                    return base.Graphic;
                }
                if (def.plant.immatureGraphic != null && !HarvestableNow)
                {
                    return base.Graphic;
                }
                if (!RM_PyrelandsSettings.plantGrowthStagesEnabled)
                {
                    return base.Graphic;
                }
                PlantGrowthStages ext = def.GetModExtension<PlantGrowthStages>();
                if (ext == null)
                {
                    return base.Graphic;
                }
                return PlantGrowthStageGraphics.For(def, CurrentStage(ext)) ?? base.Graphic;
            }
        }

        // A WILD plant's growth never dirties the map mesh: vanilla's own
        // reprint on growth is gated on CurrentlyCultivated()
        // (decompiled Plant.cs:827), so an uncultivated plant keeps the
        // mesh it was last printed with until something else in its
        // section happens to dirty it. Without this the stage art would
        // change only by accident, minutes or hours late. One comparison
        // per plant per long tick, and a reprint only on the two frames of
        // its life where the stage actually changes.
        public override void TickLong()
        {
            base.TickLong();
            if (base.Destroyed || !base.Spawned)
            {
                return;
            }
            PlantGrowthStages ext = def.GetModExtension<PlantGrowthStages>();
            if (ext == null)
            {
                return;
            }
            int stage = CurrentStage(ext);
            if (stage == lastStage)
            {
                return;
            }
            lastStage = stage;
            Map map = base.Map;
            if (map != null)
            {
                map.mapDrawer.MapMeshDirty(base.Position, MapMeshFlagDefOf.Things);
            }
        }

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            PlantGrowthStages ext = def.GetModExtension<PlantGrowthStages>();
            lastStage = (ext != null) ? CurrentStage(ext) : -1;
        }
    }
}
