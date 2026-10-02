# BENCH_REBOOT_HANDOFF_202610020550 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610012119`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The shared checkout `/mnt/d/Luke/dev/RimMandrake` is still far behind origin. `--wake` run there printed a STALE handoff (05:27 instead of 21:19). On wake, read the newest `BENCH_REBOOT_HANDOFF_*` from `git show origin/main:` first. Publish through a sparse worktree, as before. Every subagent this session followed that procedure without incident.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
1. **Sump turn-3 card is drafted, not yet put:** section 8 of `design/Jawa/worldbuilding/biomes/sump_bedazzle_review_2026-10-01.md` (`b1ef1acc1`). Its questions are the Sinking's god (Ishko recommended), how ownership claims get erased via RimProperty, the size of the Heat drop, and four map-local offerings. Option "Grudge at table" is an effigy of your own colonist, which the turn-1 write-up ruled out; flag it when putting the card.
2. **Rite A ("the Sinking") lowers Imperial Heat on his word,** overriding the standing "Heat is never lowered by success" rule for this rite only. RimProperty has no claim-removal call yet.
3. **The Lasso cut also needs Melee Animation's own "No Lassos" setting.** The mod hands lassos out from its own code; Cherry Picker alone is not enough (`LASSO_CHERRYPICKER_REMOVAL_1`).
4. **CLAUDE.md corrected:** the ship flies to the `RM_SeabedLayer` planet layer; `RM_SeaDiveHatch` is a leftover (`SEA_DIVE_HATCH_RETIRE_1`).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `SUMP_BEDAZZLE_SITTING_1` — turns 1-2 ruled and ticketed (7 FOUNDRY items, 17 art jobs); NEXT: put the turn-3 card from the review doc section 8 to the owner, fold his answers, file the two tar-rite build items, close the sitting.
- `BEDAZZLE_TOP_SHAPE_PROGRAM_1` — sittings 1-3 closed (Nightside Ice, Lantern Deeps, Pyrelands), 4 (The Sump) at turn 3; NEXT: after the Sump closes, open sitting 5 `WEBWORK_BEDAZZLE_SITTING_1` with an Opus review in the Pyrelands/Sump shape, carrying today's liked/rejected patterns.
- `SALVATION_RITES_UNIFICATION_1` — pitched rites still unruled; NEXT: put the remaining pitched rites to him on cards (Zizzik's rite cap is waived for now, by his word).
- `GRAVSHIP_PEACEFUL_SETTLEMENT_LANDING_1` — filed for FOUNDRY, gates the Hutt slave pit test site; NEXT: FOUNDRY proves it live.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `--wake` in a stale checkout prints the wrong handoff. (filed: LESSONS_INBOX)
- The rimflow owner-quote flag rejects quotes ending in a question mark and stitched multi-answer quotes. (filed: LESSONS_INBOX)
- A worktree commit that fails on `index.lock` leaves HEAD at the base, so `merge-base --is-ancestor` falsely passes; guard with a HEAD != BASE check. (filed: LESSONS_INBOX, prior handoff)
- The question-card gate refuses options labelled "Neither"/"None" and headers over 12 characters. (see: CLAUDE.md, question-card gate)

## Closed since the last handoff (6)

- `NIGHTSIDEICE_BEDAZZLE_SITTING_1` — 9cc70cce762b748259134f947c46ff8baf585903
- `NINE_FAULTS_PERMANENT_RITE_1` — 2abb78f03
- `SHIP_CARGO_HOIST_DESIGN_1` — 97ca59bad
- `LANTERNDEEPS_BEDAZZLE_SITTING_1` — 9e1a090aebf9b0054f46de151dab5af6e53083b1
- `DEEPS_FAUNA_REPOPULATION_1` — 56f9c12e7
- `PYRELANDS_BEDAZZLE_SITTING_1` — 4ff85e5e0f

## Filed and still open (28) — the next seat's queue

- `GODS_NOT_EVIL_SWEEP_1` — No god is evil: remove 'evil' god framing from the pantheon canon and the ~25 docs/code comments listed in nine_faults_permanent_rite_2026-10-01.md se
- `NINEFOLD_FAVOUR_ODDS_BUILD_1` — Build Nine Faults (fresh-find rite, Rekko to Zizzik), the Left Behind transfer (Ohm to Ta'Baa), the god-favour odds-shift def type with incident and w
- `HOIST_SHIP_PART_BUILD_1` — Keel hoist as a gravship part: items, awake colonists, downed beasts captured on arrival; tether lock; manifest; Lantern Deeps test (animation optiona
- `HOIST_FIXED_SITE_FRAMES_1` — Fixed hoist head-frames placed only by site gensteps, plus the sealed holder-feature target; Foundry tower first (animation optional, last)
- `HUTT_SLAVE_PIT_TEST_SITE_1` — Hutt slave pit at a small stand-alone test site: sell slaves, prisoners and downed beasts for silver; sealed oubliette liftable only after conquest; n
- `HUTT_LOTTERY_CHUTE_BUILD_1` — Hutt chance chute: stake goods, slaves or beasts; house cut; value-matched crate returns; needs the slave-pit test site (animation optional, last)
- `LANTERNDEEPS_FAUNA_TIER_PORT_BUILD_1` — Lantern Deeps: port the eight invented RSW_ residents to RM_ (Q12) and repoint the darkness predators
- `LANTERNDEEPS_WORKING_DEAD_BUILD_1` — Lantern Deeps: the well-provisioned dead, the Working Dead and the Shard-minds
- `LANTERNDEEPS_LANTERN_LIGHT_BUILD_1` — Lantern Deeps: the Lantern, the one safe light the darkness mechanic does not count
- `LANTERNDEEPS_HYDROCARBON_FAUNA_BUILD_1` — Lantern Deeps: the twelve hydrocarbon animals (galuush, hush, knocker, candler, sipper, drifter, tapper, pooler, blinker, chiller, slick, shoal)
- `LANTERNDEEPS_CREEP_CLEAVERS_BUILD_1` — Lantern Deeps: the Creep (accretive predator) and the Cleavers (fracture-moving fragment life)
- `LANTERNDEEPS_AURORA_COLLAPSE_BUILD_1` — Lantern Deeps: the aurora feast-day condition and the ruled collapse warnings
- `LANTERNDEEPS_MINDSTONE_GALLERY_BUILD_1` — Lantern Deeps: the mindstone gallery, the mindstone as a find, the Kindled made reachable (campaign)
- `LANTERNDEEPS_ORUN_GHAL_BUILD_1` — Lantern Deeps: Orun-Ghal, the crystal-worn mining suit, an inhabitant to study and befriend
- `LANTERNDEEPS_ANSWERING_RITE_BUILD_1` — Lantern Deeps: The Answering, Ohm's found settlement rite (campaign)
- `PYRELANDS_FAUNA_TIER_PORT_BUILD_1` — Pyrelands: move the eight invented RUT_ animals to RM_ in the free mod (Q11a/Q12)
- `PYRELANDS_HEAT_KIND_BUILD_1` — Pyrelands: declare heat kind (overhead, sun from latitude) and move furnace warmth onto the sun-heat code
- `PYRELANDS_ULLAI_GIANT_BUILD_1` — Pyrelands: the ullai herd and the furnace-beast grown into a giant
- `PYRELANDS_LIGHTNING_BREAKER_BUILD_1` — Pyrelands: lightning breakers (metal+sand forge recipe, learnable only in the Pyrelands, Mod Settings)
- `PYRELANDS_STRUCK_GLASS_RITE_BUILD_1` — Pyrelands: The Struck Glass rite for Zizzik (stamped lightning-glass ring, random powerful strike)
- `SUMP_BEDAZZLE_SITTING_1` — The Sump bedazzle sitting (grandfathered track a, sitting 4)
- `SUMP_FREE_TIER_MOVE_BUILD_1` — Sump: move all 24 Sep content (tar coating, tarred, solvents, walkways, gaslight, vault, research) into Baroque Biomes as RM_; fix the RUT_Tarred refe
- `SUMP_FAUNA_WIRING_BUILD_1` — Sump: wire the built gulveth and thrummel family into RM_TheSump beside the donors (no eviction)
- `SUMP_HUNGRY_GOD_TEXT_1` — Sump: strike 'evil sun god' from About.xml and four def comments (no god is evil)
- `SUMP_TAR_BEAST_BUILD_1` — Sump: the tar beast, full station-eater (RM_TarBeast replaces the Thrumbo placeholder)
- `SUMP_KETHREL_BUILD_1` — Sump: the kethrel, scrap-armoured hydrocarbon animal with four static armour stages
- `SUMP_CAPSTAN_TURRET_BUILD_1` — Sump: the capstan turret, a turret on Melee Animation's lasso pull, learned at the Sump
- `LASSO_CHERRYPICKER_REMOVAL_1` — Remove lassos: Cherry Picker cut AM_LassoCloth + Melee Animation lasso spawning off

## Commits

```
46dc9fafe ledger: FOUNDRY northstar events; MOTION_FRAMES prose to closed/
b1ef1acc1 Sump tar rites: split into the Sinking and Mob'Unloo's Price, map-local offerings, turn-3 card
eca3d0aca publish: second publish before catch-up uses the last-published base; shebang files publish +x
8a2549b7e Northstar pass 3: launch gate refuses a map on missing RimMandrake types; prep composes folded mods; J3/J6 start a world
6598ac41e publish: put files on origin/main without a checkout (plumbing, 3-way, ledger union, race retry)
6daef10b1 Sump turn-2 rulings: tar offering splits into two rites; Empire lull x5; whole group tarred
68608e0a5 Sump turn 1 ticket-out: seven FOUNDRY items, 17 art jobs, tar-offering rite and turn-2 card
846bf5b85 Northstar live pass 2026-10-01 time ledger: where 210 min went, ranked fixes
f5aeeebd2 Northstar: saved bland world (J6), name_colony tool, world_reset by load
c71911f79 Sump: owner's tar-offering rite recorded
372642ebb Sump turn-1 rulings: all to Baroque Biomes, station-eater, capstan turret replaces lassos, kethrel, tar-offering rite
b3b4290c4 northstar pass 2: live results J2/J3/J4 PASS, J1 logs (agent stopped mid-J1)
b677fbc23 modcheck.bland_world: reusable featureless world setup/reset/assert; Watch feeds low colonists
d36aefc78 Sump bedazzle sitting: review, GPT five, rites, draft turn-1 card
6ed7c84bb Close PYRELANDS_BEDAZZLE_SITTING_1 (turn 1 ruled, ticketed, art commissioned)
4ff85e5e0 Pyrelands commission: 8 artpipe jobs (ullai, giant furnace-beast, lightning breaker, Struck Glass ring)
f3074d7fc Pyrelands ticket-out: five FOUNDRY build items, one per ruled slate package
e63e9e47a Pyrelands turn 1: rulings recorded, Struck Glass in register B9, Zizzik cap waived
571847c06 Pyrelands turn-1 rulings: animals+heat, ullai+giant, glass breakers, Struck Glass revised
596735161 Northstar live queue J0-J5 all MEASURED PASS; harness fixes found live
... 70 more: git log --oneline 13921d602..HEAD
```

## Game / bridge / tree state at wrap

- running : NOT RUNNING (tasklist lists no RimWorldWin64); recorded : DOWN
- Bridge: FREE    since 2026-10-02T05:40:53Z

Worktree clean. The shared checkout's `infrastructure/artpipe/pending/` holds the new untracked art jobs (Nightside Ice 22, Lantern Deeps 51, Pyrelands 8, Sump 17), deliberately: the daemon reads them from there.

