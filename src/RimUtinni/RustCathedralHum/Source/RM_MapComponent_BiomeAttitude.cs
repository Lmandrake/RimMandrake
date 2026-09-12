using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.Utinni.RustCathedralHum
{
	// RUST_CATHEDRAL_MECHANICS_1 §1 -- the hum-mood system. Per the kit spec's
	// own build order this is the item everything else plugs into: §3 (living
	// bolts) reads GetBand() for its dance/freeze display, §4 (eel-fishing)
	// and §5 (deep-drill response) call AddIrritation() for their own inputs.
	// Only this component and its content are built by this pass -- §3/§4/§5
	// remain untouched and reference nothing here yet.
	//
	// A plain MapComponent (not CustomMapComponent) -- Verse.Map.FillComponents
	// auto-instantiates every non-abstract MapComponent subclass on every map
	// (confirmed via RimSage read of Map.cs), so this never needs a
	// MapGeneratorDef entry. It is a no-op on any map whose biome has no
	// matching RM_BiomeAttitudeDef, which is every biome but the Cathedral
	// today -- cheap and harmless everywhere else.
	//
	// Ledger (zero C#): the slow layer IS faction-13 (Forsaken/Forgotten
	// Arsenal, vanilla Mechanoid, Faction.OfMechanoids) player goodwill --
	// vanilla's own FactionRelation.CheckKindThresholds flips Hostile at <=-75
	// and back to Neutral only at >=0. This component reads that goodwill and
	// writes to it (worst-band sustained drain only); it never sets faction
	// relations directly.
	//
	// Fast layer (this class): "irritation" is a float that events bump and
	// time decays. composite = irritation - goodwill*weight decides a 0..N
	// band (N = def.WorstBand) via ascending thresholds with a de-escalation-
	// only hysteresis margin (the sheet's own "hysteresis wiring" mechanic).
	// Band drives: (a) how many layered hum Sustainers play (0 at the worst
	// band -- the sheet's "when the hum drops, stop moving" survival tell),
	// (b) droid commentary messages on transition, cooldown-gated, only with
	// a player droid on the map, (c) sustained-worst-band goodwill drain.
	public class RM_MapComponent_BiomeAttitude : MapComponent
	{
		private float irritation;
		private int currentBand = -1; // -1 = uninitialized; forces a sync on first tick
		private int lastCommentaryTick = -999999;
		private int worstBandGoodwillLastTickGametime = -999999;
		private int goodwillDrainDayAnchorTick;
		private int goodwillDrainedToday;
		private int checksSinceStart;

		private RM_BiomeAttitudeDef cachedDef;
		private bool defLookupDone;

		private readonly List<Sustainer> activeSustainers = new List<Sustainer>();

		public RM_MapComponent_BiomeAttitude(Map map)
			: base(map)
		{
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref irritation, "irritation", 0f);
			Scribe_Values.Look(ref currentBand, "currentBand", -1);
			Scribe_Values.Look(ref lastCommentaryTick, "lastCommentaryTick", -999999);
			Scribe_Values.Look(ref worstBandGoodwillLastTickGametime, "worstBandGoodwillLastTickGametime", -999999);
			Scribe_Values.Look(ref goodwillDrainDayAnchorTick, "goodwillDrainDayAnchorTick", 0);
			Scribe_Values.Look(ref goodwillDrainedToday, "goodwillDrainedToday", 0);
			// activeSustainers is intentionally not saved -- Sustainer is a
			// live-audio handle, not save data. currentBand survives the
			// save/load and the next tick resyncs sustainers to it.
		}

		public override void MapRemoved()
		{
			base.MapRemoved();
			EndAllSustainers();
		}

		public override void MapComponentTick()
		{
			if (!RustCathedralHumSettings.humMechanicEnabled)
			{
				if (activeSustainers.Count > 0)
				{
					EndAllSustainers();
				}
				return;
			}

			RM_BiomeAttitudeDef def = GetDef();
			if (def == null)
			{
				return;
			}

			if (!map.IsHashIntervalTick(def.checkIntervalTicks))
			{
				return;
			}

			checksSinceStart++;
			DecayIrritation(def);
			int band = ComputeBand(def);
			bool bandChanged = band != currentBand || activeSustainers.Count == 0 && checksSinceStart <= 1;
			currentBand = band;

			SyncSustainers(def, band);

			if (bandChanged)
			{
				MaybeFireCommentary(def, band);
			}

			if (band >= def.WorstBand)
			{
				MaybeDrainGoodwill(def);
			}
		}

		// ---- public API for §3/§4/§5 to plug into ----

		/// <summary>Current attitude band for this map, or -1 if the biome has no attitude def (never fires here).</summary>
		public static int GetBand(Map map)
		{
			RM_MapComponent_BiomeAttitude comp = map?.GetComponent<RM_MapComponent_BiomeAttitude>();
			return comp?.currentBand ?? -1;
		}

		/// <summary>Bumps this map's irritation. Negative amounts are allowed (a mercy event), though nothing calls that yet.</summary>
		public static void AddIrritation(Map map, float amount)
		{
			RM_MapComponent_BiomeAttitude comp = map?.GetComponent<RM_MapComponent_BiomeAttitude>();
			comp?.Notify_Irritation(amount);
		}

		public void Notify_Irritation(float amount)
		{
			irritation = Mathf.Max(0f, irritation + amount);
		}

		// ---- internals ----

		private RM_BiomeAttitudeDef GetDef()
		{
			if (defLookupDone)
			{
				return cachedDef;
			}
			defLookupDone = true;
			if (map.Biome == null)
			{
				return null;
			}
			string biomeDefName = map.Biome.defName;
			List<RM_BiomeAttitudeDef> allDefs = DefDatabase<RM_BiomeAttitudeDef>.AllDefsListForReading;
			for (int i = 0; i < allDefs.Count; i++)
			{
				if (allDefs[i].targetBiome == biomeDefName)
				{
					cachedDef = allDefs[i];
					break;
				}
			}
			return cachedDef;
		}

		private void DecayIrritation(RM_BiomeAttitudeDef def)
		{
			if (irritation <= 0f)
			{
				return;
			}
			float halfLifeDays = Mathf.Max(0.01f, def.irritationDecayHalfLifeDays / Mathf.Max(0.01f, RustCathedralHumSettings.irritationDecayRateMultiplier));
			float halfLifeTicks = halfLifeDays * GenDate.TicksPerDay;
			float intervalTicks = def.checkIntervalTicks;
			float decayFactor = Mathf.Pow(0.5f, intervalTicks / halfLifeTicks);
			irritation *= decayFactor;
			if (irritation < 0.05f)
			{
				irritation = 0f;
			}
		}

		private int ComputeBand(RM_BiomeAttitudeDef def)
		{
			int goodwill = Faction.OfMechanoids != null ? Faction.OfMechanoids.GoodwillWith(Faction.OfPlayer) : 0;
			float composite = Mathf.Clamp(irritation - goodwill * def.goodwillCompositeWeight, 0f, 100f);

			int previousBand = currentBand < 0 ? 0 : currentBand;
			int rawBand = 0;
			for (int i = 0; i < def.bandThresholds.Count; i++)
			{
				if (composite >= def.bandThresholds[i])
				{
					rawBand = i + 1;
				}
			}

			if (rawBand >= previousBand)
			{
				// Escalation is immediate -- no hysteresis on the way up.
				return rawBand;
			}

			// De-escalation only takes effect once composite has fallen the
			// hysteresis margin below the threshold that put us in the
			// PREVIOUS band, so composite hovering at a cutoff doesn't
			// chatter the band every check.
			int thresholdIndexForPreviousBand = previousBand - 1;
			if (thresholdIndexForPreviousBand < 0 || thresholdIndexForPreviousBand >= def.bandThresholds.Count)
			{
				return rawBand;
			}
			float holdLine = def.bandThresholds[thresholdIndexForPreviousBand] - def.bandHysteresisMargin;
			return composite < holdLine ? rawBand : previousBand;
		}

		private void SyncSustainers(RM_BiomeAttitudeDef def, int band)
		{
			// Layer count: band 0 -> 1 layer (the baseline "warm drone"),
			// rising one layer per band up to the layer list length, and
			// SILENCE (0 layers) at the worst band -- the sheet's own
			// survival tell that the hum has "dropped".
			int desiredLayers;
			if (band >= def.WorstBand)
			{
				desiredLayers = 0;
			}
			else
			{
				desiredLayers = Mathf.Clamp(band + 1, 0, def.humLayers.Count);
			}

			while (activeSustainers.Count > desiredLayers)
			{
				Sustainer last = activeSustainers[activeSustainers.Count - 1];
				last?.End();
				activeSustainers.RemoveAt(activeSustainers.Count - 1);
			}
			while (activeSustainers.Count < desiredLayers)
			{
				SoundDef layerSound = def.humLayers[activeSustainers.Count];
				Sustainer sustainer = layerSound?.TrySpawnSustainer(SoundInfo.OnCamera(MaintenanceType.PerTick));
				activeSustainers.Add(sustainer);
			}
		}

		private void EndAllSustainers()
		{
			for (int i = 0; i < activeSustainers.Count; i++)
			{
				activeSustainers[i]?.End();
			}
			activeSustainers.Clear();
		}

		private void MaybeFireCommentary(RM_BiomeAttitudeDef def, int band)
		{
			if (!RustCathedralHumSettings.commentaryEnabled)
			{
				return;
			}

			int ticksSinceLast = Find.TickManager.TicksGame - lastCommentaryTick;
			float cooldownTicks = def.commentaryCooldownHours * GenDate.TicksPerHour;
			if (ticksSinceLast < cooldownTicks)
			{
				return;
			}

			RM_BandCommentaryEntry entry = FindCommentaryFor(def, band);
			if (entry == null || entry.lines.Count == 0)
			{
				return;
			}

			if (!IsPlayerDroidOnMap())
			{
				return;
			}

			string line = entry.lines.RandomElement();
			Messages.Message(line, MessageTypeDefOf.NeutralEvent, historical: false);
			lastCommentaryTick = Find.TickManager.TicksGame;
		}

		private static RM_BandCommentaryEntry FindCommentaryFor(RM_BiomeAttitudeDef def, int band)
		{
			for (int i = 0; i < def.commentary.Count; i++)
			{
				if (def.commentary[i].band == band)
				{
					return def.commentary[i];
				}
			}
			return null;
		}

		private bool IsPlayerDroidOnMap()
		{
			IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn pawn = pawns[i];
				if (pawn.Faction == Faction.OfPlayer && pawn.RaceProps != null && pawn.RaceProps.FleshType == FleshTypeDefOf.Mechanoid)
				{
					return true;
				}
			}
			return false;
		}

		private void MaybeDrainGoodwill(RM_BiomeAttitudeDef def)
		{
			if (!RustCathedralHumSettings.goodwillDrainEnabled)
			{
				return;
			}
			if (Faction.OfMechanoids == null)
			{
				return;
			}

			int nowTick = Find.TickManager.TicksGame;
			if (nowTick - goodwillDrainDayAnchorTick >= GenDate.TicksPerDay)
			{
				goodwillDrainDayAnchorTick = nowTick;
				goodwillDrainedToday = 0;
			}
			if (goodwillDrainedToday <= def.worstBandGoodwillCapPerDay)
			{
				return; // already at (or past) today's cap
			}

			int intervalTicks = Mathf.RoundToInt(def.worstBandGoodwillTickIntervalHours * GenDate.TicksPerHour);
			if (nowTick - worstBandGoodwillLastTickGametime < intervalTicks)
			{
				return;
			}
			worstBandGoodwillLastTickGametime = nowTick;

			int amount = def.worstBandGoodwillTickAmount;
			// Never drain past the day's cap in one tick.
			int remainingBudget = def.worstBandGoodwillCapPerDay - goodwillDrainedToday;
			if (amount < remainingBudget)
			{
				amount = remainingBudget;
			}
			if (amount >= 0)
			{
				return;
			}

			Faction.OfMechanoids.TryAffectGoodwillWith(Faction.OfPlayer, amount, canSendMessage: false, canSendHostilityLetter: true);
			goodwillDrainedToday += amount;
		}
	}
}
