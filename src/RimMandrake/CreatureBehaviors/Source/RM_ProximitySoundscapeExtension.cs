using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // GREENTIDE_HUMMING_GROVE_1 — the data side of
    // RM_MapComponent_ProximitySoundscape.
    //
    // Owner ruling 2026-09-22: build this GENERIC, reusable by any biome,
    // because this is the SECOND time the idea has come up (RustCathedralHum
    // is the first) and a second occurrence is the signal to generalise
    // rather than copy. So this assembly names no plant, no biome and no
    // sound of its own — a content mod tags its own ThingDef and supplies
    // its own SoundDefs, exactly the comp-plus-extension posture
    // RM_CompPlantAlarm and RM_CompWoundLink already set here.
    //
    //   <ThingDef>                      <!-- e.g. a humming tree -->
    //     <defName>RM_Thalquith</defName>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.CreatureBehaviors.RM_ProximitySoundscapeExtension">
    //         <groupKey>GreentideHummingGrove</groupKey>
    //         <humLayers>
    //           <li>RM_Hum_Thalquith_Low</li>
    //           <li>RM_Hum_Thalquith_Mid</li>
    //           <li>RM_Hum_Thalquith_High</li>
    //         </humLayers>
    //         <radius>22</radius>
    //         <thingsPerLayer>3</thingsPerLayer>
    //       </li>
    //     </modExtensions>
    //   </ThingDef>
    //
    // "Different frequencies" is several authored SoundDefs at different
    // pitches, NOT runtime pitch manipulation — the item's own ruling,
    // which sidesteps per-instance pitch entirely.
    public class RM_ProximitySoundscapeExtension : DefModExtension
    {
        // Groups several ThingDefs into one shared mix. Two defs with the
        // same groupKey count toward the same layer total and share one set
        // of sustainers; different keys are independent soundscapes that can
        // play at once. Required — a blank key is a config error rather than
        // a silent merge into an unnamed group.
        public string groupKey;

        // Played in list order: layer 0 first, each further layer added as
        // the nearby count rises. The list length is the hard ceiling on
        // layers, so a content mod controls how loud its own grove can get
        // purely by how many SoundDefs it ships.
        public List<SoundDef> humLayers = new List<SoundDef>();

        // Cells around the listener that count toward the total. INVENTED:
        // 22 — wide enough that walking in and out of a grove crosses the
        // boundary gradually rather than in one step.
        public float radius = 22f;

        // How many tagged Things must be near the listener per layer. With
        // thingsPerLayer 3 and four humLayers, 3 trees give one layer and 12
        // give the full mix. INVENTED.
        public int thingsPerLayer = 3;

        // How often the mix is recomputed. INVENTED: 60 — once a second, so
        // walking reads as continuous without scanning every tick.
        public int checkIntervalTicks = 60;

        // De-escalation-only hysteresis, in Things, copied in spirit from
        // RM_MapComponent_BiomeAttitude's own hysteresis margin: a layer is
        // ADDED as soon as the count earns it, but only DROPPED once the
        // count falls this far below the threshold that added it. Stops a
        // pawn standing on a boundary from flickering a layer on and off.
        // INVENTED.
        public int dropHysteresisThings = 1;

        // Floor on how often the layer count may change at all, on top of
        // the hysteresis. 🔴 This is the mitigation for the one recorded
        // obstacle: RM_MapComponent_SilenceCue records (RimSage-verified
        // against Verse/Sound/Sustainer.cs) that neither Sustainer nor
        // SustainerManager exposes a partial volume ramp, so a layer ENDS
        // outright and may pop audibly. Nothing here can fade it; all this
        // can do is make pops rare. INVENTED: 180.
        // ⛔ Do not report the result as smooth — the item requires the
        // owner to hear it before any such claim.
        public int minLayerChangeIntervalTicks = 180;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (groupKey.NullOrEmpty())
            {
                yield return "RM_ProximitySoundscapeExtension needs a groupKey.";
            }

            if (humLayers == null || humLayers.Count == 0)
            {
                yield return "RM_ProximitySoundscapeExtension needs at least one humLayers entry.";
            }
            else
            {
                for (int i = 0; i < humLayers.Count; i++)
                {
                    if (humLayers[i] == null)
                    {
                        yield return "RM_ProximitySoundscapeExtension humLayers[" + i + "] is null.";
                    }
                }
            }

            if (radius <= 0f)
            {
                yield return "RM_ProximitySoundscapeExtension radius must be > 0.";
            }

            if (thingsPerLayer < 1)
            {
                yield return "RM_ProximitySoundscapeExtension thingsPerLayer must be >= 1.";
            }

            if (checkIntervalTicks < 1)
            {
                yield return "RM_ProximitySoundscapeExtension checkIntervalTicks must be >= 1.";
            }

            if (dropHysteresisThings < 0)
            {
                yield return "RM_ProximitySoundscapeExtension dropHysteresisThings must be >= 0.";
            }

            if (minLayerChangeIntervalTicks < 0)
            {
                yield return "RM_ProximitySoundscapeExtension minLayerChangeIntervalTicks must be >= 0.";
            }
        }
    }
}
