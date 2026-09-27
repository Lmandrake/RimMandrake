using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_DANGER_LIGHTWEB_1 §D4b — "killed, its lure organ is a small
    // trophy glower item." Attach to the vaulisk's RACE ThingDef. Pawn.Kill()
    // destroys the live Pawn Thing with DestroyMode.KillFinalize as part of
    // making its Corpse — the same hook family RM_CompEmergentSpawnOnDestroy
    // (Webwork, this repo) already proves for PostDestroy, there checking
    // DestroyMode.Vanish for a harvest; this checks KillFinalize for a kill.
    public class RM_CompProperties_DropLureOrganOnDeath : CompProperties
    {
        public RM_CompProperties_DropLureOrganOnDeath()
        {
            compClass = typeof(RM_Comp_DropLureOrganOnDeath);
        }

        // Soft lookup at drop time (never at load) — same posture as
        // RM_CompEmergentSpawnOnDestroy's spawnPawnKindDefName.
        public string dropThingDefName = "RM_VauliskLureOrgan";
    }

    public class RM_Comp_DropLureOrganOnDeath : ThingComp
    {
        public RM_CompProperties_DropLureOrganOnDeath Props => (RM_CompProperties_DropLureOrganOnDeath)props;

        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            if (previousMap == null || mode != DestroyMode.KillFinalize)
            {
                return; // only a kill drops the organ, never a despawn/vanish
            }
            ThingDef dropDef = DefDatabase<ThingDef>.GetNamedSilentFail(Props.dropThingDefName);
            if (dropDef == null)
            {
                return;
            }
            IntVec3 pos = parent.PositionHeld;
            if (!pos.IsValid || !pos.InBounds(previousMap))
            {
                return;
            }
            Thing organ = ThingMaker.MakeThing(dropDef);
            GenPlace.TryPlaceThing(organ, pos, previousMap, ThingPlaceMode.Near);
        }
    }
}
