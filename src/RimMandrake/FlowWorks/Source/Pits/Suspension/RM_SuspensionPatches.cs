using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.Pits
{
	// SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS: the engine doors of the surface suspension bridge. Each is one rule of
	// design/RimMandrake/suspension_bridge_construction_design_2026-10-18.md or the parent design, named on its class.

	/// <summary>Build order (construction design §1.3): a deck square is worked from an anchor or a finished deck square next
	/// to it along its lane; one whose neighbours toward both anchors are unbuilt cannot be started (no floating middles).</summary>
	[HarmonyPatch(typeof(GenConstruct), nameof(GenConstruct.CanConstruct),
		new[] { typeof(Thing), typeof(Pawn), typeof(bool), typeof(bool), typeof(JobDef) })]
	[RimMandrake.Shared.PatchFeature("Suspension bridges build from the anchors inward")]
	public static class RM_Patch_SuspensionBuildOrder
	{
		[HarmonyPostfix]
		public static void Postfix(Thing t, ref bool __result)
		{
			if (!__result || t == null || !t.Spawned || !(t.def.IsBlueprint || t.def.IsFrame) || !RM_SuspensionDefOf.IsDeckDef(t.def.entityDefToBuild))
			{
				return;
			}
			Map map = t.Map;
			SuspensionBridgeRecord r = map.GetComponent<RM_MapComponent_SuspensionBridges>()?.RecordAt(t.Position);
			if (r == null || !r.TryIndexOf(t.Position, out int lane, out int i))
			{
				return;
			}
			// a jetty builds outward from its root only (no far end to build from)
			bool ok = r.jetty ? (i <= 1 ? RM_MapComponent_SuspensionBridges.BuiltAt<Building_SuspensionAnchor>(map, r.Cell(lane, 0)) != null
					: RM_MapComponent_SuspensionBridges.DeckAt(map, r.Cell(lane, i - 1)) != null)
				: RM_SuspensionMath.MayBuildDeck(i, r.length, k =>
			{
				IntVec3 c = r.Cell(lane, k);
				return k == 0 || k == r.length - 1
					? RM_MapComponent_SuspensionBridges.BuiltAt<Building_SuspensionAnchor>(map, c) != null
					: RM_MapComponent_SuspensionBridges.DeckAt(map, c) != null;
			});
			if (!ok)
			{
				__result = false;
				JobFailReason.Is("Build a suspension bridge from its anchors inward: the square next to this one is not built yet.");
			}
		}
	}

	/// <summary>Terrain: a deck square or tower stands on any dug square (the hole's floor terrain may be water or mud), and a
	/// built deck lends its type's affordances to what is built on it (timber Light; steel Light/Medium; heavy all three;
	/// rope none).</summary>
	[HarmonyPatch(typeof(GenConstruct), nameof(GenConstruct.CanBuildOnTerrain))]
	[RimMandrake.Shared.PatchFeature("Suspension bridges carry buildings by type")]
	public static class RM_Patch_SuspensionAffordance
	{
		[HarmonyPostfix]
		public static void Postfix(BuildableDef entDef, IntVec3 c, Map map, Rot4 rot, ThingDef stuffDef, ref bool __result)
		{
			if (__result || entDef == null || map == null || !c.InBounds(map))
			{
				return;
			}
			RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null)
			{
				return;
			}
			if (RM_SuspensionDefOf.IsDeckDef(entDef) || entDef == RM_SuspensionDefOf.RM_SuspensionTower)
			{
				// SUSPENSION_WATERS_BUILD_MAY_BACKTRACK: natural water as well as dug ground
				__result = ex.ExcavatedDepthAt(c) > 0 || RM_SuspensionWaters.Spannable(c.GetTerrain(map));
				return;
			}
			// SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD: a sunken bridge's anchor stands on a dry dug ledge (the designator
			// checks it is at the deck's height)
			if (RM_SuspensionDefOf.IsAnchorDef(entDef) && ex.ExcavatedDepthAt(c) > 0)
			{
				__result = RM_SuspensionSettings.sunkenBridges && ex.FillAt(c) == 0;
				return;
			}
			if (entDef == RM_SuspensionDefOf.RM_SuspensionRailing)
			{
				__result = RM_MapComponent_SuspensionBridges.DeckAt(map, c) != null;
				return;
			}
			TerrainAffordanceDef need = entDef.GetTerrainAffordanceNeed(stuffDef);
			int bit = need == TerrainAffordanceDefOf.Light ? RM_SuspensionMath.AffordLight
				: need == TerrainAffordanceDefOf.Medium ? RM_SuspensionMath.AffordMedium
				: need == TerrainAffordanceDefOf.Heavy ? RM_SuspensionMath.AffordHeavy : 0;
			if (bit == 0)
			{
				return;
			}
			CellRect rect = GenAdj.OccupiedRect(c, rot, entDef.Size);
			rect.ClipInsideMap(map);
			foreach (IntVec3 cell in rect)
			{
				if (cell.GetAffordances(map).Contains(need))
				{
					continue;
				}
				Building_SuspensionDeck d = RM_MapComponent_SuspensionBridges.DeckAt(map, cell);
				if (d == null || (RM_SuspensionMath.LentAffordances(d.Tier) & bit) == 0)
				{
					return;
				}
			}
			__result = true;
		}
	}

	/// <summary>Q6 (parent design §2.1, ruled by card): the game's own Bridge / HeavyBridge are refused on any square the
	/// excavation component owns ("Use a suspension bridge over dug ground"). Setting vanillaBridgeRefusedOverDug.</summary>
	[HarmonyPatch(typeof(GenConstruct), nameof(GenConstruct.CanPlaceBlueprintAt_NewTemp))]
	[RimMandrake.Shared.PatchFeature("Game bridges refused over dug ground", typeof(RM_SuspensionSettings), "vanillaBridgeRefusedOverDug")]
	public static class RM_Patch_VanillaBridgeRefusedOverDug
	{
		public const string Reason = "Use a suspension bridge over dug ground";

		[HarmonyPostfix]
		public static void Postfix(BuildableDef entDef, IntVec3 center, Map map, ref AcceptanceReport __result)
		{
			if (!__result.Accepted || !RM_SuspensionSettings.vanillaBridgeRefusedOverDug || !(entDef is TerrainDef t) || !t.bridge
				|| map == null || !center.InBounds(map))
			{
				return;
			}
			RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
			if (ex != null && ex.IsExcavated(center))
			{
				__result = new AcceptanceReport(Reason);
			}
		}
	}

	/// <summary>Parent design §6.4: digging or filling in under a suspension bridge (deck, anchor, tower; built or planned) is
	/// refused: its clearance and supports were checked when it was planned.</summary>
	[HarmonyPatch(typeof(Designator_DigCanal), nameof(Designator_DigCanal.CanDesignateCell))]
	[RimMandrake.Shared.PatchFeature("No digging under a suspension bridge")]
	public static class RM_Patch_DigRefusedUnderSuspension
	{
		public const string Reason = "Remove the suspension bridge first.";

		[HarmonyPostfix]
		public static void Postfix(Designator __instance, IntVec3 c, ref AcceptanceReport __result)
		{
			if (__result.Accepted && RM_MapComponent_SuspensionBridges.AnyPartAt(__instance.Map, c))
			{
				__result = new AcceptanceReport(Reason);
			}
		}
	}

	[HarmonyPatch(typeof(Designator_DigCanalTo), nameof(Designator_DigCanalTo.CanDesignateCell))]
	[RimMandrake.Shared.PatchFeature("No deepening under a suspension bridge")]
	public static class RM_Patch_DigToRefusedUnderSuspension
	{
		[HarmonyPostfix]
		public static void Postfix(Designator __instance, IntVec3 c, ref AcceptanceReport __result)
		{
			if (__result.Accepted && RM_MapComponent_SuspensionBridges.AnyPartAt(__instance.Map, c))
			{
				__result = new AcceptanceReport(RM_Patch_DigRefusedUnderSuspension.Reason);
			}
		}
	}

	[HarmonyPatch(typeof(Designator_FillInCanal), nameof(Designator_FillInCanal.CanDesignateCell))]
	[RimMandrake.Shared.PatchFeature("No filling in under a suspension bridge")]
	public static class RM_Patch_FillRefusedUnderSuspension
	{
		[HarmonyPostfix]
		public static void Postfix(Designator __instance, IntVec3 c, ref AcceptanceReport __result)
		{
			if (__result.Accepted && RM_MapComponent_SuspensionBridges.AnyPartAt(__instance.Map, c))
			{
				__result = new AcceptanceReport(RM_Patch_DigRefusedUnderSuspension.Reason);
			}
		}
	}

	/// <summary>Construction design §2: a stagger on an open-edged deck square drops the pawn into the hole 25% of the time.</summary>
	[HarmonyPatch(typeof(Pawn_StanceTracker), nameof(Pawn_StanceTracker.StaggerFor))]
	[RimMandrake.Shared.PatchFeature("Staggered off an open suspension bridge edge")]
	public static class RM_Patch_SuspensionStaggerFall
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn_StanceTracker __instance)
		{
			Pawn p = __instance?.pawn;
			if (p != null && p.Spawned && !p.Dead)
			{
				RM_MapComponent_SuspensionBridges.TryKnockOff(p, RM_SuspensionMath.StaggerFallChance, "staggered");
			}
		}
	}

	/// <summary>Construction design §2: a damaging blast reaching a pawn on an open-edged deck square drops it into the hole
	/// 25% of the time (a knockback throw, where a mod adds one, is RM_FallRails' and stops at a railing).</summary>
	[HarmonyPatch(typeof(DamageWorker), nameof(DamageWorker.ExplosionAffectCell))]
	[RimMandrake.Shared.PatchFeature("Blasted off an open suspension bridge edge")]
	public static class RM_Patch_SuspensionBlastFall
	{
		[HarmonyPostfix]
		public static void Postfix(Explosion explosion, IntVec3 c)
		{
			Map map = explosion?.Map;
			if (map == null || explosion.damType == null || !explosion.damType.harmsHealth || !c.InBounds(map)
				|| RM_MapComponent_SuspensionBridges.DeckAt(map, c) == null)
			{
				return;
			}
			foreach (Pawn p in RM_MapComponent_SuspensionBridges.PawnsOn(map, c))
			{
				RM_MapComponent_SuspensionBridges.TryKnockOff(p, RM_SuspensionMath.BlastFallChance, "blasted");
			}
		}
	}

	/// <summary>Construction design §2: a slime slip on an open-edged deck square drops the pawn 10% of the time. Wired at the
	/// slip itself; RM_SlimeSlip lets a slip happen on a deck only on a GRATE (the splash, SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP),
	/// so that is where this fires; a solid deck keeps the slime below off its walkers.</summary>
	[HarmonyPatch(typeof(RM_SlimeSlip), "Slip")]
	[RimMandrake.Shared.PatchFeature("Slipped off an open suspension bridge edge")]
	public static class RM_Patch_SuspensionSlimeFall
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn p)
		{
			RM_MapComponent_SuspensionBridges.TryKnockOff(p, RM_SuspensionMath.SlimeFallChance, "slipped");
		}
	}

	/// <summary>Construction design §2: a railed square has no way down on purpose; an open edge keeps the "Jump into pit"
	/// order (RM_SuperdeepTrap.JumpTargetFor already sees a deck square as ground beside the hole).</summary>
	[HarmonyPatch(typeof(RM_SuperdeepTrap), nameof(RM_SuperdeepTrap.JumpTargetFor))]
	[RimMandrake.Shared.PatchFeature("Railings stop jumping off a suspension bridge")]
	public static class RM_Patch_SuspensionRailedNoJump
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn p, ref IntVec3 __result)
		{
			if (__result.IsValid && p?.Map != null && RM_MapComponent_SuspensionBridges.DeckAt(p.Map, p.Position) != null
				&& RM_MapComponent_SuspensionBridges.RailedAt(p.Map, p.Position))
			{
				__result = IntVec3.Invalid;
			}
		}
	}

	/// <summary>The P8 readout line (parent design §7): "Suspension bridge (timber) · deck at surface · load 210 / 600 kg ·
	/// below: Hole 4 m".</summary>
	[HarmonyPatch(typeof(RM_Patch_MouseoverDepth), nameof(RM_Patch_MouseoverDepth.DepthSuffix))]
	[RimMandrake.Shared.PatchFeature("Suspension bridge mouseover line")]
	public static class RM_Patch_SuspensionReadout
	{
		[HarmonyPostfix]
		public static void Postfix(Map map, IntVec3 c, ref string __result)
		{
			if (map == null || !c.InBounds(map))
			{
				return;
			}
			RM_MapComponent_SuspensionBridges b = map.GetComponent<RM_MapComponent_SuspensionBridges>();
			if (b == null || RM_MapComponent_SuspensionBridges.DeckAt(map, c) == null)
			{
				return;
			}
			SuspensionBridgeRecord r = b.RecordAt(c);
			if (r == null || !r.TryIndexOf(c, out _, out int i))
			{
				return;
			}
			float load = b.SpanLoad(r, r.SpanOfIndex(i));
			string line = r.jetty ? RM_SuspensionMath.JettyReadoutLine(r.tier, load, r.RatingKg, r.deckNotches)
				: RM_SuspensionMath.ReadoutLine(r.tier, load, r.RatingKg, r.deckNotches, RM_MapComponent_SuspensionBridges.DeckAt(map, c).FloorBandPassesUnder);
			__result = __result == null ? line : line + " · below: " + __result;
		}
	}

	/// <summary>
	/// SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP (parent design §4.1-§4.2, as ruled: Q4 spilled liquid only; Q9 rain falls through
	/// every deck, so rain is no grate difference): what a grated deck lets through, read at the call sites that already
	/// existed (RM_LiquidFire's effects, RM_SlimeSlip, RM_PitFillEffects, RM_LiquidSpill.Spill).
	///   * fire: burning liquid below sets the people on a grate alight at the open-pit chance × 0.75 (RM_FireMath), and burns
	///     them over time with vanilla Burn injuries (one kind of heat: no new hediff). Setting grateFirePasses.
	///   * spills: liquid spilled or poured on a grate over a dug square goes into the hole's body (stock conserved). Items stay
	///     on the deck. Setting grateDrainsSpills.
	///   * splash: slime slips and toxic fill reach the people on a grate at half the open-pit chance (never drowning).
	///   * shots: a grate does not block shots between the deck band and the floor band (read by the underpass item).
	/// </summary>
	public static class RM_GrateEffects
	{
		/// <summary>State reads for the functional script: Burn injuries dealt on grates, decilitres drained through them.</summary>
		public static int Scorches;
		public static long DrainedDl;

		/// <summary>The intact grated deck on this square, or null.</summary>
		public static Building_SpanDeck GrateAt(Map map, IntVec3 c)
		{
			Building_SpanDeck d = RM_SpanUtility.DeckAt(map, c);
			return d != null && d.Grated ? d : null;
		}

		public static bool GratePassesFire(Map map, IntVec3 c)
		{
			return RM_SuspensionSettings.grateFirePasses && GrateAt(map, c) != null;
		}

		/// <summary>Is this pawn down in the hole beneath a suspension deck (the floor band)? Then nothing about the deck
		/// shields it: it is in the fire, the slime and the fill like anyone in the open hole.</summary>
		public static bool UnderDeck(Pawn p)
		{
			return RM_SuspensionUnderpass.InFloorBand(p);
		}

		/// <summary>How much of the hole's splash reaches this pawn on this square: 1 with no deck (or under one, in the floor
		/// band), half on a grate, nothing on a solid deck.</summary>
		public static float SplashShare(Building_SpanDeck deck, Pawn p)
		{
			if (deck == null || UnderDeck(p))
			{
				return 1f;
			}
			return deck.Grated ? RM_SuspensionMath.GrateSplashChance(1f) : 0f;
		}

		/// <summary>A pawn on a grate over a fire: now and then one vanilla Burn injury.</summary>
		public static void Scorch(Pawn p)
		{
			if (p == null || p.Dead || !Rand.Chance(RM_SuspensionMath.GrateBurnChancePerCheck))
			{
				return;
			}
			p.TakeDamage(new DamageInfo(DamageDefOf.Burn, RM_SuspensionMath.GrateBurnDamage));
			Scorches++;
		}

		/// <summary>A spill of <paramref name="dl"/> decilitres of <paramref name="fluid"/> landing on <paramref name="c"/>: the
		/// share a grate drains into the hole below (poured there now). Returns the decilitres it took.</summary>
		public static long DrainSpill(Map map, IntVec3 c, FluidDef fluid, long dl)
		{
			if (map == null || fluid == null || dl <= 0 || !c.InBounds(map) || GrateAt(map, c) == null)
			{
				return 0;
			}
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			bool dug = ex != null && ex.IsExcavated(c);
			long room = dug ? ex.PourRoomDl(c, fluid, dl) : 0;
			long n = RM_SuspensionMath.GrateDrainDl(true, RM_SuspensionSettings.grateDrainsSpills, dug, dl, room);
			if (n <= 0 || !ex.TryPourDl(c, fluid, n))
			{
				return 0;
			}
			DrainedDl += n;
			return n;
		}
	}

	/// <summary>
	/// SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD (construction design §1.4, §4; parent §5.1-§5.2; R8 amended 2026-10-18,
	/// owner: <i>"only for these new bridges uniquely, NOT actual tunnels."</i>): the FLOOR BAND under a suspension deck.
	///
	/// A deck square has two bands: the deck band (everyone who came on from an anchor, a ledge or another deck square) and the
	/// floor band (everyone who walked in along the hole's floor). The floor band exists only under a Building_SuspensionDeck
	/// whose floor is at least 2 m below it (FloorBandPassesUnder, setting suspensionWalkUnder); no roof, dug passage, cover or
	/// other building ever grants it. A pawn's band is decided as it steps onto the square (StepGoesUnder) and kept in the
	/// bridges component (saved). Everything that asks "is this pawn down in the hole" (fire, slime, fill, exposure, falls,
	/// crush, shots, the sink, the walked-step cost and floor, the cliff masks' floor view) reads InFloorBand.
	/// </summary>
	public static class RM_SuspensionUnderpass
	{
		/// <summary>The suspension deck on this square whose floor band passes under it (intact), or null.</summary>
		public static Building_SuspensionDeck PassingDeckAt(Map map, IntVec3 c)
		{
			return RM_MapComponent_SuspensionBridges.DeckAt(map, c) is Building_SuspensionDeck d && d.FloorBandPassesUnder ? d : null;
		}

		/// <summary>Is this pawn under a suspension deck now (in the floor band of the square it stands on)?</summary>
		public static bool InFloorBand(Pawn p)
		{
			if (RM_MapComponent_SuspensionBridges.BandTotal == 0 || p == null || !p.Spawned)
			{
				return false;
			}
			RM_MapComponent_SuspensionBridges b = p.Map.GetComponent<RM_MapComponent_SuspensionBridges>();
			return b != null && b.InBandSet(p) && PassingDeckAt(p.Map, p.Position) != null;
		}

		/// <summary>The walking depth (notches) of a square as the floor band reads it: a deck the floor band passes under reads
		/// its floor; any other deck its walking height (a cover 0); no deck, the climb depth.</summary>
		public static int FloorViewDepthAt(Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			if (eng == null || !c.InBounds(map))
			{
				return 0;
			}
			int d = eng.ClimbDepthAt(c);
			if (d <= 0)
			{
				return d;
			}
			Building_SpanDeck deck = RM_SpanUtility.DeckAt(map, c);
			if (deck == null || deck.FloorBandPassesUnder)
			{
				return d;
			}
			return RM_SpanMath.WalkingDepth(d, deck.Read);
		}

		/// <summary>Does this pawn's step from <paramref name="from"/> into <paramref name="to"/> go under a deck (or along
		/// the floor band from one deck square to the next)?</summary>
		public static bool StepGoesUnder(Pawn p, IntVec3 from, IntVec3 to)
		{
			Map map = p?.Map;
			if (map == null || !from.InBounds(map) || !to.InBounds(map))
			{
				return false;
			}
			Building_SuspensionDeck dTo = PassingDeckAt(map, to);
			if (dTo == null)
			{
				return false;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			bool fromDecked = RM_SpanUtility.DeckedAt(map, from);
			int fromWalk = eng == null ? 0 : RM_SpanUtility.WalkingDepth(map, from, eng.ClimbDepthAt(from));
			bool fromBand = fromDecked && from == p.Position ? InFloorBand(p) : fromDecked && PassingDeckAt(map, from) != null
				&& RM_MapComponent_SuspensionBridges.Of(map)?.InBandSet(p) == true;
			return RM_SuspensionMath.StepGoesUnder(true, dTo.DeckNotches, fromDecked, fromBand, fromWalk);
		}

		/// <summary>Does a step that leaves a floor-band square stay at floor level (it always does: the floor band never climbs
		/// onto the deck it is under)? True when the pawn is in the floor band at <paramref name="from"/>.</summary>
		public static bool StepLeavesUnder(Pawn p, IntVec3 from)
		{
			return p != null && from == p.Position && InFloorBand(p);
		}

		/// <summary>Which view of the cliff masks a path request of this pawn uses: the floor view (decks the floor band passes
		/// under read as the floor) for a pawn in the floor band or down in a hole on an undecked square; else the deck view.</summary>
		public static bool UsesFloorView(Pawn p)
		{
			if (p == null || !p.Spawned || !RM_SuspensionSettings.suspensionWalkUnder)
			{
				return false;
			}
			if (InFloorBand(p))
			{
				return true;
			}
			Map map = p.Map;
			if (RM_SpanUtility.DeckedAt(map, p.Position))
			{
				return false;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			return eng != null && eng.ClimbDepthAt(p.Position) > 0;
		}

		/// <summary>The pawn just walked from <paramref name="from"/> onto <paramref name="to"/>: its band there.</summary>
		public static void Entered(Pawn p, IntVec3 from, IntVec3 to)
		{
			RM_MapComponent_SuspensionBridges b = RM_MapComponent_SuspensionBridges.Of(p?.Map);
			if (b == null)
			{
				return;
			}
			if (PassingDeckAt(p.Map, to) == null)
			{
				b.SetBand(p, false);
				return;
			}
			bool fromDecked = RM_SpanUtility.DeckedAt(p.Map, from);
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(p.Map);
			int fromWalk = eng == null ? 0 : RM_SpanUtility.WalkingDepth(p.Map, from, eng.ClimbDepthAt(from));
			bool fromBand = fromDecked && b.InBandSet(p) && PassingDeckAt(p.Map, from) != null;
			b.SetBand(p, RM_SuspensionMath.StepGoesUnder(true, PassingDeckAt(p.Map, to).DeckNotches, fromDecked, fromBand, fromWalk));
		}

		/// <summary>The sink depth (notches) the pawn's draw reads on a square: its walking height on a suspension deck in the
		/// deck band, the hole's depth under it (floor band). Covers keep their old read.</summary>
		public static int DrawDepth(Pawn p, IntVec3 c, int hollow)
		{
			if (hollow <= 0 || p?.Map == null || !(RM_MapComponent_SuspensionBridges.DeckAt(p.Map, c) is Building_SuspensionDeck d))
			{
				return hollow;
			}
			bool under = c == p.Position ? InFloorBand(p) : StepGoesUnder(p, p.Position, c);
			if (under)
			{
				return hollow;
			}
			int h = d.DeckNotches;
			return h < hollow ? h : hollow;
		}

		/// <summary>Is this pawn standing on a deck (deck band)?</summary>
		public static bool OnDeck(Pawn p)
		{
			return p != null && p.Spawned && RM_SpanUtility.DeckedAt(p.Map, p.Position) && !InFloorBand(p);
		}

		/// <summary>The nearest open floor square for something that may not rest under a deck: dug, no deck, standable.</summary>
		public static IntVec3 OpenFloorNear(Map map, IntVec3 c)
		{
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null)
			{
				return IntVec3.Invalid;
			}
			foreach (IntVec3 n in GenRadial.RadialCellsAround(c, 8.9f, false))
			{
				if (n.InBounds(map) && eng.ClimbDepthAt(n) > 0 && !RM_SpanUtility.DeckedAt(map, n) && n.Standable(map)
					&& n.GetFirstItem(map) == null)
				{
					return n;
				}
			}
			return IntVec3.Invalid;
		}

		/// <summary>Nothing rests under a deck: an item or corpse a floor-band pawn left on a decked square slides to the
		/// nearest open floor square. Returns whether it moved.</summary>
		public static bool SlideOut(Thing t)
		{
			if (t == null || !t.Spawned || PassingDeckAt(t.Map, t.Position) == null)
			{
				return false;
			}
			Map map = t.Map;
			IntVec3 to = OpenFloorNear(map, t.Position);
			if (!to.IsValid)
			{
				return false;
			}
			t.DeSpawn();
			GenSpawn.Spawn(t, to, map);
			Slid++;
			return true;
		}

		/// <summary>State read for the functional script: things slid out from under a deck this session.</summary>
		public static int Slid;
	}

	/// <summary>SUSPENSION_UNDERPASS: each walked step decides the pawn's band on the square it lands on.</summary>
	[HarmonyPatch(typeof(Pawn_PathFollower), "TryEnterNextPathCell")]
	[RimMandrake.Shared.PatchFeature("Walking under suspension bridges", typeof(RM_SuspensionSettings), "suspensionWalkUnder")]
	public static class RM_Patch_SuspensionBandStep
	{
		[HarmonyPrefix]
		public static void Prefix(Pawn ___pawn, out IntVec3 __state)
		{
			__state = ___pawn?.Position ?? IntVec3.Invalid;
		}

		[HarmonyPostfix]
		public static void Postfix(Pawn ___pawn, IntVec3 __state)
		{
			if (___pawn != null && ___pawn.Spawned && __state.IsValid && ___pawn.Position != __state)
			{
				RM_SuspensionUnderpass.Entered(___pawn, __state, ___pawn.Position);
			}
		}
	}

	/// <summary>SUSPENSION_UNDERPASS: a pawn set down anywhere (a fall, a teleport, a knock off the edge) is on whatever it
	/// lands on: the deck band if that is a deck.</summary>
	[HarmonyPatch(typeof(Pawn), nameof(Pawn.Notify_Teleported))]
	[RimMandrake.Shared.PatchFeature("Walking under suspension bridges", typeof(RM_SuspensionSettings), "suspensionWalkUnder")]
	public static class RM_Patch_SuspensionBandTeleport
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn __instance)
		{
			RM_MapComponent_SuspensionBridges.Of(__instance?.Map)?.SetBand(__instance, false);
		}
	}

	/// <summary>SUSPENSION_UNDERPASS: the per-step floor (RM_Patch_PathFollower_SuperdeepFloor.RelativeStepAllowed) reads a decked square at its
	/// walking height; a floor-band step under a deck is judged at the floor instead.</summary>
	[HarmonyPatch(typeof(RM_Patch_PathFollower_SuperdeepFloor), nameof(RM_Patch_PathFollower_SuperdeepFloor.RelativeStepAllowed))]
	[RimMandrake.Shared.PatchFeature("Walking under suspension bridges", typeof(RM_SuspensionSettings), "suspensionWalkUnder")]
	public static class RM_Patch_SuspensionUnderStepFloor
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn pawn, RM_MapComponent_Excavation eng, IntVec3 next, ref bool __result)
		{
			if (__result || pawn == null || eng == null || !RM_SuspensionSettings.suspensionWalkUnder)
			{
				return;
			}
			IntVec3 from = pawn.Position;
			if (!RM_SuspensionUnderpass.StepGoesUnder(pawn, from, next) && !RM_SuspensionUnderpass.StepLeavesUnder(pawn, from))
			{
				return;
			}
			Map map = pawn.Map;
			int k = RM_PocketGrid.ClimbLimitOf(pawn);
			int fromD = RM_SuspensionUnderpass.FloorViewDepthAt(map, eng, from);
			int toD = RM_SuspensionUnderpass.FloorViewDepthAt(map, eng, next);
			if (from.x != next.x && from.z != next.z)
			{
				__result = RM_PitTrapMath.DiagonalAllowed(fromD, toD,
					RM_SuspensionUnderpass.FloorViewDepthAt(map, eng, new IntVec3(next.x, 0, from.z)),
					RM_SuspensionUnderpass.FloorViewDepthAt(map, eng, new IntVec3(from.x, 0, next.z)), k);
				return;
			}
			__result = RM_PitTrapMath.StepAllowed(fromD, toD, k);
		}
	}

	/// <summary>SUSPENSION_UNDERPASS: the walked step under a deck costs what a step along the hole's floor costs (the pit step
	/// cost would price it as a climb onto the deck). Runs before RM_Patch_PitStepCost, which yields to an override.</summary>
	[HarmonyPatch(typeof(PathGrid), nameof(PathGrid.CalculatedCostAt))]
	[RimMandrake.Shared.PatchFeature("Walking under suspension bridges", typeof(RM_SuspensionSettings), "suspensionWalkUnder")]
	public static class RM_Patch_SuspensionUnderStepCost
	{
		[HarmonyPrefix]
		[HarmonyPriority(Priority.First)]
		public static void Prefix(PathGrid __instance, IntVec3 c, bool perceivedStatic, IntVec3 prevCell, ref int? baseCostOverride)
		{
			if (perceivedStatic || !prevCell.IsValid || baseCostOverride.HasValue || !RM_SuspensionSettings.suspensionWalkUnder)
			{
				return;
			}
			Pawn p = RM_Patch_PathFollower_StepPawn.current;
			Map map = __instance.map;
			if (p == null || map == null || p.Map != map || !c.InBounds(map) || !prevCell.InBounds(map))
			{
				return;
			}
			if (!RM_SuspensionUnderpass.StepGoesUnder(p, prevCell, c) && !RM_SuspensionUnderpass.StepLeavesUnder(p, prevCell))
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null)
			{
				return;
			}
			if (eng.FillAt(c) > 0)
			{
				baseCostOverride = map.terrainGrid.TerrainAt(c)?.pathCost ?? 0;   // wading under the deck: the water's cost
				return;
			}
			int from = RM_SuspensionUnderpass.FloorViewDepthAt(map, eng, prevCell);
			int to = RM_SuspensionUnderpass.FloorViewDepthAt(map, eng, c);
			int deeper = to > from ? to : from;
			int cost = RM_ExcavationDepth.DryTerrainFor((byte)deeper)?.pathCost ?? 0;
			baseCostOverride = RM_PitTrapMath.DryStepBaseCost(from, to, cost);
		}
	}

	/// <summary>SUSPENSION_UNDERPASS (construction design §1.4): shots. Under a deck a pawn is at the floor, so the cliff rule
	/// (V5) judges it there; and a SOLID deck blocks a shot between someone on a deck and someone under one (a grate does not;
	/// within a band the deck is ignored).</summary>
	[HarmonyPatch(typeof(Verb), nameof(Verb.CanHitTargetFrom))]
	[RimMandrake.Shared.PatchFeature("Walking under suspension bridges", typeof(RM_SuspensionSettings), "suspensionWalkUnder")]
	public static class RM_Patch_SuspensionBandShots
	{
		[HarmonyPostfix]
		public static void Postfix(Verb __instance, IntVec3 root, LocalTargetInfo targ, ref bool __result)
		{
			Thing caster = __instance?.caster;
			Map map = caster?.Map;
			if (map == null || !targ.IsValid || __instance.IsMeleeAttack || !RM_SuspensionSettings.suspensionWalkUnder)
			{
				return;
			}
			Pawn shooter = caster as Pawn;
			Pawn target = targ.Thing as Pawn;
			bool sUnder = shooter != null && root == shooter.Position && RM_SuspensionUnderpass.InFloorBand(shooter);
			bool tUnder = target != null && RM_SuspensionUnderpass.InFloorBand(target);
			if (!sUnder && !tUnder)
			{
				return;
			}
			if (!__result)
			{
				// the cliff rule read the decked square at the deck's height: judge the floor band at the floor
				if (!RM_SuperdeepShooting.RuleAppliesTo(__instance) || RM_SuperdeepTrap.EngineOf(map) == null)
				{
					return;
				}
				RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
				bool sFloorSide = sUnder || (!RM_SpanUtility.DeckedAt(map, root) && eng.ClimbDepthAt(root) > 0);
				bool tFloorSide = tUnder || (!RM_SpanUtility.DeckedAt(map, targ.Cell) && eng.ClimbDepthAt(targ.Cell) > 0);
				if (!(sFloorSide && tFloorSide))
				{
					return;
				}
				__result = !RM_RelativeRulesMath.ShotBlocked((x, z) => RM_SuspensionUnderpass.FloorViewDepthAt(map, eng, new IntVec3(x, 0, z)),
					root.x, root.z, targ.Cell.x, targ.Cell.z, RM_SuperdeepShooting.CliffNotches);
				return;
			}
			bool sOnDeck = shooter != null && root == shooter.Position ? RM_SuspensionUnderpass.OnDeck(shooter) : RM_SpanUtility.DeckedAt(map, root);
			bool tOnDeck = target != null ? RM_SuspensionUnderpass.OnDeck(target) : RM_SpanUtility.DeckedAt(map, targ.Cell);
			bool sGrate = sUnder && RM_SpanUtility.DeckAt(map, root)?.Grated == true;
			bool tGrate = tUnder && RM_SpanUtility.DeckAt(map, targ.Cell)?.Grated == true;
			if (RM_SuspensionMath.ShotBlockedBetweenBands(sUnder, sGrate, sOnDeck, tUnder, tGrate, tOnDeck))
			{
				__result = false;
			}
		}
	}

	/// <summary>SUSPENSION_UNDERPASS: nothing rests under a deck. What a floor-band pawn puts down there slides to the nearest
	/// open floor square (corpses: RM_MapComponent_SuspensionBridges' sweep).</summary>
	[HarmonyPatch(typeof(Pawn_CarryTracker), nameof(Pawn_CarryTracker.TryDropCarriedThing),
		new[] { typeof(IntVec3), typeof(ThingPlaceMode), typeof(Thing), typeof(System.Action<Thing, int>) },
		new[] { ArgumentType.Normal, ArgumentType.Normal, ArgumentType.Out, ArgumentType.Normal })]
	[RimMandrake.Shared.PatchFeature("Walking under suspension bridges", typeof(RM_SuspensionSettings), "suspensionWalkUnder")]
	public static class RM_Patch_SuspensionDropUnder
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn_CarryTracker __instance, bool __result, Thing resultingThing)
		{
			if (__result && __instance?.pawn != null && RM_SuspensionUnderpass.InFloorBand(__instance.pawn))
			{
				RM_SuspensionUnderpass.SlideOut(resultingThing);
			}
		}
	}

	[HarmonyPatch(typeof(Pawn_CarryTracker), nameof(Pawn_CarryTracker.TryDropCarriedThing),
		new[] { typeof(IntVec3), typeof(int), typeof(ThingPlaceMode), typeof(Thing), typeof(System.Action<Thing, int>) },
		new[] { ArgumentType.Normal, ArgumentType.Normal, ArgumentType.Normal, ArgumentType.Out, ArgumentType.Normal })]
	[RimMandrake.Shared.PatchFeature("Walking under suspension bridges", typeof(RM_SuspensionSettings), "suspensionWalkUnder")]
	public static class RM_Patch_SuspensionDropUnderCount
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn_CarryTracker __instance, bool __result, Thing resultingThing)
		{
			RM_Patch_SuspensionDropUnder.Postfix(__instance, __result, resultingThing);
		}
	}

	/// <summary>
	/// SUSPENSION_WATERS_BUILD_MAY_BACKTRACK (parent design §3, §7; owner Q5: <i>"Let's design towards including rivers and
	/// oceans and large lakes (non canal pit types) but if we have to we can backtrack."</i>): suspension bridges over natural
	/// water. The deck is a building on top of vanilla water (R10: rivers and the sea stay vanilla and limitless; nothing
	/// converts their terrain). Its square is walking ground even over deep water (the path grid answers the deck's cost),
	/// never a swim square (no swimming, no drowning, items may lie on it), and the river's current never carries anything
	/// on it (the fords' exemption, RM_MapComponent_RiverCurrent). Floods: a rope or timber square awash takes 5% of its hit
	/// points an hour; steel and heavy do not.
	///
	/// TOWERS IN WATER (decided at build, construction design §1.3): a tower is built by a builder who can touch the square beside
	/// it: wading in shallow water, swimming where swimming is allowed (lakes, R12; the sea and deep moving water only with the
	/// swim setting for open water), or standing on the finished deck square next to it: decks are built from the anchors inward,
	/// so the deck itself reaches the tower. No new job: vanilla's touch-adjacent construction does it.
	///
	/// BACKTRACK: the settings suspensionOverWater (rivers, lakes) and suspensionOverSea are the levers; if a crossing type proves
	/// unworkable live, its measured reason goes on FLOWWORKS_BRIDGES_DESIGN_SPAN_ANYTHING and that type's default goes off.
	/// </summary>
	public static class RM_SuspensionWaters
	{
		public static bool Spannable(TerrainDef t)
		{
			return t != null && RM_SuspensionMath.WaterSpannable(t.IsWater, t.IsOcean, RM_SuspensionSettings.suspensionOverWater,
				RM_SuspensionSettings.suspensionOverSea);
		}

		/// <summary>Nothing on a deck is carried by a current (read by RM_MapComponent_RiverCurrent with the fords).</summary>
		public static bool CurrentExempt(Map map, IntVec3 c)
		{
			return RM_SpanUtility.DeckedAt(map, c);
		}

		/// <summary>A deck came or went over natural water: the path grid (and with it the regions), reachability and the swim
		/// grids see the change at once.</summary>
		public static void Notify_DeckChanged(Map map, IntVec3 c)
		{
			if (map == null || !c.InBounds(map) || c.GetTerrain(map)?.IsWater != true)
			{
				return;
			}
			map.pathing?.RecalculatePerceivedPathCostAt(c);
			map.reachability?.ClearCache();
			Swimming.RM_SwimPathing.Bump(map);
		}

		/// <summary>State read for the functional script: hit points floods took from decks this session.</summary>
		public static int FloodHits;

		/// <summary>Every in-game hour: rope and timber deck squares awash in a flood (a flood's water on the square's temporary
		/// terrain layer, Flood_FlowWorks or the game's own) take their flood damage.</summary>
		public static void FloodHour(Map map, IReadOnlyList<SuspensionBridgeRecord> bridges)
		{
			if (!RM_SuspensionSettings.floodsDamageLightBridges)
			{
				return;
			}
			List<Building_SuspensionDeck> hit = new List<Building_SuspensionDeck>();
			foreach (SuspensionBridgeRecord r in bridges)
			{
				if (RM_SuspensionMath.FloodDamage(r.tier, 100) <= 0)
				{
					continue;
				}
				for (int lane = 0; lane < r.width; lane++)
				{
					for (int i = 1; i <= r.LastDeck; i++)
					{
						IntVec3 c = r.Cell(lane, i);
						if (c.InBounds(map) && map.terrainGrid.TempTerrainAt(c)?.IsWater == true
							&& RM_MapComponent_SuspensionBridges.DeckAt(map, c) is Building_SuspensionDeck d)
						{
							hit.Add(d);
						}
					}
				}
			}
			foreach (Building_SuspensionDeck d in hit)
			{
				if (!d.Spawned || d.Destroyed)
				{
					continue;
				}
				int dmg = RM_SuspensionMath.FloodDamage(d.Tier, d.MaxHitPoints);
				FloodHits += dmg;
				d.TakeDamage(new DamageInfo(DamageDefOf.Deterioration, dmg));
			}
		}
	}

	/// <summary>SUSPENSION_WATERS_BUILD_MAY_BACKTRACK: a deck over natural water is walking ground: the path grid answers the
	/// deck's own cost instead of the water's (10000 on deep water; still closed by an impassable thing or a fence on it). Last,
	/// after the swim cost (a deck is not swum).</summary>
	[HarmonyPatch(typeof(PathGrid), nameof(PathGrid.CalculatedCostAt))]
	[RimMandrake.Shared.PatchFeature("Suspension bridges over natural water", typeof(RM_SuspensionSettings), "suspensionOverWater")]
	public static class RM_Patch_SuspensionDeckOverDeepWater
	{
		[HarmonyPostfix]
		[HarmonyPriority(Priority.Last)]
		public static void Postfix(PathGrid __instance, IntVec3 c, ref int __result)
		{
			Map map = __instance.map;
			if (map == null || !c.InBounds(map))
			{
				return;
			}
			TerrainDef t = map.terrainGrid.TerrainAt(c);
			if (t == null || !t.IsWater)
			{
				return;   // a deck over a dug hole is priced by RM_Patch_PathGrid_PitCoverCost
			}
			if (!(RM_MapComponent_SuspensionBridges.DeckAt(map, c) is Building_SuspensionDeck))
			{
				return;
			}
			int cost = 0;
			List<Thing> list = map.thingGrid.ThingsListAt(c);
			for (int i = 0; i < list.Count; i++)
			{
				ThingDef d = list[i].def;
				if (d.passability == Traversability.Impassable || (!__instance.def.fencePassable && d.building != null && d.building.isFence))
				{
					__result = 10000;
					return;
				}
				if (d.pathCost > cost)
				{
					cost = d.pathCost;
				}
			}
			__result = cost;
		}
	}

	/// <summary>
	/// SUSPENSION_ART_RESKIN_HE_SEES_FIRST (construction design §5; parent §8): the suspension bridge parts in the four looks,
	/// through the shared style picker FlowWorks' pipes, tanks and weir use (Machinery/PipeLook.cs: a look menu on the build
	/// button, the default look from the pipes' setting, a legacy unstyled part drawn in the default look). One ThingStyleDef
	/// per part per look, <c>&lt;part&gt;_&lt;Look&gt;</c> (Defs/Pits/ThingDefs/RM_SuspensionStyles.xml). The drag designators place
	/// every part of one bridge in the look picked on its button; the railings and the wreck follow the bridge's look. The rope
	/// type is Scrapper-only and keeps its own art. Registered only when the style defs are loaded (installed with their art).
	/// Item title "he sees first" is superseded by the owner's 2026-10-18 ruling: new art is accepted the first time.
	/// </summary>
	[StaticConstructorOnStartup]
	public static class RM_SuspensionLooks
	{
		public static readonly string[] StyledDefs =
		{
			"RM_SuspensionDeck_Timber", "RM_SuspensionDeck_Steel", "RM_SuspensionDeck_Heavy", "RM_SuspensionDeck_SteelGrated",
			"RM_SuspensionDeck_HeavyGrated", "RM_SuspensionJetty_Steel", "RM_SuspensionJetty_Heavy", "RM_SuspensionAnchor_Timber",
			"RM_SuspensionAnchor_Steel", "RM_SuspensionAnchor_Heavy", "RM_SuspensionTower", "RM_SuspensionRailing", "RM_SuspensionWreck",
		};

		static RM_SuspensionLooks()
		{
			if (DefDatabase<ThingStyleDef>.GetNamedSilentFail(Machinery.PipeStyles.StyleDefName(StyledDefs[0], Machinery.PipeStyles.Scrapper)) != null)
			{
				Machinery.PipeLook.Core.Register(StyledDefs, Machinery.PipeStyles.StyleDefName);
			}
		}

		/// <summary>The look the build button will place now (its menu pick, else the default look), or null if unstyled.</summary>
		public static string LookFor(Designator_Build des)
		{
			ThingStyleDef s = Machinery.PipeLook.Core.Resolve(des);
			return s == null ? null : Machinery.PipeLook.Core.LookOfStyle(s);
		}

		public static ThingStyleDef StyleFor(ThingDef d, string look)
		{
			return look == null ? null : Machinery.PipeLook.Core.StyleFor(d, look);
		}

		/// <summary>Give a part made in code (god mode, a railing, a wreck) its bridge's look.</summary>
		public static void Apply(Thing t, string look)
		{
			ThingStyleDef s = StyleFor(t?.def, look);
			if (s != null)
			{
				t.StyleDef = s;
			}
		}
	}
}
