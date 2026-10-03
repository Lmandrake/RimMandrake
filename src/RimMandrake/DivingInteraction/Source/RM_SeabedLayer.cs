using System;
using System.Reflection;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // SEABED_PLANET_LAYER_1, Phase 1 — the layer and nothing else.
    //
    // The sea floor is a real planet layer: a GEOMETRIC TWIN of the surface. Same origin,
    // radius, view angle, subdivisions and tile count, so seabed tile N lies beneath surface
    // tile N and translation between them is arithmetic — new PlanetTile(id, otherLayer).
    // There is deliberately NO dictionary, registry or any other ledger pairing surface tiles
    // to floor tiles: the arithmetic IS the mapping, and a second copy of it can only rot.
    //
    // Phase 1 builds the layer, its two placeholder biomes and its world object. Descent is
    // Phase 2; terrain, plants and fauna are Phase 3; real per-sea biomes are Phase 4; depth
    // and geology shaping is Phase 5, taken with the world remake. Seams for those are marked
    // "PHASE n SEAM" below.
    //
    // This file adds no Harmony patch and takes no Harmony reference: the one private field it
    // needs is read with plain reflection (see SubdivisionsOf), keeping this mod's documented
    // "no Harmony" property intact.

    [DefOf]
    public static class RM_SeabedDefOf
    {
        public static PlanetLayerDef RM_SeabedLayer;
        public static BiomeDef RM_SeabedUnavailable;
        public static BiomeDef RM_SeabedFloor;
        public static WorldObjectDef RM_SeabedSite;

        static RM_SeabedDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_SeabedDefOf));
        }
    }

    /// <summary>
    /// Declared on a SURFACE BiomeDef to say that the water there has a reachable floor.
    ///
    /// This exists so we never classify OUR content by reading a vanilla flag. Vanilla's own
    /// test is SurfaceTile.WaterCovered, i.e. elevation &lt;= 0 — a good classification, so we
    /// SEED from it when a surface biome says nothing, and own the answer wherever a biome of
    /// ours does carry this extension.
    ///
    /// PHASE 4 SEAM: each of the four seas gets this extension, and gains a field naming the
    /// real seabed BiomeDef that belongs under it. Phase 1 deliberately has one placeholder
    /// floor biome, so there is nothing yet to name.
    /// </summary>
    public class RM_SeabedAccessExtension : DefModExtension
    {
        public bool hasSeabed = true;

        // SEABED_PER_SEA_FLOORS_1: the real floor biome beneath this sea. Null falls back to the
        // generic RM_SeabedFloor placeholder, so a surface biome with no mapping still works.
        public BiomeDef floorBiome;
    }

    /// <summary>Registers the seabed layer on a fresh world, before any layer is generated.</summary>
    public class GameSetupStep_SeabedLayer : GameSetupStep
    {
        public override int SeedPart => 61140337;

        public override void GenerateFresh()
        {
            // Registration only. At this point the surface's geometry exists (RegisterPlanetLayer
            // calls InitializeLayer, so TilesCount is already valid) but no layer has run its
            // world gen steps yet, so there is nothing to mirror. WorldGenerator.GenerateWorld
            // walks every registered layer in layer-id order immediately after the setup steps,
            // which is what runs WorldGenStep_SeabedLayer below — after the surface, because the
            // surface was registered first and therefore holds the lower id.
            RM_SeabedLayerUtility.EnsureLayer(generate: false);
        }
    }

    /// <summary>
    /// Mirrors the surface onto the seabed layer. This step GENERATES NOTHING of its own — the
    /// surface's finished tiles are authoritative and every value here is copied or derived.
    /// </summary>
    public class WorldGenStep_SeabedLayer : WorldGenStep
    {
        public override int SeedPart => 61140338;

        public override void GenerateFresh(string seed, PlanetLayer layer)
        {
            RM_SeabedLayerUtility.MirrorSurfaceOnto(layer);
        }
    }

    /// <summary>
    /// Runs on every load as well as every fresh game, so an existing save gains the layer.
    /// WorldComponents are discovered by type, not by def, so no def registers this.
    /// </summary>
    public class WorldComponent_SeabedLayer : WorldComponent
    {
        public WorldComponent_SeabedLayer(World world) : base(world) { }

        public override void FinalizeInit(bool fromLoad)
        {
            base.FinalizeInit(fromLoad);
            RM_SeabedLayerUtility.EnsureLayer(generate: true);
        }
    }

    public static class RM_SeabedLayerUtility
    {
        // PlanetLayer.subdivisions is private and there is no accessor. It must be READ, never
        // guessed: the parameter defaults to 10, a scenario may set anything, and a mismatch
        // would silently pair seabed tiles with different places on the planet rather than fail.
        private static readonly FieldInfo SubdivisionsField =
            typeof(PlanetLayer).GetField("subdivisions", BindingFlags.Instance | BindingFlags.NonPublic);

        private static int SubdivisionsOf(PlanetLayer layer)
        {
            if (SubdivisionsField == null)
            {
                throw new InvalidOperationException(
                    "[RimMandrake.DivingInteraction] PlanetLayer.subdivisions could not be read. Refusing to " +
                    "fall back on a default, which would pair the seabed with the wrong world locations.");
            }

            return (int)SubdivisionsField.GetValue(layer);
        }

        public static bool IsSeabedLayer(PlanetLayer layer)
        {
            return layer != null && RM_SeabedDefOf.RM_SeabedLayer != null && layer.Def == RM_SeabedDefOf.RM_SeabedLayer;
        }

        public static bool IsSeabedTile(PlanetTile tile)
        {
            return tile.Valid && IsSeabedLayer(tile.Layer);
        }

        /// <summary>The registered seabed layer, or null if it has not been registered yet.</summary>
        public static PlanetLayer Layer
        {
            get
            {
                if (RM_SeabedDefOf.RM_SeabedLayer == null)
                {
                    return null;
                }

                WorldGrid grid = Find.WorldGrid;
                // FirstLayerOfDef returns the surface for a null def, so the guard above matters.
                return grid?.FirstLayerOfDef(RM_SeabedDefOf.RM_SeabedLayer);
            }
        }

        /// <summary>
        /// Registers the seabed layer if it is absent, links it to the surface, and — when asked —
        /// generates its tiles. Safe to call repeatedly; every step is idempotent.
        /// </summary>
        public static PlanetLayer EnsureLayer(bool generate)
        {
            WorldGrid grid = Find.WorldGrid;
            SurfaceLayer surface = grid?.Surface;
            if (surface == null)
            {
                return null;
            }

            PlanetLayer layer = Layer;
            if (layer == null)
            {
                layer = grid.RegisterPlanetLayer(
                    RM_SeabedDefOf.RM_SeabedLayer,
                    surface.Origin,
                    surface.Radius,
                    surface.ViewAngle,
                    surface.ExtraCameraAltitude,
                    SubdivisionsOf(surface),
                    surface.BackgroundWorldCameraOffset,
                    surface.BackgroundWorldCameraParallaxDistancePer100Cells,
                    surface.ViewCenter);
            }

            // The twin guard. Everything downstream — translation, descent, the floor a ship
            // arrives at — assumes tile N is tile N. Refuse to run rather than pair the wrong
            // places, which would be invisible and unrecoverable once a colony was built on it.
            if (layer.TilesCount != surface.TilesCount)
            {
                throw new InvalidOperationException(
                    "[RimMandrake.DivingInteraction] The seabed layer is not a geometric twin of the surface: " +
                    layer.TilesCount + " seabed tiles against " + surface.TilesCount + " surface tiles. " +
                    "Refusing to register a layer whose tiles would point at the wrong places.");
            }

            // World.FinalizeInit runs BEFORE Scribe resolves the saved connection dictionary.
            // Inserting connections during LoadingVars collides with references still to come,
            // so the work waits for PostLoadInit (loading) or runs straight away (fresh game).
            if (Scribe.mode == LoadSaveMode.Inactive || Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (!surface.HasConnectionFromTo(layer))
                {
                    surface.AddConnection(layer, 0f);
                }

                if (!layer.HasConnectionFromTo(surface))
                {
                    layer.AddConnection(surface, 0f);
                }

                // Only set a zoom route that is currently empty, so a scenario's or another
                // mod's route through this layer survives us.
                if (surface.zoomInToLayer == null)
                {
                    surface.zoomInToLayer = layer;
                }

                if (layer.zoomOutToLayer == null)
                {
                    layer.zoomOutToLayer = surface;
                }
            }

            // An existing save has no seabed tiles and no seabed world gen step in its history,
            // so generate them here. A save that already carries the layer arrives with its tiles
            // and skips this.
            if (generate && layer.Tiles.Count == 0 && surface.Tiles.Count > 0)
            {
                // Loading an older world must not consume the game's random stream, or every
                // roll after the load differs from the one the save would otherwise have made.
                Rand.PushState();
                try
                {
                    layer.RunWorldGeneration(Find.World.info.Seed);
                    layer.Standardize();
                }
                finally
                {
                    Rand.PopState();
                }
            }

            return layer;
        }

        /// <summary>
        /// Replaces the layer's tiles with one per surface tile and populates each from the
        /// surface tile above it.
        /// </summary>
        public static void MirrorSurfaceOnto(PlanetLayer layer)
        {
            if (layer == null || !IsSeabedLayer(layer))
            {
                return;
            }

            layer.Tiles.Clear();
            for (int i = 0; i < layer.TilesCount; i++)
            {
                layer.Tiles.Add(new SurfaceTile(new PlanetTile(i, layer)));
            }

            for (int i = 0; i < layer.TilesCount; i++)
            {
                PopulateTile(new PlanetTile(i, layer));
            }
        }

        /// <summary>The surface tile directly above a seabed tile. Arithmetic, not a lookup.</summary>
        public static PlanetTile SurfaceTileOf(PlanetTile floorTile)
        {
            if (!floorTile.Valid)
            {
                return PlanetTile.Invalid;
            }

            if (!IsSeabedTile(floorTile))
            {
                return floorTile;
            }

            SurfaceLayer surface = Find.WorldGrid?.Surface;
            if (surface == null || floorTile.tileId >= surface.TilesCount)
            {
                return PlanetTile.Invalid;
            }

            return new PlanetTile(floorTile.tileId, surface);
        }

        /// <summary>The seabed tile directly below a surface tile. Arithmetic, not a lookup.</summary>
        public static PlanetTile FloorTileOf(PlanetTile surfaceTile)
        {
            if (!surfaceTile.Valid)
            {
                return PlanetTile.Invalid;
            }

            if (IsSeabedTile(surfaceTile))
            {
                return surfaceTile;
            }

            if (surfaceTile.Layer != Find.WorldGrid?.Surface)
            {
                return PlanetTile.Invalid;
            }

            PlanetLayer layer = Layer;
            if (layer == null || surfaceTile.tileId >= layer.TilesCount)
            {
                return PlanetTile.Invalid;
            }

            return new PlanetTile(surfaceTile.tileId, layer);
        }

        /// <summary>
        /// Does the water on this surface tile have a floor a ship can reach?
        ///
        /// Our own declaration wins where a surface biome makes one; otherwise this seeds from
        /// vanilla's classification (SurfaceTile.WaterCovered, elevation &lt;= 0).
        /// </summary>
        public static bool SurfaceHasFloor(Tile surfaceTile)
        {
            if (surfaceTile?.PrimaryBiome == null)
            {
                return false;
            }

            RM_SeabedAccessExtension ext = surfaceTile.PrimaryBiome.GetModExtension<RM_SeabedAccessExtension>();
            if (ext != null)
            {
                return ext.hasSeabed;
            }

            return surfaceTile.WaterCovered;
        }

        /// <summary>
        /// The floor biome under a surface tile: the surface biome's declared floorBiome, else the
        /// generic placeholder. Data-driven; no per-sea code.
        /// </summary>
        public static BiomeDef FloorBiomeFor(Tile surfaceTile)
        {
            BiomeDef declared = surfaceTile?.PrimaryBiome?.GetModExtension<RM_SeabedAccessExtension>()?.floorBiome;
            return declared ?? RM_SeabedDefOf.RM_SeabedFloor;
        }

        /// <summary>
        /// Derives one seabed tile from the surface tile above it. Deliberately minimal in
        /// Phase 1: mirror what the surface already decided, choose between the two placeholder
        /// biomes, and invent nothing.
        /// </summary>
        public static void PopulateTile(PlanetTile floorTile)
        {
            Tile floor = floorTile.Tile;
            PlanetTile aboveTile = SurfaceTileOf(floorTile);
            Tile above = aboveTile.Valid ? aboveTile.Tile : null;
            if (floor == null || above == null)
            {
                return;
            }

            // PHASE 5 SEAM: depth is -elevation, and vanilla bottoms the ocean at -500 m, so a
            // usable depth range needs the elevation RESHAPED here at worldgen. That is taken
            // with the world remake; until then the floor simply carries the surface's number.
            floor.elevation = above.elevation;

            // Mirrored, not invented. PHASE 4 SEAM: a real thermocline belongs to the per-sea
            // biomes, not to this step.
            floor.temperature = above.temperature;

            // No weather reaches a sea floor.
            floor.rainfall = 0f;

            bool hasFloor = SurfaceHasFloor(above);
            floor.PrimaryBiome = hasFloor
                ? FloorBiomeFor(above)
                : RM_SeabedDefOf.RM_SeabedUnavailable;

            // PHASE 3/5 SEAM: real seabed relief arrives with terrain and geology. Flat under
            // water, impassable under land, is the least-inventing pair that still reads sanely.
            floor.hilliness = hasFloor ? Hilliness.Flat : Hilliness.Impassable;
        }
    }
}
