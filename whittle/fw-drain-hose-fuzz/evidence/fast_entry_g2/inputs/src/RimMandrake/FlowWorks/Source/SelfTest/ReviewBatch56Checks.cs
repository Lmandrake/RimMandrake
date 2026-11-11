// FlowWorks code-review batches 5 and 6 (2026-10-11): offline guards for the behaviour fixes. Each case reads the
// PRODUCTION source (whitespace collapsed, RiverSwitchFlipChecks.Src) and requires the fixed shape, so a revert fails here.
// Where the fix rests on a Verse-free rule (RM_PlacerMath) the rule is exercised too.
// NOT proven here: anything a live map decides (a pawn actually pathing round a burning cover, a projectile's
// launch origin in game, a frame's occlusion). Those stay live checks.
using System;
using System.IO;
using System.Xml.Linq;
using RimMandrake.FlowWorks.Quarry;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class ReviewBatch56Checks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        /// <summary>The text from <paramref name="start"/> up to the next <paramref name="end"/> after it.</summary>
        private static string Between(string src, string start, string end)
        {
            int i = src.IndexOf(start, StringComparison.Ordinal);
            Assert(i >= 0, "marker present: " + start);
            int j = src.IndexOf(end, i + start.Length, StringComparison.Ordinal);
            return j < 0 ? src.Substring(i) : src.Substring(i, j - i);
        }

        private static int At(string src, string what)
        {
            int i = src.IndexOf(what, StringComparison.Ordinal);
            Assert(i >= 0, "present: " + what);
            return i;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("TankSearch_refusal_only_from_usable_tanks", () =>
            {
                string s = Src("LiquidTypes", "RM_LiquidTankUtility.cs");
                string body = Between(s, "private static bool TryFindTank(", "tank = best;");
                Assert(At(body, "CanReach(candidate") < At(body, "predicate(candidate)"),
                    "the refusal-recording predicate runs after the forbidden/reserve/range/reach filters");
                Assert(At(body, "IsForbidden(pawn)") < At(body, "predicate(candidate)"), "forbidden tanks never reach the predicate");
                Assert(!s.Contains("TryFindTankToDrain(Pawn pawn, RM_ContainerSize size"), "dead size-only drain overload removed");
                string b = Src("LiquidTypes", "RM_LiquidBottleUtility.cs");
                Assert(!b.Contains("TryFindFillCell(Pawn pawn, out IntVec3 cell"), "dead container-less fill overload removed");
            });
            Case("PitCover_path_cost_keeps_fire_snow_and_doors", () =>
            {
                string s = Between(Src("Pits", "Building_PitCover.cs"), "class RM_Patch_PathGrid_PitCoverCost", "class ZZZ_none");
                Assert(s.Contains("ref int? baseCostOverride"), "the cover's cost goes in as the base-cost override");
                Assert(s.Contains("baseCostOverride = Mathf.Max(cover.def.pathCost, 0)"), "override = cover pathCost");
                Assert(s.Contains("if (baseCostOverride.HasValue)"), "an override already set (water, pit step) is left alone");
                Assert(!s.Contains("__result ="), "can-fail: the total cost is never overwritten (fire/snow/door add-ons survive)");
            });
            Case("PlacerStock_cap_follows_the_setting_live", () =>
            {
                Assert(Math.Abs(RM_PlacerMath.StockCap(1000f, 2f) - 20f) < 1e-4f, "2% of 1000");
                Assert(Math.Abs(RM_PlacerMath.StockCap(1000f, 5f) - 50f) < 1e-4f, "can-fail: moving the slider moves the cap");
                Assert(RM_PlacerMath.Regrow(50f, 20f, 0) == 20f, "a lowered cap clamps the stock");
                string s = Src("Quarry", "RM_PlacerWorks.cs");
                Assert(s.Contains("CapNow => RM_PlacerMath.StockCap(units, RM_QuarrySettings.placerStockPercent)"),
                    "the cap is derived live from the saved base and the current setting");
                Assert(!s.Contains("Look(ref cap, \"RM_placerCap\"") && !s.Contains("Scribe_Values.Look(ref stockCap"),
                    "the cap itself is no longer saved (it froze the slider)");
                Assert(s.Contains("else if (stock > cap) { stock = cap;"),
                    "can-fail: Ensure clamps the stock to a lowered cap at once (not only at the next Regrow)");
                Assert(s.Contains("Scribe_Values.Look(ref units, \"RM_placerUnits\""), "the base is saved");
            });
            Case("PlacerStock_debited_only_after_placement", () =>
            {
                string s = Src("Quarry", "RM_PlacerWorks.cs");
                Assert(At(s, "TryPlaceThing(t, BankCell") < At(s, "stock.Take(got); stock.SluiceUnits += got;"),
                    "sluice: place first, then debit what was placed");
                Assert(At(s, "TryPlaceThing(t, pawn.Position") < At(s, "stock.Take(got); stock.PanUnits += got;"),
                    "pan: place first, then debit what was placed");
                Assert(!s.Contains("int got = stock?.Take(want)") && !s.Contains("int got = stock.Take(want)"),
                    "can-fail: no debit before placement");
            });
            Case("RiverCurrent_cheap_test_first_and_no_stack_on_stack", () =>
            {
                string s = Src("Rivers", "RM_MapComponent_RiverCurrent.cs");
                string scan = Between(s, "private void Scan()", "present.Add(t);");
                Assert(At(scan, "HasCurrent(t.Position)") < At(scan, "IsCarried(t)"), "the O(1) current test runs before IsCarried");
                string step = Between(s, "public void StepOne(Thing t)", "Move(t, next);");
                Assert(step.Contains("!(t is Pawn) && next.GetFirstItem(map) != null"),
                    "a drifting item never lands on a cell already holding an item");
            });
            Case("FerryPathProof_destroys_only_its_own_posts", () =>
            {
                string s = Src("Rivers", "RM_RiverWorksProofWorks.cs");
                string body = Between(s, "public static string ProofFerryPath(string arg)", "private static void DestroyIfSpawned");
                Assert(body.Contains("SpawnFerry(\"keep\", out Thing postA, out Thing postB)"), "the probe keeps hold of its two posts");
                Assert(body.Contains("DestroyIfSpawned(postA)") && body.Contains("DestroyIfSpawned(postB)"), "and removes exactly those");
                Assert(!body.Contains("ThingsOfDef(RM_RiverWorksDefOf.RM_FerryPost)"), "can-fail: never every ferry post on the map");
            });
            Case("FerryProof_searches_every_crossing_within_the_rope_span", () =>
            {
                // TESTENV_FERRY_ROPE_HARDEN_WIDE_RIVER_BANKS (r8): one line from the first weir site was the whole search
                string s = Src("Rivers", "RM_RiverWorksProofWorks.cs");
                string spawn = Between(s, "private static string SpawnFerry(string arg", "public static bool FindFerryCrossing(");
                Assert(spawn.Contains("FindFerryCrossing(map, comp, out IntVec3 water, out IntVec3 a, out IntVec3 b, out string why)"),
                    "the ferry probe asks the crossing search");
                Assert(!spawn.Contains("FindWeirSite("), "can-fail: never the first weir site's single line");
                Assert(spawn.Contains("\"FERRY paired=\" + paired + \" rope=\" + rope + \" ropeExempt=\" + ropeExempt"),
                    "what it measures is unchanged");
                string find = Between(s, "public static bool FindFerryCrossing(", "private static int WalkToBank(");
                Assert(find.Contains("foreach (IntVec3 c in map.AllCells)") && find.Contains("comp.FlowDirAt(c)"),
                    "every moving-water cell is a start");
                Assert(find.Contains("d > span") && find.Contains("RM_RiversSettings.ferryMaxSpan"),
                    "a crossing longer than the rope is not chosen (it could never pair)");
                Assert(find.Contains("tooWide=") && find.Contains("blockedBank="), "a miss says why");
                Assert(find.Contains("float best = -1f;") && find.Contains("if (d > best)"),
                    "can-fail: the longest crossing within the span wins (r9: shortest-wins strung a 1-cell side trickle)");
                string walk = Between(s, "private static int WalkToBank(", "/// <summary>levee.holds:");
                Assert(walk.Contains("!c.Standable(map) || c.GetEdifice(map) != null"), "a bank must take a post");
            });
            Case("PitDepthDraw_shots_leave_from_the_unsunk_position", () =>
            {
                string s = Src("Superdeep", "RM_PitDepthDraw.cs");
                Assert(s.Contains("[HarmonyPatch(typeof(Verb), \"TryCastNextBurstShot\")]"), "the firing window is patched");
                Assert(s.Contains("[HarmonyFinalizer]") && s.Contains("Firing--"), "the window always closes, even on a throw");
                string post = Between(s, "public static void Postfix(Pawn_DrawTracker __instance", "float sink = SinkOf(");
                Assert(post.Contains("RM_Patch_PitDepthDrawCombatOrigin.Firing > 0"), "DrawPos is unsunk while a verb fires");
            });
            Case("PitLipOcclusion_pawn_rects_read_once_per_frame", () =>
            {
                string s = Src("Superdeep", "RM_PitLipOcclusion.cs");
                string hit = Between(s, "private bool HitsShallowerPawn(", "public override void MapComponentUpdate()");
                Assert(!hit.Contains("DrawPos") && !hit.Contains("AllPawnsSpawned"), "the per-piece test reads the frame's cached rects");
                Assert(s.Contains("if (!rectsBuilt)"), "the rects are built once per update");
            });

            // ── re-review of d1898bef91 (2026-10-11) ──────────────────────────────────────────
            Case("SuperdeepTrap_cover_beside_open_pit_is_no_way_out", () =>
            {
                string s = Src("Superdeep", "RM_SuperdeepTrap.cs");
                string bfs = Between(s, "public static bool TryGetTrapRegion(", "public static bool AllowedDestination(");
                Assert(bfs.Contains("eng.IsSuperdeepExcavation(n) && !Pits.RM_PitCoverUtility.IsCovered(p.Map, n)"),
                    "can-fail: the hold region expands only into OPEN pit cells (a covered neighbour used to mark the pit untrapped)");
                string floor = Between(s, "class RM_Patch_PathFollower_SuperdeepFloor", "RM_PitTrapMath.StepBlocked(");
                Assert(floor.Contains("RM_PitCoverUtility.IsCovered(pawn.Map, __instance.nextCell) ? 0 :"),
                    "can-fail: the per-move floor reads a covered destination as ground");
                Assert(RM_PitTrapMath.StepBlocked(true, 0), "a held pawn may not step onto ground (so onto a cover read as 0)");
                Assert(!RM_PitTrapMath.StepBlocked(true, 4), "precondition: the raw D=4 under a cover never blocked the step");
            });
            // the room depth is the setting pitRoomMinDepthMetres: shipped 3.0 m for a person (PIT_ROOM_TUNE_TALL_FOLK_DIG_DEEPER,
            // owner card 2026-10-18), 0 = any depth.
            Case("PitRooms_pit_room_is_a_pocket_at_the_setting_depth", () =>
            {
                string s = Src("Superdeep", "RM_PitRooms.cs");
                string f = Between(s, "public static bool IsPitCell(", "private sealed class Side");
                Assert(f.Contains("RM_RelativeRulesMath.PitRoomCell(RM_PocketGrid.IsPersonPocketCell(map, c), eng.ExcavatedDepthRaw(c), MinRoomNotches)"),
                    "a pit room cell is a person pocket at least the setting's depth");
                Assert(!f.Contains("IsDugRaw"), "can-fail: the old dug-at-all test");
                Assert(!RM_RelativeRulesMath.PitRoomCell(true, 3, RM_RelativeRulesMath.Notches(2f, 0)) && RM_RelativeRulesMath.PitRoomCell(true, 3, 0),
                    "a 2 m setting refuses a sheer D3 pocket; 0 (any depth) takes it");
            });
            Case("PitStepCost_stepping_off_a_cover_is_no_climb", () =>
            {
                string s = Src("Superdeep", "RM_PitStepCost.cs");
                Assert(s.Contains("if (from > 0 && Pits.RM_SpanUtility.DeckedAt(map, prevCell, out float fromDeckM))")
                    && s.Contains("from = System.Math.Min(from, RM_SpanMath.Notches(fromDeckM));"),
                    "can-fail: a decked previous cell counts as its deck height (a cover: depth 0)");
                Assert(s.Contains("Pits.Building_SpanDeck toCover = to > 0 ? Pits.RM_SpanUtility.DeckAt(map, c) : null;")
                    && s.Contains("to = RM_SpanMath.WalkingDepth(to, toCover.Read);"), "a decked destination counts as its deck height (a cover: depth 0)");
                Assert(RM_SpanMath.WalkingDepth(4, RM_SpanMath.CoverRead) == 0, "a cover's walking depth is the surface");
                Assert(s.Contains("int surface = toCover != null ? Mathf.Max(toCover.def.pathCost, 0) :")
                    && s.Contains("[HarmonyPriority(Priority.High)]"),
                    "a climb onto a cover is priced as the cover's cost + the climb, ahead of the cover-cost prefix (no order dependence)");
                Assert(At(s, "DeckedAt(map, prevCell") < At(s, "if ((to == 0 && from == 0)"), "both are read before the surface early-out");
                Assert(RM_PitTrapMath.DryStepBaseCost(0, 0, 300) == 0 && RM_PitTrapMath.DryStepBaseCost(4, 0, 300) > 0,
                    "precondition: read as D=4 the step off a deck was a full climb; read as 0 it is free");
            });
            Case("PlacerStock_old_save_recovers_its_base_from_the_cap", () =>
            {
                Assert(Math.Abs(RM_PlacerMath.UnitsFromCap(20f, 2f) - 1000f) < 1e-3f, "20 at 2% came from 1000 units");
                Assert(Math.Abs(RM_PlacerMath.StockCap(RM_PlacerMath.UnitsFromCap(37f, 5f), 5f) - 37f) < 1e-3f, "round trip");
                Assert(RM_PlacerMath.UnitsFromCap(-1f, 2f) < 0f && RM_PlacerMath.UnitsFromCap(20f, 0f) < 0f,
                    "no cap saved, or a 0% setting: not recoverable (re-derived from the map)");
                string s = Between(Src("Quarry", "RM_PlacerWorks.cs"), "public override void ExposeData()", "public override void MapComponentTick()");
                Assert(s.Contains("if (Scribe.mode == LoadSaveMode.LoadingVars && units < 0f)"), "only an old save (no units key) is repaired");
                Assert(s.Contains("Scribe_Values.Look(ref legacyCap, \"RM_placerCap\", -1f);"), "can-fail: the old key is read");
                Assert(s.Contains("units = RM_PlacerMath.UnitsFromCap(legacyCap, RM_QuarrySettings.placerStockPercent);"),
                    "can-fail: the base is recovered from the old cap");
            });
            Case("DigFind_letter_points_at_the_stack_it_landed_in", () =>
            {
                string s = Src("RM_DigDiscovery.cs");
                Assert(s.Contains("ThingPlaceMode.Near, out Thing placed)"), "can-fail: placement reports the resulting stack");
                Assert(s.Contains("LetterDefOf.PositiveEvent, target);") && s.Contains("target, MessageTypeDefOf.PositiveEvent"),
                    "can-fail: letter and message target the placed stack, not a possibly absorbed (destroyed) `made`");
                Assert(!s.Contains("LetterDefOf.PositiveEvent, made)"), "no letter aimed at `made`");
            });
            Case("Settings_pit_section_reset_reruns_rebuild_redraw_apply", () =>
            {
                // review 2026-10-14: per-frame snapshots around Section() caught a section reset but not the confirmed Reset-all,
                // whose dialog callback runs outside the window's frame. One compare against the last-applied values now runs at
                // the start AND the end of every frame, so every route that changes a setting reruns its rebuild/redraw/apply.
                string s = Src("RimMandrakeFlowWorksMod.cs");
                int first = At(s, "ApplyChangedSettings();");
                Assert(first < At(s, "Widgets.BeginScrollView(inRect"), "can-fail: the compare runs before drawing (catches a confirmed Reset-all)");
                int second = s.IndexOf("ApplyChangedSettings();", first + 1, StringComparison.Ordinal);
                Assert(second > At(s, "list.End();"), "can-fail: and again after drawing (catches this frame's controls and section resets)");
                string apply = Between(s, "private static void ApplyChangedSettings()", "\n        }");
                foreach (string f in new[] { "pondBedHollowEnabled", "pitRelativeClimbEnabled", "pitClimbAbilityMultiplier", "pitRampsEnabled",
                    "pitRampMaxSpan", "superdeepRoomsEnabled", "excavationWallFacesEnabled", "excavationWallMaterialEnabled",
                    "pitOutlineEnabled", "pitScorchEnabled", "liquidLooksEnabled", "liquidSeeThroughEnabled" })
                {
                    Assert(apply.Contains("!= " + f) && apply.Contains(" = " + f + ";"), "can-fail: compared and recorded: " + f);
                }
                foreach (string call in new[] { "RM_PocketGrid.SettingsChanged();", "WholeMapChanged(", "RM_PitRooms.RebuildAllMaps();",
                    "SectionLayer_RMExcavationWalls.RedrawAll();", "RM_LiquidLooks.ApplyAll();", "RM_LiquidLooks.RevertAll();" })
                {
                    Assert(apply.Contains(call), "can-fail: the compare runs " + call);
                }
                Assert(!s.Contains("Was = "), "no per-frame snapshot left behind to drift from the compare");
            });
            Case("LiquidDrill_unstamped_outlet_is_left_to_the_engine", () =>
            {
                string s = Src("Drilling", "Building_LiquidDrill.cs");
                Assert(s.Contains("excavation.FillAt(outlet) > 0 && outletFluid != null && outletFluid != canalFluid"),
                    "can-fail: a filled outlet with no stamped fluid is not refused here (TrySetDriverFill decides)");
                Assert(!s.Contains("excavation.FillAt(outlet) > 0 && excavation.FluidAt(outlet) != canalFluid"), "the old refusal is gone");
            });
            Case("LiquidDef_unread_forms_do_not_count", () =>
            {
                string s = Src("LiquidTypes", "LiquidDef.cs");
                string hasForm = Between(s, "bool hasForm =", ";");
                foreach (string unread in new[] { "weather", "worldTag", "pipeResource", "trade", "cuisineTags" })
                {
                    Assert(!hasForm.Contains(unread), "can-fail: " + unread + " (read by no code) is not a form");
                }
                Assert(hasForm.Contains("thirstQuality.HasValue") && hasForm.Contains("conversions"), "the read forms still count");
            });
            Case("LiquidSuites_only_real_water_is_fishable", () =>
            {
                string dir = Path.Combine(ContainerMatFixture.Root(), "TerrainDefs");
                foreach (string f in new[] { "RM_AcidWater", "RM_Ammonia", "RM_FuelSap", "RM_Ichor", "RM_Ooze", "RM_ReactionLiquor",
                    "RM_SlimeRed", "RM_SlimeGreen", "RM_SlimeWhite", "RM_SlimeYellow", "RM_WaterPoisoned", "RM_Tar" })
                {
                    XDocument d = XDocument.Load(Path.Combine(dir, f + ".xml"));
                    int n = 0;
                    foreach (XElement t in d.Root.Elements("TerrainDef"))
                    {
                        n++;
                        Assert((string)t.Element("waterBodyType") == "None",
                            "can-fail: " + (string)t.Element("defName") + " is no fishable freshwater body (waterBodyType None)");
                    }
                    Assert(n >= 2, f + ": shallow and deep read");
                }
                foreach (string f in new[] { "RM_WaterBoiling", "RM_WaterFrigid" })
                {
                    int n = 0;
                    foreach (XElement t in XDocument.Load(Path.Combine(dir, f + ".xml")).Root.Elements("TerrainDef"))
                    {
                        n++;
                        string wb = (string)t.Element("waterBodyType"), parent = (string)t.Attribute("ParentName");
                        // an absent waterBodyType is inherited, so it is fishable only when the parent is a real water base
                        Assert(wb != null ? wb != "None" : (parent == "WaterShallowBase" || parent == "WaterDeepBase"),
                            "real water stays fishable: " + (string)t.Element("defName"));
                    }
                    Assert(n >= 2, f + ": shallow and deep read");
                }
            });
            Case("PitFill_splashes_agree_with_the_fluid_look", () =>
            {
                string p = Path.Combine(ContainerMatFixture.Root(), "..", "Canals", "TerrainDefs", "FlowWorks_PitFluidTerrain.xml");
                var splash = new System.Collections.Generic.Dictionary<string, string>();
                foreach (XElement t in XDocument.Load(p).Root.Elements("TerrainDef"))
                {
                    splash[(string)t.Element("defName")] = (string)t.Element("takeSplashes");
                }
                foreach (string tier in new[] { "Trace", "Half", "Brim", "Superdeep" })
                {
                    Assert(splash["RM_Fill_Poison_" + tier] == "true", "can-fail: poison (water look, splashes) tier " + tier + " splashes");
                    Assert(splash["RM_Fill_Blood_" + tier] == "false", "can-fail: blood (thick Flow look, no splash) tier " + tier + " does not");
                }
            });
        }
    }
}
