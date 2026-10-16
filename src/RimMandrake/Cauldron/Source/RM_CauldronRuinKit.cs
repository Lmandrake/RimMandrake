using System.Collections.Generic;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using Verse;

namespace RimMandrake.Cauldron
{
    // ════════════════════════════════════════════════════════════════════
    // CAULDRON_MECHANICS_BUILD_1 part 4 — the corroded ruin kit that teaches the Filter-Works (owner Q2 2026-10-15:
    // "Everything except the Seismometer" -> the Filter-Works, the ruin set-pieces and the Oomo shrine are in).
    //
    // One set-piece per Cauldron map (RM_CauldronRuinScatter, the shared Environmental Hazards scatterer, registered onto
    // Base_Player). It spawns ONE thing: RM_CorrodedFilterRig. The rig is studied in place
    // (CompAnalyzableUnlockResearch, vanilla's own "study this to unlock research" route) and unlocks
    // RM_FilterWorksResearch. On its first spawn it dresses its own site from RM_CompProperties_CauldronRuinKit.pieces:
    // corroded tanks still holding the toxic water hauled in as offerings that failed, broken pipe and slag — and any
    // `shrineDefs` a higher tier adds by patch (the RM tier names no god; the Utinni layer patches in Oomo's grudging
    // shrine). Dressing runs once (scribed), never on load.
    // ════════════════════════════════════════════════════════════════════
    public class RM_RuinPiece
    {
        public ThingDef def;
        public IntRange count = new IntRange(1, 1);
        public LiquidDef liquid;                      // tanks only: what is left in them
        public FloatRange liquidFraction = new FloatRange(0.1f, 0.4f);
        public FloatRange hitPoints = new FloatRange(0.2f, 0.6f);
    }

    public class RM_CompProperties_CauldronRuinKit : CompProperties
    {
        public List<RM_RuinPiece> pieces = new List<RM_RuinPiece>();
        public List<ThingDef> shrineDefs = new List<ThingDef>();   // empty in the RM tier; a Utinni patch adds Oomo's shrine
        public float radius = 5f;

        public RM_CompProperties_CauldronRuinKit()
        {
            compClass = typeof(RM_CompCauldronRuinKit);
        }
    }

    public class RM_CompCauldronRuinKit : ThingComp
    {
        private bool dressed;
        public int piecesPlaced;
        public int shrinesPlaced;

        public RM_CompProperties_CauldronRuinKit Props => (RM_CompProperties_CauldronRuinKit)props;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref dressed, "rmRuinDressed", false);
            Scribe_Values.Look(ref piecesPlaced, "rmRuinPieces", 0);
            Scribe_Values.Look(ref shrinesPlaced, "rmRuinShrines", 0);
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (respawningAfterLoad || dressed) return;
            dressed = true;
            if (parent.Faction == Faction.OfPlayer) return;   // a player-built copy (dev spawn as player) is never dressed
            Map map = parent.Map;
            foreach (ThingDef shrine in Props.shrineDefs)
                if (shrine != null && Place(shrine, map, null, new FloatRange(0.5f, 0.8f)) != null) shrinesPlaced++;
            foreach (RM_RuinPiece p in Props.pieces)
            {
                if (p?.def == null) continue;
                int n = p.count.RandomInRange;
                for (int i = 0; i < n; i++)
                {
                    Thing t = Place(p.def, map, p, p.hitPoints);
                    if (t == null) continue;
                    piecesPlaced++;
                    if (t is Building_LiquidTank tank && p.liquid != null)
                        tank.TryAddLiquid(p.liquid, System.Math.Max(1, (int)(tank.Capacity * p.liquidFraction.RandomInRange)));
                }
            }
        }

        private Thing Place(ThingDef def, Map map, RM_RuinPiece piece, FloatRange hp)
        {
            ThingDef stuff = def.MadeFromStuff ? GenStuff.DefaultStuffFor(def) : null;
            CellRect own = parent.OccupiedRect();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(parent.Position, Props.radius, false).InRandomOrder())
            {
                Rot4 rot = def.rotatable ? Rot4.Random : Rot4.North;
                CellRect rect = GenAdj.OccupiedRect(c, rot, def.size);
                if (!Free(rect, own, map, def.category == ThingCategory.Item)) continue;
                Thing t = ThingMaker.MakeThing(def, stuff);
                if (t.def.useHitPoints) t.HitPoints = System.Math.Max(1, (int)(t.MaxHitPoints * hp.RandomInRange));
                GenSpawn.Spawn(t, c, map, rot);
                return t;
            }
            return null;
        }

        private static bool Free(CellRect rect, CellRect own, Map map, bool item)
        {
            foreach (IntVec3 r in rect)
            {
                if (!r.InBounds(map) || own.Contains(r) || !r.Standable(map) || r.GetEdifice(map) != null) return false;
                TerrainDef t = r.GetTerrain(map);
                if (t == null || t.IsWater) return false;
                if (!item && r.GetFirstBuilding(map) != null) return false;
            }
            return true;
        }

        public override string CompInspectStringExtra()
        {
            return DebugSettings.godMode ? "Ruin kit: " + piecesPlaced + " pieces, " + shrinesPlaced + " shrine(s)" : null;
        }
    }

    // The site test for the ruin scatter: the Mod Setting, a Cauldron map, and a dry, unroofed, open 7x7 around the cell.
    public class RM_ScattererValidator_CauldronRuinSite : ScattererValidator
    {
        public int clearRadius = 3;

        public override bool Allows(IntVec3 c, Map map)
        {
            if (!RM_CauldronSettings.ruinKitEnabled) return false;
            if (map.Biome == null || map.Biome.defName != "RM_Cauldron") return false;
            CellRect rect = CellRect.CenteredOn(c, clearRadius);
            foreach (IntVec3 r in rect)
            {
                if (!r.InBounds(map) || !r.Standable(map) || r.Roofed(map) || r.GetEdifice(map) != null) return false;
                TerrainDef t = r.GetTerrain(map);
                if (t == null || t.IsWater) return false;
            }
            return true;
        }
    }
}
