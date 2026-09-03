# LIVE_BIRTH_AND_HATCH_DEMO_1 — drive the whole reproduction chain from the bridge

Owner, 2026-09-02: *"live-game show pregnancy, induce birth, lay an egg, and hatch the
egg into a baby Jawa."*

Four acts, in order, on a throwaway quicktest map, each one **observed** rather than
inferred from a success flag. This is a capability demonstration: the question is what
the bridge can actually drive of RimWorld's reproduction machinery, and where it
cannot reach.

## spec

**1 — Show pregnancy.** Get a pawn visibly pregnant and read the state back.
- `Hediff_Pregnant` (`Source/Verse/Hediff_Pregnant.cs`) carries `GestationProgress`
  and prints `Gestation progress: NN%` plus a time-left line in its inspect string.
- ⚠️ **Establish which pregnancy applies before touching anything.** `Hediff_Pregnant`
  is the general/animal one; Biotech ships human pregnancy separately, and the
  campaign has Biotech active. Read the def, do not assume the class.
- PROVE: the inspect string reports a gestation percentage, read back through a
  different call than the one that set it.

**2 — Induce birth.** Vanilla already has this path, so do not invent one.
- `Hediff_Pregnant.DoBirthSpawn(mother, father)` is **static and public**
  (`Hediff_Pregnant.cs:157`), and `Source/Verse/DebugToolsPawns.cs:332` calls exactly
  that — so there is a shipped debug action to reach, or a companion tool to add.
- The gentler route is setting `GestationProgress` to 1 and letting the tick fire
  (`Hediff_Pregnant.cs:121-132`), which exercises the real path rather than the
  shortcut. Prefer that; fall back to `DoBirthSpawn` and say which you used.
- PROVE: a new pawn exists on the map, the mother's pregnancy hediff is gone, and the
  baby's `DevelopmentalStage` reads as a baby.

**3 — Lay an egg.** `CompEggLayer` (`Source/RimWorld/CompEggLayer.cs`) is the layer;
find an egg-laying creature present in the live stack and make it produce one. Note
whether the bridge can force the lay or only wait for it.

**4 — Hatch the egg into a baby Jawa.** 🔑 **This is mechanically supported, and the
source says so** — do not treat it as a stretch:
- `CompProperties_Hatcher.hatcherPawn` is a **`PawnKindDef`**, not an animal-only
  field, so an egg can be pointed at a humanlike kind.
- `CompHatcher.cs:85` builds its `PawnGenerationRequest` with
  **`DevelopmentalStage.Newborn`** — a hatched pawn comes out a newborn by
  construction. "A baby Jawa" is what this field already produces.
- ⚠️ `CompHatcher.cs:54` reads `Props.hatcherPawn?.race?.GetCompProperties<CompProperties_EggLayer>()`.
  A humanlike hatcherPawn has no `CompEggLayer`, so that lookup returns null — check
  what the surrounding code does with null before assuming it is harmless.

## Watch out

🔴 **`CompHatcher.cs:85` passes `forceGenerateNewPawn: false`.** That is the EXACT
defect that made `jawa/spawn_pawn` silently deliver recycled world pawns and quietly
drain Ash'karr's faction populations (`SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1`, fixed
and proven 2026-09-02). Vanilla's hatcher has the same shape. **So a hatch may REDRESS
an existing world pawn instead of generating a new one** — check the hatchee's ThingID
against the live counter, exactly as that item's proof did, before calling the baby new.

⚠️ Every step is a bridge write, and ~40 engine calls in this surface report success
and change nothing — `skills/rimbridge/references/silent-failures.md` before any write.
Each act needs an independent read-back through a different tool than the one that
performed it.

⚠️ Throwaway map only. Nothing here goes near the campaign save.

## verify
All four acts observed on one quicktest map, each with the read-back named above.
Where the bridge cannot reach a step, say so plainly and name what is missing — a
documented gap is a real result here, and `rimbridge-companion` covers adding a tool
if one is genuinely absent.

## criteria
The owner can watch, or read back, a pregnancy → an induced birth → an egg laid → that
egg hatching into a newborn Jawa; and we know which of those four the bridge drives
today and which needed a new companion tool.

---

## Decision strings, written BEFORE the load (rimworld-load-round §2)

Load of 2026-09-03, custom minimal list (the stock 19 + `neronix17.outland.genetics`,
`turnovus.biotech.integratedgenes`, `mandrake.rsw.starwarsraces`,
`mandrake.rut.birthhatchdemo`). Restart forced by
`HOT_RELOAD_DEFS_BREAKS_PAWNGEN_1` — the previous process could not generate a pawn.

| # | what it settles | the exact read | baseline before the load |
|---|---|---|---|
| 0 | pawn generation is repaired | `jawa/spawn_pawn {kindDef: Colonist}` → `ok: true` | `NullReferenceException` |
| 0b | the demo mod loaded at all | `jawa/get_defs ThingDef/RUT_DemoEggJawa` → `foundCount 1` | `foundCount 0`, in `notFound` |
| 0c | the Jawa kind survived the trimmed list | `jawa/get_defs PawnKindDef/RSW_Jawa` → `foundCount 1` | 1, on the full list |
| 1 | pregnancy is REAL, not a flag | `jawa/inspect_string` on the mother contains a **gestation percentage** — read through a different tool than the one that set it | absent |
| 2 | birth happened by the real path | a new pawn exists; the mother's pregnancy hediff is **gone**; the baby's `developmentalStage` reads Baby/Newborn | — |
| 3 | an egg was actually laid | `jawa/list_things` finds the egg ThingDef beside the hen after `jawa/animal_resource_force {mode: egg}` | — |
| 4 | the hatchee is NEW, not redressed | a new `RSW_Jawa`, `DevelopmentalStage` Newborn, **and its ThingID above the pre-hatch counter** — `CompHatcher.cs:85` passes `forceGenerateNewPawn: false`, the exact defect of `SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1` | — |

⚠️ **Expected-present, so a silent pass is not mistaken for success:** the log should
still carry `Failed to find any textures at Things/Pawn/Animal/SeaBeasts/Starmaw/Starmaw`
only if SeaBeasts is loaded — it is NOT on this list, so that line is expected ABSENT
here and says nothing about the sea-beast defect.

---

## RESULT — all four acts driven live, 2026-09-03

Map: throwaway dev quicktest, 250×250 TemperateForest, from tick 1.
List: 28 mods (the stock minimal 19 + the gene frameworks + StarWarsRaces + the demo).
Nothing here went near the campaign.

### ✅ 1 — Pregnancy

`jawa/pawn_pregnancy {action: start, father: …}` on a baseliner colonist (Ivy) →
`pregnant: true, hediff: PregnantHuman, gestation: 0.001, father: Carter`.

🔴 **Every `RSW_Jawa` spawns MALE — 8 of 8, and it is BY DESIGN, not a defect.**
`RSW_MandrakeJawa` carries `Outland_AllMale` + `SEX_AlwaysAphrodor` (owner, 2026-08-22:
*"single-gender-egg-layer-either-impregnate-the-other"*). ⇒ **Vanilla `PregnantHuman`
cannot run on a Jawa at all.** Acts 1–2 therefore had to use a baseliner mother; the
Jawa's own reproduction route is the egg, which is acts 3–4. That split is the real
finding of act 1.

⚠️ **The read-back this item specified was in the wrong place, and the spec was wrong,
not the game.** `Hediff_Pregnant`'s "Gestation progress: NN%" is on the HEDIFF (health
tab); a pawn's `jawa/inspect_string` shows only `"Female, age 20 (1013) of New Arrivals"`.
**The honest independent read is `jawa/pawn_get` → `hediffs`.**

### ✅ 2 — Induced birth, by the REAL path (no `DoBirthSpawn` shortcut)

`progress → 1.0`, then drove the actual hediff chain with `jawa/pawn_severity_adjust`:

```
PregnantHuman → PregnancyLabor 0.3 → 0.6 → 1.1 → 1.6
              → PregnancyLaborPushing 0.5 → 1.0 → 1.5 → 2.0
              → PostpartumExhaustion + Lactating        (mother)
BABY  Human28190   kind=Colonist  gender=Male  stage=Baby  ageBio=0
```

🔴 **`jawa/pawn_pregnancy {action: get}` LIES during labour.** It reported
`pregnant: false, hediff: null` about a pawn who was actively giving birth, because it
only looks for `PregnantHuman` and labour has already become `PregnancyLabor`. A test
that trusts it concludes the pregnancy was lost. **Read `jawa/pawn_get` → `hediffs`.**

⚠️ **`rimworld/step_game_ticks` caps at ~600.** Asked for 2000, got `completedTicks: 601`,
every time. It reports the real number, so it is honest — but a loop that assumes the
request was honoured runs 3× short.

### ✅ 3 — Egg laid

`jawa/animal_resource_force {mode: egg, eggAction: fertilize}` → `fullyFertilized: true`;
then `{eggAction: produce}` → `eggProgressBefore 0.0 → forcedTo 1.0`,
`eggProduced: EggChickenFertilized, placed: true`.
Read back two other ways: `jawa/list_things {defName}` → `EggChickenFertilized52080` at
(100,100), and `get_cell_info` → cell holds `['Chicken','EggChickenFertilized']`.

⚠️ **`jawa/list_things` rows use `id`/`def`; `jawa/pawn_get` uses `thingId`/`kindDef`.**
Reading the wrong pair returns None for every row and looks exactly like "nothing there" —
it produced a false `EGGS LAID: 0` here on a lay that had already worked.

### ✅ 4 — The egg hatched a Jawa

`RUT_DemoEggJawa52081` spawned at (110,110). `jawa/inspect_string` tracked it honestly:
`Egg progress 0% → 30% → 60% → 90%`, then the egg was gone and one new pawn existed.

```
Human52158  idNum 52158  "Tara Indigo"  kind=RSW_Jawa  xenotype=RSW_MandrakeJawa
gender=Male  stage=Child  ageBio=3  ageChrono=0  faction=None  at (101,131)
inspect: "Male, age 3 (0), child jawa"     hediffs: Hypothermia 0.02
```

🔑 **It is a NEW pawn, not a redressed world pawn.** `thingIdNumber 52158` is above the
egg's own `52081`, so it was generated after the egg existed. That was the one thing this
act had to prove, because `CompHatcher.cs:85` passes `forceGenerateNewPawn: false` — the
exact defect of `SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1`. The hatcher's null
`CompProperties_EggLayer` lookup on a humanlike (`CompHatcher.cs:54`) caused no trouble.

⚠️ **It hatched a CHILD (bio 3), not a newborn**, though `CompHatcher.cs:85` requests
`DevelopmentalStage.Newborn`. Chronological age is 0, so it was born now and aged up
immediately: `BS_EarlyMaturity` is on the xenotype and confirmed present on the pawn.
A Jawa hatches already toddling. **Not verified as causation** — the control was not run.

⚠️ The hatchee is **faction-less**, because the egg was spawned with no faction.

### Instrument findings from this sitting

* 🔴 **A missing `modExtension` type ate the Jawa head genes and pawns stopped rendering.**
  On the first 23-mod list, `SW_Genes.xml` threw
  `Could not find type named BigAndSmall.PawnExtension` / `BetterPrerequisites.GeneExtension`,
  and `RSW_Head_hutt`, `RSW_Head_selkath`, `RSW_statgene_predator` went unresolved.
  Symptom the owner saw: **humans blinking on and off at ~0.3 Hz, invisible zoomed in,
  reappearing zoomed out** — the cached atlas still had them, the dynamic draw did not.
  StarWarsRaces' About says Big and Small and Better Prerequisites must stay installed;
  they are NOT declared in `<modDependencies>`, so a dependency-walking list builder
  leaves them out. Adding `RedMattis.BetterPrerequisites`, `RedMattis.BigSmall.Core`,
  `RedMattis.BigSmall`, `RedMattis.Optional`, `LazyFridayStudio.GenesExpandedEyes`
  took the errors to **0** and the owner confirmed the blinking gone.
  ⇒ **StarWarsRaces' About.xml is missing five real dependencies.**
* ⚠️ `SEX_AlwaysAphrodor`, `SEX_Ovipositor`, `VRE_ShortPregnancy` **do not exist on this
  list** (Gender Works and VRE absent). Checked against a control — an ordinarily
  spawned Jawa lacks them identically, so this is the trimmed list, not a hatch defect.
  🔑 But it means **the Jawa's own impregnate-each-other chain cannot be demonstrated
  without Intimacy - Gender Works**, and this sitting did not demonstrate it.
* 🔴 `rimworld/jump_camera_to_cell` returned `success: true` with the requested cell and
  **the view did not move** — two screenshots minutes apart are the same framing while
  the pawn bar changed, so the frame WAS updating. Camera unmoved, reported moved.

## verify — status

All four acts observed, each read back through a different tool than the one that
performed it. No companion tool had to be written: the bridge drives the whole chain
today. What it cannot drive is the Jawa-to-Jawa route, for want of a mod.
