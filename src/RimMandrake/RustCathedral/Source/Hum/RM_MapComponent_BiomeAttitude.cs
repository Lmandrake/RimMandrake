using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.RustCathedral.Hum
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
	// Slow layer (RUSTCATHEDRAL_GOODWILL_FLOOR_1): the Cathedral's own
	// STANDING with the player, an int in [-100, 100] kept and saved by this
	// component, starting at def.standingStart. It is NOT faction goodwill:
	// the faction this campaign relabels as the Forgotten Arsenal is vanilla
	// Mechanoid, which is permanentEnemy, so Faction.CanChangeGoodwillFor
	// refuses every change and its goodwill never moves -- reading it
	// floored the composite and made every drain a no-op. The worst-band
	// drain, §4's catch cost and §5's drill response all move this value
	// through AffectStanding(); nothing here touches faction relations.
	//
	// Fast layer (this class): "irritation" is a float that events bump and
	// time decays. composite = irritation - standing*weight decides a 0..N
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
		private int displayBand = -1; // currentBand clamped to the active stage's bandCeiling
		private int stage; // CATHEDRAL_STAGE_HUM_BRIDGE_1: 0 = WARY (arc spec's own numbering), set by the bridge/GM blackboard, never ratcheted here
		private int lastCommentaryTick = -999999;
		private int worstBandGoodwillLastTickGametime = -999999;
		private int goodwillDrainDayAnchorTick;
		private int goodwillDrainedToday;
		private int checksSinceStart;
		private int standing;
		private bool standingInitialized;

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
			Scribe_Values.Look(ref displayBand, "displayBand", -1);
			Scribe_Values.Look(ref stage, "stage", 0);
			Scribe_Values.Look(ref lastCommentaryTick, "lastCommentaryTick", -999999);
			Scribe_Values.Look(ref worstBandGoodwillLastTickGametime, "worstBandGoodwillLastTickGametime", -999999);
			Scribe_Values.Look(ref goodwillDrainDayAnchorTick, "goodwillDrainDayAnchorTick", 0);
			Scribe_Values.Look(ref goodwillDrainedToday, "goodwillDrainedToday", 0);
			Scribe_Values.Look(ref standing, "standing", 0);
			Scribe_Values.Look(ref standingInitialized, "standingInitialized", false);
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

			// PerTick sustainers end once TicksGame > lastMaintainTick + 1, so every
			// live layer must be maintained on EVERY tick, before the interval gate.
			for (int i = 0; i < activeSustainers.Count; i++)
			{
				activeSustainers[i]?.Maintain();
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
			displayBand = ClampToStage(def, band);

			SyncSustainers(def, displayBand);

			// §4's line-in tell. The kit spec's own preferred, zero-Harmony
			// route: read the FISHING STATE off this map's pawns on the same
			// interval this component already runs. Self-gated inside, and
			// reached only on a map that HAS an attitude def (def != null
			// above), so every other map pays nothing.
			RM_CathedralFishing.ScanForFishing(map);

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

		/// <summary>The band this map's hum/bolts actually SHOW right now (raw band clamped to the active stage's ceiling), or -1 if the biome has no attitude def. This is "the on-map voice" -- what §3/§7/§8 consumers should read, not the raw internal composite.</summary>
		public static int GetBand(Map map)
		{
			RM_MapComponent_BiomeAttitude comp = map?.GetComponent<RM_MapComponent_BiomeAttitude>();
			return comp?.displayBand ?? -1;
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

		/// <summary>The Cathedral's standing with the player on this map ([-100, 100]), or null if the biome has no attitude def.</summary>
		public static int? GetStanding(Map map)
		{
			RM_MapComponent_BiomeAttitude comp = map?.GetComponent<RM_MapComponent_BiomeAttitude>();
			if (comp == null || comp.GetDef() == null)
			{
				return null;
			}
			return comp.Standing;
		}

		/// <summary>Moves this map's standing by delta (negative = offence), clamped to [-100, 100]. No-op off an attitude-def map.</summary>
		public static void AffectStanding(Map map, int delta)
		{
			RM_MapComponent_BiomeAttitude comp = map?.GetComponent<RM_MapComponent_BiomeAttitude>();
			if (comp == null || comp.GetDef() == null)
			{
				return;
			}
			comp.Notify_Standing(delta);
		}

		public void Notify_Standing(int delta)
		{
			standing = Mathf.Clamp(Standing + delta, -100, 100);
		}

		private int Standing
		{
			get
			{
				if (!standingInitialized)
				{
					RM_BiomeAttitudeDef def = GetDef();
					standing = def != null ? Mathf.Clamp(def.standingStart, -100, 100) : 0;
					standingInitialized = true;
				}
				return standing;
			}
		}

		// ---- CATHEDRAL_STAGE_HUM_BRIDGE_1: the stage source's own lane ----

		/// <summary>This map's current conduct-stage (0 WARY by default), or -1 if the biome has no attitude def.</summary>
		public static int GetStage(Map map)
		{
			RM_MapComponent_BiomeAttitude comp = map?.GetComponent<RM_MapComponent_BiomeAttitude>();
			return comp?.stage ?? -1;
		}

		/// <summary>Sets this map's conduct-stage. Not a second attitude system and not ratcheted here -- the arc's GM blackboard (item 1) owns the one-way-knowledge/two-way-standing rules; this is a dumb setter, including the dark-flip case (drive back to 0/WARY at any time, regardless of history).</summary>
		public static void SetStage(Map map, int stage)
		{
			RM_MapComponent_BiomeAttitude comp = map?.GetComponent<RM_MapComponent_BiomeAttitude>();
			comp?.Notify_StageChanged(stage);
		}

		public void Notify_StageChanged(int newStage)
		{
			stage = newStage;
			RM_BiomeAttitudeDef def = GetDef();
			if (def != null)
			{
				// Re-clamp immediately rather than waiting up to checkIntervalTicks
				// for the next tick -- a stage change (especially the dark flip)
				// should be audible/visible on the next sustainer sync, not lag
				// behind by up to checkIntervalTicks worth of game time.
				displayBand = ClampToStage(def, currentBand < 0 ? 0 : currentBand);
				SyncSustainers(def, displayBand);
			}
		}

		private int ClampToStage(RM_BiomeAttitudeDef def, int rawBand)
		{
			RM_StageAttitudeParams sp = def.GetStageParams(stage);
			int ceiling = sp?.bandCeiling ?? def.WorstBand;
			return Mathf.Clamp(rawBand, 0, ceiling);
		}

		// ---- proof hooks (RM_RustCathedralHumProof, RUSTCATHEDRAL_COVERAGE_GAPS_1) ----

		public float ProofIrritation => irritation;

		public int ProofLayers => activeSustainers.Count;

		public int ProofStanding => Standing;

		/// <summary>Sets standing directly (proof restore only).</summary>
		public void ProofSetStanding(int value)
		{
			standing = Mathf.Clamp(value, -100, 100);
			standingInitialized = true;
		}

		/// <summary>Runs one worst-band drain step with the interval and day budget cleared, then restores the
		/// drain bookkeeping. Returns false if no def is bound.</summary>
		public bool ProofDrainOnce()
		{
			RM_BiomeAttitudeDef def = GetDef();
			if (def == null)
			{
				return false;
			}
			int lastTick = worstBandGoodwillLastTickGametime, anchor = goodwillDrainDayAnchorTick, drained = goodwillDrainedToday;
			worstBandGoodwillLastTickGametime = -999999;
			goodwillDrainDayAnchorTick = Find.TickManager.TicksGame;
			goodwillDrainedToday = 0;
			try
			{
				MaybeDrainGoodwill(def);
			}
			finally
			{
				worstBandGoodwillLastTickGametime = lastTick;
				goodwillDrainDayAnchorTick = anchor;
				goodwillDrainedToday = drained;
			}
			return true;
		}

		/// <summary>Binds this map to an attitude def regardless of its biome (a quicktest map has none).</summary>
		public void ProofUseDef(RM_BiomeAttitudeDef def)
		{
			cachedDef = def;
			defLookupDone = true;
		}

		/// <summary>Sets irritation, computes the band through the real ComputeBand (hysteresis against the
		/// current band included) and syncs the hum layers; returns the raw band.</summary>
		public int ProofBandAt(float irr)
		{
			RM_BiomeAttitudeDef def = GetDef();
			if (def == null)
			{
				return -1;
			}
			irritation = Mathf.Max(0f, irr);
			currentBand = ComputeBand(def);
			displayBand = ClampToStage(def, currentBand);
			SyncSustainers(def, displayBand);
			return currentBand;
		}

		/// <summary>Undoes ProofUseDef/ProofBandAt: silence, irritation 0, band unset, biome lookup redone.</summary>
		public void ProofReset()
		{
			EndAllSustainers();
			irritation = 0f;
			currentBand = -1;
			displayBand = -1;
			cachedDef = null;
			defLookupDone = false;
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
			RM_StageAttitudeParams stageParams = def.GetStageParams(stage);
			float stageDecayMultiplier = stageParams?.decayRateMultiplier ?? 1f;
			float halfLifeDays = Mathf.Max(0.01f, def.irritationDecayHalfLifeDays
				/ Mathf.Max(0.01f, RustCathedralHumSettings.irritationDecayRateMultiplier * stageDecayMultiplier));
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
			float composite = Mathf.Clamp(irritation - Standing * def.goodwillCompositeWeight, 0f, 100f);

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

			Notify_Standing(amount);
			goodwillDrainedToday += amount;
		}
	}
}
