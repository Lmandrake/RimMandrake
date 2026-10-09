using RimWorld;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.Watchers
{
    /// <summary>
    /// WATCHER_CREATURES_MOD_1, owner ruling 2026-10-08 (DEATH card, typed): "Watchers can't be flushed. They just won't. Many damage
    /// types will take them out like fire explosions acid l, mostly aoe. Should take almost no damage to destroy them. Remains are of
    /// highly dubious value and kind of sad."
    ///
    /// How a hidden watcher dies (RimSage, decompiled 1.6): hiding is a HediffComp_Invisibility hediff, so the pawn stays SPAWNED in the
    /// thing grid. DamageWorker.ExplosionAffectCell damages every non-Ethereal thing in each cell, Fire damages the pawns in its cell,
    /// Projectile_Liquid (acid spray) damages every thing in each cell it lands on; none of them reads invisibility. Direct attacks are
    /// what invisibility stops: hostile verbs refuse an invisible target (Verb.CanHitTargetFrom), melee and AttackStatic give up on one,
    /// predators skip hidden prey (FoodUtility), the player cannot select or click it (IsHiddenFromPlayer), and the watch job drops any
    /// Hunt order as it goes under. Fragility (RM_WatcherKernel.FragilityErrors, audited at startup) makes one AOE hit lethal.
    /// RM_WatcherHidden sets recoverFromDisruptedTicks 0, so a survivor of a hit is not forced into view for the engine's default window.
    ///
    /// The death transition, one place: the watch job's finish action already runs (Pawn.Kill -> DeSpawn -> jobs.StopAll) and removes
    /// the hediff and the job's sign. This worker then removes ANY other sign naming the dead pawn (the live occupant relationship ends
    /// here, so no sign outlives its animal), takes the hidden hediff off the corpse's pawn (a hidden pawn draws nothing, corpse
    /// included), starts an alarm ripple from where it died, and swaps the corpse for the member's remains when it names one.
    /// </summary>
    public class RM_DeathActionWorker_Watcher : DeathActionWorker
    {
        public override void PawnDied(Corpse corpse, Lord prevLord)
        {
            Pawn pawn = corpse?.InnerPawn;
            if (pawn == null)
            {
                return;
            }
            RM_WatcherExtension ext = pawn.def.GetModExtension<RM_WatcherExtension>();
            Map map = corpse.MapHeld;
            IntVec3 cell = corpse.PositionHeld;
            if (ext == null || map == null)
            {
                return;
            }
            RM_WatcherDeath.ClearLivingState(pawn, ext, map);
            RM_WatcherAlarm.RaiseAt(pawn, cell, map);
            if (ext.remainsDef != null && corpse.Spawned)
            {
                Thing remains = ThingMaker.MakeThing(ext.remainsDef);
                remains.stackCount = ext.remainsCount;
                corpse.Destroy();
                GenPlace.TryPlaceThing(remains, cell, map, ThingPlaceMode.Near);
                if (ext.remainsCarries != null)
                {
                    foreach (ThingDefCountClass carry in ext.remainsCarries)
                    {
                        if (carry?.thingDef == null || carry.count <= 0)
                        {
                            continue;
                        }
                        Thing extra = ThingMaker.MakeThing(carry.thingDef);
                        extra.stackCount = carry.count;
                        GenPlace.TryPlaceThing(extra, cell, map, ThingPlaceMode.Near);
                    }
                }
            }
        }
    }

    public static class RM_WatcherDeath
    {
        /// <summary>Hediff off, every sign naming it gone (with any order on it).</summary>
        public static void ClearLivingState(Pawn pawn, RM_WatcherExtension ext, Map map)
        {
            if (ext.hiddenHediff != null && pawn.health?.hediffSet != null)
            {
                Hediff h = pawn.health.hediffSet.GetFirstHediffOfDef(ext.hiddenHediff);
                if (h != null)
                {
                    pawn.health.RemoveHediff(h);
                }
            }
            RM_WatcherUtility.RemoveSignsOf(pawn, map, ext.signDef);
        }

        /// <summary>Startup: give a member the kit's death action unless it already declares its own (then the job's finish action and the
        /// sign's own check still clear the living state, but no remains swap or death ripple happens, and a warning says so).</summary>
        public static void InstallDeathAction(ThingDef race, RM_WatcherExtension ext)
        {
            if (race.race == null || ext == null)
            {
                return;
            }
            DeathActionProperties cur = race.race.deathAction;
            if (cur == null || cur.workerClass == typeof(DeathActionWorker_Simple))
            {
                race.race.deathAction = new DeathActionProperties { workerClass = typeof(RM_DeathActionWorker_Watcher) };
            }
            else if (cur.workerClass != typeof(RM_DeathActionWorker_Watcher))
            {
                Log.Warning("[Watchers] " + race.defName + " has its own deathAction (" + cur.workerClass?.Name
                    + "): its remains and death ripple are not applied");
            }
        }
    }
}
