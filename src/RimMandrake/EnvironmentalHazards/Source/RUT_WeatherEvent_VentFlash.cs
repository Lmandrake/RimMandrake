using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound; // PlayOneShotOnCamera is an extension method on SoundStarter, not a SoundDef member

namespace RimMandrake.EnvironmentalHazards
{
    // SCALD_STEAM_WEATHER_DESIGN_1 §3.1 step 7, built 2026-09-26.
    //
    // The sheet's §9 sound line asks for "geyser percussion" felt across
    // the whole shore, and its motion line for "geyser rhythm". A vent
    // field already spouts per-vent (vanilla's geyser effecter, on
    // RUT_ScaldVent), but that is local: stand fifty cells away and the
    // Scald's rhythm is invisible. This is the map-wide half — every few
    // hours the sky briefly whites out as a big vent lets go somewhere
    // beyond the frame, with the spray heard off-camera.
    //
    // Cribbed directly from vanilla's own WeatherEvent_LightningFlash
    // (RimWorld/WeatherEvent_LightningFlash.cs, read in full): same
    // age/duration shape, same SkyTarget override, same fade curve. Two
    // deliberate differences:
    //
    //   * NO shadow vector. A lightning flash throws hard shadows from one
    //     side because it is a point source overhead; a vent plume lighting
    //     the underside of a standing steam layer is diffuse, and a raking
    //     shadow would read as lightning — which the Scald never has (its
    //     own weather is zero rain, zero snow, by ruling).
    //   * Warmer, whiter, gentler colours and a lower lerp ceiling, so it
    //     reads as the steam layer brightening rather than a strike.
    //
    // ⚠️ Every number here is INVENTED. The sheet gives a rhythm, not a
    // figure. `averageInterval` lives in XML (RUT_ScaldSteam.xml's
    // eventMakers) so it is tunable without a rebuild.
    //
    // Gate: Scald.S1.flash, checked in FireEvent — the cheapest correct
    // place, because an event already constructed and added costs nothing
    // if it neither plays nor brightens. Returning early from FireEvent
    // leaves `age` ticking and the event expiring normally; SkyTarget is
    // suppressed by the same flag so a mid-flight flash goes dark
    // immediately when the toggle flips.
    public class RUT_WeatherEvent_VentFlash : WeatherEvent
    {
        private const int FadeInTicks = 6;
        private const int MinDurationTicks = 30;
        private const int MaxDurationTicks = 90;

        // White with the Scald's own cyan bleed, saturation just above
        // neutral: the steam layer lighting up from below, not a strike.
        private static readonly SkyColorSet VentFlashColors = new SkyColorSet(
            new Color(0.95f, 0.99f, 1f),
            new Color(0.88f, 0.93f, 0.95f),
            new Color(0.95f, 0.99f, 1f),
            1.05f);

        private readonly int duration;
        private int age;

        private static bool Allowed => RM_MechanicGates.Enabled("Scald.S1.flash");

        public RUT_WeatherEvent_VentFlash(Map map)
            : base(map)
        {
            duration = Rand.Range(MinDurationTicks, MaxDurationTicks);
        }

        public override bool Expired => age > duration;

        public override SkyTarget SkyTarget => new SkyTarget(1f, VentFlashColors, 1f, 1f);

        public override float SkyTargetLerpFactor => Allowed ? Brightness : 0f;

        // Deliberately not overriding OverrideShadowVector — see the header.

        private float Brightness
        {
            get
            {
                if (age <= FadeInTicks)
                {
                    return (float)age / FadeInTicks * 0.7f;
                }
                return (1f - (float)age / duration) * 0.7f;
            }
        }

        public override void FireEvent()
        {
            if (!Allowed)
            {
                return;
            }

            // Vanilla's own geyser sound, resolved by name rather than
            // through SoundDefOf (which does not carry it). SilentFail so a
            // future rename is a missing noise, never a red error every
            // four hours.
            SoundDef spray = DefDatabase<SoundDef>.GetNamedSilentFail("GeyserSpray");
            if (spray != null)
            {
                spray.PlayOneShotOnCamera(map);
            }
        }

        public override void WeatherEventTick()
        {
            age++;
        }
    }
}
