## spec
🔴 **DECIDE authored the renormalization; the deploy is BUILD's** — owner's ruling 2026-08-23.

**Redeploy `design/Jawa/fauna/BiomeCast_Ashkarr.xml`** (regenerated at `1e7cf0ec`, 26 biomes,
746 records). ⚠️ It lives under `design/` and BUILD owns whether and how it ships — that has not
changed.

**Why it changed.** The owner reviewed all 621 cast creatures himself and ruled `replace` on ten.
🔑 **That was a CASTING verdict, not an art one** — his notes say *"terrestrial, not wanted"*
(gorilla, capybara, enhydriodon) and *"I can't even see what this thing is"* (revenant). Ten
creatures held twelve cast rows; all twelve are refilled, band- and biome-matched.

| biome | band | now |
|---|---|---|
| `Wasteland` | small | skiphound |
| `AridShrubland` | med | painted spat |
| `BMT_FungalForest` | huge | Ceratosaurus |
| `ZBiome_DesertOasis` | small | fission mouse |
| `AB_GelatinousSuperorganism` | med | decay drake |
| `Scarlands` | SUPER | mycoid colossus |
| `AB_MiasmicMangrove` | small · med · large | swarmling · Protosolpuga · Gorgonops |
| `AB_PyroclasticConflagration` | small | smog caterpillar |
| `Volcano` | large | ironhusk beetle |
| `LavaField` | med | raptor shrimp |

## Watch out
⚠️ **The picks were assigned GREEDILY, and that is not a detail.** The reuse penalty has to update
as each hole is filled — the first pass held `used` fixed and put `skiphound` in three biomes,
which would have rebuilt the ubiquity the whole cast exists to prevent (581 of 652 creatures
appear in exactly one biome).
🔴 **Two picks were overruled by judgement against the score, both the same error the score cannot
see.** `belong` ranks climate fit and does not know that **a battle droid is not wildlife** — it
offered Droidekas for a mangrove — or that a **rabbitcat is not a volcano animal**. Machines are
now excluded outside mechanoid biomes. ⛔ **Do not "restore" a higher-scoring pick over these.**
⚠️ Two cast entries are skipped by the generator as not-PawnKindDefs — `SWPotF_RaceDef_ysalamir`
and `GiantAnt_Race`. **Both pre-date this change**; neither is a substitute.

## verify
`BiomeDef` count still 80; zero cross-reference errors naming any substitute; then a map in
`AB_MiasmicMangrove` (three slots changed there) and `Volcano`, and look at what is walking around.

## criteria
- [ ] Deployed, and the ten rejected creatures spawn nowhere.
- [ ] The twelve substitutes spawn in their biomes.
- [ ] No red errors.
