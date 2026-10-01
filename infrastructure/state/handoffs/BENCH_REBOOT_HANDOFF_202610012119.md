# BENCH_REBOOT_HANDOFF_202610012119 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610010838`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The shared checkout at `/mnt/d/Luke/dev/RimMandrake` is still far behind origin and cannot sync (peers' dirty files block `shared_sync.py`). Every BENCH publish this session went through a private worktree off `origin/main`. A FULL worktree checkout now fails on write errors, so use a sparse one (`git worktree add --no-checkout --detach <wt> origin/main; git sparse-checkout set --no-cone /design/Jawa/ /infrastructure/state/ /src/RimMandrake/rimflow/ /src/RimMandrake/Utils/; git checkout`). The artpipe daemon reads the SHARED tree's `infrastructure/artpipe/pending/`, so commissioned jobs must also be copied there as new untracked files, or they never generate.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
1. **Abyss lore is in use as Claude drafts, waiting for his pen:** the Summ biology, the ship's part-refusal lines, the wreck description and the four rite inscriptions (cast bible §6, `design/Jawa/worldbuilding/biomes/abyss_cast_bible_2026-10-01.md`). He ruled "use drafts now, I'll edit later".
2. **Summ stage labels:** "summ", "summing", "summ egg", "Summ the All-Render". He named the summing; the rest are Claude's.
3. **Greentide at-risk feature:** I called it "steam-fog" on a card. The scores doc names the roil weather plus wet-bulb locks, and `BIOME_TIER_CLEANUP_1` was filed on that. Confirm it's what he meant.
4. **Nightside Ice:** he passed on all five new pieces (ship, sound and tech stay unfilled by his choice) and made the ridge a plain landform.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `NIGHTSIDEICE_BEDAZZLE_SITTING_1` — turn 1 ruled (`90dcf41f9`), build item `NIGHTSIDEICE_HEAT_DIAL_BUILD_1` filed; NEXT: commission art for the ratified cast (sohl, shivven, frissim, wyrmlet, dhorrumak, hessarund landform, hoarfrost) in the Abyss commission shape, copy the jobs into the shared tree's `pending/`, then close the sitting.
- `BEDAZZLE_TOP_SHAPE_PROGRAM_1` — track (a) sitting 1 of 12 ruled; NEXT: file `LANTERNDEEPS_BEDAZZLE_SITTING_1` and background its review + the mandatory five-idea GPT consult to Opus (shape: `design/Jawa/worldbuilding/biomes/nightsideice_bedazzle_review_2026-10-01.md`).
- `SALVATION_RITES_UNIFICATION_1` — the register holds 98 rows, with the rites pass ruled where the owner answered; NEXT: put the remaining pitched B7 rites (`design/Jawa/biome_rites_pass_2026-10-01.md`) to him on cards, explaining each in full.
- `BIOME_TIER_CLEANUP_1` — filed for FOUNDRY; NEXT: FOUNDRY builds it (needs a load to prove).

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A commit inside a private worktree failed on `index.lock` (the health publisher holds it), yet `merge-base --is-ancestor HEAD origin/main` passed, because HEAD was still the base. Check `git log -1 --format=%s` before claiming a push. (filed: LESSONS_INBOX)
- A full `git worktree add` checkout fails with write errors on this drive; use sparse. (filed: LESSONS_INBOX)
- The owner wants every card subject re-explained in full and never relies on his memory. (see: auto-memory explain-fully-never-assume-he-remembers)

## Closed since the last handoff (2)

- `BLACKCRAGS_BEDAZZLE_SITTING_1` — 62444e7ad
- `BAROQUE_BEDAZZLE_PROGRAM_1` — 6c16589f2

## Filed and still open (23) — the next seat's queue

- `CAULDRON_ENRICHMENT_AUDIO_1` — Cauldron enrichment sounds: vexxiss bellow, metal-tree harvest noise, directional vapour-bank hisses
- `CAULDRON_ENRICHMENT_VISUALS_1` — Cauldron enrichment visuals: dewfall chemical beads, dewfall plant saturation, assay flecks on old trees, vexxiss mineral-ringed footprints
- `VEXXITH_CLOSED_LOOP_BUILD_1` — Vexxith closed loop: acid immunity hook, plate-only recipes, poor-walls/weapons stance - three open questions
- `LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1` — Pitch further venomvine forms to the owner (he typed "Might need even more"); rule before any art
- `LEANINGSCRUB_SWEETLINE_GUARDIAN_1` — Sweetline tree guardian: what creature, dormant pawn or incident, what counts as harm
- `LEANINGSCRUB_SWEETLINE_NAME_REGISTER_1` — Sweetline tree naming register (current RM_NamerSweetlineTree vocabulary is a placeholder)
- `FORGE_SPUNSTONE_SOURCES_1` — Spunstone bonding remainder: foundry salvage as a study source, and what the high-speed doors and advanced structural parts are
- `LONGSHADE_MIDDENS_DESIGN_1` — Lee-side middens: owner to rule what a midden is, what searching yields, the clean-patch tell, the vrekka
- `SHADECRAFT_LESSONS_DESIGN_1` — Shade gear learned by study: lesson-to-piece mapping, and Long-Shade-only lessons vs the cross-biome gear ruling
- `GLOOMCAST_WAKE_RIDERS_1` — Gloomcast shadow: which small grazers actively follow it, and whether feeding leaves a scar distinct from dung
- `ABYSS_ETCHFALL_BUILD_1` — Etchfall: Dark grain erodes unroofed stone and steel into tholin dust (slider)
- `ABYSS_LAMP_CROPS_BUILD_1` — Lamp crops: transplanted glowing trees light a farm against the Dark
- `ABYSS_INVENTED_CREATURES_TO_RM_1` — Move cindermare and skarnix into the free RM_ tier
- `ABYSS_FOLD_LAMP_BUILD_1` — Heat-folding research and the fold-lamp (Abyss)
- `ABYSS_SOUNDSCAPE_BUILD_1` — Abyss gust soundscape plus Dark-swallows-sound spike
- `ABYSS_FREE_TIER_BODY_1` — Abyss free-tier body: own labels, wire 12 done crags art sets, guard/own 8 flora, weather labels, About fix
- `SALVATION_RITES_UNIFICATION_1` — Salvation rites unified in mandrake.rut.rites; biomes teach rites (four Abyss rites, four gods)
- `SALVATION_RITES_RENORMALIZE_PASS_1` — Renormalize gods, appeasement kinds and outcomes across all rites
- `BEDAZZLE_TOP_SHAPE_PROGRAM_1` — Bedazzle top-shape program: re-score 12, finish seas, build backlog, rites over the 11
- `NIGHTSIDEICE_BEDAZZLE_SITTING_1` — Nightside Ice bedazzle sitting (grandfathered track a, worst-first)
- `BIOME_TIER_CLEANUP_1` — Biome tier cleanup: move twin-only features to RM_, scrub Star Wars IP, move RUT_ defs out of free mods
- `FLAWED_MASTERWORK_ENGINE_CHECK_1` — Can Ninefold damp Ozzik's knock-on to Sh'kaar and Zizzik for one call?
- `NIGHTSIDEICE_HEAT_DIAL_BUILD_1` — Nightside Ice: eviction housekeeping, heat dial and shivven breach loop

## Commits

```
7a7158ae7 Health artifacts refresh Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com> Claude-Session: https://claude.ai/code/session_01TV3UHcYF6XK8Tv2D5kJ5mj
90dcf41f9 Nightside Ice turn-1 rulings recorded; heat dial build filed
21e5f59a3 WEEPING_STONES_FIRST_SCRIPT_1: first north-star script for WeepingStones (47 components, tier weepingstones_solo)
fdef1627d WeepingStones About.xml: remove two false statements (stocked pools "OFF by default", jobs "STILL OWED")
0c94ed68c Ledger sync: slime seeker tool item
18669c79a LEANING_SCRUB_FIRST_SCRIPT_1: first north-star script for LeaningScrub (43 components, never run live) Tier baroque_wave0 (LeaningScrub ships composed in mandrake.rm.biomes, so EXPECT_MODS is that id). The Lean is UNCOVERED: needs a Scrub-biome map site. Offline only: selftest proves each check red under a broken fake game; live shapes are unproven.
34011ad43 Rites rulings 2026-10-01: rites everywhere, Charged Reed, pyre merged into waking
2a85fd309 GELATINOUS_SLIME_FIRST_SCRIPT_1: first north-star script (39 components, 10/10 settings), offline-proven
53e2f369a Pyrelands suite: pen the warmth pair, record room_heat results
dc4bbe167 Ledger sync: ExplosiveGrowth probe-tool item
9739a6002 ExplosiveGrowth first north-star script: 33 chains, 51 walk lines, tier explosivegrowth_solo
ae74fb663 BACTA_FIRST_SCRIPT_1: first north-star script for Bacta (35 components, 8 chains, mock-proven)
27419f367 Nightside Ice bedazzle sitting: review, roster fill, GPT five, rites, turn-1 card
0516a3d46 WARCASKET_FIRST_SCRIPT_1: Warcasket first north-star script + walk; fix two MOD defects MOD: RM_Warcasket had no tickerType (apparel default Never), so the compound-failure comp never ticked; ToxicEnvironmentResistance sat in statBases, not equippedStatOffsets, so the pawn stat never rose. Guards: compound_failure_fires, toxin_cover.
5d5f7b546 Debug process: keep the bridge busy (owner ruling), file bridge-utilization metric item
736a2a36c Bedazzle: grandfathered order + GPT five-ideas step; file BIOME_TIER_CLEANUP_1
b80b24bc0 Rites register: drop wind-hour from the Weeping Stones row
4541ee03a HARNESS: offline lint of bridge calls against declared tool schemas (LINT_CALLS_1)
054fc56fe Biome rites pass: 23 found rites for the ten other bedazzle biomes
cc1c60659 Health artifacts refresh
... 125 more: git log --oneline 9c6edaf00..HEAD
```

## Game / bridge / tree state at wrap

- Game, from a bare `./game` in the shared tree (its UP stamp went into the shared tree's ledger, which cannot sync): running   : RUNNING   (RimWorldWin64 running, bridge answers) recorded  : DOWN  → corrected to UP, measured now
- Bridge: for     FOUNDRY: first-to-completion north-star trials (FlowWorks/Graffiti/Pyrelands)

Working tree clean apart from untracked `Transient/`.

