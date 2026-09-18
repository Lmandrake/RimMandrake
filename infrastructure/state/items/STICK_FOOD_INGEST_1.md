# STICK_FOOD_INGEST_1 — measured ingest scope (BENCH, 2026-09-02)

## 2026-09-18 (FOUNDRY, belt mode, subagent)

Re-verified everything offline, confirmed the block reason from 2026-09-07
still holds, and made **no live change** this pass — the game (`rimflow
game`) reads RUNNING with an unrelated water-terrain investigation live
elsewhere tonight, and a new mod's assemblies/defs cannot be hot-loaded into
a running session (`rimworld-start-prep` §3: RimWorld only writes
`ModsConfig.xml` on an in-game menu change; loading a NEW mod's content
needs a real restart either way). Forcing that restart on a shared,
currently-running session for this alone was judged not worth the ~15 min
cold-load cost without the owner present to confirm — noted as still owed,
not attempted.

**Deploy check**: `diff -rq` between
`src/RimStarWars/Cuisine/{About,Assemblies,Defs,Textures}` and the deployed
copy at `.../RimWorld/Mods/Cuisine/` — byte-identical, all four subtrees.
`git status --short src/RimStarWars/Cuisine/` — clean, nothing uncommitted.
No `.cs` file under `Source/` is newer than the shipped
`RimStarWarsCuisine.dll` — the deployed build is current. Re-ran
`validate_patch.py` against the full live load set (`--defs` pointed at
`Mods`, `Data`, and the Workshop content root; 634/634 active mods resolved
on disk): **0 errors, 0 warnings**, same clean result as 2026-09-05 — only
advisory `info` lines noting `CompProperties_NameGen`'s class isn't found in
the *active* load set, which is expected and correct since the mod itself
isn't active (see next paragraph), not a defect in the mod.

**Not enabled, confirmed again**: parsed the live
`Config/ModsConfig.xml` (`ET.parse(...).find('activeMods')`, never a grep,
per this file's own trap) — 634 active mods, `mandrake.rsw.cuisine` is
**not** among them. Both donor mods ARE active: `badoaks.meatonastick`
(packageId on disk: `badoaks.MeatOnAStick`, workshop `3435027361`) and
`badoaks.meatonastick.expansion` (`badoaks.MeatOnAStick.expansion`, workshop
`3577333297`) — matches this item's own 2026-09-05 measurement exactly, no
drift since.

**Live craft-proof**: NOT run. Impossible without the mod being active, and
enabling it requires the restart this pass declined to force on a shared,
currently-running session mid-investigation elsewhere. Still owed to the
next session that can spend a cold load on it (or the owner's own restart).

**Donor retirement**: NOT done, and correctly so — retiring
`badoaks.meatonastick`/`badoaks.meatonastick.expansion` means editing the
live `ModsConfig.xml` (a live mod-list change, verify-first territory per
the task brief), and doing that *before* our own replacement has ever been
live-tested would be backwards: if the untested replacement turns out
broken after the donors are gone, the "stuff on a stick" line disappears
entirely with nothing proven in its place. This item's own 2026-09-02 note
already scoped retirement as a step that comes *after* craft-proof, not
alongside it — that ordering still holds. `design/Jawa/mods/required_mods.md:1109`
only carries a one-line census entry for the base BadOaks mod ("CLEAN
ADOPT"), not a runtime dependency — nothing else in the repo was found
depending on either donor mod's defNames.

**Net**: no new criterion satisfied this pass; all three remain unchecked.
Left `doing` — not reblocked, since the blocker text from 2026-09-07 already
covers the situation precisely and nothing changed to require restating it
as a fresh block. What's left, in order: (1) a session with room for a real
restart adds `mandrake.rsw.cuisine` to the live mod list and does the
craft-proof — spawn ingredients, run the `RSW_*OnAStick` recipes at a
Campfire/CraftingSpot, confirm art+stats on the resulting item and that
eating one leaves an `RSW_CookedSkewer`; (2) only once that's clean, retire
both BadOaks donor packageIds from `ModsConfig.xml` and re-verify with a
clean load.

## 2026-09-05 (FOUNDRY) — in-house sprite regeneration complete, all 9 icons

All 9 `Graphic_StackCount` icons generated fresh (Codex `image_gen` + local
chroma-key, per `generating-rimworld-sprites`), 256x256 RGBA, none copied from
either BadOaks donor mod. Owner course-corrected mid-pass toward an alien
Star Wars cuisine look (not vanilla brown-meal realism) — all 8 food icons
below were generated under that direction from the start, nothing had to be
redone:

- `RSW_Skewer` — plain pale wood stick, mundane by design (raw resource, no
  alien treatment called for).
- `RSW_MeatOnAStick` — three chunks of deep violet-blue alien meat with
  iridescent marbling, charred edges.
- `RSW_VegOnAStick` — three bulbous spiraled alien vegetable chunks, teal and
  violet-purple.
- `RSW_FungusOnAStick` — three alien mushroom caps, deep teal/cobalt with
  glowing blue bioluminescent speckles and a ridged gill pattern.
- `RSW_LittleMeatOnAStick` — same violet-blue alien meat treatment as
  `RSW_MeatOnAStick`, one small chunk on a mostly-bare stick to read as the
  smaller portion.
- `RSW_BlendOnAStick` — alternating violet-blue alien meat and teal alien veg
  chunks on one stick.
- `RSW_FishOnAStick` — a small alien aquatic creature skewered lengthwise,
  cyan/blue scales, asymmetric fins, extra eyes.
- `RSW_FruitOnAStick` — two segments of spiky pink-and-orange alien fruit
  with a spiral rind pattern.
- `RSW_CookedSkewer` — bare stick, tip lightly charred black, otherwise plain
  wood (the "empty stick" joke item).

`validate_patch.py src/RimStarWars/Cuisine/Defs/ThingDefs_Cuisine.xml`: 0
errors, 0 warnings (was 9 texPath errors before this pass). Deployed via
`deploy_custom_mods.py --mod Cuisine --apply` (9 files, verified in sync).
Not enabled in ModsConfig, no live/bridge testing done — that and retiring
both BadOaks donor mods are still owed next.

## 2026-09-05 (FOUNDRY) — moved from a standalone RimUtinni mod into RimStarWars: Cuisine

Owner, verbatim: *"we shouldn't even have Mandrake stick mods, it should be
folded directly into the star wars cuisine project we own."* The "star wars
cuisine project" is `design/Jawa/proposals/high_cuisine_deep_design.md` —
ruled by the owner 2026-09-02 (mostly v1'd, 9 rows), including this exact
mechanic: *"Ingest the 'stuff on a stick' mod into our own version and
jettison that mod eventually... Let's take what we need and release them."*
That design was never given a mod home; it should have been this pass's
container from the start rather than a second standalone `RimUtinni` mod.

**Retired**: `src/RimUtinni/StickCuisine/` (`mandrake.rut.stickcuisine`) —
deleted from the repo and un-deployed from the game's Mods folder. It was
never enabled in `ModsConfig.xml`, so nothing live changes for the owner.

**New home**: `src/RimStarWars/Cuisine/` (`mandrake.rsw.cuisine`, ns
`RimMandrake.StarWars.Cuisine`, `RSW_` prefix — RimStarWars tier per
`NAMING_SCHEME_PLAN.md`'s tier test: general Star Wars cuisine content, not
Ash'karr-specific). All 9 ThingDefs, 17 RecipeDefs, 1 ThoughtDef and both C#
hooks (`NameGenComp`, `IngredientValueGetter_ExcludeSkewer`) moved verbatim,
`RUT_` renamed to `RSW_` throughout (defNames, texPaths, namespace, DefOf).
`dotnet build`: 0 warnings/errors. `validate_patch.py`: 0 errors on
Defs/RecipeDefs/ThoughtDefs/About; the 9 `texPath` errors on ThingDefs are
the same pre-existing missing-art gap as before the move (never a regression
introduced by it) — sprite regeneration is next.

This mod's own `About.xml` now states it is the intended eventual home for
the rest of `high_cuisine_deep_design.md`'s build ladder (hazard-pantry,
diplomacy meals, brewing, the Feastboss, the Nine-Course Ninefold Feast) as
later waves land, so future cuisine work has nowhere else to default to.

**Owed next**: in-house sprite regeneration for all 9 ThingDefs (owner,
2026-09-05: "Yes, do sprite regeneration"), THEN both BadOaks donor mods can
finally be retired per this item's own long-standing, still-open criterion.

Survey: research/Jawa/stick_food_mods_survey_2026-09-02.md. Both mods ACTIVE:
- `badoaks.meatonastick` (workshop 3435027361): MEASURED 4 defNames (1 meal
  ThingDef `MeatOnAStick`, 2 recipes, 1 MealSimple patch target), 3 PNGs.
- `badoaks.meatonastick.expansion` (workshop 3577333297): MEASURED 26 defNames
  (7 stick-food ThingDefs incl. meatless/fish/fruit/fungus/veg/blend/little,
  13 recipes incl. x4 bulk, a craftable stick `chrisb_moas_sticks` + its
  recipe, 2 ingredient-category defs, 1 thought `AteMeatlessStick`), 18 PNGs.

⇒ Ingest = ~8 ThingDefs + ~15 recipes reimplemented under RUT_ names inside
the recipe-discovery tree (cui:recipe-discovery ruling), sprites REGENERATED
in-house (no license found — do not copy BadOaks art). Then both retire.
`chrisb_` prefix inside the expansion suggests a third author's stick def is
embedded — check attribution before reusing that name shape.

## 2026-09-02 (FOUNDRY) — ported under RUT_, art deliberately not copied

Built `mandrake.rut.stickcuisine` (`src/RimUtinni/StickCuisine/`), per this
item's own scoping above: RUT_ prefix, RimUtinni tier. Ported both donor
mods' full content:

- 9 ThingDefs (`RUT_Skewer` + 8 meal variants: meat/veg/fungus/little/blend/
  fish/fruit/cooked-empty), all `ParentName="MealCookedIngredientless"` or
  `"ResourceBase"` (real vanilla Core abstracts, confirmed on disk before
  use).
- 17 RecipeDefs (base mod's 2 + expansion's 15, incl. the skewer-crafting
  recipe and every ×4 bulk variant), wired via each `RecipeDef`'s own
  `<recipeUsers>` (Campfire/CraftingSpot) — **not** a re-declared vanilla
  ThingDef patch, which would have silently discarded Campfire's real
  fields. Caught and removed a first-draft mistake that did exactly that
  before it shipped.
- 1 ThoughtDef (`RUT_AteEmptySkewer`).
- Two small C# hooks (`RimMandrake.Utinni.StickCuisine`): `NameGenComp` is a
  direct port of the base mod's own shipped `Source/MeatOnAStick_Naming/
  NameGenComp.cs` ("Roasted X" label transform). `IngredientValueGetter_
  ExcludeSkewer` is FOUNDRY's own reconstruction of the expansion's
  un-sourced `MOAS_Expansion.IngredientValueGetter_MeatlessStick` (compiled
  DLL only, no `Source/` shipped) — inferred intent (zero out the skewer's
  nutrition contribution so it doesn't skew product-count math), not a
  byte-for-byte decompile. Flagged in the file's own header.

**Art**: NOT copied, per this item's own instruction (no license found on
either donor mod). Textures folders exist but are empty; both `ThingDef`s
and the loose PNGs were briefly copied in an early draft of this pass and
then deliberately removed once this note's own earlier text was re-read —
in-house sprite regeneration (`generating-rimworld-sprites` skill) is
separate, still-owed work.

`dotnet build`: 0 warnings/errors. `validate_patch.py`: 0 errors, 9 advisory
warnings (all missing-texPath, expected and correctly non-fatal — the art
gap is real, not a validator false positive this time). Deployed file-copy
only, not enabled in ModsConfig, no restart, no live proof.

**Recipe-discovery gating, a judgment call**: `high_cuisine_deep_design.md`
§8 (recipe-discovery) is a big, not-yet-built system (physical cookbooks,
rumors, district visits). §1's ruling table calls stick food "basic stuff"
at the START of the progression, and both donor mods themselves unlock at
the Campfire immediately, no research/discovery gate at all. FOUNDRY read
"inside the recipe-discovery tree" as *belongs to that content family*, not
*gated behind the not-yet-built discovery mechanism* — these recipes stay
immediately available, matching the donors' own design and the "basic
stuff" framing. Flagging this interpretation explicitly in case the owner
meant something stricter.

**`chrisb_` prefix note**: not independently re-investigated this pass: the
expansion's own stick-craft def/recipe (`chrisb_moas_sticks`/
`chrisb_Craft_moas_sticks`) used that prefix; our port renamed both to
`RUT_Skewer`/`RUT_CraftSkewers`, so the attribution question this item
raised no longer has a load-bearing defName riding on it, but the original
donor mod's own author credit (if any) hasn't been separately verified.

## criteria
- [ ] All stick foods reachable in our own mod — **defs and art done**
      (in-house regeneration, 0 texPath errors), live spawn/cook proof still
      owed.
- [ ] Both badoaks mods retired from the full list with a clean cold load —
      not started; retirement is explicitly a LATER step per the owner's own
      "jettison eventually" framing, not this pass's job.
- [ ] No cast/thought references left dangling — not yet checked against a
      live game (needs the retirement step first to even be testable).
