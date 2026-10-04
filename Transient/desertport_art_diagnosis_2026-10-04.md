# Desertport art diagnosis (2026-10-04) — ART_VERSION_WRANGLING_1

Owner, on `Transient/desert_art_review_2026-10-03.html`: renders "appear older", "uninformed by much of
our biome work", canon creatures "uninformed by the canon library", "cartoonish", "different faces being
different creatures", and "crude skeletons were shown as the prior art". **He is right on every count, and
each has a measurable cause.** Nothing here was changed; this is diagnosis only.


## 1. Provenance of the jobs — MEASURED from `D:\Luke\dev\_artpipe\done\`

"218 desertport" is 109 job JSONs + 109 manifests. The sheet actually draws on **all 269 jobs** stamped
`rimflow_item_id = DESERT_FAMILY_PORT_EXECUTION_1`: 109 `desertportb_*`, 102 `desert_swaca_*`,
55 `RSW_*` (renamed Alpha-Animals ports), 3 `rut_*`.

| field | value across all 269 |
|---|---|
| created | **2026-09-20** (254), 2026-09-21 (6), 2026-09-27 (9) — i.e. two weeks old |
| filler | `fill_queue.py`, by the FOUNDRY port pass (`Transient\desert_port_swac_b_20260920.md` §"art jobs filed": 94 jobs, "Prompts built from each species' real donor description text, painterly-vanilla-RimWorld style boilerplate, no `reference=` set") |
| `reference` | **none on any job** (0/269) — so the validator was skipped ("no reference ... not a pass") |
| `style_notes` | **empty on every desertportb/swaca job** — no biome register, no palette, no anatomy notes |
| `derive_from` | **0/269** — every facing generated independently |
| channel / mode | `codex` built-in imagegen, `generate` (same channel as recent good jobs; the model is not the difference) |
| canon brief | not used. 22 of the ~99 subjects have a `design\RimStarWars\canon_references\<name>\description.md` with a `## Visual brief` and reference images (bantha, krayt dragon, greater krayt, bolotaur, ronto, eopie, porg, vulptex, zeer, ...). No prompt quotes any of them. The bantha brief (dated 2026-09-15, five days before the job) lists dark-brown-to-black fur and ivory horns, and three images; the job prompt is the Wookieepedia lead sentence. |

Prompt shape, verbatim pattern:
- `desertportb_*`: `"RimWorld creature sprite, painterly vanilla-RimWorld animal art style: the Star Wars canon <x> -- <donor/Wookieepedia description, cut at ~200 chars with an ellipsis>... Single creature, centered ... Heavy, clean black outline ..."`. **75 of 109 prompts are truncated mid-sentence** (contain an ellipsis), e.g. bolotaur ends "...which resulted in...".
- `desert_swaca_*`: `"A bantha (Bantha), a Star Wars canon creature. <wiki lead>. RimWorld top-down pawn sprite, desert-world creature, painterly game-art style matching the existing RimWorld/Star Wars mod roster ..."`
- `RSW_*` Alpha-Animals ports: one-line agent paraphrases ending "Star Wars creature design, desert palette, painterly style".

**What the art he liked looks like** (`Transient\longshade_fills_art.decisions.json`, ruled 2026-10-02: tazzok,
skarrok, vrekka, pavecrust, sippra, maidenbloom kept; jobs `RM_Tazzok_b_*`, `RM_Vrekka_*`, created 2026-10-02):
- `style_notes` of ~1,500 chars: the **biome's light and palette register** (golden-hour ochre/violet
  split for the Long Shade), **"realistic painted natural-history illustration, grounded believable
  anatomy, matte surface texture, never cartoonish, never cute, no outlines"**, a per-subject palette
  anchor, size/drawSize, behaviour, and an explicit true-rear-view north instruction.
- Prompt written from the **biome design doc's creature entry**, not a donor blurb.
- `derive_from`: north/south are `edit` jobs off the accepted east master (manifest mode `edit`,
  `derive_from_distance` recorded).

So the difference is entirely **job authoring + facing process**, not model or daemon: desert jobs are
generic donor-blurb prompts with a heavy-outline cartoon clause and no context; the liked jobs carry the
biome register, an explicit anti-cartoon/no-outline direction, and a shared master across facings.


## 2. "Different faces being different creatures" — facing incoherence, not row mis-pairing

**Row pairing checked, and it holds.** Of 98 rows with renders, every non-name-matched pairing (13
`inferred` rows + 13 Alpha-Animals rows renamed through the `Alpha Animals AA_X -> RSW_Y` def comments)
was read against its job prompt: Boulder Mit -> crab with a boulder shell (`RSW_Korrum`), Fuelmite ->
beetle (`RSW_Cindermite`), Sand Squid -> shelled cephalopod (`RSW_Sandmaw`), CrimsonCushion -> crimson
mat (`RSW_EmberCarpet`), etc. No row shows another creature's render. (One soft mismatch: the Terrorworm's
`RSW_Ashworm` prompt asks for "unthreatening in posture".)

**The real cause is the facings.** All 269 jobs predate `07676bd1d` (2026-09-27,
`ARTPIPE_FACING_COHERENCE_1` S2: north/south derive from the accepted east master; `fill_queue
--derive-facings` default ON). With `derive_from` unset, south, east and north were three unrelated
text-to-image draws, and the sheet put them side by side. A four-creature contact sheet
(bantha / krayt dragon / varactyl / bolotaur x S/E/N) shows it:
- **Varactyl**: south is a blue-and-green feathered biped; east and north are a red-and-cream raptor.
  These are two different animals.
- **Krayt dragon**: south is a squat horned toad-brute with a gaping mouth; east is a lean spiny
  lizard. Neither matches the canon krayt (huge, long-necked, horned).
- Bantha and bolotaur hold together better, because the prompt nailed one distinctive silhouette.


## 3. Why the current-art column showed skeletons — MEASURED, builder bug

The owner was right: the "current" column mostly showed **desiccated-corpse textures** — the
skeleton graphic RimWorld draws for a rotted carcass — not the live animal.

- Builder: `D:\Luke\dev\RimMandrake\Transient\desert_art_review_build_2026-10-03.py` (committed `078b778af`).
- Lines 84-88 collect **every** `<texPath>` under a PawnKindDef (`pk.iter('texPath')`) into one
  list per race, in document order. A lifeStage carries `bodyGraphicData` **then**
  `dessicatedBodyGraphicData`, so the last texPath is the corpse.
- Lines 170-171 then try `for tp in reversed(tps)` — **last first** — and stop at the first
  that resolves. The desiccated PNG always exists, so it always wins.
- The filesystem fallback (`_fs_fallback`, line 119) DOES exclude `'dess'`; the primary
  `resolve_texture` path does not. Only the fallback was guarded.
- Measured from the sheet's own ITEMS payload: **65 of 109 rows** show a `*_Dessicated` /
  `Dessicated_*` texture as "current" (64 `ours: swanimals/<X>/<X>_Dessicated`, plus
  `A_Rat` -> vanilla `Dessicated_Rat`; `P_AB_DessertTree` matched "dess" by spelling only and is
  a real plant). That is every ported `swanimals/` creature row with a resolvable current.
  Examples: A_Bantha, A_KraytDragon, A_Varactyl, A_Uvak, A_RSW_Jellypot (-> vanilla
  `Dessicated_Spelopede`), A_RSW_ImperialToad (-> `Dessicated_GoetoToad`).
- 17 rows had no current resolved at all (Terrorworm, 9 plants, 6 OuterRim droids, 1 other).
- So the "prior art" comparison was invalid for ~60% of the sheet. The owner's 4 "keep-current"
  and his doubts about the comparisons were made against corpses.


## 4. Stale template? — partly. The daemon template is current; the jobs predate two process fixes

- `build_job_prompt` in `D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\artpipe\artpiped.py` is
  applied at render time, so it is not frozen into the job. Its "painterly" branch skips the generic
  readability block because those prompts carry their own "Heavy, clean black outline" clause
  (`139c4342e`, ART_PAINTERLY_RESTORATION_1, 2026-09-14). That clause is part of the restored wave-4/5
  painterly family. It is also the most likely source of the **cartoon look**: the liked 2026-10-02 jobs
  say the opposite ("no outlines ... never cartoonish"). Across all done jobs the outline clause is in
  most prompts through 09-27, drops to ~0 on 09-28..10-02 (the period of the art he likes), and comes
  back on 10-03 (187 of 285), so new jobs are being filed with it again.
- **Stale at queue time:** `fill_queue --derive-facings` (09-27) did not exist when these were filed.
  Neither the 09-20 queue nor today's pipeline injects canon-library briefs, reference images or biome
  registers automatically. Those only exist when a job author writes them in, as the Long Shade agent
  did by hand.


## Root causes ranked

1. **Sheet bug: the "current" column showed corpses.** 65/109 rows rendered `*_Dessicated` (builder
   `reversed(texPaths)` picks `dessicatedBodyGraphicData`). The comparison he was asked to make was invalid.
2. **No coherent facings.** 0/269 jobs use `derive_from`; all predate `07676bd1d`. So a creature's
   S/E/N are different animals (varactyl, krayt).
3. **Context-free prompts.** Donor/Wookieepedia blurbs, 75/109 truncated mid-sentence, with no
   `style_notes`, no biome register (desert docs `desert.md`, `deep_desert.md`, `the_blue_desert.md` exist
   from 09-05/06), no canon-library visual brief (22 entries existed and went unused) and no reference images.
4. **Cartoon register.** The "Heavy, clean black outline" painterly boilerplate against the liked
   "natural-history, matte, no outlines, never cartoonish" register. It is back in 10-03 jobs.
5. They are simply **two weeks old** (09-20): generated before the canon push and the biome sittings he
   now judges against.

**Fix direction (not done here):** regenerate rather than wire. Author per-subject jobs from the biome
doc + canon `## Visual brief` (and attach the canon reference image as the edit input or master), use
the Long Shade-style register with no outlines, keep `--derive-facings` on, and rebuild the sheet's
current column excluding `dessicated*` texPaths (take the `bodyGraphicData` of the last lifeStage).
