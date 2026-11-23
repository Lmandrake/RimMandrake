namespace RimMandrake.Patches
{
    // ════════════════════════════════════════════════════════════════════
    // RIMMASTER_FIX_SOUTH_DRAWS_FRONT_SAID_MANY_TIMES — owner, 2026-10-16: "if you are more south, you go in front."
    // Owner, 2026-11-08: "Can we somehow fix this once and for all, for ALL large pawns and objects in the game?"
    //
    // Pure math, no game types (the offline selftest parses these constants; the scenario test compiles this file).
    //
    // MEASURED from decompiled 1.6 (decomp/rw16/all/Verse):
    //   * Altitudes.cs:11,13      layers sit 0.36585367 apart; AltInc 0.03658537 is a tenth of a layer.
    //   * Pawn_DrawTracker.cs:43  a pawn draws at def.Altitude (Pawn = 8.4146) + FlightYOffset + SeededYOffset, and
    //     Pawn_DrawTracker.cs:60  SeededYOffset = Rand.RangeSeeded(-AltInc, +AltInc, thingIDNumber): which of two
    //                             overlapping pawns is in front is a coin flip fixed by their thing ids. THAT is the
    //                             Dalgo mare bug, and why "south in front" kept failing for big pawns.
    //   * PawnRenderUtility.cs:334 a render node sits AltitudeForLayer(clamp(layer,-10,100)) = layer * 0.000366 above
    //                             the pawn's y, so one pawn's stack spans -0.0037 .. +0.0366.
    //   * Printer_Plane.cs:67     a printed quad's north edge is topVerticesAltitudeBias (default 0.01) nearer the
    //                             camera: two buildings of different heights on one layer order by size, not by z.
    //
    // THE RULE: on every map, a pawn's y and a printed building's or plant's y rise with how far south it stands,
    // inside a band that never reaches the next used layer. More south = nearer the camera = in front.
    // ════════════════════════════════════════════════════════════════════
    public static class SouthDrawsFrontKernel
    {
        public const float AltInc = 0.03658537f;
        public const float LayerSpacing = 0.36585367f;

        // Pawns: offset from the Pawn layer (23). Vanilla's lowest seeded offset is the floor, so the northern edge of
        // a map draws exactly as low as vanilla's lowest pawn. Ground top = Floor + PawnBand + stack 0.0366 = 0.30,
        // under PawnUnused (24, +0.366, nothing in 1.6 prints there). A pawn in full flight adds another PawnBand on
        // top of vanilla's flight lift: up to 0.64, under PawnState (25, +0.732).
        public const float PawnFloor = -0.03658537f;
        public const float PawnBand = 0.30f;

        // Printed things (map mesh). Plants on LowPlant..BuildingOnTop print flat on BuildingOnTop, as the plant fix
        // did in our biomes since 2026-10-16; so do all other things on Building..BuildingOnTop (BuildingAltitude).
        public const int PlantMinLayer = 11;     // AltitudeLayer.LowPlant
        public const int CommonLayer = 17;       // AltitudeLayer.BuildingOnTop
        public const int BuildingMinLayer = 15;  // AltitudeLayer.Building
        public const float PrintBand = 0.30f;    // of the 0.366 to the next layer; an overlay's +AltInc still fits
        public const float MaxCarriedOffset = 0.01f;   // vanilla's snow-overlay lift (0.000366) rides along; more is foreign
        // Inside one row, things on Building..BuildingOnTop keep vanilla's layer order: LayerTie per layer below the common one.
        // About 10 steps of a 24-bit depth buffer over the camera's 0.5..65.5 clip range (CameraDriver.cs:283, 65/2^24 =
        // 3.9e-6), so the order is resolvable; small beside one row (PrintBand / 1002 = 3.0e-4 on a 1000-deep map), so a plant
        // whose foot is under 2 * LayerTie / row of a cell north of a Building-layer thing is the only pair it turns.
        public const float LayerTie = 0.00004f;

        /// <summary>0 at the map's north edge, 1 at its south edge.</summary>
        public static float Southness(float z, int mapSizeZ)
        {
            float t = (z + 1f) / (mapSizeZ + 2f);
            if (t < 0f) t = 0f;
            else if (t > 1f) t = 1f;
            return 1f - t;
        }

        /// <summary>Replaces vanilla's SeededYOffset: where the pawn stands, plus a lift while it flies.</summary>
        public static float PawnYOffset(float z, int mapSizeZ, float flightFactor)
        {
            if (flightFactor < 0f) flightFactor = 0f;
            else if (flightFactor > 1f) flightFactor = 1f;
            return PawnFloor + PawnBand * Southness(z, mapSizeZ) + PawnBand * flightFactor;
        }

        /// <summary>Lift above a printed thing's layer altitude.</summary>
        public static float PrintOffset(float footZ, int mapSizeZ)
        {
            return PrintBand * Southness(footZ, mapSizeZ);
        }

        /// <summary>Vanilla's Altitudes.AltitudeFor: layer i sits at i * LayerSpacing (Altitudes.cs:25).</summary>
        public static float LayerAltitude(int layer)
        {
            return layer * LayerSpacing;
        }

        /// <summary>Does the rule order this printed or drawn thing? Plants on LowPlant..BuildingOnTop, everything else
        /// on Building..BuildingOnTop. (Pawns have their own path; layers outside these keep vanilla's altitude.)</summary>
        public static bool Orders(bool isPlant, int layer)
        {
            return layer >= (isPlant ? PlantMinLayer : BuildingMinLayer) && layer <= CommonLayer;
        }

        /// <summary>How much higher one row further south prints: PrintBand spread over the map's rows.</summary>
        public static float RowStep(int mapSizeZ)
        {
            return PrintBand / (mapSizeZ + 2f);
        }

        /// <summary>The altitude a plant quad prints at: the common layer, lifted by its own foot.</summary>
        public static float PlantAltitude(float foot, int mapSizeZ)
        {
            return LayerAltitude(CommonLayer) + PrintOffset(foot, mapSizeZ);
        }

        /// <summary>The altitude a non-plant thing on Building..BuildingOnTop prints and draws at, from its donor
        /// layer and its footprint's south row (OccupiedRect().minZ). Every such thing joins the common layer, as plants do,
        /// so a building south of a mast, a tree or another building draws in front of it whatever its own layer and however
        /// far north its picture reaches (RIMMANDRAKE_ORDER_SLACK_MAST_BEHIND_TALL_SOUTHERN_PICTURES); its donor layer only
        /// breaks the tie inside one row.</summary>
        public static float BuildingAltitude(int layer, int footMinZ, int mapSizeZ)
        {
            return LayerAltitude(CommonLayer) + PrintOffset(footMinZ, mapSizeZ) - (CommonLayer - layer) * LayerTie;
        }

        /// <summary>What every quad and every real-time part of such a thing gets added to its vanilla altitude: one
        /// number per thing, so its own parts keep vanilla's order among themselves.</summary>
        public static float BuildingLift(int layer, int footMinZ, int mapSizeZ)
        {
            return BuildingAltitude(layer, footMinZ, mapSizeZ) - LayerAltitude(layer);
        }

        /// <summary>The foot of a printed plant quad: where Plant.Print plants the bottom of the plant
        /// (center.z - visualSize/2, with visualSize = quad side / drawSize.x).</summary>
        public static float PlantFoot(float centerZ, float quadSide, float drawSizeX)
        {
            return centerZ - 0.5f * quadSide / (drawSizeX > 0.01f ? drawSizeX : 1f);
        }
    }
}
