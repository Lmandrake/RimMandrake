using System.Collections.Generic;
using RimWorld;
using Verse;
using RimMandrake.FlowWorks.LiquidTypes;

namespace RimMandrake.FlowWorks.Drilling
{
	// ════════════════════════════════════════════════════════════════════
	// MANY_WATERS_DRILL_BUILDINGS_1 — WHICH MAPS YIELD A DRILLABLE LIQUID.
	// The data hook, same shape as ManyWaters/RiverSteamHook.cs's
	// RiverSteamBiomeExtension: a biome that carries this extension can be
	// drilled; a biome that does not carry it never yields, and this
	// assembly names no biome of its own. Campaign wiring (which biome, which
	// liquids, how rich) is a RimUtinni-tier patch, exactly like river steam.
	// ════════════════════════════════════════════════════════════════════

	/// <summary>One candidate liquid a map on this biome might turn out to sit
	/// on, and how much of it. <see cref="liquid"/> is a soft reference in
	/// spirit only (a null entry is skipped, never a ConfigError) because a
	/// biome extension authored against a liquid another mod ships must not
	/// discard the whole biome the way a hard MayRequire would.</summary>
	public class RM_SubsurfaceLiquidOption
	{
		public LiquidDef liquid;

		/// <summary>Weight among the OTHER options on the same biome once a
		/// map has already rolled "yes, something is down there" — never a
		/// probability on its own. Two options at 1 each are equally likely;
		/// one at 2 is twice as likely as one at 1.</summary>
		public float commonality = 1f;

		/// <summary>Fill-units banked underground before a single drill has
		/// touched it — the finite reserve <see cref="RM_MapComponent_SubsurfaceLiquid"/>
		/// draws down and never refills, the same "real volume everywhere"
		/// discipline ruling 4 gives natural bodies.</summary>
		public FloatRange reserveUnits = new FloatRange(600f, 1800f);
	}

	public class RM_SubsurfaceLiquidBiomeExtension : DefModExtension
	{
		/// <summary>Chance a MAP on this biome yields anything at all before
		/// <see cref="options"/> is even consulted — "the right maps", not
		/// every map. 0 disables drilling on this biome without removing the
		/// extension (present-but-off, same convention as
		/// RiverSteamBiomeExtension.riverSteam).</summary>
		public float chanceMapHasYield = 0.6f;

		public List<RM_SubsurfaceLiquidOption> options = new List<RM_SubsurfaceLiquidOption>();
	}
}
