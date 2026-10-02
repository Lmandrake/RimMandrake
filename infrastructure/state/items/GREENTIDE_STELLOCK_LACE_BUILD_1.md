# GREENTIDE_STELLOCK_LACE_BUILD_1 — stellock lace: study a branch that closes its own veins, then stop every bleed on a pawn, anywhere

Caused by `GREENTIDE_SCORING_SITTING_1` (turn 1). Free tier, `mandrake.rm.greentide`. Design:
`design/Jawa/worldbuilding/biomes/greentide_bedazzle_review_2026-10-02.md` §5 idea 1 (GPT, "Nethr lace"),
§4 row 2, §8. Ruling: **new marks: the blood-stopping lace only** (decision taken by question card
2026-10-02 07:43 PDT): *a doctor studies a cut jungle branch that closes its own veins, and the colony
learns to make a cartridge that stops all bleeding on a wounded pawn, anywhere.* ⛔ The hull rasp and
noise cover were not chosen and are not to be built.

Mark 2 (discoverable technology): learned here, used anywhere, like the lightning breakers. **Renamed:**
GPT's "nethr" collides in `design/` (4 files) and is not used. The name is **stellock** (Greentide accent,
*-ock*, doubled *ll*): python sweep of `src/`, `design/`, `infrastructure/` 0 hits (probes `korrum` 92,
`krannock` 15 files); Wookieepedia search 0 results (probe `wyyyschokk` 50); artpipe `find stellock` 0
hits. 2026-10-02.

## spec

1. **The specimen, `RM_StellockBranch`** (item, free tier): a severed jungle branch whose cut end has
   drawn closed under a glossy film, the vessels inside visibly pinched shut. Source: when any tree of the
   Greentide roster (`RM_Greentide_TreeRoster.xml`, plus `RM_Greatbole`) is felled on a Greentide map, by
   a pawn, a tree fall (`RM_TreeFallUtility`) or a thurrock, there is a small chance (Mod Settings, default
   about 1 in 8) of one branch dropping at the stump. It rots like raw plant matter (days, not seasons), so
   it must be studied while in the jungle or carried home quickly.
2. **The study: reuse the Forge's found-tech pattern, do not write a second one.**
   `src/RimMandrake/TheForge/Source/RM_ForgeSpunstone.cs` (`RM_CompSpunstoneStudy`, a knowledge-less
   `CompStudiable` that core's `WorkGiver_StudyInteract` already serves, RimSage-checked in that file's
   header) counts study interactions into a colony knowledge counter and keeps the project hidden
   (`IsHidden` postfix) until a threshold, then sends a breakthrough letter naming who studied. Give
   `RM_StellockBranch` the same comp shape (generalise the Forge's classes into a shared
   `RM_CompFoundTechStudy` keyed by project def, or subclass; one mechanism, two users), so a doctor or
   researcher studies the branch and, at the threshold, `RM_Research_StellockLace` appears (prerequisite:
   vanilla Medicine production research; cost first value about 1200). The study does not consume the
   branch; the branch's own rot does.
3. **The cartridge, `RM_StellockLace`** (medical item, stackable): recipe at a drug lab or medical bench,
   first values: `RM_SapResin` 2 (the Greentide's sap, free tier), `MedicineIndustrial` 1, `Cloth` 4 (the
   *vascular film*). Work about 1500 ticks. Market value high: it is costly on purpose (balanced by cost,
   not scope).
4. **Use: it stops all bleeding on one pawn.** Administered like a vanilla medicine-on-self/other job (an
   `CompUseEffect` on the item, used by a doctor on a patient or by the patient). It adds hediff
   `RM_StellockLaced` whose stage sets the pawn's total bleed rate to zero for a duration (Mod Settings,
   default 12 in-game hours): every bleeding wound **and amputation stumps** stop bleeding. 🔴 UNMEASURED:
   whether 1.6 `HediffStage` has a total-bleed factor field that `HediffSet.BleedRateTotal` reads (believed
   `totalBleedFactor`; confirm in RimSage). If it does, this is pure XML; if not, a one-line Harmony postfix
   on `HediffSet.BleedRateTotal` gated on the hediff. **Wounds still need tending**: the lace does not tend,
   heal, or remove infection risk; when it expires, untended wounds bleed again.
5. **Usable anywhere.** Learned once, the recipe and the item work on any map and any biome; only the sap
   ties it back to the Greentide.
6. **Readable signs:** the branch's glossy closed cut, the "laced" hediff on the health tab with its time
   left, a bleed-rate readout of 0 while it holds, wounds still listed as untended.
7. **Mod Settings:** on/off (off = no branch drops, no project); branch drop chance; lace duration.

Reuses: `RM_SapResin`, vanilla research, vanilla medical item use, the Forge's found-tech study
(`RM_CompSpunstoneStudy`). New code: generalising that study comp, possibly the bleed postfix (UNMEASURED
above).

Depends on: nothing open. Art: `infrastructure/artpipe/art_lists/greentide_turn1_2026-10-02.csv`
(`RM_StellockBranch`, `RM_StellockLace` rows).

## criteria

Deterministic state reads through `jawa/get_defs` and debug `[Tool]`s, recorded in the Greentide functional
script:
- `ThingDef/RM_StellockBranch`, `ThingDef/RM_StellockLace`, `HediffDef/RM_StellockLaced`,
  `ResearchProjectDef/RM_Research_StellockLace` and the lace's `RecipeDef` resolve on the free tier alone; a
  python search of `src/` for `nethr` returns 0 (probe `krannock` > 0).
- With the drop chance forced to 1: felling a roster tree on a Greentide test map spawns one
  `RM_StellockBranch` at the stump; felling the same tree on a non-Greentide map spawns none.
- Before the study, `RM_Research_StellockLace` reports `IsHidden` true and not startable; after study
  interactions reach the threshold, it reports `IsHidden` false and startable, and one breakthrough letter
  exists. The Forge's spunstone project still hides and unhides on its own counter (no cross-talk).
- A pawn with three cut injuries and one amputated hand: bleed rate total > 0 before use; after using one
  `RM_StellockLace`, bleed rate total == 0, every injury still reads untended, and the pawn holds
  `RM_StellockLaced` with ticks-left equal to the configured duration. After the duration (simulated
  ticks), bleed rate total > 0 again for the still-untended wounds.
- On a non-Greentide test map (any other biome), the same use gives the same zero bleed rate.
- Each Mod Settings toggle off removes exactly its effect.
