using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ColdStorage
{
    /// <summary>
    /// The engine comp on a storage building (§4.0). Chill: the unit keeps its own temperature and items on its cells
    /// read it (Patch_Thing_AmbientTemperature), so vanilla rot does the rest. Stasis: items on its cells skip the rot
    /// tick and deterioration while the field holds, and keep room temperature, so they come out unfrozen.
    /// </summary>
    [StaticConstructorOnStartup]
    public class CompStorageClimate : ThingComp
    {
        private static readonly Texture2D TexLower = ContentFinder<Texture2D>.Get("UI/Commands/TempLower", true);
        private static readonly Texture2D TexRaise = ContentFinder<Texture2D>.Get("UI/Commands/TempRaise", true);
        private static readonly Texture2D TexReset = ContentFinder<Texture2D>.Get("UI/Commands/TempReset", true);

        public float currentTemp = float.NaN;
        public float setpoint = float.NaN;

        /// <summary>Per-instance stasis strength (share of rot the field stops), NaN = none: the Wrecked Machines grade
        /// or the def's stasisRotFactor decides. Set by code that places a chamber of a known grade (vault loot).</summary>
        public float stasisStrength = float.NaN;

        /// <summary>The tick this unit's temperature was last stepped; -1 before the first step.</summary>
        private int lastStepTick = -1;

        private CompPowerTrader power;
        private CompRefuelable fuel;
        private CompFlickable flick;
        private MapComponent_StorageClimate registeredOn;
        private CellRect registeredRect;

        public CompProperties_StorageClimate Props => (CompProperties_StorageClimate)props;

        public EffectiveMode Effective => ColdStorageKernel.Resolve(Props.mode, RM_ColdStorageSettings.chillEnabled, RM_ColdStorageSettings.stasisEnabled);

        public float EffectiveSetpoint => ColdStorageKernel.EffectiveSetpoint(Props.mode, Effective, setpoint);

        /// <summary>Powered, fuelled and switched on; a unit with neither power nor fuel is always active, except a stasis
        /// unit that needs power.</summary>
        public bool Active
        {
            get
            {
                if (flick != null && !flick.SwitchIsOn)
                {
                    return false;
                }
                if (power != null)
                {
                    return power.PowerOn;
                }
                if (fuel != null)
                {
                    return fuel.HasFuel;
                }
                return Props.mode != StorageMode.Stasis || Props.stasisNeedsNoPower;
            }
        }

        /// <summary>True while a stasis field holds: the rot tick and deterioration of held items are skipped.</summary>
        public bool StasisHolding => ColdStorageKernel.StasisHolds(Effective, Active);

        /// <summary>The stasis strength this instance has, or NaN to use the def's factor: its own
        /// <see cref="stasisStrength"/>, else its Wrecked Machines grade's ratio (owner ruling 2026-10-26: stasis strength
        /// follows the quality grade).</summary>
        public float InstanceStasisStrength => !float.IsNaN(stasisStrength) ? stasisStrength : ColdStorageStartup.GradeStrength(parent.def);

        /// <summary>The rot (and deterioration) multiplier on what a holding field of this unit holds.</summary>
        public float StasisRotFactor => ColdStorageKernel.UnitStasisRotFactor(Props.stasisRotFactor, InstanceStasisStrength);

        /// <summary>The temperature an item held here reads, if this unit overrides it.</summary>
        public bool TryGetHeldTemperature(out float temperature)
        {
            if (float.IsNaN(currentTemp))
            {
                temperature = 0f;
                return false;
            }
            return ColdStorageKernel.TryHeldTemperature(Effective, currentTemp, parent.Spawned, out temperature);
        }

        public float RoomTemperature
        {
            get
            {
                Map map = parent.MapHeld;
                if (map == null)
                {
                    return parent.AmbientTemperature;
                }
                return GenTemperature.GetTemperatureForCell(parent.PositionHeld, map);
            }
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            power = parent.GetComp<CompPowerTrader>();
            fuel = parent.GetComp<CompRefuelable>();
            flick = parent.GetComp<CompFlickable>();
            if (float.IsNaN(setpoint))
            {
                setpoint = Props.defaultSetpoint;
            }
            if (float.IsNaN(currentTemp))
            {
                currentTemp = RoomTemperature;
            }
            else if (!respawningAfterLoad && lastStepTick >= 0 && Find.TickManager != null)
            {
                // Reinstalled after being minified or carried: it was not ticked meanwhile, so let it drift for the time away.
                float hours = (Find.TickManager.TicksGame - lastStepTick) / ColdStorageKernel.TicksPerHour;
                currentTemp = ColdStorageKernel.Drift(currentTemp, RoomTemperature, Props.driftPerHour, RM_ColdStorageSettings.insulationMultiplier, hours);
            }
            if (Find.TickManager != null)
            {
                lastStepTick = Find.TickManager.TicksGame;
            }
            registeredOn = parent.Map.GetComponent<MapComponent_StorageClimate>();
            registeredRect = parent.OccupiedRect();
            registeredOn?.Register(this);
            UpdatePower(false);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            registeredOn?.Deregister(this, registeredRect);
            registeredOn = null;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref currentTemp, "currentTemp", float.NaN);
            Scribe_Values.Look(ref setpoint, "setpoint", float.NaN);
            Scribe_Values.Look(ref stasisStrength, "stasisStrength", float.NaN);
            Scribe_Values.Look(ref lastStepTick, "lastStepTick", -1);
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            Step(250);
        }

        public override void CompTickInterval(int delta)
        {
            base.CompTickInterval(delta);
            Step(delta);
        }

        /// <summary>Advance the unit's own temperature by <paramref name="ticks"/> and set its power draw.</summary>
        public void Step(int ticks)
        {
            if (!parent.Spawned)
            {
                return;
            }
            lastStepTick = Find.TickManager.TicksGame;
            float room = RoomTemperature;
            EffectiveMode eff = Effective;
            if (eff == EffectiveMode.Chill)
            {
                if (float.IsNaN(currentTemp))
                {
                    currentTemp = room;
                }
                float passiveDrop = power == null && fuel == null ? Props.passiveDrop : 0f;
                currentTemp = ColdStorageKernel.StepUnitTemperature(currentTemp, EffectiveSetpoint, room, Active, Props.canHeat,
                    Props.coolPerHour, Props.driftPerHour, passiveDrop, RM_ColdStorageSettings.insulationMultiplier,
                    ticks / ColdStorageKernel.TicksPerHour);
            }
            else
            {
                // Stasis keeps room temperature; a switched-off unit is a plain shelf.
                currentTemp = room;
            }
            UpdatePower(Mathf.Abs(currentTemp - EffectiveSetpoint) < 0.5f);
        }

        private void UpdatePower(bool atSetpoint)
        {
            if (power == null)
            {
                return;
            }
            power.PowerOutput = -ColdStorageKernel.PowerDraw(Effective, power.Props.PowerConsumption,
                RM_ColdStorageSettings.powerDrawMultiplier, atSetpoint, Props.idlePowerFactor);
        }

        public void SetSetpoint(float value)
        {
            setpoint = Mathf.Clamp(Mathf.Round(value), Props.minSetpoint, Props.maxSetpoint);
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra())
            {
                yield return g;
            }
            if (Effective != EffectiveMode.Chill || Props.mode != StorageMode.Chill || parent.Faction != Faction.OfPlayer)
            {
                yield break;
            }
            yield return SetpointCommand(-10f, TexLower, "RM_ColdStorage_SetpointLower10");
            yield return SetpointCommand(-1f, TexLower, "RM_ColdStorage_SetpointLower1");
            yield return new Command_Action
            {
                defaultLabel = "RM_ColdStorage_SetpointReset".Translate(),
                defaultDesc = "RM_ColdStorage_SetpointDesc".Translate(Props.defaultSetpoint.ToStringTemperature("F0")),
                icon = TexReset,
                action = () => SetSetpoint(Props.defaultSetpoint),
            };
            yield return SetpointCommand(1f, TexRaise, "RM_ColdStorage_SetpointRaise1");
            yield return SetpointCommand(10f, TexRaise, "RM_ColdStorage_SetpointRaise10");
        }

        private Command_Action SetpointCommand(float delta, Texture2D icon, string labelKey)
        {
            return new Command_Action
            {
                defaultLabel = labelKey.Translate(),
                defaultDesc = "RM_ColdStorage_SetpointDesc".Translate(setpoint.ToStringTemperature("F0")),
                icon = icon,
                action = () => SetSetpoint(setpoint + delta),
            };
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_ColdStorageSettings.showClimateReadout)
            {
                return null;
            }
            string name = (Props.method?.LabelCap ?? parent.LabelCap).ToString();
            switch (Effective)
            {
                case EffectiveMode.Chill:
                    if (float.IsNaN(currentTemp))
                    {
                        return null;
                    }
                    StringBuilder sb = new StringBuilder();
                    sb.Append("RM_ColdStorage_ChillReadout".Translate(name, currentTemp.ToStringTemperature("F0"), EffectiveSetpoint.ToStringTemperature("F0")));
                    if (!Active)
                    {
                        sb.Append(" ").Append("RM_ColdStorage_Drifting".Translate());
                    }
                    if (Props.mode == StorageMode.Stasis)
                    {
                        sb.AppendLine().Append("RM_ColdStorage_StasisOffChilling".Translate());
                    }
                    return sb.ToString();
                case EffectiveMode.Stasis:
                    string line = (StasisHolding ? "RM_ColdStorage_StasisHolding" : "RM_ColdStorage_StasisDown").Translate(name);
                    float factor = StasisRotFactor;
                    if (StasisHolding && factor > 0f)
                    {
                        // A partial-strength field (a Kludged or Refurbished grade) says how much rot still gets through.
                        line += "\n" + "RM_ColdStorage_StasisPartial".Translate((1f - factor).ToStringPercent(), factor.ToStringPercent());
                    }
                    return line;
                default:
                    return "RM_ColdStorage_SwitchedOff".Translate();
            }
        }
    }
}
