// RIMMANDRAKE_LET_PAWN_WALK_UNDER_PLANK_COVER_BRIDGES_ALREADY_ALLOW_IT (owner, station 45, 2026-11-22: "She should be able to
// walk beneath it.") and RIMMANDRAKE_FADE_EVERY_PIT_COVER_TRANSPARENT_OVER_A_PAWN_LIGHTEN_PLEASED_HIM ("transparent rather than
// merely lightened ... applied to any covering that a pit can have, bridge, planks, hidden"). Offline sweeps on the shipped
// pure rules (RM_SpanMath.PassesUnder, RM_SuspensionMath.StepGoesUnder/BandExitIsFloorWalk, RM_PocketGridMath.ViewDepth and
// UsesFloorView, RM_PitTrapMath.StepAllowed/ArrivalDropsTooFar, RM_CoverFadeMath) over the whole range the game can produce:
// span kind and deck height, floor 0..16 notches, the walker's stand depth 0..16 and climb limit 1..6, the deepest passing deck
// on the map (-1 none, 0..6), the walk-under setting. Each prints its case count, its worst value and its limit.
// NOT proven here: the live look (the faded print, the pawn shown through it) - stage-6 sc_covered_pit / sc_hung_bridge, owed live.
using System;
using System.IO;
using RimMandrake.FlowWorks.Pits;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class CoverUnderFadeChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static void Report(string name, int cases, int failures, string worst, string limit)
        {
            Console.WriteLine("      " + name + ": cases=" + cases + " failures=" + failures + " worst=" + (worst ?? "none") + " limit=" + limit);
        }

        public static void Run(Action<string, Action> Case)
        {
            // The clearance a span needs before the floor band passes under it: the bar of design §2 rule 1 (owner Q2: 2 m).
            const int Clear = RM_SpanMath.UnderpassClearanceNotches;

            Case("CoverUnder_every_cover_passes_like_a_bridge", () =>
            {
                int cases = 0, fails = 0;
                string worst = null;
                foreach (bool on in new[] { false, true })
                {
                    for (int floor = 0; floor <= 16; floor++)
                    {
                        for (int deck = 0; deck <= 6; deck++)
                        {
                            bool want = on && floor - deck >= Clear;
                            bool bridge = RM_SpanMath.PassesUnder(RM_SpanMath.SpanKind.SuspensionDeck, on, floor, deck);
                            cases++;
                            if (bridge != want) { fails++; worst = worst ?? ("bridge on=" + on + " floor=" + floor + " deck=" + deck); }
                            if (deck != 0)
                            {
                                continue;   // a pit cover is always at the surface
                            }
                            bool cover = RM_SpanMath.PassesUnder(RM_SpanMath.SpanKind.PitCover, on, floor, 0);
                            bool read = RM_SpanMath.CoverRead(floor, on).FloorBandPassesUnder;
                            cases++;
                            if (cover != want || read != want || RM_SpanMath.WalkingDepth(floor, RM_SpanMath.CoverRead(floor, on)) != 0)
                            {
                                fails++;
                                worst = worst ?? ("cover on=" + on + " floor=" + floor + " passes=" + cover + " want=" + want);
                            }
                        }
                    }
                }
                Report("CoverUnder_every_cover_passes_like_a_bridge", cases, fails, worst, "passes iff setting on and floor-deck>=" + Clear + " notches, cover walk depth 0");
                Assert(fails == 0, "can-fail: a pit cover passes under exactly as a bridge at the surface does (" + worst + ")");
            });

            Case("CoverUnder_pit_pawn_steps_in_and_goes_under", () =>
            {
                // A pawn down in a pit or canal (stand depth d > K, so it cannot climb out) beside an intact cover whose pit floor
                // f it can step to (|f - d| <= K): the floor view reads the cover square at f, the step is allowed and it goes under.
                int cases = 0, fails = 0;
                string worst = null;
                for (int k = 1; k <= 6; k++)
                {
                    for (int d = k + 1; d <= 16; d++)
                    {
                        for (int f = Clear; f <= 16; f++)
                        {
                            if (Math.Abs(f - d) > k)
                            {
                                continue;
                            }
                            for (int deepest = -1; deepest <= 0; deepest++)   // covers only (0), or none counted (-1, the parent's scan)
                            {
                                bool passes = RM_SpanMath.PassesUnder(RM_SpanMath.SpanKind.PitCover, true, f, 0);
                                int deepestSeen = passes ? Math.Max(deepest, 0) : deepest;
                                bool floorView = RM_PocketGridMath.UsesFloorView(true, false, false, d, deepestSeen);
                                int toView = RM_PocketGridMath.ViewDepth(f, true, 0, passes, floorView);
                                bool allowed = RM_PitTrapMath.StepAllowed(d, toView, k);
                                bool under = RM_SuspensionMath.StepGoesUnder(passes, 0, f, k, false, false, d);
                                cases++;
                                if (!allowed || !under)
                                {
                                    fails++;
                                    worst = worst ?? ("K=" + k + " d=" + d + " floor=" + f + " view=" + toView + " allowed=" + allowed + " under=" + under);
                                }
                            }
                        }
                    }
                }
                Report("CoverUnder_pit_pawn_steps_in_and_goes_under", cases, fails, worst, "every pit pawn within climb of the cover's floor walks under it");
                Assert(cases > 0 && fails == 0, "can-fail: a pawn in the pit walks under the cover (" + worst + ")");
            });

            Case("CoverUnder_no_walk_drops_anyone_into_the_hole", () =>
            {
                // Owner ruling: "You can't fall in by careless colonist pathing." Any step the walk allows (the step allowed in the
                // view this pawn plans on) that ends UNDER a span must reach the floor within the walker's climb; a pawn at ground
                // never goes under. Swept over bridges (deck 0..6) and covers (0), the map's deepest passing deck, the setting.
                int cases = 0, fails = 0, groundUnder = 0, worstDrop = 0;
                string worst = null;
                foreach (bool cover in new[] { false, true })
                {
                    for (int deck = 0; deck <= (cover ? 0 : 6); deck++)
                    {
                        for (int f = 0; f <= 16; f++)
                        {
                            bool passes = RM_SpanMath.PassesUnder(cover ? RM_SpanMath.SpanKind.PitCover : RM_SpanMath.SpanKind.SuspensionDeck, true, f, deck);
                            for (int deepest = -1; deepest <= 6; deepest++)
                            {
                                int deepestSeen = passes ? Math.Max(deepest, deck) : deepest;
                                for (int k = 1; k <= 6; k++)
                                {
                                    for (int d = 0; d <= 16; d++)
                                    {
                                        bool floorView = RM_PocketGridMath.UsesFloorView(true, false, false, d, deepestSeen);
                                        int toView = RM_PocketGridMath.ViewDepth(f, true, deck, passes, floorView);
                                        if (!RM_PitTrapMath.StepAllowed(d, toView, k))
                                        {
                                            continue;
                                        }
                                        bool under = RM_SuspensionMath.StepGoesUnder(passes, deck, f, k, false, false, d);
                                        cases++;
                                        int drop = Math.Abs(f - d);
                                        if (under && d == 0)
                                        {
                                            groundUnder++;
                                        }
                                        if (under && drop > k)
                                        {
                                            fails++;
                                            if (drop - k > worstDrop)
                                            {
                                                worstDrop = drop - k;
                                                worst = (cover ? "cover" : "bridge") + " deck=" + deck + " floor=" + f + " deepest=" + deepest + " K=" + k + " d=" + d;
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                Report("CoverUnder_no_walk_drops_anyone_into_the_hole", cases, fails, worst == null ? null : worst + " (over K by " + worstDrop + ")",
                    "0 walked steps go under with |floor-d|>K; 0 ground pawns go under (got " + groundUnder + ")");
                Assert(cases > 0 && fails == 0 && groundUnder == 0, "can-fail: a walked step goes under a span into a drop beyond the climb (" + worst + ")");
            });

            Case("CoverUnder_walking_out_from_under_is_no_second_fall", () =>
            {
                // A pawn in the floor band walks out from under a span onto an open square: a walk along the floor, judged at
                // the floor, not an arrival from the span's walking height (which read every pit prisoner leaving from under a
                // lid as a fresh fall onto the spikes). A real drop beyond the natural climb is still judged.
                int cases = 0, fails = 0;
                string worst = null;
                for (int k = 1; k <= 4; k++)
                {
                    for (int from = Clear; from <= 16; from++)
                    {
                        for (int to = 0; to <= 16; to++)
                        {
                            bool floorWalk = RM_SuspensionMath.BandExitIsFloorWalk(true, false, from, to, k);
                            bool want = !RM_PitTrapMath.ArrivalDropsTooFar(from, to, k);
                            cases++;
                            if (floorWalk != want) { fails++; worst = worst ?? ("K=" + k + " floor=" + from + " to=" + to + " got=" + floorWalk); }
                            cases++;
                            if (RM_SuspensionMath.BandExitIsFloorWalk(false, false, from, to, k) || RM_SuspensionMath.BandExitIsFloorWalk(true, true, from, to, k))
                            {
                                fails++;
                                worst = worst ?? ("not a band exit read as one: floor=" + from + " to=" + to);
                            }
                        }
                    }
                }
                Report("CoverUnder_walking_out_from_under_is_no_second_fall", cases, fails, worst, "floor walk iff in band, not under at to, to-floor<=max(1,K)");
                Assert(fails == 0, "can-fail: walking out from under a span is judged from the floor (" + worst + ")");
            });

            Case("CoverUnder_production_reads_the_rules", () =>
            {
                string cover = Src("Pits", "Building_PitCover.cs");
                string deck = Src("Pits", "Suspension", "Building_SuspensionDeck.cs");
                string under = Src("Pits", "Suspension", "RM_SuspensionPatches.cs");
                string beneath = Src("Pits", "RM_PitCoverBeneath.cs");
                Assert(cover.Contains("override bool FloorBandPassesUnder") && cover.Contains("RM_SpanMath.PassesUnder(RM_SpanMath.SpanKind.PitCover"),
                    "can-fail: a pit cover's floor band flag reads RM_SpanMath.PassesUnder");
                Assert(deck.Contains("RM_SpanMath.PassesUnder(RM_SpanMath.SpanKind.SuspensionDeck"), "can-fail: a bridge reads the same rule");
                Assert(under.Contains("public static Building_SpanDeck PassingDeckAt") && under.Contains("RM_PitCoverUtility.CoverAt(map, c)"),
                    "can-fail: the passing deck lookup finds a cover the floor band passes under");
                Assert(under.Contains("things[i] is Building_SpanDeck d && d.Decked && d.FloorBandPassesUnder"),
                    "can-fail: the deepest passing deck (the floor view switch) counts covers");
                Assert(under.Contains("RM_SuspensionMath.StepGoesUnder(true, dTo.DeckNotches, floorTo, k,")
                    && under.Contains("RM_SuspensionMath.StepGoesUnder(true, dTo.DeckNotches, floorTo, k, fromDecked, fromBand, fromWalk)"),
                    "can-fail: the step decision reads the guarded rule (floor and climb limit)");
                Assert(under.Contains("RM_SuspensionMath.BandExitIsFloorWalk(") && under.Contains("NoteHandledArrival(p, to)"),
                    "can-fail: a walk out from under is noted as a floor walk for the fall detector");
                Assert(beneath.Contains("SetBand(p, true)"), "can-fail: a lid laid over a pit pawn puts it in the floor band when it passes under");
                int riders = cover.IndexOf("!RM_SuspensionUnderpass.InFloorBand(p))", StringComparison.Ordinal);
                Assert(riders >= 0 && cover.IndexOf("!RM_SuspensionUnderpass.InFloorBand(p))", riders + 1, StringComparison.Ordinal) > riders,
                    "can-fail: a cover breaking or blasted drops only those ON it, never those under it (DeSpawn and the blast)");
            });

            Case("CoverFade_every_covering_turns_transparent_over_a_pawn", () =>
            {
                int cases = 0, fails = 0;
                string worst = null;
                foreach (RM_CoverFadeMath.SpanLook kind in (RM_CoverFadeMath.SpanLook[])Enum.GetValues(typeof(RM_CoverFadeMath.SpanLook)))
                {
                    RM_CoverFadeMath.Look on = RM_CoverFadeMath.For(kind, true);
                    RM_CoverFadeMath.Look off = RM_CoverFadeMath.For(kind, false);
                    cases += 2;
                    if (!on.PrintSuppressed || Math.Abs(on.OverAlpha - RM_CoverFadeMath.UnderAlpha) > 1e-6f || !on.PawnDrawn)
                    {
                        fails++;
                        worst = worst ?? (kind + " beneath: suppressed=" + on.PrintSuppressed + " alpha=" + on.OverAlpha + " pawnDrawn=" + on.PawnDrawn);
                    }
                    if (off.PrintSuppressed || off.OverAlpha != 0f || !off.PawnDrawn)
                    {
                        fails++;
                        worst = worst ?? (kind + " nobody: suppressed=" + off.PrintSuppressed + " alpha=" + off.OverAlpha);
                    }
                }
                Report("CoverFade_every_covering_turns_transparent_over_a_pawn", cases, fails, worst, "beneath: print held back, alpha " + RM_CoverFadeMath.UnderAlpha + ", pawn drawn; nobody: opaque print");
                Assert(cases == 6 && fails == 0, "can-fail: every covering is transparent over a pawn beneath it (" + worst + ")");
            });

            Case("CoverFade_lip_sees_through_a_faded_lid", () =>
            {
                int cases = 0, fails = 0;
                string worst = null;
                for (int h = 0; h <= 16; h++)
                {
                    foreach (bool lid in new[] { false, true })
                    {
                        foreach (bool faded in new[] { false, true })
                        {
                            int want = h > 0 && lid && !faded ? 0 : h;
                            int got = RM_CoverFadeMath.SeenDepth(h, lid, faded, 0);
                            cases++;
                            if (got != want) { fails++; worst = worst ?? ("hollow=" + h + " lid=" + lid + " faded=" + faded + " got=" + got); }
                        }
                    }
                }
                Report("CoverFade_lip_sees_through_a_faded_lid", cases, fails, worst, "faded lid shows the hollow, intact lid ground");
                Assert(fails == 0, "can-fail: a lid with someone beneath does not occlude its own square (" + worst + ")");
            });

            Case("CoverFade_production_reads_the_look", () =>
            {
                string cover = Src("Pits", "Building_PitCover.cs");
                string deck = Src("Pits", "Suspension", "Building_SuspensionDeck.cs");
                string comp = Src("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs");
                string under = Src("Pits", "Suspension", "RM_SuspensionPatches.cs");
                string beneath = Src("Pits", "RM_PitCoverBeneath.cs");
                string lip = Src("Superdeep", "RM_PitLipOcclusion.cs");
                Assert(cover.Contains("RM_MapComponent_SuspensionBridges.FadedAt(map, Position)") && deck.Contains("RM_MapComponent_SuspensionBridges.FadedAt(map, Position)"),
                    "can-fail: a cover's and a bridge's print hold back a faded square");
                Assert(comp.Contains("RM_CoverFadeMath.For(") && comp.Contains("FadeMaterial(out float angle)"), "can-fail: the fade pass draws every covering kind from the look");
                Assert(comp.Contains("UnderFade = RM_CoverFadeMath.UnderAlpha"), "can-fail: the bridge fade the owner liked (0.6) is the one alpha every covering uses");
                Assert(under.Contains("RM_CoverFadeMath.SeenDepth("), "can-fail: the pit lip search reads the faded lid as open");
                Assert(!beneath.Contains("RM_Patch_PawnBeneathCoverHidden") && !beneath.Contains("RM_Patch_PawnBeneathCoverNoLabel"),
                    "can-fail: a pawn beneath a lid is drawn (shown through the faded lid), not hidden");
                Assert(!lip.Contains("Pits.RM_PitCoverBeneath.IsBeneath(p))"), "can-fail: the lip occluder treats a pawn beneath a lid like any pit pawn");
            });

            // The faded square must show the picture its Print would have drawn: a laid raid plank prints its own plank pieces
            // and a bridge with picked art prints its strip piece BEFORE the linked tile, so the fade picks its material through
            // the same choosers, in the same order (else a pawn under a raid plank or a picked-art bridge sees the wrong deck).
            Case("CoverFade_deck_fades_in_the_art_it_prints", () =>
            {
                string deck = Src("Pits", "Suspension", "Building_SuspensionDeck.cs");
                string art = Src("Pits", "Suspension", "RM_DeckArt.cs");
                string plank = Src("Pits", "Drawbridge", "RM_DrawbridgeArt.cs");
                int fm = deck.IndexOf("public override Material FadeMaterial(out float angle)");
                Assert(fm >= 0, "can-fail: the bridge deck names its fade material");
                int end = deck.IndexOf("/// <summary>", fm, StringComparison.Ordinal);   // the next member's doc ends the body
                string body = end > fm ? deck.Substring(fm, end - fm) : "";
                int a = body.IndexOf("RM_DrawbridgeArt.RaidPlankMat(this, r, out angle)", StringComparison.Ordinal);
                int b = body.IndexOf("RM_DeckArt.DeckMat(this, r, out angle)", StringComparison.Ordinal);
                int c = body.IndexOf("RM_SuspensionDeckLink.TileFor(this, out angle)", StringComparison.Ordinal);
                Console.WriteLine($"    fade chooser order raidPlank={a} deckArt={b} linked={c} (want 0 <= raidPlank < deckArt < linked)");
                Assert(a >= 0 && b > a && c > b, "can-fail: the fade tries raid plank art, then picked deck art, then the linked tile, as Print does");
                Assert(plank.Contains("Material mat = RaidPlankMat(deck, r, out float angle);"), "can-fail: PrintRaidPlank draws the chooser's material");
                Assert(art.Contains("Material m = DeckMat(deck, r, out float angle);"), "can-fail: PrintDeck draws the chooser's material");
            });
        }
    }
}
