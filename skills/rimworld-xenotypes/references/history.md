# History: the measurements, and the lines that were wrong

`SKILL.md` holds the lessons. This file holds dates, old counts, old names and corrected claims (corrected 2026-11-23).

## The rescue, and where the mod is now

The lessons were first measured on a 587-mod 1.6 stack. The mod was then at
`D:\Luke\dev\RimMandrake\src\Jawa\RimMandrake_StarWarsRaces` (`src/Jawa/RimMandrake_StarWarsRaces/`): 69 xenotypes, 114 genes,
104 head types. "Our 69 species defs use these fields and no others" was true then: `nameMaker` came later.

Counted 2026-11-23 in `src/RimStarWars/StarWarsRaces`: 70 XenotypeDefs (69 generated, and `RSW_MandrakeJawa`), 185 GeneDefs,
151 HeadTypeDef elements (128 with a defName), 87 PawnKindDefs (69 of them one per species), 71 RulePackDefs, 189 word lists, 922 PNGs.

The tier rename put `RSW_` on the names. Old: `RimMandrakeAbednedo`, `RimMandrake_AbednedoHead`,
`RimMandrake_Jawa_Eyes_HugeOrange`, `MandrakeJawa`, `RimMandrakeJawa`.

## Corrected claims

0. **§1.** The old words were: "the gene list is fixed" does not mean "every pawn of this species looks identical".
1. **§3a, which colour renders.** The text of 2026-09-20 said that a gene list "is NOT a pool", and that another
   skin-colour gene adds "a *competing override*" and no variety. It said that "A line-up of N pawns of one species is a SAMPLE OF
   ONE", and not to build a "palette review" on it. It left open "which one renders is NOT established here", with three
   candidates: `displayOrderInCategory` precedence, a per-pawn seeded pick, or the added `Skin_MelaninN` compositing over
   the override. It said that no "one fixed winner" story explains the three Bith colours. It said not to promise an owner that an edit of the list changes what they see. It called the
   claim "each pawn rolls one of six" the most expensive misconception about xenotype colour. The engine code (RimSage, 1.6)
   settles it: a random pick per pawn among the conflicting genes. The measurement of 17 identical gene lists stands.
2. **§5, the unset defaults.** The text said: Unset defaults are `0` and `false`. The engine defaults are `1` and `true`
   (`XenotypeDef`). The reading on `BTD_Jawa` (declares neither; "only 1 of BTD's 71 xenotypes declares
   `factionlessGenerationWeight` at all"; `0.0 / False` at runtime) was "identical to `MandrakeJawa`, which must and does generate". Its
   cause was not found. BTD's 1.6 file holds 70 XenotypeDefs; `BTD_Yoder` is the one that declares the weight (0.001).
3. **§5, `<li>` in `xenotypeChances`.** The text said that ParseFloat returns null and that the loss is silent. The parse
   throws, and the loader logs `Exception loading def from file`. The skill's description still says "silently".
4. **§3, `skipFlag Hair`.** The text said that it hides the node "when hair is drawn over it". Worn headgear sets the flag
   (`PawnRenderTree.AdjustParms`).
5. **§3, `rotDrawMode`.** `references/appearance.md` said that without it "the species partially reverts to human on death". The
   default is all three states.
6. **§3, head pool.** The text did not name `randomChosen`.
7. **§4.** "A XenotypeDef on its own is unverifiable in game. To test our 70 xenotypes we had to author 70 PawnKindDefs."
   `jawa/spawn_pawn` with `xenotype` and any kind does it. The skill's description still says "cannot be spawned at all
   without a PawnKindDef". A description changes only with the trigger evals of `skill-creator`.
8. **§8, `.xtp`.** The file also holds the genes and `iconDef`. "Keep the two in step by hand" was replaced: the
   35-gene set is now 38 in the def, on purpose.
9. **§9.** "The live def dump is disk state, not process state." A DefDump comes from a running game, after patches. For
   Cherry Picker it comes after the deletion of XenotypeDefs (`infrastructure/state/facts/dump-is-pre-cherrypicker.md`).
   For BTD's dedup, the dump of that time held the removed names. "Bridge rights belong to CHECK": CHECK is a retired seat.

10. **§10.** "`ParentName` resolves to nothing and the child is a silent discard." `XmlInheritance.GetBestParentFor` logs an
    error, and the child loads with its own XML only.
11. **§3, `texPaths`.** "two pawns of one species differ": they can differ. A pick from few variants often matches.

## Facial Animation

- Measured 2026-08-15: 70 species moved into a new mod under new `RimMandrake*` names. All 86 exclusions still read
  `Human-BTD_*`, `Human-OuterRim*`, `Human-guy762_*`. All 70 new species had human faces at once.
- 2026-10-21: the mod ships the opt-out (item `FACE_OPTOUT_REPAIR_ONLY_AT_HOME`). The list holds 69 names.
- 2026-11-23: the owner's FA file held 68 `Human-RSW_` entries, `Human-MandrakeJawa` (dead) and no
  `Human-RSW_MandrakeJawa`.

## The survey tools

The genome tools existed for a day before this skill did. Their knowledge was in scripts and in one HTML page,
`design/Jawa/worldbuilding/review/genome_register.html`, "the rendered result, art inlined". That page was deleted with the outmoded review sheets on
2026-09-01 (1016e3823c).
