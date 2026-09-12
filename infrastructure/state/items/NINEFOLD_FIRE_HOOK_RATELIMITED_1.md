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

## Checked 2026-09-12 (FOUNDRY, owner AFK) — still blocked on deploy, not force-able

`mandrake.rm.ninefold` is present in the live `ModsConfig.xml` (currently
loaded), and the bridge is held by another window (`GIZKA hook live
confirmation`, idle 0 min) — the game is up and driving. Per the normal
"game must be DOWN to overwrite the DLL" rule, `deploy_custom_mods.py
--apply` is unsafe right now: the Ninefold DLL is locked. No live
fire-triggering quicktest attempted either, both because the bridge is
already contended by another agent and because deploying first is a
prerequisite for the live proof anyway (the offline-reverified source has
never round-tripped through a real load).

Set `needs=deploy` via rimflow. Nothing else to do on this item until the
game comes down for a load — at that point: deploy, then take the bridge
and run the fire repro described above before closing.
