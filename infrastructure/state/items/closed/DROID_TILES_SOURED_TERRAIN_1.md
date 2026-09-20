# DROID_TILES_SOURED_TERRAIN_1 — Free Droid Enclave tiles get polluted ground and fouled water

Caused by `DROID_SYSTEM_BUILD_1` (closed). Unblocked 2026-09-20: its stated
prerequisite, the FDE goodwill layer, is `DROID_FDE_GOODWILL_CAP_1`, closed
2026-09-07/09.

## doctrine (found, not guessed)

The 2026-08-04 doctrine is `design/Jawa/worldbuilding/desert_world_design.md`
lines 644/646, the "android water-denial doctrine" (owner, verbatim, quoted
there): rogue/free droids don't drink, so water is free for them to destroy and
fatal for the player to lose. Ruled shape:

1. **They settle the ✗-water terrains on purpose** — the terrain itself is
   their moat (no fallback path needed here; this project's FDE settlement
   placement already did this — see below).
2. **They poison and pollute what water and ground they hold**: "a tile they
   occupy has its surface water fouled (drinking it inflicts toxic buildup /
   food poisoning rather than slaking Thirst) and its ground progressively
   polluted — which in RimWorld's terms means toxic terrain, spreading
   tox-fallout-like contamination, and no clean growing until it's cleaned."
3. **Route ruled explicitly**: *"pollution is a native Biotech mechanic
   (polluted terrain, toxic wastepacks, tox buildup), and since all DLC is
   assumed present we simply seed android tiles with polluted terrain + fouled
   water at authoring/RimBridge — no fallback path needed."*
4. **Cleansing resolved same day**: a captured android tile CAN be temporarily
   cleansed (Biotech's own pollution-pump/cleanup tools) — that's fine, the
   Empire pursuit is the real timer, not permanent poison.
5. **Guardrail**: environmental faction flavor only, never a player-usable
   water-poisoning tool.

`DROID_UNIFIED_FRAMEWORK_DESIGN.md` §3.2 names the faction this binds to:
**Free Droid Enclaves** (`RUT_Jawa_FreeDroidEnclaves`), "territory-only
hostility, after goodwill collapse" — C2 (kinds repoint) + C3 (goodwill cap,
closed) + this item.

## mechanism (MEASURED against decompiled engine source via RimSage, 2026-09-20)

A world tile's `pollution` field (0.0–1.0, one of the ten real per-tile scalars
`jawa/world_tile_get`/`world_tile_export` return) is the **entire** lever, and
it satisfies BOTH halves of the doctrine with no custom code:

- `GenStep_Pollution.Generate` (`Source/RimWorld/GenStep_Pollution.cs`) calls
  `PollutionUtility.PolluteMapToPercent(map, Find.WorldGrid[map.Tile].pollution)`
  at LOCAL MAP GENERATION time — the world tile's stored fraction becomes the
  fraction of the generated map's pollutable cells that spawn polluted.
- `PollutionGrid.EverPollutable` gates on `cell.GetTerrain(map).canBePolluted`,
  **not** on dry land — a water terrain with `canBePolluted=true` is polluted
  exactly like ground. `PollutionGrid.SetPolluted` calls
  `map.waterBodyTracker.Notify_PollutionChanged`, and
  `FishingUtility.PollutionToxfishChanceCurve.Evaluate(waterBody.PollutionPct)`
  is the live consumer — a polluted water body yields toxic fish instead of
  clean ones. **This is "fouled water" exactly as the doctrine names it, native
  and automatic** — no Water-Butt/Thirst hook was built or is needed for the
  doctrine's own ask.
- `TileMutatorDef Pollution_Increased` (`MayRequire="Biotech"`, label
  "increased pollution", worker `TileMutatorWorker_IncreasedPollution`) is a
  thin, non-load-bearing flavor layer: `OnAddedToTile` just nudges
  `tile.pollution` by +0.1..0.2 and clamps. Adding it gives the tile a visible
  in-game label/description; it changes nothing the raw field write doesn't
  already cover.

No fallback, no C#, no player-facing tool — matches ruling #3 exactly.

## what was found on the live frozen world (`jawa/world_objects_get faction=RUT_Jawa_FreeDroidEnclaves`)

7 FDE settlements, 7 tiles: `19350` (No Master), `21560` (Unbound Exception),
`21547` (The Free Charge), `5072` (Second Speaker) — all `RUT_RustCathedral`
biome, **already pollution 0.95–1.0** (that biome's own authoring already
satisfies the doctrine; untouched here) — and `8735` (The Cracking Station),
`9077` (Coldfire), `733` (Vent Nine) — all `RUT_Umbra` biome, **pollution
0.0, no Pollution-category mutator**. The doctrine was true for 4 of 7 FDE
tiles and false for 3.

## spec

Close the gap on the 3 non-compliant tiles only (`8735`, `9077`, `733`) —
leave the 4 already-compliant `RUT_RustCathedral` tiles untouched (no need to
re-author curated content that already satisfies the doctrine):

- `jawa/world_tile_set` — `pollution = 1.0` on tiles `8735,9077,733`.
- `jawa/world_mutators_set action=add def=Pollution_Increased` on the same 3
  tiles — declared marker, matches how the doctrine describes this as
  authored/placed content, not just a raw number. Checked for category
  conflict first: none of the 3 carry any other `Pollution`-category mutator
  (`Mountain`/`Caves` are different categories), so this cannot displace
  anything.
- `jawa/world_commit`.

## verify

```
PROVE   world_tile_get on 8735,9077,733 reads pollution == 1.0 (was 0.0)
        world_mutators_get on the same 3 shows Pollution_Increased present
        world_mutators_get on the untouched 4 RustCathedral tiles is BYTE-IDENTICAL
        to the pre-write read (no collateral displacement)
LIES    a `success: true` on world_tile_set/world_mutators_set alone — both are
        read back with a separate GET call before this closes
```

No live map-generation test is owed: these are NPC-faction settlement tiles
the player has not visited, so no `Map` object exists yet to observe polluted
terrain on directly. `GenStep_Pollution` is vanilla Biotech code, already
exercised on every other polluted tile in this save (the 4 RustCathedral FDE
tiles included) — the mechanism is not "never once observed running" project-
wide, only never observed on these specific 3 tiles, which is a live-play
observation for whoever next visits one, not a build-time blocker.

## criteria

- [x] Doctrine found and quoted, not guessed (§ above)
- [x] All 7 FDE settlement tiles enumerated and read live
- [ ] The 3 non-compliant tiles' `pollution` set to 1.0 and committed
- [ ] `Pollution_Increased` mutator added to the same 3 tiles and committed
- [ ] Read-back confirms both writes landed; the 4 already-compliant tiles are
      unchanged

## 2026-09-20 (FOUNDRY) — research + target tiles done; write NOT executed, game switched worlds mid-session

Bridge was FREE, taken, and the frozen Ash'karr save was live and read
successfully (`ticksGame: 126812`, `RUT_Jawa_FreeDroidEnclaves` with 7
settlements at tiles `19350/21560/21547/5072/8735/9077/733`, exactly as
recorded above). Immediately before the write call, the connection was
refused; `Player.log` showed a brand-new RimBridge boot sequence completing
at 08:16:25 that same morning (game PID freshly started ~08:16:05) — the
game process restarted **independently of this session**, cause unknown (not
triggered by any call this session made; every call up to that point was a
read).

Waited out the reload (~4 min, polled via `rimworld/get_ui_state` until
`Playing`). **The game that came back is not Ash'karr**: `jawa/world_stats`
reports a **119,904-tile, single-biome (`TemperateForest`) world, seed
`"strick"`, `ticksGame: 1`**, factions only `TradersGuild`/`PlayerColony` —
a freshly-generated throwaway/test world, not the frozen campaign save. No
`RUT_Jawa_*` faction exists in it at all. Tiles `8735`/`9077`/`733` on THIS
world read back as generic `TemperateForest`/pollution 0 — meaningless
coincidence, not the FDE tiles.

**Did not write anything.** Writing pollution/mutators onto this unrelated
world would do nothing for the doctrine and could stomp on whatever another
window is actually using it for. Released the bridge immediately
(`rimflow bridge release`) rather than holding it against someone else's
test. **Leaving this `doing`, not `blocked`** — there is no design ambiguity,
only a timing one: the frozen Ash'karr save needs to be the loaded game
again. All research, the exact mechanism, and the exact 3 target tiles are
final and above; the only remaining work is two bridge writes
(`world_tile_set pollution=1.0` + `world_mutators_set action=add
def=Pollution_Increased`, both on tiles `8735,9077,733`) plus
`world_commit` and a read-back, next time Ash'karr is the live game.
