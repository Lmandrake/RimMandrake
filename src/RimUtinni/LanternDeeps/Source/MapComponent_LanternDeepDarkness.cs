using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.LanternDeeps
{
	// LANTERN_DEEPS_INJECTION_1 spec item 6, the darkness mechanic
	// (design/Jawa/proposals/underground_caverns_deep_design.md ss8, ruled v1 by
	// the owner's 2026-09-02 sitting: "This is just needed in so many places...
	// Light is what we bring because we need it, but in such great abundance
	// compared to the local creatures we are like blazing beacons begging to
	// be messed with."). That doc's own mechanics table calls for exactly ONE
	// shared signal -- "ambient light level" -- read by multiple creature
	// behaviors; this MapComponent is that signal's first consumer. It is
	// NOT the doc's separate map-chain/vault-layer infrastructure (out of
	// this item's scope) -- just the light-draws-things mechanic, applied to
	// the one pocket map Lantern Deeps already has.
	//
	// Scoped to Lantern Deep pocket maps only: CustomMapComponent subclasses
	// are NOT auto-added to every map (see Verse.Map.FillComponents -- the
	// engine's own auto-registration loop explicitly skips any type assignable
	// to CustomMapComponent). Only a map whose MapGeneratorDef lists this type
	// in customMapComponents gets one; RUT_LanternDeepGenerator.xml does.
	//
	// Mechanism: periodically samples ground glow at every colonist's position.
	// Sustained bright light accumulates "exposure"; darkness lets it decay.
	// Once exposure crosses a threshold, a predator already resident in
	// RUT_LanternDeeps (RSW_BloodropMoth) is drawn toward the brightest
	// colonist and goes manhunter -- no new creature invented; the
	// crystal-studded roster stays evicted per HARD BAN #3, and the rest of
	// the non-crystal cast is still "the sitting"'s call, not this build's.
	// A player who carries less light, or spaces bright work out, is never
	// bothered -- the "master of dim/no light is visibly rewarded" half of
	// the ruling this item is scoped to prove, not just the punishment half.
	public class MapComponent_LanternDeepDarkness : CustomMapComponent
	{
		private const int CheckIntervalTicks = 250;
		private const float ExposureThreshold = 60f;
		private const float ExposureDecayPerCheck = 1.5f;
		private const int MinTicksBetweenAmbushes = 15000; // a quarter of an in-game day (GenDate.TicksPerDay = 60000)
		private static readonly IntRange AmbushGroupSize = new IntRange(1, 2);

		// CAVERNS_PARITY_BUILD_1: the predators that actually live in
		// RUT_LanternDeeps.wildAnimals, in order of preference. Bloodrop moth is
		// the donor biome's own predator, ported as RSW_BloodropMoth; shatterjaw
		// is the fallback if SWBestiary ever drops the moth line.
		private static readonly string[] DeepPredatorKindNames =
		{
			"RSW_BloodropMoth",
			"RSW_ShatterjawBeetle",
		};

		private float lightExposure;
		private int lastAmbushTick = -999999;

		public MapComponent_LanternDeepDarkness(Map map)
			: base(map)
		{
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref lightExposure, "lightExposure", 0f);
			Scribe_Values.Look(ref lastAmbushTick, "lastAmbushTick", -999999);
		}

		public override void MapComponentTick()
		{
			if (!LanternDeepsSettings.darknessMechanicEnabled)
			{
				return;
			}
			if (map.IsHashIntervalTick(CheckIntervalTicks))
			{
				CheckAmbientLight();
			}
		}

		private void CheckAmbientLight()
		{
			var colonists = map.mapPawns.FreeColonistsSpawned;
			if (colonists.Count == 0)
			{
				lightExposure = Mathf.Max(0f, lightExposure - ExposureDecayPerCheck);
				return;
			}

			float brightest = 0f;
			Pawn brightestPawn = null;
			for (int i = 0; i < colonists.Count; i++)
			{
				Pawn pawn = colonists[i];
				float glow = map.glowGrid.GroundGlowAt(pawn.Position);
				if (glow > brightest)
				{
					brightest = glow;
					brightestPawn = pawn;
				}
			}

			// Darkness (glow ~0) accumulates almost nothing; bright light
			// accumulates fastest -- the "beacon" tension the ruling
			// describes. Squared so a dim work-light reads very differently
			// from a floodlit base.
			//
			// GlowGrid.GroundGlowAt CAPS a roofed cell at 0.5 for every
			// non-overlit light (MaxGameGlowFromNonOverlitGroundLights) and
			// returns 1.0 only inside a sun lamp's overlight radius. The Deep
			// is roofed everywhere, so 0.5 IS "fully lit" here: torches,
			// campfires and standing lamps all top out there. MEASURED live
			// 2026-09-18: six campfires around a drafted colonist for 16,500
			// ticks never fired the old (glow^2 * 4) formula, because
			// 0.5^2 * 4 = 1.0 < the 1.5 decay. Normalise against the cap.
			float lit = Mathf.Min(1f, brightest * 2f);
			lightExposure += lit * lit * 4f;
			lightExposure = Mathf.Max(0f, lightExposure - ExposureDecayPerCheck);

			if (lightExposure < ExposureThreshold * LanternDeepsSettings.darknessThresholdMultiplier)
			{
				return;
			}
			if (Find.TickManager.TicksGame - lastAmbushTick < MinTicksBetweenAmbushes)
			{
				return;
			}
			if (brightestPawn == null)
			{
				return;
			}

			DrawSomethingToTheLight(brightestPawn);
			lightExposure = 0f;
			lastAmbushTick = Find.TickManager.TicksGame;
		}

		private static void DrawSomethingToTheLight(Pawn targetPawn)
		{
			// CAVERNS_PARITY_BUILD_1: was BMT_CaveSpider, a donor PawnKindDef that
			// is ALSO one of the seven stragglers RULED CUT 2026-09-11 -- so it was
			// going to become a permanent silent no-op twice over. Now the ambush
			// draws a resident of our own biome's wildAnimals list, which are the
			// RSW_* ports already shipped in SWBestiary. First match wins; a null
			// return is still a no-op and never a crash.
			PawnKindDef predatorKind = null;
			foreach (string kindName in DeepPredatorKindNames)
			{
				predatorKind = DefDatabase<PawnKindDef>.GetNamedSilentFail(kindName);
				if (predatorKind != null)
				{
					break;
				}
			}
			if (predatorKind == null)
			{
				return; // SWBestiary absent or the defNames changed -- no-op, never crash
			}

			Map map = targetPawn.Map;
			int count = AmbushGroupSize.RandomInRange;
			for (int i = 0; i < count; i++)
			{
				if (!CellFinder.TryFindRandomCellNear(targetPawn.Position, map, 12,
					c => c.InBounds(map) && c.Standable(map) && !c.Fogged(map), out IntVec3 cell))
				{
					continue;
				}

				var request = new PawnGenerationRequest(
					predatorKind,
					null,
					PawnGenerationContext.NonPlayer,
					forceGenerateNewPawn: true,
					canGeneratePawnRelations: false,
					mustBeCapableOfViolence: true);
				Pawn pawn = PawnGenerator.GeneratePawn(request);
				GenSpawn.Spawn(pawn, cell, map);
				pawn.mindState.mentalStateHandler.TryStartMentalState(
					MentalStateDefOf.Manhunter,
					reason: "Drawn out of the dark by the light.",
					forced: true,
					forceWake: true);
			}
		}
	}
}
