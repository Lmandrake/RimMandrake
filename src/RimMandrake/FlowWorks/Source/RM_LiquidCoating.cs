using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RIMMANDRAKE_BUILD_FLOWWORKS_COATING_WASH_PASSED_ON_NOTHING (bar inv_liquid_coating, owner card 2026-11-14: <i>"A pawn
	/// who comes out of oil, tar, blood or another staining liquid carries it as a named condition with a clean, not crude,
	/// look, and walking into normal water plainly washes it off."</i>). Once a second: a pawn wading a liquid whose FluidDef
	/// <c>coats</c> is remembered; when it steps out it carries RM_LiquidCoat, named for that liquid ("coated in oil"); a
	/// pawn wading a liquid that <c>washesCoat</c> (water, icy water, or Water-tagged natural ground no LiquidDef claims) loses it.
	/// Both say so over the pawn's head, so nobody changes without a readable sign. The coat is a condition only: no stat
	/// effect, no graphic (its look waits on RIMMANDRAKE_DESIGN_LIQUID_DIRT_AS_CONDITION_NOT_GRAPHICS). It also fades on
	/// its own after liquidCoatFadeDays. Mod Setting liquidCoatEnabled (off: no coat, and any coat comes off).
	/// </summary>
	public static class RM_LiquidCoating
	{
		public const int IntervalTicks = 60;
		public const string CoatDefName = "RM_LiquidCoat";

		/// <summary>The coating liquid each pawn (thingIDNumber) is wading now; not saved (a reload mid-wade loses one coat).</summary>
		private static readonly Dictionary<int, FluidDef> wading = new Dictionary<int, FluidDef>();
		private static Dictionary<TerrainDef, FluidDef> byFillTerrain;
		private static HediffDef coatDef;

		private static readonly Color CoatText = new Color(0.85f, 0.75f, 0.55f);
		private static readonly Color WashText = new Color(0.6f, 0.8f, 1f);

		public static HediffDef CoatDef => coatDef ?? (coatDef = DefDatabase<HediffDef>.GetNamedSilentFail(CoatDefName));

		public static void Tick(Map map, RM_MapComponent_Excavation ex)
		{
			if (!RimMandrakeFlowWorksSettings.liquidCoatEnabled || Find.TickManager.TicksGame % IntervalTicks != 0 || CoatDef == null)
			{
				return;
			}
			IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn p = pawns[i];
				if (p.Dead || p.health == null || p.Flying)
				{
					continue;
				}
				FluidDef f = LiquidUnder(map, ex, p.Position);
				int id = p.thingIDNumber;
				if (f != null && f.coats)
				{
					wading[id] = f;
					continue;
				}
				if (wading.TryGetValue(id, out FluidDef left))
				{
					wading.Remove(id);
					Coat(p, left);
				}
				if (f != null && f.washesCoat)
				{
					Wash(p, f);
				}
			}
		}

		/// <summary>The liquid a pawn at <paramref name="c"/> wades, or null on dry ground: a wet dug cell's recorded fluid,
		/// else a natural liquid terrain's (RM_FluidIdentity), else a FluidDef's own fill or spill terrain, else plain natural
		/// water (a Water-tagged terrain no LiquidDef claims) reads as RM_Fluid_Water.</summary>
		public static FluidDef LiquidUnder(Map map, RM_MapComponent_Excavation ex, IntVec3 c)
		{
			if (ex != null && ex.IsExcavated(c))
			{
				return ex.WetAt(c) ? ex.FluidAt(c) ?? ex.ActiveFluid : null;
			}
			TerrainDef t = map.terrainGrid.TerrainAt(c);
			FluidDef f = RM_FluidIdentity.FluidOfTerrain(t) ?? FluidOfFillTerrain(t);
			if (f != null)
			{
				return f;
			}
			// natural slime ground carries the Water tag too: it is not water to wash in
			return t != null && t.IsWater && RM_SlimeSlip.NaturalSlime(map, c) == null ? RimMandrakeFlowWorks_DefOf.RM_Fluid_Water : null;
		}

		private static FluidDef FluidOfFillTerrain(TerrainDef t)
		{
			if (t == null)
			{
				return null;
			}
			if (byFillTerrain == null)
			{
				var d = new Dictionary<TerrainDef, FluidDef>();
				foreach (FluidDef f in DefDatabase<FluidDef>.AllDefsListForReading)
				{
					foreach (TerrainDef ft in new[] { f.floodTerrain, f.fillTerrainVeryShallow, f.fillTerrainHalf, f.fillTerrainBrim, f.fillTerrainSuperdeep })
					{
						if (ft != null && !d.ContainsKey(ft))
						{
							d[ft] = f;
						}
					}
				}
				byFillTerrain = d;
			}
			return byFillTerrain.TryGetValue(t, out FluidDef r) ? r : null;
		}

		/// <summary>Put (or refresh) the coat of <paramref name="f"/> on <paramref name="p"/>.</summary>
		public static void Coat(Pawn p, FluidDef f)
		{
			string liquid = f.label ?? f.defName;
			Hediff_LiquidCoat h = p.health.hediffSet.GetFirstHediffOfDef(CoatDef) as Hediff_LiquidCoat;
			bool news = h == null || h.liquid != liquid;
			if (h == null)
			{
				h = (Hediff_LiquidCoat)HediffMaker.MakeHediff(CoatDef, p);
				h.liquid = liquid;
				p.health.AddHediff(h);
			}
			h.liquid = liquid;
			h.ageTicks = 0;
			if (news && p.Map != null)
			{
				MoteMaker.ThrowText(p.DrawPos + new Vector3(0f, 0f, 0.5f), p.Map, "Coated in " + liquid, CoatText, 3.5f);
			}
		}

		/// <summary>Wash any coat off <paramref name="p"/> in <paramref name="inWater"/>; true if there was one.</summary>
		public static bool Wash(Pawn p, FluidDef inWater)
		{
			Hediff_LiquidCoat h = p.health.hediffSet.GetFirstHediffOfDef(CoatDef) as Hediff_LiquidCoat;
			if (h == null)
			{
				return false;
			}
			p.health.RemoveHediff(h);
			if (p.Map != null)
			{
				MoteMaker.ThrowText(p.DrawPos + new Vector3(0f, 0f, 0.5f), p.Map,
					"Washed off the " + (h.liquid ?? "coat") + " in the " + (inWater?.label ?? "water"), WashText, 3.5f);
			}
			return true;
		}

		/// <summary>static_call surface: "" -&gt; "COAT n enabled= | id@x,z liquid= coat= wading=" for every pawn coated or
		/// wading a liquid. "x,z" narrows to the pawns on that cell.</summary>
		public static string ProofReport(string arg)
		{
			Map map = Find.CurrentMap;
			if (map == null) return "REFUSED: no current map";
			RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
			IntVec3 only = IntVec3.Invalid;
			string[] xz = (arg ?? "").Split(',');
			if (xz.Length == 2 && int.TryParse(xz[0].Trim(), out int x) && int.TryParse(xz[1].Trim(), out int z))
			{
				only = new IntVec3(x, 0, z);
			}
			var rows = new List<string>();
			foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
			{
				if (only.IsValid && p.Position != only) continue;
				FluidDef f = LiquidUnder(map, ex, p.Position);
				Hediff_LiquidCoat h = p.health?.hediffSet?.GetFirstHediffOfDef(CoatDef) as Hediff_LiquidCoat;
				if (f == null && h == null && !only.IsValid) continue;
				rows.Add(p.ThingID + "@" + p.Position.x + "," + p.Position.z + " liquid=" + (f?.defName ?? "none")
					+ " coat=" + (h?.liquid ?? "none")
					+ " wading=" + (wading.TryGetValue(p.thingIDNumber, out FluidDef w) ? w.defName : "none"));
			}
			return "COAT " + rows.Count + " enabled=" + RimMandrakeFlowWorksSettings.liquidCoatEnabled + " | " + string.Join(" | ", rows);
		}
	}

	/// <summary>RM_LiquidCoat: "coated in &lt;liquid&gt;", gone in water (RM_LiquidCoating), after liquidCoatFadeDays, or with
	/// the setting off.</summary>
	public class Hediff_LiquidCoat : HediffWithComps
	{
		public string liquid;

		public override string LabelBase => "coated in " + (liquid ?? "liquid");

		public override bool ShouldRemove => base.ShouldRemove || !RimMandrakeFlowWorksSettings.liquidCoatEnabled
			|| ageTicks > Mathf.RoundToInt(RimMandrakeFlowWorksSettings.liquidCoatFadeDays * GenDate.TicksPerDay);

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref liquid, "liquid");
		}
	}
}
