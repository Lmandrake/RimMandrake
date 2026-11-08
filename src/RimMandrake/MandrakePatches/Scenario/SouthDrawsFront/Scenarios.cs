// Literal scenarios for "if you are more south, you go in front" (owner 2026-10-16, 2026-11-08) at the pawn caller.
// Larger y = nearer the camera = in front. A render node adds layer * 0.000366 to its pawn's y (PawnRenderUtility.cs:334).
using System;
using RimMandrake.Patches;
using Verse;

public static class Scenarios
{
    const float Node = 0.0003658537f;
    const float Layer = 0.36585367f;
    const float AltInc = 0.03658537f;
    static int failed, passed;

    static void Check(string scenario, bool ok, string detail)
    {
        Console.WriteLine((ok ? "PASS: " : "FAIL: ") + scenario + (ok ? "" : "  " + detail));
        if (ok) passed++; else failed++;
    }

    // Is a's body (node layer bodyLayer) drawn over b's node on layer bLayer where they overlap?
    static bool InFront(Pawn a, float aLayer, Pawn b, float bLayer) => a.Drawer.DrawPosY + aLayer * Node > b.Drawer.DrawPosY + bLayer * Node;

    public static int Main()
    {
        var map = new Map(250);
        RM_PatchesSettings.southDrawsFront = true;

        // The reported case: two Dalgo mares one cell apart, the northern one holding the larger thing-id seed.
        var southMare = new Pawn("south mare", map, 100.5f, 120.5f, -AltInc * 0.8f);
        var northMare = new Pawn("north mare", map, 100.5f, 121.5f, +AltInc * 0.8f);
        Check("two Dalgo mares a cell apart: the southern mare's body covers the northern mare's body",
            InFront(southMare, 0, northMare, 0), southMare.Drawer.DrawPosY + " vs " + northMare.Drawer.DrawPosY);
        Check("... and covers the northern mare's wound overlay (layer 1) too", InFront(southMare, 0, northMare, 1), "");

        RM_PatchesSettings.southDrawsFront = false;
        Check("setting off: vanilla's seed decides, and the northern mare draws over the southern one (the bug)",
            InFront(northMare, 0, southMare, 0), "");
        RM_PatchesSettings.southDrawsFront = true;

        // Walking: tweened positions a third of a cell apart, seeds the wrong way round.
        var walker = new Pawn("walking mare", map, 50.2f, 60.30f, -AltInc);
        var behind = new Pawn("mare just behind", map, 50.9f, 60.63f, AltInc);
        Check("two mares mid-stride a third of a cell apart: the southern one is in front", InFront(walker, 0, behind, 0), "");

        // A herd: five big animals in a column, every southern one over every northern one.
        bool herd = true;
        var column = new Pawn[5];
        for (int i = 0; i < 5; i++)
            column[i] = new Pawn("herd " + i, map, 30.5f, 200.5f + i * 0.8f, (i % 2 == 0 ? 1 : -1) * AltInc * 0.9f);
        for (int i = 0; i < 5; i++)
            for (int j = i + 1; j < 5; j++)
                herd &= InFront(column[i], 0, column[j], 0);
        Check("a column of five big animals 0.8 cells apart: each one covers everyone north of it", herd, "");

        // Not on a map (carried, in a caravan): vanilla.
        var carried = new Pawn("carried pawn", null, 0f, 0f, 0.012f);
        Check("a pawn on no map keeps vanilla's seeded offset",
            Math.Abs(carried.Drawer.DrawPosY - (Pawn.PawnLayerAltitude + 0.012f)) < 1e-6f, carried.Drawer.DrawPosY.ToString());

        // A bird in full flight standing (by its ground position) north of a mare: it is in the air, so in front.
        var bird = new Pawn("flying bird", map, 100.5f, 125.5f, 0f) { flight = new RimWorld.Pawn_FlightTracker { Flying = true, PositionOffsetFactor = 1f } };
        Check("a bird in full flight north of a mare draws over the mare", InFront(bird, 0, southMare, 90), "");
        var landed = new Pawn("landed bird", map, 100.5f, 125.5f, 0f) { flight = new RimWorld.Pawn_FlightTracker { Flying = false, PositionOffsetFactor = 0f } };
        Check("the same bird landed is ordered like any pawn: behind the southern mare", InFront(southMare, 0, landed, 0), "");

        // Bounds: the southernmost ground pawn's top node stays under PawnUnused; a flyer there under PawnState.
        var edge = new Pawn("pawn at the south edge", map, 1f, 0f, 0f);
        Check("the southernmost pawn's highest node stays under the next layer",
            edge.Drawer.DrawPosY + 100 * Node < Pawn.PawnLayerAltitude + Layer, edge.Drawer.DrawPosY.ToString());
        var edgeFly = new Pawn("flyer at the south edge", map, 1f, 0f, 0f) { flight = new RimWorld.Pawn_FlightTracker { Flying = true, PositionOffsetFactor = 1f } };
        Check("a flyer at the south edge stays under PawnState",
            edgeFly.Drawer.DrawPosY + 100 * Node < Pawn.PawnLayerAltitude + 2 * Layer, edgeFly.Drawer.DrawPosY.ToString());
        var northEdge = new Pawn("pawn at the north edge", map, 1f, 249.5f, 0f);
        Check("the northernmost pawn draws no lower than vanilla's lowest seed",
            northEdge.Drawer.DrawPosY >= Pawn.PawnLayerAltitude - AltInc - 1e-6f, northEdge.Drawer.DrawPosY.ToString());

        Console.WriteLine(failed == 0 ? "PASS: " + passed + " scenarios" : "FAIL: " + failed + " of " + (passed + failed) + " scenarios");
        return failed == 0 ? 0 : 1;
    }
}
