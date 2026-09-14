using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SCALD_MECHANICS_1 S2 build pass (scald_kit_spec.md "the steam-catch").
    //
    // Crib of the confirmed-real `PlaceWorker_OnSteamGeyser`
    // (RimWorld/PlaceWorker_OnSteamGeyser.cs, decompile, spike finding 2):
    // that class hardcodes `ThingDefOf.SteamGeyser` in a two-line check.
    // This kit's condensers must instead lock onto whatever
    // `CompProperties_ResourceCondenser.requiredThingAtPosition` the
    // BUILDING ITSELF carries — hardcoding RUT_ScaldVent here would make a
    // generic RM_ class know a Scald-tier defName, exactly the "one class,
    // many hardcoded subclasses" problem this kit family exists to remove
    // (ALPHA_MECHANICS_KIT_1's own stated design). `ThingDef.GetCompProperties<T>()`
    // (Verse/ThingDef.cs, confirmed real) lets the PlaceWorker read the
    // required def straight off checkingDef's own comps list — zero new
    // XML surface, zero per-kit subclassing needed.
    //
    //   <placeWorkers>
    //     <li>RimMandrake.EnvironmentalHazards.RM_PlaceWorker_OnRequiredVentComp</li>
    //   </placeWorkers>
    //
    // A building using this PlaceWorker MUST also carry a
    // CompProperties_ResourceCondenser (or ConfigErrors would need to catch
    // the omission at the comp, not here — PlaceWorker instances get no
    // ConfigErrors hook of their own). Not enforced here; ban 1 patrol only
    // cares that misconfiguration fails safe (AllowsPlacing false-by-null
    // below), not that it fails loud.
    public class RM_PlaceWorker_OnRequiredVentComp : PlaceWorker
    {
        public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
        {
            ThingDef required = RequiredThingDef(checkingDef);
            if (required == null)
            {
                // Misconfigured (no CompProperties_ResourceCondenser, or its
                // requiredThingAtPosition is unset) — refuse rather than
                // silently allow placing anywhere, which would defeat the
                // whole "locked to vents" point.
                return "RM_MustPlaceOnRequiredVent".Translate();
            }

            Thing found = map.thingGrid.ThingAt(loc, required);
            if (found == null || found.Position != loc)
            {
                return "RM_MustPlaceOnRequiredVent".Translate();
            }

            return true;
        }

        public override bool ForceAllowPlaceOver(BuildableDef otherDef)
        {
            ThingDef other = otherDef as ThingDef;
            return other != null && IsAnyKnownRequiredDef(other);
        }

        public override void DrawMouseAttachments(BuildableDef def)
        {
            ThingDef required = RequiredThingDef(def);
            if (required == null || Find.CurrentMap == null)
            {
                return;
            }

            List<Thing> list = Find.CurrentMap.listerThings.ThingsOfDef(required);
            for (int i = 0; i < list.Count; i++)
            {
                TargetHighlighter.Highlight(list[i]);
            }
        }

        private static ThingDef RequiredThingDef(BuildableDef checkingDef)
        {
            ThingDef td = checkingDef as ThingDef;
            CompProperties_ResourceCondenser props = td != null
                ? td.GetCompProperties<CompProperties_ResourceCondenser>()
                : null;
            return props != null ? props.requiredThingAtPosition : null;
        }

        // ForceAllowPlaceOver has no "this specific instance" context, only
        // the two ThingDefs — so this checks against every def in the
        // database that carries a matching comp rather than a single
        // required def. Rare enough (a handful of condenser-family
        // buildings) that the scan cost is irrelevant, and it is only ever
        // evaluated in the placement-preview UI, never per-tick.
        private static bool IsAnyKnownRequiredDef(ThingDef otherDef)
        {
            List<ThingDef> allDefs = DefDatabase<ThingDef>.AllDefsListForReading;
            for (int i = 0; i < allDefs.Count; i++)
            {
                CompProperties_ResourceCondenser props = allDefs[i].GetCompProperties<CompProperties_ResourceCondenser>();
                if (props != null && props.requiredThingAtPosition == otherDef)
                {
                    return true;
                }
            }
            return false;
        }
    }
}
