<!-- status: live — BENCH working design, PAWN_FLAVOR_STARWARS_1 -->
# Pawn Flavor — backstories, childhoods, traits (design in progress)

**Item**: `PAWN_FLAVOR_STARWARS_1`. Owner's charge (2026-08-29, verbatim): "assess
and make star wars compliant all backgrounds, childhoods, traits, etc. Make them
robust, interesting, and star wars themes where appropriate. Work with the user to
define this richly."

**Method, per the owner**: two phases — (1) brainstorm the gameplay possibility
space thoroughly; (2) THEN dress the winners in Star Wars lore and prose. This doc
is phase 1 in progress. Names below are placeholders unless marked homage.

## Rulings so far (owner, 2026-08-29)

- **VOLUME MANDATE (owner, 2026-08-29, third sitting, verbatim intent):** per
  faction, AT LEAST **5 unique childhoods** (one the "common" one), **10
  adulthoods** (one common/boring), and **15 traits to select from** — the trait
  pools mined from vanilla + the trait-expansion mods (VTE 53, RimTraits 46,
  Core 43, …) and down-selected per faction's definition, racial mix and
  ideoligion. Terminology settled: "backstory" is the engine's one def type;
  childhood/adulthood are its two slots. ISEKAI's 47 traits are leveling
  content for everyone and do NOT satisfy the faction pools.
  Mechanism note (not yet ruled): traits are not faction-scoped natively —
  steering rides BackstoryDef forcedTraits/disallowedTraits (plain XML) or a
  spawn hook (C#); the 15-per-faction pool is design-level selection first.

- **Wrong-fiction cuts RULED (owner, 2026-08-29, second sitting)**: cut Minotaur
  (37), Medieval (27), VQE Ancients (27), VRE Archon (52) — PURE-SW style, Cherry
  Picker + the moderation skill's post-cut checks. **ISEKAI (47) is PENDED, not
  spared**: owner verbatim — *"Cut all except ISEKAI... can we put ours in for
  its? I assume it wires up its leveling system into what it's got somehow?
  Investigate."* ⇒ investigate whether the RPG-leveling framework can drive OUR
  Star Wars traits/backstories in place of its shipped 47; cut or rewire on the
  answer.
- **"etc." scope RULED: ALL of it** — ThoughtDef labels, MentalBreakDef flavor,
  xenotype titles are all IN this item. Multi-session prose arc accepted.
- **Salvagers FOLD INTO Junkers (owner, 2026-08-29)** — one casket faction.
  VFE-Pirates' `Salvagers` world presence re-points at `Jawa_Junkers`; casket
  identity stays Junker-exclusive by construction. Canon entry:
  `infrastructure/state/canon.yml > ruled > SALVAGERS_FOLD_JUNKERS`.
- **Work order RULED**: cuts first, then deepen the thin factions, then the
  phase-2 prose pass — "for everything", i.e. the full etc. scope rides the same
  three-step order.

- **Rebellion walk APPROVED**: Unbending→Broken as trait degrees flipped by a
  Harmony hook on vanilla's existing slave-rebellion resolution. ⛔ No fourth
  resistance meter, no new bar, no new UI — the trait degree IS the state.
- **Wildsteam are NOT a steam cult** — see the canon note in
  `worldbuilding/FACTION_SPEC.md` §6. Life-web reverence; the name means
  spring-mist. Their set is remade below.
- **Droids may become their own v2 system** — the assembly×service-record space
  plus restraining bolts, data spikes, memory wipes as mechanics. Keep the droid
  set growing here but design it detachable.
- **Droid system: spec then PARK (owner, later 2026-08-29).** V1 plays all three
  shipped frameworks raw, unrationalized. The droid flavor layer here does NOT
  wait on a spine — plain BackstoryDefs fit KotOR's shipped spawn categories;
  whether to author them in v1 is this item's own scoping call. Full ruling:
  `infrastructure/state/queue/items/DROID_SYSTEM_EMBRACE_1.md`.
- **Warcasket flag RULED and EXECUTED (owner, 2026-08-29): fold Salvagers into
  Junkers.** Correction: `Salvagers` is ODYSSEY's faction (VFEP injects its
  `VFEP_Salvager_Warcasket` kind), not VFE-Pirates'. On the frozen world it held
  zero settlements — the fold is `<defeated>True</defeated>` scribed into its
  block ("The Comet Party", loadID 24) in WORLDMAP_V1_original.rws, backup
  `.pre_salvager_fold_2026-08-29.rws`. Caskets are Junker-exclusive in play.

## Census (2026-08-29, 582-mod dump `d1be0632`)

1,225 BackstoryDefs: ~1,017 generic vanilla (Core 784, VBE 174, Royalty 59); ~34
already SW (KotOR Droids 19, KotOR Resources 13, Droid Depot 2); ~145 wrong-fiction
(Minotaur 37, Medieval 27, VQE Ancients 27, VRE Archon 52). 266 TraitDefs: mostly
fiction-neutral frameworks; ISEKAI RPG LEVELING (47) is the loud offender; The
Force – Lightsaber (7) already SW. No `mandrake.*` mod authors either def type yet.
Wrong-fiction sets are expected to be CUT (Cherry Picker + the moderation skill's
post-cut checks) and replaced by the volume below — not yet ruled item-by-item.

## The design spine

Every faction answers "why raid them, why enslave theirs, why free them"
differently. Per faction: themed **childhoods** × themed **adulthoods**
(combinatorics free in-faction, cross-faction drift allowed for drama) + a
**trait pool** weighted by faction and species mix.

## Cross-cutting slave mechanics

- **Ransomable** — origin faction pays; income vs workforce decision.
- **Rescue-Worthy** — origin faction raids to retrieve this pawn specifically.
- **Unbending / Broken** — approved, see rulings. Unbending: resists suppression,
  keeps signature bonuses. Broken: docile, signature bonus halved.
- **Collared Expertise** — some skills usable only when trusted/freed; freeing is
  a gameplay verb (buy low, free high — very Jawa).
- Wildsteam captives interlock with canon: their faction already runs Liberation
  raids against slaver factions — keeping Wildsteam slaves invites them.

## Family A–H: the faction-agnostic seed set (round 1)

A. **Trade-off engines**: Scavenger's Eye (salvage bonus / hoarder mood);
Jury-Rigger (fast+cheap crafts / breakdown-prone output); Podracer's Reflexes
(speed+dodge / bad ranged aim, reckless-charge break); Void-Touched (high psychic
sensitivity cuts both ways — stock XML).
B. **Story generators**: Debt to the Hutts (periodic tithe-or-raid); Imperial
Deserter (Empire relations penalty while present; capture becomes a raid goal);
Carries a Secret (hidden second backstory revealed on trigger); Last of the Crew
(grief thought converts to buff after N new bonds).
C. **Relationship/clan**: Clan-Born (kin-link web on shared tag); Master-and-
Apprentice (paired, double learning, separation penalty); Sworn Rival (hostile
links to a category, payoff on reconciliation).
D. **Environmental adaptation**: Dune-Raised (heat/sand mastery, roof-sick);
Vault-Born (inverse); Water-Discipline (low needs, colony-waste mood hit).
E. **Craft/salvage/economy**: Droid-Whisperer (droid affinity, soothe berserk
droids — light C#); Tinkerer's Childhood (crafting passion + restorable heirloom
possession); Haggler of the Sand Bazaars (trade bonus, follow-up-visitor risk).
F. **Combat identities**: Stormtrooper Washout (aim penalty vs moving targets —
C#, on-lore); War-Echoed (flashback break with decay-on-calm-battles recovery
curve); Shield-Line Veteran (adjacency formation bonus).
G. **Force spectrum**: Latent/Awakened/Trained trait ladder (psychic sensitivity,
meditation, rare top-end abilities; childhoods feed it without guaranteeing it);
Force-Null (psychic immunity, no psycasts, unsettling aura).
H. **Two-act arcs**: childhoods that MODIFY any adulthood (Sold Young → freed-
slave interactions; Sandcrawler-Born → mech-work bonus on craft adulthoods).

Family placement: A/C/E → Jawa Trade Moot (Moot variants lean trade/kin);
D-hard → Deep Desert Tribes; D-technical stays Jawa.

## Round 6 — the volume mandate is MET (2026-08-29, third sitting)

**Owner, 2026-08-29, on the 401-row register: "I'm going to go with them as is
for now. No further review for now."** ⇒ the round-6 roster is accepted AS-IS,
including the seven contested-flagged inventions; the review sheet stays open
for later passes but nothing waits on it. Build proceeds on this roster.

All 12 factions now carry ≥5 childhoods (1 COMMON), ≥10 adulthoods (1 COMMON)
and ≥15-trait pools. 🔑 **The roster of record moved out of this doc**: it lives
in `src/RimMandrake/Utils/gen_pawn_flavor_register.py` (single-sourced into the
review sheet `design/Jawa/worldbuilding/review/pawn_flavor_register.html`,
401 rows). This doc keeps mechanics, capture economies and rulings; the
per-faction item lists below are HISTORY, not the roster. Round 6 items were
drafted by four subagents from the INHABITED cast files
(`design/Jawa/bridge/INHABITED_CAST_*.md`) — most entries cite the character
that inspired them.

**Invented in round 6, flagged for the owner (contested rows in the sheet):**
Deepwater "Jetty-Taught" childhood + "Jetty Hand" adulthood (from the cast's
own catechism, no doc source); Junkers "Junk-Reckoner" trait; Homestead
"Death-Bed Sitter" (dark register); droid traits "Continuity-Bound",
"Chassis-Proud", "Wipe-Averse/Wipe-Ready". Trait pools are existing-mod PICKS
(status `pool-pick`), steered per faction via backstory
forcedTraits/disallowedTraits (XML) or a spawn hook (C#) — mechanism not yet
ruled.

## Per-faction sets (rounds 2–3 depth) — ⚠ superseded for the ROSTER by round 6

### Homestead Defense League — the Tatooine homage set
Childhoods: **Farm-Fostered** (Luke: learns from elders; horizon-yearning debuff
converts to permanent buff on first caravan off-map); **Vaporator Apprentice**;
**Raider-Orphaned** (combat buff, fire-fear break weight).
Adulthoods: **Moisture Baron** (Owen: plant/animal mastery, resists recruitment
AND enslavement); **Homestead Matron** (Beru: cooking/medical, colony mood aura);
**Hermit of the Wastes** (Obi-Wan: old, melee/medicine/social, HIDDEN Force-latent
flag that can fire late); **Militia Sergeant** (passive shooting trainer).
Traits: patient, stubborn, provincial ("uneasy off-world"), quietly brave.
Slave note: farm captives are superb and morally ugly to take — flavor working.

### Wildsteam Clan — REMADE (life-web covenant, not steam)
Childhoods: **Spring-Sworn** (plant/animal bonus; needs green — mood debuff when
few growing plants nearby); **Canopy-Cradled** (animals passion, bonded-animal
start); **Drought-Marked** (water-discipline; break weight spikes in heat waves).
Adulthoods: **Web-Tender** (plants/medicine elite; refuses hunting — workDisables);
**Seed-Carrier** (sows on caravan, growing-speed aura); **Freehold Warrior** (the
canon line "devastating at home, near-useless anywhere else" AS a trait: combat
bonus on home map/near water, penalty raiding out); **Beast-Sung** (handling
savant, calm-manhunter ability — light C#; severe grief on bonded death);
**The Small Elder** (HOMAGE, retained and re-rooted: ancient exile hiding in the
life-web — frail, awful on paper, hidden top-degree Force trait + teaching aura).
Traits: **Web-Minded** (mood scales with count of distinct living species on map —
C#, signature mechanic); **Green-Grief** (mass plant destruction mood hit);
**Rooted** (home bonus, hates travel); **Life-Debt** (strong bond to healer).
Slave note: they wilt — easy to suppress, mood collapses without a garden; and
their faction liberation-raids slavers (canon). A slave you must landscape for.

### Junkers — everything orbits the casket
Childhoods: **Casket-Cradled** (immune to casket-fear thoughts, social bonus to
casket pawns); **Scrap-Sifter** (E-family, cruder).
Adulthoods: **Casket-Bound** (in a warcasket; VFEP hediffs carry mechanics, we
author the story: irreversible, social debuffs, combat monster); **Casket-Wright**
(crafting elite, desensitized: no gore/death-witness mood hits); **Casket-Denied**
(rejected volunteer: envy interactions toward Casket-Bound, +work speed from
frantic ambition, permanent small mood debuff); **Wall-of-Meat Veteran**
(adjacency bonus, unarmored doctrine).
Trait axis: **Casket-Dreamer** (mood buff near caskets, wants in) vs
**Casket-Haunted** (fear: debuff near them, refuses surgery) — assigned across
Junkers AND leaking to captives of other factions reacting to YOUR caskets.

### Droids — the flagship set (v2-system candidate)
Reframed slots: **Assembly** (childhood) × **Service Record** (adulthood).
Variance deliberately NOT centered on zero: the market prices it — god-rolls are
rare finds, junk-rolls are the Jawa resale economy.
Assemblies: **Factory-Fresh** (boring on purpose); **Battlefield Salvage** (combat
stats, missing capacity); **Artisan Hand-Build** (one savant skill, one crippled);
**Frankenframe** (stats re-roll on each down-and-repair); **Cursed Line** (cheap,
one guaranteed severe quirk).
Service Records: **Three Centuries of Protocol** (social/trade monster, absolute
pacifist); **Memory-Wiped ×N** (degrees: lower skills, faster learning, sudden
skill-return event chance); **War-Surplus** (shooting elite, anti-droid targeting
bonus — Arsenal flavor); **Restraining-Bolt Decades** (tireless, berserk-on-
liberation risk); **Companion-Imprinted** (R2 pairing: huge buffs near ONE
colonist, useless after their death); **Corrupted Core** (savant + periodic
scrambled wander/babble state).
v2 hooks the owner named: restraining bolts, data spikes, memory wipes as active
mechanics, not just history.

### Galactic Empire — the procedural occupier (round 4)
Capture economy: permanent enemy → no goodwill, NO ransom; the Empire retrieves
or erases, never buys. Pure slave-or-recruit pipeline.
Childhoods: **Academy Cadet** (combat floors raised, passions rare, disciplined
sleep); **Garrison Brat** (social bonus with any faction's pawns, low recruitment
resistance — never belonged, just lived there); **Core-Worlds Evacuee** (fast
learner; "displaced" debuff fading with time in one owned bedroom).
Adulthoods: **Stormtrooper** (mass line: formation bonus, helmeted anonymity —
low grief for comrades, small social penalty; spawns closer to Broken);
**Imperial Deserter** (from B-family; Empire "rescue" is a death squad);
**Requisitions Officer** (inventory savant, mood from colony cleanliness);
**Propaganda Auditor** (conversion elite, others' opinion of them decays);
**Inquisitorial Washout** (rare: failed Force-adept, haunted breaks, hidden
ladder potential with dark-flavored berserk breaks).
Traits: **Order-Bound** (mood tied to kept schedule), **Rank-Minded** (opinion
bonus to higher-skilled pawns), **Numbered** (bonds slowly, insult-immune).

### Hutt Cartel — everything is for sale (round 4)
Capture economy: the ransom anchor — the Cartel ALWAYS pays for its own; no
liberation raids, business is business.
Childhoods: **Palace-Raised** (social/art, spoiled: permanent expectation floor);
**Debt-Born** (+work speed, windfalls barely register); **Toll-Gate Child**
(trade savant, gift-giving mood penalty).
Adulthoods: **Majordomo** (peak ransom); **Collection Enforcer** (melee + warden
aura: slaves suppress faster nearby); **Spice-Runner** (fast, latent addiction
under stress); **Cistern Auditor** (colony spoilage reduced); **Freed Proxy**
(social elite, Cartel opinion floor permanently low).
Traits: **Transactional** (favor/slight opinion swings doubled), **Appetite**,
**Cold-Blooded**.

### Deep Desert Tribes — the conversion arc (round 4)
Capture economy: convertible via adoption (canon); until converted their faith
attacks your infrastructure.
Childhoods: **Sun-Sworn Child** (hard D-family: sandstorm immunity, roofed
penalty); **Krayt-Watcher** (animals+shooting, dodge vs beasts);
**Water-Priest's Ward** (mood HIT while colony runs vaporators — sacrilege as
mechanic; conversion clears it).
Adulthoods: **Water-Raider** (fast, high carry, combat bonus decaying in-fight —
strike and vanish); **Bantha-Bonded** (bonded pack animal, caravan speed);
**Sun-Debt Cantor** (conversion priest, heat-immune); **Adopted Outsider** (any
species, fast learner, low resistance).
Traits: **Water-Pious**, **Vengeful**, **Stoic**.

### Geonosian Foundry Hive — the hive economy (round 4)
Capture economy: no trade, no ransom, no rescue — losses unacknowledged;
captives are forever IF you sustain hive-mass.
Childhoods: **Hatched to the Line** (drone: tireless, low rest, crafting floor,
mood spiral below 3 hive-kin); **Winged Brood** (aristocrat: social/intellect,
move bonus, disdain toward drones).
Adulthoods: **Foundry Artisan** (crafting savant, droid-repair synergy — v2
droid-system hook); **Siege-Caller** (construction+mortars); **Jedi-Hunt
Veteran** (damage bonus vs psychically sensitive, slight psychic deafness);
**Queen's Attendant** (rare: counts as multiple hive-kin for others — makes
drone-keeping viable).
Traits: **Hive-Tuned** (mood averages toward nearby Geonosians — C#),
**Tireless**, **Chitin-Proud**.

### Ascendant Helix — two populations, one cult (round 4)
Capture economy: retrieval and containment; their Made they destroy rather than
free. Two pawn streams: Curators and the manufactured underclass (the Made).
Childhoods: **Design-Born** (curator: excellence + one random "editing scar");
**Vat-Decanted** (the Made: no memories — fastest learning in game, zero
starting passions, mood buff per passion gained later); **Catalogue Orphan**
(discarded line: random genes, flagged "recall item").
Adulthoods: **Gene-Curator** (medical/research elite, no mood from prisoner
surgery); **Retrieval Agent** (capture specialist); **Escaped Asset** (strong,
HUNTED — Helix retrievals target them alive; recruiting = accepting the raids);
**Bioweapon Warden** (toxin/disease immune, unsettling).
Traits: **Perfected** (global bonus + sterile), **Catalogued**
(suppression-friendly), **Draft-Hater** (opinion penalty toward baseliners).

### Blackstar Company — the Code (round 4)
Capture economy: no money ransom — honored EXCHANGES (prisoner swaps); few
entries, all vivid (canon: "one dangerous person with a name").
Childhoods: **Raised on Retainer** (weapons early; mood hit when colony attacks
traders/caravans); **Bounty Posted Young** (fast, light sleeper, ambush-hard).
Adulthoods: **Named Hunter** (elite combat; holding them SPIKES Blackstar raids,
freeing them fires a one-time truce event — the only lever on a permanent enemy,
via the Code; C#, worth it); **Contract Broker** (negotiation elite, colony
ransom bonus); **Disgraced Hunter** (full skills, on the kill-list, self-loathing
breaks converting to loyalty after N defenses — Last-of-the-Crew shape).
Traits: **The Code** (professional-pride mood after clean victories),
**Laconic**, **Gear-Proud** (mood from equipped weapon quality — feeds the Jawa
economy loop).

### Jawa Trade Moot — the kin set (round 5, 2026-08-29)
THE PLAYER'S OWN PEOPLE (shares The Salvation; FACTION_SPEC R19). Capture
economy: taking Moot pawns is a taboo the colony itself feels — same-ideo
guests convert trivially but enslaving them is the one act the fiction says
kin do not forgive; the Moot ransoms generously and REMEMBERS, both
directions. Shipped five claimed by this set: **Sandcrawler-Born** and
**Tinkerer's Child** (childhoods), **Bazaar Haggler**, **Salvage Master**,
**Moot Speaker** (adulthoods).
Extension childhoods: **Offworlder's Shadow** (creche translator for spacer
crews: social/intellect, wanderlust thought); **Salvage-Sifter** (E-family
cruder: mining/hauling floors, hoarder mood).
Extension adulthoods: **Utinni Prospector** (mining/ruins savant, greed-spike
break weight); **Crawler Mechanic** (construction/craft elite, breakdown
affinity); **Droidwright of the Moot** (droid affinity — the droid-system
bridge, pairs with DROID_SYSTEM_EMBRACE_1).
Traits: **Utinni!** (mood buff on acquiring new things — C#, the signature);
**Kin-Web** (opinion bonus across Moot/Jawa pawns — C#); **Chatter-Trade**
(trade-price statOffsets — plain XML, shippable now).

### Deepwater Compact — armed neutrality (round 5, 2026-08-29)
FACTION_SPEC §7: amphibian water monopolists, secular (the Balance), sell to
EVERYONE including the Empire; `raidsForbidden` — wardens dehydrate off-water
and both of you know it. Capture economy: the Compact pays ransom promptly in
silver and water contracts — reliable, capped, unsentimental; an enslaved
warden is INFRASTRUCTURE-HUNGRY (needs water access to stay sane — the
signature trait below), and while you hold one the Compact's caravans stop
carrying water to YOUR beacon (fiction v1); freeing one buys the Balance's
quiet favor.
Childhoods: **Cistern-Hatched** (swimming before walking: construction/
medicine floors, heat-wave break weight); **Toll-Wharf Child** (every bucket
metered: social+melee floors, gift-giving mood penalty); **Drought-Witness**
(saw a reservoir fail: water discipline, hoards water, resists heat breaks).
Adulthoods: **Water Warden** (defense elite at home/near water, penalty
raiding out — Freehold Warrior's mechanic, C# conditional); **Purification
Engineer** (construction/intellect elite, hygiene-mod synergy);
**Balance Arbiter** (secular judge: social elite, conversion-resistant both
ways); **Reservoir Cartographer** (caravan speed, scout); **Compact Factor**
(trade elite, no mood from selling to anyone's enemy).
Traits: **Amphibian-Blooded** (mood/health scales with water access — C#,
signature; a slave you must plumb for); **Neutral to the Bone** (damped
opinion swings, conversion resistance); **Monopolist** (sell-price bonus,
gift-giving mood hit); **Still-Water Patience** (lower break weights, slower
work).

### The capture-economy matrix (design spine, completed)
Empire no-ransom/Broken-prone · Hutts everything-for-sale · Tribes conversion ·
Geonosians hive-mass logistics · Helix hunted assets/containment · Blackstar
swaps and the truce token · Homestead morally-ugly excellence · Wildsteam
landscape-for-them + liberation raids · Junkers fear/eagerness · **Moot
kin-taboo + generous remembering ransom · Deepwater prompt capped ransom +
plumb-for-them slaves** (round 5). **Free Droid Enclaves / Forgotten Arsenal**
feed the droid set (next: the deep droid pass).

## Implementation ceilings (informational, not yet ruled)
Most stat/mood/thought content is stock XML. Light-C# tier: rebellion-walk hook,
Droid-Whisperer soothe, Beast-Sung calm, Web-Minded species count, hidden-
backstory reveal, skill-return event, aim-vs-moving. The full droid system
(bolts/spikes/wipes as verbs) is v2-scale C#.

## Open questions
1. ~~Salvagers vs Junkers~~ RULED: fold Salvagers into Junkers (see rulings).
2. ~~Wrong-fiction cuts~~ RULED: cut Minotaur/Medieval/VQE/Archon now; ISEKAI
   pends the leveling-rewire investigation (see rulings).
3. ~~"etc." scope~~ RULED: all of it is in (see rulings).
4. ~~Remaining six factions~~ RESOLVED 2026-08-29: "six" was stale (written
   before round 4). Round 5 added the real remainder — Jawa Trade Moot and
   Deepwater Compact are now at full depth; Free Droid Enclaves stays parked
   with DROID_SYSTEM_EMBRACE_1; the Forgotten Arsenal has no human pawns.
5. Slave-arc pieces in v1 core vs later (Collared Expertise is the C#-hungriest).
6. Phase 2 (lore prose pass) — runs THIRD, after cuts and faction depth, over
   everything including ThoughtDef/MentalBreakDef/xenotype-title flavor.

## CUT PASS EXECUTED (2026-08-29, second sitting — verification owed at next load)

143 Cherry Picker entries written (config 1342 -> 1485 keys, backup
`Mod_CherryPicker.xml.bak-20260829-pawnflavor`): 141 BackstoryDefs from
tug.minotaur (36), shavius.medieval.flavour (26), vanillaquestsexpanded.ancients
(27), vanillaracesexpanded.archon (52) + 2 TraitDefs (RBM_Herculean_Trait,
VQE_IdealPatient). **Excluded on campaign-save evidence**: `RBM_Roamer` and
`SH_MED_MedievalAlchemist` — one pawn each in WORLDMAP_V1_original.rws carries
them; swap those in the save when SW replacements exist, then cut them too.

Post-cut analysis (dump d1be0632, engine source read):
- General pools cleaned: Offworld -12, Outlander -12, Raider -11, Pirate -2,
  Cult -2, GTGTC approvals -5..7 each; all keep hundreds of survivors.
- 10 mod-private categories go to ZERO (Minotaur x4, Medieval x2, Classical,
  VQE x2, Archon). Consumers: the cut mods' own kinds/factions (not in the
  frozen world's cast) + `VRESaurids_TownGuard_Saurid` (MinotaurOutlander) and
  VQE quest patients. Engine behavior on an empty category is CONFIRMED benign:
  `PawnBioAndNameGenerator.FillBackstorySlotShuffled` logs one error and picks a
  random backstory — no crash. VQE Ancients quest patients will carry random
  backstories; if that noise offends, the follow-up is cutting VQE quest content
  itself (not ruled — raise with the owner).
- ⚠️ BackstoryDef is an UNPRECEDENTED def type in this config (no prior entries).
  Cherry Picker support is proven only by the next load's
  `[Cherry Picker] ... defs were removed:` lines — that check rides
  COLD_LOAD_RUN_SHEET_2. If unsupported, fallback is spawnCategories-neutering
  patches.

## ISEKAI investigation (2026-08-29, answered — awaiting the owner's word)

Its 47 traits are vanilla-class TraitDefs (no Class=, no modExtensions), but
every leveling hook — XP multipliers, stat/star bonuses, NPC trait rolling,
rank grants (`Isekai_Rank_<X>` literal name pattern), color-coding — is
hardcoded to those 47 defNames in its C# (`IsekaiTraitHelper.cs`,
`PawnStatGenerator.cs`). Its grant-items resolve `traitDefName` GENERICALLY, so
they can hand out foreign traits too. ⇒ **Cutting the 47 breaks the mod;
reflavoring them in place (keep defNames, patch labels/descs/degree text to
Star Wars) keeps all machinery working** — that is the "put ours in for its"
route, plus optional grant-items for our `Jawa_` traits. No backstories shipped;
no backstory machinery to worry about. Recommendation: reflavor-in-place.

**EXECUTED 2026-08-29 (owner's yes at the bench):**
`Jawa_Patches/Patches/IsekaiTraits_StarWarsReflavor.xml`, deployed. Five
origins → Chosen One / Dark Side Ascendant / Force Echo / Foresight-Touched /
Outlander; the 10-rank ladder → Bounty Hunters' Guild threat ratings (letters
kept), Rank Nation → sector-class threat. Mechanics bullets and
conflictingTraits untouched; the 32 genre-neutral traits left as shipped.
First-load check on COLD_LOAD_RUN_SHEET_2. Still open (owner's call, later):
grant-items handing out `Jawa_` traits through its generic
`CompProperties_UseEffectIsekaiTrait`.

## SHIPPED v1 content (2026-08-29, `Jawa_PawnFlavor`, commit fb86639a)

50 BackstoryDefs (2 childhoods + 3 adulthoods × 10 factions) and 5 TraitDefs
(Jawa_WaterDiscipline, Jawa_SandStoic, Jawa_Numbered, Jawa_Laconic,
Jawa_PodracerReflexes), wired via one filter per faction (JawaBSC_*). Deployed,
active at load position 581; first-load verification lives in
COLD_LOAD_RUN_SHEET_2. Everything XML could express shipped; every mechanic
needing C# remains designed-not-built — the authoritative deferred list is in
the mod's About.xml (rebellion walk hook, proximity/mood traits, schedule and
opinion traits, conditional combat bonuses, hidden reveals, Blackstar truce).
Droid backstories deliberately absent (parked with DROID_SYSTEM_EMBRACE_1).
