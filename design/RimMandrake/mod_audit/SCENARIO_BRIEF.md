# Scenario brief for the mod audit

_For assessor agents grading every mod on the full list (550 active at the 2026-10-10 cold load
[`Transient/foundry_fulllist_deploy_20261010.md`, 14:00 entry]) as KEEP / KEEP-TEMPORARILY-THEN-
PHASE-OUT / REPLACE-NOW-WITH-OUR-OWN / ELIMINATE-COMPLETELY. Written 2026-10-10. Every claim
carries its source in brackets; paths are repo-relative to `/home/mandrake/rm/foundry`. Where a
source is older than a later owner ruling, §5 says so rather than resolving it._

## 1. Identity

**What the game is.** *Flight of the Utinni*: RimWorld 1.6 with all DLC, a Jawa scavenger clan on
the desert world **Ash'karr, "The Sundered"**, who steal and wake an ancient Rakatan ship (born
*Kolyska*, painted *The Utinni*) out of a Hutt discard yard. "Getting it off the ground is the
campaign." Feel: *"Firefly / Battlestar Galactica / Oregon-Trail-in-space / a scientific expedition
crossing an unexplored world."* [`design/Jawa/reconciled_lore/01_campaign.md` §Premise, §Names of
record]. (`design/Jawa/concept.md` is marked SUPERSEDED by that file [its line 1].)

**The loop.** Land, camp, explore, gather, improve the ship, pressure rises, **decide what to leave
behind**, launch, repeat. The colony lives aboard; crew ~3–8; no tile is self-sufficient. Motion is
forced by the Empire (orbital pursuer), the Hutt ledger and Ta'Baa's theological clock; fuel has
many redundant paths [`01_campaign.md` §The loop, §The three pressures, §Fuel is life].

**Who the player is.** Six fixed `MandrakeJawa` founders; fixed pawns, ship and map; the start is
HARD; flight hardware ships unbuilt [`01_campaign.md` §v1 start]. The world is **one hand-made
frozen planet delivered as a savegame** [`CLAUDE.md` §"There is no worldgen feature"].

**Pillars.** Anti-exponential (the gravship and its industry are the only scalable trees); no arms
race (qualitative danger, never stat inflation); the 7-question test; "Mod count is not the
constraint — the capability ceiling is", with curation by Cherry Picker trimming, not uninstalling
[`01_campaign.md` §The pillars].

**Tone.** Star Wars *style*; invented exotic names are not IP and are franchise-free [`CLAUDE.md`
§"Star Wars style naming is NOT Star Wars IP"; `design/RimMandrake/biome_mod_architecture.md` §7 Q11a].

**The three tiers decide a mod's home** [`design/NAMING_SCHEME_PLAN.md` §1–2; owner 2026-08-30]:

| Tier | packageId / prefix | Means | Test |
|---|---|---|---|
| RimMandrake | `mandrake.rm.*` / `RM_` | any RimWorld game | "Would a medieval-tribe player install this alone and understand it?" |
| RimStarWars | `mandrake.rsw.*` / `RSW_` | any Star Wars scenario | "Would a Hoth or Tatooine-smuggler campaign want this unchanged?" |
| RimUtinni | `mandrake.rut.*` / `RUT_` | this campaign only | "Does it name Ash'karr, the Kolyska, the Nine, this clan, or this story?" |

A functional fix takes the tier of the mod it fixes; an aesthetic reskin takes the tier of the
aesthetic [`NAMING_SCHEME_PLAN.md` §1 tie-break rules].

## 2. Hard rulings that bear on mod decisions

Each bullet: ruling ⇒ implied filter.

- **No worldgen, ever; no alternative planets** (*"Do not build anything that produces ALTERNATIVE
  planets"*) [`CLAUDE.md` §"There is no worldgen feature", owner 2026-08-15/18]. ⇒ World generators,
  seed/biome-scoring tools and mechanics that need world creation have no campaign job. But
  "dissonant" is not "safe to remove": the current save may reference them (§3). Precedent: a raid
  faction needing world-creation ticking was graded "keep for parts, not for its own mechanic"
  [`design/Jawa/mods/outgrown_audit_2026-08-30.md` §1 They!].
- **Biomes are painted once, at the end; a zero-tile owned BiomeDef is expected** [`CLAUDE.md` §"A
  BIOME WITH ZERO TILES IS NOT A DEFECT"]. ⇒ "Our biome has no tiles, the donor's does" is never a
  reason to keep a donor biome mod. The world still runs on frozen `RUT_` twins (306 donor rows) that
  die at the paint [`design/RimMandrake/donor_retirement_plan_2026-10-02.md` §1].
- **All biome content is one RM mod, `mandrake.rm.biomes`** (executed 2026-09-28), Utinni patches
  beneath [`biome_mod_architecture.md` §7 Q17, Q15]. ⇒ A third-party biome mod overlaps us wherever
  our roster covers its biome.
- **RM never names Star Wars; canon names route through Utinni patches** [`biome_mod_architecture.md` §7 Q11, Q11a]. ⇒ A Star Wars
  donor's replacement is an `RSW_` port: *"if it's a canon reference, we make our own version and
  it's NOT a conflict with the IP in MLIE"* [Q11].
- **An RM mod may require other mods; "free" means free of the franchise** (2026-09-24, on Vanilla
  Helixien Gas Expanded) [`biome_mod_architecture.md` §7 Q16]. ⇒ A framework our mods lean on is KEEP, not dissonance.
- **Every DLC is a hard prerequisite, for players too** (2026-09-26) [`CLAUDE.md` §design assumes
  every DLC]. ⇒ DLC back-fill mods have no job. Anomaly's *storyline* is at zero; its creatures
  remain a reskin library [`reconciled_lore/01_campaign.md` header].
- **Anti-exponential / 7-question test** [`forbidden_mods.md` §Excluded player-progression systems].
  ⇒ Player psycasting, genetics labs, mechanitor ladder, fluid ideology, royal permits, infinite
  storage, large-scale automation, free fuel, reward-spoiling info and ruin-cheese mods are out as
  *player* systems. Bundled threat roster + player engine ⇒ "Cherry-Pick the engine, keep the
  creatures" (Vanilla Genetics Expanded, VFE-Insectoids 2) [same].
- **Named exclusions**: Combat Extended, full Dubs Bad Hygiene and Gravship Water Systems (Thirst-only
  accepted), Real Ruins, Mini Gravships, GravTech, Force-psycast mods, Mythological Creatures
  (*"primitive, off-genre, and poorly implemented"*), randomized research, Natural Disasters for v1
  [`forbidden_mods.md` headings]. **Force powers are v2; VPE is out on purpose**; lightsaber weapons
  stay [`design/Jawa/mods/required_mods.md` banner].
- **The Empire is vanilla Royalty `Empire`, reskinned**; the OuterRim faction is cut but its mod stays
  for the raid armor [`memory/galactic-empire-is-reskinned-vanilla.md`]. ⇒ Grade content actually
  used, not the mod's headline.
- **Ship or nothing to the sea floor** (`RM_SeabedLayer`); **flyers use core 1.6 flight**; **one kind
  of heat** (vanilla); **a pit is a superdeep cell** [`CLAUDE.md` §sea rulings, §flyers, §heat, §pit].
  **Liquids**: one `LiquidDef` registry, FlowWorks is the flow engine, conversion found never built,
  "never redundant tanks" [`memory/liquids-framework-ruled.md`]. ⇒ Pawn-diving, parallel heat
  needs, flight frameworks for creatures and third-party fluid/pipe systems overlap ours.
- **In-game LLM is `claude -p` only** [`CLAUDE.md` §In-game LLM]; Powerful AI Integration dropped
  [`forbidden_mods.md` §AI dialogue layer]. ⇒ Hosted-API LLM mods are dissonant.
- **Every mod we ship has superb Mod Settings** [`CLAUDE.md`]. ⇒ A real cost of REPLACE.
- **No donor art is kept; vanilla counts as donor** (*"We're not keeping any"*, 2026-10-05)
  [`memory/no-donor-art-kept.md`]; art is judged against the canon library in a natural-history,
  matte, no-outline register [`memory/art-lawset-and-canon-push.md`]. ⇒ Art-only donors are REPLACE.
- **Recognizability**: *"If it's obvious and easy, we shouldn't use it"*; a starved biome never admits
  a recognisable animal [`design/Jawa/worldbuilding/creature_recognizability_rule.md`].
- **Evictions are stopped; roster changes happen at each biome's sitting** [`CLAUDE.md` §"An animal
  belongs to ONE biome"]. ⇒ Never recommend a roster sweep.

## 3. Direction of travel for third-party content

**Owner, 2026-09-20: *"Everything should be moved t our own thing defs."*** [`infrastructure/state/
items/DONOR_DEFS_PORT_TO_OURS_1.md` §the ruling]. On whole mods: *"retire entire mods if we're barely
keeping their content and reskinning what they got... Less mod mod conflict, easier maintenance"*;
survivors are absorbed (the `Absorbed_*` pattern in `RimStarWars/Armoury`)
[`design/Jawa/worldbuilding/creature_recognizability_rule.md` §6].

Under way:

- **Star Wars donors are being sunset** (*"get rid of them all so we don't forget"*, 2026-09-02);
  KotOR Weapons, E-Web, Archotech turret, JDS Armory and Sith already retired
  [`infrastructure/state/items/closed/STARWARS_DONOR_SUNSET_1.md`]. Per-mod cards for the 20 SW mods:
  `design/Jawa/sw_ownership_survey.md`.
- **Mlie's Star Wars Animal Collection: absorb, then retire** (*"port the ~150 creature defs before
  retiring"*) [`items/closed/MLIE_FAUNA_ABSORPTION_1.md`]; only 7 shipping rows still name it.
  **Alpha Animals is now the main job** (72 of 128 shipping donor rows), then Alpha Biomes 14, ReGrowth
  5. Paired retirements: Isopoda gene line with VFE-Insectoids 2; `GR_Beetlefleet` (VGE) with Alpha
  Animals [`donor_retirement_plan_2026-10-02.md` §1, §3].
- **Megafauna, Mythic Ages, Beasts of the Rim, Jurassic** ruled out 2026-09-05
  [`design/Jawa/worldbuilding/RETIREMENT_CHECKLIST.md` header].
- **Off-lore proper nouns** (Orc Clan, Dark Ages trolls, Big and Small Norse races, MiningCo., Horrors,
  Mo'Events, VRE Archon) are a rename backlog; retheme-or-drop is an undecided design call
  [`design/Jawa/donor_proper_noun_backlog.md`].
- **Prior whole-list audit**: `design/Jawa/mods/outgrown_audit_2026-08-30.md` (+`.csv`, 585 rows) is
  evidence, not rulings, and did not open its 416 "framework" mods individually [its §Method].

**Implications for the verdicts** (a reading, not a ruling):

- Content **already ported** ⇒ PHASE-OUT candidate; cite the absorption item. **Art-only** ⇒ REPLACE.
  Behaviour living in the donor's C# (15 Alpha Animals creatures, dryads, swarmlings, mecharat) is
  decided per creature at biome review [`donor_retirement_plan` §5 Q4].
- **Retirement needs three checks**: dependent mods (`WEAPONS_DONOR_RETIREMENT_1`); placed Things in
  the save (`lumi.doorsexpanded` killed the game on load, 2026-09-09)
  [`memory/donor-retirement-mod-check-not-save-check.md`]; and `ParentName` order
  (`src/RimMandrake/Utils/retirement_order.py`) [`RETIREMENT_CHECKLIST.md` §Before unticking]. An
  unguarded donor row reset `ModsConfig.xml` to Core-only twice on 2026-09-27 [`CLAUDE.md` §Patch and
  def behaviour].
- **Donor-absent tests wait for the paint** [`donor_retirement_plan` §3 Step D]. Only worldmap,
  gravship and founders survive the expected remake, so save continuity is no long-term reason to keep
  a donor [`memory/world-remake-is-the-last-step.md`].
- **Keep the mod, cut the content** (Cherry Picker) is a legitimate verdict shape (§2).

## 4. Resonance tests

Ask of every mod, in this order. Each test names its source.

1. **What does it actually ship, and is any of it used?** Read its About.xml `<name>` and
   `<description>` and its Defs; a pure-C# mod can look like a framework
   [`outgrown_audit_2026-08-30.md` honesty note; `CLAUDE.md` §"Is there a mod that does X?"].
   Check Cherry Picker cuts and our own `MayRequire`/`loadAfter` references before calling it unused.
2. **Does anything of ours depend on it?** A framework or library one of our mods requires is KEEP
   until that dependency is removed [`biome_mod_architecture.md` §7 Q16].
3. **Fit: desert scavenger crew, Star-Wars-style frontier, ship-centred, keep moving?** Resonant:
   scarcity, salvage, water and fuel pressure, qualitative threats, alien-looking creatures.
   Dissonant: medieval/fantasy/Norse/orc identities, Earth-recognizable animals, modern-corporate
   brands [`01_campaign.md` §Premise, §The pillars; `creature_recognizability_rule.md`;
   `donor_proper_noun_backlog.md` categories].
4. **Does it raise the ceiling?** Run the 7 questions: parallel ladder, scales indefinitely, bypasses
   fuel/space/risk/time/mood/scarcity, makes the ship less necessary. Cosmetic, QoL, UI and sound mods
   "pass trivially" [`01_campaign.md` §The pillars; `forbidden_mods.md` §Excluded player-progression
   systems].
5. **Does it generate worlds, vary planets, or need world creation to work?** Dissonant
   [`CLAUDE.md` §no worldgen].
6. **Does it duplicate a system we own or have ruled on?** Biomes (`mandrake.rm.biomes`), liquids
   and depth (FlowWorks, `LiquidDef` registry), creatures (SWBestiary and the biome rosters), heat
   (vanilla only), flight (core), sea-floor access (the ship), in-game LLM (`claude -p`)
   [§2 above and sources there].
7. **Is it Star Wars IP?** Then its future is an `RSW_` port routed through Utinni patches, and the
   donor is on the sunset track [`biome_mod_architecture.md` §7 Q11; `STARWARS_DONOR_SUNSET_1`].
8. **Is it kept only for its art?** Donor and vanilla art are not kept [`memory/no-donor-art-kept.md`].
9. **What does retiring it cost?** Dependents, placed Things in the save, `ParentName` order,
   paired donors [§3 above].
10. **Performance.** On the 550 list a quicktest map ran **~8–10 TPS** (~120 ms/tick), main thread
    saturated, 30.6 GB private, cold load 20.7 min; the cause awaits "its own diagnosis", so per-mod
    cost is **UNMEASURED** [`Transient/foundry_fulllist_deploy_20261010.md` 14:00–14:20, §Owed].
    Noisy donors seen there: Worldbuilder (ConfigErrors NRE), Quarry (duplicate `Sandstone` key),
    Leo.RaidProtectionFee (a modal swallowed a raid) [same].

## 5. Contradictions and open tensions

Listed with both sources; **not resolved here**.

1. **Who is the audience?** "A single-player build for the owner's own play — never design for
   release-robustness or other players' mod lists" [`reconciled_lore/01_campaign.md` header] **vs**
   "future players will have all the Rimworld DLC's" (2026-09-26) [`CLAUDE.md` §DLC], an RM biome mod
   "meant to be playable on a generated planet by anyone" [`biome_mod_architecture.md` §1], and "public
   wave later" [`memory/liquids-framework-ruled.md`]. Decides whether portability is a criterion.
2. **Premise and Empire in the older mod docs.** `forbidden_mods.md` §Star Wars theme layer still
   frames the theme as "crashed Factory ship / Jawa stowaways", and `concept.md` §4 has "Empire =
   fused vanilla Royalty + Outer Rim Galactic Empire" plus world-interest mods (Geological Landforms,
   Biome Transitions, Alpha Biomes, Exploration Mode) **vs** the Rakatan-ship premise
   [`01_campaign.md` §Premise], the OuterRim faction excluded [`memory/galactic-empire-is-reskinned-
   vanilla.md`], and no worldgen [`CLAUDE.md`]. `concept.md` is marked superseded;
   `forbidden_mods.md` is marked live.
3. **Big-creature mods welcome vs retired.** `forbidden_mods.md` §Excluded player-progression systems
   lists "Megafauna, Alpha Animals, Star Wars Animal Collection, Jurassic-Dinos-Only" as welcome threat
   content **vs** the 2026-09-05 retirement of Megafauna, Mythic Ages and Jurassic
   [`RETIREMENT_CHECKLIST.md`], the recognizability rule, and the port-everything ruling
   [`DONOR_DEFS_PORT_TO_OURS_1.md`].
4. **ISEKAI RPG Leveling.** Graded "keep" as "a full RPG leveling system… a whole layer nothing else
   owns" [`outgrown_audit_2026-08-30.md` §2] **vs** the anti-exponential pillar's ban on parallel
   ladders [`01_campaign.md` §The pillars]. No owner ruling on it was found in `design/` or `canon.yml`.
5. **Build pause.** `donor_retirement_plan_2026-10-02.md` §6 gates steps B–D on the 2026-10-01 build
   pause **vs** "Build pause is lifted" (owner 2026-10-02) [`CLAUDE.md` §How we debug].
6. **Which BiomeDefs the world carries.** `the_one_map.md` §Owner's rulings 2026-08-18 names donor
   defs as the world's biomes ("The Pyrelands is `ZBiome_Grasslands`", `AB_*`, `COMIGO_*`)
   **vs** the 2026-09-12 donor→`RUT_` repaint and the rule that the painted def must be the RM def
   [`biome_mod_architecture.md` §1]. Which donor biome defs the live save still uses is a live-read
   question [`CLAUDE.md` §tiles CSV is a RECORD].
7. **Anomaly.** "Storyline content at zero… a reskin library" [`01_campaign.md` header] **vs**
   "Anomaly's kept content… IS the Assailant war: permanent, load-bearing canon… the Anomaly DLC
   becomes UNPICKABLE" [`design/Jawa/canon_reintegration_plan.md` header ruling ②].
8. **"Worldgen" wording.** `NAMING_SCHEME_PLAN.md` header speaks of "the one irreversible worldgen";
   `memory/world-remake-is-the-last-step.md` expects the world "remade from scratch" **vs** "no
   worldgen in any version" [`CLAUDE.md`] and "The map is edited DIRECTLY, one map, in place"
   [`the_one_map.md` banner]. Whether a remake regenerates anything is not settled in these docs.
9. **Stale verdict files.** `design/Jawa/mods/mod_config_rulings.md` says of itself "Nothing here has
   been re-verified against the current stack" (written against 562–580 mods)
   [its header]; `sw_ownership_survey.md` (2026-08-30) counts 590 active, the deploy record 550.
   Treat their per-mod verdicts as history to re-check.

## 6. What this brief does not decide

- **No verdict on any individual mod.** It supplies filters; per-mod verdicts are the assessors'
  output and the owner's rulings.
- **No resolution of §5.**
- **No roster or eviction calls** — those belong to each biome's review sitting
  [`CLAUDE.md` §evictions are stopped; `biome_mod_architecture.md` §7 Q12].
- **No retirement order or timing.** Ordering is `donor_retirement_plan_2026-10-02.md` §5's open
  owner questions, and donor-absent tests wait for the paint [same, §3 Step D].
- **No performance attribution.** Per-mod TPS cost is unmeasured [`foundry_fulllist_deploy_20261010.md`
  §Owed].
- **No ModsConfig edits.** Nothing here authorizes unticking a mod; `modcheck run` rewrites the live
  list and is an expensive-list action [`CLAUDE.md` §Tools with surprising side effects].
