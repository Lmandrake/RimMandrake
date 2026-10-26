using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.ColdStorage
{
    /// <summary>Which Mod Settings switch hides a station or recipe (§6 "Methods").</summary>
    public enum ColdStorageGate
    {
        None,
        Resin,
        SandDry,
        Brine,
        EvaporativeCrock,
        SaltCrust,

        /// <summary>No switch of ours: the gate reads only <see cref="ColdStorageGateExtension.settingField"/> (another
        /// mod's switch, e.g. the Sump's tar sealing).</summary>
        External,
    }

    /// <summary>
    /// One preservation method (Chill / Stasis / CarbonFreeze / TarSeal / ResinSeal / SaltCrust / SandDry / Canned /
    /// Brine). The vocabulary other mods' recipes and cuisine require (§5); the engine reads its mode and its words.
    /// </summary>
    public class ColdStorageMethodDef : Def
    {
        public StorageMode mode = StorageMode.Sealed;

        /// <summary>The participle in inspect lines: "tar-sealed", "carbon-frozen".</summary>
        [MustTranslate]
        public string sealedLabel;

        /// <summary>The Mod Settings switch that hides stations and recipes of this method, if any.</summary>
        public ColdStorageGate gate = ColdStorageGate.None;

        public string SealedLabelCap => (sealedLabel ?? label ?? defName).CapitalizeFirst();

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (mode == StorageMode.Sealed && sealedLabel.NullOrEmpty())
            {
                yield return "sealed method has no sealedLabel";
            }
        }
    }

    /// <summary>Put on a BuildableDef or RecipeDef to hide it while its method is switched off in Mod Settings.</summary>
    public class ColdStorageGateExtension : DefModExtension
    {
        public ColdStorageGate gate = ColdStorageGate.None;

        /// <summary>Optional "Namespace.Type:field" naming a public static bool in another mod's settings, read live by
        /// reflection so that mod is never a dependency. The station or recipe shows only while that switch is on too.
        /// Unreadable (mod absent, field renamed): counts as on, with one warning.</summary>
        public string settingField;

        /// <summary>On a recipe whose ingredients come only from optional mods (MayRequire filter entries, e.g. brine
        /// or salt): when, after load, any ingredient's filter allows nothing, the recipe is hidden rather than left as
        /// a bill no pawn can ever fill.</summary>
        public bool hideIfIngredientEmpty = false;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (!settingField.NullOrEmpty() && !ColdStorageKernel.SplitSettingRef(settingField, out _, out _))
            {
                yield return "settingField must read Namespace.Type:field, got " + settingField;
            }
            if (gate == ColdStorageGate.External && settingField.NullOrEmpty())
            {
                yield return "gate External needs a settingField";
            }
        }
    }

    /// <summary>
    /// On a RecipeDef: an unskilled worker may spoil the product. Each product stack is rolled once; a spoiled stack
    /// becomes the same count of <see cref="ruinedInto"/>. Tar sealing uses it (Cooking under 8: 10% tar-ruined);
    /// Cuisine can reuse it for any "skill or it goes wrong" step.
    /// </summary>
    public class ColdStorageProductHazardExtension : DefModExtension
    {
        public SkillDef skill;
        public int belowLevel = 8;
        public float chance = 0.1f;
        public ThingDef ruinedInto;

        /// <summary>Optional "Namespace.Type:field" naming a public static float that overrides <see cref="chance"/>
        /// live (a Mod Settings slider in the mod that owns the recipe). Unreadable: the def chance.</summary>
        public string chanceSettingField;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (skill == null || ruinedInto == null)
            {
                yield return "ColdStorageProductHazardExtension needs skill and ruinedInto";
            }
            if (!chanceSettingField.NullOrEmpty() && !ColdStorageKernel.SplitSettingRef(chanceSettingField, out _, out _))
            {
                yield return "chanceSettingField must read Namespace.Type:field, got " + chanceSettingField;
            }
        }
    }

    /// <summary>
    /// On a preserved item ThingDef that is not sealed (sand-dried jerky, pickles, salt-crusted rations): the method
    /// tag Cuisine recipes require (section 5), and a fixed rot multiplier the engine applies to its rot tick.
    /// </summary>
    public class ColdStoragePreservedExtension : DefModExtension
    {
        public ColdStorageMethodDef method;

        /// <summary>Fixed multiplier on the item's rot tick: 0.1 = ten times slower. 1 = tag only.</summary>
        public float rotFactor = 1f;

        /// <summary>Flavour words a cuisine recipe may require or a dish may name ("amber", "pitch", "smoke", "brine").
        /// Free vocabulary for Star Wars Cuisine; the engine only stores it (ColdStorageFlavour reads it).</summary>
        public List<string> flavours;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (method == null)
            {
                yield return "ColdStoragePreservedExtension has no method";
            }
            if (rotFactor < 0f)
            {
                yield return "ColdStoragePreservedExtension rotFactor is negative";
            }
        }
    }

    public class CompProperties_StorageClimate : CompProperties
    {
        public StorageMode mode = StorageMode.Chill;
        public ColdStorageMethodDef method;

        public float defaultSetpoint = -10f;
        public float minSetpoint = -30f;
        public float maxSetpoint = 10f;

        /// <summary>Degrees an hour an active unit moves toward its setpoint.</summary>
        public float coolPerHour = 20f;

        /// <summary>Fraction of the gap to the room an inactive unit closes per hour, before the insulation setting.</summary>
        public float driftPerHour = 0.2f;

        /// <summary>For a unit with no power and no fuel: the most it can cool below the room (an evaporative crock).</summary>
        public float passiveDrop = 0f;

        public bool canHeat = false;

        /// <summary>Fraction of full power drawn once the setpoint is reached.</summary>
        public float idlePowerFactor = 0.3f;

        /// <summary>Whether the unit serves a nutrient paste dispenser while the hopper setting is on.</summary>
        public bool hopperCapable = false;

        /// <summary>For a stasis unit with no power and no fuel: whether its field holds anyway (an ancient locker).</summary>
        public bool stasisNeedsNoPower = true;

        /// <summary>Stasis mode: the fixed rot multiplier on what the field holds. 0 = a true stasis field (no rot, no
        /// deterioration); 0.1 = a weaker field that slows rot tenfold.</summary>
        public float stasisRotFactor = 0f;

        /// <summary>Stasis mode, powered unit: draw base power / field strength (design §4.2, a Kludged field runs
        /// hungry). Strength is the grade's (Wrecked Machines) or 1 - stasisRotFactor.</summary>
        public bool scalePowerByStrength = false;

        /// <summary>Stasis mode: mean in-game hours between field flickers; 0 = never. A flicker drops the field for
        /// stasisFlickerTicks (default one hour), letting normal rot through, and throws a spark mote.</summary>
        public float stasisFlickerMtbHours = 0f;

        public int stasisFlickerTicks = 2500;

        /// <summary>Coarse setpoint detents (warmest first, e.g. cool / cold / deep). When set, the setpoint gizmo cycles
        /// these instead of offering 1-degree steps: a crude machine has three settings, not a thermostat.</summary>
        public List<float> detents;

        /// <summary>Evaporative cooling: the passive drop scales with how dry the map's tile is and stops while it rains.
        /// Full drop at or under <see cref="evaporativeFullBelowRainfall"/> mm a year, none at or over
        /// <see cref="evaporativeZeroAtRainfall"/>.</summary>
        public bool evaporative = false;
        public float evaporativeFullBelowRainfall = 400f;
        public float evaporativeZeroAtRainfall = 1600f;

        /// <summary>Built into a wall: it replaces a wall (building.canPlaceOverWall), stores in its own cell, and serves
        /// the room on its facing side. Gets the wall Mod Settings (blocks light, airtight) and the propriety and reach
        /// patches.</summary>
        public bool wallMounted = false;

        /// <summary>Optional fuel the unit can burn instead of power (Mod Settings, per unit; takes effect on restart).
        /// The unit's CompProperties_Power is swapped for a CompProperties_Refuelable of this fuel.</summary>
        public ThingDef fuelAlternative;
        public float fuelAlternativePerDay = 6f;
        public float fuelAlternativeCapacity = 30f;

        public CompProperties_StorageClimate()
        {
            compClass = typeof(CompStorageClimate);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (mode == StorageMode.Sealed)
            {
                yield return "CompProperties_StorageClimate mode Sealed belongs on an item (CompProperties_Sealed), not a building";
            }
            if (minSetpoint > maxSetpoint)
            {
                yield return "minSetpoint above maxSetpoint";
            }
            if (stasisRotFactor < 0f || stasisRotFactor >= 1f)
            {
                yield return "stasisRotFactor must be in [0, 1)";
            }
            if (stasisFlickerMtbHours < 0f || stasisFlickerTicks < 1)
            {
                yield return "stasisFlickerMtbHours must be 0 or more and stasisFlickerTicks at least 1";
            }
            if ((scalePowerByStrength || stasisFlickerMtbHours > 0f) && mode != StorageMode.Stasis)
            {
                yield return "scalePowerByStrength / stasisFlickerMtbHours only apply to a Stasis unit";
            }
            if (detents != null)
            {
                if (detents.Count < 2)
                {
                    yield return "detents needs at least two settings";
                }
                foreach (float d in detents)
                {
                    if (d < minSetpoint || d > maxSetpoint)
                    {
                        yield return "detent " + d + " outside minSetpoint..maxSetpoint";
                    }
                }
            }
            if (evaporative && (passiveDrop <= 0f || evaporativeZeroAtRainfall <= evaporativeFullBelowRainfall))
            {
                yield return "evaporative needs passiveDrop > 0 and evaporativeZeroAtRainfall above evaporativeFullBelowRainfall";
            }
            if (wallMounted && (parentDef.building == null || !parentDef.building.canPlaceOverWall || parentDef.passability != Traversability.Impassable))
            {
                yield return "wallMounted needs building.canPlaceOverWall and Impassable passability";
            }
            if (fuelAlternative != null && (fuelAlternativePerDay <= 0f || fuelAlternativeCapacity <= 0f))
            {
                yield return "fuelAlternative needs a positive fuelAlternativePerDay and fuelAlternativeCapacity";
            }
            if (hopperCapable && parentDef.building == null)
            {
                yield return "hopperCapable on a def with no building properties";
            }
        }
    }

    public class CompProperties_Sealed : CompProperties
    {
        public ColdStorageMethodDef method;

        /// <summary>What it becomes after <see cref="agingDays"/>. Null: it never ages.</summary>
        public ThingDef agesInto;

        public float agingDays = 0f;

        /// <summary>Chance the aging transition ruins it instead, before the failure setting.</summary>
        public float failureChance = 0f;

        /// <summary>What a ruined seal becomes. Null: the seal opens and the food is rotten.</summary>
        public ThingDef ruinedInto;

        /// <summary>What breaking the seal gives. Null: the same item, unsealed, rotting normally from then on.</summary>
        public ThingDef openedInto;

        public CompProperties_Sealed()
        {
            compClass = typeof(CompSealed);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (method == null)
            {
                yield return "CompProperties_Sealed has no method";
            }
            if (agesInto != null && agingDays <= 0f)
            {
                yield return "agesInto set but agingDays is not positive";
            }
            if (parentDef.category != ThingCategory.Item)
            {
                yield return "CompProperties_Sealed on a non-item def";
            }
        }
    }

    /// <summary>
    /// On a workbench that works only in the right weather (a sand-drying box): bills wait while it is too cold
    /// outdoors or the box is roofed. Enforced by a postfix on Building_WorkTable.UsableForBillsAfterFueling.
    /// </summary>
    public class CompProperties_StationClimate : CompProperties
    {
        /// <summary>Outdoor temperature at or over which it works. -9999 = no heat needed. The sand box takes it from
        /// Mod Settings when <see cref="minTempFromSettings"/> is set.</summary>
        public float minOutdoorTemp = -9999f;
        public bool minTempFromSettings = false;
        public bool needsOpenSky = false;

        public CompProperties_StationClimate()
        {
            compClass = typeof(CompStationClimate);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (!typeof(Building_WorkTable).IsAssignableFrom(parentDef.thingClass))
            {
                yield return "CompProperties_StationClimate needs a Building_WorkTable (it gates bills)";
            }
        }
    }

    /// <summary>A tap on a living tree: draws resin (sap) from an adjacent tree and drops it in batches.</summary>
    public class CompProperties_ResinTap : CompProperties
    {
        public ThingDef resinDef;

        /// <summary>Resin a day from a fully grown, 25-wood, non-native tree, before the Mod Settings multiplier.</summary>
        public float perDay = 2f;

        public int batch = 10;

        public CompProperties_ResinTap()
        {
            compClass = typeof(CompResinTap);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (resinDef == null || perDay <= 0f || batch < 1)
            {
                yield return "CompProperties_ResinTap needs resinDef, a positive perDay and a batch of at least 1";
            }
        }
    }
}
