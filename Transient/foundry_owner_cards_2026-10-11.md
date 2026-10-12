# FOUNDRY `needs: owner` — question-card drafts (2026-10-11 17:31 PDT)

Source: the 24 blocks in `infrastructure/state/queue/FOUNDRY.md` carrying `needs:    owner`, each read against its
item prose, its ledger history (`rimflow show`), `infrastructure/state/OWNER_DECISIONS.md` (no hits for any of the
24) and `design/RimMandrake/standing_rulings.md`. Result: **3 genuine decisions** (cards below), **11 already
ruled** (clear `needs: owner`), **10 owed looks/listens or agent work** (not a decision).

Card layout follows the `question-card` skill; the asker must stamp the real local time when it is asked and keep
the write-in line.

---

## Card 1 — the five broken holy relics in the start save

*Context that changes the answer:* one of the five ("Strong Rifle") belongs to the religion the player's colony
follows in the start save (the Ascendant Genome); the other four belong to rival factions' religions
(Astropolitan, the Contract / the Balance, the Green Oath). MEASURED from
`CANONICAL_ASHKARR_START_2026-09-12.rws` ideoManager, 2026-10-11.

**Question:** When we remove the weapons mod, five holy relics in the saved world lose the item they point at.
What should replace them?

- **A. Let the game pick a random replacement for each.** Buys: no work at all; it happens on load.
  Costs: the player's own religion may end up revering something random, possibly a non-Star-Wars object.
- **B. We propose five Star Wars items, one per relic, and you approve the list.** Buys: every relic fits the
  setting, the player's included. Costs: one small extra repair step in the save script and five picks for you
  to check.
- **C. Hand-pick only the player's own relic; let the four rival ones roll randomly.** Buys: the one the player
  sees most is right, for one pick. Costs: rival relics (seen in relic-hunt quests) may still be off-setting.
- **D. Delete the five relic entries from those religions.** Buys: nothing left to go wrong. Costs: those
  religions lose a relic, and with it reliquary and relic-hunt content.

**Recommended: B** — five picks is cheap, and a random relic in a frozen shipped world is permanent.

item: SAVE_RELIC_PRECEPTS_REPAIR_VWE_NULLS

---

## Card 2 — the game-health recorder: what stays, what gets built

*Context:* the outside recorder that watches the running game has 12 measurements built and 8 more designed but
not built. All 12 together cost about 0.3% of one CPU core (measured 2026-10-10 on the full mod list).
Table: `design/RimMandrake/game_health_record.md` §Metrics ledger.

**Question:** The game-health recorder is cheap so far. What should we do with its measurements?

- **A. Keep all 12, build none of the other 8 until a real slowdown hunt needs one; judge them again in a
  month.** Buys: no time from you now; the verdict is based on which ones actually got used. Costs: a few
  readings nobody needs keep running meanwhile (near-zero cost).
- **B. Go down the 12 with you now, keep or cut each.** Buys: a lean recorder today. Costs: about ten minutes of
  your time, judging tools before anyone has used them in anger.
- **C. Build the other 8 too, then judge all 20 together.** Buys: the full picture, including frame-time and
  "what do our own mods cost" readings. Costs: several build sessions, and a few of the 8 hook into the game
  itself, which is where cost actually shows up.
- **D. Trim now to the core five (running?, which game, CPU, memory, load milestones).** Buys: smallest possible
  recorder. Costs: loses log-growth and save-size forensics that have already answered questions.

**Recommended: A** — the cost is already negligible, and "earns its keep" can only be judged after use.

item: HEALTH_METRICS_JUDGE_EARN_THEIR_KEEP

---

## Card 3 — turning the borrowed creatures into our own

*Context:* about 218 creature rows in our biomes still borrow from two other people's mods. One (a Star Wars
animal pack, 160 rows) is plain data and cheap to copy over. The other (102 rows) leans on a shared framework we
already keep; its 20 code-carrying creatures were already sorted by your review sheet on 2026-10-09.
Which creatures stay in each biome is decided at that biome's own sitting (evictions are stopped).

**Question:** In what order should we convert the borrowed creatures into our own?

- **A. Copy the whole cheap Star Wars pack over now, then the rest of the other pack; keep/cut stays with each
  biome's sitting.** Buys: the biggest chunk done fast with no sittings from you. Costs: some creatures you later
  cut get converted for nothing (cheap waste).
- **B. Keep/cut every biome first, convert only the survivors.** Buys: no wasted conversions. Costs: roughly 20
  biome sittings with you before the bulk of the work can start.
- **C. Do the harder pack first.** Buys: removes the riskier dependency soonest. Costs: the slow work comes
  first and the cheap win waits.
- **D. One biome at a time, fully converted and ruled, desert first.** Buys: finished, showable biomes one by
  one. Costs: the same packs are reopened twenty times; the overall finish is slowest.

**Recommended: A** — the cheap pack is pure copying, so converting first and cutting later costs less than
holding the work for twenty sittings.

item: DONOR_DEFS_PORT_TO_OURS_1

---

## ALREADY RULED — clear `needs: owner`

| item | the ruling (source, date, his words) | what still genuinely needs him |
|---|---|---|
| `CHILL_AIR_PUMP_1` | FOUNDRY ledger note 2026-10-09T13:23:44Z, question card: keep 300 W / 60 cells, "accepted, still PROVISIONAL" (by card). H1 *is* that judgement | nothing |
| `FORGE_DHUVVOX_SWARM_REMAINDER_1` | Q1: question card 2026-10-08 (ledger note 2026-10-09T05:59:15Z), keep the pawn-as-nodule build, do not convert to Things. Q3: audio ruling 2026-10-03, typed: vanilla sounds until sound work (ledger note 2026-10-04T04:26:14Z says Q3 "is ours now"; the later note calling Q3 unruled is wrong). Q2 asks whether there is a performance problem: nobody has counted dhuvvox, so that is a measurement for an agent, not a choice | nothing |
| `FLOWWORKS_PIT_OCCUPANT_HIDDEN_BY_LIP_1` | Question card 2026-10-09 (FOUNDRY note on `FLOWWORKS_VISUAL_PRINCIPLES_1`, 2026-10-09T13:28:05Z): the near-lip hide is overridden for occupied cells. Built as `FLOWWORKS_PIT_OCCUPANT_LIP_CUT_1`; BENCH verify A1 L2 **pass** 2026-10-11 (`Transient/bench_gss_fw_live_20261011/cut_true.png`) | nothing; this bug is superseded by the fix item |
| `MACRO_GENERATOR_V0_1` | Question card 2026-10-09: its sibling items `MAPGEN_PAINTER_V1_1`, `MAPGEN_GL_SHEET_1` and `MAPGEN_CONVERGENCE_LOOP_1` were closed "Absorbed into MAP_LANDFORM_MUTATORS_DESIGN_1 / BIOME_MAP_GENERATORS_DESIGN_1 (owner card 2026-10-09)". The new design has landforms painted on each tile by hand, which replaces a per-map random chooser. His typed card words are in `infrastructure/state/items/MAP_LANDFORM_MUTATORS_DESIGN_1.md` | nothing here. The round-4 open calls (wind grain, canyon size cap, salt-pan amendment) belong to BENCH's `MAP_LANDFORM_MUTATORS_DESIGN_1` review if they still matter. ⚠️ The card did not name this item, so "absorbed" is my inference from the closed siblings |
| `FASCINATING_WORLD_JUNK_1` | FOUNDRY note 2026-10-09T13:16:44Z, question card 2026-10-09: "appearance now, flavours later"; no roster cards until the junk-reskin curation is ruled | later: the wreck-roster cards, once the reskin curation is done. Nothing now |
| `DROIDWORKS_PRIMITIVE_TIER_1` | FOUNDRY note 2026-10-09T13:12:08Z, question card 2026-10-09: the primitive droid review is "deferred until after the world remake" | a look at the review save, after the remake (already blocked on that) |
| `MINERALS_WHERE_THEY_BELONG_1` | All four design questions ruled: 2026-10-03 cards and typed (ledger note 2026-10-03T23:21:23Z, 2026-10-04T00:06:13Z), 2026-10-09 card (note 2026-10-09T13:09:02Z). Plasteel reversed, typed 2026-10-09: *"Apparently Plasteel is already Star Wars canon … we should not equate it with any other Star Wars material."* | approving the per-biome numbers on `Transient/mineral_numbers_review_2026-10-03.html` (37 rows). That is a numbers review, not a choice |
| `ABYSS_DARK_MUFFLE_ALL_SOUNDS_1` | The Harmony-dependency question was answered by his own typed card note of 2026-10-09 (in the item): *"…all the biomes are being moved into a single Baroque Biome mod that WILL take harmony, right? Then this is moot... right?"* | a joint listening session in the Abyss (sound is never judged solo) |
| `UNROUTABLE_CORD_BUILD_DIVE_THROUGH_WALLS` | BENCH filing 2026-10-10T21:39:23Z: "decision taken by question card 2026-10-10" (cord dives into the wall and re-emerges) | a look at a diving cord in game |
| `GRAFFITI_SIGIL_FRAMES_ART_1` | Forks ruled by question card 2026-10-09 (`GRAFFITI_PUNK_IDEOLIGION_SCOPE_1`; `design/RM_GRAFFITI_SCOPE_WIDENING.md` §7): wildstyle + stencil, asemic only | a look, folded into `GRAFFITI_PUNK_ART_REVIEW_1` |
| `COMPANION_PROFILE_ENFORCE_SAFE_BY_DEFAULT` | FOUNDRY note 2026-10-10T20:09:54Z: the owner's 2026-10-10 card rulings replace the title (by card): campaign is the default and is not read-only; it refuses only the debug, test-only, heavy-diagnostic and quiet-world families, with a 10% recorder budget | nothing. A1/A2 are live checks an agent with the bridge can run |

## Not a decision (an owed look, or work an agent can do)

| item | why it is not a card |
|---|---|
| `ART_TEXTURE_GAPS_FOLLOWUP_1` | art picks only: Braskeen redo variant, Ismerrow variant A |
| `CANON_CREATURE_REGEN_1` | grading the art on the wave-4 sheet (`Transient/canon_regen_wave4_2026-09-23/sheet.html`) |
| `STONEBACK_BOKKA_ART_STANDARD_1` | a yes/no on swapping in art that is already made (`Transient/bokka_old_vs_new_20261010.png`) |
| `STARWARS_JUNK_RESKIN_1` | art curation on `Transient/junk_reskin_review_2026-10-09/` |
| `GRAFFITI_PUNK_ART_REVIEW_1` | an in-game look at the punk set, glyphs and frames |
| `ICON_OUTLINE_REPAINT_1` | per-sheet install yes/no on the icon contact sheets (`Transient/OWNER_MORNING_LOOK_20261010.md`) |
| `NORTHSTAR_ISHKO_PILOT_1` | A4 is an *optional* owner layer; the pilot reached GREEN-MIN without it. Can close without him |
| `TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS` | A1/A2 are a full-list live session an agent can run; nothing of his |
| `BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD` | A1/A2 are reload checks an agent with the bridge can run |
| `AWARENESS_GENPAWN_TAME_ARM_BEFORE_USE` | A1 is a status read after world gen; agent work |
