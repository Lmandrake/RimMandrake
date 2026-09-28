using RimWorld;
using Verse;

namespace RimMandrake.Stillsand
{
    // SANDBUSTER_CASTES_BUILD_1 — the one piece of vanilla's Infestation
    // mechanism that genuinely cannot be reused unmodified through pure XML.
    //
    // Everything else about "re-skin the vanilla Infestation mechanism" is
    // data-driven and needed no C#:
    //   - CompSpawnerHives.TrySpawnChildHive spawns MORE OF THE PARENT'S OWN
    //     ThingDef (ThingMaker.MakeThing(parent.def)), not a hardcoded Hive —
    //     so mound reproduction (the "escalating waves") works for free once
    //     RM_SandBusterMound carries its own CompProperties_SpawnerHives.
    //   - CompSpawnerPawn.RandomPawnKindDef() reads ITS OWN
    //     CompProperties_SpawnerPawn.spawnablePawnKinds (per-instance), never
    //     the static Hive.spawnablePawnKinds list — so wiring RM_Ruukka/
    //     RM_Oorrik into the mound's own comp is enough to make it spawn our
    //     castes instead of Megaspider/Spelopede/Megascarab. (The static list
    //     is read only by TunnelHiveSpawner's own insectsPoints-based assault
    //     spawn, a branch neither vanilla's IncidentWorker_Infestation nor our
    //     own worker ever exercises — see RM_IncidentWorker_SandBusterEruption.)
    //   - The IncidentDef-level `allowedBiomes`/`disallowedBiomes` fields
    //     (checked in IncidentWorker.CanFireNow, engine-side, RimSage-read
    //     2026-09-27) confine the eruption incident to RM_Stillsand with no
    //     C# at all.
    //
    // The ONE hardcoded seam: RimWorld.TunnelHiveSpawner.Spawn() calls
    // RimWorld.HiveUtility.SpawnHive(...), which is hardcoded to
    // ThingMaker.MakeThing(ThingDefOf.Hive) — there is no def-level hook to
    // redirect that to our own mound. So this subclass overrides Spawn() to
    // do the equivalent for RM_SandBusterMound directly, skipping the
    // jelly/sludge extras HiveUtility.SpawnExtras adds (this mod's mound
    // carries neither comp, by design — see RM_SandBusterMound.xml's header).
    //
    // Faction/dormancy/wake-up all fall out for free: RM_SandBusterMound's
    // thingClass is RimWorld.Hive, whose own SpawnSetup() already does
    // `if (Faction == null) SetFaction(Faction.OfInsects)`, and its own
    // TickInterval() already wakes a freshly-erupted, unfogged mound the next
    // tick (CompCanBeDormant.startsDormant governs the initial "still under
    // the sand" beat; nothing here needs to touch it).
    public class RM_SandBusterTunnelSpawner : TunnelHiveSpawner
    {
        protected override void Spawn(Map map, IntVec3 loc)
        {
            if (spawnHive)
            {
                Thing mound = GenSpawn.Spawn(
                    ThingMaker.MakeThing(RM_StillsandDefOf.RM_SandBusterMound),
                    loc,
                    map,
                    WipeMode.FullRefund);
                mound.questTags = questTags;
            }

            // insectsPoints (the vanilla immediate-assault-force branch) is
            // never set for this incident — RM_IncidentWorker_SandBusterEruption
            // never passes it, matching vanilla IncidentWorker_Infestation's own
            // TryExecuteWorker, which also leaves it null. The threat here comes
            // entirely from the mound's own CompProperties_SpawnerPawn, exactly
            // like a vanilla storyteller-fired Infestation.
        }
    }
}
