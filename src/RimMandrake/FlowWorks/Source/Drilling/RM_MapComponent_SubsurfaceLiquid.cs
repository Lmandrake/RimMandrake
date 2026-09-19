using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.FlowWorks.LiquidTypes;

namespace RimMandrake.FlowWorks.Drilling
{
	/// <summary>
	/// MANY_WATERS_DRILL_BUILDINGS_1 — "maps whose subsurface yields it".
	///
	/// One survey per map, rolled ONCE at FinalizeInit and never re-argued —
	/// the same sticky discipline ruling 16 gives a liquid body's limitless
	/// classification (§ RM_LiquidBody): a lake nobody has dug to is not
	/// classified, and a map nobody has surveyed does not yet know what is
	/// under it, but once it is known it is fixed for the life of the map,
	/// so a drill cannot "re-roll" a dry hole into a productive one by
	/// deconstructing and rebuilding.
	///
	/// This component decides ONE fact per map: does the subsurface yield a
	/// liquid, which one, and how much of it is down there. It does NOT
	/// touch the excavation grid, does NOT create an RM_LiquidBody, and is
	/// NOT a source in ruling 24's sense (a source is terrain). A drill is
	/// its own acquisition route (design doc §3 ruling 3: "you can drill it,
	/// on the right maps, with custom buildings") and stays that way — the
	/// reserve this component owns is spent directly into an adjacent
	/// excavated cell by <see cref="Building_LiquidDrill"/>, through the
	/// same public driver API a flood client uses
	/// (RM_MapComponent_Excavation.TrySetDriverFill), never through
	/// RM_LiquidStock.
	///
	/// MapComponent subclasses are auto-instantiated per map by
	/// Map.FillComponents() (same note as RiverSteamHook.cs) — no
	/// registration needed.
	/// </summary>
	public class RM_MapComponent_SubsurfaceLiquid : MapComponent
	{
		private bool rolled;

		private bool hasYield;

		private LiquidDef yieldedLiquid;

		private float reserveUnits;

		public RM_MapComponent_SubsurfaceLiquid(Map map) : base(map)
		{
		}

		/// <summary>The survey result, unconditional on Mod Settings — the
		/// SAME separation RM_LiquidStock draws between classification
		/// (BodyAt, always runs) and the budget being consulted
		/// (CanSupply/TryDebit, gated). Whether drilling FUNCTIONS is
		/// Building_LiquidDrill's call via
		/// RimMandrakeFlowWorksSettings.liquidDrillingEnabled; whether this
		/// map HAS anything down there is a fact of the map and does not
		/// flip when a slider does.</summary>
		public bool HasYield => rolled && hasYield;

		public LiquidDef YieldedLiquid => yieldedLiquid;

		public float ReserveRemaining => reserveUnits;

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref rolled, "RM_subsurfaceRolled", false);
			Scribe_Values.Look(ref hasYield, "RM_subsurfaceHasYield", false);
			Scribe_Defs.Look(ref yieldedLiquid, "RM_subsurfaceYieldedLiquid");
			Scribe_Values.Look(ref reserveUnits, "RM_subsurfaceReserveUnits", 0f);
		}

		public override void FinalizeInit()
		{
			base.FinalizeInit();
			if (rolled)
			{
				return;
			}
			rolled = true;
			RollYield();
		}

		private void RollYield()
		{
			hasYield = false;
			yieldedLiquid = null;
			reserveUnits = 0f;

			if (map.Biome == null)
			{
				return;
			}
			RM_SubsurfaceLiquidBiomeExtension ext = map.Biome.GetModExtension<RM_SubsurfaceLiquidBiomeExtension>();
			if (ext == null || ext.options.NullOrEmpty())
			{
				return;
			}
			float chance = Mathf.Clamp01(ext.chanceMapHasYield * RimMandrakeFlowWorksSettings.drillYieldChanceMultiplier);
			if (!Rand.Chance(chance))
			{
				return;
			}

			float totalWeight = 0f;
			for (int i = 0; i < ext.options.Count; i++)
			{
				RM_SubsurfaceLiquidOption o = ext.options[i];
				if (o.liquid != null)
				{
					totalWeight += Mathf.Max(0f, o.commonality);
				}
			}
			if (totalWeight <= 0f)
			{
				return;
			}

			float roll = Rand.Range(0f, totalWeight);
			float acc = 0f;
			RM_SubsurfaceLiquidOption picked = null;
			for (int i = 0; i < ext.options.Count; i++)
			{
				RM_SubsurfaceLiquidOption o = ext.options[i];
				if (o.liquid == null)
				{
					continue;
				}
				acc += Mathf.Max(0f, o.commonality);
				if (roll <= acc)
				{
					picked = o;
					break;
				}
			}
			if (picked == null)
			{
				return;
			}

			hasYield = true;
			yieldedLiquid = picked.liquid;
			reserveUnits = Mathf.Max(0f, picked.reserveUnits.RandomInRange);

			if (Prefs.DevMode)
			{
				Log.Message("[RimMandrake.FlowWorks] subsurface survey: this map yields "
					+ yieldedLiquid.defName + " (" + reserveUnits.ToString("F0") + " fill-units). "
					+ "Rolled once — sticky like a liquid body's classification, and it never runs again.");
			}
		}

		/// <summary>Spend from the reserve. Never grants more than is left, and
		/// never refills — a subsurface deposit is not a body with seepage; it
		/// is exactly as finite as it sounds. Returns what was actually
		/// granted, the same TryDebit-style contract RM_LiquidStock uses so a
		/// caller can never move more than this returns.</summary>
		public float TryExtract(float requestedUnits)
		{
			if (!HasYield || requestedUnits <= 0f)
			{
				return 0f;
			}
			float granted = Mathf.Min(requestedUnits, reserveUnits);
			reserveUnits -= granted;
			if (reserveUnits < 0f)
			{
				reserveUnits = 0f;
			}
			return granted;
		}

		/// <summary>The inspect-string report a drill building forwards
		/// verbatim — §5's "disclosed, never silent" discipline applied to a
		/// resource the player cannot see with their own eyes the way a pond
		/// is visible.</summary>
		public string StatusReport()
		{
			if (!rolled)
			{
				return "RM_SubsurfaceUnsurveyed".Translate();
			}
			if (!hasYield)
			{
				return "RM_SubsurfaceNoYield".Translate();
			}
			return "RM_SubsurfaceYieldReport".Translate(yieldedLiquid.LabelCap, reserveUnits.ToString("F0"));
		}
	}
}
