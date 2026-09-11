# Star Wars proper-noun raid — repo docs + this session's judgment calls

Deliverable of a disk-raid research pass (2026-09-11). Sources actually read in
full or in substantial part are listed at the bottom. This is a SEED LIST for a
later merge step — no game/mod files were touched.

---

## PART 1 — Explicit canon-vs-reimagine rulings found verbatim

These are the load-bearing judgment calls a merge step needs. Quoted or
closely paraphrased with source.

1. **"Iconic Star Wars status protects completely."** — owner, 2026-09-05,
   `creature_recognizability_rule.md` §"THE STAR WARS ICON CARVE-OUT". The
   Earth-animal recognizability CUT rule inverts for in-universe SW icons: a
   bantha that reads as a bantha, a dewback that reads as a dewback, an
   astromech that reads as an astromech is the campaign WORKING, not failing.
   Iconic SW creatures/droids are exempt from the cut rule outright, and a
   MISSING SW icon is an opportunity to reskin/recreate something into it.

2. **`starwars_iconic_creatures.md`** is itself a standing ruling-in-progress:
   a 68-creature research catalogue of every findable iconic SW creature,
   each tagged FIT-CORE / FIT-POSSIBLE / FIT-POOR / UNCERTAIN for fit to
   Ash'karr, explicitly marked "a research catalogue, not a ruling — nothing
   here is authored into the game." Cross-referenced against the live 595-mod
   set: **27 of 28 live SW icons come from Star Wars Animal Collection
   (Continued)**, ruled "protected content." Six creatures were named as the
   real gap / recreate worklist: Luggabeast, Sarlacc, Steelpecker, Rakghoul,
   Firaxan shark, Profogg.

3. **`donor_proper_noun_backlog.md`**: explicitly checked and ruled OUT (not a
   canon clash) — **"SW-flavored donor factions (Outer Rim's Galactic Empire /
   Rebel Alliance / moisture farmers / binary star raiders, VFE Pirates'
   Junkers, VFE Tribals' Wild Men) — surface-checked... all read as near-lore
   already."** Also explicitly ruled: `HoraxCult` (Anomaly DLC) is **vanilla
   RimWorld canon, not donor content, out of scope** — i.e. NOT a Star Wars
   proper noun despite superficially SW-adjacent naming.

4. **Latin-dinosaur creature renaming rule** (`creature_names_ashkarr.md`,
   DECIDE 2026-08-22): non-SW donor creatures with Latin binomial names
   (Jurassic Rimworld, Megafauna) get invented Star-Wars-STYLE (not
   Star-Wars-IDENTITY) names via a phonetic clade system — these are
   REIMAGINED, not canon SW creatures wearing a new label. English-compound
   names (`dunbear`, `duskhorn`, `manehound`, `hellboar`, `sporemole`) are
   explicitly kept as "spacer slang" nicknames, not renamed.

5. **Recognizability doctrine `creature_recognizability_rule.md`**: full
   decision matrix —
   | art | mechanics | verdict |
   |---|---|---|
   | recognizable (as an Earth animal) | ordinary | CUT |
   | recognizable | unique custom mechanics | REGENERATE ART + RENAME |
   | strange (unrecognizable as Earth) | anything | KEEP |
   — this is the rule an SW-canon creature is EXEMPT from (see #1).

6. **`infrastructure/artpipe/README.md` "improve" semantics ruling** (owner,
   2026-09-11, referenced by ART_REGEN_WAVE4/5): for the `art: "improve"`
   bucket specifically — **"Star Wars-named creatures keep their canon
   identity, non-SW names are free to be reimagined (general kind fixed,
   specific name/character not)."** This is the operative rule the art waves
   below apply creature-by-creature.

7. **ART_REGEN_WAVE1_WIRE_IN_1** (2026-09-11): names explicitly labeled
   "Star Wars canon 'redo' creatures, reference gathered online per the
   redo-semantics ruling": **Kreetle, Horax, Fambaa, Dragonsnake, Zakkeg**
   (art fully regenerated but IDENTITY/name kept as canon SW creatures, no
   rename).

8. **ART_REGEN_WAVE4_QUEUE_1** (2026-09-11) — worked example of the
   canon-vs-reimagine split under ruling #6:
   - SW-canon, identity KEPT: **Ronto, Anooba, Dewback**.
   - Non-SW donor names, REIMAGINED (general kind kept, name invented):
     `GR_ParagonRat` → **Grithe**, `BMT_Maligoat` → **Kroffa**,
     `GR_Molebear` → **Grutt**, `BMT_FleeceSpider` → **Puffmite**.

9. **ART_REGEN_WAVE5_QUEUE_1** (2026-09-11) — second worked example:
   - SW-canon, identity KEPT: **GreaterKraytDragon, Vornskyr, Orray**.
   - Non-SW, REIMAGINED: `RSW_Yobshrimp` → **FeatherFeel** (owner-mandated
     rename per the row's own note), `Jamel` → **Duskram**,
     `BMT_FoundryBeetle` → **Slagmaw**.
   - `AA_Terramorph`: name explicitly KEPT AS-IS (not SW, not renamed) because
     a prior 2026-09-10 sitting had already given it an earned lore identity
     ("dayside lurker") — cited as the carve-out's own exception clause
     ("if the current one doesn't earn its place... this one does").

10. **ANCIENTS_AS_RAKATA_SPEC.md** (owner, 2026-08-20, reaffirmed 2026-08-29):
    **the frozen "Ancients" sleepers ARE the Rakata** (genuine KOTOR/Legends
    Star Wars precursor species) — endonym `Rakata`, exonym in modern mouths
    "the Forgotten" / "the Forsaken". This is a canon-identity ruling, not a
    reskin: "Rakata is the ancient's name for themselves. Modern people on
    this planet just call them the Forgotten or the Forsaken."

11. **EMPIRE_GAP_AUDIT.md** (owner, 2026-08-20): **"OuterRim_GalacticEmpire is
    no longer in the game, we patch Empire."** The vanilla RimWorld Royalty
    `Empire` FactionDef is PATCHED/reskinned into the canon Star Wars
    "Galactic Empire" — defName `Empire` and its six `Empire_*` PawnKind
    defNames are load-bearing and must never be renamed; everything else
    (label, description, art, ideo) is patched to the SW identity. The
    `Neronix17.OuterRim.GalacticEmpire` mod stays active only as a pawn-kind
    supplier (stormtroopers), its own FactionDef is retired.

12. **Mindstone/Kindled canon** (`RUT_mechanoid_origin_canon.md`, owner sitting
    2026-09-11): explicit ruling that **"The Kindled have never been made"**
    — this is a wholly INVENTED (non-SW) race/concept, not a Star Wars proper
    noun, flagged here only so a later merge does not mistake it for one.
    "Rakata" is reaffirmed canon SW/KOTOR; "the Forgotten Sentinels" is ruled
    the official canon name (superseding in-doc-voice "Forgotten Sentries" /
    "Forsaken Sentinels", which survive only as in-world speech variants).

---

## PART 2 — Proper nouns by category

### Creatures / species (Star Wars canon or Legends — identity to be drawn faithfully)

| Name | Source | Note |
|---|---|---|
| Bantha | starwars_iconic_creatures.md; git 25a077005, b3808b986 | FIT-CORE, canon (films). Live in campaign; art redrawn from own reference. |
| Dewback | starwars_iconic_creatures.md; ART_REGEN_WAVE4 | FIT-CORE, canon (films). Identity KEPT in wave 4 art regen. |
| Ronto | starwars_iconic_creatures.md; ART_REGEN_WAVE4 | FIT-CORE, canon — "the Jawas' actual canonical mount." Identity KEPT wave 4. |
| Eopie | starwars_iconic_creatures.md; git 25a077005, 44ae7e3a1, 4f3afc796, d55456885 | FIT-CORE, canon (Phantom Menace). Multiple art passes ("eopie sled"). |
| Jerba | starwars_iconic_creatures.md | FIT-CORE but "canon-thin — Legends/comics only." Retirement note: campaign's `jerbal` analogue (Beasts of the Rim) is being retired; acceptable loss per doc. |
| Krayt dragon / Greater krayt dragon | starwars_iconic_creatures.md; ART_REGEN_WAVE5; git 47c230bb8 | FIT-CORE, canon (The Mandalorian S2) + Legends taxonomy. `GreaterKraytDragon` identity KEPT in wave 5. |
| Sarlacc | starwars_iconic_creatures.md; many git commits (sarlacc_spec.md family); nine_voices_cast_bible.md §4 | FIT-CORE, canon (Return of the Jedi, Book of Boba Fett). Extensive dedicated spec work (sarlacc_spec.md, sarlacc_discussion_pack.md, sarlacc_native_habitat_draft.md). Named as one of the "real gap" recreate worklist. |
| Womp rat | starwars_iconic_creatures.md | FIT-CORE, canon (dialogue-referenced ANH) + Legends design. Size contested canon. |
| Massiff | starwars_iconic_creatures.md | FIT-CORE, Legends/games (KOTOR-era). |
| Anooba | starwars_iconic_creatures.md; ART_REGEN_WAVE4 | FIT-CORE, Legends. Identity KEPT wave 4 art regen. |
| Worrt | starwars_iconic_creatures.md | FIT-CORE, Legends/games, glimpsed in ANH background. |
| Scurrier | starwars_iconic_creatures.md | FIT-CORE, Legends. |
| Steelpecker | starwars_iconic_creatures.md | FIT-CORE, canon (Battlefront II, Jakku). Named a "real gap" recreate-worklist creature. |
| Profogg | starwars_iconic_creatures.md | FIT-CORE, Legends/games. Named a "real gap" recreate-worklist creature. |
| Gorg | starwars_iconic_creatures.md | FIT-CORE, canon+Legends (Tatooine desert form; a separate Naboo/Rori swamp subspecies is NOT desert-relevant). |
| Vulptex ("crystal fox") | starwars_iconic_creatures.md | FIT-CORE, canon (The Last Jedi, Crait). |
| Luggabeast | starwars_iconic_creatures.md | FIT-CORE, canon (Force Awakens era, Jakku). Top-priority "real gap" — "near-perfect Jawa-clan parallel." |
| Kath hound | starwars_iconic_creatures.md | FIT-POSSIBLE, games (KOTOR/SWTOR), Legends-rooted. |
| Orray | starwars_iconic_creatures.md; ART_REGEN_WAVE5 | FIT-POSSIBLE, canon (Attack of the Clones, Geonosis). Identity KEPT wave 5. |
| Roggwart | starwars_iconic_creatures.md | FIT-POOR, canon (Clone Wars, Grievous's pet). |
| Sandwhirl | starwars_iconic_creatures.md | UNCERTAIN — possibly a hazard, not a lifeform, thin Legends sourcing. |
| Tauntaun | starwars_iconic_creatures.md | FIT-POOR (wrong biome, ice), canon (Empire Strikes Back). Live in campaign per cross-ref. |
| Rancor | starwars_iconic_creatures.md | FIT-CORE, canon (ROTJ + Clone Wars/Mandalorian/Book of Boba Fett/Fallen Order). Live in campaign. |
| Rakghoul | starwars_iconic_creatures.md | FIT-CORE, SWTOR canon-adjacent (core plague lore Legends/KOTOR). Named a "real gap" recreate-worklist creature — sourced to tunnels BENEATH Tatooine. |
| Kinrath | starwars_iconic_creatures.md | FIT-CORE, games (KOTOR/KOTOR II), Legends. Live in campaign. |
| Dianoga ("garbage squid") | starwars_iconic_creatures.md | FIT-CORE, canon+Legends (A New Hope trash compactor). Live in campaign. |
| Mynock | starwars_iconic_creatures.md; git 1365f9bfa, 0d199cbd0, 565b9156f, a085bf59c, 75115178c | FIT-POSSIBLE, canon+Legends (Empire Strikes Back). Extensive dedicated build (`RSW_Mynock`, ShipVermin mod). Live in campaign. |
| Rakat / "energy spider" (likely "ginntho") | starwars_iconic_creatures.md | FIT-POSSIBLE, background-only (Revenge of the Sith, Utapau). Canon-thin, contested. |
| Wampa | starwars_iconic_creatures.md; git d55905c91 | FIT-POSSIBLE, canon (Empire Strikes Back). "Wired in" per git commit. |
| Nexu | starwars_iconic_creatures.md | FIT-POSSIBLE, canon (Attack of the Clones, Geonosis arena). Live in campaign. |
| Oggdo Bogdo | starwars_iconic_creatures.md | FIT-POSSIBLE, game canon (Jedi: Fallen Order, Bogano). |
| Rabid Jotaz | starwars_iconic_creatures.md | FIT-POSSIBLE, game canon (Jedi: Fallen Order, Zeffo). |
| Gundark | starwars_iconic_creatures.md; ART_REGEN_WAVE2/3 (`Gundark`, excluded pending biome/design call) | FIT-POOR/UNCERTAIN, dialogue reference (Empire Strikes Back) + Legends/EU art; never shown fully on screen. |
| Akk dog | starwars_iconic_creatures.md | FIT-POSSIBLE, Legends/EU comics; habitat-flexible in its own lore. |
| Firaxan shark | starwars_iconic_creatures.md | FIT-CORE, games (KOTOR) + light canon reference. Named a "real gap" recreate-worklist creature. |
| Sando aqua monster | starwars_iconic_creatures.md | FIT-POSSIBLE, canon+Legends (Phantom Menace, Naboo Abyss). |
| Colo claw fish | starwars_iconic_creatures.md | FIT-POSSIBLE, canon+Legends (Phantom Menace, Naboo Abyss). |
| Opee sea killer | starwars_iconic_creatures.md | FIT-POSSIBLE, canon+Legends (Phantom Menace, Naboo Abyss). |
| Thala-siren ("sea sow") | starwars_iconic_creatures.md | FIT-POSSIBLE, canon (The Last Jedi, Ahch-To). |
| Aiwha ("air whale") | starwars_iconic_creatures.md; ART_REGEN_WAVE2/3 (excluded, biome/design call pending) | FIT-POSSIBLE, canon (Attack of the Clones, Kamino). |
| Yobshrimp | starwars_iconic_creatures.md; ART_REGEN_WAVE5 (`RSW_Yobshrimp` → renamed **FeatherFeel**) | UNCERTAIN sourcing as SW canon; **the campaign's own def was explicitly RENAMED away from this SW-echoing name to an invented one**, owner-mandated. |
| Purrgil | starwars_iconic_creatures.md | FIT-POOR, canon (Rebels, Ahsoka, Mandalorian reference). Deep-space only, no habitat transfer. |
| Howler / summa-verminoth | starwars_iconic_creatures.md | FIT-POOR, canon (Solo). "Howler" as distinct species is UNCERTAIN (likely conflation). |
| Convor | starwars_iconic_creatures.md | FIT-POSSIBLE, canon (Clone Wars/Rebels era). Live in campaign. |
| Porg | starwars_iconic_creatures.md | FIT-POOR, canon (The Last Jedi, Ahch-To). Live in campaign. |
| Reek | starwars_iconic_creatures.md | FIT-POSSIBLE, canon (Attack of the Clones); already on Tatooine. Live in campaign. Also added to `the_slime_gene_lists.md` per git 53864475f. |
| Varactyl ("Boga") | starwars_iconic_creatures.md | FIT-POSSIBLE, canon (Revenge of the Sith, Utapau). Live in campaign. |
| Blurrg | starwars_iconic_creatures.md | FIT-POSSIBLE, canon (Clone Wars/Rebels/Mandalorian). Live in campaign. |
| Nekko | starwars_iconic_creatures.md | FIT-POSSIBLE, game canon (Jedi: Survivor, Koboh). |
| Voritor lizard | starwars_iconic_creatures.md | FIT-POSSIBLE, Legends (Star Wars Galaxies). |
| Fathier | starwars_iconic_creatures.md | FIT-POSSIBLE, canon (The Last Jedi, Canto Bight). |
| Orbak | starwars_iconic_creatures.md | FIT-POSSIBLE, canon (Rise of Skywalker, Kef Bir). |
| Kybuck | starwars_iconic_creatures.md | FIT-POSSIBLE, Legends (Kashyyyk). |
| Shaak | starwars_iconic_creatures.md | FIT-POSSIBLE, Legends/Clone Wars background (Naboo). |
| Tooka cat | starwars_iconic_creatures.md | FIT-POSSIBLE, Legends/canon references; galaxy-wide. |
| Gizka | starwars_iconic_creatures.md | FIT-CORE, game (KOTOR), Legends; has a Tatooine-set arc. Live in campaign. |
| Acklay | starwars_iconic_creatures.md | FIT-POOR (wrong biome), canon (Attack of the Clones, Vendaxa). Live in campaign; "wired in" per git d55905c91. |
| Loth-cat | starwars_iconic_creatures.md | FIT-POOR, canon (Rebels/Ahsoka, Lothal). Live in campaign. |
| Loth-wolf | starwars_iconic_creatures.md | FIT-POOR, canon (Rebels, Lothal). Live in campaign. |
| Kowakian monkey-lizard (Salacious Crumb's species) | starwars_iconic_creatures.md | FIT-POOR, canon (ROTJ) + games. |
| Nuna | starwars_iconic_creatures.md; git d55905c91 ("Nuna forks under new name") | FIT-POOR, canon background (Naboo). Campaign explicitly forked it under a NEW (non-canon) name per that commit — flag for the merge. |
| Roba | starwars_iconic_creatures.md | FIT-POOR, Legends. |
| Veermok | starwars_iconic_creatures.md | FIT-POOR, Legends (Star Wars Galaxies-era). |
| Boma beast | starwars_iconic_creatures.md | FIT-POOR, game (KOTOR II), Legends. |
| Zakkeg | starwars_iconic_creatures.md; ART_REGEN_WAVE1 (canon "redo", identity kept) | FIT-POOR/UNCERTAIN habitat but explicitly labeled SW-canon in the art wave; game (KOTOR II), Legends. |
| Binog | starwars_iconic_creatures.md | FIT-POOR/UNCERTAIN, game canon (Jedi: Fallen Order, background-only). |
| Peko-peko | starwars_iconic_creatures.md | FIT-POOR, Legends (Star Wars Galaxies bestiary). |
| Fambaa | ART_REGEN_WAVE1 (canon "redo", identity kept) | Genuine SW canon — Gungan war-beast (The Phantom Menace). Art regenerated, identity/name kept. |
| Kreetle | ART_REGEN_WAVE1 (canon "redo", identity kept) | Labeled SW canon by the wave item; small Tatooine insect species (Legends/EU). Art regenerated, identity kept — has a maggot life-stage per wave 2 note. |
| Horax | ART_REGEN_WAVE1 (canon "redo", identity kept) | Labeled SW canon by the wave item — NOTE: distinct from `Horrors`/`HoraxCult` (vanilla Anomaly DLC, ruled OUT-of-scope by donor_proper_noun_backlog.md); do not conflate at merge time — verify "Horax" independently before treating as settled canon. |
| Dragonsnake | ART_REGEN_WAVE1 (canon "redo", identity kept) | Labeled SW canon — dragon snake, Clone Wars-era creature (Felucia/related). Art regenerated, identity kept. |
| Insectomorph | ART_REGEN_WAVE2/3 (canon, "no rename per the redo-semantics doctrine") | SW canon creature (Star Wars Animal Collection donor) — "ridable mount associated with the Drug, found near Hutt settlements." Identity kept explicitly. |
| Vornskyr | ART_REGEN_WAVE5 (canon, identity kept) | Genuine SW canon — Kessel/Rebels predator. |
| GreaterKraytDragon | ART_REGEN_WAVE5 (canon, identity kept) | See Krayt dragon entry above; def-level name. |

### Creatures — explicitly REIMAGINED (non-SW donor name → invented name; general kind kept, no SW identity claimed)

| Donor defName | New invented name | Source | Note |
|---|---|---|---|
| `GR_ParagonRat` | **Grithe** | ART_REGEN_WAVE4 | Chitin-plated insectoid-rodent scavenger, "not a literal rat." |
| `BMT_Maligoat` | **Kroffa** | ART_REGEN_WAVE4 | Six-legged plated desert grazer, "not a literal goat." |
| `GR_Molebear` | **Grutt** | ART_REGEN_WAVE4 | Tusked armor-plated burrower, "not a literal mole-bear." |
| `BMT_FleeceSpider` | **Puffmite** | ART_REGEN_WAVE4 | Filament-tufted crystalline/bioluminescent tiny arachnid. |
| `RSW_Yobshrimp` | **FeatherFeel** | ART_REGEN_WAVE5 | Owner-mandated rename in the row's own note; feather-fronded filter-feeder. |
| `Jamel` | **Duskram** | ART_REGEN_WAVE5 | Frilled ceratopsian-headed desert grazer, "not a literal camel" despite the source name's echo. |
| `BMT_FoundryBeetle` | **Slagmaw** | ART_REGEN_WAVE5 | Rust-and-slag-plated grinder, "not a literal beetle." |
| `AA_Terramorph` | (name KEPT, not renamed) | ART_REGEN_WAVE5 | Explicitly exempted from renaming — earned its identity in a prior 2026-09-10 sitting ("dayside lurker"). |

### Creatures/renaming ladder — non-SW donor names given Star-Wars-STYLE (not SW-identity) coined names

Source: `creature_names_ashkarr.md` (DECIDE, 2026-08-22). These are phonetic
inventions, NOT Star Wars canon creatures — flagged here only so a merge step
does not mistake the SW-flavored *style* for SW *identity*. Full ladder (Latin
donor → coined name) is in that doc; examples: Protovermes→ssik (DEAD, mod not
installed), Compsognathus→sskek (DEAD), Coelophysis→sslek, Brachiosaurus→
ssorrbantha, castoroides→grondik, smilodon→dhakar, woolly mammoth→vhorbantha,
sivatherium→obbakar (RESERVE), dinornis→kessik (RESERVE). Kept-as-is per the
bestiary's own rule (English-compound "spacer slang," not renamed): dunbear,
duskhorn, manehound, hellboar, sporemole.

### Species / peoples (Star Wars canon)

| Name | Source | Note |
|---|---|---|
| Rakata | ANCIENTS_AS_RAKATA_SPEC.md; RUT_mechanoid_origin_canon.md; many git commits | KOTOR/Legends precursor species. Endonym; campaign's "Ancients" ARE the Rakata (ruled 2026-08-20, dark-half ruled 2026-08-29). Victims AND tyrants — see Part 1 §10. |
| Hutt(s) | FACTION_SPEC.md; git (dozens of commits, e.g. 25bb3b5b8, 1df7a874f, 2a95239ae) | Genuine SW species/faction. Campaign's `Jawa_HuttCartel` is an AUTHORED faction (not a reskin) built around them. |
| Nikto | FACTION_SPEC.md (`RimMandrakeNikto`), git 95cf85254 | SW alien species, part of the Hutt Cartel roster. |
| Gamorrean | FACTION_SPEC.md (`RimMandrakeGamorrean`, `Jawa_Gamorrean_Guard`) | SW alien species (Jabba's guards), part of Hutt Cartel roster. |
| Rodian | FACTION_SPEC.md (`RimMandrakeRodian`) | SW alien species (Greedo's species), Hutt Cartel roster. |
| Trandoshan | FACTION_SPEC.md (`RimMandrakeTrandoshan`) | SW alien species (Bossk's species), Hutt Cartel roster. |
| Aqualish | FACTION_SPEC.md (`RimMandrakeAqualish`) | SW alien species (cantina scene), Hutt Cartel roster. |
| Twi'lek | FACTION_SPEC.md (`RimMandrakeTwilek`) | SW alien species, Hutt Cartel roster. |
| Pyke | FACTION_SPEC.md (`RimMandrakePyke`) | SW alien species (spice syndicate, Book of Boba Fett/Clone Wars), Hutt Cartel roster. |
| Devaronian | FACTION_SPEC.md (`RimMandrakeDevaronian`) | SW alien species, Hutt Cartel roster. |
| Sith (Pureblood) | FACTION_SPEC.md (`BTD_SithK` → `RimMandrakeSithKissaiPureblood`); git abd9a457b, 3516e06fd | Genuine SW species (Korriban/Sith homeworld natives). Note: `abd9a457b` — "the assailant is a rumour called Sith, and their technology rots" — flags a DISTINCT in-campaign usage of the word "Sith" as an unnamed-assailant rumor register, separate from the playable Sith Pureblood species; verify which sense applies before merging. |
| Weequay | FACTION_SPEC.md (referenced as absent — "Weequay ZERO") | Genuine SW species; noted as MISSING from the Hutt/Nikto/Gamorrean dossier despite being canonically common muscle for Hutt cartels. |
| Wookiee(s) | git 216d0bb6d, 46bba0323, 527d7763f; RM_gelatinous_slime_mod.md | Genuine SW species (Chewbacca's species). Body-size ratio rulings recorded (2.7x/2.15x a Jawa). Also appears in `the_fever_wood.md`'s Wookiees/Ewoks nectar-for-safety canton per git 527d7763f. |
| Ewok(s) | git 527d7763f | Genuine SW species (Endor natives), referenced alongside Wookiees in `the_fever_wood.md`. |
| Tusken Raiders / Sand People | FACTION_SPEC.md; git 5a23f3454, 6c23ecdf9, 689522d51, 5e386c642 | Genuine SW species/culture (Tatooine). Campaign's "Deep Desert Tribes field Tuskens, not vanilla tribals" (git 6c23ecdf9). |
| Jawa(s) | pervasive; the entire campaign's playable clan | Genuine SW species — the whole campaign's premise. Not itemized further here (out of scope as "found," it's the base assumption). |
| Nautolan | RM_gelatinous_slime_mod.md line 72 | Genuine SW species, named among "SW-race gene lists" content the owner ruled OUT of the slime mod ("nothing to do with Star Wars"). |

### Factions

| Name | Source | Note |
|---|---|---|
| Galactic Empire (patched vanilla `Empire`) | EMPIRE_GAP_AUDIT.md; FACTION_SPEC.md; git 78a096733 | See Part 1 §11. Ideo "The Rising Order." Palpatine referenced (git 78a096733: "One Empire: vanilla Empire reskinned as the Galactic Empire, Palpatine"). |
| Rebel Alliance | donor_proper_noun_backlog.md (Outer Rim donor faction, ruled near-lore/OK) | Genuine SW canon faction; appears via the Outer Rim donor mod, not separately authored. |
| Hutt Cartel (`Jawa_HuttCartel`) | FACTION_SPEC.md | AUTHORED (not reskinned) around genuine SW Hutt lore. Ideo "the Reckoning of Debts." |
| Trade Federation | donor_proper_noun_backlog.md (Category 4 note: "a Trade Federation/Guild-flavored analog already exists in RSW canon") | Referenced as an existing in-canon analog for the MiningCo. donor-leak retheme; genuine SW faction. |
| Separatist(s) / Separatist remnants | design/RimMandrake/Custom_World.md; JDS Separatists (droid_taxonomy.md) | Genuine SW canon faction (Clone Wars-era); "JDS Separatists" droid family is a live mechanism in the droid economy. |
| Bounty Hunters | design/RimMandrake/Custom_World.md | Genuine SW archetype/faction, named as an "Act-II pursuer" design element. |
| Geonosian(s) / Geonosian Foundry Hive | starwars_iconic_creatures.md (Orray/Geonosis); FACTION_SPEC.md/EMPIRE_GAP_AUDIT.md (`Jawa_GeonosianFoundryHive`) | Genuine SW species/world. Campaign's Geonosian Foundry Hive faction — owner-ruled the Empire "sterilised their species... every one of them here is a refugee." |
| Ancients (vanilla RimWorld def, NOT touched as a faction) | ANCIENTS_AS_RAKATA_SPEC.md | Explicitly ruled NOT a faction reskin — sleepers are appearance-only (Rakatan xenotype on pawn kinds); the vanilla `Ancients` FactionDef itself is untouched. |

### Characters (named individuals)

| Name | Source | Note |
|---|---|---|
| Palpatine | git 78a096733 | Referenced in the Galactic Empire reskin commit message. |
| Boba Fett | starwars_iconic_creatures.md (krayt dragon entry: "its teeth arm Boba Fett's helmet") | Reference only, not an authored character. |
| Salacious Crumb | starwars_iconic_creatures.md (Kowakian monkey-lizard entry) | Reference only (names the species' famous example). |
| Teedo | starwars_iconic_creatures.md (Luggabeast entry) | Reference only (a luggabeast handler). |
| Grievous | droid_taxonomy.md context / starwars_iconic_creatures.md (Roggwart, "Grievous's pet") | Reference only. |
| Obi-Wan (Kenobi) | starwars_iconic_creatures.md (Varactyl entry, "Obi-Wan's steed") | Reference only. |

### Planets / places (Star Wars canon)

| Name | Source | Note |
|---|---|---|
| Tatooine | starwars_iconic_creatures.md (pervasive); music_protocol.md ("Tatooine-flavoured scavenger campaign") | The primary real-world referent for Ash'karr's desert design register — not itself a place IN the campaign (Ash'karr is an original planet), but the constant comparison target. |
| Jakku | starwars_iconic_creatures.md (Steelpecker, Luggabeast entries) | Canon planet, reference only. |
| Geonosis | starwars_iconic_creatures.md (Orray entry) | Canon planet, reference only. |
| Naboo (incl. Naboo Abyss) | starwars_iconic_creatures.md (Sando aqua monster, Colo claw fish, Opee sea killer, Gorg swamp form, Shaak, Nuna, Veermok entries) | Canon planet/region, reference only. |
| Dathomir | starwars_iconic_creatures.md (Rancor, Voritor lizard entries) | Canon planet, reference only. |
| Manaan | starwars_iconic_creatures.md (Firaxan shark entry) | Canon planet (KOTOR), reference only. |
| Ahch-To | starwars_iconic_creatures.md (Thala-siren, Porg entries) | Canon planet, reference only. |
| Kamino | starwars_iconic_creatures.md (Aiwha entry) | Canon planet, reference only. |
| Crait | starwars_iconic_creatures.md (Vulptex entry) | Canon planet, reference only. |
| Hoth | starwars_iconic_creatures.md (Tauntaun, Wampa entries) | Canon planet, reference only. |
| Dxun | starwars_iconic_creatures.md (Boma beast, Zakkeg entries) | Canon planet, reference only. |
| Utapau | starwars_iconic_creatures.md (Rakat/energy spider, Varactyl entries); ANCIENTS_AS_RAKATA_SPEC.md (Grievous ref adjacent) | Canon planet, reference only. |
| Lothal | starwars_iconic_creatures.md (Loth-cat, Loth-wolf entries) | Canon planet, reference only. |
| Kessel | starwars_iconic_creatures.md (Howler/summa-verminoth, Vornskyr entries) | Canon planet/region, reference only. |
| Kashyyyk | starwars_iconic_creatures.md (Kybuck, Kinrath entries) | Canon planet, reference only. |
| Cholganna | starwars_iconic_creatures.md (Nexu entry) | Canon planet, reference only. |
| Korriban | (implied by Sith Pureblood species entry) | Canon Sith homeworld, not directly named in text read but the species' origin. |

### Ships (Star Wars canon terminology — generic, not a named individual vessel)

No specific canon SW ship NAMES (e.g. Millennium Falcon, Star Destroyer class
names) were found authored into the campaign's own docs in the material read.
The campaign's own vessel is an ORIGINAL ship named **the *Utinni*** (the
gravship — not a Star Wars proper noun; campaign-original) referenced
throughout `the_forgotten_war.md`, `ship_designs.md`, `ship_deck_plan.md`, and
`ANCIENTS_AS_RAKATA_SPEC.md` ("the player flies a ship built by the people
they are cracking out of cold storage").

### Items / technology / materials (Star Wars canon terms)

| Name | Source | Note |
|---|---|---|
| Lightsaber | ship_legacy_armoury.md; balance_paradigm.md; git b5a524f1a, b616bbbe7, d55905c91 | Genuine SW canon weapon/technology. `lee.theforce.lightsaber` mod referenced as active-in-config-but-not-installed; git d55905c91: "lightsaber stays upstream." Explicit ruling: do NOT casually conflate the campaign's own "laser sword" item with a lightsaber — decision deferred pending the Force-users spec. |
| Kyber (crystal) | RUT_mechanoid_origin_canon.md; git 05f67a48a, ab3c2f313 | Genuine SW canon material — kyber-crystal engineered mind is the ruled nature of the Rust Cathedral/mechanoids. |
| Beskar | (not found explicitly in material read this pass) | Genuine SW canon material (Mandalorian armor) — flagged as a term to check for in a future pass; not confirmed present in the docs read. |
| Blaster(s) | pervasive (droid_taxonomy.md, ship_legacy_armoury.md, FACTION_SPEC.md) | Genuine SW canon weapon category; "Outer Rim blasters" referenced as an existing donor-mod weapon line alongside the laser-weapon armoury. |
| Restraining bolt | restraining_bolt_doctrine.md, restraining_bolt_technical.md | Genuine SW canon droid-control device; the subject of two dedicated design docs. |
| Astromech (droid) | creature_recognizability_rule.md ("an astromech that reads as an astromech") | Genuine SW canon droid class, cited as an icon-carve-out example. |
| Protocol droid | (implied class, not directly quoted in material read) | Genuine SW canon droid class — flagged for a future pass; not directly confirmed quoted. |
| Podracer / podrace | starwars_iconic_creatures.md (Eopie entry, "pod-race pit crews"); map_content_injection_research.md ("podracer wreck") | Genuine SW canon technology/sport; a "podracer wreck" is an authored Lua map-dressing template. |

---

## Sources actually read (with content) this pass

- `design/Jawa/donor_proper_noun_backlog.md` — full.
- `design/Jawa/worldbuilding/starwars_iconic_creatures.md` — full.
- `design/Jawa/worldbuilding/creature_names_ashkarr.md` — full.
- `design/Jawa/worldbuilding/creature_normalization_doctrine.md` — full.
- `design/Jawa/worldbuilding/creature_recognizability_rule.md` — full.
- `design/Jawa/worldbuilding/the_one_map.md` — full (no new SW proper nouns beyond map-doctrine terms already covered; confirms "no worldgen" doctrine, irrelevant to this list).
- `design/Jawa/worldbuilding/ANCIENTS_AS_RAKATA_SPEC.md` — first ~150 lines (Rakata ruling core).
- `design/Jawa/worldbuilding/mindstone_arc_legends.md` — full.
- `design/Jawa/worldbuilding/EMPIRE_GAP_AUDIT.md` — first ~150 lines (Empire ruling core).
- `design/Jawa/worldbuilding/droid_taxonomy.md` — full.
- `design/Jawa/worldbuilding/ship_legacy_armoury.md` — full.
- `design/Jawa/worldbuilding/creatures/RUT_mechanoid_origin_canon.md` — full.
- `design/Jawa/worldbuilding/biomes/kits/greentide_kit_spec.md`, `scarlands_kit_spec.md`, `webwork_kit_spec.md` — grepped for SW terms only (no kit_spec files exist directly under `design/RimMandrake/`; these three live under `design/Jawa/worldbuilding/biomes/kits/` — nothing beyond generic "droid"/"Jawa" mentions found; no new proper nouns).
- `design/RimMandrake/nine_voices_cast_bible.md` — full (originally-invented "Nine Voices" pantheon; no SW proper nouns of note beyond a cross-reference to `sarlacc_spec.md`).
- `design/RimMandrake/*.md` — grepped for SW canon terms (Custom_World.md, RM_gelatinous_slime_mod.md, balance_paradigm.md, droid_oracle_voice_design.md, llm_ingame_wiring_spec.md, map_content_injection_research.md, music_protocol.md, nine_voices_cast_bible.md hit).
- `design/Jawa/worldbuilding/FACTION_SPEC.md` — grepped for faction/species names (not read in full; 54 KB).
- `infrastructure/state/items/ART_REGEN_WAVE1_WIRE_IN_1.md` through `ART_REGEN_WAVE5_QUEUE_1.md` (7 files) — full.
- `infrastructure/artpipe/README.md` — referenced via the wave items' own quotes of its "improve" semantics section (not independently re-read; the wave items quote it directly).
- `git log --oneline --all`, grepped for SW proper-noun keywords — ~100 matching commit subject lines reviewed.

## Not read in full (too large / out of the day's budget; flagged as gaps)

`design/Jawa/worldbuilding/faction_roster_v2.md` (189 KB), `jawa_society.md`
(62 KB), `desert_world_design.md` (155 KB), `ASHKARR_WORLD_DEFINITION.md`
(111 KB), `Alien_Bestiary.md` (30 KB), `ANCIENTS_AS_RAKATA_SPEC.md` (remaining
~39 KB beyond the first 150 lines), `EMPIRE_GAP_AUDIT.md` (remaining ~19 KB
beyond the first 150 lines), and the majority of the ~150-file
`design/Jawa/worldbuilding/` tree beyond what is listed above. A follow-up
pass grepping these for the same SW-keyword list (as was done for
`FACTION_SPEC.md` and the RimMandrake dir) would likely surface additional
named individuals, planets, and item names, particularly from
`faction_roster_v2.md` and `jawa_society.md`.
