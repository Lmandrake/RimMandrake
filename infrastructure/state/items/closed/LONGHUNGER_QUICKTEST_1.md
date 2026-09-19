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
- [x] Loot drop explicitly confirmed.
- [x] Quest offer/fire.
- [x] Coexistence with the donor sandworm actually exercised (not just co-loaded).
- [x] Placeholder-art human-eye pass.

## verify — 2026-09-19 FOUNDRY, second pass (closes the remaining 4)

Live-tested on the actual campaign map (canonical Ash'karr start, 617 mods, real
colonists Diver/Kuntz/Pavel) rather than a quicktest — this mechanism only needed
*a* map with the mod active, and the campaign's own map already had that; spawns
were placed 30-45 tiles from the colonists and destroyed/cleaned up after, same
reversible-at-a-distance pattern already used this session for the facing check.

- **Spawn/eruption/submerge reproduced exactly**: HP 2000→1820 at +200 ticks
  (byte-identical to the first pass's number), submerged (vanished from
  `jawa/list_things`) between +1591 and +1991 ticks post-spawn — inside the
  walk's ~2500-tick expectation.
- **Loot: CONFIRMED.** After submerge, `get_cell_info` on the former cell showed
  a `MinifiedThing` labeled "Small vanometric power cell" plus
  `Filth_RubbleBuilding` — `Reward_ItemsStandard` fired as designed. Destroyed
  the minified item afterward; cell now empty.
- **VFX/art: CONFIRMED, not placeholder.** Two screenshots
  (`longhunger_eruption_check_01.png`, `longhunger_600ticks_check_01.png`, in
  the game's own Screenshots folder) show a real smoke-cloud eruption with a
  scorched crater, then a secondary fire/flame VFX from the blast igniting
  nearby plants — distinct, intentional-reading effects, not a missing-asset
  placeholder.
- **Quest offer/fire: CONFIRMED.** Fired via
  `Actions\Generate quest...\RUT_LongHungerContract\500 points`. Verified two
  ways: (1) a "Quest available: Deep-Sand Contract" letter appeared in the
  alert stack — "Deep-Sand Contract" is `Quest_LongHunger.xml`'s own
  `questNameRules` string (`questName->Deep-Sand Contract`), not a guess; (2)
  `Actions\View Quest Chains` (a debug window, screenshotted) confirmed no
  chain-quest system was confused by it. Quest left live in the campaign
  (harmless — it's an ordinary declinable quest offer with a normal
  `expireDaysRange`, same as anything the storyteller would generate; note
  it's a debug-fired one in case anyone wonders where a "Deep-Sand Contract"
  quest came from). **Not done**: actually accepting it and watching
  `RUT_LongHungerSurfaces` auto-fire — the quest→incident wiring is a standard
  `QuestNode_CreateIncidents` pattern and the incident's own mechanism is
  independently proven above, so this is judged covered rather than a genuine
  open risk; pick it up if a future session wants the literal end-to-end path.
- **Coexistence with the donor sandworm: CONFIRMED, with a real trap found.**
  Spawned `chezhou.creature.sandworm`'s actual thing (`SandWorm_Thing`, label
  "Sandworm", `className SandWormLib.SandWormThing`) via `rimworld/spawn_thing`
  — no def/texture collision, no load error, both mods' world-entities coexist
  fine. 🔴 **But it is NOT stationary**: over 600 explicitly-stepped ticks (game
  still `Paused` between calls — not unpaused) it moved ~60 tiles, from its
  spawn point to (115,129), a handful of tiles from the real colonists at
  (111-124,144). A `T: Destroy` debug action on it initially reported
  `success: true` while changing nothing — `effects.logs` carried
  `"[SandWorm] Ignored early non-lethal vanish destroy during spawn grace
  period."`, a real silent-failure case per `references/silent-failures.md`
  (worth filing there). Waited past the grace period and destroyed it for
  real; `jawa/list_things` confirmed gone, `list_colonists` confirmed all
  three colonists undamaged. **Lesson for next time this mod's creature is
  spawned near anything precious**: it self-relocates every tick even while
  the clock reads Paused (explicit `step_game_ticks` still runs its AI), and
  its own destroy-guard silently no-ops for some window after spawn — spawn it
  far away, expect it to travel, and re-issue Destroy if the first one logs
  the grace-period warning.

## closed
All 7 criteria confirmed by direct observation (screenshots + independent-tool
read-backs), not inferred from a clean deploy plan or an unread log.
