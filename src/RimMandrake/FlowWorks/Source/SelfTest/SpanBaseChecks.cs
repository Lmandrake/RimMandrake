// SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT (stage S0, design/RimMandrake/flowworks_bridges_design_2026-10-17.md): the span
// base lifted out of Building_PitCover, no behaviour change. Offline checks on the production deck read (RM_SpanMath) and
// the production call sites: a cover reads decked / height 0 / floor band by the shared rule (owner 2026-11-22), an open dug cell reads the floor, the
// cover inherits the base's defaults, and every height-dependent "is it covered" site reads RM_SpanUtility. Each case has
// a can-fail. NOT proven here: a cover still holding 40/120/220 kg and dropping a pawn in a live game (L2, owed).
using System;
using System.IO;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class SpanBaseChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        public static void Run(Action<string, Action> Case)
        {
            Case("SpanBase_cover_read_is_decked_surface_no_underpass", () =>
            {
                RM_SpanMath.DeckRead c = RM_SpanMath.CoverRead(8, true);
                // RIMMANDRAKE_LET_PAWN_WALK_UNDER_PLANK_COVER_BRIDGES_ALREADY_ALLOW_IT supersedes "nothing passing under" (owner
                // 2026-11-22: "She should be able to walk beneath it."): the floor band passes under a cover as under a bridge.
                Assert(c.Decked && c.DeckHeightM == 0f && c.DeckNotches == 0 && c.FloorBandPassesUnder,
                    "a cover reads decked, at the surface, the floor band passing under it (8 notches, walk-under on)");
                Assert(!RM_SpanMath.CoverRead(8, false).FloorBandPassesUnder && !RM_SpanMath.CoverRead(3, true).FloorBandPassesUnder
                    && RM_SpanMath.CoverRead(4, true).FloorBandPassesUnder,
                    "can-fail: nothing passes under a cover with walk-under off or under 2 m (4 notches) of floor");
                Assert(RM_SpanMath.WalkingDepth(4, c) == 0 && RM_SpanMath.WalkingDepth(16, c) == 0, "a covered pit is ground at any depth");
                RM_SpanMath.DeckRead open = RM_SpanMath.DeckRead.None;
                Assert(!open.Decked && RM_SpanMath.WalkingDepth(4, open) == 4 && RM_SpanMath.WalkingDepth(0, open) == 0,
                    "an open dug cell is not decked and reads its own floor");
                // can-fail: a deck that is not at the surface reads its own height, never deeper than the floor
                RM_SpanMath.DeckRead sunk = new RM_SpanMath.DeckRead(true, 2f, true);
                Assert(RM_SpanMath.WalkingDepth(14, sunk) == 4 && sunk.FloorBandPassesUnder, "a 2 m deck over 7 m reads 4 notches");
                Assert(RM_SpanMath.WalkingDepth(2, new RM_SpanMath.DeckRead(true, 3f, false)) == 2, "a deck never reads deeper than its floor");
                RM_SpanMath.DeckRead none = new RM_SpanMath.DeckRead(false, 3f, true);
                Assert(none.DeckHeightM == 0f && !none.FloorBandPassesUnder, "a read that is not decked carries no height or underpass");
            });

            Case("SpanBase_drop_and_underpass_rules", () =>
            {
                Assert(RM_SpanMath.Notches(0.5f) == 1 && RM_SpanMath.Notches(2f) == 4 && RM_SpanMath.Notches(-1f) == 0, "metres to notches");
                Assert(RM_SpanMath.HasDrop(1, 0) && !RM_SpanMath.HasDrop(0, 0) && !RM_SpanMath.HasDrop(8, 8), "a span needs 0.5 m of drop");
                Assert(RM_SpanMath.ClearsUnderpass(4, 0) && !RM_SpanMath.ClearsUnderpass(3, 0) && RM_SpanMath.ClearsUnderpass(14, 8)
                    && !RM_SpanMath.ClearsUnderpass(11, 8), "pawns pass under at 2 m of clearance, not less");
            });

            Case("SpanBase_cover_is_the_trap_tier_of_the_base", () =>
            {
                string cover = Src("Pits", "Building_PitCover.cs");
                Assert(cover.Contains("public class Building_PitCover : Building_SpanDeck, IPitCoverHost"), "a cover is a span deck");
                Assert(!cover.Contains("override float DeckHeightM") && !cover.Contains("override bool Grated"),
                    "can-fail: a cover keeps the base's surface / solid defaults");
                // owner 2026-11-22 "She should be able to walk beneath it.": the cover's underpass is the one rule every span shares
                Assert(cover.Contains("public override bool FloorBandPassesUnder")
                    && cover.Contains("RM_SpanMath.PassesUnder(RM_SpanMath.SpanKind.PitCover, RM_SuspensionSettings.suspensionWalkUnder,"),
                    "can-fail: a cover lets the floor band under by the shared span rule (setting + 2 m clearance)");
                Assert(cover.Contains("protected override string CollapseSaveKey => \"rmCoverSprung\";"), "old saves keep their sprung flag");
                // FLOWWORKS_PITCOVER_FIX_BURNS_PAWN_UNHARMED: a killed (not deconstructed) cover drops its riders through the trap
                Assert(cover.Contains("public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)")
                    && cover.Contains("(mode == DestroyMode.KillFinalize || mode == DestroyMode.KillFinalizeLeavingsOnly")
                    && cover.Contains("RM_SuperdeepTrap.OnForcedDescent(p, pos, state);"), "a cover destroyed by damage drops whoever stood on it");
                Assert(cover.IndexOf("riders = new List<Pawn>()") < cover.IndexOf("base.DeSpawn(mode);", cover.IndexOf("class Building_PitCover")),
                    "riders are read while the cover is still spawned (after DeSpawn its cell is empty of it)");
                // PIT_COVER_BUILD_DECONSTRUCT_DROPS_TOO (owner card 2026-10-20): deconstructing a cover drops its riders too
                Assert(cover.Contains("|| mode == DestroyMode.Deconstruct)"), "a deconstructed cover drops whoever stood on it, as a destroyed one does");
                Assert(cover.Contains("return RM_SpanUtility.DeckedAt(map, c);"), "IsCovered is the span read (any deck, height ignored)");
                string b = Src("Pits", "Building_SpanDeck.cs");
                Assert(b.Contains("public virtual float DeckHeightM => 0f;") && b.Contains("public virtual bool FloorBandPassesUnder => false;"),
                    "the base defaults are the surface and no underpass");
                Assert(b.Contains("new RM_SpanMath.DeckRead(true, DeckHeightM, FloorBandPassesUnder)"), "the read carries the deck's own height and flag");
                string trig = Src("Pits", "Trigger", "CompPitCoverTrigger.cs");
                Assert(trig.Contains("RM_SpanUtility.LoadOn(map, cells, parent.Faction, RimMandrakeFlowWorksSettings.superdeepCapturesOwnFaction, onCover)"),
                    "the trap trigger sums the span's load, own faction by the setting");
            });

            Case("SpanBase_height_sites_read_DeckedAt", () =>
            {
                string[][] sites =
                {
                    new[] { "Superdeep", "RM_PitStepCost.cs" },
                    new[] { "RM_Patch_SuperdeepShooting.cs" },
                    new[] { "Superdeep", "RM_PitRooms.cs" },       // exposure and liquid fire read IsPitFloor here
                    new[] { "RM_PitFillEffects.cs" },
                    new[] { "RM_SlimeSlip.cs" },
                    new[] { "Superdeep", "RM_PocketGrid.cs" },
                };
                foreach (string[] site in sites)
                {
                    string s = Src(site);
                    string name = Path.Combine(site);
                    Assert(s.Contains("RM_SpanUtility.") || s.Contains("Building_SpanDeck"), name + " reads the span deck");
                    Assert(!s.Contains("RM_PitCoverUtility.IsCovered("), "can-fail: " + name + " still asks 'is it covered'");
                }
                Assert(Src("RM_Patch_SuperdeepShooting.cs").Contains("return Pits.RM_SpanUtility.WalkingDepth(map, c, d);"), "a shot reads the walking depth");
                Assert(Src("Superdeep", "RM_PocketGrid.cs").Contains("depth[idx] = (byte)RM_SpanMath.WalkingDepth(depth[idx], c.Read);"),
                    "the pocket grid reads a deck at its walking height");
            });
        }
    }
}
