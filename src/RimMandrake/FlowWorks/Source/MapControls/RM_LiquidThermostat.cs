using System.Collections.Generic;
using System.Globalization;
using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.MapControls
{
	/// <summary>FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES (owner card 2026-10-16, design §2 #7): the LIQUID THERMOSTAT. FlowWorks
	/// liquid has no temperature of its own: hot and icy liquids warm or chill the ROOM they stand in through vanilla heat
	/// (RM_LiquidHeat, "one kind of heat"). This pebble makes the liquid within its radius behave as liquid held at a set
	/// temperature: every 250-tick liquid-heat interval (called from RM_LiquidHeat.Tick, after its own push), the wet
	/// squares in reach (a dug square's levels, or natural liquid as RM_LiquidHeat counts it) warm a room colder than the
	/// setting and chill a room warmer, at the liquid-heat rates, capped per room and never past the setting
	/// (RM_MapControlMath.ThermostatEnergy). So a roofed bath holds 40 C and a cistern room holds -5 C.
	/// As with all liquid heat, a room open to the sky takes no heat (vanilla Room.PushHeat), and the liquid-heat switch in
	/// Mod Settings ("liquidHeatPushEnabled") and its strength govern it.</summary>
	public class Building_RM_LiquidThermostat : Building_RM_MapControl
	{
		public const int NaturalCellLevels = 2;   // = RM_LiquidHeatMath.NaturalCellLevels

		public float targetC = 21f;
		public float radius = 3f;

		private int lastLevels;
		private int lastRooms;
		private float lastEnergy;
		private int lastOutdoorCells;

		private readonly Dictionary<Room, int> levelsByRoom = new Dictionary<Room, int>();

		public override bool WorksOnDugChannel => false;
		public override bool NeedsDepthEngine => false;
		protected override float SelectionRadius => radius;

		public override void FlowPulse(RM_MapComponent_Excavation ex)
		{
			// The heat interval drives it (HeatInterval), not the flow pulse.
		}

		/// <summary>One liquid-heat interval: push each touched room towards the setting.</summary>
		public void HeatInterval(RM_MapComponent_Excavation ex, float strength)
		{
			levelsByRoom.Clear();
			lastLevels = lastRooms = lastOutdoorCells = 0;
			lastEnergy = 0f;
			foreach (IntVec3 c in CellsInRadius(radius))
			{
				int levels = ex.IsExcavated(c) ? ex.FillAt(c) : (ex.IsSourceCell(c) ? NaturalCellLevels : 0);
				if (levels <= 0)
				{
					continue;
				}
				lastLevels += levels;
				Room room = c.GetRoom(Map);
				if (room == null)
				{
					// Deep water has no room: its first roomed neighbour takes it (RM_LiquidHeat routes it the same way).
					for (int i = 0; i < 8 && room == null; i++)
					{
						IntVec3 n = c + GenAdj.AdjacentCells[i];
						if (n.InBounds(Map))
						{
							room = n.GetRoom(Map);
						}
					}
				}
				if (room == null || room.UsesOutdoorTemperature)
				{
					lastOutdoorCells++;
					continue;
				}
				levelsByRoom.TryGetValue(room, out int had);
				levelsByRoom[room] = had + levels;
			}
			foreach (KeyValuePair<Room, int> kv in levelsByRoom)
			{
				float e = RM_MapControlMath.ThermostatEnergy(kv.Value, kv.Key.Temperature, kv.Key.CellCount, targetC, strength);
				if (e != 0f && kv.Key.PushHeat(e))
				{
					lastEnergy += e;
					lastRooms++;
				}
			}
		}

		protected override void AppendInspect(StringBuilder sb, RM_MapComponent_Excavation ex)
		{
			sb.AppendLine("Holds the liquid within " + radius.ToString("0.#", CultureInfo.InvariantCulture) + " squares at "
				+ targetC.ToStringTemperature() + ": it warms or chills the room over it towards that.");
			if (!RimMandrakeFlowWorksSettings.liquidHeatPushEnabled)
			{
				sb.AppendLine("Liquid heat is switched off in Mod Settings: no room is warmed or chilled.");
			}
			sb.Append("Last: " + lastLevels + " level(s) of liquid, " + lastRooms + " room(s) moved"
				+ (lastOutdoorCells > 0 ? ", " + lastOutdoorCells + " wet square(s) open to the sky (no effect)" : ""));
		}

		protected override IEnumerable<Gizmo> ControlGizmos()
		{
			yield return new Command_Action
			{
				defaultLabel = "Hold at " + targetC.ToStringTemperature(),
				defaultDesc = "The temperature this thermostat holds the liquid around it at.",
				icon = def.uiIcon,
				action = () =>
				{
					List<FloatMenuOption> opts = new List<FloatMenuOption>();
					foreach (float t in RM_MapControlMath.ThermostatPresets)
					{
						float pick = t;
						opts.Add(new FloatMenuOption(pick.ToStringTemperature(), () => targetC = pick));
					}
					Find.WindowStack.Add(new FloatMenu(opts));
				},
			};
			yield return RadiusGizmo("the liquid it holds", () => radius, v => radius = v);
		}

		public override string StateLine()
		{
			return "thermostat " + ThingID + " at " + Position.x + "," + Position.z + " active=" + active
				+ " target=" + targetC.ToString("0.#", CultureInfo.InvariantCulture)
				+ " radius=" + radius.ToString("0.#", CultureInfo.InvariantCulture) + " levels=" + lastLevels
				+ " rooms=" + lastRooms + " energy=" + lastEnergy.ToString("0.##", CultureInfo.InvariantCulture)
				+ " outdoorCells=" + lastOutdoorCells;
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref targetC, "RM_thermostatTarget", 21f);
			Scribe_Values.Look(ref radius, "RM_thermostatRadius", 3f);
		}
	}
}
