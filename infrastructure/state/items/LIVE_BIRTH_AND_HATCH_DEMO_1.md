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
