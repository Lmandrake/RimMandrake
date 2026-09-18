# Polluted Lands / mutapox eval — 2026-09-18

Donor: /mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3390196656/
(biomesteam.biomespollutedlands). Source/ shipped (C# available, read directly).

## Part A — mechanism (CONFIRMED from source)

Trigger: IncidentDef `BMT_Disease_Mutapox` (ParentName DiseaseIncident), workerClass
`IncidentWorker_Mutapox`, targets Map_PlayerHome/TempIncident/Misc/RaidBeacon. Its
GeneExtension.pollutionAmountCurve maps MAP POLLUTION % (Biotech engine mechanic) to
disease chance: 0% pollution -> 0 chance, 25%->0.02, 50%->0.1, 80%->0.6, 100%->0.8,
reduced by tox resistance stats. So the trigger is Biotech pollution on the map, not
biome type per se.

Disease: HediffDef `BMT_Mutapox` (ParentName InfectionBase, hediffClass
`Hediff_Mutapox`) - ordinary tendable/immunizable disease shape (12h tend, immunity
race) but lethalSeverity 1 (can kill if untreated).

Gene acquisition (read from Source/Hediffs/Hediff_Mutapox.cs, exact code):
while Severity >= 0.4, each tick rolls Rand.MTBEventOccurs(0.6/scaledSeverity, ...);
on a hit, picks a random gene from GeneCategoryDef `BMT_MutaGenes` the pawn doesn't
already have and calls `pawn.genes.AddGene(def, false)` - false = added as an
ENDOGENE, permanent, not a removable xenogene - then sends a letter. Sicker pawns
mutate faster; a pawn can stack multiple of the 18 genes if it keeps surviving.
Mechanism is disease-driven progressive random mutation, not on-death/on-infection-once.

## Part A — 18 genes, by effect class (defNames confirmed; per-gene stat/value XML
not exhaustively read, class + hediff names are)
- Offense/toxin: BMT_AcidicGlands, BMT_ToxspewingPores, BMT_BloodExplusion,
  BMT_ImpalingClaws, BMT_PestilentSymbiosis (ability "toxflies")
- Metabolic/organ: BMT_CarrionMetabolism (corpse-eating ability), BMT_OverdevelopedOrgans
  ("absorb HP" hediff), BMT_ConjoinedHeart, BMT_MutagenicFertility
- Defensive/regen: BMT_EpidermalOssification, BMT_MoltingRegeneration (skin-shed filth),
  BMT_ProtectiveLeprosy
- Debuff: BMT_ChronicPains (5-stage escalating pain hediff), BMT_HandsMutated
- Sensory/rare: BMT_ClusterEyes, BMT_PsychicCortex (psychic shield ability),
  BMT_GoliathArms, BMT_EvermutatingCells (drives ongoing mutation)
All body-horror/mutant flavor (Fallout-ghoul-adjacent), not combat power picks first.

## Part A — what else we use
Census (BIOMES_CAVERNS_DEEPSCAN_1 / Transient/biomes_caverns_deepscan_2026-09-18.md,
MEASURED 2026-09-18): 39 PawnKindDef, ~40-45 plant ThingDef injected via 74
PatchOperations into 23+ biomes (vanilla Desert/ExtremeDesert/etc. + own Caverns
biomes + third-party). ZERO BiomeDefs of its own.

grep -rln "BMT_" src/RimUtinni/UtinniPatches/Patches/: AnimalTolerances_Ashkarr.xml,
CreatureResize_Ashkarr.xml, BiomeFloraStatAdjustments_Generated.xml,
BiomeCast_Ashkarr.xml, BiomeFlora_Ashkarr.xml, HumanTemperatureBand_Ashkarr.xml,
JawaWorld_BiomeMix.xml, PlantTolerances_Ashkarr.xml, SandFishing_CrackedLands.xml,
FactionSlate/OnlyOurFactions.xml - these carry the creature/plant injection rows
(39 distinct plants, per scoping doc), NOT the gene system.

Gene-specific (18 defNames + Mutapox) grep across src/design/infrastructure: the ONLY
hits are comments in our OWN biome defs (RUT_Wasteland.xml, RUT_TheForge.xml,
RUT_RustCathedral.xml) recording that BMT_Disease_Mutapox was explicitly DROPPED from
each biome's diseases list when authored (BIOME_OWNERSHIP_WAVE_1, 2026-09-09). No live
def anywhere references any of the 18 genes. The mutation system is currently
completely unused/inert in our own content.

## Part B — prior rulings

1. FOUND, executed decision (not just a ledger note): RUT_Wasteland.xml,
   RUT_TheForge.xml, RUT_RustCathedral.xml (authored 2026-09-09,
   BIOME_OWNERSHIP_WAVE_1) all explicitly drop BMT_Disease_Mutapox from their
   diseases list. RUT_Wasteland.xml comment verbatim: "diseases trimmed to the
   plain vanilla suite (dropped the donor's AnimalFlu/AnimalPlague/OrganDecay/
   BMT_Disease_Mutapox): ban 4 requires every resident to be 'visibly shaped by
   the contamination,' and the sheet's own disease register is radiation/toxin,
   not wildlife epidemiology - left at the donor's core set rather than inventing
   a radiological disease that does not exist as a def yet (SS Owed 'needs a
   dose/geiger layer')."

2. FOUND, ledger event CAVERNS_PARITY_BUILD_1, ts 2026-09-18T19:10:54Z (BENCH
   "file" event, spec field): "Owner ruled all six scoping questions 2026-09-18...
   (6) Polluted Lands mutations: DROP when that mod cuts (recorded for the cut
   path, not this build)."

3. FOUND, same-day ledger event CAVERNS_PARITY_BUILD_1 note ts
   2026-09-18T20:26:43Z (BENCH note, an hour+ later): "Polluted Lands Q2: owner
   asked for merits + prior-ruling search before ruling - research agent
   running." -- i.e. this exact task. So the (6)-DROP line above is recorded as
   owner-ruled, but the same day, later, BENCH's own note treats Q2 as still
   OPEN pending merits+prior-ruling research. Two same-day ledger entries
   disagree on whether Q2 is closed.

4. Scoping doc's own §5 Q2 (design/Jawa/worldbuilding/biomes/
   caverns_replacement_scoping.md) still lists it as an open decision, written
   same day.

5. canon.yml: not found under design/Jawa/worldbuilding (searched, absent);
   no pollution/mutation entry to check.

6. wasteland.md §"Owed": "Biotech's pollution system (wastepacks, polluted
   terrain, tox resistance) is the obvious spine and is nearly this biome
   verbatim; needs a dose/geiger layer" - UNBUILT, explicitly OWED, not yet
   using Polluted Lands' gene system. poison_forest.md: zero pollution/mutation
   hits - that biome's sheet carries no pollution flavor at all today.

## Part C — merits
FOR: wasteland.md's "wretched and mutated as the rule" wildlife doctrine and its
explicit "Owed" engine-feasibility note both point at exactly this shape (Biotech
pollution -> disease -> visible mutation); the mechanism already exists, built,
tested, tunable via pollutionAmountCurve - zero engine work vs. the dose/geiger
layer that's currently unbuilt.

AGAINST: already executed as DROP in all three biome defs that could have carried
it (Wasteland, Forge, RustCathedral) with a reasoned rationale (bespoke
radiological disease wanted, not wildlife epidemiology); zero live refs anywhere
else; 18 permanent endogenes of grungy body-horror flavor is a much bigger
tonal/mechanical commitment than the sheet's restrained "visibly shaped by
contamination" ask, and nothing currently gates it to only the Wasteland/
war-ground tiles the doctrine wants (it fires on any sufficiently polluted
player map).
