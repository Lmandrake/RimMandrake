using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.NightsideIce
{
    // NIGHTSIDEICE_HEAT_DIAL_1 (split from NIGHTSIDEICE_HEAT_DIAL_BUILD_1 item 2; design
    // nightsideice_bedazzle_review_2026-10-01.md section 4 row 1, "the heat dial is the biome's law and
    // every later package reads it"). One continuous dial, 0..1, of how loud the colony is in heat on
    // the Sleeping Ice: working heaters, fires, power drawn, and warm enclosed rooms against the
    // outdoor cold. Readers (the breach loop, the shivven, the thaw pulse) call
    // RM_HeatDial.For(map).Dial; nothing here does harm by itself. The player sees it as an alert.
    //
    // raw = heater heat/s (player-owned pushers that are pushing now)
    //     + 20 x fire size (any fire on the map)
    //     + 0.01 x watts drawn (player-owned powered consumers that are on)
    //     + 0.002 x sum over enclosed rooms of (room temp - outdoor temp) x cells, warm rooms only
    // target = 1 - exp(-raw / heatDialScale); the dial eases halfway to the target every hour.
    public class RM_HeatDial : MapComponent
    {
        public const int IntervalTicks = 2500;
        public const float FireWeight = 20f;
        public const float PowerWeight = 0.01f;
        public const float RoomWeight = 0.002f;

        public float dial;
        public float lastRaw;
        public float heaters, fires, power, rooms;

        private static BiomeDef biome;
        public static BiomeDef NightsideIce => biome ?? (biome = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_NightsideIce"));

        public RM_HeatDial(Map map) : base(map)
        {
        }

        public static RM_HeatDial For(Map map)
        {
            return map?.GetComponent<RM_HeatDial>();
        }

        public bool Applies => RM_NightsideIceSettings.masterEnabled && RM_NightsideIceSettings.heatDialEnabled
            && map.Biome != null && map.Biome == NightsideIce;

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % IntervalTicks != 71)
            {
                return;
            }
            if (!Applies)
            {
                dial = 0f;
                return;
            }
            float target = Measure();
            dial = Mathf.Clamp01(Mathf.Lerp(dial, target, 0.5f));
        }

        /// <summary>Re-reads every source and returns the target dial (also stores the parts).</summary>
        public float Measure()
        {
            heaters = 0f;
            fires = 0f;
            power = 0f;
            rooms = 0f;
            Faction player = Faction.OfPlayer;

            List<Building> colony = map.listerBuildings.allBuildingsColonist;
            for (int i = 0; i < colony.Count; i++)
            {
                Building b = colony[i];
                if (b.Faction != player)
                {
                    continue;
                }
                CompHeatPusher hp = b.TryGetComp<CompHeatPusher>();
                if (hp != null && hp.ShouldPushHeatNow && hp.Props.heatPerSecond > 0f)
                {
                    heaters += hp.Props.heatPerSecond;
                }
                CompPowerTrader pt = b.TryGetComp<CompPowerTrader>();
                if (pt != null && pt.PowerOn && pt.PowerOutput < 0f)
                {
                    power += -pt.PowerOutput * PowerWeight;
                }
            }

            List<Thing> fireList = map.listerThings.ThingsOfDef(ThingDefOf.Fire);
            for (int i = 0; i < fireList.Count; i++)
            {
                if (fireList[i] is Fire f)
                {
                    fires += f.fireSize * FireWeight;
                }
            }

            float outdoor = map.mapTemperature.OutdoorTemp;
            IReadOnlyList<Room> all = map.regionGrid.AllRooms;
            for (int i = 0; i < all.Count; i++)
            {
                Room r = all[i];
                if (r == null || r.UsesOutdoorTemperature)
                {
                    continue;
                }
                float delta = r.Temperature - outdoor;
                if (delta > 0f)
                {
                    rooms += delta * r.CellCount * RoomWeight;
                }
            }

            lastRaw = heaters + fires + power + rooms;
            float scale = Mathf.Max(1f, RM_NightsideIceSettings.heatDialScale);
            return 1f - Mathf.Exp(-lastRaw / scale);
        }

        public string Readout()
        {
            StringBuilder sb = new StringBuilder();
            sb.Append("DIAL ").Append(dial.ToString("0.00"))
              .Append(" raw ").Append(lastRaw.ToString("0.0"))
              .Append(" heaters ").Append(heaters.ToString("0.0"))
              .Append(" fires ").Append(fires.ToString("0.0"))
              .Append(" power ").Append(power.ToString("0.0"))
              .Append(" rooms ").Append(rooms.ToString("0.0"))
              .Append(" applies=").Append(Applies)
              .Append(" biome=").Append(map.Biome?.defName ?? "-");
            return sb.ToString();
        }

        public override void ExposeData()
        {
            Scribe_Values.Look(ref dial, "rmHeatDial", 0f);
        }

        /// <summary>Bridge proof (jawa/static_call "current"): one immediate measure, dial snapped to the
        /// target. Holds on any map; "applies=False" off the Nightside Ice.</summary>
        public static string ProofDial(Map map)
        {
            RM_HeatDial d = For(map);
            if (d == null)
            {
                return "REFUSED: no map or no heat dial component";
            }
            d.dial = d.Measure();
            return d.Readout();
        }

        /// <summary>Bridge proof: measure, light a fire near the map centre, measure again, put it out.
        /// "BEFORE raw 12.0 AFTER raw 32.0 rose=True".</summary>
        public static string ProofFireRaisesDial(Map map)
        {
            RM_HeatDial d = For(map);
            if (d == null)
            {
                return "REFUSED: no map or no heat dial component";
            }
            d.Measure();
            float before = d.lastRaw;
            IntVec3 c;
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 15,
                    x => x.Standable(map) && !x.Fogged(map) && x.GetFirstThing<Fire>(map) == null, out c))
            {
                return "REFUSED: no free standable cell near the centre";
            }
            Fire fire = (Fire)ThingMaker.MakeThing(ThingDefOf.Fire);
            fire.fireSize = 1f;
            GenSpawn.Spawn(fire, c, map);
            d.Measure();
            float after = d.lastRaw;
            if (!fire.Destroyed)
            {
                fire.Destroy();
            }
            return "BEFORE raw " + before.ToString("0.0") + " AFTER raw " + after.ToString("0.0")
                + " rose=" + (after > before + 1f);
        }
    }

    /// <summary>The dial, shown: a plain alert on a Nightside Ice map once the colony is audible.</summary>
    public class Alert_RM_ThermalSignature : Alert
    {
        public Alert_RM_ThermalSignature()
        {
            defaultLabel = "Thermal signature";
            defaultPriority = AlertPriority.Medium;
        }

        private RM_HeatDial Current
        {
            get
            {
                Map m = Find.CurrentMap;
                RM_HeatDial d = RM_HeatDial.For(m);
                return d != null && d.Applies && RM_NightsideIceSettings.heatDialAlert
                    && d.dial >= RM_NightsideIceSettings.heatDialAlertThreshold ? d : null;
            }
        }

        public override string GetLabel()
        {
            RM_HeatDial d = Current;
            return d == null ? defaultLabel : "Thermal signature: " + Mathf.RoundToInt(d.dial * 100f) + "%";
        }

        public override TaggedString GetExplanation()
        {
            RM_HeatDial d = Current;
            string parts = d == null ? "" : "\n\nHeaters " + d.heaters.ToString("0") + ", fires " + d.fires.ToString("0")
                + ", power " + d.power.ToString("0") + ", warm rooms " + d.rooms.ToString("0") + ".";
            return "The ice is cold all the way down, and your colony is not. Everything warm here - heaters, fires, "
                + "running machines, heated rooms - carries through the ice, and things in the ice can feel it." + parts;
        }

        public override AlertReport GetReport()
        {
            return Current != null;
        }
    }
}
