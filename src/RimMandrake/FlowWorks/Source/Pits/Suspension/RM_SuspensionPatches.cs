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
			bool ok = RM_SuspensionMath.MayBuildDeck(i, r.length, k =>
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
				__result = ex.ExcavatedDepthAt(c) > 0;
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
			float load = b.SpanLoad(r, RM_SuspensionMath.SegmentOf(i, r.Supports));
			string line = RM_SuspensionMath.ReadoutLine(r.tier, load, r.RatingKg);
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

	/// <summary>SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD: the floor band under a suspension deck. Until that item lands nobody
	/// is ever in it (a deck is a wall from below).</summary>
	public static class RM_SuspensionUnderpass
	{
		public static bool InFloorBand(Pawn p)
		{
			return false;
		}
	}
}
