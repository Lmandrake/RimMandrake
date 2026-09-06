<!-- status: DESIGN, Fable pass 2026-09-06, for BENCH → owner → FOUNDRY.
     Reads on top of (never restates): droid_system_spec.md (WHAT),
     droid_system_build_spec.md (HOW, 14 units), droidworks_assumptions.md,
     droid_verbs_decisions.json (FROZEN), reconciled_lore/08_droids.md.
     State of play with citations: DROID_PROGRAM_STATE_2026-09-06.md.
     Nothing here is ruled until the owner answers §7; defaults are marked. -->
# Droidworks — the unified framework, the retirement, the ladder, the fan-out

## 0. The one sentence

Droidworks is built and idle. What remains is **(A) prove it live, (B) close the
five design holes that were deliberately left open, (C) retire five donors in an
order that keeps the game loading at every step, (D) then improve droids** — and
(D) is where the "beautiful Droidworks efforts" the owner remembers actually
live. Foundry can start A today; B–D need the §7 answers first.

## 1. The unified framework (what every droid IS on the platform)

### 1.1 Identity: a droid is a HAR humanlike pawn of our flesh type — never a mech

| axis | ruling / mechanism | status |
|---|---|---|
| substrate | `AlienRace.ThingDef_AlienRace`, `ParentName="Human"`, `fleshType RSW_DW_FleshType_Droid` (isOrganic false, mech corpse category, mech wound art), `IsMechanoid` **false** | built |
| intelligence | **Humanlike, deliberately** — buys traits, backstories, social, apparel slots, Mood/Joy for the soul layer. Food/Rest suppressed at race level (`foodType None`, `needsRest false`); Mood/Joy/Beauty/Comfort/Outdoors **stay on** | built; owner confirm (§7 Q4) |
| the one need | `RSW_DW_Power`, Harmony-gated to our flesh type (postfix on `Pawn_NeedsTracker.ShouldHaveNeed` — the fix that stopped it reaching every pawn in the game) | built |
| class hierarchy (XML) | `DW_Race_Base` → `DW_Family_{Labour,Protocol,Astromech,Battle,Heavy,Probe,Power}` (tuning lives here) → 57 thin concrete races (defName + art + label, overrides only where the donor genuinely differed) | built |
| class hierarchy (C#) | namespace `RimMandrake.StarWars.Droidworks`; one `DefModExtension` (`DroidworksExtension`: `powerFallPerDay`, `energyDensity`, `deliberateDenyModule`, `chassisClass`) on the family; comps per verb (`CompDroidDetonation`, `CompDWCharger`, `CompDWDataSpike`); hediffs per state (`RSW_DW_PoweredDown`, `RSW_DW_RestrainingBolt`, `RSW_DW_BoltResentment`); recipes per shop verb | built |
| campaign layer | RimUtinni owns FDE membership, FDE backstories, Ash'karr factions; Droidworks owns none of them (naming grammar: platform = RSW, campaign = RUT) | ruled |

**"Except Mechanoids — they aren't droids."** Enforced by construction, not by
policy: mechanoids are `FleshTypeDefOf.Mechanoid` (force-kill on down, mechanitor
gestation, no inner life) and Droidworks never touches that flesh type, never
patches `Races_Mechanoid.xml`, never adds its need or recipes to a mech race, and
its ion comp keys on `RSW_DW_FleshType_Droid` (the ion *guard* in
JawaIonWeapons keys on `IsMechanoid`, which is the other side of the same wall).
Shared code between the two: **none, and keep it none.** The lore wall
(Forgotten Arsenal = ancient self-replicating tech, no part compatibility) is
the same wall seen from the fiction. The one new pressure on it is the
mindstone race (§7 Q3).

### 1.2 The five states, as engine objects (unchanged; what's proven)

| state | engine | live-proven? |
|---|---|---|
| 1 functional | normal pawn | yes (spawns) |
| 2 transient stun | vanilla stun on hit (non-flesh) + `RSW_JawaIon_Stun` buildup (guard `IsMechanoid`, floor stage at 0.5, decay −0.3/day) | yes, on donor races |
| 3 powered-down | `HediffComp_IonOverloadsDroid` on the ion hediff adds `RSW_DW_PoweredDown` (Consciousness ≤0.10, never decays) — only `RSW_DW_RebootDroid` (Crafting 4, restores 15 % power) clears it | **NO — the wiring was fixed after the only live run** |
| 4 unbootable | conventional death → non-rotting mech corpse; shop rebuild recipe **unbuilt** (unit 13) | corpse yes; rebuild no |
| 5 detonation | `CompDroidDetonation` on `Notify_Killed`: damage `50 × charge × energyDensity`, radius `3.9 × √scale`, no boom below 5 % charge; on 21 races (energyDensity > 0) | **NO** |

### 1.3 One construction method — "the shop", not a factory

Every droid is *repaired into existence*, never manufactured. The construction
method is one bench pair plus one identity component:

- **Repair bench** (`RSW_DW_RepairBench`): bills consume **part items** and repair
  a downed/unbootable droid or a corpse *into a pawn* when the head survives.
- **Reassembly harness** (`RSW_DW_ReassemblyHarness`): a pawn-from-bill (the ABF
  Cradle pattern, proven feasible) consuming `1 head + 1 chassis frame + N parts`;
  the head carries identity (`CompHeadIdentity` snapshot: backstory, traits,
  service record, faction of origin). A fresh head = a fresh mind.
- **Parts model — coarse on purpose (v1)**: per family, three part items —
  `RSW_DW_Frame_<Family>` (chassis, drops on unbootable), `RSW_DW_Head_<Family>`
  (identity + spike feedstock; **never craftable**), `RSW_DW_Servo` (generic,
  craftable from steel+components). Modules (§1.4) are the fourth kind. Finer
  granularity (limbs, sensors) is a v2 tail, not v1.
- **Reboot / bolt / wipe / spike** stay surgeries-on-the-operations-tab (already
  built) — they are the "bring it in to the shop" verbs; only *repair* moves to
  benches.
- The Cradle-equivalent (blank body from raw materials) stays **enabled but
  head-gated**: no head, no droid. That is the anti-exponential brake (§6).

### 1.4 Modules = apparel in droid-only body groups (KotOR's six slots, absorbed)

`kotorcore/_DroidsBase/ThingDefs_DroidEquipment/` ships 9 apparel files
(armor ×3, cloak, utility weapons, weapons, light cannons, sensors, tech) plus
batteries and repair kits (both CUT). Absorb them as `RSW_DW_Module_*` via a
generator in the Armoury-absorption pattern (`gen_kotorcore_absorption.py`), keep
the six `apparelLayers`/body groups, re-point `apparelTags` so the 44 KotOR kinds
keep their loadouts, and add one comp (`CompModulePersonality`, unit 12) that
grants a trait-equivalent hediff while worn. Modules are **loot and salvage
first**; craftable ones need the module research row (§4).

### 1.5 How every existing droid maps on

| donor | kinds → DW | what changes at cutover |
|---|---|---|
| KotOR Droids (44/22) | `RSW_DW_KotORDroid*_*` on `DW_Family_Battle` etc. — generated, recipes inherited | kinds need a faction (rogue collective → §3.2), backstory categories re-pointed, modules absorbed |
| Droid Depot (20/19) | `RSW_DW_OuterRim_*` — generated | 4 FDE kinds + 1 Galactic Empire kind repointed; `NoDroidManufacture`/`MSEDroidFix`/`DroidFemaleTexture_Fix` retire |
| JDS (16/16) | `RSW_DW_JDSCIS_*` — generated, capturable by construction | donor already off; kinds need a faction or they never appear (§7 Q2) |
| our 4 `Jawa_Droid_*` | stay RUT, `race` → `RSW_DW_Race_OuterRim_*` | one XML edit + FDE pawnGroupMakers unchanged |
| mechanoids | **not mapped, ever** | — |

## 2. Retirement plan — order of operations that keeps the game loading

Precedent: `WEAPONS_DONOR_RETIREMENT_1` (one wave per cold load, back up
ModsConfig, `harvest_log.py` baseline, check the WHOLE active list for
dependents) and `KOTORWEAPONS_ABSORPTION_DANGLING_REFS_1` (grep our own XML for
the donor's defNames before flipping). Every step below ends in a cold load
that must read clean before the next.

| step | flip | prerequisites (absorb list) | dangling-reference risks to grep first | Cherry Picker |
|---|---|---|---|---|
| **R0** | enable `mandrake.rsw.droidworks` alongside all donors | packets A1–A2 green | texPath duplicates (457 yanked PNGs at donor paths — ContentFinder returns the first; verify which); Harmony postfix idempotency vs `RimUtinni.Doctrine`'s relations fix (documented idempotent, unverified live) | none |
| **R1** | retire `guy762.kotordroids` | modules absorbed (B3); `RSW_DW_` rogue-droid FactionDef or re-key (C1); `RSW_DW_DataSpike.spikeFaction` re-keyed; FDE backstory `spawnCategories` re-pointed (they were authored against `guy762BSC_Droid_*`); Baragwin trader stock lines (sites 7–10, already absence-gated); frozen-save FactionDef check (haiku) | `KotORDroid*` in `src/RimUtinni`, `src/RimStarWars/Armoury`, `PawnFlavor`, `Inhabited`; `btd.gbp.shippack.kotor.vge`'s Droid Distress Call quest names KotOR kinds — **UNMEASURED**, must grep | its 44 kinds' cut rows become dead — clean |
| **R2** | retire `killathon.artificialbeings` + `.syncore` | R1 done ⇒ `_DroidsBase` never loads ⇒ Site 1 moot; `DroidDonor_ABFGate.xml` fires by `nomatch`; kotorcore's `MHC`/`ATC` folders self-exclude | `ArtificialBeings.` in every active mod's XML (a haiku grep across `Mods/` + workshop, case-insensitive) | — |
| **R3** | retire `neronix17.outerrim.droiddepot` + `neronix17.asimov` (+ `mandrake.rsw.msedroidfix`) | 4 `Jawa_Droid_*` repointed (C2); `OuterRim_ImperialKXSecurityDroid` gated or repointed (it lives in `outerrim.galacticempire`, which stays); `NoDroidManufacture.xml`, `DroidsAreMachines.xml`'s Asimov half, `DroidFemaleTexture_Fix.xml` gated/retired; Inhabited cast 04 chassis names are prose only (check) | `OuterRim_*Droid*`, `Asimov` in `src/` (there are `OuterRim_DroidBrain` research rows in the Retag tree — `waking_mind_ai_deep_dive.md` §1); 82 `Asimov.Need_Energy` need entries in the frozen save (Scribe spam, scrub optional) | Depot's 20 kinds + factory rows |
| **R4** | retire `guy762.mm.kotorcore` | `STARWARS_DONOR_SUNSET_1` wave 3 + Armoury's four dangling files (`KOTORWEAPONS_ABSORPTION_DANGLING_REFS_1`) + crystal texPaths (FOUNDRY note 2026-09-05) | outside the droid program; sequence after R3 | — |

`DroidsAreMachines.xml` retires in halves: the ABF flesh-type xpath after R2, the
Asimov one after R3 (each is `PatchOperationFindMod`-gated, so they no-op early
anyway — retire for cleanliness, not necessity).

## 3. The Droidworks dream as a build ladder

### 3.1 v1 — the platform plays (before any retirement)
Live proof of the five states · format tiers (blank/mindless/programmable/sapient
as one `Hediff_FormatTier`, stages gate capacities and `WorkTagIsDisabled`) · the
shop pair + coarse parts + head identity · per-faction heads → per-faction
spikes · modules absorbed · bolt payoff (mood aura thought on nearby pawns;
resentment ≥ threshold → `MentalState` rebellion on removal; shear-on-damage) ·
droid factions on the platform · research rows in The Unbolting tab.

### 3.2 Factions — who fields droids
The platform ships **zero** factions; the campaign needs three registers
(`droid_taxonomy.md`: convert · scavenge · purchase). Proposed, all RUT-tier:
`RUT_RogueDroidCollective` (permanent enemy, drop-pod raids from day 45, the
KotOR Bad kinds — replaces `guy762_KotORFaction_RogueDroids`), the **Free Droid
Enclaves** (already authored; membership → DW races; retaliation only), and the
Separatist remnant question (§7 Q2). Droid *traders* ride existing trader kinds
(Baragwin absorbed copy). Spikes are keyed per faction: one `RSW_DW_DataSpike_<X>`
per faction that fields droids, crafted from that faction's heads.

### 3.3 v1.5 — droids become people
`CompServiceRecord` drift (time-since-wipe accretes idiosyncrasy traits from
chassis-weighted pools — the Assembly × Service-Record set in
`pawn_flavor_design.md` is the content) · module personality (unit 12) · chassis
personality bias as starting-trait weights per family (data, not C#) ·
protocol-droid pedantry as a social-roll modifier · wild-droid faction +
seek-a-master + reprogram-as-recruit with resistance (unit 14) · FDE goodwill
cap (`GoodwillSituationDef`, spec written) → unblocks
`DROID_TILES_SOURED_TERRAIN_1` · the Unbolting as liberation rite (Ohm/Oomo hooks
via `NINEFOLD_MISSING_EVENT_HOOKS_1`'s "droid-online").

### 3.4 v2 — the voice and the shop floor
- **Droid dialogue via the Oracle** — under CLAUDE.md's rule the transport is
  `claude -p` (subprocess, off-tick, timeout, kill-switch), and the two Oracle
  laws hold: **text authority only**. Consumers, each shipping its prescribed
  text first: the memory-wipe reaction letter (the droid's last words, from its
  service record), the bolt-removal moment, a wild droid's offer to serve, a
  long-unwiped droid's "I remember" fragment. Never a def, never a number.
  Blocked on `ORACLE_EXPERIMENT_SPIKE_1`'s client rewrite; design-only until then.
- **Repair Shop quest pack** (ruled a pack on top): visitors with broken droids,
  diagnosis reveals (the wiped assassin), reputation gates customers.
- Fine-grained parts + jury-rigging provenance (shared data shape with the
  salvage-provenance proposal) · mouse-droid/gonk logistics comedy · astromech
  machine familiarity · detonation tuned by a savegame review (`Options he must
  LOOK at ship as a savegame`).

## 4. Research rows (Droidworks brings none — MEASURED)
Author in The Unbolting tab (`waking_mind_ai_deep_dive.md`'s ruled home for droid
construction): `RSW_DW_Research_Reboot` (free at start — the Jawa can always
reboot) → `_Bolting` → `_Spiking` (per-faction spikes) → `_ShopRepair` (bench)
→ `_Reassembly` (harness) → `_Modules` (craftable modules) → `_Formatting`
(tier changes). Six rows, one small tree; the Retag pass owns placement.

## 5. Foundry fan-out — packets, tiers, dependency graph

Model per `infrastructure/agents/Agent_Policy.md` ("who catches it?"): haiku =
compiler/validator/grep catches; sonnet = another agent re-derives; opus = a
recorded fact or Harmony/C#/bridge. Every packet: one agent, explicit inputs,
outputs, a verify line, no push without BENCH. Names are proposals for
`rimflow file`.

| # | packet | model | inputs | outputs | verify | after |
|---|---|---|---|---|---|---|
| A1 | `DROIDWORKS_LIVE_LOOP_PROOF_1` | **opus** | minimal list + Droidworks + JawaIonWeapons; `rimworld-debug-testing`; the 8 open checkboxes | quicktest log: spawn `RSW_DW_OuterRim_GNKDroid` + one KotOR kind, ion → `RSW_DW_PoweredDown`, stays down, reboot, bolt, wipe, spike, kill → corpse, GNK detonation at 100 % vs 5 % charge | `jawa/pawn_get` hediff reads per step; explosion radius/damage measured; all 8 boxes ticked or bugs filed | — |
| A2 | `DROIDWORKS_FULL_LIST_COEXIST_1` | sonnet | A1 green; full ModsConfig backup | Droidworks enabled beside donors; cold load; texPath-duplicate census; Harmony idempotency check | `harvest_log.py` baseline unchanged; 0 new `Config error in`; DW pawn generates in a real-ideo faction 10/10 | A1 |
| A3 | `DROID_FACTIONS_IN_FROZEN_SAVE_1` | haiku | `rimworld-savegame` skill, `WORLDMAP_V1_original.rws`, campaign save | table: which droid FactionDefs / kindDefs / need classes are scribed | counts via the skill's grep method, MEASURED | — |
| B1 | `DROIDWORKS_FORMAT_TIERS_1` | opus | build spec unit 10; ABF `Format*` design (design only) | `RSW_DW_FormatTier` hediff, 4 stages; `WorkTagIsDisabled` postfix; needs switch; 4 recipes (format up/down, deformat = murder thought per faction ethics) | compile; quicktest: a mindless droid refuses skilled work, a sapient breaks | A1 |
| B2 | `DROIDWORKS_MODULE_ABSORB_1` | sonnet | kotorcore `_DroidsBase/ThingDefs_DroidEquipment` (9 files), kotordroids `ThingDefs_DroidEquipment`; `gen_kotorcore_absorption.py` pattern; BLOCKED-manifest discipline | `Defs/Absorbed_KotorDroidModules/` as `RSW_DW_Module_*`, body groups, apparelTags on the 44 kinds re-pointed | `validate_patch.py` 0/0; manifest lists every excluded class; a KotOR kind spawns wearing its modules | A1 |
| B3 | `DROIDWORKS_HEADS_AND_SPIKES_1` | opus | unit 8 + 13's identity half; `Items_Droidworks.xml` placeholders | `RSW_DW_Head_<Family>` items dropped on unbootable/death, `CompHeadIdentity` snapshot, `RSW_DW_DataSpike_<Faction>` per faction, recipes | quicktest: kill droid → head drops with its name; spike keyed wrong does nothing; right key flips faction | A1, C1 |
| B4 | `DROIDWORKS_SHOP_BENCHES_1` | opus (L) | unit 13; §1.3 parts model; ABF Cradle as feasibility proof (design only) | repair bench, reassembly harness, `Recipe_ShopRebuild` (corpse+head → pawn, quality by partsLeft), frame/servo items, overclock as bench job | quicktest: rebuild a corpse; harness makes a pawn only with a head | B3 |
| B5 | `DROIDWORKS_BOLT_PAYOFF_1` | opus | unit 7; `HediffComp_DWBoltResentment` (stub) | aura thought on nearby pawns; resentment threshold → rebellion `MentalState` on removal; shear-on-damage; un-bolt-each-other job during rebellion | quicktest: bolt 30 days, remove → rebels; damage shears | A1 |
| B6 | `DROIDWORKS_ION_SHIELD_BODYSIZE_1` | sonnet | `droid_ruling.md` §5A items 3–4; `ION_STUN_IGNORES_BODY_SIZE_1` (existing item — merge, don't duplicate) | EMP side-damage on ion projectile; `BodySize` scaling in `DamageWorker_IonBuildup` | shield belt drops on ion; thrumbo vs squirrel hit counts measured | — |
| B7 | `DROIDWORKS_DETONATION_REVIEW_1` | sonnet | A1's numbers; `explosion_energy_model.md`; `Options … ship as a savegame` rule | one map, grid of energyDensity 1/2/3 × charge 5/50/100 %, saved for the owner; `deliberateDenyModule` wired on JDS battle kinds | new save file exists, keepers untouched; grid key in item file | A1 |
| B8 | `DROIDWORKS_RESEARCH_ROWS_1` | sonnet | §4; `ResearchRetag` conventions | 6 `ResearchProjectDef`s in The Unbolting; recipes gated | tree renders; reboot ungated at start | B3, B4 |
| C1 | `DROID_FACTIONS_ON_PLATFORM_1` | opus | §3.2; owner's §7 Q2 answer; A3; `FACTION_SPEC.md`; `guy762`'s `Factions_RogueDroids.xml` as design reference | `RUT_RogueDroidCollective` FactionDef + pawnGroupMakers on `RSW_DW_KotORDroidBad_*`; FDE `pawnGroupMakers` → DW kinds; spike keys | raid fires on quicktest with DW kinds; FDE caravan spawns DW droids | A2 |
| C2 | `DROID_FDE_KINDS_REPOINT_1` | sonnet | `JawaFactionRoster.xml` (generated — fix the generator `gen_pawnkind_roster.py`, not the output), `Backstories_FDE_Droids.xml`, `FactionBackstoryWiring.xml` | 4 `Jawa_Droid_*` on DW races; FDE backstory categories re-pointed to DW `spawnCategories` | generator diff shows only the 4 race lines; validate 0/0 | A2 |
| C3 | `DROID_FDE_GOODWILL_CAP_1` | sonnet | `restraining_bolt_technical.md` (spec complete) | `GoodwillSituationDef` + worker in RimUtinni | cap holds in play; unblocks `DROID_TILES_SOURED_TERRAIN_1` | C1 |
| D1 | `DROID_DONOR_REFGREP_1` | haiku | §2 risk column | per donor, every reference in `src/` + every other active mod's XML (case-insensitive) | a file per donor, counts MEASURED | — |
| D2 | `DROID_RETIRE_KOTORDROIDS_1` | sonnet | B2, B3, C1, C2, D1, A3 all closed | ModsConfig flip + cold load | baseline clean; `harvest_log.py` crossref unchanged | B2 B3 C1 C2 |
| D3 | `DROID_RETIRE_ABF_SYNCORE_1` | sonnet | D2; `DroidDonor_ABFGate.xml` | flip + cold load; `DroidsAreMachines.xml` ABF half removed | 0 `ArtificialBeings` class errors | D2 |
| D4 | `DROID_RETIRE_DEPOT_ASIMOV_1` | sonnet | D3; C2; galacticempire KX kind gated; `NoDroidManufacture`/`MSEDroidFix`/`DroidFemaleTexture_Fix` retired; optional save scrub | flip + cold load | 0 `Asimov` class errors; FDE droids still spawn | D3 |
| E1 | `DROIDWORKS_CHASSIS_PERSONALITY_1` | sonnet | `sw_mod_concepts_triage.md` §G; dream text §2 | per-family trait weight tables (data) + protocol social-roll modifier (small Harmony → opus if it grows) | 20 spawns per family show the bias | B1 |
| E2 | `DROIDWORKS_SERVICE_RECORD_DRIFT_1` | opus | unit 11; `pawn_flavor_design.md` Assembly × Service-Record | `CompServiceRecord`, chassis-weighted idiosyncrasy pools, wipe resets | quicktest: 2 years unwiped → traits accrete; wipe clears | B1, E1 |
| E3 | `DROIDWORKS_MODULE_PERSONALITY_1` | sonnet | unit 12; B2 | `CompModulePersonality` (trait-hediff while worn) | wear spider-arm → trait appears; remove → gone | B2 |
| E4 | `DROIDWORKS_WILD_DROIDS_1` | opus | unit 14; §3.2 | wild faction, seek-a-master incident, reprogram-as-recruit resistance | quicktest incident fires | C1, B1 |
| E5 | `DROID_ORACLE_VOICE_DESIGN_1` | **fable** (design only) | §3.4; Oracle spec; cast bible | consumer contracts + prescribed fallbacks for 4 droid moments | reviewed by owner | Oracle client rewrite |

**Critical path**: A1 → A2 → {B2, B3, C1, C2} → D2 → D3 → D4. Everything in B/E
except B2/B3 can run in parallel with D once A2 is green. A3 and D1 are haiku
sweeps runnable today, before the owner answers anything.

## 6. Anti-exponential check (`concept.md` §3, the 7 questions) on the player-facing additions

| addition | Q1 parallel ladder | Q3 scales indefinitely | Q5 bypasses scarcity | verdict / guardrail |
|---|---|---|---|---|
| chargers ×3 | no (a need, not a tree) | no | no — costs power, the ship's leash | clean |
| repair bench | no | **only if parts are craftable** | — | frames/heads never craftable; servos cost components (VFE-Factory's own scarcity) |
| reassembly harness | **the Cradle risk** — a droid printer | yes if raw→droid | crew composition (Q4) if droids are free labour | **head-gated: no head, no droid.** Heads come only from salvage/capture. That single rule is the whole brake, replacing `NoDroidManufacture.xml` |
| data spikes | no | consumable, from heads | Q4: capture replaces recruitment? | keyed per faction, one head each — capture stays a fight, not a click |
| memory wipe | no | **re-roll-for-god-rolls exploit** | — | wipe costs the service record (drift resets) and Crafting 5 + 1,200 work; add a "recently wiped" hediff (7 days, −skills) to price the reroll |
| modules (craftable) | a parallel gear ladder | yes via research | — | loot/salvage first; craftable tier behind the last research row; no stat above the donor's own numbers (§19.5 audit precedent) |
| format tiers | no | no | Q4 yes if sapient = free colonist | sapient is *earned* (formatting costs + murder ethics), mindless is a reduced state — ruled |
| detonation / bolts / drift | enemy-side or cost-side | — | — | pass trivially |

Q7 (does it make the ship MORE important?): repair benches live on the deck and
draw ship power; heads are salvage the ship flies to. Yes.

## 7. Questions for the owner — cards for BENCH (recommended default marked ★)

1. **Activation route.** Enable Droidworks in the full 603-mod list *now*, beside the donors, and prove live there (★ after A1 on a minimal list first — one quicktest hour, then the full-list flip)? Or hold until B1–B4 are built?
2. **Who fields droids against you after retirement?** The KotOR rogue collective and the JDS CIS faction both die with their mods. ★ Author one `RUT_RogueDroidCollective` (permanent enemy, drop-pod raids, KotOR Bad kinds) now; leave the Separatist remnant unfielded until a Geonosian/foundry faction wants those 16 chassis. Alternative: a CIS remnant faction too.
3. **The mindstone race vs the wall.** Is a mindstone-minded droid a Droidworks chassis with a special head (★ — the head-identity model makes it one item, and "not really a droid any more" is what the head *is*), a separate HAR race, or a mechanoid-side thing? This decides whether `MECHANOID_ORIGIN_CANON_1` rides B3.
4. **Droid inner life by default.** Keep Humanlike intelligence with Mood/Joy/Beauty/Comfort on for every droid (★ — the soul layer needs it; mindless tier turns them off per droid), or strip them and re-add per tier?
5. **Parts granularity for v1.** ★ Coarse (frame / head / servo / modules per family). Or fine (limbs, sensors, motivators) from the start, doubling B4?
6. **Reassembly harness head-gate.** ★ A droid can only ever be assembled around a salvaged head — no head printer, ever. Confirm this replaces the Droid Depot factory ban as the standing rule.
7. **Memory-wipe cost.** ★ Add a 7-day "recently wiped" debuff and reset the service record, so wipes are a real decision. Or leave wipes free (as built)?
8. **Modules craftable at all?** ★ Yes, behind the last research row, at donor stats. Or loot-only forever?
9. **Detonation numbers** (`50 × charge × density`, `3.9 × √scale`, 5 % floor) — review by walking the B7 savegame grid, or accept as tuned?
10. **Which save is the port boundary?** Droidworks kinds enter the *campaign* save when it is next started fresh from the frozen world (★), or mid-campaign with the FDE repoint riding a save-edit?
11. **Save scrub** of the 82 inert `Asimov.Need_Energy` entries in `WORLDMAP_V1_original.rws` before Asimov retires (★ yes, it is a haiku job; otherwise 82 Scribe lines every load of that file).
12. **Reboot skill**: Crafting 4 only (as built), or Crafting 4 *or* Medicine 4 (needs a custom worker; ★ Crafting only — "a doctor or a craftsman" was the sheet's words, but the shop fiction is craft).
13. **The Droid Distress Call quest** (`btd.gbp.shippack.kotor.vge`, adopted, names KotOR kinds — UNMEASURED): re-point it to DW kinds (★) or let it lapse with kotordroids?
14. **Droid dialogue via the Oracle**: design now as E5 (★, design only, dormant until the `claude -p` client exists) or leave the voice for v2 entirely?
15. **Priority between tracks once A is green**: ★ B (holes) and C (factions) before D (retire), because retiring first leaves a droid-less game for a week. Or retire first to "stop the bleeding" of donor bugs?
