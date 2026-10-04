## the ask (owner, 2026-09-19)

Owner spotted `Impid` (vanilla Biotech's horned, fire-spitting xenotype — read as
"fire imp") and ruled: *"Only Star Wars xenotypes are supposed to be here."* Rather
than purge Impid alone, he asked for a proper BENCH assessment of every
non-Star-Wars xenotype for possible removal, weighing: **(a) do our Star Wars-native
xenotypes already cover the same gameplay role/niche this one fills, and (b) what
does removing it actually cost/break.**

## what FOUNDRY found (2026-09-19, def dump 621 mods, captured 2026-09-19T12:48:16Z)

`src/RimUtinni/PawnFlavor/Patches/PawnFlavorPhase2_Xenotype.xml` (2,922 lines) is a
deliberate, already-built system that keeps a long list of vanilla/other-mod
XenotypeDefs ACTIVE and re-flavors their label/description with campaign-appropriate
lore text, rather than cutting them. This is not a stray leftover — someone
purpose-built this file to give every vanilla xenotype a Star-Wars-flavored
description (e.g. Impid: *"Horned and quick as a scared varmint... can spit fire..."*).

**14 non-Star-Wars xenotypes touched by that file** (everything else in it is an
`RSW_RimMandrake*` species, correctly in scope):

```
Baseliner   Dirtmole   Genie   Highmate   Hussar   Impid   Neanderthal
Pigskin   Sanguophage   Starjack   VRESaurids_Saurid   Waster   Yttakin
guy762_debugxenotype_droid
```

`Impid` also carries a vanilla Biotech FactionDef, `TribeSavageImpid` — check whether
that faction (or any other of these 14) is actually placed on the frozen Ash'karr
world (per CLAUDE.md's "there is no worldgen feature... one hand-made, frozen world"
— a faction absent from that hand-made placement is already effectively absent from
every player's game, which changes the removal calculus for that one).

## what to assess, per xenotype

- **Role coverage**: what gameplay niche does it fill (fast/fragile raider, tough
  soldier, cave-dweller, etc.) and is there already an `RSW_RimMandrake*` species (or
  a droid kind) that covers the same niche without it?
- **Removal cost**: what references it — FactionDefs, PawnKindDefs, other genes/
  RulePackDefs sharing its GeneDef pool, any canonical-save pawn already carrying it,
  any quest/incident keyed on it. `guy762_debugxenotype_droid` in particular may be
  load-bearing debug tooling, not player-facing content — check before recommending
  removal.
- **Removal mechanism**: Cherry Picker is the sanctioned cut path (never a bare
  mod uninstall) per `rimworld-content-moderation`; note the post-cut tag/pawnkind
  reattribution check that skill requires.

## Watch out

- `PawnFlavorPhase2_Xenotype.xml` is one large `PatchOperationSequence` per
  xenotype — removing an entry means deleting its whole `<li Class=
  "PatchOperationSequence">` block cleanly, not just its content, or the XML
  structure breaks for the next entry.
- A def dump hit only proves the xenotype LOADS somewhere in the 621-mod set, not
  that it is reachable by a real pawn (faction xenotype chance, quest-only kinds,
  etc.) — verify reachability before recommending against removal on presence alone.
- This is an assessment/recommendation ticket, not an execution order — the actual
  cuts still need an owner ruling per xenotype (or per batch), same as any other
  content-removal decision.


---

# BENCH assessment, 2026-09-20

MEASURED against `defs.sqlite` `mods=617/6a41e05c828eed67`, captured 2026-09-20T07:47:24Z,
which matches the live mod list exactly. Raw output:
`Transient/xenotype_removal_footprint_20260920.txt`.

## 🔴 Two counting artifacts, caught — read this before trusting any reference count

A naive substring sweep says each of these 14 has **230–450 references**, which would make
every one of them expensive to remove. **Both sources of that number are constants that
apply to every xenotype in the game, ours included, so neither is a removal cost:**

1. **`Outland - Genetics` ships ~228 `XenotypeAscension` genes whose DESCRIPTIONS
   enumerate every xenotype by name.** Prose, not structure.
2. **Each of those same genes carries a `modExtensions` list of 136
   `DefModExt_Xenotype` entries — one per xenotype in the whole load**, including all 60+
   `RSW_RimMandrake*` species. That is why every target returned an identical ~226–228
   "structural GeneDef reference" count.

🔑 Excluding a prose field was not enough; the second artifact is genuinely structural and
still meaningless. **A count that comes out the same for every member of a set is
measuring the set, not the member.**

## The numbers that actually differ

| xenotype | own defs | PawnKindDefs | FactionDefs | read |
|---|---|---|---|---|
| **Baseliner** | 4 | **100** | **15** | ⛔ **not removable** |
| Hussar | 9 | 32 | 11 | widely wired |
| Genie | 8 | 29 | 8 | widely wired |
| Neanderthal | 17 | 26 | 9 | widely wired |
| Starjack | 27 | 21 | 6 | Odyssey-native |
| Pigskin | 12 | 12 | 6 | |
| Yttakin | 41 | 12 | 7 | large own family |
| Highmate | 8 | 10 | 3 | |
| Waster | 15 | 10 | 2 | |
| Sanguophage | 46 | 10 | **1** | self-contained |
| Impid | 13 | 9 | 4 | ← the one he spotted |
| VRESaurids_Saurid | 15 | 8 | 2 | |
| Dirtmole | 19 | 6 | 7 | |
| **guy762_debugxenotype_droid** | **0** | **0** | **0** | 🔑 **not in the load at all** |

## Findings that decide things

**1. ⛔ `Baseliner` must not be cut, and it is not really in scope.** It is vanilla's
"ordinary human — no xenotype", wired into 100 PawnKindDefs and 15 FactionDefs including
Core's `OutlanderCivil`, `TribeCivil` and `Pirate`. Removing it does not remove a
Star-Wars-foreign species; it removes *baseline humanity*. It belongs on the keep list
without further discussion.

**2. 🔑 `guy762_debugxenotype_droid` does not exist in the 617-mod load** — zero defs of
any type, zero pawnkinds, zero factions. The item asked whether it was load-bearing debug
tooling; it is not load-bearing and it is not present. ✅ And the patch that names it is
**already guarded**: `DROID_DONOR_PATCH_GATE_NODE_GUARD_1` wrapped it in a Conditional on
2026-09-19 because its gating mods (`guy762.KotORDroids`, `SWCP.GCWVehicles`) are absent
while `kotorcore` itself is active. So there is nothing to fix and nothing to cut — it is
already inert. Drop it from this item's list of 14.

**3. `Sanguophage` is the cheapest real cut by wiring** — 1 FactionDef (its own
`Sanguophages`), 10 PawnKindDefs — but it carries **46 own defs** of genes and abilities,
which is a self-contained mechanical system (deathless, hemogen, the whole vampire
fantasy). Cheap to unwire, expensive to replace. ⚠️ It is also the one with a clear Star
Wars analogue worth ruling on rather than cutting: a Sith/dark-side-corrupted longevity
line. That is a design call, not a measurement.

**4. Most of the rest ride the same generic faction xenotype sets** — `OutlanderRough`,
`OutlanderRefugee`, `Beggars`, `Pilgrims`, `PirateWaster` — from Core/Royalty/Ideology/
Biotech. ⇒ **Removing them from play is a patch to those faction xenotype sets, not a
Cherry Picker cut.** That is much cheaper and much more reversible than the item assumed,
and it leaves the defs loadable for any save that already holds a pawn carrying one.

## What needs him — one call, not fourteen

The measurement does not decide this; his taste does. But it collapses to a single
question, because the wiring is nearly uniform:

> **Do the non-Star-Wars xenotypes get CUT, or just stop being SPAWNED?**
>
> - **Stop spawning** — patch them out of the generic faction xenotype sets. They stay
>   loadable, no save breaks, no pawn loses its genes, and no player ever meets one.
>   Reversible in one file. ⇒ **Recommended.**
> - **Cut** — Cherry Picker, per `rimworld-content-moderation`, with the post-cut
>   tag/pawnkind reattribution check. Irreversible, risks the canonical save, and buys
>   nothing a spawn-block does not.
>
> Either way: `Baseliner` stays (it is baseline humanity), and
> `guy762_debugxenotype_droid` is already gone.

## Still owed after he rules

- The niche-coverage half — "does an `RSW_RimMandrake*` species already fill this role" —
  is genuine design judgment and is **not** answered here. It wants an Opus design pass against
  the canon library, per xenotype, once he has picked cut-vs-spawn-block.
- If he picks spawn-block: the list of faction xenotype sets to patch is in the raw
  output, faction by faction.


---

# FOUNDRY cut plan, 2026-10-03 (after the owner's ruling: CUT the twelve entirely)

MEASURED against the load-13 def dump (637 mods, captured 2026-10-04T05:22:20Z) by a python
walk over every def's fields, excluding description/label and `modExtensions` (the Outland
artifact above). 211 defs carry a structural reference; the ones that decide the cut:

## What the cut has to get past

1. **xenotypeSets — 17 FactionDefs, ~45 PawnKindDefs** (Core/Royalty/Ideology/Biotech/Anomaly/
   Odyssey + VFE Empire/Pirates, BigSmall, OrcClan, VRE Saurid). ✅ **DONE as slice 1,
   `ff934d915`** (`UtinniPatches/Patches/XenotypeCut_SpawnSets.xml`): one Conditional>Remove per
   xenotype at `Defs/*/xenotypeSet/xenotypeChances/<X>` (XenotypeChance loads by NODE NAME). The
   unassigned chance falls to Baseliner, so no faction or pawnkind is left unable to make a pawn.
   Five factions become all-baseliner (OutlanderRoughPig, PirateYttakin, TribeRoughNeanderthal,
   TribeSavageImpid, VRESaurids_OutlanderRoughSaurid); all five are already zeroed out of world
   creation by `FactionSlate/OnlyOurFactions.xml`. Whether any of them sits on the FROZEN world is
   UNMEASURED here (needs the canonical .rws read through `savemap.py`, never a grep). Check:
   `selftest_xenotype_cut_spawnsets.py` (217 dump references, 0 uncovered, 4 mutants red).
2. 🔴 **Sanguophage cannot simply be deleted.** `XenotypeDefOf.Sanguophage` is a
   `[MayRequireBiotech]` DefOf binding (RimSage): with Biotech active (always, per the all-DLC
   ruling) a missing def is a startup error and every engine path that compares against it reads
   null. It also owns the `Sanguophages` faction (`basicMemberKind` Sanguophage), the
   `Sanguophage`/`Sanguophage_Player` pawnkinds, the `Sanguophage` ScenarioDef, the AbilityCategoryDef
   of the same name and 46 own gene/ability defs. Slice 1 removed it only from the VFE Empire noble
   sets. ⇒ the honest shape is "unreachable, def kept": suppress the faction/scenario/quest routes,
   keep the XenotypeDef. That is a variance from "remove the definition" and goes back to him.
3. 🔴 **Our own content uses two of them.** Inhabited CharacterDefs: `Inhabited_Empire_DrillInstructorHeskVaro`
   (race Hussar) and four Wildsteam crew `Inhabited_Wildsteam_{BoKesh,HakkoVurr,PellYoon,YorrumPell}`
   (race Yttakin). Cutting the defs breaks them; each needs a Star Wars species chosen (design call).
4. **Name collision:** `Neanderthal` is ALSO a Beasts-of-the-Rim animal (ThingDef + PawnKindDef +
   Corpse/Meat, 80 RecipeDef recipeUsers). Any cut must be typed `XenotypeDef/Neanderthal`; a
   type-agnostic `cut_name` would take the animal too.
5. `lazyfridaystudio.genesexpandedeyes` ships 12 `GeneGroups` defs named after these xenotypes;
   `PawnFlavor/Patches/PawnFlavorPhase2_Xenotype.xml` re-flavours them (delete each whole
   `PatchOperationSequence` block when its def goes — the patch would otherwise fail red).
6. **The canonical save:** any saved pawn carrying one of the twelve loses its xenotype on load
   once the def is gone (Scribe "Could not load reference"). UNMEASURED; read the save first.

## 🔑 The ruling's own premise is wider than the list

*"Only Star Wars xenotypes are supposed to be here."* The load holds **115 XenotypeDefs**:
70 ours (`mandrake.rsw.starwarsraces`) + 1 `RSW_Jawa_Xeno_Gamorrean`, the 12, Baseliner — and
**32 more non-Star-Wars xenotypes nobody listed**: AlphaGenes 15 (`AG_*`, `VRE_Ocularkin`),
Phytokin 3, the det.* singles (Avaloi, Bogleg, Brawnum, Buzzer, Keshig, Venator), BX_Beliar,
HBX_Highborn, KAR_Orc, VRE_Archon, VRE_Fungoid, XylTitan, BS_FrostJotunInBlue. `DV_Buzzer`
alone is 12.4% of PirateWaster. Filed for him as one question, not 32.

## Split
- `VANILLA_XENOTYPE_CUT_SPAWNSETS_1` — slice 1, closed `ff934d915`.
- `VANILLA_XENOTYPE_DEFCUT_1` — slice 2: Cherry Picker typed cuts of the eleven, PawnFlavor block
  deletion, Inhabited repoint, save read; Sanguophage as "unreachable, def kept" pending his word.
- `NONSW_XENOTYPES_SCOPE_1` (BENCH, needs owner) — do the other 32 go the same way?
