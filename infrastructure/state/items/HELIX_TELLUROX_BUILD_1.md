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
Helix. Their two named `HorrorWastes` holdings (*Cold Archive*, *The
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
