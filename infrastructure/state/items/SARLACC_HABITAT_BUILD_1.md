# SARLACC_HABITAT_BUILD_1 — build the accepted sarlacc design

Supersedes SARLACC_NATIVE_HABITAT_1 (design phase — done). The design is
ACCEPTED whole (owner, 2026-09-12, verbatim on the filing event) with every
§7 fork RULED — the single source is
`design/Jawa/worldbuilding/sarlacc_native_habitat_draft.md` §8 (read it
first; this file only routes).

## spec (routes, not repeats)
- RSW-tier mod: `mandrake.rsw.sarlacc`-family packageId, namespace
  `RimMandrake.StarWars.Sarlacc`, RSW_ defNames; Mod Settings per
  MOD_OPTIONS_RETROFIT_1. Legacy `sw_` landmark defs stay until
  NAMING_SCHEME_EXECUTION_1.
- Stage I swimmer modeled on Anomaly's Devourer (owner's direction):
  swallow/digest kit re-themed as the press; verify the Devourer C# seams
  live before copying the pattern (never the numbers).
- Rooting-in-play (fork 1), one-way anchoring (3), clutch = THE birth-traps
  (4), breach-only kill (5), tile+tribe consequences first (7), all seven
  changed-return hediffs dealt by how taken (8).
- Tribal stage labels: write the four words, land on the owner's yes (9).
- Engine layer: `sarlacc_spec.md` (tentacle pawns, pocket-map nesting,
  portals — its 2026-08-31 measurements stand; its struck premises are
  bannered at top).
- Bridge leg: relocate the live `sw_Sarlacc` landmark off tile 2920 (now
  ZBiome_DesertOasis/Weeping Stones — collision) into Glare / Long Sand /
  Dry Marches; place 2-4 cisterns total; per worldmap freeze discipline
  (backup save, re-verify, re-stamp CSV if the landmark column exists there).
- At build: amend `water_doctrine.md`'s no-water-layer line (DBH thirst is in
  the shipped list — breach flood is fillable); deep_desert.md ban 5 already
  carries the carve-out (amended under the freeze 2026-09-12).

## verify
- Devourer-pattern swimmer swallows and can be cut open on a quicktest map.
- A swimmer roots on a seep in play; the pit persists.
- Breach floods the pocket maps upward and converts landmark live→dead.
- No RSW_/RUT_ grammar violations; features toggle in Mod Settings.
- 2-4 cisterns live on deep-desert tiles; tile 2920 carries none.

## criteria
The deep desert has its keystone animal, at RSW tier, per the accepted draft.

## build status — FOUNDRY, 2026-09-12 (BLOCKED, not closed)

**Built and pushed**, `src/RimStarWars/Sarlacc/` (`mandrake.rsw.sarlacc`,
namespace `RimMandrake.StarWars.Sarlacc`, RSW_ defNames — `naming_lint.py`
clean):

- **Stage I — RSW_SarlaccSwimmer.** ThingDef+PawnKindDef reusing Anomaly's
  Devourer BY REFERENCE (its BodyDef, PawnRenderTreeDef, ThinkTreeDef,
  `ConsumeLeap_Devourer` ability, `CompProperties_Devourer` swallow mechanic)
  with every message re-themed as the press wringing a drink, never digestion.
  `CompSarlaccSwimmer` (new C#) implements Fork 1 — a real water-reserve float
  that drains per in-game day (faster while moving), refills on a kill, and
  roots the swimmer (spawns `RSW_SarlaccAnchored`, destroys the pawn) either
  when the reserve hits zero or when a `RSW_DeepDesertSeep` marker is noticed
  nearby. Compiles clean (`dotnet build … Release`, 0 errors).
- **Stage II — RSW_SarlaccAnchored.** A destructible building (not
  breach-gated — draft §4.4's breach-only rule sits under "the cistern",
  Stage III, not Stage II) with `CompSarlaccAnchoredMouth`: a rare (MTB ~20
  days), adjacency-only strike, matching "it does not chase... strikes rarely,
  and only to tithe."
- **Seven changed-return hediffs, all shipped** (Fork 8):
  RSW_TheWrung / RSW_SaltEyed / RSW_TheStillness / RSW_TheTithe /
  RSW_TheBloom / RSW_Pressed / RSW_TakenAndReturned, each with a real
  mechanical stage (verified StatDef/PawnCapacityDef names via RimSage:
  InjuryHealingFactor, BloodPumping, Sight, MentalBreakThreshold, MoveSpeed,
  PainShockThreshold, Breathing, Manipulation). `CompSarlaccSwimmer` grants one
  (occasionally two, `secondHediffChance`) to a pawn who survives being
  swallowed and is spat free. "Dealt by how the pawn was taken" (pressed vs.
  shore) needs the pocket-map interior to know where the pawn was — not built
  (see below) — so this ships as a weighted-random pick instead; noted as a
  simplification, not silently dropped.
- **Mod Settings** (`RSW_SarlaccSettings`/`RSW_SarlaccMod`, MOD_OPTIONS_RETROFIT_1
  shape): toggles for rooting-in-play (+ drain-speed slider), rooting
  messages, the anchored tithe strike, changed-return hediffs (+ second-hediff
  chance slider), and the breach flood's cosmetic puddle. All-off degrades
  gracefully — every gate is an early return.
- **Stage III — RSW_SarlaccCistern / RSW_SarlaccThroat, v1 surface-only.**
  Fork 5 (breach is the ONLY kill): `useHitPoints=false`, `destroyable=false`,
  and `CompSarlaccCisternBreach` (a `CompInteractable` subclass, same pattern
  as vanilla's `CompDestroyHeart`/FleshmassHeart) is the sole route — no
  hit-point bar, no poison route. On breach it runs a SIMPLIFIED version of
  draft §4.4's sequence: narrative messages for the multi-level flood and
  ecosystem death, a real `Filth_Water` puddle spread at the surface, and a
  real conversion (destroy the cistern, spawn `RSW_SarlaccThroat` in its
  place — "the player's dungeon becomes the player's monument").
- **Tribal stage labels (Fork 9), DRAFT pending the owner's yes**, per the
  ruling's own wording: Seeker (swimmer) / Debtor (anchored) / Collector
  (cistern) / Paid (throat), echoing the Sun-Debt's own theology ("the sun
  lends and the sand collects... we take back what was drawn" —
  `FACTION_SPEC.md`). Shipped as description flavor text only; the doc
  register (swimmer/anchored/cistern/throat) stays the defName/mechanism
  vocabulary either way.
- **Art**: every texPath is a real, already-shipped file reused as a
  placeholder (Devourer's own body/swim/dessicated art for the swimmer;
  Anomaly's `RevenantFleshChunk` tinted for the anchored pit and the cistern)
  — nothing renders magenta, and nothing here is invented final art.

### Owed — why this is BLOCKED, not closed

1. **Live verification.** None of `CompSarlaccSwimmer`,
   `CompSarlaccAnchoredMouth` or `CompSarlaccCisternBreach` has been observed
   running in the game — a mechanism CHARTER says is owed a live check.
   Deliberately NOT spent solo here: a game-up cycle is expensive-list
   ceremony (`rimworld-load-round`), and CLAUDE.md's own lesson
   (`batch-game-up-work-before-restarting`) says to batch it with other
   pending game-up work rather than restart for one item. Bridge was FREE at
   build time (checked, not used). Next FOUNDRY/BENCH game-up window: deploy
   `Sarlacc`, quicktest-spawn a swimmer, watch it swallow a pawn and (with
   `rootingInPlayEnabled`) root; spawn a `RSW_DeepDesertSeep` next to one to
   force the seep trigger; place an `RSW_SarlaccCistern` and breach it.
2. **The pocket-map dungeon interior (press/gallery/reservoir, draft §4.1)
   does not exist.** `sarlacc_spec.md`'s own KCSG/pocket-map build ladder —
   named by this item's own spec as "the engine layer" — is not built by
   this pass or by anything else in this repo (confirmed: no SymbolDefs/
   StructureLayoutDefs/SitePartDefs anywhere reference a sarlacc; the
   `StructureInjectionsRUT` VaultDungeons/WarLab/DarkTower trio is the
   closest existing example of the pattern this would need). The native
   habitat draft's own §0 places this ladder explicitly out of its scope.
   Stage III therefore ships as a surface-only building this pass (see
   above), not the three-level dungeon the item's own "verify" section asks
   for ("breach floods the pocket maps upward").
3. **World placement is correctly NOT duplicated here** — it is
   `SARLACC_WORLDMAP_RELOCATE_1` (already filed, unclaimed): tile 2920
   relocation and 2-4 cistern tiles in Glare/Long Sand/Dry Marches. This
   build's `RSW_SarlaccCistern` is ready to be the thing that item places,
   but nothing places it yet.
4. **DBH thirst-need integration for the breach flood** (Fork 6: DBH thirst
   is confirmed live, so this is a real wiring task, not a design question)
   — not attempted; the flood is cosmetic filth only.
5. **Real sprite art** — the draft's own §Owed line, untouched here.
6. **A RimUtinni-side patch** making `RSW_TakenAndReturned` sacred/unclean
   specifically to the Sun-Debt ideoligion — correctly NOT built in this
   RSW-tier mod (naming-tier doctrine: faction-specific reactions are
   RimUtinni content), owed as a small follow-up item.
7. **`water_doctrine.md`'s no-water-layer line** — this item's own spec says
   to amend it at build (DBH thirst is shipped); not done this pass, folded
   into item 4 above.

Commit(s): see git log for `SARLACC_HABITAT_BUILD_1` (not closed — no
`Closes:` trailer).
