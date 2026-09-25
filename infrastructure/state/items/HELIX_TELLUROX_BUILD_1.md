# HELIX_TELLUROX_BUILD_1 — Tellurox, Ascendant Helix labour-line livestock

Owner-approved design row from `FORSAKEN_CRAGS_FAUNA_1` (closed), with a
correction the owner made at ruling time (recorded verbatim in
`design/Jawa/worldbuilding/review/forsaken_crags_fauna_sheet.decisions.json`):
*"a livestock animal genetically modified by the Helix faction — origin and
biome follow Helix, not 'general'."* The design row's original "biome left
general" framing (FOUNDRY's own placeholder, written before the ruling) is
now WRONG and is superseded by this item.

Filed separately from `FORSAKEN_CRAGS_PREDATORS_BUILD_1` (Cindermare/Skarnix)
because Tellurox is a different shape entirely: Ascendant Helix engineered
livestock, not wild `AB_RockyCrags` fauna — different faction, different
biome, different mechanic, no shared batching value.

## Where "Helix" actually is (looked up, not guessed)

`design/Jawa/worldbuilding/FACTION_SPEC.md` §9 and
`design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md` §7a (settlement
table): the **Ascendant Helix** (`Jawa_AscendantHelix`) is the campaign's
genome-engineering faction — "a religion of engineered improvement" doctrine
(`faction_religions_spec.md` §9, "the Ascendant Genome"). Their world
presence is 7 settlements, RULED 2026-08-24 (owner): *"the Helix sits where
the BIOWEAPON is"* — `HorrorWastes`, the mycoid tiles (`AB_MycoticJungle`/
`BMT_FungalForest`), and the poison forests (`PoisonForest`) of the
terminator, plus one ocular-forest outpost (*Helix Landing*, Scald shore).

**Biome chosen for Tellurox: `HorrorWastes`** (nightside, −74.9…−33.9 °C,
468 tiles across `Deadstone`/`Umbra`/`Ammonia Flats`). Reasoning, not a
coin-flip: `HorrorWastes` was literally carved out of `AB_RockyCrags`
(`ASHKARR_WORLD_DEFINITION.md` §7a note, 2026-08-23 ruling) — the same
territory Cindermare and Skarnix live in, one biome-split away. That is
almost certainly why Tellurox's source art (`karrask_opt3.png`) got grouped
into the same mockup batch as the two Rocky Crags creatures in the first
place: it reads as crags-adjacent stock, now claimed and re-bred by the
Helix. Their two named `HorrorWastes` holdings (*Cold Stores*, *The
Revision*) are the plausible breeding/holding sites. If a future pass finds
a stronger owner-named pin (e.g. specifically `PoisonForest` or mycoid),
that overrides this — this is FOUNDRY's best-evidence read, not an owner
quote.

## spec

**Tellurox** (`karrask_opt3.png`) — Ascendant Helix labour-line livestock,
`HorrorWastes`. A draft/pack beast, genetically engineered by the Helix
(their "Ascendant Genome" doctrine — see `Alien_Bestiary.md`'s
vernacular/registry naming convention: give it a Helix registry name
alongside "Tellurox" the vernacular one, e.g. `Helix Model XX-N` shape,
per the doc's own pattern for Helix-touched organisms). Deliberately NOT
another molt-armor farm like karrask — its shell is permanent (grows with
the animal, never sheds), so first-rate plate only comes from slaughtering
a mature working animal, not a renewable shear cycle. The permanent-armor
trait now reads doubly intentional given the corrected biome: `HorrorWastes`
is bioweapon-adjacent hostile territory, so an unshedding shell is armor the
Helix bred FOR, not incidental flavor.

Tameable, tradeable, RimStarWars tier, sprite via `generating-rimworld-sprites`
contract (128 px/cell, chroma-key alpha, silhouette-first, matching
`karrask_opt3.png`), beast-normalization spirit.

Invented premises carried over (declared, not snuck in): the name, the
permanent-shell mechanic and its differentiation from karrask, and this
item's own registry-name/breeding-site reasoning above (flag as invented
if the owner wants a different Helix tie).

## verify

- Def compiles/loads clean, `validate_patch.py` 0 errors.
- Live quicktest: spawns as `HorrorWastes` fauna, tameable, produces a
  permanent (non-regrowing) shell/plate item only on slaughter of a mature
  animal — no shear/harvest job exists for it.
- Art matches `karrask_opt3.png`'s silhouette.

## criteria

Tellurox spawns on `HorrorWastes`, tameable and tradeable as Helix-sourced
livestock, permanent-shell-on-slaughter mechanic live-proven (not a
renewable harvest), art traced to the promoted mockup, Helix
origin/registry naming reflected in its def (not left as generic
livestock).

## 2026-09-02 (FOUNDRY) — offline build: defs done, art blocked, biome-cast wiring identified as its own step

**Built** (`src/RimStarWars/HelixTellurox/`, `mandrake.rsw.helixtellurox`):
`RSW_TelluroxRace` (ThingDef, `AnimalThingBase`), `RSW_Tellurox` (PawnKindDef),
`RSW_TelluroxShell` (StuffDef, `LeatherBase`) carrying the permanent-shell
mechanic as a `butcherProducts` bonus entry (6x `RSW_TelluroxShell` per
slaughter) — deliberately NOT a `CompHasGatherableBodyResource` shear job,
which is karrask's mechanism and the thing this item says not to copy.
`packAnimal`/`herdAnimal` true, `trainability: Intermediate`,
`ComfyTemperatureMin: -60` for HorrorWastes' −74.9…−33.9 °C. Registry name
invented (not owner-sourced, flag if he wants different): "Helix Model GT-4",
lore-only per `Alien_Bestiary.md`'s vernacular/registry convention — never
the in-game `<label>`.

**Art: BLOCKED on a real, named tool failure, not skipped.** Three attempts
via `codex_image.py edit` (anchored on `karrask_opt3.png`) — two hung past
the 120s timeout, the third returned the actual cause: `ERROR: Selected
model is at capacity. Please try a different model.` No `--model` override
exists in this project's `codex_image.py`. `validate_patch.py` confirms the
gap for real (not guessed): `RSW_Tellurox`'s own texPath has no file on
disk, "renders as pink placeholder." Two OTHER texPath errors on the same
run (`Leather_Plain`, `Muffalo/Dessicated_Muffalo`, both reused real vanilla
paths) are very likely the same asset-bundle blind spot this session's
`WEATHER_SUITE_SLICE_1` build already hit and documented (vanilla textures
packed in Unity asset bundles, invisible to a loose-file scanner) —
plausible, not independently re-confirmed this pass.

**Biome-cast wiring: NOT a quick patch, deliberately not attempted.**
`HorrorWastes`' `wildAnimals` list is this campaign's curated, algorithmically-
scored cast (`design/Jawa/fauna/cast_assignment.csv` → `gen_cast_patch.py` →
`BiomeCast_Ashkarr.xml`, GENERATED, do-not-hand-edit), scored on
`belong`/`standout`/`defence` against each biome's sprite palette
(`allocate_cast.py`, `biome_fit.py`, `sprite_features.csv`). Tellurox has no
census/sprite-features row (it's a brand-new creature, and its own sprite
doesn't exist yet per the block above), so it isn't a `refill_cast.py`
candidate either — that script only refills VACATED slots from the existing
candidate pool. `refill_cast.py`'s own header measures a full
`allocate_cast.py` re-run at **560 of 746 rows changed, 75% of the planet's
fauna** — re-running it to add one creature would be exactly the "re-
allocate a curated artifact" mistake this project's own doctrine warns
against. **Correct next step, once art exists**: a single hand-placed row in
`cast_assignment.csv` for `RSW_Tellurox` under `HorrorWastes`, diffed to a
temp path before touching the real file, never a full allocator re-run.

🔴 **`HorrorWastes` (the donor def from Horrors (Continued)) no longer holds any
painted world tiles** — its ~2,338 tiles were dissolved 2026-09-07 into
`RUT_NightsideIce`/`BiomeGRimond`/`AB_PropaneLakes`
(`design/Jawa/worldbuilding/horrorwastes_dissolve_execution.md`), whose own
"Cast re-homing" section already ruled the cast-roster successor as
`BiomeGRimond` (68% tile plurality + `the_blue_desert.md`'s "the Horrors' host"
framing) — which the 2026-09-07 world-switch then repainted to `RUT_BlueDesert`.
**UNMEASURED whether that's still the right target for THIS row**:
`cast_assignment.csv` currently has zero `RUT_BlueDesert` rows at all, so
hand-placing under `HorrorWastes` would silently orphan the row. Whoever
picks up biome-cast wiring: re-derive the live successor key before adding
the row, don't paste `HorrorWastes` in unchanged.

**Left `doing`** — none of `## criteria`'s bars are met yet (spawn, live
mechanic proof, art, biome wiring all still owed). `validate_patch.py`: 7
errors, all texPath-only (see above) — otherwise clean (0 structural
errors). Deployed file-copy only (`deploy_custom_mods.py --mod
HelixTellurox --apply`), not enabled in `ModsConfig.xml`, no restart
triggered.

## 2026-09-02 — sprite retry, 5 attempts, all failed: genuinely blocked, not skipped

Ran the full retry budget (`skills/generating-images/scripts/codex_image.py
generate`, `#00ff00` chroma-key, 120s cap per the `generating-rimworld-sprites`
skill's own guidance): attempt 1 timed out (`codex exec exceeded 120s`),
attempt 2 failed fast with `ERROR: Selected model is at capacity. Please try a
different model.` (plus a `windows sandbox: helper_unknown_error` on the same
run), attempts 3-5 all timed out identically. No image was ever produced —
`ls` on the output directory after all 5 attempts is empty. This matches the
prior pass's finding exactly; the blocker is real, reproducible, and not a
one-off. `codex_image.py` has no `--model` override to route around a
capacity-limited model. **Not retrying further this pass** — the skill's own
guidance is spaced retries, not an unbounded loop, and 5 is past that budget.

Applied one real, independently-useful fix while investigating: none of the
three `lifeStages/li/bodyGraphicData` blocks declared
`<graphicClass>Graphic_Single</graphicClass>` (the pattern the sibling
Cindermare/Skarnix build uses for the same single-facing-art scope) — without
it, RimWorld defaults an animal's body graphic to `Graphic_Multi`, which
expects `_north`/`_south`/_east`/`_west` files and would silently fall back to
drawing an unsuffixed base-path file for every direction if one ever landed
without the four variants (the `generating-rimworld-sprites` skill's own
documented "bare-path fallback" trap). Added `Graphic_Single` to all three
life-stage entries now, before art exists, so the eventual single sprite
actually renders correctly the first time rather than needing a second pass.
`validate_patch.py` re-run after the fix: same 7 texPath-only errors as
before (no new/different errors — the graphicClass edit is structurally
inert until a texture exists), confirming the fix didn't regress anything.

Biome-cast CSV still untouched, correctly — no art to reference. This item's
art blocker is now the single remaining offline-addressable gap; everything
else offline (defs, mechanism, validation) is done and correct.

## 2026-09-05/06 (FOUNDRY) — art unblocked without codex_image.py; biome-cast CSV still correctly untouched

**Art blocker resolved by a different route, not a repeat of the dead end.**
Before touching anything, re-read the two prior sprite-gen commits
(`c325d982`, and the 5-attempt retry noted above) — both routed through
`codex_image.py`'s cloud generate/edit call, which hit "model at capacity"
and hangs past its 120s cap. This pass never calls `codex_image.py` at all:
`karrask_opt3.png` is *already* a clean, chroma-keyed (`#00ff00`, auto-detected)
side-view render with a real subject silhouette — 38% coverage, 0% fringe.
Per the item's own `## verify` bar ("Art matches `karrask_opt3.png`'s
silhouette") and `## criteria` ("art traced to the promoted mockup"), tracing
the promoted mockup IS the spec, not a stopgap — the mechanical differentiation
from karrask (permanent shell, no shear job) already lives entirely in the defs
built 2026-09-02, so the art itself needing no separate edit is consistent with
the item's own bar, not a shortcut around it.

Pipeline used (`skills/generating-images/scripts/chroma_key.py` +
`skills/generating-rimworld-sprites/scripts/validate_sprite.py --describe`,
per `generating-rimworld-sprites/SKILL.md`):
1. `chroma_key.py` on `karrask_opt3.png` → clean cut, 1453x768 subject,
   0% fringe, corners `[0,0,0,0]`.
2. Measured the sibling convention rather than guessing a canvas: Karrask's
   own shipped `Karrask.png` (same mockup batch, drawSize 1.5) is 256x256 with
   its subject at 88% width / bottom-anchored ~5% margin; Cindermare.png
   (drawSize 2.6, the SAME adult drawSize Tellurox uses) is 512x512 with the
   same ~88%-width / ~3.5%-bottom-margin layout. Tellurox's adult `drawSize`
   is 2.6 → `2.6 × 128 = 332.8` → round up to **512**, matching Cindermare's
   own precedent exactly (not a coincidence — same batch, same convention).
3. Cropped-to-bbox, scaled to 88% canvas width, bottom-anchored at ~3.5%
   margin, centered horizontally (small script, not `conform_sprite.py` —
   that tool registers a candidate against an EXISTING same-creature
   reference by mask overlap, which does not apply to a first-ever sprite).
   Result: 451x238 subject on a 512x512 canvas, alpha mix 77.65% clear /
   0.32% fringe / 20.55% solid — matches Cindermare's own numbers
   (77.00%/0.18%/21.74%) closely enough to call it the same quality bar.
4. Deployed to `src/RimStarWars/HelixTellurox/Textures/Things/Pawn/Animal/
   Tellurox/Tellurox.png` and via `deploy_custom_mods.py --mod HelixTellurox
   --apply` (file-copy only, mod still disabled in `ModsConfig.xml`, no
   restart triggered).

**`validate_patch.py` re-run: RSW_Tellurox's own texPath now resolves clean —
0 errors on that file.** The remaining 4 ERRORs (`RSW_TelluroxShell`'s
`Leather_Plain`, and 3x `Dessicated_Muffalo` in the PawnKindDef's lifeStages)
are a validator false-positive, confirmed by precedent rather than assumed:
the SIBLING `Livestock` mod (already-shipped, same directory tree) throws
the **identical** error shape on `RSW_KarraskShedRaw`/`RSW_KarraskPlate`'s
own reused-vanilla `Things/Item/Resource/Leather` texPath — 2 errors, 0
elsewhere, `validate_patch.py` source at line ~2068-2074 explains why:
once a mod ships ANY loose texture under a top-level folder name (here
`things`), the validator treats that ENTIRE top-level namespace as
self-supplied and stops treating a miss as an unmeasurable vanilla-bundle
gap — it starts calling it a hard error instead, even for paths that are
correctly reused vanilla art. Since Karrask ships in production today with
this exact same false-positive standing, HelixTellurox's 4 remaining errors
are the same known class, not a real defect. Both intentional vanilla reuses
(`Leather_Plain` for the shell's own leather-family stuff, `Dessicated_
Muffalo` for the standard animal-corpse fallback) are real, correctly-spelled
vanilla paths — checked against a working def (Karrask's identical pattern),
per this project's own "never guess a texPath" rule.

**Biome-cast CSV: still correctly untouched, for a DIFFERENT reason than
2026-09-02's note (art no longer the blocker).** Went looking for the
`sprite_features.csv` row Tellurox would need to enter `allocate_cast.py`'s
`belong`/`standout`/`defence` scoring — confirmed (again) it has none, and
this time also confirmed **no generator script for that CSV exists anywhere
in this repo** (`grep -rl sprite_features design/ src/` finds only
`biome_fit.py`, which *reads* it, and two `gen_creature_*_sheet.py` files
that also only read it — nothing that writes it). Whatever produced the
existing ~1,260 rows' `px/w/h/fill/spiky/symmetry/hue/hue_conc/sat/val/
contrast/hist` columns is not present offline, and guessing those numbers
by a different, ad hoc method than whatever built the other 1,260 rows would
put an inconsistent measurement into a curated, cross-compared artifact —
worse than leaving the row absent. **Still explicitly owed**, and now the
correctly-scoped blocker is "the sprite-feature extraction method used to
build the rest of the corpus is not available offline," not "no art exists."
When that tool is available (or the owner names one), the item's prior
guidance stands: one hand-placed row, diffed to a temp path first, never a
full `allocate_cast.py` re-run (560/746 rows, 75% of the planet's fauna,
measured).

**Live check still owed in full** — nothing in this pass touched the bridge
or the live game. Exact live verify, superseding the item's `## verify`
block with the concrete steps:

```
PROVE   enable mandrake.rsw.helixtellurox in a MINIMAL-list relaunch (bridge-holding
        session's call, not this one) alongside the already-fixed butcherProducts
        form (HELIX_TELLUROX_SHELL_LOAD_CRASH_1's decision strings: no Core-only
        fallback, no unresolved cross-ref naming "RSW_TelluroxShell6")
EXPECT  RSW_Tellurox spawns via dev-spawn or a quicktest colony, renders the new
        Tellurox.png (not pink, not a Muffalo silhouette from the bare-path-fallback
        trap), tameable, and butchering a mature adult yields exactly 6x
        RSW_TelluroxShell (butcherProducts value) with NO shear/gather job ever
        offered on it
LIES    a mis-deployed or wrong-cased Tellurox.png falls back to drawing the base
        (unsuffixed) path fine for Graphic_Single, so "it rendered" is not itself
        proof the FILE I built is what's showing — diff the in-game screenshot
        against `src/RimStarWars/HelixTellurox/Textures/Things/Pawn/Animal/
        Tellurox/Tellurox.png` pixel-for-pixel, not just "an animal appeared"
```

Also still owed once the live check passes: `HELIX_TELLUROX_SHELL_LOAD_CRASH_1`
itself closes on the same relaunch (its own criteria: no Core-only fallback,
no `RSW_TelluroxShell6` cross-ref, butcher yields 6 plates) — the fix is
already deployed (commit `3468e2a0`), only the confirming relaunch is missing.

**Left `doing`** — `## criteria`'s spawn/live-mechanic/biome-wiring bars are
still unmet (bridge-only work). Art and def-side criteria are now met offline:
art traced to the promoted mockup (unaltered, not edited — the correct
reading of "traced"), Helix origin/registry naming in the def (unchanged from
2026-09-02). `validate_patch.py`: 0 errors on the mod's own new-art texPath,
4 errors remaining are the confirmed false-positive class shared with the
already-shipped Karrask sibling.

## 2026-09-09 (FOUNDRY) — offline re-verification only, no rebuild; folder moved under a merge this item didn't cause

Re-read this file plus the git history before touching anything (per this
pass's own instructions — several other items tonight turned out further
along than their last entry suggested). Found the standalone
`src/RimStarWars/HelixTellurox/` mod folder is gone: commit `247cd6d4`
("Sprint wave A ... fauna → SWBestiary") absorbed it, unchanged, into
`src/RimStarWars/SWBestiary/Defs/HelixTellurox/ThingDefs_Races/Races_Tellurox.xml`
and `Textures/Things/Pawn/Animal/Tellurox/Tellurox.png` under
`mandrake.rsw.swbestiary`. `SWBestiary/About/About.xml` already documents the
absorption verbatim ("Absorbed HelixTellurox ... the Tellurox draft/pack
beast def and texture; not yet wired into any biome's wild-spawn cast") —
this item's own outstanding gap carried over correctly, nothing lost in the
merge. `mandrake.rsw.swbestiary` is active in the live `ModsConfig.xml`
(confirmed by reading it directly, not assumed).

Did not attempt any live bridge call this pass — RimWorld was mid-cold-load
on the full ~600-mod list at the time (`rimflow bridge who` read FREE, but a
mid-load game is not a safe target regardless of bridge-lock state, and this
item's own verify plan calls for a MINIMAL-list relaunch, which a full-list
load in progress is not). All work this pass was offline re-verification:

- `validate_patch.py` re-run against the whole (now-merged) `SWBestiary` mod,
  `--defs` pointed at the real installed Data/Mods/Workshop roots (not the
  def dump — `--defs` scans mods on disk, `--live`/`--defnames` is the dump
  flag, and no dump path exists in this repo right now to hand it). Result
  unchanged from the 2026-09-05/06 entry: **0 structural errors**, exactly 4
  texPath ERRORs on `Races_Tellurox.xml`, all on reused-vanilla paths
  (`RSW_TelluroxShell`'s `Leather_Plain`, `RSW_Tellurox`'s 3x
  `Dessicated_Muffalo` corpse fallback). Independently re-confirmed the
  false-positive class this time, not just trusted the prior log: the
  *same* mod file throws the identical error shape on `RSW_KarraskShedRaw`/
  `RSW_KarraskPlate` (`Leather` reuse, 2 errors) and on two unrelated
  creatures merged into the same mod, `RSW_Protovermes`
  (`Dessicated_Boomrat`, 3 errors) and `RSW_Jerba` (`Dessicated_Dromedary`,
  3 errors) — all already-shipped, all the same "own top-level texture
  namespace makes a vanilla-reuse miss read as a hard error" class
  documented in `validate_patch.py`. Tellurox's own new-art texPath
  (`Things/Pawn/Animal/Tellurox/Tellurox`) throws nothing.
- Sprite re-measured with `validate_sprite.py --describe` directly (not
  taken on faith): `Tellurox.png` is 512x512, real alpha, clean chroma-key
  corners `[0,0,0,0]`, alpha mix 77.65% clear / 0.32% fringe / 20.55% solid —
  re-confirms the 2026-09-05/06 entry's own numbers against the shipped
  `Cindermare.png` sibling (77.00%/0.18%/21.74%), same convention, same
  quality bar.
- Also ran `validate_sprite.py --reference karrask_opt3.png --candidate
  Tellurox.png --strict`: it REJECTs (canvas 512² vs 1536x1024, subject
  -71%/-77% span, aspect squashed). **This is the tool applied outside its
  contract, not a real defect** — per `generating-rimworld-sprites/SKILL.md`,
  `--reference`/`--candidate` conformance checks a same-subject variant
  against its own canvas (a damaged version of one sprite), not a
  first-of-kind sprite deliberately re-scaled off a raw, un-keyed mockup
  into an unrelated sibling's canvas convention — which is exactly what the
  2026-09-05/06 pass did and documented. Recording the REJECT here so a
  future pass doesn't re-run this exact invocation and mistake it for a
  regression.

**No design/stat decision was open to fill, so nothing was invented.**
Everything still owed on this item (spawn proof, permanent-shell butcher
proof, `HorrorWastes` wild-spawn cast row) requires the live bridge on a
minimal mod list per the verify block above — genuinely blocked tonight, not
skipped. **Left `doing`.**

## 2026-09-12 (FOUNDRY) — live spawn + corpse-gen proof DONE on the canonical save; HorrorWastes wiring confirmed NOT done, re-blocked

Owner AFK, autonomous pass. Canonical campaign save was already loaded and
stable (bridge `get_game_info`: `game_loaded`, 1 map, 4 colonists visible,
paused throughout) — used it directly rather than a fresh quicktest, per this
pass's own briefing (avoids `QUICKTEST_POSTSETUP_CRASH_1`, owned by another
agent, unrelated to this item).

**Spawn — live-proven, independently verified (not trusted on `success:
true`).** `Actions\Spawn Pawn...\RSW_Tellurox` (`ToolMap`, x=130 z=130, an
open field cell outside the home area, away from the 4 colonists) returned
`success:true`; **independently confirmed** via `get_cell_info` (cell now
held `RSW_TelluroxRace`, class `Verse.Pawn`) and `jawa/list_pawns`
(`RSW_TelluroxRace632209`... `632207`, kindDef `RSW_Tellurox`, faction null,
hostile false, bodySize 2.6). Screenshot after `jump_camera_to_cell` +
`set_camera_zoom` + `jawa/clear_ui` shows a real, distinct armored-plate
quadruped sprite — not pink, not a Muffalo-shaped bare-path fallback.
Confirms `mandrake.rsw.swbestiary`'s `RSW_Tellurox`/`RSW_TelluroxRace` load
clean in the live, active mod list (already-active per 2026-09-09's read of
`ModsConfig.xml`).

**Corpse-gen / butcher-yield resolution — live-proven for the crash class,
not for the exact 6x count.** Killed the spawned animal via `jawa/damage`
(thingId `RSW_TelluroxRace632207`, 2 applications, `dead:true`,
`destroyed:true`) — this directly exercises the code path
`HELIX_TELLUROX_SHELL_LOAD_CRASH_1`'s own comment names (`butcherProducts`
`<li>` cross-ref bug -> corpse-gen NRE): the corpse (`Corpse_RSW_
TelluroxRace`) spawned cleanly at the death cell with **zero errors** in
`jawa/drain_log` (`errorsOnly`) attributable to Tellurox — only pre-existing,
unrelated Alien Worlds Framework biome-config warnings. Re-read
`Races_Tellurox.xml`: `butcherProducts` is the correct
`<RSW_TelluroxShell>6</RSW_TelluroxShell>` element form (the fix already
deployed, commit `3468e2a0`, now re-confirmed live-clean via this kill).
**Did not force an actual colonist butcher-bill job** (no documented bridge
primitive exists to add/force a bill without a colonist path + real tick
advance; the two closest tools, `jawa/order_pawn`'s GOTO and the debug
`Actions\Spawn Pawn...`/`T: Damage To Death` tree, don't reach "butcher this
corpse now" — `T: Damage To Death` is `ToolMapForPawns`, player-colonists-
only, and no `utcher` debug-action leaf exists under `Actions`) — judged the
canonical-save-disruption risk of unpausing + hauling + job-scheduling not
worth it for the marginal proof over what the corpse-gen test above already
gives. `jawa/get_def` cannot read `butcherProducts` itself (list field, not a
reflected scalar) so the exact "6" could not be re-confirmed as a *live*
number this pass beyond the source XML + the clean corpse-gen.

**Cleanup:** killed animal, corpse, blood filth and spawn-effect motes at
(130,130) removed via `jawa/destroy_batch` (rect `129,129,3,3`, category
`All`). Collateral: this also swept 4 nearby wild decorative plants
(`GRimClivia` x2, `RG_Plant_AridGrass` x2) in the same 3x3 — trivial, remote
open-field ground cover, not colony infrastructure, will regrow; noted rather
than hidden. Cell (130,130) now `thingCount: 0`. Canonical save left running,
paused, untouched otherwise — no save-over performed, no time advanced
(`ticksGame` never read as moved; no `set_time_speed`/unpause call made this
pass).

**HorrorWastes wild-spawn wiring — re-confirmed NOT done, more precisely than
2026-09-09's entry.** `grep -c HorrorWastes design/Jawa/fauna/
cast_assignment.csv` = **0**: `HorrorWastes` has **no rows at all** in the
cast CSV, not merely a missing Tellurox row in an existing pyramid. It is one
of the biomes `gen_cast_patch.py`'s own coverage check (`_missing`) flags as
keeping "whatever their mod ships" — i.e. today it wild-spawns entirely on
some donor mod's default roster, with no Ash'karr-authored ecosystem at all.
`gen_cast_patch.py`'s header names the fix for a fully-missing biome:
`refill_cast.py`, which the 2026-09-02 entry already ruled out for Tellurox
specifically (no `sprite_features.csv` row, no extraction method available
offline to make one honestly).

A single hand-placed `cast_assignment.csv` row for `RSW_Tellurox` under
`HorrorWastes` (bypassing the scorer entirely, per the 2026-09-02 entry's own
suggested route) is now MECHANICALLY possible — nothing blocks the CSV edit
itself — but making Tellurox the *entire* wild-spawn cast of a previously
un-cast biome is a content decision this pass declined to make solo: the
owner's own brief for this pipeline (`gen_cast_patch.py` header, 2026-08-22)
is "many small, some medium, a few large, ONE super-huge rare per biome" —
one hand-invented row cannot honestly fill that pyramid, and HorrorWastes
being cast at all, with what else, is exactly the kind of whole-biome
ecosystem call this project's doctrine routes through the owner/BENCH
design loop (`biome_sheets are a conversation loop`), not an overnight
FOUNDRY improvisation.

**Verdict: criteria not met, re-blocked.** Spawn + corpse-gen/crash-class
proof are now live-confirmed and can stand as done; the wild-spawn wiring
bar in `## criteria` is not met and was not attempted beyond confirming its
exact scope. `rimflow block` reason names precisely this: HorrorWastes has
zero cast rows and populating it is a content decision, not a mechanical
gap.

## 2026-09-25 (FOUNDRY) — re-verified offline, still correctly blocked; the open question got HARDER, not easier

Bridge held by another FOUNDRY window (full-modlist restart + a 5-item
live-verify batch, idle at claim time) — correctly did not take it or wait on
it, per this pass's own briefing. All work this pass is offline
re-verification plus one new fact that changes the shape of the remaining
decision.

**Nothing regressed.** `mandrake.rsw.swbestiary` still active (`ModsConfig.xml`
parsed directly: 627 active mods total, flag present). `Races_Tellurox.xml`
unchanged since 2026-09-09: `Wildness 0.3`, `butcherProducts` correct
element-form (`<RSW_TelluroxShell>6</RSW_TelluroxShell>`), `Graphic_Single` on
all 3 lifeStages, `Tellurox.png` still deployed. `HELIX_TELLUROX_SHELL_LOAD_CRASH_1`
re-confirmed **closed** (`4c7cec49...`, `rimflow show`) — no outstanding action
there.

**`validate_patch.py` re-run with a FULLER defs root than any prior pass used**
(`--defs Data --defs Mods --defs steamapps/workshop/content/294100` — the
Workshop content root, which prior passes never pointed at, hence their
"502 mods have no folder" / partial-visibility runs): **load set now 627 of
627 active mods found on disk, 8,862 def files.** Result: **0 ERRORs, 4
WARNs** — the same 4 reused-vanilla-path findings (`Leather_Plain`,
3x `Dessicated_Muffalo`) demoted from the ERROR class every prior pass logged
to WARN now that the tool can see the full mod set. Independent
re-confirmation of the false-positive call, not just a repeat of the old log.

**The HorrorWastes/BlueDesert cast question — re-checked, and now a
bigger ask than it was in September.** `cast_assignment.csv`: still 0 rows
for `HorrorWastes`, still 0 rows for `RUT_BlueDesert` (unchanged from
2026-09-12) — **and now also 0 rows for `RM_BlueDesert`**, which answers a
question the 2026-09-12 entry hadn't checked: `RUT_BlueDesert`'s actual wild
roster (`RM_Vekkit` 0.8, `RM_Dorrak` 0.5, `RM_Krissek` 0.35 — read directly
from `BLUEDESERT_RM_MOD_BUILD_1.md`'s own MEASURED section, which itself read
`RUT_BlueDesert.xml`) was authored by **hand-editing the BiomeDef XML
directly**, not through the `cast_assignment.csv` → `allocate_cast.py`
pipeline at all. That work closed as `BLUE_DESERT_LIFE_AUTHORING_1`,
2026-09-21, `4299f9262` — 9 days before this pass, and after this item's own
last entry.

That closure changes what "add Tellurox to this biome" now means. On
2026-09-12 the ask was "populate an empty biome's cast," which this item
correctly declined to improvise solo. Today the ask is **"add a 4th species to
an already-authored, already-CLOSED, owner-ruled biome sitting"** —
`BLUEDESERT_RM_MOD_BUILD_1.md` §9 explicitly lists this item's own
cross-reference and rules only that it "does not block" the mod-split work,
taking no position on whether Tellurox belongs in that roster. Modifying a
closed sitting's roster is the harder case, not the easier one: it is exactly
the shape the owner stopped doctrine-driven eviction/addition sweeps over
(`BIOME_SPECIFIC_FAUNA_LAW_1` — "I don't think we should be having rules
here. This is a human review process issue," "biome sheets are a conversation
loop, one biome at a time with him"). There is also a live question this pass
did not resolve either way: Tellurox is Helix-**engineered livestock**
(`Wildness 0.3`, same order as Muffalo), not a wild-evolved species like its
three BlueDesert neighbours — whether it belongs on a `<wildAnimals>` roster
at all, versus being Helix-settlement/trade-only stock with no wild spawn, is
itself an unasked design question, not something to default either way.

**Left `doing (BLOCKED)`, same reason class as 2026-09-12, now sharper: the
remaining gap is a human review-sheet decision on an already-closed roster,
not a mechanical CSV edit and not FOUNDRY's to invent.** Everything else the
item's `## criteria` can measure offline (defs, mechanism, art, validator)
remains done and re-confirmed clean this pass.
