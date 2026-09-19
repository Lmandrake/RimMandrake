# LONGHUNGER_QUICKTEST_1 — live quicktest, RUT_LongHunger enabled alongside donor sandworm

## spec
`mandrake.rut.longhunger` was enabled into the live 621-mod `ModsConfig.xml` by
`MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1` on 2026-09-19, on the strength of the
2026-09-05 owner ruling to keep both `chezhou.creature.sandworm` and
`RUT_LongHunger` active side by side. That enable had never been fire-tested. The
validation walk at `design/validation_walks/RimUtinni/LongHunger.md` lists the exact
checks; this item runs as many of them as one FOUNDRY overnight batch slot allows.

## verify — 2026-09-19 FOUNDRY (overnight full-621-mod batch)

Full 621-mod cold load confirmed clean via `Bridge token:`.

**Def read-backs — all 5/5 CONFIRMED** via `jawa/get_defs`:
- `ThingDef/RUT_LongHunger` resolved (thingClass reflection field name mismatch in the
  read tool — reports "(no such field)" for `thingClass`/`workerClass` since those are
  set via an XML `Class=` attribute, not a runtime field of that name; not a defect).
- `ThingDef/RUT_Groundcaller` resolved, `costList` present (2 entries, Steel+Component),
  `minifiedDef: MinifiedThing`.
- `IncidentDef/RUT_LongHungerSurfaces`: `baseChance: 0.0`, `minThreatPoints: 0.0`,
  `maxThreatPoints: 99999.0` — exactly the walk's expectation (never fires from the
  natural pool, threat range wide enough that `TestRunInt` never rejects it).
- `QuestScriptDef/RUT_LongHungerContract`: `rootSelectionWeight: 0.4` — matches.
- `WeatherDef/RUT_DuneHaze`: `isBad: true`, `favorability: Bad` — matches.

**Live spawn/eruption/submerge — CONFIRMED.** `rimworld/spawn_thing` placed
`RUT_LongHunger` on a quicktest map (2000/2000 HP at spawn, matching the walk's
`statBases.MaxHitPoints`). After 200 game ticks (`rimworld/step_game_ticks`, explicit
paused-mode stepping): HP dropped to 1820/2000 (91%) — self-damage consistent with the
eruption `GenExplosion` firing in `SpawnSetup` (a Bomb-radius blast this close to its
own origin plausibly clips the caster). Continued stepping to ~2700 ticks
post-spawn: the thing was **gone** (`jawa/list_things` returns 0 matches, scan count
consistent with the map's real thing total, not a filter miss) somewhere in the
~950–2450-tick-post-spawn window — consistent with the walk's "submerges at 2500
ticks" `Submerge()`/`Destroy(DestroyMode.Vanish)` behavior.

**Not confirmed this pass** (time-boxed, prioritized against the rest of the
overnight batch):
- Explicit loot verification — nearby cells after submerge showed only pre-existing
  mineable rubble (`HewnMarble`/`SolidMarble` chunks from the eruption crater); the
  full nearby-things list was not read to completion to specifically confirm a
  `Reward_ItemsStandard` (600–1400 marketValue) item landed. Worth a quick recheck —
  the mechanism fired (eruption + submerge both happened on schedule), so this is
  most likely a read-depth gap in this pass, not evidence the loot step failed.
- Quest offer/fire (`RUT_LongHungerContract` actually appearing/resolving in a live
  quest flow) — not attempted.
- Coexistence with the donor sandworm (`chezhou.creature.sandworm`) on the same
  map/campaign — not attempted; both mods loaded clean together in the same 621-mod
  session with no config errors or crossref failures naming either, which is a weak
  positive signal but not the actual coexistence test.
- The human-eye VFX/placeholder-art sanity check (walk step 9) — not looked at.

## criteria
- [x] Loads clean (no config error/XML error naming any of the 4 def files) —
      already confirmed by the enabling pass, re-confirmed this session.
- [x] Def read-backs (5/5).
- [x] Spawns, erupts (self-damage observed), submerges/destroys on schedule.
- [ ] Loot drop explicitly confirmed.
- [ ] Quest offer/fire.
- [ ] Coexistence with the donor sandworm actually exercised (not just co-loaded).
- [ ] Placeholder-art human-eye pass.

Leaving `doing` — 3 of 7 checks solidly confirmed, 1 more (loot) very likely fine but
not read to completion, 3 not attempted. A good candidate for a short follow-up rather
than a full re-run: def read-backs and the spawn/eruption/submerge mechanism do not
need re-proving.
