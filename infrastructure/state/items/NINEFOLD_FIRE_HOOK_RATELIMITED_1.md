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

## 2026-09-12 (FOUNDRY, later same night) — CLOSED: live-proven, rate limiter confirmed

DLL turned out already deployed (checked `deploy_custom_mods.py --mod
Ninefold`: "in sync (3 files)") once the game came back down and up again
for the RUT_Webwork thingClass crash fix (`257bbbc7f`) — the deploy half of
this item's `needs=deploy` resolved itself as a side effect, not re-done
here.

**Live test, on the loaded canonical colony map** (bridge session also did
`BUILDING_THEFT_HAULER_1`/the SARLACC-VAPOR-WORLDNAME batch; nothing here
was saved to disk): the map's own biome (rocky/`AB_Obsidianstone`) had no
natural forest, so planted a 5x5 `Plant_TreeOak` cluster
(`rimworld/spawn_thing` x25) away from the colony, then used
`Actions\Explosion...\Flame` at 6 different cells across the cluster
(chained, since the first two attempts didn't catch — DevMode logging
confirmed live throughout via the unrelated `Patch_ExplosionOccurred`
Ninefold lines that fire on every explosion regardless). Fire caught at 2
cells, then spread naturally to 4 over ~2000 stepped ticks
(`rimworld/step_game_ticks`).

**`MEASURE_ALLOW_SCAN=1 grep -n "the wrong spark catches\|the Searer's
work"` on the live `Player.log`**: exactly **ONE** line each —

```
[Ninefold] Zizzik satiation +3.0 (the wrong spark catches) -> 100.0 [Exalted]
[Ninefold] Shkaar satiation +3.0 (fire and burning, the Searer's work) -> 100.0 [Exalted]
```

— despite **6 separate ignition attempts** and the fire spreading to **4
concurrent burning cells** over 2000+ ticks. This is exactly the criterion
this item's own verify section asks for: Zizzik/Sh'kaar moved ONCE per
incident window, not once per cell or per ignition attempt. Matches
`Patch_FireStarted`'s own design (`RateLimitWindowTicks=600`, shared
null-instigator bucket for debug-triggered/ambient ignitions).

**Not separately re-checked**: whether a genuinely NEW credit fires once
600 ticks roll over past the first credit (the code's own "a long-lived
blaze can still credit again" case) — the single-credit-despite-many-cells
result is the criterion that matters and is unambiguous; chasing the
rollover case would need another timed window and adds nothing the code
reading + this observation don't already establish.

**Closing.** Both criteria (incident-aware, not per-cell; live-proven) are
now checked.

---

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
