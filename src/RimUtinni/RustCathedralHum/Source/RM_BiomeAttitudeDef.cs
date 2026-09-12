using System.Collections.Generic;
using Verse;

namespace RimMandrake.Utinni.RustCathedralHum
{
	// RUST_CATHEDRAL_MECHANICS_1 §1. RM_ tier on purpose (kit spec's own naming
	// note: "nothing below is Star-Wars- or Utinni-specific as a mechanism") --
	// this Def type is a generic banded-biome-attitude description any biome
	// could reuse; only the CONTENT instance (RUT_RustCathedralAttitude) and
	// its sound/text content are campaign-specific.
	//
	// One instance targets one biome via `targetBiome`. RM_MapComponent_
	// BiomeAttitude looks up the instance whose targetBiome matches
	// map.Biome.defName the first time it runs on that map and caches it; a
	// map on a biome with no matching instance is a permanent, cheap no-op.
	public class RM_BiomeAttitudeDef : Def
	{
		// The BiomeDef defName this instance governs. Not a <li> reference to
		// the biome itself on purpose -- keeping this a plain string means a
		// biome mod need not depend on this one to be *targeted* by it.
		public string targetBiome;

		// Composite-score cutoffs, ascending, one fewer entry than the band
		// count: composite < bandThresholds[0] => band 0 (calmest); composite
		// >= bandThresholds[i] for the highest satisfied i => band i+1, capped
		// at bandThresholds.Count (the worst band). Spec's own placeholder
		// numbers (10/30/55/80) produce exactly 5 bands (0-4).
		public List<float> bandThresholds = new List<float> { 10f, 30f, 55f, 80f };

		// Hysteresis wiring (spec §1's own named mechanic): a band only
		// DE-escalates once composite has fallen a further margin below the
		// threshold that raised it, so composite hovering right at a cutoff
		// doesn't chatter the band back and forth every check. Escalation is
		// immediate (no margin) -- the Cathedral notices sacrilege instantly,
		// it only forgives slowly.
		public float bandHysteresisMargin = 6f;

		// Composite = irritation - goodwill * goodwillCompositeWeight, clamped
		// to [0, 100]. Only faction-13 (Forsaken/Forgotten Arsenal, vanilla
		// Mechanoid) goodwill is read; the ledger itself needs no new C#.
		public float goodwillCompositeWeight = 0.5f;

		// Irritation decays continuously; this is the in-game half-life.
		public float irritationDecayHalfLifeDays = 1f;

		// How often (in ticks) the component re-samples irritation decay,
		// composite, band and the droid/commentary/goodwill checks.
		public int checkIntervalTicks = 250;

		// Sustained WORST band converts irritation pressure into a direct
		// faction-13 goodwill tick -- "the hum never flips hostility by
		// itself; the ledger does" (spec's own framing). Interval in hours of
		// game time between ticks, magnitude per tick, and a per-day cap so a
		// long AFK stretch at the worst band can't zero goodwill in one sitting.
		public float worstBandGoodwillTickIntervalHours = 4f;
		public int worstBandGoodwillTickAmount = -1;
		public int worstBandGoodwillCapPerDay = -5;

		// One Sustainer per active layer, spawned in order as the band rises
		// and stopped in reverse as it falls; ended entirely (silence) at the
		// worst band -- the sheet's own survival tell ("when the hum drops,
		// stop moving. The bolts freeze first."). v1 ships 3 layers per the
		// kit spec's own scope line; a biome that wants more/fewer just lists
		// a different count here.
		public List<SoundDef> humLayers = new List<SoundDef>();

		// Droid commentary, keyed by band. A band with no entry fires no
		// message. Every line here is §P register per the sheet's register
		// law -- the droids' own incomprehension is the one permitted voice
		// (ban 2's named exception), never a mechanical explanation (ban 1).
		public List<RM_BandCommentaryEntry> commentary = new List<RM_BandCommentaryEntry>();
		public float commentaryCooldownHours = 12f;

		public int BandCount => bandThresholds.Count + 1;

		public int WorstBand => bandThresholds.Count;
	}

	public class RM_BandCommentaryEntry
	{
		public int band;
		public List<string> lines = new List<string>();
	}
}
