# CAVERNS_PARITY_BUILD_1

🔴 **Reconstructed 2026-09-20 — the item file was EMPTY/absent while the ledger
carried `state: doing`.** Rebuilt from `python3 src/RimMandrake/rimflow/cli.py why
CAVERNS_PARITY_BUILD_1`, `infrastructure/state/ledger/events.jsonl` (grep
`"id":"CAVERNS_PARITY_BUILD_1"`, ~30 events 2026-09-18T19:10Z →
2026-09-19T03:36Z), `design/Jawa/worldbuilding/biomes/caverns_replacement_scoping.md`,
and `git log`. This file states what IS, not a guess at what the title implies.

## spec (as filed, BENCH, 2026-09-18T19:10:54Z)

"Donor-free crystal Deeps: M-tier parity build on the Lantern Deeps route." Make
`RUT_LanternDeepGenerator`'s existing pocket-map + entrance-building route
donor-free — owning the biome/terrain/crystal-GenStep/flora it was borrowing from
`Biomes! Caverns` (BMT) — so that mod can be cut without losing the Deeps. Owner
ruled all six scoping questions the same sitting
(`design/Jawa/worldbuilding/biomes/caverns_replacement_scoping.md` §2 is the build
plan):

1. **Art**: regenerate to the crystal-caverns reference sheet's blue-on-black
   palette (owner: "Regenerate to the sheet" = the cosmetic-change permission).
2. **Collapse hazard**: DEFERRED to a future crystal-life program — no C# this build.
3. **Timing**: "Run it now" — dedicated build, not batched into the next load round.
4. **Precept**: replace `BMT_FungusEating_DontCare` with an owned RUT equivalent.
5. **Maguana**: port `BMT_Maguana` into the owned bestiary (MLIE absorption
   pattern) rather than let it vanish silently at the cut.
6. **Polluted Lands mutations**: DROP at that mod's own cut (not this build).

## verify

- `validate_patch.py` clean against the live mod set.
- Quicktest / full-list load with the donor (`Biomes! Caverns`) ABSENT from
  `ModsConfig.xml` shows the Deeps generating from owned defs only: 0 `BMT_`
  references, new defNames present, no crash.
- `caverns_replacement_scoping.md`'s own parity checks.

## criteria

`Biomes! Caverns` can be removed from the mod list with the Lantern Deeps still
generating, playable, and visually matching the reference sheet, with zero
donor defNames left in the owned mod's own files.

---

## status log — reconstructed from the ledger, 2026-09-18 → 2026-09-19

**This build is DONE and DEPLOYED, not merely "doing."** `state: doing` in the
ledger is itself stale — nobody ever ran `rimflow close`, but every concrete
piece of the spec above landed:

- **Donor-free at source.** BENCH note 2026-09-18T21:39Z (post shutdown-window
  deploy): *"Lantern Deeps consume zero Biomes! Caverns defs at source level."*
  `dotnet build` 0 warnings/0 errors, 25/25 XML parse, `validate_patch.py` clean.
- **Maguana ported** (2026-09-18T19:24Z): `RSW_Maguana`, donor stats byte-for-byte,
  Ashkarr retune baked into the owned def (replacing BMT-targeted patches),
  wired into the biome. Owner ruled it ships on donor art verbatim for now
  (speed over the crash-elimination goal); a real art pass is deferred to the
  Deeps' own review round.
- **Incident suppression built same sitting** (owner note 2026-09-18T19:33Z):
  `RUT_LanternDeepIncidentSuppression.xml` blocks the donor's incident list
  (Aurora/ColdSnap/Eclipse/Flashstorm/HeatWave/MeteoriteImpact/ToxicFallout/
  Volcanic...) from firing on the owned biome.
- **Wall atlases**: donor used as LAYOUT ONLY — owned blue-on-black art
  assembled into the donor atlas's cell grid, zero donor pixels ship
  (`validate_sprite` PASS both, `dbf6d8a9b`).
- **Ambient sound**: `RUT_DeepCalm` shipped silent (donor `.ogg` does not come
  with us) — filed and closed as `DEEPCALM_AMBIENT_SOUND_1` (owned cave-hum
  `SoundDef`).
- **Precept**: `BMT_FungusEating_DontCare` replaced with an owned RUT
  equivalent (ruling 4) — resolved (`RUT_FungusEating_DontCare` confirmed
  resolving with 0 dangling refs at Load B, 2026-09-18T22:13Z).
- **Entrance biomes → Mod Settings** (`DEEP_ENTRANCE_BIOMES_SETTING_1`, closed):
  default = the Utinni three (BiomeGRimond, RUT_NightsideIce, RUT_PropaneLake),
  any biome selectable.
- **Flora renamed with invented Star-Wars-style names** (`DEEP_FLORA_RENAME_1`,
  closed): Lantern Deeps and lanternstone keep their names; the dulcis mushroom
  and others got owned names.
- **Raw-dulcis dedup ruled and executed** (`DEEP_DULCIS_DEDUP_1`, closed):
  `RUT_DeepRawDulcis` dropped, harvest yields `RotSporeKit`'s `RUT_RawDulcis`
  instead; `mandrake.rut.rotsporekit` dependency added.
- **Art review DONE and approved** (owner note 2026-09-19T01:17Z): all 48 sheet
  rows kept on his word; `wire_art.py --apply` copied 47 PNGs (49 with the 2
  generated wall atlases) into `src/RimUtinni/LanternDeeps/Textures`.
- **Tint DONE and approved** (owner note 2026-09-19T01:27Z, looked at
  `Transient/deeps_tint/plants_before_after.png`, said "Approved."): organics
  +70° on the blue-cyan band, minerals unchanged, `b2119d69c`.
- **Deployed 2026-09-19T02:20Z**: LanternDeeps whole — 55 files (DLL with
  entrance-biome settings, renamed flora defs, 50 textures, sound, About).
- **`Biomes! Caverns` cut from the live mod list 2026-09-18T22:17Z** (owner
  note): `biomesteam.biomescaverns` removed from `ModsConfig.xml`,
  `mandrake.rut.lanterndeeps` inserted in its place in load order.
  `CAVERNS_LOADAFTER_STRIP_1` (closed) stripped the now-inert `loadAfter`
  lines from 12 other mods' `About.xml`.
- **Load C, 2026-09-19T02:53Z — the parity proof, MEASURED live via bridge on
  the 621-mod full list with the donor ABSENT**: 17/17 new defs present
  (biome, weather, 2 sounds, 11 flora, tendrils), 0/11 old (BMT_) names,
  `BMT_CrystalCaverns` absent. Log: 0 lines naming any LanternDeeps def,
  Harmony failures at baseline (1), no `CaveFungus` crash, no
  `Patch_PocketMapGrowthRate` error, no `entranceBiomes` Scribe error. The
  Deep generated on the full list from the canonical map: 489 lanternstone
  walls, 21 formations, 47 renamed flora present. **This is the criteria in
  the spec, satisfied and measured, not asserted.**

### What this build caused, still open (fallout from cutting the donor — adjacent
work, not part of this build's own criteria)

- `CUT_FALLOUT_GENERATED_DATA_1` (FOUNDRY, `doing`) — offline patch/generator
  residue from the Caverns + Polluted Lands cuts (BMT_ plant defNames in flora
  generator roster JSON, stale `BiomeFlora_Ashkarr.xml` patch actively
  clobbering already-fixed content). Per its own 2026-09-20 status entry, down
  to ONE open content call (port-or-cut 3 `RUT_TheForge` flora refs) blocking
  a clean `--write`; everything else is fixed or purged. **Not touched this
  pass** — it is FOUNDRY's, already claimed and mid-work, and the one blocking
  call is a design decision (temperature-tolerance mismatch), not a
  mechanical rename.
- `CANONICAL_SAVE_CUT_RESIDUE_1` (FOUNDRY, `proposed`, thin) — the canonical
  start save still references ~4,800 dead `BMT_`/other defNames from the cut
  mods; needs a scrub or re-save. Not touched this pass (not one of the four
  items in scope, FOUNDRY's to claim).
- `BIOME_CONFIGERRORS_NRE_1` — filed as a `CAVERNS_PARITY_BUILD_1`-caused
  defect (5 biomes NRE in `BiomeDef.ConfigErrors()`), **already closed**
  (`26fd2c9139`).

### Bottom line

Every piece of the owner's six-question spec is BUILT and DEPLOYED and the
donor-absent full-list load (Load C) proves parity. `state: doing` in the
ledger should read `done`; nobody closed it. **This subagent has not called
`rimflow close`** (closing/reclassifying is a judgement call the mission did
not ask this pass to make, and BENCH should look at the Load C evidence above
before closing) — flagging it here instead so whoever owns the ledger can
close it on this evidence.
