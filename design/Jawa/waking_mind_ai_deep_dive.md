<!-- status: ANALYSIS for owner review (BENCH/Fable fork, 2026-09-04), ordered
     by the owner during the canon-reintegration G6 ruling: "What IS all of
     this? Persona cores used to only be to launch Tanaka drives — what are
     they now? ... Do a thorough analysis of all the 'AI' tech options here to
     make sure we're inclusive and leave no stragglers lying about."
     Feeds canon_reintegration_plan.md §G6 (deferred pending this doc). -->

# The Waking Mind — what "AI" is on this planet, and where it should live

## 1. The census — every mind-shaped thing in the live game

Sources: frozen deck (`research_deck_FROZEN_20260904.json`), manifest
(522 rows), live dump capture `2026-09-04T02-23-44Z` (589 mods), mod XML.
All MEASURED unless marked.

### 1.1 The Waking Mind's actual 10 rows (frozen deck)

| tier | row | what it mechanically does |
|---|---|---|
| T1 | gravitational-wave communication (RimAI) | unlocks the GW antenna — comms infrastructure |
| T1 | crypto-harmonization (AM) | warcasket/anti-mech comms kit (apparel) |
| T2 | Subspace gravitic penetration (RimAI) | flavor/gate node, no unlocks (functionless list) |
| T2 | RimAI Level 1 | Lv1 AI servers + terminals |
| T2 | mechanoid beamcasting (AM) | MechDisruptor weapon + command gear (kept on owner's word, rename owed) |
| T2 | quantum pulse messaging (AM) | more comms/warcasket kit |
| T3 | RimAI Level 2 | Lv2 servers + AI terminal |
| T3 | voidlink connectivity (AM) | beamcaster pack, efficiency boosters |
| T4 | RimAI Level 3 | Lv3 servers |
| T4 | Positronic Brain (KotOR) | implant dock replacing 30% of a pawn's brain |

**Honest read**: this is a comms-hardware pile + the RimAI server ladder +
one brain implant. The tab's grand name is writing a check its rows don't
cash — which is exactly the owner's instinct.

### 1.2 AI-shaped things living in OTHER trees (correctly or not)

| thing | where it lives | note |
|---|---|---|
| **machine persuasion** (`ShipComputerCore`, Core) — *"persuade an existing persona core into serving as a ship's machine captain"*; unlocks ship computer + pilot/gunner subpersona cores | THE SHIP (frozen) | the single most persona-relevant research in the game |
| `AIPersonaCore` (item, Core) · `TechprofSubpersonaCore` · pilot/gunner/operator subpersona cores (Odyssey/VGE/VFEPD) · **`EmptyAICore` / `UnfinishedAICore` (GravTech — CRAFTABLE persona cores)** · `VFEPD_ShipPart_ShipComputer_AI` | items, mostly gated via SHIP-tree rows | 37 persona/AI items MEASURED in the dump |
| persona WEAPONS (bladelink mono/zeus/plasma, GravHammer, 4 Big&Small) | items; their Royalty research (`BrainWiring`, `NeuralComputation`) is CUT | weapons remain acquirable as loot — a mind bound to a blade, researchless |
| droid construction (~24 rows: OuterRim + guy762 + Synstructs) | The Unbolting (faction-held, Enclaves) | ruled home; the liberation curriculum |
| droid repair (Energy Systems, Replacement/adv parts, armor, shields) | Scavenger (owner's own move — Droidsmith dissolved) | ruled home; do not touch |
| droid weapon systems (2 rows) | Blasterworks | fine — guns are guns whoever aims them |
| `OuterRim_DroidBrain` (item) | crafting chain under Unbolting rows | droid minds as manufacturable parts |
| neural supercharger | The Ascendant Ladder | flesh-adjacent; fine |
| CCTV/automated cameras (CAI 5000, 3 rows) | Powder & Slug | weak-AI surveillance; fine as security |
| automated smelter restoration (WreckedMachines) | The Workshop | automation, not mind; fine |
| **Droidworks** (inactive, port-wave) | — | **carries ZERO ResearchProjectDefs (MEASURED: no research XML in the mod)** — it is a race/pawnkind overhaul making droids PEOPLE. The port adds pawns and fiction, not rows; any "Droidworks research" must be AUTHORED, it does not arrive |
| CUT and staying cut | — | Royalty neural pair (persona-weapon links), Anomaly brainwipe/mind-numb serum, Big&Small android conversion, the 3 named-droid equipment rows, all mechtech |

**Stragglers found: two.** ① The persona-core story is split — items and
"machine persuasion" in THE SHIP, craftable empty cores in GravTech rows,
persona weapons researchless — with no tab claiming the DOMAIN. ② The AM
comms kit (4 rows) is communications infrastructure wearing an AI tab.

## 2. What a mind IS on this planet — the ontology

The campaign already committed to the strangest fact first: **the player
lives inside a persona core.** The Utinni is a Rakatan core, patterned with
a Jawa mind so it would obey, and the gods came with the pattern as running
personas; above the nine, only the non-egoic Narrator — the old ship-mind's
remnant — and no landlord (06_the_ship, owner 2026-08-15/30). Around that
fact, five kinds of mind exist here:

1. **Born minds** — crew, colonists, the living factions. People.
2. **Made-and-freed minds** — droids. Made as tools, become a PEOPLE
   (Droidworks' whole point; the Enclaves' Continuity Protocol; the
   Unbolting as trust-curriculum). The campaign's moral answer is already
   ruled: building them is a liberation rite, not an industry.
3. **Bound minds** — subpersona cores, droid brains as parts, RimAI
   servers, persona weapons: constructed intelligences under command,
   *tools that might be slaves*. This is the live wire of the Ohm/Oomo war
   (principles §2.3: Ohm demands, Oomo protests, the player walks in
   knowingly).
4. **Haunted substrate** — the Utinni herself: tenancy, not identity. Nine
   tenants, a grieving Cradle-Mind, no self.
5. **The dead who whisper** — Rakatan machinery voices (the Cathedral's
   congregation learns from them; reintegration plan C2 made them
   machine-canon Antiquities). Minds gone, patterns leaking.

And one **anti-mind** for contrast: the Assailant — total comprehension of
data, total blindness to art. What a made mind becomes with completeness
and no culture. The Doctrine of the Unwritten is the ancients' verdict on
unbounded machine reading; every AI the player builds sits in that shadow.

**Persona cores, answered.** In this canon a persona core is not a mind —
it is a **house for minds**: Rakatan tenancy architecture. That is why one
core can hold nine gods and a remnant; why vanilla's research is called
machine *persuasion* (you negotiate with a tenant, you do not program a
tool); why an empty craftable core (GravTech) is the most theologically
loaded object in the game — an empty house, and this planet's houses do
not stay empty. Subpersona cores are deliberately *small* houses — a
single-room tenant who can only be a pilot, a gunner: bounded tenancy as
safety doctrine. "Launching the ship" was never what they were; on this
planet they are real estate for souls.

**What researching AI means morally**: every rung asks *tool, tenant, or
person?* Repair and restoration of existing minds is Rekko-neutral (the
restore≠transcend rule). Making NEW bound minds feeds Ohm and bills Ozzik.
Freeing minds is the Enclaves' sacrament. Housing them is the ship's own
mystery.

## 3. Options

**(a) Keep The Waking Mind, expanded to "the study of bound minds."**
Claim the domain census §1.2 found homeless: comms kit re-described as the
*nervous system* rows, RimAI as bound-mind servers, Positronic as merger,
plus NEW authored rows over time (persona-weapon attunement, subpersona
doctrine, droid-brain refurbishment). Fiction: the tab where the clan
decides what a tool is. *Trade-offs*: keeps the Ohm/Oomo stage and an
address for future authored content; but stays thin until authoring happens
(Droidworks brings nothing), and the persona-core rows it most wants
(machine persuasion) are frozen in THE SHIP — the tab claims a domain whose
crown jewel lives elsewhere.

**(b) Merge into The Unbolting → one tree: "minds you make."** (The
owner's leaning.) The 10 rows relabel into The Unbolting; tiers keep their
frozen positions. The merged tree's ladder: *understand minds* (comms,
servers — common access) → *repair and refit them* (interfaces Scavenger's
repair floor) → *merge with them* (positronic) → *make BODIES for them*
(droid construction — faction-held, Enclave trust). Fiction in one line:
**you may study minds freely; you may make people only when the freed ones
trust you.** The access-class mix inside one tab is the FEATURE — the
common on-ramp is the Enclaves' open evangelism, the boon-gated summit
their sacrament — and it puts the whole droid argument in one visible
branch, which is literally what principles §2.3 ordered. *Trade-offs*: tab
bar tightens to 16; cost is one tab relabel + manifest strings (placements
untouched). Risks: the Enclaves' tree absorbs rows they have no fictional
claim on (RimAI servers are not droid liberation — needs one line of
fiction: the Enclaves teach ALL made minds, servers included, as
"pre-persons"); and if the AI domain later grows rich (stations, orbital
minds), it re-crowds a faction tree.

**(c) Split by scale**: personal/droid minds → The Unbolting; ship/station
minds (RimAI servers, machine persuasion's neighborhood) → The Utinni's
tree. *Trade-offs*: scale is a clean engineer's cut but a bad moral one —
it separates rows by SIZE when the campaign's question is STATUS
(tool/tenant/person); and it pours common-access research into the
Utinni's ship-only, memory-gated tab, muddying the one tab whose gate story
is pure.

**(d) The census's own suggestion — merge (b), plus a persona-core
DOCTRINE line in The Utinni.** Adopt (b) wholesale, and additionally give
THE SHIP/Utinni tab a named 3-row "Tenancy" thread (machine persuasion +
its two subpersona neighbors, already frozen there) re-described in the
house-for-minds canon, cross-linked by hidden reveal: completing Unbolting
tiers re-describes the Tenancy rows and vice versa. No row moves anywhere;
two tabs tell one argument from both ends — the made mind looking up, the
haunted house looking down. *Trade-offs*: everything from (b) plus a
description-only pass on 3 SHIP rows; the only cost over (b) is authoring.

## 4. Recommendation

**(d)** — which is the owner's (b) with the persona-core answer actually
landed. The Waking Mind dissolves into The Unbolting ("minds you make"; 16
tabs); the Utinni keeps tenancy as her own mystery; the comms-kit rows get
honest re-descriptions (nervous system, not intelligence); and the
persona-core ontology (§2) enters canon so every future AI row has a place
to stand. If the owner would rather preserve a 17-tab bar for symmetry
with Antiquities' arrival, (a) is the fallback — but it should then adopt
§2 wholesale and accept authoring debt as the price of the address.
