using System.Collections.Generic;
using System.Text;
using RimMandrake.ExplosiveGrowth;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FloodedCanyon.MapControls
{
	/// <summary>FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS (owner 2026-10-16, by card, design item 6 "Soak Zone"): a square of
	/// ground around this marker that Plant Growth (the ExplosiveGrowth engine) keeps soaked for a set number of hours each
	/// day, through ExplosiveGrowthAPI.SoakCells -- the same hook the canyon flood and the "Soak 5x5 here" debug action use.
	///
	/// SCOPE (decided here): a soak zone works only where Plant Growth runs, i.e. Baroque Biomes' own biomes (or the engine's
	/// own unsupported "other biomes" option). Outside, it stands inert and its inspect pane says why. Owner 2026-10-15:
	/// "We can't guarantee they will work in other biomes beyond our framework" and "build no new cross-biome switch"; the
	/// engine's out-of-scope pass arms, charges and bursts nothing anyway, so lifting the gate for a marker would be a new
	/// per-map cross-biome switch in disguise. The flood trigger differs because the owner asked for it by card.
	///
	/// Not a FlowWorks map control (it touches no liquid and needs no channel), but the same look (ThingDef parent
	/// RM_MapControlBase), the same rules: no faction, dev-only buttons, saved with the map.</summary>
	public class Building_RM_SoakZone : Building
	{
		public bool active = true;
		public int radius = 2;
		public float hoursPerDay = 24f;
		private int startTick = -1;
		private int lastSoaked;

		public static readonly int[] RadiusPresets = { 1, 2, 3, 5, 8 };
		public static readonly float[] HourPresets = { 24f, 12f, 6f, 3f, 1f };

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			if (Faction != null)
			{
				SetFaction(null);
			}
			if (startTick < 0)
			{
				startTick = Find.TickManager.TicksGame;
			}
		}

		public IEnumerable<IntVec3> Cells()
		{
			return CellRect.CenteredOn(Position, radius).ClipInsideMap(Map).Cells;
		}

		/// <summary>Ticks left in today's soak window, or 0 outside it. The day is counted from placement.</summary>
		public int WindowTicksLeft(int now)
		{
			int window = Mathf.Clamp(Mathf.RoundToInt(hoursPerDay * 2500f), 0, 60000);
			int into = (now - Mathf.Max(0, startTick)) % 60000;
			return into < window ? window - into : 0;
		}

		/// <summary>Why the zone soaks nothing right now, or null when it works.</summary>
		public string Inert()
		{
			if (!RM_FloodedCanyonSettings.soakZonesEnabled) return "soak zones are switched off in Mod Settings (Flooded Canyon)";
			if (!active) return "switched off";
			if (!ExplosiveGrowthSettings.On) return "Plant Growth is switched off in Mod Settings";
			if (Map != null && RM_ExplosiveGrowthRegistry.BiomeRefusesSoak(Map.Biome))
			{
				return RM_ExplosiveGrowthRegistry.BiomeInScope(Map.Biome)
					? "this biome never takes a soak (a dry carve-out biome)"
					: "not one of Baroque Biomes' own biomes: Plant Growth does not run here";
			}
			return null;
		}

		public override void TickRare()
		{
			base.TickRare();
			if (!Spawned || Inert() != null)
			{
				return;
			}
			int left = WindowTicksLeft(Find.TickManager.TicksGame);
			// Soak only extends, never shortens; the window's end is the soak's end, so the zone dries on schedule.
			lastSoaked = left > 0 ? ExplosiveGrowthAPI.SoakCells(Map, Cells(), Mathf.Max(250, left)) : 0;
		}

		public override void DrawExtraSelectionOverlays()
		{
			base.DrawExtraSelectionOverlays();
			GenDraw.DrawFieldEdges(new List<IntVec3>(Cells()));
		}

		private string SizeLabel(int r)
		{
			return (2 * r + 1) + "x" + (2 * r + 1);
		}

		private static string HoursLabel(float h)
		{
			return h >= 24f ? "always (24 hours a day)" : h.ToString("0.#") + " hours a day";
		}

		public override string GetInspectString()
		{
			StringBuilder sb = new StringBuilder();
			string b = base.GetInspectString();
			if (!b.NullOrEmpty())
			{
				sb.AppendLine(b);
			}
			sb.AppendLine("Soak zone " + SizeLabel(radius) + ", soaked " + HoursLabel(hoursPerDay) + ".");
			string why = Spawned ? Inert() : null;
			if (why != null)
			{
				sb.AppendLine("Soaks nothing: " + why + ".");
			}
			else if (Spawned)
			{
				int left = WindowTicksLeft(Find.TickManager.TicksGame);
				sb.AppendLine(left > 0 ? "Soaking now (" + lastSoaked + " cells took it)." : "Dry until its next soak hour.");
			}
			return sb.ToString().TrimEndNewlines();
		}

		public override IEnumerable<Gizmo> GetGizmos()
		{
			foreach (Gizmo g in base.GetGizmos())
			{
				yield return g;
			}
			if (!DebugSettings.ShowDevGizmos)
			{
				yield break;
			}
			yield return new Command_Toggle
			{
				defaultLabel = "On",
				defaultDesc = "Switch this soak zone on or off. Off, the ground it soaked dries on its own clock.",
				icon = def.uiIcon,
				isActive = () => active,
				toggleAction = () => active = !active,
			};
			yield return new Command_Action
			{
				defaultLabel = "Size...",
				defaultDesc = "The square of ground it keeps soaked, centred on it. Now: " + SizeLabel(radius) + ".",
				icon = def.uiIcon,
				action = () =>
				{
					List<FloatMenuOption> opts = new List<FloatMenuOption>();
					foreach (int r in RadiusPresets)
					{
						int v = r;
						opts.Add(new FloatMenuOption(SizeLabel(v), () => radius = v));
					}
					Find.WindowStack.Add(new FloatMenu(opts));
				},
			};
			yield return new Command_Action
			{
				defaultLabel = "Hours...",
				defaultDesc = "How many hours of each day the ground stays soaked (the day counts from when it was placed). Now: "
					+ HoursLabel(hoursPerDay) + ".",
				icon = def.uiIcon,
				action = () =>
				{
					List<FloatMenuOption> opts = new List<FloatMenuOption>();
					foreach (float h in HourPresets)
					{
						float v = h;
						opts.Add(new FloatMenuOption(HoursLabel(v), () => hoursPerDay = v));
					}
					Find.WindowStack.Add(new FloatMenu(opts));
				},
			};
			yield return new Command_Action
			{
				defaultLabel = "Remove",
				defaultDesc = "Take this soak zone off the map. Ground it already soaked dries on its own clock.",
				icon = def.uiIcon,
				action = () => { if (!Destroyed) Destroy(DestroyMode.Vanish); },
			};
		}

		public string StateLine()
		{
			return def.defName + " " + ThingID + " at " + Position.x + "," + Position.z + " on=" + active + " size=" + SizeLabel(radius)
				+ " hoursPerDay=" + hoursPerDay.ToString("0.#", System.Globalization.CultureInfo.InvariantCulture)
				+ " lastSoaked=" + lastSoaked + " inert=" + (Spawned ? (Inert() ?? "no").Replace(' ', '_') : "unspawned");
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref active, "RM_soakZoneActive", true);
			Scribe_Values.Look(ref radius, "RM_soakZoneRadius", 2);
			Scribe_Values.Look(ref hoursPerDay, "RM_soakZoneHoursPerDay", 24f);
			Scribe_Values.Look(ref startTick, "RM_soakZoneStartTick", -1);
		}
	}
}
