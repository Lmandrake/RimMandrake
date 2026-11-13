using System.Collections.Generic;
using System.Globalization;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>What a bath in a non-water liquid costs (owner by card 2026-11-12: "each with a cost"), data on its FluidDef.
	/// Each part follows its own setting (RM_GeyserPitSettings geyserBathFilthEnabled / MoodCost / Slip).</summary>
	public class RM_BathCost
	{
		public ThingDef filth;
		public int filthCount;
		public ThoughtDef thought;
		public int slipStunTicks;
	}

	/// <summary>
	/// RIMMANDRAKE_SINK_GEYSER_INTO_PIT_BUBBLING_HOT_TUB: a steam geyser in a dug pit (spec
	/// design/specs/geyser_in_pit_hot_tub_2026-11-12.md). The geyser is never moved or replaced: its SEAT is read from the
	/// excavation grid every time (the shallowest of its four squares, RM_GeyserTubMath.SeatNotches), so no field is saved and
	/// filling the pit back in raises it. Drawn at the seat by the one under-liquid law (RM_SubmergeDraw: a thing standing on
	/// the floor, RM_GeyserTubMath.GeyserMetres tall) and lowered by the pawns' sink while that keeps it inside the pit. Its
	/// puffs rise from the seat; once liquid covers the vent they stop and the plume (<see cref="RM_MapComponent_GeyserPits"/>)
	/// bubbles instead. Vanilla heat is untouched. A covered, uncapped geyser under a bathable liquid is a pool
	/// (JobDriver_RM_SoakInGeyserPool).
	/// </summary>
	public static class RM_GeyserPit
	{
		private static readonly AccessTools.FieldRef<Building_SteamGeyser, IntermittentSteamSprayer> SprayerOf =
			AccessTools.FieldRefAccess<Building_SteamGeyser, IntermittentSteamSprayer>("steamSprayer");
		private static readonly AccessTools.FieldRef<IntermittentSteamSprayer, int> SprayTicksLeft =
			AccessTools.FieldRefAccess<IntermittentSteamSprayer, int>("sprayTicksLeft");
		internal static readonly AccessTools.FieldRef<IntermittentSteamSprayer, Thing> ParentOf =
			AccessTools.FieldRefAccess<IntermittentSteamSprayer, Thing>("parent");

		public static bool On => RM_GeyserPitSettings.geyserSinksEnabled;

		/// <summary>State reads for the live proof (RM_GeyserPoolProof): counted since the last reset.</summary>
		public static int plumeBubbles, dryPuffs, coveredPuffsStopped;

		/// <summary>The geyser whose sprayer is ticking now (set around IntermittentSteamSprayer.SteamSprayerTick).</summary>
		internal static Building_SteamGeyser spraying;

		private const int MaxRoomRows = 5;

		public struct State
		{
			public int seat;
			public IntVec3 seatCell;
			public float levelMetres;
			public FluidDef fluid;
			public bool covered, capped;
		}

		private static readonly int[] depthBuf = new int[4];

		public static State Read(Building_SteamGeyser g)
		{
			State s = default;
			if (g == null || !g.Spawned)
			{
				return s;
			}
			s.capped = g.harvester != null;
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(g.Map);
			if (eng == null)
			{
				return s;
			}
			int i = 0, low = int.MaxValue;
			foreach (IntVec3 c in g.OccupiedRect())
			{
				int d = eng.HollowDepthAt(c);
				if (i < depthBuf.Length)
				{
					depthBuf[i++] = d;
				}
				if (d < low)
				{
					low = d;
					s.seatCell = c;
				}
			}
			s.seat = i == depthBuf.Length ? RM_GeyserTubMath.SeatNotches(depthBuf) : 0;
			if (s.seat <= 0)
			{
				return s;
			}
			float lv = RM_UnderLiquid.NoteLevel(RM_SubmergeDraw.NoteAt(eng, s.seatCell));
			s.levelMetres = (lv > s.seat ? s.seat : lv) * RM_UnderLiquid.Notch;
			if (s.levelMetres > 0f)
			{
				s.fluid = FluidOn(g.Map, eng, s.seatCell);
			}
			s.covered = RM_GeyserTubMath.Covered(s.levelMetres);
			return s;
		}

		/// <summary>The liquid on a cell: the one recorded, else the terrain's, else (an unrecorded wet square takes the map
		/// default) fresh water.</summary>
		public static FluidDef FluidOn(Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			return eng.FluidAt(c) ?? RM_FluidIdentity.FluidOfTerrain(map.terrainGrid.TerrainAt(c)) ?? RimMandrakeFlowWorks_DefOf.RM_Fluid_Water;
		}

		public static bool Bathable(FluidDef f)
		{
			return f != null && RM_GeyserTubMath.GroupAllowed(f.bathGroup, RM_GeyserPitSettings.geyserBathTarEnabled,
				RM_GeyserPitSettings.geyserBathOilEnabled, RM_GeyserPitSettings.geyserBathBloodEnabled, RM_GeyserPitSettings.geyserBathSlimeEnabled);
		}

		/// <summary>A pool: the feature on, and a bathable liquid over an uncapped vent it covers.</summary>
		public static bool PoolOpen(Building_SteamGeyser g, out State s)
		{
			s = Read(g);
			return On && RM_GeyserPitSettings.geyserPoolEnabled && s.seat > 0
				&& RM_GeyserTubMath.PoolSafe(s.fluid != null, Bathable(s.fluid), s.covered, s.capped);
		}

		public static bool Spraying(Building_SteamGeyser g)
		{
			IntermittentSteamSprayer sp = g == null ? null : SprayerOf(g);
			return sp != null && SprayTicksLeft(sp) > 0;
		}

		/// <summary>How far south the print and its steam are drawn (cells, &lt;= 0): the pawns' sink for the seat, held inside
		/// the pit (RM_GeyserTubMath.SeatSink over the rows of pit at least as deep south of the footprint).</summary>
		public static float PrintShiftZ(Building_SteamGeyser g)
		{
			if (!On || g == null || !g.Spawned || !RimMandrakeFlowWorksSettings.pitDepthDrawOffsetEnabled)
			{
				return 0f;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(g.Map);
			State s = Read(g);
			if (eng == null || s.seat <= 0)
			{
				return 0f;
			}
			CellRect r = g.OccupiedRect();
			int room = 0;
			for (int k = 1; k <= MaxRoomRows; k++)
			{
				bool deep = true;
				for (int x = r.minX; x <= r.maxX && deep; x++)
				{
					IntVec3 c = new IntVec3(x, 0, r.minZ - k);
					deep = c.InBounds(g.Map) && eng.HollowDepthAt(c) >= s.seat;
				}
				if (!deep)
				{
					break;
				}
				room++;
			}
			return -RM_GeyserTubMath.SeatSink(s.seat, RimMandrakeFlowWorksSettings.pitSinkPerLevel, room);
		}

		/// <summary>FleckMaker.ThrowAirPuffUp while <see cref="spraying"/> is ticking: false = no puff (the vent is covered: the
		/// plume replaces it); otherwise the puff rises from the drawn seat. The heat push beside it is never touched.</summary>
		internal static bool Puff(ref Vector3 loc)
		{
			State s = Read(spraying);
			if (s.seat <= 0)
			{
				return true;
			}
			if (s.covered)
			{
				coveredPuffsStopped++;
				return false;
			}
			loc.z += PrintShiftZ(spraying);
			dryPuffs++;
			return true;
		}

		/// <summary>The cells of an open pool <paramref name="p"/> could soak in: in reach of the vent's centre, dug, wet with
		/// the pool's own liquid, standable, and not over its head unless it keeps its head up (FlowWorks drowning).</summary>
		public static IEnumerable<IntVec3> SoakCells(Building_SteamGeyser g, State s, Pawn p)
		{
			Map map = g.Map;
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null)
			{
				yield break;
			}
			float reach = RM_GeyserPitSettings.geyserPoolReach;
			Vector3 centre = g.TrueCenter();
			CellRect around = g.OccupiedRect().ExpandedBy(Mathf.CeilToInt(reach)).ClipInsideMap(map);
			foreach (IntVec3 c in around)
			{
				if (!RM_GeyserTubMath.InReach(c.x + 0.5f - centre.x, c.z + 0.5f - centre.z, reach) || !c.Standable(map))
				{
					continue;
				}
				int d = eng.HollowDepthAt(c);
				if (d <= 0)
				{
					continue;
				}
				float lv = RM_UnderLiquid.NoteLevel(RM_SubmergeDraw.NoteAt(eng, c));
				float w = (lv > d ? d : lv) * RM_UnderLiquid.Notch;
				if (!(w > 0f) || FluidOn(map, eng, c) != s.fluid)
				{
					continue;
				}
				if (p != null && RM_Drowning.HeadUnder(p, w) && !RM_Drowning.KeepsHeadUp(p, c, w))
				{
					continue;
				}
				yield return c;
			}
		}

		/// <summary>A pawn that may be sent to soak at all: not downed, not an animal, not a mechanoid or other unfeeling body.</summary>
		public static bool MaySoak(Pawn p)
		{
			return p != null && p.Spawned && !p.Downed && p.RaceProps.Humanlike && !p.InMentalState && p.health?.hediffSet != null;
		}

		/// <summary>The nearest free soak cell of an open pool this pawn can reserve and reach, or invalid.</summary>
		public static IntVec3 FreeSoakCell(Building_SteamGeyser g, State s, Pawn p)
		{
			IntVec3 best = IntVec3.Invalid;
			float bestD = float.MaxValue;
			foreach (IntVec3 c in SoakCells(g, s, p))
			{
				float dd = (c - p.Position).LengthHorizontalSquared;
				if (dd < bestD && p.CanReserveAndReach(c, PathEndMode.OnCell, Danger.Some))
				{
					best = c;
					bestD = dd;
				}
			}
			return best;
		}

		/// <summary>Is <paramref name="p"/> in the soaking toil of a geyser pool now (the clothes postfixes read it).</summary>
		public static bool Soaking(Pawn p)
		{
			return p?.jobs?.curDriver is JobDriver_RM_SoakInGeyserPool d && d.soaking;
		}

		/// <summary>The healing number is the experience: written onto both hediffs' stages from the setting before each soak.</summary>
		public static void ApplyHealing()
		{
			float h = RM_GeyserPitSettings.geyserPoolHealing;
			foreach (string n in new[] { "RM_HotPoolSoak", "RM_HotPoolAfterglow" })
			{
				HediffDef d = DefDatabase<HediffDef>.GetNamedSilentFail(n);
				if (d?.stages != null && d.stages.Count > 0)
				{
					d.stages[0].naturalHealingFactor = h;
				}
			}
		}

		public static RM_MapComponent_GeyserPits PitsOf(Map map) => map?.GetComponent<RM_MapComponent_GeyserPits>();
	}

	/// <summary>
	/// The geysers of one map (kept from spawn, never a map scan per tick) and the plume: while liquid covers a sunk, uncapped
	/// vent in view, RM_Fleck_LiquidBubble (the bubble every liquid surface uses; real plume art is its own art item) is thrown
	/// over the vent at the liquid's own bubble colour, larger and clustered to the centre, fewer and bigger in thick liquids,
	/// with a ripple ring in thin ones and a steam wisp off a clear one while it sprays. Every 250 ticks a geyser whose seat
	/// moved re-meshes its squares so the print follows the dig. Cosmetic RNG isolated (Rand.PushState).
	/// </summary>
	public class RM_MapComponent_GeyserPits : MapComponent
	{
		private readonly List<Building_SteamGeyser> geysers = new List<Building_SteamGeyser>();
		private readonly Dictionary<int, int> seatDrawn = new Dictionary<int, int>();
		private static FleckDef bubbleFleck;

		public RM_MapComponent_GeyserPits(Map map) : base(map)
		{
		}

		public List<Building_SteamGeyser> Geysers => geysers;

		public override void FinalizeInit()
		{
			base.FinalizeInit();
			geysers.Clear();
			foreach (Thing t in map.listerThings.ThingsOfDef(ThingDefOf.SteamGeyser))
			{
				Note(t as Building_SteamGeyser);
			}
		}

		public void Note(Building_SteamGeyser g)
		{
			if (g != null && !geysers.Contains(g))
			{
				geysers.Add(g);
			}
		}

		/// <summary>True when <paramref name="c"/> is in the reach of a sunk, uncapped geyser (FreezeManager: it never freezes).</summary>
		public bool Warmed(IntVec3 c)
		{
			for (int i = 0; i < geysers.Count; i++)
			{
				Building_SteamGeyser g = geysers[i];
				if (g == null || !g.Spawned || g.harvester != null)
				{
					continue;
				}
				Vector3 ctr = g.TrueCenter();
				float dx = c.x + 0.5f - ctr.x, dz = c.z + 0.5f - ctr.z;
				if (dx * dx + dz * dz > 25f || !RM_GeyserTubMath.InReach(dx, dz, RM_GeyserPitSettings.geyserPoolReach))
				{
					continue;
				}
				if (RM_GeyserPit.Read(g).seat > 0)
				{
					return true;
				}
			}
			return false;
		}

		public override void MapComponentTick()
		{
			if (!RM_GeyserPit.On || geysers.Count == 0)
			{
				return;
			}
			bool remesh = Find.TickManager.TicksGame % 250 == 0;
			bool show = RM_GeyserPitSettings.geyserPlumeEnabled && Find.CurrentMap == map && !RimWorld.Planet.WorldRendererUtility.WorldRendered;
			if (!remesh && !show)
			{
				return;
			}
			CellRect view = show ? Find.CameraDriver.CurrentViewRect.ExpandedBy(2) : CellRect.Empty;
			for (int i = geysers.Count - 1; i >= 0; i--)
			{
				Building_SteamGeyser g = geysers[i];
				if (g == null || g.Destroyed || g.Map != map)
				{
					geysers.RemoveAt(i);
					continue;
				}
				if (!g.Spawned)
				{
					continue;
				}
				if (remesh)
				{
					Remesh(g);
				}
				if (show && view.Contains(g.Position))
				{
					Plume(g);
				}
			}
		}

		private void Remesh(Building_SteamGeyser g)
		{
			int seat = RM_GeyserPit.Read(g).seat;
			if (seatDrawn.TryGetValue(g.thingIDNumber, out int was) && was == seat)
			{
				return;
			}
			seatDrawn[g.thingIDNumber] = seat;
			foreach (IntVec3 c in g.OccupiedRect().ExpandedBy(1).ClipInsideMap(map))
			{
				map.mapDrawer.MapMeshDirty(c, (ulong)MapMeshFlagDefOf.Things | (ulong)MapMeshFlagDefOf.Buildings);
			}
		}

		private void Plume(Building_SteamGeyser g)
		{
			RM_GeyserPit.State s = RM_GeyserPit.Read(g);
			if (s.seat <= 0 || !s.covered || s.capped || s.fluid == null)
			{
				return;
			}
			if (bubbleFleck == null)
			{
				bubbleFleck = DefDatabase<FleckDef>.GetNamedSilentFail("RM_Fleck_LiquidBubble");
				if (bubbleFleck == null)
				{
					return;
				}
			}
			bool spraying = RM_GeyserPit.Spraying(g);
			int tpt = s.fluid.ticksPerTile;
			float rate = RM_GeyserTubMath.PlumeRate(spraying, tpt, RM_GeyserPitSettings.geyserPlumeDensity);
			Rand.PushState(Gen.HashCombineInt(Find.TickManager.TicksGame, g.thingIDNumber));
			try
			{
				int n = RM_GeyserTubMath.BubblesThisTick(rate, Rand.Value);
				if (n <= 0)
				{
					return;
				}
				RM_LiquidSurfaceLook look = RM_SubmergeDraw.LookAt(map, RM_SuperdeepTrap.EngineOf(map), s.seatCell);
				Color tint = look != null ? look.bubbleColor : new Color(0.9f, 0.95f, 1f);
				bool thick = RM_GeyserTubMath.Thick(tpt);
				Vector3 ctr = g.TrueCenter();
				ctr.z += RM_GeyserPit.PrintShiftZ(g);
				ctr.y = AltitudeLayer.MoteLow.AltitudeFor();
				for (int k = 0; k < n; k++)
				{
					Vector2 off = Rand.InsideUnitCircle * (0.95f * Rand.Value);   // clustered toward the vent's centre
					Vector3 at = ctr + new Vector3(off.x, 0f, off.y);
					if (!at.ShouldSpawnMotesAt(map))
					{
						continue;
					}
					FleckCreationData d = FleckMaker.GetDataStatic(at, map, bubbleFleck,
						Rand.Range(RM_GeyserTubMath.PlumeScaleMin(tpt), RM_GeyserTubMath.PlumeScaleMax(tpt)));
					d.instanceColor = tint;
					d.velocityAngle = Rand.Range(0f, 360f);
					d.velocitySpeed = thick ? Rand.Range(0f, 0.03f) : Rand.Range(0.02f, 0.12f);
					map.flecks.CreateFleck(d);
					RM_GeyserPit.plumeBubbles++;
					if (spraying && !thick && Rand.Chance(0.6f))
					{
						FleckMaker.WaterRipple(at, map, Rand.Range(0.6f, 1.2f));
					}
				}
				if (spraying && look != null && look.seeThrough > 0f && Rand.Chance(0.15f))
				{
					FleckMaker.ThrowAirPuffUp(ctr, map);   // a faint steam wisp off the surface of a clear liquid
				}
			}
			finally
			{
				Rand.PopState();
			}
		}
	}

	/// <summary>Every geyser that spawns is kept on its map's list.</summary>
	[HarmonyPatch(typeof(Building_SteamGeyser), nameof(Building_SteamGeyser.SpawnSetup))]
	[RimMandrake.Shared.PatchFeature("Geysers in pits (list)", typeof(RimMandrake.FlowWorks.RM_GeyserPitSettings), "geyserSinksEnabled")]
	internal static class Patch_RM_GeyserSpawn
	{
		[HarmonyPostfix]
		private static void Postfix(Building_SteamGeyser __instance, Map map)
		{
			RM_GeyserPit.PitsOf(map)?.Note(__instance);
		}
	}

	/// <summary>Marks the geyser whose sprayer is ticking, so its puffs rise from the seat or stop under liquid.</summary>
	[HarmonyPatch(typeof(IntermittentSteamSprayer), nameof(IntermittentSteamSprayer.SteamSprayerTick))]
	[RimMandrake.Shared.PatchFeature("Geysers in pits (steam from the seat)", typeof(RimMandrake.FlowWorks.RM_GeyserPitSettings), "geyserSinksEnabled")]
	internal static class Patch_RM_GeyserSprayerTick
	{
		[HarmonyPrefix]
		private static void Prefix(IntermittentSteamSprayer __instance)
		{
			RM_GeyserPit.spraying = RM_GeyserPit.On ? RM_GeyserPit.ParentOf(__instance) as Building_SteamGeyser : null;
		}

		[HarmonyFinalizer]
		private static void Finalizer()
		{
			RM_GeyserPit.spraying = null;
		}
	}

	/// <summary>The puff itself (only while a geyser's sprayer ticks; GenTemperature.PushHeat is a separate call and runs).</summary>
	[HarmonyPatch(typeof(FleckMaker), nameof(FleckMaker.ThrowAirPuffUp))]
	[RimMandrake.Shared.PatchFeature("Geysers in pits (puffs)", typeof(RimMandrake.FlowWorks.RM_GeyserPitSettings), "geyserSinksEnabled")]
	internal static class Patch_RM_GeyserPuff
	{
		[HarmonyPrefix]
		private static bool Prefix(ref Vector3 loc)
		{
			return RM_GeyserPit.spraying == null || RM_GeyserPit.Puff(ref loc);
		}
	}

	/// <summary>The pool's reach never freezes while its geyser is sunk and uncapped (like vanilla's hot spring terrain).</summary>
	[HarmonyPatch(typeof(FreezeManager), "CanFreeze")]
	[RimMandrake.Shared.PatchFeature("Geysers in pits (no ice over the vent)", typeof(RimMandrake.FlowWorks.RM_GeyserPitSettings), "geyserSinksEnabled")]
	internal static class Patch_RM_GeyserNoFreeze
	{
		[HarmonyPostfix]
		private static void Postfix(IntVec3 c, Map ___map, ref bool __result)
		{
			if (__result && RM_GeyserPit.On && RM_GeyserPit.PitsOf(___map)?.Warmed(c) == true)
			{
				__result = false;
			}
		}
	}

	/// <summary>A geothermal generator (anything placed by PlaceWorker_OnSteamGeyser) may stand on a DRY sunk geyser: the
	/// vent is bedrock, so the dug floor's missing Heavy affordance is waived on the geyser's own 2x2 only; every other square
	/// of the generator's footprint still needs its ground. Wet: refused, as before.</summary>
	[HarmonyPatch(typeof(GenConstruct), nameof(GenConstruct.CanBuildOnTerrain))]
	[RimMandrake.Shared.PatchFeature("Geysers in pits (generator caps a dry vent)", typeof(RimMandrake.FlowWorks.RM_GeyserPitSettings), "geyserGeneratorOnSunkEnabled")]
	internal static class Patch_RM_GeyserGeneratorTerrain
	{
		[HarmonyPostfix]
		private static void Postfix(BuildableDef entDef, IntVec3 c, Map map, Rot4 rot, ThingDef stuffDef, ref bool __result)
		{
			if (__result || map == null || !RM_GeyserPit.On || !RM_GeyserPitSettings.geyserGeneratorOnSunkEnabled
				|| !(entDef is ThingDef td) || td.placeWorkers == null || !td.placeWorkers.Contains(typeof(PlaceWorker_OnSteamGeyser)))
			{
				return;
			}
			if (map.thingGrid.ThingAt(c, ThingDefOf.SteamGeyser) is Building_SteamGeyser g && g.Position == c)
			{
				RM_GeyserPit.State s = RM_GeyserPit.Read(g);
				if (s.seat <= 0 || s.levelMetres > 0f)
				{
					return;
				}
				// the waiver is the vent's own squares only: the rest of the generator's footprint still needs its ground
				TerrainAffordanceDef need = entDef.GetTerrainAffordanceNeed(stuffDef);
				CellRect vent = g.OccupiedRect();
				foreach (IntVec3 q in GenAdj.OccupiedRect(c, rot, entDef.Size))
				{
					if (!vent.Contains(q) && (!q.InBounds(map) || (need != null && !q.GetAffordances(map).Contains(need))))
					{
						return;
					}
				}
				__result = true;
			}
		}
	}

	/// <summary>A soaking pawn's clothes are set aside (drawing only, never in portraits).</summary>
	[HarmonyPatch(typeof(PawnRenderNodeWorker_Apparel_Body), nameof(PawnRenderNodeWorker_Apparel_Body.CanDrawNow))]
	[RimMandrake.Shared.PatchFeature("Geyser pool bathers set clothes aside", typeof(RimMandrake.FlowWorks.RM_GeyserPitSettings), "geyserPoolHidesClothes")]
	internal static class Patch_RM_GeyserPoolClothes
	{
		[HarmonyPostfix]
		private static void Postfix(PawnRenderNode node, PawnDrawParms parms, ref bool __result)
		{
			if (__result && !parms.Portrait && RM_GeyserPitSettings.geyserPoolHidesClothes && RM_GeyserPit.Soaking(node?.tree?.pawn))
			{
				__result = false;
			}
		}
	}

	[HarmonyPatch(typeof(PawnRenderNodeWorker_Apparel_Head), nameof(PawnRenderNodeWorker_Apparel_Head.HeadgearVisible))]
	[RimMandrake.Shared.PatchFeature("Geyser pool bathers set headgear aside", typeof(RimMandrake.FlowWorks.RM_GeyserPitSettings), "geyserPoolHidesClothes")]
	internal static class Patch_RM_GeyserPoolHeadgear
	{
		[HarmonyPostfix]
		private static void Postfix(PawnDrawParms parms, ref bool __result)
		{
			if (__result && !parms.Portrait && RM_GeyserPitSettings.geyserPoolHidesClothes && RM_GeyserPit.Soaking(parms.pawn))
			{
				__result = false;
			}
		}
	}

	/// <summary>Live state reads (jawa/static_call RimMandrake.FlowWorks.RM_GeyserPoolProof.Read "&lt;thingID&gt;", or
	/// "reset" to zero the counters), spec 4.2.</summary>
	public static class RM_GeyserPoolProof
	{
		public static string Read(string arg)
		{
			if (arg == "reset")
			{
				RM_GeyserPit.plumeBubbles = RM_GeyserPit.dryPuffs = RM_GeyserPit.coveredPuffsStopped = 0;
				return "reset";
			}
			Map map = Find.CurrentMap;
			Building_SteamGeyser g = null;
			if (map != null)
			{
				foreach (Thing t in map.listerThings.ThingsOfDef(ThingDefOf.SteamGeyser))
				{
					if (string.IsNullOrEmpty(arg) || t.ThingID == arg)
					{
						g = t as Building_SteamGeyser;
						break;
					}
				}
			}
			if (g == null)
			{
				return "spawned=false thingId=" + arg;
			}
			RM_GeyserPit.State s = RM_GeyserPit.Read(g);
			bool pool = RM_GeyserPit.PoolOpen(g, out _);
			int soakers = 0;
			foreach (Pawn p in g.Map.mapPawns.AllPawnsSpawned)
			{
				if (p.CurJob?.targetA.Thing == g && p.CurJobDef?.defName == "RM_SoakInGeyserPool")
				{
					soakers++;
				}
			}
			CultureInfo ci = CultureInfo.InvariantCulture;
			return "spawned=" + g.Spawned + " thingId=" + g.ThingID + " seatNotches=" + s.seat
				+ " drawDz=" + RM_GeyserPit.PrintShiftZ(g).ToString("F3", ci) + " levelMetres=" + s.levelMetres.ToString("F3", ci)
				+ " covered=" + s.covered + " fluid=" + (s.fluid?.defName ?? "none") + " bathable=" + RM_GeyserPit.Bathable(s.fluid)
				+ " pool=" + pool + " spraying=" + RM_GeyserPit.Spraying(g) + " plumeBubbles=" + RM_GeyserPit.plumeBubbles
				+ " dryPuffs=" + RM_GeyserPit.dryPuffs + " coveredPuffsStopped=" + RM_GeyserPit.coveredPuffsStopped
				+ " soakers=" + soakers + " capped=" + s.capped;
		}
	}
}
