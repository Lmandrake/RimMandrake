using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.PropaneLakeMechanics
{
	/// <summary>
	/// Row 2 of propane_gas_deep_design.md §9's build ladder: "GasSaturationTracker
	/// — transient during release events, perpetual in authored caverns and
	/// dead-sarlacc dungeons (with rotstink)." A per-cell 0-100 float, PLUS one
	/// global "ambient surge" for map-wide release events (RUT_GasVent's
	/// pump-removal release; a whole-network rupture) so those never need to
	/// touch every cell on the map. Auto-registers on every Map — no def needed
	/// (Map.FillComponents() instantiates every non-abstract MapComponent
	/// subclass with a (Map) constructor).
	/// </summary>
	public class MapComponent_GasSaturationTracker : MapComponent
	{
		private Dictionary<int, float> perCell = new Dictionary<int, float>();
		private Dictionary<int, float> perpetualFloor = new Dictionary<int, float>();
		private HashSet<int> perpetualRotstink = new HashSet<int>();

		/// <summary>Global transient bump — a map-wide release event, not tied to
		/// any single cell. Decays over time, faster in higher wind ("clears by
		/// wind" — the ruled vent behaviour).</summary>
		private float ambientSurge;

		// Working buffers, avoid per-call allocation.
		private List<int> keysToRemoveBuffer = new List<int>();

		public MapComponent_GasSaturationTracker(Map map) : base(map)
		{
		}

		private bool Enabled => PropaneLakeMechanicsMod.Settings == null || PropaneLakeMechanicsMod.Settings.saturationDeflagrationEnabled
			|| PropaneLakeMechanicsMod.Settings.pipeNetworksEnabled || PropaneLakeMechanicsMod.Settings.gasVentsEnabled;

		public float AmbientSurge => ambientSurge;

		/// <summary>0-100. Perpetual floor and local additions stack with the
		/// ambient surge; never exceeds 100.</summary>
		public float SaturationPercentAt(IntVec3 cell)
		{
			if (!cell.InBounds(map))
			{
				return 0f;
			}
			int idx = map.cellIndices.CellToIndex(cell);
			float local = perCell.TryGetValue(idx, out float v) ? v : 0f;
			float floor = perpetualFloor.TryGetValue(idx, out float f) ? f : 0f;
			return Mathf.Clamp(Mathf.Max(local, floor) + ambientSurge, 0f, 100f);
		}

		/// <summary>A rupture jet or a vent puff feeding the field locally — falls
		/// off with distance from the center cell.</summary>
		public void AddSaturation(IntVec3 center, float amount, float radius)
		{
			if (!Enabled || amount <= 0f)
			{
				return;
			}
			foreach (IntVec3 c in GenRadial.RadialCellsAround(center, radius, true))
			{
				if (!c.InBounds(map))
				{
					continue;
				}
				float dist = c.DistanceTo(center);
				float falloff = (radius <= 0.01f) ? 1f : Mathf.Clamp01(1f - dist / radius);
				if (falloff <= 0f)
				{
					continue;
				}
				int idx = map.cellIndices.CellToIndex(c);
				float existing = perCell.TryGetValue(idx, out float v) ? v : 0f;
				perCell[idx] = Mathf.Clamp(existing + amount * falloff, 0f, 100f);
			}
		}

		/// <summary>The transient half of the ruled design: a release event
		/// raises the WHOLE map's baseline at once, cheaply. Clears itself by
		/// wind over time in MapComponentTick.</summary>
		public void AddAmbientSurge(float amount)
		{
			if (!Enabled)
			{
				return;
			}
			ambientSurge = Mathf.Clamp(ambientSurge + amount, 0f, 100f);
		}

		/// <summary>The perpetual half: "caverns where this is just perpetually
		/// true... also true within dead-sarlacc dungeons, along with rotstink."
		/// Map-authoring code (a dungeon/cavern generator) calls this once on the
		/// cells it wants permanently hazed; nothing here decays it below floor.</summary>
		public void MarkPerpetual(IEnumerable<IntVec3> cells, float floorPercent, bool withRotstink)
		{
			foreach (IntVec3 c in cells)
			{
				if (!c.InBounds(map))
				{
					continue;
				}
				int idx = map.cellIndices.CellToIndex(c);
				perpetualFloor[idx] = Mathf.Clamp(floorPercent, 0f, 100f);
				if (withRotstink)
				{
					perpetualRotstink.Add(idx);
				}
				else
				{
					perpetualRotstink.Remove(idx);
				}
			}
		}

		public void UnmarkPerpetual(IEnumerable<IntVec3> cells)
		{
			foreach (IntVec3 c in cells)
			{
				if (!c.InBounds(map))
				{
					continue;
				}
				int idx = map.cellIndices.CellToIndex(c);
				perpetualFloor.Remove(idx);
				perpetualRotstink.Remove(idx);
			}
		}

		/// <summary>The ruled 0-20/20-50/50-80/80+ curve (propane_gas_deep_design.md
		/// §5). `flashoverTier` true means "any heat source ignites the whole
		/// contiguous volume" rather than a localized fireball at the shooter.</summary>
		public float DeflagrationChanceAt(IntVec3 cell, out bool flashoverTier)
		{
			flashoverTier = false;
			float p = SaturationPercentAt(cell) / 100f;
			float intensity = PropaneLakeMechanicsMod.Settings?.deflagrationIntensity ?? 1f;
			if (p < 0.20f)
			{
				return 0f;
			}
			if (p < 0.50f)
			{
				return Mathf.Lerp(0.05f, 0.35f, (p - 0.20f) / 0.30f) * intensity;
			}
			if (p < 0.80f)
			{
				return Mathf.Lerp(0.35f, 0.85f, (p - 0.50f) / 0.30f) * intensity;
			}
			flashoverTier = true;
			return Mathf.Clamp01(Mathf.Lerp(0.85f, 0.98f, (p - 0.80f) / 0.20f) * intensity);
		}

		/// <summary>"Rare and telegraphed... never a silent gotcha": the whole
		/// contiguous saturated volume around origin ignites at once, then burns
		/// itself out (the ignited cells' local saturation is consumed).</summary>
		public void TriggerFlashover(IntVec3 origin, Thing instigator)
		{
			var ignited = new List<IntVec3>();
			map.floodFiller.FloodFill(origin, c => c.InBounds(map) && SaturationPercentAt(c) >= 80f, delegate (IntVec3 c)
			{
				ignited.Add(c);
			}, GenRadial.NumCellsInRadius(20f));

			if (ignited.Count == 0)
			{
				ignited.Add(origin);
			}
			foreach (IntVec3 c in ignited)
			{
				FireUtility.TryStartFireIn(c, map, Rand.Range(0.4f, 1.0f), instigator);
			}
			GenExplosion.DoExplosion(origin, map, 1.9f, DamageDefOf.Flame, instigator, chanceToStartFire: 1f, doSoundEffects: true);
			foreach (IntVec3 c in ignited)
			{
				int idx = map.cellIndices.CellToIndex(c);
				perCell[idx] = 0f;
			}
			Messages.Message("RUT_Message_GasFlashover".Translate(), new TargetInfo(origin, map), MessageTypeDefOf.ThreatBig);
		}

		public override void MapComponentTick()
		{
			base.MapComponentTick();
			if (map.IsHashIntervalTick(60))
			{
				DecayTick();
			}
			if (map.IsHashIntervalTick(400))
			{
				RotstinkTick();
			}
			if (map.IsHashIntervalTick(500))
			{
				HazeVisualTick();
			}
		}

		private void DecayTick()
		{
			// "clears by wind": higher wind speed clears the ambient surge faster.
			float windFactor = 1f + map.windManager.WindSpeed * 2f;
			ambientSurge = Mathf.Max(0f, ambientSurge - 0.6f * windFactor);

			keysToRemoveBuffer.Clear();
			foreach (int idx in perCell.Keys.ToList())
			{
				float floor = perpetualFloor.TryGetValue(idx, out float f) ? f : 0f;
				float v = perCell[idx];
				if (v <= floor)
				{
					continue;
				}
				float decayed = Mathf.Max(floor, v - 1.5f * windFactor);
				if (decayed <= floor + 0.01f && floor <= 0f)
				{
					keysToRemoveBuffer.Add(idx);
				}
				else
				{
					perCell[idx] = decayed;
				}
			}
			for (int i = 0; i < keysToRemoveBuffer.Count; i++)
			{
				perCell.Remove(keysToRemoveBuffer[i]);
			}
		}

		private void RotstinkTick()
		{
			if (perpetualRotstink.Count == 0)
			{
				return;
			}
			foreach (int idx in perpetualRotstink)
			{
				map.gasGrid.AddGas(map.cellIndices.IndexToCell(idx), GasType.RotStink, 12);
			}
		}

		private void HazeVisualTick()
		{
			if (perCell.Count == 0 && ambientSurge <= 0.1f)
			{
				return;
			}
			// Cosmetic-only warning register (§5: "0-20%: cosmetic haze, no
			// mechanical effect"). Cheap: sample a handful of hot cells rather
			// than every one on the map.
			int sampled = 0;
			foreach (KeyValuePair<int, float> kv in perCell)
			{
				if (kv.Value < 5f || !Rand.Chance(0.15f))
				{
					continue;
				}
				FleckMaker.ThrowSmoke(map.cellIndices.IndexToCell(kv.Key).ToVector3Shifted(), map, 0.6f + kv.Value / 100f);
				sampled++;
				if (sampled >= 6)
				{
					break;
				}
			}
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Collections.Look(ref perCell, "perCell", LookMode.Value, LookMode.Value);
			Scribe_Collections.Look(ref perpetualFloor, "perpetualFloor", LookMode.Value, LookMode.Value);
			Scribe_Collections.Look(ref perpetualRotstink, "perpetualRotstink", LookMode.Value);
			Scribe_Values.Look(ref ambientSurge, "ambientSurge", 0f);
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				perCell ??= new Dictionary<int, float>();
				perpetualFloor ??= new Dictionary<int, float>();
				perpetualRotstink ??= new HashSet<int>();
			}
		}
	}
}
