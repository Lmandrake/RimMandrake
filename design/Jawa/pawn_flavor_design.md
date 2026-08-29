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

- **Rebellion walk APPROVED**: Unbending→Broken as trait degrees flipped by a
  Harmony hook on vanilla's existing slave-rebellion resolution. ⛔ No fourth
  resistance meter, no new bar, no new UI — the trait degree IS the state.
- **Wildsteam are NOT a steam cult** — see the canon note in
  `worldbuilding/FACTION_SPEC.md` §6. Life-web reverence; the name means
  spring-mist. Their set is remade below.
- **Droids may become their own v2 system** — the assembly×service-record space
  plus restraining bolts, data spikes, memory wipes as mechanics. Keep the droid
  set growing here but design it detachable.
- **Warcasket flag, unresolved**: VFE-Pirates' `Salvagers` faction exists on the
  frozen world alongside `Jawa_Junkers` and also fields warcasket kinds
  (`VFEP_Salvager_Warcasket`). If caskets are the Junkers' signature, Salvagers
  need re-relating/retheming — owner has not ruled.

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

## Per-faction sets (rounds 2–3 depth)

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

### The capture-economy matrix (design spine, completed)
Empire no-ransom/Broken-prone · Hutts everything-for-sale · Tribes conversion ·
Geonosians hive-mass logistics · Helix hunted assets/containment · Blackstar
swaps and the truce token · Homestead morally-ugly excellence · Wildsteam
landscape-for-them + liberation raids · Junkers fear/eagerness. **Free Droid
Enclaves / Forgotten Arsenal** feed the droid set (next: the deep droid pass).

## Implementation ceilings (informational, not yet ruled)
Most stat/mood/thought content is stock XML. Light-C# tier: rebellion-walk hook,
Droid-Whisperer soothe, Beast-Sung calm, Web-Minded species count, hidden-
backstory reveal, skill-return event, aim-vs-moving. The full droid system
(bolts/spikes/wipes as verbs) is v2-scale C#.

## Open questions
1. Salvagers vs Junkers casket exclusivity (see rulings).
2. Wrong-fiction cuts: rule the Isekai/Minotaur/Medieval/VQE/Archon sets.
3. "etc." scope: ThoughtDef labels, MentalBreakDef flavor, xenotype titles —
   in or out of this item.
4. Remaining six factions to full three-layer depth.
5. Slave-arc pieces in v1 core vs later (Collared Expertise is the C#-hungriest).
6. Phase 2 (lore prose pass) starts only after the owner calls phase 1 wide enough.
