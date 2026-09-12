using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.JawaIonWeapons
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Jawa Ion Weapons.
    //
    // Precedent, copied field-for-field in shape:
    //   src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs
    //   src/RimMandrake/Greentide/Source/RM_GreentideMod.cs
    // STATIC fields, read from everywhere, written only here — the damage
    // worker and the StatPart both run in contexts where no Mod instance is
    // handy, so the values have to survive as statics.
    //
    // 🔑 DEFAULTS ARE THE SHIPPED NUMBERS, EXACTLY.
    //   stunBuildupMultiplier    1.0  — severity comes from the DamageDef's own
    //                                   additionalHediffs block (0.03 per point
    //                                   of damage, DamageDefs_JawaIon.xml); this
    //                                   multiplies that, it does not replace it.
    //   bodySizeResistExponent   2.0  — the owner's ruled bodySize^2 barrier
    //                                   (ION_STUN_IGNORES_BODY_SIZE_1, 2026-08-29).
    //                                   At exactly 2 the arithmetic below is the
    //                                   literal `bodySize * bodySize` that shipped,
    //                                   NOT Mathf.Pow, so there is no float drift
    //                                   at the default.
    //   machineTier*             on, 1.0 — empAmountMachine 60 / empAmountDroid 24
    //                                   still come from IonDamageDef's XML.
    //   vehicleTier*             on, 1.0 — read across by JawaIonVehicleTier.dll.
    //
    // ALL-OFF DEGRADES GRACEFULLY: with every toggle off the ion blaster is
    // still a working (very weak) gun — it simply stops depositing buildup,
    // stops re-issuing EMP, and stops breaking shields. Nothing NREs, no def
    // fails to resolve, because every gate is an early return inside a method
    // that is allowed to do nothing.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_JawaIonWeaponsSettings : ModSettings
    {
        /// <summary>Bottom tier: the accumulating RSW_JawaIon_Stun on flesh and droids.</summary>
        public static bool fleshBuildupEnabled = true;

        /// <summary>Multiplier on the XML-declared severity deposited per hit.</summary>
        public static float stunBuildupMultiplier = 1f;

        /// <summary>
        /// Exponent of the body-size resistance barrier. 2 = shipped (a target
        /// twice the size takes four times the fire). 0 = size does not matter.
        /// </summary>
        public static float bodySizeResistExponent = 2f;

        /// <summary>
        /// The pure-XML route that lends the same body-size barrier to OTHER mods'
        /// stun weapons, via StatDef RSW_Jawa_InverseBodySize and
        /// StatPart_InverseBodySize. Off = that stat reads its neutral
        /// defaultBaseValue of 1.0 and third-party weapons behave as they always did.
        /// </summary>
        public static bool thirdPartyBodySizeScaling = true;

        /// <summary>Top two tiers: the EMP re-issue that hard-stuns mechs and droids.</summary>
        public static bool machineTierEnabled = true;

        /// <summary>Multiplier on empAmountMachine / empAmountDroid.</summary>
        public static float machineTierMultiplier = 1f;

        /// <summary>The 1-point EMP dispatch that pops a personal shield on hit.</summary>
        public static bool shieldBreakEnabled = true;

        /// <summary>Master switch for the Vehicle Framework tier (JawaIonVehicleTier.dll).</summary>
        public static bool vehicleTierEnabled = true;

        /// <summary>Multiplier on the vehicle stun amount, before footprint scaling.</summary>
        public static float vehicleTierMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref fleshBuildupEnabled, "fleshBuildupEnabled", true);
            Scribe_Values.Look(ref stunBuildupMultiplier, "stunBuildupMultiplier", 1f);
            Scribe_Values.Look(ref bodySizeResistExponent, "bodySizeResistExponent", 2f);
            Scribe_Values.Look(ref thirdPartyBodySizeScaling, "thirdPartyBodySizeScaling", true);
            Scribe_Values.Look(ref machineTierEnabled, "machineTierEnabled", true);
            Scribe_Values.Look(ref machineTierMultiplier, "machineTierMultiplier", 1f);
            Scribe_Values.Look(ref shieldBreakEnabled, "shieldBreakEnabled", true);
            Scribe_Values.Look(ref vehicleTierEnabled, "vehicleTierEnabled", true);
            Scribe_Values.Look(ref vehicleTierMultiplier, "vehicleTierMultiplier", 1f);
        }

        /// <summary>
        /// The number a stun severity (or an EMP amount) is DIVIDED by to model a
        /// bigger target resisting. Returns the literal shipped `bodySize * bodySize`
        /// at the default exponent so defaults reproduce shipped behavior bit for bit.
        /// </summary>
        public static float BodySizeDivisor(float bodySize)
        {
            if (bodySize <= 0f)
            {
                return 1f;
            }
            float exponent = bodySizeResistExponent;
            if (exponent <= 0f)
            {
                return 1f;
            }
            if (exponent == 2f)
            {
                return bodySize * bodySize;
            }
            return Mathf.Pow(bodySize, exponent);
        }

        private static string ResistLabel()
        {
            if (bodySizeResistExponent <= 0.01f) return "size is ignored";
            if (bodySizeResistExponent < 1.5f) return "mild (" + bodySizeResistExponent.ToString("0.0") + ")";
            if (bodySizeResistExponent < 2.5f) return "default (" + bodySizeResistExponent.ToString("0.0") + ")";
            return "harsh (" + bodySizeResistExponent.ToString("0.0") + ")";
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("People and droids — wearing a target down");
            list.CheckboxLabeled("Stun buildup enabled", ref fleshBuildupEnabled,
                "Every ion hit adds \"ion buildup\" to a living target until it collapses, alive and "
              + "unhurt. Off: the blaster still fires and still breaks shields, but nobody ever "
              + "builds up a charge.");
            list.Label("Stun buildup per hit: " + stunBuildupMultiplier.ToString("0.00") + "x");
            list.Label("Higher means fewer shots to drop someone. 1.00x is the shipped weapon: "
              + "about six solid hits on a person.");
            stunBuildupMultiplier = list.Slider(stunBuildupMultiplier, 0.25f, 3f);
            list.Gap();

            list.Label("How much bigger targets resist stunning: " + ResistLabel());
            list.Label("At the default, doubling a target's size makes it take four times the fire, "
              + "so a rat drops instantly and a giant barely notices. Slide to the left to make size "
              + "matter less; at the far left every target takes the same buildup.");
            bodySizeResistExponent = list.Slider(bodySizeResistExponent, 0f, 3f);
            list.CheckboxLabeled("Use the same size rule on other mods' stun guns", ref thirdPartyBodySizeScaling,
                "Other mods' sonic and knockout weapons get the same \"bigger targets resist more\" "
              + "rule, where a patch has opted them in. Off: those weapons keep their own behaviour.");
            list.GapLine();

            list.Label("Machines and mechanoids — instant overload");
            list.CheckboxLabeled("Overload machines on hit", ref machineTierEnabled,
                "A mechanoid or droid is hard-stunned the moment it is hit, the way an EMP grenade "
              + "does it. Off: machines take no stun from ion fire at all.");
            list.Label("Overload strength: " + machineTierMultiplier.ToString("0.00") + "x");
            machineTierMultiplier = list.Slider(machineTierMultiplier, 0.25f, 3f);
            list.GapLine();

            list.Label("Shields");
            list.CheckboxLabeled("Ion fire pops personal shields", ref shieldBreakEnabled,
                "A hit instantly drains a shield belt, on anyone wearing one. Off: shields absorb ion "
              + "fire like any other shot.");
            list.GapLine();

            list.Label("Vehicles (needs Vehicle Framework installed)");
            list.Label("These do nothing unless the Vehicle Framework mod is active — without it the "
              + "vehicle part of this mod switches itself off already.");
            list.CheckboxLabeled("Stun vehicles", ref vehicleTierEnabled,
                "Ion fire stalls a vehicle. Bigger vehicles take proportionally more hits. Off: "
              + "vehicles take ordinary component damage and nothing else.");
            list.Label("Vehicle stun strength: " + vehicleTierMultiplier.ToString("0.00") + "x");
            vehicleTierMultiplier = list.Slider(vehicleTierMultiplier, 0.25f, 3f);

            list.End();
        }
    }

    public class RSW_JawaIonWeaponsMod : Mod
    {
        public static RSW_JawaIonWeaponsSettings settings;

        public RSW_JawaIonWeaponsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_JawaIonWeaponsSettings>();
        }

        public override string SettingsCategory()
        {
            return "Jawa Ion Weapons";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
