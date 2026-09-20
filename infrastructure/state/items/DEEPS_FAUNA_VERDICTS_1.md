# DEEPS_FAUNA_VERDICTS_1

Lantern Deeps fauna verdicts: cut 8 kinds from RUT_LanternDeeps `<wildAnimals>`,
rename/restyle 8 (Drinker, Grabber, Soulchime, Gembug, Glowbulb, Megapleura,
MossBeetleLarvae, Shatterjaw), file 8 restyle art jobs with the owner's briefs.

Frozen source of truth: `Transient/deeps_flora_fauna_review_2026-09-18.decisions.json`
(`frozen: true`, `owner_said: "Accept Lantern Deeps ruling and follow its
regeneration request."`). Note: the filing note in rimflow says "cut 7 kinds"
but the frozen decisions file lists 8 `cut` rows and 8 `regen` rows (16 total,
matching `decidedCount: 16`) — treating the frozen JSON as authoritative over
the prose summary.

## spec

Flora: all 12 kept, no action.

| defName | decision | new label | owner's note (verbatim) |
|---|---|---|---|
| RSW_AaroxisDendoria | cut | — | (no note) |
| RSW_AaroxisDendoriaLarvae | cut | — | (no note) |
| RSW_BloodropLarvae | cut | — | (no note) |
| RSW_BovineBeetleLarvae | cut | — | (no note) |
| RSW_FacetMoth | cut | — | "Please propose more truly alien hydrocarbon-based life forms that are utterly different than anything on the dayside... we need to repopulate this biome's fauna significantly with surprising life forms." |
| RSW_MossBeetle | cut | — | (no note) |
| RSW_PodWorm | cut | — | (no note) |
| RSW_RoyalRhino | cut | — | (no note) |
| RSW_BloodropMoth | regen | drinker | "give it sacks that it uses to store drained body fluids. Strangely, if it drains any day-side races with normal warm iron blood, it becomes poisoned and rapidly dies. Make it the glowing pale blue with yellow internal liquids of hydrocarbon-based life. Call it a Drinker." |
| RSW_BovineBeetle | regen | grabber | "Horrible, total remake. This should be huge, bodysize 4. A small room-sized blob of pale yellow substance with a glass-like carapace, many small legs, and one large pincer-ending arm. Truly alien. Call it a Grabber. Give it great strength to Hold someone with its pincer and slowly crush them each round." |
| RSW_FacetMothLarvae | regen | soulchime | "A stubby larva-like creature that builds armor out of crystal shards it collects along the ground. Emits a powerful psychic stun on anyone that gets too close and alarms it. Taming one produces a soothing effect on those around it. Call it a Soulchime." |
| RSW_Gembug | regen | (label unchanged) | "Make it the glowing pale blue with yellow internal liquids of hydrocarbon-based life. Strangely beautiful rounded-jewel-like body with carb-like legs and eye-like spots around its body like a starfish." |
| RSW_GlowSlug | regen | glowbulb | "Make it the glowing pale blue with yellow internal liquids of hydrocarbon-based life. Call it a Glowbulb. Make it actually glow." |
| RSW_Megapleura | regen | (label unchanged) | "Same body plan, but Make it the glowing pale blue with yellow internal liquids of hydrocarbon-based life" |
| RSW_MossBeetleLarvae | regen | (label unchanged) | "Slender, maggot-like bodyplan, pale yellow liquids and pale blue exterior, oozing and curling along the tunnels." |
| RSW_ShatterjawBeetle | regen | (label unchanged) | "A shiny black beetle, strangely conventional and out of place in this alien tunnel system. Enormous, thick, strong mandibles." |

House palette (all regen jobs except Shatterjaw): "hydrocarbon-based life:
glowing pale blue exterior, pale yellow internal liquids, painterly RimWorld
sprite, top-down-ish south facing, transparent background."

Task-brief scope (BENCH instructions, narrower than the frozen file — only 4 of
the 8 regens get defName-level XML edits beyond the art job): rename labels for
Drinker (RSW_BloodropMoth), Grabber (RSW_BovineBeetle, also bodySize 4 stat +
check larva link), Soulchime (RSW_FacetMothLarvae), Glowbulb (RSW_GlowSlug, also
add CompProperties_Glower). Gembug, Megapleura, MossBeetleLarvae, Shatterjaw get
art-restyle jobs only (no defName rename requested — labels unchanged per table
above), per the task brief's step 3/4 split.

Cross-refs: RSW_BovineBeetle is also in the Rot's wildAnimals (RotHerd
wound-link carrier) — flag on `ROT_FAUNA_KIN_WIRING_1` that the Rot row needs a
re-look now that Grabber is bodySize 4. Mechanics (Hold/crush, drain-poison,
psychic stun/soothe) ride `DEEPS_FAUNA_MECHANICS_1`, not this item.

## status log

- 2026-09-19 skeleton written; spec copied from frozen decisions file + rimflow item text.
- CUT: removed all 8 `cut` kinds from `RUT_LanternDeeps.xml` `<wildAnimals>` and
  also dropped `RSW_RoyalRhino` from `<allowedPackAnimals>` in the same file
  (extended slightly beyond the literal "wildAnimals only" instruction — a cut
  animal left as an allowed pack animal for a biome that no longer spawns it
  read as an oversight to leave). Race defs untouched. `RSW_MossBeetle` is
  still live in `RUT_AridShrubland.xml` and `BiomeCast_Ashkarr.xml`;
  `RSW_AaroxisDendoria` is still live in `RUT_Miasma.xml` and
  `BiomeCast_Ashkarr.xml` — left alone, cut only from the Deeps.
- RENAME/restyle (label + description; defName unchanged): RSW_BloodropMoth ->
  "drinker", RSW_BovineBeetle -> "grabber" (+ `baseBodySize` 2.45 -> 4 on both
  the ThingDef `<race>` block AND the earlier duplicate at line ~7492 was
  NOT touched — that one belongs to a different def, verified by context),
  RSW_FacetMothLarvae -> "soulchime", RSW_GlowSlug -> "glowbulb" (+
  `CompProperties_Glower`, glowRadius 4, pale-blue glowColor). Gembug,
  Megapleura, MossBeetleLarvae, ShatterjawBeetle: art job only, no label
  change (task brief's scope, narrower than the frozen decisions file's
  8-way regen list).
- RSW_BovineBeetle -> RSW_BovineBeetleLarvae link: confirmed hard via
  `CompProperties_Hatcher.hatcherPawn` on `RSW_EggBovineBeetleFertilized`
  (`RSW_BiomesTeamPort_Items.xml:1286`), NOT via lifeStageAges (all 3
  BovineBeetle lifeStages are `AnimalAdult` — no forced growth chain). Left
  the link intact per instructions; the larva race def still exists (cut only
  from the Deeps spawn table), so the egg->larva hatch still resolves.
- All 8 target races confirmed Graphic_Multi (loose `_south/_east/_north`
  PNGs on disk under `src/RimStarWars/SWBestiary/Textures/swanimals/...`),
  so every art job got all 3 facings.
- 8 art jobs filed via `fill_queue.py` (24 job files, one per facing) —
  ids `deeps_{drinker,grabber,soulchime,gembug,glowbulb,megapleura,
  mossbeetlelarvae,shatterjaw}_v2_{south,east,north}`, priority 50 (below
  the Rot wave's rut_* jobs at 60... i.e. FLOOR of 50 < 60 so this wave
  claims later), no `reference` field, canvas matched to each creature's
  existing `_south.png` dimensions except Grabber (1024x1024, the pipeline
  ceiling, `drawsize: 8` to avoid a spurious oversize warning while
  representing the bodySize-4 "room-sized" remake). Shatterjaw prompt has no
  house-palette line per the owner's own words (shiny black beetle, not
  hydrocarbon life).
- `validate_patch.py` on both edited XML files: 0 errors, 9 pre-existing
  warnings (RSW_Yooka/RSW_Jellypot/RSW_Stoneback texPath advisories,
  unrelated to any of the 16 target defNames).
- Deployed `LanternDeeps` (--apply): only `RUT_LanternDeeps.xml` drifted,
  clean apply, VERIFIED in sync.
- SWBestiary: the bulk plan also listed `RSW_MlieWaveC_Resources.xml` as
  drifted (another window's uncommitted work, per the task brief's warning) —
  did NOT run `--apply` on the mod. Instead copied
  `RSW_BiomesTeamPort_Races.xml` directly to
  `/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml`
  and diffed byte-identical.
- Hit a transient `.git/index.lock` held by a concurrent peer process in this
  shared worktree; waited for it to clear rather than removing it, then
  staged and committed only the paths listed above (explicit pathspec on
  both `add` and `commit`) — did not touch the large concurrent
  artpipe/pending/ churn (many deletions, several `rut_*` new jobs) visible
  in `git status` at the same time; that belongs to another agent's wave.
- 2026-09-20: all 8 restyle renders landed in `infrastructure/artpipe/done/`
  as `deeps_{drinker,grabber,soulchime,gembug,glowbulb,megapleura,
  mossbeetlelarvae,shatterjaw}_v2_{south,east,north}` (24 files, `facts: PASS`
  on all, canvas dimensions matching the existing live texture at each
  target). Mapped each job to its live texPath via each race's PawnKindDef
  `lifeStages/li/bodyGraphicData/texPath` (not the ThingDef — these races
  carry no `<graphicData>` of their own; the art lives on the PawnKindDef,
  same defName as the race): BloodropMoth/BloodropMoth, BovineBeetle/
  BovineBeetle, FacetMoth/Crystalpillar (Soulchime), Gembug/Blue/Jewelbug
  (Gembug's Red/Green/Yellow color variants are NOT referenced by the live
  PawnKindDef and were left untouched — out of scope, the frozen decision
  filed one job per creature), GlowSlug/GlowSlug, Megapleura/Megapleura,
  MossBeetle/MossGrub, ShatterjawBeetle/ShatterJaw. Copied all 24 PNGs over
  the live textures, `deploy_custom_mods.py --mod SWBestiary --apply` —
  clean drift (exactly these 24 files, nothing else), VERIFIED in sync.
  All def/rename/mechanics work was already complete from the prior wave
  (`a00f52f10`); this closes the harvest gap. No live bridge spot-check —
  RimWorld caches `ContentFinder<Texture2D>` for the process lifetime with
  no hot-reload tool in JawaBench, so a live check now would read the OLD
  art regardless of the deploy's correctness; the swap is verified at the
  file level (byte-identical on disk, clean `Graphic_Multi` texPath already
  proven to resolve for these races) and will show correctly on RimWorld's
  next restart, same as any other texture-only change.
