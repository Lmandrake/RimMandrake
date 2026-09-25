using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M3 remainder, second half — greentide_kit_spec.md
    // M3's own line: "Spawned by an IncidentDef weighted into the biome and,
    // rarely, by the Roil condition itself." RUT_IncidentWorker_SteamDevil
    // shipped the IncidentDef route (M3/M7 build pass, 2026-09-14); this
    // ships the Roil-condition route, left explicitly owed by that pass —
    // its own note: "wiring a rare vortex spawn into [GameCondition_
    // EnvironmentalWeather] would mean extending a widely-reused shared
    // class, not a small addition, so it stays owed rather than retrofitted
    // under this pass" — and the item's "Owed" line named the fix as
    // "the shared GameCondition_EnvironmentalWeather class extended, OR A
    // SIDE MAPCOMPONENT". This ships the side MapComponent: RUT_RoilLock's
    // own conditionClass (GameCondition_EnvironmentalWeather) is untouched,
    // so every other biome's lock riding that same shared class (Scald
    // Steam, Miasma, this biome's own Wet Bulb pause hook) is unaffected.
    //
    // "The Roil condition itself" is read as the map's weather ACTUALLY
    // being RUT_RoilWeather right now, not merely RUT_RoilLock's permanent
    // biomeMapConditions entry being present (which is true on every
    // Greentide map at all times, Breaklight included — RUT_RoilLock never
    // ends; RUT_BreaklightCondition's own temporary ForcedWeather just wins
    // the actual sky for its own duration, per the M4/M5 build pass' own
    // note on how the two locks coexist). Gating on curWeather rather than
    // ConditionIsActive is what makes M4's own player-experience line true
    // here too ("it is always on; its absence [Breaklight] is the event"):
    // no fog-borne vortex spins up while the sky is genuinely clear.
    public class RM_MapComponent_RoilVortexSpawner : MapComponent
    {
        // INVENTED — the spec names no figure for this route's own rarity,
        // only "rarely". An order of magnitude rarer than the plain
        // incident route's own baseChance 2/minRefireDays 5
        // (RUT_SteamDevilAppears): this is meant to read as an occasional
        // extra flavor spawn straight out of the standing fog, not a second
        // storyteller-weighted event competing with the first.
        private const float SpawnMtbDays = 30f;

        // 1 in-game hour — matches RM_MapComponent_VaporColumns' own rescan
        // cadence for "a periodic ambient check", not a per-tick scan.
        private const int CheckIntervalTicks = 2500;

        private int ticksUntilCheck = CheckIntervalTicks;

        private static ThingDef steamDevilDefCached;
        private static WeatherDef roilWeatherDefCached;

        public RM_MapComponent_RoilVortexSpawner(Map map)
            : base(map)
        {
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (--ticksUntilCheck > 0)
            {
                return;
            }

            ticksUntilCheck = CheckIntervalTicks;
            TryRareSpawn();
        }

        private void TryRareSpawn()
        {
            if (!RM_EnvironmentalHazardsSettings.steamDevilEnabled)
            {
                return; // same master switch RUT_IncidentWorker_SteamDevil/RM_WanderingVortex already gate on
            }

            if (map?.Biome == null || map.Biome.defName != "RM_Greentide")
            {
                return; // matches RUT_IncidentWorker_SteamDevil's own CanFireNowSub biome check
            }

            WeatherDef roil = roilWeatherDefCached ??= DefDatabase<WeatherDef>.GetNamedSilentFail("RUT_RoilWeather");
            if (roil == null || map.weatherManager == null || map.weatherManager.curWeather != roil)
            {
                return; // content not deployed, or the sky isn't actually roiling right now (Breaklight, most likely)
            }

            ThingDef steamDevilDef = steamDevilDefCached ??= DefDatabase<ThingDef>.GetNamedSilentFail("RUT_SteamDevil");
            if (steamDevilDef == null)
            {
                return; // content not deployed — never a hard error over it, same posture as the incident route
            }

            if (map.listerThings.ThingsOfDef(steamDevilDef).Count > 0)
            {
                return; // one at a time from THIS route — a storyteller-fired one from the incident route can still coexist
            }

            if (!Rand.MTBEventOccurs(SpawnMtbDays, GenDate.TicksPerDay, CheckIntervalTicks))
            {
                return;
            }

            if (!RUT_IncidentWorker_SteamDevil.TryFindRiverCell(map, out IntVec3 cell))
            {
                return; // no water on this map — not a Greentide river map, quiet no-op
            }

            GenSpawn.Spawn(steamDevilDef, cell, map);

            Find.LetterStack.ReceiveLetter(
                "RUT_SteamDevilAppearsFromRoil".Translate(),
                "RUT_SteamDevilAppearsFromRoilDesc".Translate(),
                LetterDefOf.NeutralEvent,
                new TargetInfo(cell, map));
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ticksUntilCheck, "ticksUntilCheck", CheckIntervalTicks);
        }
    }
}
