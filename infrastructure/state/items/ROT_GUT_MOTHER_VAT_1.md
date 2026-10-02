# ROT_GUT_MOTHER_VAT_1 — The Gut-Mother: a digestive sac cut from the dead hwelgrue grows a vat anywhere that gives back implants and gear from corpses; starter cultures are a trade good

Caused by `ROT_SCORING_SITTING_1` (turn 1, new-marks redo). Free tier, `mandrake.rm.therot`. Design:
`design/Jawa/worldbuilding/biomes/rot_new_marks_redo_2026-10-02.md` T1, review
`design/Jawa/worldbuilding/biomes/rot_bedazzle_review_2026-10-02.md` §8. Mark 2 (discoverable technology that
travels).

Ruling: **tech = BOTH The Gut-Mother and The Unjoining Draught** (decision taken by question card 2026-10-02
10:50 PDT), the Gut-Mother **chosen with the card's stated condition that a culture may leave the Rot**.
🔴 **Ruled exception to ban 4** (*"no stockpilable teas or symbionts"*; the come-here-and-brew law): the
gut-mother culture is neither a tea nor a symbiont and **may leave the Rot**; it is exempt from the live-prep
viability clock. The ban is otherwise unchanged: no tea or symbiont becomes portable through this item. Recorded
in the review §8.

## spec

1. **The sac.** `ThingDef RM_GutMotherSac`: a butcher product of `RM_Hwelgrue` (`ROT_HWELGRUE_GIANT_BUILD_1`
   part 6), one per carcass; a living item that slowly dies (rots in ~15 days, vanilla `CompRottable`) unless
   used. Not touched by `RM_Patch_LivePrepViability` (exempt by def, not by map).
2. **Learning it.** `ResearchProjectDef RM_GutMotherCulture` (prerequisite `RM_AdvancedFungi`) that can only be
   started after a sac has been studied: measure the 1.6 options (Anomaly's `CompStudiable` + the research
   project's `requiredAnalyzed`, or a techprint-style unlock) and use the vanilla one that fits; never a bespoke
   meter.
3. **The vat.** `ThingDef RM_GutMotherVat`, a grown building (the existing grown-furnace shape:
   `RM_` grown furnace in `ThingDefs_Buildings`), built anywhere (not Rot-only) from one `RM_GutMotherSac`
   **or** one `RM_GutMotherStarter`, plus fungal material. It takes corpses as fuel (`CompRefuelable`-style
   loading with a corpse filter, or a hauling bill: measure which vanilla path loads corpses cleanly) one at a
   time. New C# `RM_CompGutMotherDigest`: after **1 day** (setting) it destroys the corpse and spawns, beside
   the vat:
   - for every hediff on the dead pawn whose def has `spawnThingOnRemoved` (bionic and archotech parts,
     implants; `Hediff_AddedPart` and the implant hediffs), that thing (chance per item, setting, default 1.0);
   - all equipment, apparel and inventory the corpse carried.
   Nothing organic comes back. **Measured 2026-10-02 (RimSage):** vanilla only spawns `spawnThingOnRemoved`
   from a **living** surgery (`Recipe_RemoveImplant`, `MedicalRecipesUtility`) and butchering yields only
   life-stage `butcherBodyPart` things (`Pawn.ButcherProducts`, Pawn.cs ~4276); the full butcher path for
   implants was not read, so "no vanilla way to recover an implant from a corpse" is believed, not proven.
   Check before building; if one exists, the vat still stands (it returns everything at once, gear included).
4. **Feeding the mother.** The vat needs a nutrition top-up (any raw meat or rotten food, a small amount per
   day) or it goes dormant (no digestion, visible), never dies outright.
5. **Starter cultures, a trade good.** `RecipeDef RM_SplitGutMother` at the vat: consumes vat time and
   nutrition, makes one `ThingDef RM_GutMotherStarter` (a sealed jar of live culture; tradeable, a high market
   value, stackable to 5, does **not** rot or lose viability off the Rot: the ruled exception). Sellable to any
   trader who buys exotic goods; a starter builds a new vat anywhere.
6. **Readable signs:** the vat's inspect line (*"Digesting a body. About 14 hours."*, *"Dormant: hungry."*),
   the spill of returned items, a letter the first time an implant comes back.
7. **Mod Settings** (Technology section): on/off; digestion time; recovery chance; starter value.

Depends on: `ROT_HWELGRUE_GIANT_BUILD_1` (the sac's source). Art: `RM_GutMotherSac`, `RM_GutMotherVat`,
`RM_GutMotherStarter` in `infrastructure/artpipe/art_lists/rot_turn1_2026-10-02.csv`.

## criteria

Deterministic, in `THE_ROT_FIRST_SCRIPT_1`'s `validation.py`, through `jawa/get_defs` and debug `[Tool]`s:
- Defs resolve: `ThingDef/RM_GutMotherSac`, `ThingDef/RM_GutMotherVat`, `ThingDef/RM_GutMotherStarter`,
  `ResearchProjectDef/RM_GutMotherCulture`, `RecipeDef/RM_SplitGutMother` (`foundCount` = 5).
- `RM_GutMotherCulture` cannot be started before a sac is studied and can after (research manager read).
- On a **non-Rot** test map: a vat given a colonist corpse carrying a `BionicArm` hediff, a rifle and a parka
  produces, after the setting's time, one `BionicArm`, the rifle and the parka beside it, and the corpse no longer
  exists.
- A vat with no nutrition for the dormancy window does not progress a loaded corpse (progress read twice).
- `RM_GutMotherStarter` carried to a non-Rot map for 30 days keeps its count and has no viability/rot hediff
  or comp ticking it down; a tea carried the same way still loses viability (the ban unchanged).
- `RM_GutMotherStarter` is tradeable (`tradeability` read) and `RM_SplitGutMother` produces exactly one.
- Each Mod Settings toggle off removes exactly its effect.
</content>
</invoke>
<invoke name="Bash">
<parameter name="command">head -1 /home/mandrake/rm/bench/infrastructure/state/items/ROT_GUT_MOTHER_VAT_1.md