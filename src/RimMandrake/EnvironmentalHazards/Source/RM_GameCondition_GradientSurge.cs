using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // MIASMA_MECHANICS_1 M2 build (miasma_kit_spec.md M2: "the breath-tide
    // surge"). Generic on purpose — parameterized on direction, magnitude,
    // ramp, per the spec's own words — and a deliberately THIN driver: the
    // actual per-tick salinity walk, banded terrain repaint (with the
    // floor-exclusion fix — see RM_GradientAxisRepaint), the MTB trigger,
    // and the recede all live on RM_MapComponent_GradientAxis instead of
    // here, because a MapComponent ticks for as long as the MAP exists
    // while a GameCondition is torn down the instant it Ends — and the
    // recede (2-4 INVENTED days) must keep moving for days after THIS
    // condition's own short ramp-in Duration elapses and it is destroyed.
    // This class's whole job: kick the forward shove off at Init, force the
    // surge weather for its own (ramp-in-length) lifetime, and kick the
    // recede off at End.
    //
    // "Direction" is not a stored Rot4 here: M1's GenStep already baked the
    // spatial gradient direction into the per-cell salinity field at map-gen
    // (brine toward the coast/lake, RM_GenStep_GradientAxis.BrineDirection).
    // A uniform scalar delta applied to every cell
    // (RM_MapComponent_GradientAxis.ApplyDeltaToAllCells) shoves that
    // existing gradient's isolines by an amount proportional to the delta —
    // positive = the salt line crawls toward fresh (the shove); negative =
    // it crawls back (the recede). No separate direction field is needed.
    //
    // ForcedWeather() override point: GameCondition.ForcedWeather()
    // (Source/RimWorld/GameCondition.cs, verified this spec — same seam
    // F1's RM_GameCondition_WeatherPulse and M4's
    // GameCondition_EnvironmentalWeather already use). def.weatherDef is a
    // real, existing GameConditionDef field (Source/Verse/
    // GameConditionDef.cs) — reused directly rather than adding a bespoke
    // extension field for a single forced weather, since (unlike
    // WeatherPulse) this condition never switches between two weathers; its
    // entire lifetime IS the ramp-in.
    public class RM_GameCondition_GradientSurge : GameCondition
    {
        // The forward shove's total salinity delta, recorded at Init so End
        // can size the recede as a fraction of it. Scribed: this condition
        // can be saved mid-ramp.
        private float totalDelta;

        private RM_GradientSurgeExtension Ext
        {
            get
            {
                Map map = SingleMap;
                return map != null && map.Biome != null ? map.Biome.GetModExtension<RM_GradientSurgeExtension>() : null;
            }
        }

        public override void Init()
        {
            base.Init();

            Map map = SingleMap;
            RM_MapComponent_GradientAxis axis = map != null ? map.GetComponent<RM_MapComponent_GradientAxis>() : null;
            RM_GradientSurgeExtension ext = Ext;
            if (map == null || axis == null || ext == null)
            {
                Log.WarningOnce(
                    "[RM EnvironmentalHazards] GameConditionDef " + (def != null ? def.defName : "(null)")
                    + " uses RM_GameCondition_GradientSurge but its map carries no RM_MapComponent_GradientAxis/RM_GradientSurgeExtension; the surge will do nothing.",
                    def != null ? def.shortHash ^ 0x5A17E1D : 0x5A17E1D);
                return;
            }

            int frontCells = ext.frontCellsRange.RandomInRange;
            float halfExtent = Mathf.Max(map.Size.x, map.Size.z) * 0.5f;
            totalDelta = halfExtent > 0f ? frontCells / (2f * halfExtent) : 0f;

            // Duration is the ramp-in itself — set by
            // IncidentWorker_MakeGameCondition from RUT_Surge's own
            // durationDays (the spec's "4-8 in-game hours"), not re-picked
            // here, so the ramp's timing lives in exactly one place (the
            // IncidentDef XML) rather than being duplicated onto this class.
            axis.ShiftAxis(totalDelta, Mathf.Max(1, Duration), isRecede: false);
        }

        public override void End()
        {
            base.End();

            Map map = SingleMap;
            RM_MapComponent_GradientAxis axis = map != null ? map.GetComponent<RM_MapComponent_GradientAxis>() : null;
            RM_GradientSurgeExtension ext = Ext;
            if (axis == null || ext == null || totalDelta == 0f)
            {
                return;
            }

            // The shove back: reverses MOST, never ALL, of the forward
            // delta — residual drift, miasma_kit_spec.md M2's own "never
            // quite to the old line, so no two maps age alike". Runs on the
            // MapComponent, independent of this condition's own (already
            // ending) lifetime — see this class's header.
            float recedeDelta = -totalDelta * (1f - ext.residualFraction);
            float recedeDays = ext.recedeDaysRange.RandomInRange;
            int recedeTicks = Mathf.Max(1, Mathf.RoundToInt(recedeDays * GenDate.TicksPerDay));
            axis.ShiftAxis(recedeDelta, recedeTicks, isRecede: true);
        }

        public override WeatherDef ForcedWeather()
        {
            return def != null ? def.weatherDef : null;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref totalDelta, "totalDelta", 0f);
        }
    }
}
