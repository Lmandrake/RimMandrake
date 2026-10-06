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

## Pass 2 (2026-10-06, FOUNDRY helper, uncommitted): gorrameth, brathek, silloch
- **Built:** `RM_Gorrameth` (plain herbivore, body QuadrupedAnimalWithHooves, bs 4.0, lone 1~1, 0.02), `RM_Brathek` (Snake body, bs 0.9, foodType `VegetarianRoughAnimal, Tree`, 0.5), `RM_Silloch` (BeetleLikeWithClaw, bs 0.6, predator=false, 0.3). Defs are in `RM_FeverWoodCast.xml` and the rows are inline on `RM_FeverWood/wildAnimals`. Non-ruled numbers are marked PROVISIONAL, and every brathek number is marked INVENTED.
- **Brathek:** its only wood damage is vanilla tree-eating. No wall, building or boughway damage is built, because the dig rate and "directed" are open rulings. New toggle `brathekBoresWood` (default on). Off strips `FoodTypeFlags.Tree` at startup and on settings save (`Source/RM_BrathekBoring.cs`).
- **Silloch:** new `Source/RM_CompSillochAmbush.cs` lives in FeverWood's own source, with no shared code touched. It presses against an adjacent tree or FeverTrunk and waits. It strikes an adjacent victim of bodySize ≤1.0, follows with vanilla AttackMelee (expiry 600), and lets go past 4 cells (never chases). It eats its own kill in place. Tame: hostiles only. New toggle `sillochAmbushEnabled`. It carries `RM_AlarmResponderExtension` tag `FeverWoodCrown`, so the ollareth scream now has a responder. ⚠️ That alarm sets it Manhunter, which does pursue. The design ruled this ("pulls the crown's predators toward whatever is bothering it"), but it sits in tension with ban 3. Owner check worth flagging.
- Stale comments in `RM_SapSuckerGuild.xml` ("silloch not built / no responder tagged") were corrected.
- **Art:** 9 facings were installed via `art.py install --reason artpipe-collect` with `RIMFLOW_SEAT=FOUNDRY`, and the events landed in FOUNDRY.jsonl. Every last registry verdict is pass, and no decisions.json mentions these three.
- **Validation:** `winbuild.py FeverWood` built with 0 warnings and 0 errors (DLL+srchash updated). validate_patch reports 52 files, 0 errors, 2 advisory. `selftest_feverwood.py` passed. Its toggle-count pin went 16→18 for the two new toggles; the toggle roundtrip components are auto-declared from the source. Offline: the six descriptions are clean of banned words, none has MaxFlightTime, the six texPaths exist, and the six wildAnimals values are exact.
- New .cs files are DIRTY (never reviewed).
- **Left:** skreth, matron, `RM_FactionDef_SkrethBrood` and the TwoFrontLure change (lure C# pass); `AnimalTolerances_Ashkarr.xml` via its generator; live criteria (foundCount 16).

## Pass 3 (2026-10-06, FOUNDRY helper, uncommitted): skreth, matron, brood faction, lure change
- **Built:** `Defs/ThingDefs_Races/RM_Skreth_Race.xml` (new). One race `RM_Skreth` (BeetleLikeWithClaw, bs 2.5 ruled, CarnivoreAnimal, predator=true as one of the two raiders, Insectoid) with two PawnKindDefs, `RM_Skreth` (cp 140) and `RM_SkrethMatron` (same race, `fixedGender` Female, drawn larger, cp 200). The matron reuses the skreth renders. ecoSystemWeight 0, and there is no wildAnimals row (off-map only). Every non-ruled number is marked PROVISIONAL.
- **Faction:** `Defs/FactionDefs/RM_FactionDef_SkrethBrood.xml` (new) is cloned from KurrethSwarm: hidden, permanentEnemy (so it is hostile to the kurreth both ways), with a fixedName. Its Combat group is skreth 10 to matron 2 (PROVISIONAL).
- **Lure:** in `Source/RM_MapComponent_TwoFrontLure.cs`, the Webwork front is now `WebworkFrontFactionDefName` (a public static, for a later bridge read or `[Tool]`). It is `RSW_Shokk_FeraliskBrood` when that is loaded, otherwise `RM_FactionDef_SkrethBrood`. The ants-for-both fallback branch is gone. A pending second wave whose saved name is either Webwork faction re-resolves to this session's front. The settings tooltip in `RM_FeverWoodMod.cs` that said the second front needs the Star Wars collection was corrected.
- **Art:** 3 facings installed (`RIMFLOW_SEAT=FOUNDRY`, `--reason artpipe-collect`). Each facing's last registry verdict is pass, and no decisions.json mentions skreth.
- **Validation:** XML parses. The descriptions are clean of banned words. validate_patch reports 54 files, 0 errors, 2 advisory. `selftest_feverwood.py` passes (it now sees 6 hidden FactionDefs, all named). `winbuild.py FeverWood` built with 0 warnings and 0 errors. No toggles were added, so no pin changed.
- **Outside FeverWood (read-only, NOT fixed):** the header of `src/RimStarWars/Shokk/Defs/FactionDefs/RSW_Shokk_FeraliskBrood.xml` still says skreth is "NOT owner-ruled" and that the second front gives "ants only". Both are false now. Tension worth a look: `RM_Ollathrix` (Webwork) is ALSO skinned as the Wyyyschokk, so the "one creature, two skins" ruling now has two free bodies under one canon skin.
- **Left:** the live criteria (foundCount 16, HostileTo read, lure inspect read); `AnimalTolerances_Ashkarr.xml` via its generator; review of the new .cs files.
