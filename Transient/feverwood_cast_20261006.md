# FEVERWOOD_RM_CAST_COMPLETION_1: offline pass 2026-10-06 (FOUNDRY helper, uncommitted)

## Existence census (by name AND description)
I searched for all seven by name (`RM_*` and bare) across `src/`, and read the descriptions of every Fever Wood race (thornbug, vaulm, ollareth, drommath, chellow, murrelith, thavrik, skellick, kurreth, kurreth queen, sekkulaath juvenile, glomvar). None of the seven existed under any name. `RM_SapSuckerGuild.xml` mentions `RM_Silloch` only as "not built yet", and `RSW_Shokk_FeraliskBrood.xml` mentions "skreth" only as a proposed name.

## Built this pass (3 of 7)
- `src/RimMandrake/FeverWood/Defs/ThingDefs_Races/RM_FeverWoodCast.xml` (new) adds `RM_Lommerel`, `RM_Nemmel` and `RM_Grolth`, each as a ThingDef plus a PawnKindDef. They use the ruled bodySize and diet, and vanilla behaviour only. The grolth is predator=false, so it eats corpses and never chases (ban 3). Every other number carries a `PROVISIONAL` tag.
- `src/RimMandrake/FeverWood/Defs/BiomeDefs/RM_FeverWood.xml` gets three inline element rows on `wildAnimals` at the ruled commonalities (0.4, 0.4, 0.05). These are the creatures' only home.

## Art
Finished renders were installed through `art.py install --reason artpipe-collect`, nine facings in all. Each facing's last registry verdict is pass, and there is no `Transient/*.decisions.json` ruling on them. They are at `Textures/Things/Pawn/Animal/RM_{Lommerel,Nemmel,Grolth}/`.
The art-ledger events first landed in `infrastructure/state/art/events/BENCH.jsonl`, because `artledger.seat()` defaults to BENCH when `RIMFLOW_SEAT` is unset. I moved those 9 lines, which were the only diff in that file, to `FOUNDRY.jsonl` and restored BENCH.jsonl to HEAD. Trap: export `RIMFLOW_SEAT=FOUNDRY` before running `art install`.

## Validation
- XML parses.
- `validate_patch.py src/RimMandrake/FeverWood` with all three `--defs` roots: 52 files, 0 errors, 2 advisory warnings (the existing nomatch pattern).
- `selftest_feverwood.py`: all passed.
- No C# changed, so no winbuild was needed.
- Body-part groups were checked against Core (Cobra/Snake uses Mouth; the paws body uses FrontLeftPaw and HeadAttackTool).

## Left
- **Silloch: STOPPED.** It needs a bark wait-ambush comp. The only candidates are CreatureBehaviors' `CompProperties_FalseShadeAmbusher`, which moves the animal to OPEN ground (the opposite of hiding on bark), and `CompProperties_AquaticAmbusher`, which only works in water. A new comp is needed, either in CreatureBehaviors (read-only for this pass) or in FeverWood/Source. Also owed: `<RM_AlarmResponderExtension><tag>FeverWoodCrown</tag>` on it, which the ollareth alarm is waiting for.
- **Brathek:** ordinary animal, plus a settings toggle for wall/bough damage (the open ruling is not guessed). Not built.
- **Gorrameth:** vanilla herbivore, bodySize 4.0, commonality 0.02. Not built; the easiest one next.
- **Skreth, matron, `RM_FactionDef_SkrethBrood` and the change to `RM_MapComponent_TwoFrontLure`:** C#, not built.
- `AnimalTolerances_Ashkarr.xml` is GENERATED ("do not hand-edit") and lists no Fever Wood creature, so spec §6 needs the generator, not a hand edit.
- Criteria (foundCount 16, live) not run: offline pass.
