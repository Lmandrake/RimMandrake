<!-- status: DESIGN, Fable pass 2026-09-06, RULED by the owner the same day (§0).
     Reads on top of (never restates): droid_system_spec.md (WHAT),
     droid_system_build_spec.md (HOW, 14 units), droidworks_assumptions.md,
     droid_verbs_decisions.json (FROZEN), reconciled_lore/08_droids.md.
     State of play with citations: DROID_PROGRAM_STATE_2026-09-06.md.
     Packets in §5 are ready to file (§8 filing script). -->
# Droidworks — the unified framework, the retirement, the ladder, the fan-out

## 0. 🔴 OWNER RULINGS, 2026-09-06 (15 cards, all answered — these govern everything below)

1. **Activation**: minimal-list proof first (A1), then flip into the full list.
2. **Enemy droids — NO rogue droid faction, ever.** Verbatim: *"The Empire will use
   Droids in their attacks. Stormtroopers + Attack Droids working together (and the
   occasional Sith wielding a lightsabre). If they must, the Moisture Farmers will
   defend themselves with utility droids also trying to fight alongside (badly). The
   Hutts mostly rely on muscle but could easily have some military droids they
   purchased. Junkers might have one or two atrocious, clumsy droids spewing fire and
   able to blow themselves up against the enemy or their structures. Many traders
   will come with protocol droids to help them with communication and trade
   advantage (there should be real trade advantage to having a protocol droid with
   you, dangerous not to). Then there's the free droid enclave. They won't raid you
   unless you're in their territory and have already made them enemies. And of
   course the Trade Moot loves droids of all kinds and buys/sells them, just like
   you. I think there should be regular events where various local friendlies come
   to have you repair or upgrade their droids for profit... it's just what everyone
   knows Jawa are supposed to do. And there should be real opportunities to use
   superior or inferior parts, get rid of problematic droids or parts, and otherwise
   be... Jawa. ... Oh, and there's the wild droids that have gone crazy from being
   left out in the desert after crashing. And those trapped in the torture chambers
   of the Hutts for displeasing them."*
3. **Mindstone race** = a Droidworks chassis with a special head (rides B3).
4. **Inner life by tier**: SAPIENT gets everything; PROGRAMMABLE gets Mood but not
   Joy/Beauty/Comfort; MINDLESS and BLANK have no needs.
5. **Parts: FINE from the start** — limbs, sensors, motivators.
6. **Head-gate CONFIRMED as the standing anti-exponential rule.** Verbatim lore:
   *"Personality matrices, processors, and databanks are all too high tech and
   specialized for anyone on this world to make. You import them from Industrial
   Automaton, Cybot Galactica, Arakyd Industries, and a few others. Hacking them is
   virtually impossible without very sophisticated facilities. Helix might be able
   to, but they have no interest in Droids other than as disposable research
   assistants. And then they get damaged... you keep using them, because they're
   rare and valuable still even quirky."*
7. **Wipes**: 7-day debuff + service-record reset, *"and make it REALLY severe. Like
   it bumps into walls, learns how to use its body, and frequently forgets what it
   was doing during that week. Frequently also adds a permanent hardware quirk that
   cannot be reset but only accrete further."*
8. **Modules**: *"Basically loot-only forever. They CAN be fabricated, but at a
   grossly inferior level. The G2 repair droid is an example of what they can make
   entirely by themselves (except for the brain, which they can't do at all ever).
   Very primitive."* — G2 = the goose-necked Phantom Menace repair droid: exposed
   cabling, tube-and-plate frame, twin lamp photoreceptors on a stalk neck, claw
   hands, three-toed feet.
9. **Detonation**: walk the grid as a savegame (B7).
10. **Port boundary**: the next fresh start from the frozen world.
11. **Save scrub** of the 82 Asimov entries: yes, haiku.
12. **Reboot**: Crafting 4 only, as built.
13. **Distress Call quest**: re-point to DW kinds — it becomes the wild/crashed-droid
    rescue.
14. **Droid voice via the Oracle**: design now as dormant E5.
15. **Priority**: platform holes + factions (B, C) before retirement (D).

Contradictions these create with earlier rulings are listed in §7 for the
supersession lines that now belong in the older docs.

## 1. The unified framework (what every droid IS on the platform)

### 1.1 Identity: a droid is a HAR humanlike pawn of our flesh type — never a mech

| axis | ruling / mechanism | status |
|---|---|---|
| substrate | `AlienRace.ThingDef_AlienRace`, `ParentName="Human"`, `fleshType RSW_DW_FleshType_Droid` (isOrganic false, mech corpse category, mech wound art), `IsMechanoid` **false** | built |
| intelligence & needs | Humanlike intelligence for all (buys traits, backstories, apparel slots). Needs **by format tier (ruling 4)**: sapient = Mood/Joy/Beauty/Comfort/Outdoors; programmable = Mood only; mindless/blank = Power only. Food/Rest suppressed at race level | race built; tier gating = B1 |
| the one need | `RSW_DW_Power`, Harmony-gated to our flesh type | built |
| XML hierarchy | `DW_Race_Base` → `DW_Family_{Labour,Protocol,Astromech,Battle,Heavy,Probe,Power}` (tuning) → 57 thin concrete races; **+ `DW_Family_Primitive`** for the Jawa-fabricable tier (ruling 8): the G2 as its first race | families built; Primitive = B9 |
| C# hierarchy | namespace `RimMandrake.StarWars.Droidworks`; `DroidworksExtension` on the family; comps per verb; hediffs per state; recipes per shop verb | built |
| campaign layer | RimUtinni owns faction loadouts, FDE membership, backstories, events (naming grammar: platform = RSW, campaign = RUT) | ruled |

**"Except Mechanoids — they aren't droids."** Enforced by construction: mechanoids
are `FleshTypeDefOf.Mechanoid`; Droidworks never touches that flesh type, never
patches a mech race, never adds its need or recipes to one, and its ion comp keys
on `RSW_DW_FleshType_Droid`. Shared code: **none, keep it none.** The mindstone
race lives on *our* side of the wall as a chassis + special head (ruling 3).

### 1.2 The five states (unchanged; what's proven)

| state | engine | live-proven? |
|---|---|---|
| 1 functional | normal pawn | yes |
| 2 transient stun | vanilla stun + `RSW_JawaIon_Stun` buildup (guard `IsMechanoid`, floor 0.5, −0.3/day) | on donor races |
| 3 powered-down | `HediffComp_IonOverloadsDroid` adds `RSW_DW_PoweredDown` (never decays); only `RSW_DW_RebootDroid` (Crafting 4 — ruling 12) clears it | **NO — fixed after the only live run** |
| 4 unbootable | death → non-rotting mech corpse; shop rebuild **unbuilt** | corpse only |
| 5 detonation | `CompDroidDetonation`: `50 × charge × energyDensity`, radius `3.9 × √scale`, floor 5 %; on 21 races | **NO** |

### 1.3 One construction method — "the shop", and the imported brain

Every droid is *repaired into existence*. Two benches, one identity component,
and one hard import:

- **The brain trio** (ruling 6): `RSW_DW_PersonalityMatrix`, `RSW_DW_Processor`,
  `RSW_DW_Databank` — **never craftable by anyone on the planet**; makers are
  lore (Industrial Automaton, Cybot Galactica, Arakyd) and the items reach the
  player only as salvage from droids, Trade Moot / trader stock, and quest loot.
  A **head** is the assembled trio in a family-specific casing; the head carries
  identity (`CompHeadIdentity`: backstory, traits, service record, hardware
  quirks, faction of origin). Damaged brain parts stay in use — *"rare and
  valuable still even quirky"* — as permanent hardware quirks (ruling 7).
- **Fine parts** (ruling 5): per family, `Frame`, `Head`, and a part set —
  `Leg`/`Arm`/`Manipulator`, `Sensor` (photoreceptor / auditory / scanner),
  `Motivator`, `PowerCell`, `Servo`. Parts drop by a per-family table on
  unbootable/death (never all of them — state 5 keeps the fewest); each part has
  quality; **superior/inferior parts change stats and personality** (the "be…
  Jawa" economy of ruling 2). Frames and most parts are craftable at grossly
  inferior quality in the Primitive tier (B9); the brain trio never.
- **Repair bench** (`RSW_DW_RepairBench`): bills swap parts on a downed/unbootable
  droid or a corpse; **reassembly harness** (`RSW_DW_ReassemblyHarness`): pawn-from-
  bill consuming `1 head + 1 frame + the part set`. No head, no droid.
- **Reboot / bolt / wipe / spike** stay operations-tab surgeries (built).
- **The G2** (ruling 8): the one chassis the Jawa build whole — frame, limbs,
  sensors, claws all Primitive-tier — around an imported brain. Its art is new
  (`generating-rimworld-sprites`, owner's eye).

### 1.4 Modules — loot-only, plus a primitive fabricable tier

KotOR's six-slot apparel scheme is absorbed as `RSW_DW_Module_*` (B2), keeping
body groups and tags so the 44 KotOR kinds keep loadouts. Donor-grade modules
are **loot and salvage only, forever**; the Primitive tier can fabricate a
module per slot at grossly inferior stats (ruling 8). `CompModulePersonality`
(E3) makes installed modules carry attitudes.

### 1.5 How every existing droid maps on

| donor | → DW | at cutover |
|---|---|---|
| KotOR Droids (44/22) | generated on the families | kinds go into faction loadouts (C1), modules absorbed, backstory categories re-pointed, Distress Call re-pointed (C7) |
| Droid Depot (20/19) | generated | 4 FDE kinds + Galactic Empire's KX kind repointed; `NoDroidManufacture`/`MSEDroidFix`/`DroidFemaleTexture_Fix` retire |
| JDS (16/16) | generated, capturable | donor already off; kinds enter Empire attack loadouts and the Junker/Hutt tables (C1) |
| our 4 `Jawa_Droid_*` | stay RUT, `race` → DW | one generator edit |
| mechanoids | **never** | — |

## 2. Retirement plan — one wave per cold load, after B and C (ruling 15)

Precedent: `WEAPONS_DONOR_RETIREMENT_1` (back up ModsConfig, whole-list dependency
check, `harvest_log.py` baseline) and `KOTORWEAPONS_ABSORPTION_DANGLING_REFS_1`
(grep our own XML for the donor's defNames first).

| step | flip | prerequisites | dangling risks to grep first |
|---|---|---|---|
| **R0** | enable `mandrake.rsw.droidworks` beside all donors | A1, A2 | texPath duplicates (457 yanked PNGs at donor paths); Harmony postfix idempotency vs `RimUtinni.Doctrine`'s relations fix |
| **R1** | retire `guy762.kotordroids` | B2 modules absorbed; C1 loadouts; spike keys re-keyed (no rogue collective: keys = Empire / Hutt / Junker / wild); FDE backstory `spawnCategories` re-pointed; C7 Distress Call re-pointed (MEASURED: the quest sub-mod `1.6/Mods/BTD_KotOR_Droids/` names `KotORDroidColonist_{T3UD,SentWD,R8009UD,MPDMkI,KX12UPD}`); A3 frozen-save check | `KotORDroid*`/`guy762_KotORFaction_RogueDroids` in `src/` and every active mod |
| **R2** | retire ABF + SynCore | R1 ⇒ `_DroidsBase` never loads ⇒ Site 1 moot; `DroidDonor_ABFGate.xml` fires by `nomatch` | `ArtificialBeings.` across `Mods/` + workshop, case-insensitive |
| **R3** | retire Droid Depot + Asimov (+ `mandrake.rsw.msedroidfix`) | C2 FDE kinds; galacticempire's `OuterRim_ImperialKXSecurityDroid` repointed to a DW race (it IS an Empire attack droid now); `NoDroidManufacture`/`DroidsAreMachines` Asimov half/`DroidFemaleTexture_Fix` retired; D0 save scrub | `OuterRim_*Droid*`, `Asimov`, `OuterRim_DroidBrain` research rows in the Retag tree |
| **R4** | retire `guy762.mm.kotorcore` | `STARWARS_DONOR_SUNSET_1` wave 3 + Armoury dangling files | outside this program |

## 3. The Droidworks dream as a build ladder

### 3.1 v1 — the platform plays, and droids are everywhere they should be
Live proof · format tiers with needs by tier · fine parts + brain trio + shop
benches · heads → per-faction spikes · modules absorbed · Primitive tier + G2 ·
bolt payoff · wipe severity + hardware quirks · **droids in every faction's
hands (C1)** · protocol-droid trade advantage (C4) · repair-for-profit events (C5)
· research rows.

### 3.2 Who fields droids (ruling 2) — loadouts, not a droid faction
| faction (`FACTION_SPEC.md`) | droids | mechanism |
|---|---|---|
| Galactic Empire (`Empire` reskin) | **attack droids beside stormtroopers**, occasional Sith — the capture line now | `pawnGroupMakers` on the existing FactionDef: DW KotOR Bad + JDS battle kinds at 20–40 % of points; `Jawa_Empire_*` kinds untouched |
| Homestead Defense League (`OutlanderCivil`) | utility droids fighting badly | defence-group entries: Labour/Astromech kinds, low combatPower, Primitive-tier weapons |
| Hutt Cartel | a few purchased military droids | raid/defence entries: 0–2 Heavy kinds |
| the Junkers | 1–2 *atrocious* fire-spewing suicide droids | Primitive-family kinds with `energyDensity 3` + `deliberateDenyModule`, flamethrower module, `MentalState` charge-and-detonate |
| every trader kind | a protocol droid, with a **mechanical trade advantage** | C4: `StatDef` factor on trade prices/negotiation when a Protocol-family pawn is in the trade party; a penalty without one (*"dangerous not to"*) — both sides, so traders without one are cheaper to fleece |
| Free Droid Enclaves | membership → DW races; **territory-only hostility**, after goodwill collapse | C2 + C3 (goodwill cap) + `DROID_TILES_SOURED_TERRAIN_1` |
| Jawa Trade Moot (`Jawa_IndigenousTribes`) | buys/sells droids of all kinds, and brain parts | `StockGenerator_Colonists` on DW kinds; brain-trio stock, rare |
| wild droids | crashed, gone crazy in the desert — hostile, capturable, spike-able | E4 incident; C7 makes the Distress Call the rescue variant |
| Hutt captives | droids in Hutt torture chambers — rescue or buy | C6, rides the Hutt settlement/dungeon work |

### 3.3 v1.5 — droids become people
`CompServiceRecord` drift (E2) · module personality (E3) · chassis personality
bias per family (E1) · protocol-droid pedantry · wild droids + reprogram-as-
recruit (E4) · FDE goodwill cap (C3) · the Unbolting as liberation rite (Ohm/
Oomo hooks via `NINEFOLD_MISSING_EVENT_HOOKS_1`).

### 3.4 v2 — the voice and the shop floor
**Droid dialogue via the Oracle** (E5, design now, dormant): transport is
`claude -p` per CLAUDE.md; **text authority only**; consumers each ship
prescribed text first — the wipe reaction, the bolt-removal moment, a wild
droid's offer, a long-unwiped droid's "I remember". Blocked on
`ORACLE_EXPERIMENT_SPIKE_1`'s client rewrite. Also: jury-rigging provenance
(cross-part substitutions as the fine-parts model already allows), mouse-droid/
gonk logistics comedy, astromech machine familiarity.

## 4. Research rows (Droidworks brings none — MEASURED)
In The Unbolting tab: `RSW_DW_Research_Reboot` (free at start) → `_Bolting` →
`_Spiking` → `_ShopRepair` → `_Reassembly` → `_PrimitiveFabrication` (frames,
parts, inferior modules, the G2) → `_Formatting`. **No row ever unlocks a brain
part.** The `OuterRim_DroidBrain` crafting rows in the Retag tree die with Depot.

## 5. Foundry fan-out — packets, tiers, dependency graph

Model per `Agent_Policy.md` ("who catches it?"). Every packet: one agent,
explicit inputs/outputs/verify, no push without BENCH. Filing lines in §8.

| # | packet | model | inputs | outputs | verify | after |
|---|---|---|---|---|---|---|
| A1 | `DROIDWORKS_LIVE_LOOP_PROOF_1` | opus | minimal list + Droidworks + JawaIonWeapons; the 8 open checkboxes | quicktest: spawn GNK + a KotOR kind; ion → `RSW_DW_PoweredDown`, stays down; reboot; bolt; wipe; spike; kill → corpse; GNK detonation 100 % vs 5 % | `jawa/pawn_get` per step; radius measured; boxes ticked or bugs filed | — |
| A2 | `DROIDWORKS_FULL_LIST_COEXIST_1` | sonnet | A1 green; ModsConfig backup | Droidworks in the full list beside donors; cold load; texPath census; Harmony idempotency | `harvest_log.py` baseline unchanged; 0 new `Config error in`; DW pawn generates 10/10 in a real-ideo faction | A1 |
| A3 | `DROID_FACTIONS_IN_FROZEN_SAVE_1` | haiku | `rimworld-savegame` skill; both saves | table of droid FactionDefs/kinds/need classes scribed | counts MEASURED by the skill's method | — |
| B1 | `DROIDWORKS_FORMAT_TIERS_1` | opus | unit 10; ruling 4 | `RSW_DW_FormatTier` hediff (blank/mindless/programmable/sapient); `ShouldHaveNeed` extension gating Mood/Joy/Beauty/Comfort/Outdoors by stage; `WorkTagIsDisabled` postfix; format recipes (deformat sapient = murder thought per faction ethics) | quicktest: programmable has Mood, no Joy; mindless has Power only; sapient breaks | A1 |
| B2 | `DROIDWORKS_MODULE_ABSORB_1` | sonnet | kotorcore `_DroidsBase/ThingDefs_DroidEquipment` (9 files) + kotordroids equipment; `gen_kotorcore_absorption.py` pattern | `Absorbed_KotorDroidModules/` as `RSW_DW_Module_*`, body groups, tags re-pointed; **no recipeMaker on any** (loot-only) | validate 0/0; manifest of excluded classes; a KotOR kind spawns wearing its modules | A1 |
| B3 | `DROIDWORKS_HEADS_BRAINS_SPIKES_1` | opus | unit 8; ruling 3, 6; `Items_Droidworks.xml` placeholders | brain trio items (no recipe, tradeable), `RSW_DW_Head_<Family>` + `CompHeadIdentity` (snapshot incl. hardware quirks), **`RSW_DW_Head_Mindstone`** (`MECHANOID_ORIGIN_CANON_1`'s race = any chassis + this head), `RSW_DW_DataSpike_<Empire|Hutt|Junker|Wild>` | kill → head drops with its name; wrong key does nothing; mindstone head yields the ruled stats | A1 |
| B4a | `DROIDWORKS_FINE_PARTS_1` | opus | ruling 5; §1.3 part set; families | part items per family with quality, drop tables, `CompPartEffects` (stats + personality per quality tier) | every family drops a legal set; inferior sensor lowers Sight | B3 |
| B4b | `DROIDWORKS_SHOP_BENCHES_1` | opus (L) | unit 13; B4a | repair bench (part-swap bills), reassembly harness (head+frame+set → pawn), `Recipe_ShopRebuild` from corpse, overclock as bench job | rebuild a corpse; harness refuses without a head; swap a leg on a live droid | B4a |
| B5 | `DROIDWORKS_BOLT_PAYOFF_1` | opus | unit 7; resentment stub | aura thought; resentment ≥ threshold → rebellion `MentalState` on removal; shear-on-damage; un-bolt-each-other job | bolt 30 days, remove → rebels; damage shears | A1 |
| B6 | `DROIDWORKS_ION_SHIELD_BODYSIZE_1` | sonnet | `droid_ruling.md` §5A items 3–4; **merge with `ION_STUN_IGNORES_BODY_SIZE_1`** | EMP side-damage on the ion projectile; `BodySize` scaling | shield belt drops; thrumbo vs squirrel counts | — |
| B7 | `DROIDWORKS_DETONATION_REVIEW_1` | sonnet | A1 numbers; the savegame-review rule | one map, grid energyDensity 1/2/3 × charge 5/50/100 %, saved; `deliberateDenyModule` on JDS battle kinds | new save appeared, keepers unchanged; grid key in the item | A1 |
| B8 | `DROIDWORKS_RESEARCH_ROWS_1` | sonnet | §4; `ResearchRetag` conventions | 7 rows in The Unbolting; recipes gated; Depot brain rows cut | tree renders; reboot free | B3 B4b B9 |
| B9 | `DROIDWORKS_PRIMITIVE_TIER_1` | opus (art → owner) | ruling 8; G2 description; `generating-rimworld-sprites` | `DW_Family_Primitive`, the G2 race + kind (art: goose neck, twin lamp eyes, claws, three-toed feet, exposed cabling), primitive frame/part/module recipes at ~40 % donor stats, Junker suicide-droid kind | G2 renders in a savegame for the owner; stats measured below every donor module | B4a |
| B10 | `DROIDWORKS_WIPE_SEVERITY_1` | opus | ruling 7; `Recipe_DWMemoryWipe` | `RSW_DW_RecentlyWiped` 7-day hediff (Moving/Manipulation ramps, random job interruption, wall-bump collisions via a `JobGiver` stub), service-record reset, permanent `RSW_DW_HardwareQuirk` trait pool (accretes, never resets) | quicktest: wiped droid stumbles for 7 days, keeps the quirk after | A1 |
| C1 | `DROID_FACTION_LOADOUTS_1` | sonnet | ruling 2; §3.2; `FACTION_SPEC.md`; existing FactionDefs/rosters (`gen_pawnkind_roster.py` — edit the generator) | `pawnGroupMakers` patches: Empire attack droids, Homestead utility droids, Hutt heavies, Junker suicide droids, Trade Moot stock (DW kinds + brain trio); every trader kind gets a Protocol pawn | each faction raid/caravan on quicktest shows the droids; no droid FactionDef exists anywhere | A2 B9 |
| C2 | `DROID_FDE_KINDS_REPOINT_1` | sonnet | `JawaFactionRoster.xml` (generated), FDE backstories & wiring | 4 `Jawa_Droid_*` on DW races; backstory categories re-pointed | generator diff = 4 race lines; validate 0/0 | A2 |
| C3 | `DROID_FDE_GOODWILL_CAP_1` | sonnet | `restraining_bolt_technical.md` | `GoodwillSituationDef` + worker | cap holds; unblocks `DROID_TILES_SOURED_TERRAIN_1` | C2 |
| C4 | `DROID_PROTOCOL_TRADE_ADVANTAGE_1` | opus | ruling 2; `Tradeable`/`TradeSession` price path | a stat/Harmony factor: Protocol pawn present in either party shifts prices; absent on the player side = penalty | trade with/without a protocol droid, prices measured both ways | C1 |
| C5 | `DROID_REPAIR_FOR_PROFIT_EVENTS_1` | opus | ruling 2; `rimworld-quests` skill; B4b | recurring incident/quest: a friendly arrives with a broken/under-spec droid, pays for repair/upgrade; options to fit inferior parts, keep the good ones, or "lose" a problem droid — reputation effects | quest fires, completes, pays; validator clean | B4b C1 |
| C6 | `DROID_HUTT_CAPTIVES_1` | sonnet | ruling 2; Hutt settlement/dungeon work | captive droids as a site feature: rescue (they join, bolted or resentful) or purchase | site spawns them; both outcomes tested | C1 |
| C7 | `DROID_DISTRESS_CALL_REPOINT_1` | sonnet | ruling 13; `btd.gbp.shippack.kotor.vge` quest sub-mod | patch its 5 `KotORDroidColonist_*` refs to DW kinds; reframe as the crashed/wild-droid rescue | quest offers and completes with DW pawns | C1 |
| D0 | `DROID_ASIMOV_SAVE_SCRUB_1` | haiku | ruling 11; `rimworld-savegame` | 82 `Asimov.Need_Energy` `<li>` blocks removed from the frozen save (backup first) | count 82 → 0; save loads | A3 |
| D1 | `DROID_DONOR_REFGREP_1` | haiku | §2 risk column | per donor, every reference in `src/` and every active mod's XML | counts MEASURED, one file per donor | — |
| D2 | `DROID_RETIRE_KOTORDROIDS_1` | sonnet | B2 B3 C1 C2 C7 D1 A3 closed | flip + cold load | baseline clean | B2 B3 C1 C2 C7 |
| D3 | `DROID_RETIRE_ABF_SYNCORE_1` | sonnet | D2 | flip + cold load; `DroidsAreMachines` ABF half removed | 0 `ArtificialBeings` errors | D2 |
| D4 | `DROID_RETIRE_DEPOT_ASIMOV_1` | sonnet | D3, C2, D0; KX kind repointed | flip + cold load | 0 `Asimov` errors; FDE droids spawn | D3 |
| E1 | `DROIDWORKS_CHASSIS_PERSONALITY_1` | sonnet | triage §G; dream text §2 | per-family trait weights (data); protocol pedantry modifier | 20 spawns/family show the bias | B1 |
| E2 | `DROIDWORKS_SERVICE_RECORD_DRIFT_1` | opus | unit 11; Assembly × Service-Record | `CompServiceRecord`, chassis-weighted pools, wipe resets it | 2 years unwiped → traits accrete | B1 E1 |
| E3 | `DROIDWORKS_MODULE_PERSONALITY_1` | sonnet | unit 12; B2 | `CompModulePersonality` | wear spider-arm → trait; remove → gone | B2 |
| E4 | `DROIDWORKS_WILD_DROIDS_1` | opus | ruling 2 (crashed, crazy); unit 14 | wild-droid incident (no faction: `faction null`, hostile, erratic `MentalState`), capture → spike (Wild key) → reprogram-as-recruit with resistance | incident fires; capture loop completes | B3 C1 |
| E5 | `DROID_ORACLE_VOICE_DESIGN_1` | fable (design) | §3.4; Oracle spec | consumer contracts + prescribed fallbacks for 4 droid moments, dormant | owner review | — |

**Critical path (ruling 15)**: A1 → A2 → B3 → B4a → B4b/B9 → C1 → {C4, C5, C7} →
D2 → D3 → D4. Runnable today, before anything else: A3, D1, E5.

## 6. Anti-exponential check (`concept.md` §3) — after the rulings

| addition | risk | guardrail (ruled) |
|---|---|---|
| reassembly harness | a droid printer | **head-gate**: brain trio import-only, never a research row (ruling 6) |
| fine parts + Primitive tier | a parts ladder | Primitive parts ~40 % of donor quality; superior parts only from salvage/loot/trade — the ladder tops out at "what you can find" |
| modules | gear ladder | loot-only; fabricated ones grossly inferior (ruling 8) |
| memory wipe | reroll exploit | 7-day severe debuff + permanent quirk accretion (ruling 7) |
| protocol trade advantage | a free trade multiplier | symmetric: traders' droids work against you; the player's droid is a salvaged, brain-imported asset, not a build |
| repair-for-profit events | silver printer | payment scales with the customer's faction wealth and reputation; parts consumed are the player's own; capped incident frequency |
| chargers / spikes / bolts / detonation | — | pass (need-side, consumable, enemy-side) |

Q7: benches on the deck, brains bought where the ship flies, customers come to
the ship. Yes.

## 7. Contradictions with earlier rulings — supersession lines owed to older docs

1. **No rogue droid faction** (ruling 2) vs `droid_ruling.md` §7 (2026-08-12): *"The
   enemy is the KotOR rogue droid collective — already live"* and the 2026-08-13
   ruling *"KotOR droids are the capture-and-upgrade line"*; `droid_taxonomy.md`:
   *"KotOR is the spine… the enemy you can convert."* — The capture register
   survives; its carrier is now **the Empire's attack droids**. Also
   `droid_system_spec.md` §6 / sheet `abf_reprogram`: *"Wild droids are their own
   faction"* → wild droids are factionless crashed units (E4), not a polity.
   (`V2_DREAMS.md` B10 *"There is no independent Imperial Droid Army"* is
   consistent: droids ride the Empire's groups, no separate faction.)
2. **Programmable gets Mood** (ruling 4) vs sheet `abf_formatting`: *"Sapient brings
   the entire roster of possibilities including mental breaks and morale"* —
   morale now starts one tier lower.
3. **Brains never craftable** (ruling 6) vs `waking_mind_ai_deep_dive.md` §1:
   *"`OuterRim_DroidBrain` (item) | crafting chain under Unbolting rows | droid
   minds as manufacturable parts"* — those rows die; `required_mods.md`'s
   *"treat DroidBrains as RARE (salvage/quest-gated, don't mass-produce them)"*
   was the earlier, now-confirmed instinct.
4. **Repair-for-profit as regular events** (ruling 2) vs 2026-08-29 *"shop CUSTOMER
   layer ships as a separate quest/incident mod later; Droidworks stays pure
   platform"* — still a pack on top (C5, RUT tier), but v1 not "later".
5. **Modules fabricable at inferior grade** (ruling 8) vs sheet `abf_cradle` *"Mod
   enables, scenario down prioritizes"* — narrowed: enabled only in the Primitive
   tier, and never the brain.

## 8. Filing script (BENCH runs in this order; `--needs` per the packet's first real proof)

```
rimflow file DROID_FACTIONS_IN_FROZEN_SAVE_1 --for FOUNDRY --title "Census: which droid FactionDefs/kinds/need classes are scribed in the frozen world and campaign saves" --kind task --needs offline
rimflow file DROID_DONOR_REFGREP_1 --for FOUNDRY --title "Per-donor reference grep: every KotOR/ABF/Asimov/Depot defName and class in src/ and every active mod" --kind task --needs offline
rimflow file DROID_ORACLE_VOICE_DESIGN_1 --for FOUNDRY --title "Design (dormant): four droid Oracle consumers with prescribed fallbacks, claude -p transport" --kind task --needs offline
rimflow file DROIDWORKS_LIVE_LOOP_PROOF_1 --for FOUNDRY --title "Minimal-list quicktest proof of the five-state loop on GNK + a KotOR kind; close the 8 open live checkboxes" --kind task --needs bridge
rimflow file DROIDWORKS_FULL_LIST_COEXIST_1 --for FOUNDRY --title "Enable Droidworks in the full mod list beside the donors; cold load, texPath census, Harmony idempotency" --kind task --needs game-up
rimflow file DROIDWORKS_FORMAT_TIERS_1 --for FOUNDRY --title "Format tiers blank/mindless/programmable/sapient with needs by tier (ruling 4), work gating, format recipes" --kind task --needs offline
rimflow file DROIDWORKS_MODULE_ABSORB_1 --for FOUNDRY --title "Absorb KotOR's six-slot droid module apparel as RSW_DW_Module_* (loot-only, no recipes)" --kind task --needs offline
rimflow file DROIDWORKS_HEADS_BRAINS_SPIKES_1 --for FOUNDRY --title "Brain trio (import-only), per-family heads with CompHeadIdentity, the mindstone head, per-faction data spikes" --kind task --needs offline
rimflow file DROIDWORKS_FINE_PARTS_1 --for FOUNDRY --title "Fine parts per family (limbs, sensors, motivators, cells) with quality, drop tables and stat/personality effects" --kind task --needs offline
rimflow file DROIDWORKS_SHOP_BENCHES_1 --for FOUNDRY --title "Repair bench, reassembly harness (head-gated), rebuild-from-corpse, overclock as a bench job" --kind task --needs offline
rimflow file DROIDWORKS_BOLT_PAYOFF_1 --for FOUNDRY --title "Restraining bolt consequences: mood aura, rebellion on removal past resentment threshold, shear on damage, un-bolt-each-other" --kind task --needs offline
rimflow file DROIDWORKS_ION_SHIELD_BODYSIZE_1 --for FOUNDRY --title "Ion breaks shields (EMP side-damage) and scales by body size — merge with ION_STUN_IGNORES_BODY_SIZE_1" --kind task --needs offline
rimflow file DROIDWORKS_DETONATION_REVIEW_1 --for FOUNDRY --title "Detonation grid (energyDensity x charge) built and SAVED for the owner to walk; deny-module on JDS battle kinds" --kind task --needs bridge
rimflow file DROIDWORKS_PRIMITIVE_TIER_1 --for FOUNDRY --title "Primitive family: Jawa-fabricable frames/parts/modules at grossly inferior stats, the G2 repair droid (new art), the Junker suicide droid" --kind task --needs offline
rimflow file DROIDWORKS_WIPE_SEVERITY_1 --for FOUNDRY --title "Memory wipe: 7-day severe relearning debuff, service-record reset, permanent accreting hardware quirks" --kind task --needs offline
rimflow file DROIDWORKS_RESEARCH_ROWS_1 --for FOUNDRY --title "Seven Droidworks research rows in The Unbolting; cut the Depot droid-brain rows; brains never researchable" --kind task --needs offline
rimflow file DROID_FACTION_LOADOUTS_1 --for FOUNDRY --title "Droids in every faction's hands: Empire attack droids, Homestead utility droids, Hutt heavies, Junker suicide droids, traders' protocol droids, Trade Moot stock — no droid faction" --kind task --needs offline
rimflow file DROID_FDE_KINDS_REPOINT_1 --for FOUNDRY --title "Repoint the 4 Jawa_Droid_* FDE kinds and FDE droid backstories onto Droidworks races (fix the generator)" --kind task --needs offline
rimflow file DROID_FDE_GOODWILL_CAP_1 --for FOUNDRY --title "Free Droid Enclaves goodwill cap via GoodwillSituationDef (spec: restraining_bolt_technical.md)" --kind task --needs offline
rimflow file DROID_PROTOCOL_TRADE_ADVANTAGE_1 --for FOUNDRY --title "Protocol droid in the trade party shifts prices both ways; none on your side is a penalty" --kind task --needs offline
rimflow file DROID_REPAIR_FOR_PROFIT_EVENTS_1 --for FOUNDRY --title "Recurring event: friendlies bring droids for paid repair/upgrade; inferior/superior parts choices; offload problem droids" --kind task --needs offline
rimflow file DROID_HUTT_CAPTIVES_1 --for FOUNDRY --title "Droids held in Hutt torture chambers as a rescue-or-purchase source at Hutt sites" --kind task --needs offline
rimflow file DROID_DISTRESS_CALL_REPOINT_1 --for FOUNDRY --title "Re-point the BTD Droid Distress Call quest's 5 KotOR kinds to Droidworks kinds; reframe as the crashed-droid rescue" --kind task --needs offline
rimflow file DROID_ASIMOV_SAVE_SCRUB_1 --for FOUNDRY --title "Scrub the 82 inert Asimov.Need_Energy entries from WORLDMAP_V1_original.rws (backup first)" --kind task --needs offline
rimflow file DROID_RETIRE_KOTORDROIDS_1 --for FOUNDRY --title "Retire guy762.kotordroids (wave R1) after modules, heads, loadouts, FDE repoint and Distress Call are closed; cold load" --kind task --needs game-up
rimflow file DROID_RETIRE_ABF_SYNCORE_1 --for FOUNDRY --title "Retire ABF + SynCore (wave R2); DroidDonor_ABFGate fires; remove DroidsAreMachines ABF half; cold load" --kind task --needs game-up
rimflow file DROID_RETIRE_DEPOT_ASIMOV_1 --for FOUNDRY --title "Retire Droid Depot + Asimov + MSEDroidFix (wave R3); repoint the Empire KX kind; retire NoDroidManufacture; cold load" --kind task --needs game-up
rimflow file DROIDWORKS_CHASSIS_PERSONALITY_1 --for FOUNDRY --title "Per-family starting-trait weights and the protocol-droid pedantry social modifier" --kind task --needs offline
rimflow file DROIDWORKS_SERVICE_RECORD_DRIFT_1 --for FOUNDRY --title "CompServiceRecord: time-since-wipe accretes chassis-weighted idiosyncrasies; wipe resets" --kind task --needs offline
rimflow file DROIDWORKS_MODULE_PERSONALITY_1 --for FOUNDRY --title "Installed modules carry attitudes: CompModulePersonality trait-hediffs while worn" --kind task --needs offline
rimflow file DROIDWORKS_WILD_DROIDS_1 --for FOUNDRY --title "Wild crashed droids: factionless erratic hostiles, capture -> Wild spike -> reprogram-as-recruit with resistance" --kind task --needs offline
```
