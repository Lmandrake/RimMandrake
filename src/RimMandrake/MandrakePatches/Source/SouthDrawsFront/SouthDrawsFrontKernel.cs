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
        // did in our biomes since 2026-10-16; buildings on Building..BuildingOnTop keep their own layer.
        public const int PlantMinLayer = 11;     // AltitudeLayer.LowPlant
        public const int CommonLayer = 17;       // AltitudeLayer.BuildingOnTop
        public const int BuildingMinLayer = 15;  // AltitudeLayer.Building
        public const float PrintBand = 0.30f;    // of the 0.366 to the next layer; an overlay's +AltInc still fits
        public const float MaxCarriedOffset = 0.01f;   // vanilla's snow-overlay lift (0.000366) rides along; more is foreign

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

        /// <summary>The foot of a printed plant quad: where Plant.Print plants the bottom of the plant
        /// (center.z - visualSize/2, with visualSize = quad side / drawSize.x).</summary>
        public static float PlantFoot(float centerZ, float quadSide, float drawSizeX)
        {
            return centerZ - 0.5f * quadSide / (drawSizeX > 0.01f ? drawSizeX : 1f);
        }
    }
}
