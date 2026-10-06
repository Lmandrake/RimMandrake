using Unity.Collections;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Rivers
{
	/// <summary>
	/// Rope ferry (owner card 3, 2026-10-03: ferry included). Two posts on opposite banks string a
	/// rope between them when the straight line crosses moving water; every cell on the line is exempt
	/// from the carry (and stops drift there - the rope catches it). Drafted colonists cross along
	/// the rope; undrafted ones do too while ferryRopeGuidesColonists is on (RM_RopePathing zeroes
	/// the water's undrafted perceived cost on rope cells, so the rope reads as a crossing).
	/// </summary>
	public class RM_Building_FerryPost : Building
	{
		private RM_Building_FerryPost partner;

		public RM_Building_FerryPost Partner => partner != null && partner.Spawned && partner.Map == Map ? partner : null;

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			if (!respawningAfterLoad)
			{
				TryPair();
			}
			map.GetComponent<RM_MapComponent_RiverCurrent>()?.MarkWorksDirty();
		}

		public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
		{
			Map map = Map;
			if (partner != null && partner.partner == this)
			{
				partner.partner = null;
			}
			partner = null;
			base.DeSpawn(mode);
			map?.GetComponent<RM_MapComponent_RiverCurrent>()?.MarkWorksDirty();
		}

		/// <summary>Pair with the nearest unpaired post whose line crosses moving water.</summary>
		public bool TryPair()
		{
			if (Partner != null || Map == null)
			{
				return Partner != null;
			}
			RM_Building_FerryPost best = null;
			float bestDist = float.MaxValue;
			foreach (Thing t in Map.listerThings.ThingsOfDef(def))
			{
				if (!(t is RM_Building_FerryPost other) || other == this || other.Partner != null)
				{
					continue;
				}
				float d = other.Position.DistanceTo(Position);
				if (d > RM_RiversSettings.ferryMaxSpan || d >= bestDist || !LineCrossesWater(Position, other.Position))
				{
					continue;
				}
				best = other;
				bestDist = d;
			}
			if (best == null)
			{
				return false;
			}
			partner = best;
			best.partner = this;
			Map.GetComponent<RM_MapComponent_RiverCurrent>()?.MarkWorksDirty();
			return true;
		}

		private bool LineCrossesWater(IntVec3 a, IntVec3 b)
		{
			foreach (IntVec3 c in GenSight.PointsOnLineOfSight(a, b))
			{
				if (RM_RiverWorks.IsWaterCell(Map, c))
				{
					return true;
				}
			}
			return false;
		}

		public void AddRopeCells(HashSet<int> into)
		{
			RM_Building_FerryPost p = Partner;
			if (p == null || !RM_RiversSettings.ferryEnabled)
			{
				return;
			}
			foreach (IntVec3 c in GenSight.PointsOnLineOfSight(Position, p.Position))
			{
				if (c.InBounds(Map))
				{
					into.Add(Map.cellIndices.CellToIndex(c));
				}
			}
		}

		public override void DrawExtraSelectionOverlays()
		{
			base.DrawExtraSelectionOverlays();
			RM_Building_FerryPost p = Partner;
			if (p != null)
			{
				GenDraw.DrawLineBetween(this.TrueCenter(), p.TrueCenter());
			}
		}

		public override string GetInspectString()
		{
			string s = base.GetInspectString();
			string mine = Partner != null ? "Rope strung to the post across the river." : "No rope: build a second ferry post across moving water within "
				+ RM_RiversSettings.ferryMaxSpan + " cells.";
			return s.NullOrEmpty() ? mine : s + "\n" + mine;
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_References.Look(ref partner, "ferryPartner");
		}
	}

	/// <summary>
	/// The stake-line levee (owner card, 2026-10-03). Vanilla already refuses floodwater into any
	/// edifice cell (Flood.CanFloodSpreadInto: FoundationAt / GetEdifice), so a continuous line of
	/// RM_BankStake holds a SeasonalFlood with no code; a gap leaks. This patch exists only for the
	/// OFF setting: with stakeLineLevee off, a stake cell is let through when nothing else blocks it.
	/// </summary>
	[StaticConstructorOnStartup]
	public static class RM_RiverWorksHarmony
	{
		static RM_RiverWorksHarmony()
		{
			Harmony h = new Harmony("mandrake.rm.flowworks.rivers");
			MethodInfo target = AccessTools.Method(typeof(Flood), "CanFloodSpreadInto");
			if (target == null)
			{
				Log.Warning("[FlowWorks Rivers] Flood.CanFloodSpreadInto not found; the levee-off setting does nothing.");
				return;
			}
			h.Patch(target, postfix: new HarmonyMethod(typeof(RM_RiverWorksHarmony), nameof(LeveePostfix)));
			RM_RopePathing.Patch(h);
		}

		private static MethodInfo potentially;

		public static void LeveePostfix(Flood __instance, IntVec3 cell, ref bool __result)
		{
			if (__result || RM_RiversSettings.stakeLineLevee || !RM_RiversSettings.WorksActive)
			{
				return;
			}
			Map map = __instance.Map;
			Building ed = map != null ? cell.GetEdifice(map) : null;
			if (ed == null || ed.def != RM_RiverWorksDefOf.RM_BankStake || map.terrainGrid.FoundationAt(cell) != null)
			{
				return;
			}
			if (potentially == null)
			{
				potentially = AccessTools.Method(typeof(Flood), "CanFloodPotentiallySpreadInto");
			}
			if (potentially != null && (bool)potentially.Invoke(__instance, new object[] { cell }))
			{
				__result = true;
			}
		}
	}

	/// <summary>
	/// Ferry rope for undrafted colonists (taken over 2026-10-05; slice 2 left it as a known limit).
	/// 1.6 keeps the undrafted perceived terrain cost in PerceptualSource.costUndrafted, filled from
	/// TerrainDef.extraNonDraftedPerceivedPathCost in ComputeAll and re-read per changed cell in
	/// UpdateIncrementally (RimSage, decompiled 1.6). A postfix on both zeroes it on rope cells, so
	/// an everyday job routes along the rope instead of round to a bridge. The real move cost (the
	/// water's pathCost) is untouched; only the reluctance goes. RM_MapComponent_RiverCurrent
	/// notifies the path grid whenever the rope set or this setting changes.
	/// </summary>
	public static class RM_RopePathing
	{
		private static AccessTools.FieldRef<PerceptualSource, Map> mapRef;

		private static AccessTools.FieldRef<PerceptualSource, NativeArray<ushort>> undraftedRef;

		public static bool Active => RM_RiversSettings.WorksActive && RM_RiversSettings.ferryEnabled
			&& RM_RiversSettings.ferryRopeGuidesColonists;

		public static void Patch(Harmony h)
		{
			MethodInfo all = AccessTools.Method(typeof(PerceptualSource), "ComputeAll");
			MethodInfo inc = AccessTools.Method(typeof(PerceptualSource), "UpdateIncrementally");
			if (all == null || inc == null || AccessTools.Field(typeof(PerceptualSource), "costUndrafted") == null
				|| AccessTools.Field(typeof(PerceptualSource), "map") == null)
			{
				Log.Warning("[FlowWorks Rivers] PerceptualSource members not found; undrafted colonists will not use ferry ropes.");
				return;
			}
			mapRef = AccessTools.FieldRefAccess<PerceptualSource, Map>("map");
			undraftedRef = AccessTools.FieldRefAccess<PerceptualSource, NativeArray<ushort>>("costUndrafted");
			HarmonyMethod post = new HarmonyMethod(typeof(RM_RopePathing), nameof(ApplyRope));
			h.Patch(all, postfix: post);
			h.Patch(inc, postfix: post);
		}

		public static void ApplyRope(PerceptualSource __instance)
		{
			if (!Active || mapRef == null)
			{
				return;
			}
			Map map = mapRef(__instance);
			HashSet<int> rope = map?.GetComponent<RM_MapComponent_RiverCurrent>()?.RopeIndicesNoRebuild;
			if (rope == null || rope.Count == 0)
			{
				return;
			}
			NativeArray<ushort> cost = undraftedRef(__instance);
			foreach (int i in rope)
			{
				if (i >= 0 && i < cost.Length)
				{
					cost[i] = 0;
				}
			}
		}

		/// <summary>Proof read: the undrafted perceived cost the path grid holds for a cell.</summary>
		public static int UndraftedCostAt(Map map, IntVec3 c)
		{
			PerceptualSource src = PerceptualSourceOf(map);
			if (src == null || undraftedRef == null)
			{
				return -1;
			}
			return undraftedRef(src)[map.cellIndices.CellToIndex(c)];
		}

		private static PerceptualSource PerceptualSourceOf(Map map)
		{
			PathFinderMapData data = map?.pathFinder?.MapData;
			if (data == null)
			{
				return null;
			}
			foreach (System.Reflection.FieldInfo f in AccessTools.GetDeclaredFields(typeof(PathFinderMapData)))
			{
				if (f.FieldType == typeof(PerceptualSource))
				{
					return f.GetValue(data) as PerceptualSource;
				}
			}
			return null;
		}
	}
}
