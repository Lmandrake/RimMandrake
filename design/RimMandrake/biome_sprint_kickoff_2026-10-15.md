# Biome sprint kickoff packet — Cauldron, Contagion, LeaningScrub (BENCH, 2026-10-15)

**Owner, by card 2026-10-15 ~16:45 PDT:** *"Which shape should the next sprint take? → Three biomes deep"*. That is
option 2 of `design/RimMandrake/next_sprint_plan_2026-10-15.md`. Item: `BIOME_SPRINT_PROVE_SCRUB_SETS_PACE`. The plan's
exit criterion: a per-biome criteria list he approves at sprint start (S0), and his sign-off cites that list.

This packet exists so that sitting S0 is short. It holds:

- §1, a draft criteria list for each biome, for him to approve, edit or cut;
- §2, the design calls blocking the three mechanics builds, as question cards;
- §3, the LeaningScrub art redo;
- §4, the day-by-day schedule with his sittings marked.

Every fact was re-measured on 2026-10-15 from the item files, the ledger, the design sheets, each biome's walk file
(`design/validation_walks/RimMandrake/<Biome>.md`, which holds its `## north star`) and the 2026-10-08 modcheck records
(`Transient/modcheck/<Biome>_20261008*.json`). Those runs used fresh maps at pre-pilot HEADs: they show how far each suite
reaches, not today's state.

**Said to him in these words (plan §2.2):** wherever he chooses "defer" below, "done" means *done against the scope he
froze at S0*, not done with every mechanic he designed.

---

## 0. Corrections to the plan found while building this packet

| plan said | measured |
|---|---|
| Cauldron blocked on "falter-tell foreknowledge" | **Settled by the build, not by a question.** `src/RimMandrake/Cauldron/Source/RM_CauldronVents.cs` uses the weather-transition ramp as the tell and needs no foreknowledge. `vents.vent_falter_precedes_bloom` PASSed live on 2026-10-08. Dropped from the cards. |
| Cauldron: 4 overlay textures missing | **7.** The 2 assay-fleck overlays (`Things/Plant/RM_AssayFlecks/Flecks_{Light,Heavy}`), plus 5 dew variants `Things/Plant/RM_Dewfall/<def>_dew` for CrystalFlower, BloodBouquet, RedBugloss, KeeningCordax and GiantToxicFlower. The lint does not count the dew variants. |
| Contagion blocked on the "grown-limbs owner sheet" | **Answered.** At the bedazzle sitting on 2026-09-27 he said *"Approved, this looks great!"*. All five limbs were built to the sheet's recommendations (`CONTAGION_GROWN_LIMBS_BUILD_1` and `_REST_1` are closed). What remains is a live proof and placeholder art for three limbs, which is build work. His look at the limbs happens in the S2 review save, not on a card. |
| Contagion blocked on the "rattle render seam" | It is engineering, not design. It stays a scope card (Q6) only because it is polish that could be cut. |
| LeaningScrub blocked on the "calling-pyre ritual" | **The concept is ruled.** By card on 2026-10-01 it was merged with the controlled waking: the calling-pyre is the controlled waking's Scrub form (`design/Jawa/biome_rites_pass_2026-10-01.md` §7.1). Only the precept shape and the build size are open (Q7). |
| "Patch-added RM_ cast" for every biome | Contagion has no `WildAnimals_Contagion.xml`: its whole roster is inline in `RM_Contagion.xml`. LeaningScrub's patch-added cast (about 38 rows in `src/RimUtinni/UtinniPatches/Patches/WildAnimals_LeaningScrub.xml`) is all `RSW_`, not `RM_`. The manifests list the real files. |
| north-star line counts 7 / 8 / 8 | Those are the must-show lines. Each biome also has 2 cannot-show lines. In all three, `### the experience` is "(not yet dictated)". |

---

## 1. Draft criteria lists (for S0 approval)

**Shared lines.** These apply to all three biomes, from plan §3 "Exit criterion", and are not repeated below. All hold at
ONE HEAD on the `biomes_sprint` tier, each recorded by `rimflow verify`:

- **M1** `northstar_driver run --mod <Biome> --plan src/RimMandrake/<Biome>/northstar_plan.py` on the biome's registered
  saved site gives 0 FAIL and 0 UNMEASURED. Its row count equals the manifest's, so the run is not EMPTY. INFERRED rows
  are allowed only where listed below.
- **M2** Every manifest roster def's texture resolves offline against the deployed composite, with zero missing.
- **M3** `modcheck floor --all` reads "bar met" with bars > 0.
- **M4** Every manifest item is done, or deferred by a manifest revision he approved.
- **M5** `run_selftests.py --only` passes on the changed files, and `code_review_status.py check` reads CLEAN on them,
  marked by a reviewer who is not the builder.
- **M6** The pilot guards (GSS, FlowWorks, Pyrelands) are green at matching inputs.
- **O1** He dictates `### the experience` (his words; agents never fill it).
- **O2** He accepts the visual bars against the review save.
- **O3** His sign-off cites the manifest hash.

All three suites keep their rows in `validation.py`; `northstar_plan.py` is a thin `USE_SUITE=True` wrapper.

**Bars are written as state-independent prose**, so they can go straight into each `## north star` once he edits them.
Each one says what a map shows, never what is built today.

### 1.1 Cauldron

**Experience (from `design/Jawa/worldbuilding/biomes/cauldron.md` §1, for him to replace with his own words):** a low,
wet-black forest in permanent dusk, over ground that breathes cold, metal-rich gas; trees weep metal; the water and meat
are poison but prized.

**Machine rows.** The suite has 63 components in 15 chains: load, weather, settings, items, acid, fauna, suush, flora,
yield, bloom, water, fire, vents and log. The 2026-10-08 result was 58 PASS / 1 FAIL / 4 UNMEASURED.

| row | what closes it | kind of fix |
|---|---|---|
| `yield.yield_factor_scales` FAIL, plus `yield_toggle_off` UNMEASURED | The Harvest order is now sent with queue=False (`09d32ba8f`, proven offline only); `CAULDRON_YIELD_LIVE_RERUN_1` owes a live rerun | harness |
| `suush.suush_detonates_when_shot` | Move the control suush out of blast reach | site spacing |
| `bloom.bloom_spares_natives` | Run on a real `RM_Cauldron` site with a native and a non-native herbivore | the saved site |
| `water.water_poison_toggle_off` | Pen the test vexxiss in the pond so it cannot wander off | site |
| New, cheap rows (in only if he keeps the visuals) | Dewfall bead count; dew swap and reverse; fleck overlay draw on a graded tree; footprint ledger read | new rows |
| New rows if Q1 is built | Vent gas ignites and burns into toxic smoke; the vexxiss attacks an igniter | new rows |

Proposed INFERRED rows: none.

**Visual bars (draft):**

- *Must show:*
  - A noon map reads as a dim, even, shadowless dusk forest, never full daylight.
  - Under a vent bloom the air visibly thickens with a coloured haze.
  - Martyr and thornwood read as sweating metal, unlike vanilla trees. A mature tree's assay grade shows as flecks.
  - Under dewfall, beads form and the accent plants change to their dew look, then change back.
  - The two soils read as dark, gassy ground, and the rich one differs visibly from the plain one.
  - The four natives read as four different animals.
  - The suush floats above the ground.
  - A vexxiss leaves footprints.
- *Cannot show:*
  - A bright day.
  - Rain or snow.
  - A magenta square.

**Art set:**

- The 7 missing textures (2 fleck overlays and 5 dew variants).
- The bedazzle sheet's open picks from 2026-09-29, still unverified as actioned:
  - Eskith "improve" (five eyes, so the side profile shows three);
  - Vexxiss "improve" (as colourful as the vents);
  - Seismograph "regen" (only if Q2 keeps it).
- *Rider for the S1 art sheet:* which accent plants get dew variants. The XML default of five stands until he picks.

**Mechanics.**

- *In scope, built:* the four weathers; vents with the falter tell; the bloom metal-load hediff; vexxiss vent-drinking,
  fire warden and water poisoning; metal yield and assay; nettle gardens; vexxith acid immunity; the dewfall, fleck and
  footprint visuals; 27 settings.
- *Decided at S0:* flammable vent gas (Q1), and the Filter-Works / ruin kit / seismograph / Oomo shrine set (Q2).
- *Out of scope:* sound, by his 2026-10-03 ruling (vanilla sounds).

### 1.2 Contagion

**Experience (sheet `design/Jawa/worldbuilding/biomes/the_contagion.md`):** *"A red valley under a storm that never
stops, where the clear sky is the thing to fear."*

**Machine rows.** The suite has 59 rows in 12 chains: defs, settings, log, repulsor_clear, spawner, site, burn_forced,
burn_natural, uv, coalescence and genome. The 2026-10-08 result was 52 PASS / 0 FAIL / 7 UNMEASURED.

| row | what closes it | kind of fix |
|---|---|---|
| `defs.biome_roster_animals` | `get_defs` cannot read the non-public `wildAnimals` field. Promote the static XML roster check to the row, or add a bridge read | harness |
| `repulsor_clear.site_ready_baseline` and the 3 rows downstream of it; `site.retile_to_contagion` | All five share one cause. The suite wants a stock-biome start, but a saved Contagion site is already Contagion. Run the off-Contagion arm on the calm site, and keep the retile control there | harness + site |
| `genome.extraction_surgery_yields_sample` | Put the patient in a bed and make the bill giver usable | fixture |
| New rows | Bloom/Burn tells by a state read of `RM_MapComponent_ContagionSky`; a Sunbeam firing fixture; limb install, and limb removal spawning an Unfinished | new rows |
| New rows if built | The arrest (Q3); mulch (Q4); trader and quest stock (Q5) | new rows |

Proposed INFERRED row, to be pre-approved: natural Coalescence formation in a long Bloom. It is a statistical event,
scored from the forced-formation rows plus the Bloom-duration timer.

**Visual bars (draft):**

- *Must show:*
  - A map under its Bloom reads as a red, sick, storm-roofed sky, not an ordinary overcast.
  - At a Burn the light turns to a near-white shaft, and the gawpsacks and rattlegropes give their tells before it.
  - A powered Cloud Repulsor clears the sky around it while the rest stays under the Bloom.
  - The Sunbeam reads as a beam of light striking its target.
  - Meatvine, toothmoss, eyebark and wombpod read as grown flesh at play zoom.
  - The Unfinished read as half-made, wrong creatures, each different.
  - The Coalescence reads as one living mass, with three stages you can tell apart.
  - A colonist with a Monstrous grown limb looks different from one with a natural arm, in all four facings.
- *Cannot show:*
  - A recoloured vanilla forest.
  - A magenta square.

**Art set:**

- Placeholder limb art to replace:
  - Eyeburst (tinted vanilla);
  - Caudal Spring (Anomaly's TentacleLimbA);
  - Bellows (no render node).
- Confirm the cast-review redo wave landed. On 2026-09-29: 40 keep, 6 improve, 1 regen; 10 jobs queued, unverified since.
- The half-transformed tree, still owed by the sheet.
- The tell animation, only if Q6 builds it.
- *Rider for the S1 art sheet:* one row for the donor/port overlap. `AA_OcularJelly` shares the roster with
  `RM_Gawpsack`, and `AA_InfectedAerofleet` with `RM_Blisterfloat`.

**Mechanics.**

- *In scope, built:*
  - the Burn and the Bloom, with their tells;
  - `RM_BurnDose`;
  - the Coalescence (3 stages, Unfinished emission, Burn collapse into Monstrous samples);
  - the Cloud Repulsor and its ship variant;
  - the Sunbeam as a weapon;
  - the genome loop and the 5 grown limbs;
  - the Unfinished spawner;
  - Draftprints and the Helix contract;
  - 11 settings.
- *Decided at S0:* the arrest (Q3), mulch (Q4), trade and quest stock (Q5), and the drawn tells (Q6).
- *Proposed deferral:* the Dive and Bodyprints, parts 2 and 3 of `CONTAGION_GPT_ENRICHMENT_1`, which were never on the
  build list.

### 1.3 LeaningScrub

**Experience (sheet `design/Jawa/worldbuilding/biomes/arid_shrubland.md`):** a flat, wind-scoured fuzz plain under a low
sun. A knee-high canopy leans one way across the whole map, and the wind never stops except in the Stall.

**Machine rows.** The 2026-10-08 suite had 68 components in 17 chains: defs, patches, settings, fauna, flora, stall,
gale, lash, smother, dripping, crown, bloom, stamp, forms, four_forms, sweetline and log. The result was 50 PASS /
1 FAIL / 17 UNMEASURED. The suite has grown since (four more venomvine forms, sweetline guardians and felt), so the
manifest's row count comes from a fresh run on day 2.

| row | what closes it | kind of fix |
|---|---|---|
| `bloom.bloom_toggle_off_quiet` FAIL, plus the 2 bloom rows downstream of it | With `runwayBloomEnabled` OFF, Flee jobs still appeared. Decide whether this is a mod defect or a harness fault (other flee sources) before changing anything | diagnose |
| 12 `forms.*` rows | The live DLL exposes `ProofForm(String)`, and the harness calls a 2-parameter version. Fix the signature on one side | harness/DLL |
| `stamp.*` (2) | No loaded creature carried `RM_FireStamperExtension` on `acc_biomes-15`. `biomes_sprint` loads UtinniPatches and SWBestiary, which should clear this | tier |
| `dripping.dripping_survives_harvest` | The harvest never finished within 1200 ticks. Give the window more time, or pre-position the pawn | harness |
| New, needing a Scrub site | The Lean: the heading locks per map, animals flee upwind, fire biases downwind. `LEANING_SCRUB_LEAN_SITE_1` is cited in code but missing from the ledger; it gets filed | new rows |
| New rows if built | Calling-pyre availability (Q7); vaporator placement and the wake capping and healing (Q8); ripple concealment by weather (Q9); injection set-pieces present on a generated map (Q10) | new rows |

Proposed INFERRED row, to be pre-approved: downwind fire bias, scored from a compressed run plus the heading-lock row.

**Visual bars (draft):**

- *Must show:*
  - The ground reads as one soft fuzz carpet, leaning the same way across the map, dotted with near-black venomvine
    islands, never vanilla grass.
  - Under the Gale the map reads as driven: dust and fuzz moving.
  - Under the Stall, small animals hold still while big ones move.
  - Each venomvine form can be told apart from the others at play zoom.
  - A sweetline tree stands out as a named landmark, taller than the scrub.
  - The wild cast reads as distinct animals in one line-up.
  - A runway bloom sends dustflutters up in a burst. This is checked by a flight-state read only; flight is never
    filmed or live-tested without him.
- *Cannot show:*
  - A windless map.
  - Leans in mixed directions.
  - A donor-art stand-in.
  - A magenta square.

**Art set:** see §3.

**Mechanics.**

- *In scope, built:* the Stall and Gale calendar; the Lean v1; smother-craft; the twitcher lash; fire-stamping
  thunderstep giants; the soundscape on vanilla sounds; the dripping, crown, bloom and sweetline systems; 11 venomvine
  forms; sweetline visitors; vissler-arm scavengers.
- *Decided at S0:* the calling-pyre ritual (Q7), the vaporator and V-blight (Q8), the ripple (Q9), and the inhabited
  set-pieces (Q10).
- *Agent default, not asked:* no Lean heading readout. The lean shows in the plants themselves (the first bar), and his
  trim law reads *"Too much focus on constant advanced warning... Players arent that into it."*

**Venomvine sitting.** `LEANINGSCRUB_VENOMVINE_SITTING_1` is his own deferred sitting (*"Venomvine is a mechanic as well
as graphics... during Bench settings"*, 2026-10-08). It needs him and the game on a Scrub map, with the run sheet at
`Transient/venomvine_sitting_runsheet_2026-10-09.md`. It is folded into the S2 LeaningScrub review save, so it costs no
extra sitting.

---

## 2. Design calls blocking the mechanics builds (card-ready)

**Ten cards.** These were verified against the ledger (no owner-said, by-card or per-ruling event answers any of them),
`design/RimMandrake/standing_rulings.md`, `biome_rulings.md` and the design sheets.

**Dropped as already settled; never asked again:**

- **Cauldron falter-tell foreknowledge** — settled by the build (see §0).
- **Contagion grown limbs** — *"Approved, this looks great!"* (2026-09-27); built.
- **Calling-pyre concept** — merged with the controlled waking by card on 2026-10-01.
- **Sound for all three biomes** — vanilla sounds, by his ruling of 2026-10-03.
- **The Zizzik rite cap** — *"Just leave them all for now"* (2026-10-02).

Each card has a "leave it out of this sprint" choice, so an unanswered card never blocks the other biomes.

### Cauldron

**Q1. The Cauldron's vent gas is supposed to catch fire and burn into poison smoke. How should we make that work?**

The game's gas system has a fixed list of gases, and none of them burns. Everything about igniting vents hangs on this:
the gas tap, the toxic-smoke fire, and the vexxiss attacking whoever lights it.

- **(A) Fake it with a burnable haze — recommended.** Leaking vents lay a thin "vent haze" on the ground. Fire touching
  it flashes and releases the game's own toxic gas. It is small and safe and looks right in play, but it is not a real
  gas cloud that drifts.
- **(B) Teach the game a new burnable gas.** This is the true version, where the gas drifts, spreads and burns. It needs
  deep engine patching, is the riskiest build of the sprint, and could break other mods' gases.
- **(C) Vents leak the game's existing toxic gas, and fire does nothing special.** This is the cheapest. It loses the
  "should be stopped / burns" drama he ruled on 2026-09-28.
- **(D) Leave fire out of this sprint.** The vents ship as they are (falter, bloom, exposure). "Done" then excludes
  burning gas.

**Q2. The Cauldron design also has a Filter-Works (refine vent gas into reagents), ruin set-pieces, a seismograph and
an Oomo shrine. None is built. Which belong in this sprint?**

- **(A) Leave all four out of this sprint and file them — recommended.** This keeps the sprint to what exists plus Q1.
  The trade-off is that the "refine it to valuable reagents" payoff waits.
- **(B) Build the Filter-Works only.** It gives the payoff for stopping the gas. It needs new FlowWorks liquids, a
  building and cartridges: about two agent-days, and one more look from him.
- **(C) Build all four.** This is the whole sheet. It roughly doubles Cauldron's build, and the seismograph art needs
  regenerating (his 2026-09-29 note: "weird, replace").

### Contagion

**Q3. You ruled the Sunbeam "arrests" the Contagion's corruption: irradiate the patient and it stops getting worse. But
no corruption condition exists yet for it to stop. What should we do?**

- **(A) Add a slow "Contagion-touched" condition, which the Sunbeam freezes — recommended.**
  - Colonists exposed in the Bloom pick up a condition that slowly worsens and brings bad changes at set points.
  - A Sunbeam treatment stops it from getting any worse, and what already changed stays.
  - It fits your ruling exactly. It adds a new threat and about a day of building and testing.
- **(B) Leave the arrest out of this sprint.** The Sunbeam stays a weapon, strong against natives. Your ruled "cure"
  waits, and "done" excludes it.
- **(C) Reuse an existing mutation condition from the base game or Anomaly.** This is quicker. It risks breaking the
  rule that a colonist never just turns into a limb, and it may not read as the Contagion's own.

**Q4. You ruled Contagion mulch "the best fertilizer on Ash'karr": sunned, it is super-compost; un-sunned, it infects
your field. Nothing makes mulch yet. How much should we build?**

- **(A) A mulch item with the two states, sunned and raw — recommended.**
  - Dead Coalescences and Unfinished drop it.
  - Laying it out under a Burn turns it into super-compost.
  - Raw mulch used as fertilizer spreads ocular grass into the field.
  - About a day's build. It keeps the bargain you ruled.
- **(B) A plain fertilizer item only, with no infection and no sunning.** Half a day. It loses the risk that makes it
  interesting.
- **(C) Leave mulch out of this sprint.** The Coalescence still drops Monstrous samples, so the loop has a reward.

**Q5. You ruled the Cloud Repulsor and the Sunbeam "purchasable and quest-given". Who should sell them?**

- **(A) Quest rewards, plus a Helix trader who visits — recommended.** They appear only where the Contagion's story is,
  so they don't leak into unrelated games. Agents first have to find whether a Helix trader exists or must be added.
- **(B) Add them to an existing trader type, such as the exotic-goods trader.** It is simplest and they show up more
  often. They would also appear in colonies nowhere near the Contagion.
- **(C) Quest rewards only for now.** The quest wiring is mostly there (the Draftprint contract works). Players can't
  buy them, which contradicts "purchasable" until a later sprint.

**Q6. Before a Burn, the gawpsacks are meant to visibly sink and the rattlegropes to visibly shake. Today they puff and
rattle by sound only. Should we build the visible motion?**

- **(A) Build the visible sink and shake — recommended.** The warning becomes something you see, which matches your
  ruling. It needs a drawing hook in the engine, about a day, and an in-game look from you in the review save.
- **(B) Keep the sound-and-puff tell only.** No new work. Players who don't notice sound get no warning before the Burn.

### LeaningScrub

**Q7. The calling-pyre is the Scrub's form of the controlled waking (ruled 2026-10-01). What it should be as a
ritual isn't decided. How big should it be this sprint?**

- **(A) One ritual, with no new beliefs — recommended.** The colony lights its own dry fuzz field when thunderstep herds
  and enemies are near, and the giants come stamping. It reuses the fire-stamp behaviour that is already built. The
  belief hooks ("forbidden", "last rite", "venerated") wait.
- **(B) The ritual plus all three belief variants.** This is the full design. It adds ideology content and more choices
  for you, and probably two more days.
- **(C) Leave the ritual out of this sprint.** The biome's link to its god is then missing from "done", which your
  2026-09-29 slate admitted as a must.

**Q8. The vaporator, a moisture farm that dries a V-shaped scar downwind, is the Scrub's planned economy. Nothing of it
is built: no building, no look, no study source. What should we build?**

- **(A) A plain vaporator only, with no scar — recommended for this sprint.** Players learn it by studying a dead
  farmstead. It gives water and a little food. The look comes from one art-sheet round with you. It skips the
  ground-drying scar, which is the expensive part.
- **(B) The whole thing.** The vaporator, the drying scar that heals when you cap it, and animals raiding vaporators.
  This is the richest version and the largest build of the sprint, about three days plus terrain art.
- **(C) Leave it out of this sprint.** The Scrub then ships without its signature economy.

**Q9. The "ripple" lets small creatures hide under the fuzz: they can't be targeted from far away, the Gale doubles it,
and moving in the Stall gives them away. Should it come in, and should hiding show?**

- **(A) Hiding with a faint shimmer over hidden creatures — recommended.** The shimmer is how the mechanic looks, not a
  warning instrument, so it should sit within your "no constant advance warning" rule. About a day.
- **(B) Hiding with no visible sign.** It costs the same. Missed shots would look like bad luck rather than cover.
- **(C) Leave the ripple out of this sprint.** The stallhawk-rise and stall-exposure ideas that build on it also wait.

**Q10. The design scatters set-pieces across Scrub maps: dead farmsteads, smothered fields, venomvine homesteads,
living camps. None is placed yet. Which kinds should we build?**

- **(A) Ruins only: a dead farmstead, a smother-claimed field and a hedge homestead — recommended.** It reuses the
  set-piece tooling. The farmstead doubles as the vaporator's study source (Q8). About a day.
- **(B) Ruins plus living camps.** The map feels inhabited. It needs a faction choice and AI behaviour, and roughly
  doubles the work.
- **(C) Leave set-pieces out of this sprint.**

### Process cards (from plan §3 "Questions for S0", still open)

**Q11. Who builds?**

- **(A) BENCH owns everything, as in the pilot — recommended for one-HEAD discipline.**
- **(B) FOUNDRY builds while BENCH runs the live rounds and integrates.** This is faster in parallel, at the cost of
  the swept-files risk (plan X3).

**Q12. Can you answer each packet within about a day?**

- **(A) Yes, one day.**
- **(B) Two days.**
- **(C) No fixed window; ping me.**

His response time sets the calendar (plan §3, item 8).

---

## 3. LeaningScrub art redo

**Most of the art already exists; do not queue new renders before checking the list below.** Measured on 2026-10-15
with `artpipe_state.py find leaningscrub_` and the sheet's decisions file.

**What exists**

- **Renders.** 68 of the 69 filed redo jobs have renders on disk, under `D:\Luke\dev\_artpipe\_artsrc\leaningscrub_<id>_*\`.
  - The job file is `Transient/biome_ffar/leaningscrub_redo_jobs_2026-10-05.json`. Its 69 jobs make the item's "119"
    stale.
  - Only `leaningscrub_sketto_v2` is missing.
  - Plant variants with renders: the b/c (or a/b/c) variants of brambles, aridgrass, creepstern, crimsoncushion, dervish,
    six venomvine forms, cruststar, fuzz, grellbush, grellspine, pillowmoss, tanglefuzz, whipfuzz, wild healroot and wild
    nysyllin.
  - About 26 creature renders also exist.
- **The sheet already shows them.** `Transient/biome_ffar/leaningscrub_sheet_2026-10-05.html` was rebuilt on 2026-10-14 with
  70 render names. Its decisions file, `leaningscrub_sheet_2026-10-05.decisions.json`, has 86 rows. His rulings are copied
  to `infrastructure/state/art_rulings/2026-10-08_leaningscrub_sheet_2026-10-05.decisions.json`, and 63 rulings were
  ledgered on 2026-10-08.
- **Installed.** 99 PNGs in `src/RimMandrake/LeaningScrub/Textures`. Many of the cast live in SWBestiary and the patch
  mods instead; the 2026-10-05 pass installed Fuzz B, Gorg, Eopie, Iriaz, Mudhorn, Ronto, Skalder, Worrt and others.
- **Texture check.** No broken texPath: 84 texPaths were checked against local PNGs, and the 8 unmatched ones are
  vanilla Core paths.

**What is owed, net of what exists**

1. **His picks on the new variant renders.** Fuzz, Tanglefuzz, Whipfuzz, WildHealroot (a/b/c), Nysyllin_Wild (a/b/c),
   Brambles, CreepStern, and the redo creatures still marked redo: Chikka, Convor, Kybuck, ScrapNestBird. Once picked,
   they install as `<Name>_<letter>.png` variants through `art.py enact`.
2. **Port three donor plants to owned `RM_` defs.** These are pure agent work; his picks are already made.
   - `Plant_Brambles` (pick B);
   - `RG_Plant_CreepStern` (pick B);
   - `RSW_Durrok` (pick B; it shares the `AA_Wildpawn` path, and its description must be rewritten to match the picture).
3. **Re-picks.**
   - `RM_VenomvineThicket` B was refused because the picture was purged by his own mark. It is held for the venomvine
     sitting.
   - `RSW_Nuna`'s pick F has no ruling id, so it is re-confirmed on the sheet (the current decision is A).
4. **Venomvine.** His card of 2026-10-09 already decided that the owned venomvine renders replace the thicket copy on
   the other venomvine plants. The art ledger cannot install over a kept sha on a card path
   (`Transient/belt_art_enact_20261009.md`). **This is not a new question.** It needs one typed sentence from him at S0
   (recorded with `--owner-said`), or the S2 venomvine sitting. Quench and Rearing ("STOP USING THIS GRAPHIC AND MAKE
   VENOMVINE") get new renders only once the sitting confirms those forms stay.
5. **Dustflutter numbers.** The 0.3-cell size is done. "In great numbers" still needs his call on group size (proposal:
   8-20), density and ecosystem weight. This is a rider on the S1 sheet, as one number row.
6. **ScrapNestBird flying frames.** His note was "Make flying frames". No frame job is filed; today it borrows
   Whisperbird's flip-book. File a whole-body directional flip-book job. It is verified by a `Pawn_FlightTracker` state
   read only. Any visual check of flight is a joint session at S2, never unattended.
7. **Small items.**
   - Run Sketto v2 north/south.
   - The Lothcat north/south replacements (jobs done) and the Eopie and Scurrier male replacements (queued) unblock the
     8 remaining purges from `Transient/leaningscrub_conflict17_2026-10-08.md`.
   - Check that the `RSW_Kreetle` 0.3-cell drawSize change landed.
   - Check whether the `RSW_TunnelSnake` row is stale: `RM_TunnelSnake` already exists with 3 PNGs.

**Fastest route to his look (about 10-15 owner minutes, at S1)**

1. Run `refresh_sheets.py --dry-run --only leaningscrub`. The sheet was rebuilt on 10-14, so this is likely a no-op. If
   it changed, refresh and run `remap_decisions.py`.
2. Add the riders as rows on the same page: the Cauldron and Contagion art, the Dustflutter numbers, and Nuna.
3. Gate with `scaled_review_gate.py check`, serve with `serve_gated.py`, and send him the URL plus the full path. He only
   needs to look at the rows not yet picked; the rest keep his earlier picks.
4. When he says done, run `art.py enact <decisions.json>` as a dry run, then `--apply`, with `--hold` on the venomvine
   rows.
5. In parallel, needing no new art: the three donor ports, the ScrapNestBird frame jobs, and Sketto v2.

A second round (S1b) happens only for rows he sends back.

---

## 4. Sprint schedule

Owner sittings are marked **[S#]**. Agent days assume one BENCH builder per mod (plan X3). Each "his reply" is one
response interval; the calendar below assumes he replies within a day (Q12).

| day | agents | owner |
|---|---|---|
| **D0 (Fri 10-16)** | Send this packet. File `LEANING_SCRUB_LEAN_SITE_1`. Close the pilot's C5 once the nightly selftests are green. Tooling slice, at most one agent-day: add the `biomes_sprint` tier to `modset_builder.py`; add the preflight (companion-profile expiry, tier membership); add biome sites to `test_site_saves.py` (`northstar_site.py` builder, then clean, save and register), proven on Cauldron first. | **[S0] about 45-60 min, asynchronous or one sitting.** Answer Q1-Q12. Edit or approve the three criteria lists in §1. Dictate `### the experience` for each biome (one or two sentences; it can wait until S2). Sign off the pilot (C6). One typed sentence restating his 2026-10-09 venomvine-art card, needed because the art ledger cannot install over a kept sha on a card path (§3 item 4). |
| **D1** | Freeze the three acceptance manifests from his S0 answers and record their hashes on the ledger. Build the Cauldron and Contagion sites. One live round: the current suites at one HEAD on the saved sites. Harness fixes: Contagion's off-biome arm and its surgery fixture; Cauldron's suush spacing, vexxiss pen and yield rerun. Build the LeaningScrub art sheet (§3). | **[S1] about 30-45 min, asynchronous.** The LeaningScrub art sheet, with riders: Cauldron's 7 textures and dew-variant pick; Contagion's three limb placeholders and the donor/port row; Dustflutter numbers; the vaporator look if Q8 is A or B. |
| **D2** | Mechanics builds per S0, in parallel, one builder per mod: Cauldron Q1-Q2; Contagion Q3-Q6. LeaningScrub harness: the `ProofForm` signature; diagnose the bloom toggle; Scrub site; a fresh run for the row count. Install the art he picked. A separate reviewer marks files CLEAN. | — |
| **D3** | LeaningScrub builds per S0 (Q7-Q10) and the Lean rows. Second live round for Cauldron and Contagion; target 0/0. Second art round if his S1 asked for re-picks. | **[S1b] about 15-30 min, only if needed:** the second art round. |
| **D4** | Build the three review saves, one per biome, each with a key sheet (Pyrelands pattern: `RM_pyre_review_20261015`). Each holds every visual bar plus the venomvine forms and the grown limbs, staged at stations. Live round for LeaningScrub. | — |
| **D5** | Fix whatever his S2 rejects. Final one-HEAD round for all three, plus the pilot guards (M6). Run `rimflow verify` on each line. | **[S2] about 60-90 min, game up, one sitting** (or two half-sittings). Walk the three review saves. Accept or reject each bar (O2). Hold the venomvine sitting at the Scrub stations. Any flyer look happens here, with him present. |
| **D6-D7 (buffer)** | Redo anything S2 rejected, then rerun only the suites whose inputs changed (plan X4). | **[S3] about 10 min:** the sign-off card citing the three manifest hashes (O3). |

**Owner total:** about 3-3.5 h active, in 4-5 sittings, matching plan Option 2. The critical path is S0, then the
LeaningScrub art loop (S1/S1b), then S2.

**If an answer is late:** the agents carry on with the other biomes and the harness work, which need no answers.
Silence is never approval.
