# BENCH_REBOOT_HANDOFF_202610100440 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610100044`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Tonight's proof that phone question cards work: after a sweep of every item that was really waiting on the owner, he answered 20 cards in about an hour. The sweep also found 13 items that said "blocked on owner" after he had already ruled. Before asking him anything, sweep `needs: owner` / `blocked:` and re-check each against the ledger. The stale ones are noise that makes the queue look owner-bound when it isn't.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Restart owed. FOUNDRY holds the bridge** for its full-list acceptance sweep, so BENCH did not restart. Not yet live: Silooth v6 in 3 facings (new mod `mandrake.rsw.siloothartoverride`, enabled in ModsConfig and deployed), weather-stone item art (WeepingStones needs `deploy_custom_mods.py --compose biomes --apply`), and the 66-sheet's biome-mod and SWBestiary deploys (skipped because they write a DLL while the game runs). Plus everything from the previous handoff's restart list.
- **ModsConfig has 565 active (MEASURED 2026-10-10 01:35 by parsing), byte-for-byte the id set of `infrastructure/state/modlists/ModsConfig.FULL.CANDIDATE_NO_TRADEUI_VTE.xml`.** That is `FULL.LATEST` minus Trade UI Revised and Vanilla Trading Expanded (retired by owner card 2026-10-09, `BAZAAR_DISPLACEMENT_PASS_1`), after `ART_OVERRIDE_FOLD_ALL_1` (475863020) folded the single-creature ArtOverride mods into their owners. No mod was lost.
- **66-conflict sheet enacted, independent audit 66/66 PASS** (`Transient/sheet_conflicts_enact_audit_2026-10-09.md`). Redraws are still in flight: Peko Peko male (its delete waits on the replacement), Krayt, Blixus, Opee juvenile, Gawpsack.
- **The Sith line needs a biome identified.** The owner said "lurking in the Crags biome rarely", and no RM_ biome named Crags exists (SANGUOPHAGE_KEPT_UNREACHABLE_1).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `SANGUOPHAGE_KEPT_UNREACHABLE_1` — owner wants the vampire xenotype redesigned as a Sith line (Empire + rare in "Crags"; player can't build their buildings or be converted); NEXT: find which biome "Crags" means, then retitle and send to design.
- `NONSW_XENOTYPES_SCOPE_1` — ruled: cut all ~32; NEXT: hand to FOUNDRY to build the cut patch and repoint the raider xenotype sets.
- `SUMP_TAR_LIVING_SYSTEMS_1` / `SARLACC_SEEKER_ROOTING_1` / `SCALD_WALKING_PASTURE_1` / `CRACKEDLANDS_SALVAGE_CLAIM_CREW_1` / `SHADECRAFT_LESSONS_DESIGN_1` / `HOSTILE_MOBILE_PLANTS_1` / `SCALD_GALLERY_SCHEMATIC_UNLOCK_1` / `ROT_NAVIGATOR_CAMPAIGN_TILES_1` / `CRACKEDLANDS_THREE_HEIGHT_FLORA_1` — each ruled by card tonight, ruling in a ledger note; NEXT: the owning seat builds from the note.
- `SHIP_ALLOY_FORGE_1` — durasteel is the forge's first recipe; zersium comes from The Forge, asteroids also allowed; NEXT: FOUNDRY builds it with ASTEROID_DESERT_ORES_1.
- `FLYER_STABLE_BODY_GATE_1` — Sketto floor 0.25 confirmed; NEXT: put the Hawkbat S/N masters to the owner when they render.
- `ART_SHEET_DONOR_JOIN_GAPS_1` — NEXT: confirm RSW_Plant_Nysyllin_Wild joins its renders on the rebuilt sheet, then close.
- `SCALD_UNDERWATER_FLORA_1` / `TWILIGHTSEA_FLORA_PASS_1` / `UNSUBSTANTIATED_SPECIES_ABILITIES_1` — NEXT: check them on the next live map after the restart.
- `LEANINGSCRUB_VENOMVINE_SITTING_1` — NEXT: stage it per `Transient/venomvine_sitting_runsheet_2026-10-09.md` when the owner is present with the bridge.
- `SELFTEST_DRIFT_CLEANUP_1` — NEXT: refresh the def dump and give Greentide A3 a criterion.
- Five FOUNDRY items still carry a stale owner block that the CLI wouldn't lift from BENCH (CRACKEDLANDS_FULL_RENAME_1, UNFINISHED_LINE_SITE_CHOICE_1, SCALD_GALLERY_SCHEMATIC_UNLOCK_1, TECHPRINT_FACTION_GATING_1, DESERT_FAMILY_PORT_EXECUTION_1); NEXT: FOUNDRY runs `rimflow unblock` on each (notes left).

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `art.py enact` refuses a conflict sheet ("snapshot missing"). Its rows fold back via `.map.json` into the original per-biome decisions files first (see: sheet_conflicts_enact_audit_2026-10-09.md)
- A question card's `header` is capped at 12 characters, its question must end in `?`, and every option needs a description of at least 40 characters (see: validate-question-card.py)

## Closed since the last handoff (2)

- `WEATHER_STONES_OWN_ART_1` — e2932cb7be65ca02c309552cacb04334fbbf051d
- `SILOOTH_V6_OWNER_PICK_1` — 72efe5e8d3b0

## Filed and still open (0) — the next seat's queue

Nothing filed in this window.

## Commits

```
6854e7afc Crackedlands flora: harvests (dye, fossil finds) and Veqma glow-limit ruled by card
acacdfc1a ledger: ZERSIUM_FORGE_BIOME_1 implemented; belt log
8f6953388 ZERSIUM_FORGE_BIOME_1: RSW_Zersium + Forge-only ore GenStep, settings toggle, first script (numbers PROVISIONAL)
098784296 bridge5: jumppack patch applied; droid format tiers live on the full list (spawn tier ok, mindless/blank leak third-party needs and wander), ledger
839c46f24 bridge5: tether reel partial, lasso still craftable on the full list, ledger
fa0f7c6ba bridge5: alias chain, Fever Wood cast textures, sarlacc genstep reads on the full list, ledger
5f9b9bcab Owner ruling by card: merge the two young-sarlacc defs
0484b20ae bridge5: Explosive Knockback 22/24 + Kinetic Arms 24/24 scenes on the full list, ledger
616bbcdf3 Fold Silooth art override into SWBestiary; delete mandrake.rsw.siloothartoverride
4eb4e9507 bridge5: parental enrage does not fire on the full list (fail recorded, cause not found), ledger
c0935b101 bridge5: glow tank dry line + drum-lurer last decision live on full list, ledger
898ba078f bridge5: swim-hood live read on full list (hood proof hook passes; Jawa hood still not drawn while swimming), ledger
ba38fea93 bridge5 sitting: Shokkweave hook note, burst-death + kinetic ruins reads, ledger
265214ac8 Remove stale owner-blocker text from 10 items (owner had already ruled)
ecaf912e5 Owner rulings by card: hostile plant family, gallery pump, Rot navigator tiles
b09a57710 ProofHarvest steps single ticks until Real FoW lets the Deconstruct designator see the node (same-tick check always read False on the full list)
c38927350 Owner rulings by card: herd trample, salvage crew faction+timing, shade lessons
f9e39dd04 FOUNDRY ledger: bridge released after bridge4 sitting
1ea100dc7 bridge4 full-list sitting: VTE unwind rehearsal on a save copy (wealth step 0, 1 missing class), acceptance reads, ledger events
b4400b20a Fix two texture misses from the full-list load: RUT_DyingCreep folder art read as Graphic_Single, 12 catch items used vanilla Meat_Small as Graphic_Single (engine uses Graphic_StackCount); bridge4 sitting log + checks
... 40 more: git log --oneline 1d332d76b..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running; BRIDGE NOT PROBED — no port found in the environment or in Player.log, so LOADING here is a DEFAULT, not a reading.)
- recorded  : UP
- Bridge: for     FOUNDRY full-list acceptance sweep + Shokkweave hook rebuild

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/modcheck/fixtures.json   FOUNDRY modcheck run output (not this window)
?? conversations/   earlier BENCH windows' conversation exports (not this window)
?? deployed/config/ModsConfig.before-tier-explosiveknockback.xml   earlier BENCH windows (attributed in the 10-08 morning handoff)
?? deployed/config/ModsConfig.before-tier-flowworks.xml   earlier BENCH windows (attributed in the 10-08 morning handoff)
?? deployed/config/ModsConfig.before-tier-kineticarms.xml   earlier BENCH windows (attributed in the 10-08 morning handoff)
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Doors/   earlier BENCH windows (attributed in the 10-08 morning handoff)
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Excavation/   earlier BENCH windows (attributed in the 10-08 morning handoff)
?? src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/   earlier BENCH windows (attributed in the 10-08 morning handoff)
```

