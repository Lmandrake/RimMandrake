# The Ikee becomes the Jawa's pet — BUILD, 2026-08-23

Owner's brief: *"the Ikee are the creepy Eyeling that we want to make into a Jawa pet.
Modify the Ikee to be only a third of its current size. Give it the ability to nuzzle four
times a day, yet have it be very messy all over (disgusting). Have it be very easy to train.
The player faction will start with one."*

`src/Jawa/Jawa_Patches/Patches/Ikee_Tuning.xml` (new) + a `ScenPart_StartingAnimal` in
`Scenario_Utinni.xml`. validate_patch.py 0 errors. Deployed, VERIFIED in sync.

## the four asks, and what each actually required

| ask | field(s) | before → after |
|---|---|---|
| **a third the size** | `race.baseBodySize` | 0.4 → **0.13** |
| | `PawnKindDef.lifeStages[*].bodyGraphicData.drawSize` | 1 / 1.25 / 1.5 → **0.33 / 0.42 / 0.5** |
| | `statBases.Mass` | 60 → **20** |
| | `race.baseHealthScale` | 0.5 → **0.35** — see note |
| **nuzzle 4×/day** | `race.nuzzleMtbHours` | **−1 → 6** |
| **very easy to train** | `race.wildness` | 0.2 → **0.02** |
| | `race.trainability` | Intermediate → **Advanced** |
| **very messy** | `comps` → `CompProperties_Spawner` | **added**, spawns `Filth_Slime` |
| **a pet at all** | `race.petness` | **0 → 0.9** |
| | `race.manhunterOnDamageChance` | 0.5 → **0.02** |

## five things that were NOT obvious and are worth keeping

**1. `nuzzleMtbHours −1` is the vanilla NEVER sentinel, not a small number.** The Ikee could
not nuzzle at all. It is a mean-time-between-events in HOURS, so four a day is 6.

**2. `petness 0` would have made every other change cosmetic.** At zero the animal can never
bond, so it could be tamed and trained and would still never be a *pet*. Raised to 0.9, above
vanilla's husky at 0.75.

**3. "Very easy to train" is two fields doing different jobs.** `wildness` governs taming and
staying tame; `trainability` is the CEILING on what it can ever learn. Low wildness alone
would have given a pet that tames instantly and can never learn Rescue or Haul.

**4. 🔴 There is NO filth field on RaceProperties.** Checked across all 2,524 animal defs in
the live set — no `filthProducedPerDay` or equivalent. RimWorld's own animal filth is driven
by body size inside `Pawn_FilthTracker` and is not exposed to XML, so **making the Ikee
smaller would have made it CLEANER** — the opposite of the brief. The filth is therefore
added deliberately with `CompProperties_Spawner`, which is vanilla and proven on pawns:
`Dryad_Woodmaker`, `Dryad_Berrymaker` and `Dryad_Medicinemaker` all carry one.
`Filth_Slime` over `Filth_AnimalFilth` because it takes **70 work to clean**, lasts **35-40
days**, and **attaches to pawns walking through it** — disgusting rather than merely dirty.

**5. Health was NOT divided by three.** 0.5 → 0.35, not 0.17. A third of the health makes a
pet that dies to a stray spark; the owner asked for a posterchild, not a tragedy.

## ⚠️ two traps found while patching

**Two mods define `AA_Eyeling`** — Alpha Animals AND Alpha Memes. Every operation reports 2
matches and patches both, which is correct: RimWorld merges them into one document.

**Three fields are not authored in `Races_Eyeling.xml`** — `Mass`, `nuzzleMtbHours` and
`wildness` come from `AnimalThingBase` or another mod's patch, so a bare `PatchOperationReplace`
matched **0 nodes on disk** and would have been a silent no-op depending on load order. All
three are now `PatchOperationConditional` replace-or-add.

## the player starts with one
`ScenPart_StartingAnimal`, `animalKind AA_Eyeling`, `count 1`,
`bondToRandomPlayerPawnChance 1.0`. Read out of RimWorld's own source: that field does two
things, both wanted — it creates the **Bond** relation with a starting Jawa AND **completes
Obedience training**, so the Ikee arrives devoted rather than as livestock. The bond branch
requires `CanAssignToTrain(Obedience)` to be Accepted, which the Advanced trainability above
guarantees.

## ⛔ NOT proven, and no log line will prove it
Every one of these is a runtime behaviour: the nuzzle rate, the slime rate, the bond on load,
and above all whether a 0.33 drawSize sprite still READS as a creepy eye rather than a smudge.
That last one is the real risk in this change and it is settled on screen, not in a def.
