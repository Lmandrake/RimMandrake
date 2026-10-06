using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.RiverWorks
{
	/// <summary>
	/// Rope ferry (owner card 3, 2026-10-03: ferry included). Two posts on opposite banks string a
	/// rope between them when the straight line crosses moving water; every cell on the line is exempt
	/// from the carry (and stops drift there - the rope catches it). Drafted colonists cross along
	/// the rope. KNOWN LIMIT, deliberate for this slice: undrafted pathing still sees the water's
	/// perceived cost, so ordinary jobs do not yet prefer the rope (design §4 "the hardest piece").
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
				if (d > RM_RiverWorksSettings.ferryMaxSpan || d >= bestDist || !LineCrossesWater(Position, other.Position))
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
			if (p == null || !RM_RiverWorksSettings.ferryEnabled)
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
				+ RM_RiverWorksSettings.ferryMaxSpan + " cells.";
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
			Harmony h = new Harmony("mandrake.rm.riverworks");
			MethodInfo target = AccessTools.Method(typeof(Flood), "CanFloodSpreadInto");
			if (target == null)
			{
				Log.Warning("[River Works] Flood.CanFloodSpreadInto not found; the levee-off setting does nothing.");
				return;
			}
			h.Patch(target, postfix: new HarmonyMethod(typeof(RM_RiverWorksHarmony), nameof(LeveePostfix)));
		}

		private static MethodInfo potentially;

		public static void LeveePostfix(Flood __instance, IntVec3 cell, ref bool __result)
		{
			if (__result || RM_RiverWorksSettings.stakeLineLevee || !RM_RiverWorksSettings.WorksActive)
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
}
