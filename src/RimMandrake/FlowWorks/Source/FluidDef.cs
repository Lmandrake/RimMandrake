using System.Collections.Generic;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// What a canal carries once it reaches something wet. The terrain it
	/// floods into already carries whatever behavior it needs (flammability,
	/// extinguishing, pathCost) -- this def only says WHICH terrain, how fast
	/// a reservoir spends itself filling it, and how long the fluid stands
	/// before draining back off.
	/// </summary>
	public class FluidDef : Def
	{
		/// <summary>Terrain a flooded cell becomes. MUST be a temporary terrain
		/// (<c>&lt;temporary&gt;true&lt;/temporary&gt;</c>): a release is laid on
		/// the map's TEMP terrain layer, above whatever the cell already was, so
		/// a dug channel or a constructed floor underneath survives intact and
		/// comes back when the fluid drains. It must be a def this mod (or a
		/// client) ships: the base game's temporary water terrains all live in
		/// Data/Odyssey, and naming one hard-requires the DLC.</summary>
		public TerrainDef floodTerrain;

		/// <summary>Ruling 5's tier 2 of 3 — half full, read as chest-deep.
		/// <see cref="floodTerrain"/> is tier 1 (trace/shallow), so only the
		/// upper rungs need naming. Must be temporary, same as tier 1.</summary>
		public TerrainDef fillTerrainHalf;

		/// <summary>Ruling 5's tier 3 of 3 — brimming, read as deep. Ruling 26:
		/// fill never captures, so this stays passable however costly.</summary>
		public TerrainDef fillTerrainBrim;

		/// <summary>A flooded SUPERDEEP cell. Separate from
		/// <see cref="fillTerrainBrim"/> because the temp layer wins in
		/// TerrainAt: a passable fill over an impassable SUPERDEEP excavation
		/// would make the hole walkable the moment it filled. Falls back to
		/// the brim terrain when unset, which is the correct behaviour once
		/// program 2 ships fall-in capture and ladders.</summary>
		public TerrainDef fillTerrainSuperdeep;

		/// <summary>WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES / owner R2 (2026-10-17, by card): the look for water under 25 cm. New
		/// art the owner sees first (VERY_SHALLOW_WATER_RESKIN_HE_SEES_FIRST); unset (every liquid today), the 0.5 m look
		/// (<see cref="floodTerrain"/>) stands in. The hook <see cref="FillTerrainForLook"/> reads.</summary>
		public TerrainDef fillTerrainVeryShallow;

		/// <summary>FLOWWORKS_VISUAL_PRINCIPLES_1: the animated surface of this canal fluid's fill terrains, set by
		/// Patches/LiquidTypes/RM_FluidSurfaceLooks.xml. When set it WINS: it overrides the look of any LiquidDef row that
		/// names this fluid as canalFluid (boiling and icy water do this; RM_LiquidLooks.LookOfFluid and
		/// RM_LiquidSurface.BuildLookTable both read it first). Unset, the row's <c>surfaceLook</c> is used.</summary>
		public RM_LiquidSurfaceLook surfaceLook;

		/// <summary>Reservoir volume consumed per flooded tile, in notches. LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD (unified depth
		/// spec §2.4): PINNED to 1 for every liquid, so a notch costs the same 1,000 L in a pond, a canal and a tank (any other
		/// value is a hidden unit that makes the depth readout lie); ConfigErrors refuses anything else.</summary>
		public float volumePerTile = 1f;

		/// <summary>Ticks between one flooded tile and the next: the fluid's own
		/// flow RATE, independent of how much of it a reservoir holds. 60 (one
		/// in-game minute per tile) reads as water running down a channel and
		/// sits in the same band vanilla's own Flood engine works out to on a
		/// real map; a viscous fluid (tar, ooze) sets this far higher.</summary>
		public int ticksPerTile = 60;

		/// <summary>FLOWWORKS_BUILD_PROGRAM_1 Phase 6: how this liquid burns. None never lights; CreepingFuse travels as a
		/// front and burns a level a day; Inferno (chemfuel) is a fast front with big flames that burns down in seconds;
		/// Detonation (astrofuel) blows up the whole connected body as one chained blast (CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL,
		/// RM_LiquidFire + RM_FuelFireMath).</summary>
		public RM_FluidFireKind fireKind = RM_FluidFireKind.None;

		/// <summary>Phase 6: ticks for the fire front to cross one cell of this liquid. A fuse must be slower than a
		/// walking pawn (~13 ticks/cell) so a player can outrun it. PROVISIONAL per row.</summary>
		public int fireFrontTicksPerCell = 120;

		/// <summary>PIT_FILL_EFFECTS_1: a poison fluid. Vanilla ToxicBuildup severity per day for a pawn standing in
		/// a brimming cell, scaled by fill and the pawn's toxic resistance. 0 = not poisonous.</summary>
		public float toxicPerDayAtBrim;

		/// <summary>SLIME_CROSSING_BUILD_SLIPPERY_SLOPE: how slippery this liquid is to walk through, 0..1 (RM_SlimeSlip /
		/// RM_SlimeMath). 0 = never slips; the four slimes ship 1 (owner: "so slippery that it is nearly impossible to cross").</summary>
		public float slipperiness;

		/// <summary>LIQUID_HEAT_PUSH_1: this fluid warms (hot) or chills (cold) the room it stands in through vanilla heat
		/// (RM_LiquidHeat). A FluidDef with neither flag still heats when its LiquidDef (the one naming it as canalFluid)
		/// is hot or cold. Shipped: RM_Fluid_BoilingWater sets hot, RM_Fluid_IcyWater sets cold (FlowWorks_PitFluids.xml).</summary>
		public bool hot;
		public bool cold;

		/// <summary>Ticks the fluid stands on a cell after the whole release has
		/// finished spreading, before the map's temp-terrain manager drains it
		/// and hands the cell back. Default is the midpoint of vanilla
		/// SeasonalFlood's own 240000-360000 flooded range.</summary>
		public int floodedTicks = 300000;

		// ── PHASE 4: stock, recession and refill ──────────────────────────

		// POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK: the old per-source-cell budget field (canalCellsPerSourceCell) is gone. A pond
		// square holds its own bed depth (RM_Volume.BedLevels: shallow 2, deep RM_Volume.LevelsPerSquare), so one
		// deep pond square is exactly one deep canal square and one tank square.

		/// <summary>Ruling 2's seepage baseline: fill-units a LIMITED body regains
		/// per source cell per in-game day with no weather at all. Tuned so a
		/// one-cell seep takes multiple seasons to refill — "slow and certain",
		/// never random.</summary>
		public float groundOozePerSourceCellPerDay = 0.13f;

		/// <summary>Multiplier on <see cref="groundOozePerSourceCellPerDay"/> at a
		/// rain rate of 1. Rain is the fast lane; seepage is the floor.</summary>
		public float rainRefillFactor = 3f;

		/// <summary>What a receded cell of a NATURAL body becomes. A natural lake
		/// cell is not temporary terrain, so RemoveTempTerrain cannot dry it and
		/// the engine must write a dry terrain directly — which is exactly why
		/// the original terrain is recorded first and restored on refill. Mud,
		/// not soil: exposed lakebed should read raw (§18).</summary>
		public TerrainDef recededTerrain;

		/// <summary>SUMP_TAR_HYDROLOGY_1 ruling 3, "flood fronts cool to glass":
		/// null (default, every fluid this row does not opt in) leaves the
		/// existing recede-to-nothing behaviour completely unchanged. When set,
		/// a release that finishes NATURALLY -- its reservoir runs dry, or it
		/// walls itself in with nowhere left to spread -- writes this terrain
		/// onto the PERMANENT layer of its own outer edge (the cells that
		/// border ground the release never offered; a neighbour it offered and
		/// was refused or kept hands off, or an engine-filled channel cell,
		/// counts as reached -- Flood_FlowWorks.IsFrontCell) before it destroys itself.
		/// Deliberately NOT written for a release that expires stuck
		/// (Flood_FlowWorks.ExpiryTick) -- that path is a provably-abnormal
		/// release, never a self-limiting one, so it recedes exactly as it
		/// always has. Written to the PERMANENT layer, not the temp one: the
		/// still-standing temp fluid terrain on top hides it until that
		/// terrain's own already-queued removal fires, at which point the
		/// ground it reveals is glass rather than whatever was there before --
		/// "every belch rewrites the map" without this class touching
		/// TempTerrainManager's own removal queue at all. The INTERIOR of a
		/// release (every placed cell with no un-placed cardinal neighbour) is
		/// deliberately left alone by this mechanism -- read as "the middle
		/// stays soft" meaning unchanged, ordinary recede behaviour, not a new
		/// permanent-pool mechanic; an owner call for the interior to persist
		/// as a permanent pool instead is real follow-on work, not assumed
		/// here.</summary>
		public TerrainDef coolsToGlassEdge;

		/// <summary>WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES / LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD: the ONE fill look rule, by TRUE metres
		/// of water (RM_ExcavationDepth.FillTier = RM_LevelSolve.LookBand: 0 dry,
		/// 1 under 25 cm, 2 ≈ 0.5 m, 3 ≈ 1 m, 4 ≈ 1.5 m, 5 = 2 m and deeper), the same in every hole, whatever its depth
		/// (unified depth spec §4.1: the water picture says how deep the WATER is; the walls say how deep the hole is). The
		/// four looks each liquid already has carry 0.5 / 1 / 1.5 / 2 m+; band 1 shows <see cref="fillTerrainVeryShallow"/>, the
		/// hook for the very-shallow art (VERY_SHALLOW_WATER_RESKIN_HE_SEES_FIRST), and the 0.5 m look until it is authored.</summary>
		public TerrainDef FillTerrainForLook(int band)
		{
			switch (band)
			{
				case 0: return null;
				case 1: return fillTerrainVeryShallow ?? floodTerrain;
				case 2: return floodTerrain;
				case 3: return fillTerrainHalf ?? floodTerrain;
				case 4: return fillTerrainBrim ?? fillTerrainHalf ?? floodTerrain;
				default: return fillTerrainSuperdeep ?? fillTerrainBrim ?? floodTerrain;
			}
		}

		/// <summary>True if this terrain is one THIS fluid's engine placed, so
		/// the engine never strips a temp terrain some other system owns.</summary>
		public bool OwnsFillTerrain(TerrainDef terrain)
		{
			if (terrain == null)
			{
				return false;
			}
			return terrain == floodTerrain || terrain == fillTerrainHalf
				|| terrain == fillTerrainBrim || terrain == fillTerrainSuperdeep
				|| (fillTerrainVeryShallow != null && terrain == fillTerrainVeryShallow);
		}

		public override IEnumerable<string> ConfigErrors()
		{
			foreach (string error in base.ConfigErrors())
			{
				yield return error;
			}
			if (floodTerrain == null)
			{
				yield return "floodTerrain is null -- a fluid with nothing to flood into can never do anything.";
			}
			else if (!floodTerrain.temporary)
			{
				yield return "floodTerrain " + floodTerrain.defName + " is not temporary. TerrainGrid.SetTempTerrain " +
					"refuses any terrain without <temporary>true</temporary>, so this fluid would flood nothing at all.";
			}
			foreach (TerrainDef tier in new[] { fillTerrainHalf, fillTerrainBrim, fillTerrainSuperdeep })
			{
				if (tier != null && !tier.temporary)
				{
					yield return "fill tier terrain " + tier.defName + " is not temporary. " +
						"TerrainGrid.SetTempTerrain refuses any terrain without <temporary>true</temporary>, " +
						"so this tier would render nothing and the cell would read as dry at full.";
				}
			}
			if (volumePerTile <= 0f)
			{
				yield return "volumePerTile must be > 0 -- a reservoir spending 0 per tile never runs dry.";
			}
			else if (System.Math.Abs(volumePerTile - 1f) > 1e-4f)
			{
				yield return "volumePerTile must be 1 (it is " + volumePerTile + "): a notch is 1,000 L in a pond, a canal and a tank "
					+ "alike (LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD); any other value makes litres and metres disagree.";
			}
			if (ticksPerTile < 1)
			{
				yield return "ticksPerTile must be >= 1 (it is the flood's expand interval; 0 divides by zero).";
			}
			if (floodedTicks < 1)
			{
				yield return "floodedTicks must be >= 1.";
			}
			if (groundOozePerSourceCellPerDay < 0f)
			{
				yield return "groundOozePerSourceCellPerDay must be >= 0 -- a negative seepage drains a "
					+ "body that nothing is drawing from.";
			}
			if (coolsToGlassEdge != null && coolsToGlassEdge.temporary)
			{
				yield return "coolsToGlassEdge " + coolsToGlassEdge.defName + " is marked <temporary>true</temporary> "
					+ "-- glass cooling writes to the PERMANENT terrain layer on purpose, so a temporary terrain "
					+ "here would just be cleared by the temp-terrain manager the moment the flood's own top "
					+ "layer recedes, and the glass front would never actually be seen.";
			}
		}
	}

	/// <summary>FLOWWORKS_BUILD_PROGRAM_1 Phase 6: a creeping fuse (tar, oil), an inferno (chemfuel) or a detonation
	/// (astrofuel). Mod Settings can soften the last two (RM_FuelFireMath.Classify).</summary>
	public enum RM_FluidFireKind
	{
		None,
		CreepingFuse,
		Detonation,
		Inferno
	}
}
