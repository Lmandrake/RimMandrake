# NINEFOLD_FIRE_HOOK_RATELIMITED_1 — hook built, not yet proven live

Fire as a Zizzik/Sh'kaar input needed an incident-level or rate-limited hook — a
per-fire hook on `FireUtility.TryStartFireIn` would flood satiation in one
forest fire, since `Fire.TrySpread` calls that same method again for every
burning cell every 75-150 ticks.

## Built, 2026-09-05 (FOUNDRY, offline while BENCH held the bridge)

`src/RimMandrake/Ninefold/Source/Patch_FireStarted.cs` — a Harmony postfix on
`FireUtility.TryStartFireIn`, keyed on `Fire.instigator` identity (verified
against `Fire.cs:400`: `TrySpread` re-passes the same instigator to every
downstream spread call, so one ignition's whole spread chain shares one
identity even generations later). A per-instigator time-window rate limiter
(`RateLimitWindowTicks = 600`, ~10s, UNTUNED first-pass placeholder — same
status as `EventMagnitude`/`MoodAmplitude`/`RootedErosionPerHour` in
`GameComponent_Ninefold.cs`, deferred to the §10 SATIATION_TUNING_RIG) credits
`God.Zizzik` + `God.Shkaar` at most once per instigator per window, no matter
how many cells that fire ignites in that window. Ambient/natural ignition
(`instigator == null`) shares one conservative shared bucket.

Build clean (`dotnet build Ninefold.csproj -c Release`, 0 errors). Harmony
target signature verified against live 1.6 source via RimSage:
`bool TryStartFireIn(IntVec3 c, Map map, float fireSize, Thing instigator,
SimpleCurve flammabilityChanceCurve = null)` matches the patch's
`__result`/`instigator` parameter names exactly.

## criteria
- [x] Mechanism identified and implemented: incident-aware (instigator-keyed),
      not per-cell.
- [x] Build clean.
- [ ] **Proven live** — needs the bridge: start a fire (a molotov/incendiary
      launcher against a flammable target is the fastest repro), let it spread
      to several cells, and confirm via `jawa/harmony_patches` +
      `GameComponent_Ninefold`'s own satiation read-back that Zizzik/Sh'kaar
      moved ONCE per incident, not once per cell. Not deployed to the live
      game copy yet either (companion-DLL-style deploy not needed here — this
      is a regular mod DLL, blocked only by the normal "game must be DOWN to
      overwrite the DLL" rule like any other mod).
