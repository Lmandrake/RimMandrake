# APPROVED — the Jawa xenotype and religion are settled

**Owner's ruling, 2026-08-14 (evening).** This file is the short authoritative
record. Where any other document disagrees with it, this one wins and that one
is stale.

---

## The two decisions

| | ruling |
|---|---|
| **Xenotype** | **`MandrakeJawa` is the ONLY active Jawa xenotype.** `OuterRim_Jawa`, `guy762_xenotype_jawa` and `BTD_Jawa` are stood down. |
| **Religion** | **"The Salvation" is the approved ideoligion**, for the player faction **and** the indigenous Jawa tribes. |

## Where the artifacts live — committed, so they survive the AppData folder

| what | path |
|---|---|
| the religion | `src\Jawa\ideoligion\The Salvation.rid` |
| the xenotype, as the owner authored it | `src\Jawa\ideoligion\MandrakeJawa.xtp` |
| the xenotype, promoted to a def | `src\Jawa\Jawa_Patches\Defs\XenotypeDefs\MandrakeJawaXenotype.xml` |
| player + tribal pawnkinds | `src\Jawa\Jawa_Patches\Defs\PawnKindDefs\JawaColonistPawnKinds.xml` |
| the indigenous faction | `src\Jawa\Jawa_Patches\Defs\FactionDefs\JawaTribes.xml` |
| standing down the other three | `src\Jawa\Jawa_Patches\Patches\OnlyMandrakeJawa.xml` |
| existing pawnkinds re-pointed | `src\Jawa\Jawa_Patches\Patches\JawaXenotype_Repoint.xml` |

⚠️ **Writing these files is not deploying them.** The game reads
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Jawa_Patches`, and
nothing syncs the two — `skills/rimworld-deploy/SKILL.md`. The `.rid` and `.xtp`
are different: they belong in AppData (`Ideos\`, `Xenotypes\`) and the copies
here exist for git protection, not for the game to read.

---

## 🔴 Three engine limits that shape what "the same religion" can mean

1. **A `.rid` cannot be given to an NPC faction.** It is a fully expanded runtime
   ideo — 103 precepts, named rituals and roles, one relic. A `FactionDef` ideo
   block is a *constraint on generation*: `forcedMemes` and a name, with the
   generator filling in precepts. There is no field that accepts a `.rid`.
   ⇒ The tribes share **the name and the memes**, and therefore the doctrinal
   shape. They do **not** carry the Interment of Scrap, the Prime Trader or the
   Founding Ion Blaster. **That is an engine limit, not an omission.**
2. **A `PawnKindDef` cannot carry an ideoligion.** No such field exists in 1.6;
   a pawn takes its faction's ideo. The player's comes from loading the `.rid`
   at game start, the tribes' from their `FactionDef`.
   ⛔ XML naming a field a def does not have fails **silently**.
3. **A `.xtp` is not a def.** Custom xenotypes are loaded by the pawn editor and
   cannot be referenced by anything. That is why `MandrakeJawa` had to be
   promoted to a `XenotypeDef` — and why the two must now be kept in step by
   hand. **If the owner edits the `.xtp` in game, re-transcribe the def.**

---

## ⚠️ Two defects in the approved `.rid` — reported, not silently fixed

Measured against the live def dump on 2026-08-14. Both are real; neither was
touched, because the file is the owner's approved artifact.

1. **`AM_LovinFrequency_Exuberant` and `AM_FertilityIssue_Increased` are now
   orphaned.** Both require the **`AM_Fertility`** meme, and `AM_Fertility` is
   not in the approved meme set. `AM_LovinFrequency_Exuberant`'s `requiredMemes`
   is `[AM_Fertility]` — with the meme gone the precept has nothing to resolve
   against. **Fix: re-add `AM_Fertility`, or drop those two precepts.**

2. 🔴 **`VME_Nomad` is in the meme set, and it is the one nomadism meme measured
   as hazardous.** Its forced precept `VME_PermanentBases_Despised` runs mod C#
   with no shipped source, and **the def's own description says**: *"This precept
   will only work when using the vanilla game world system… Using other mods such
   as Caravan Adventure to leave the map won't work either."* Whether a gravship
   jump registers is **UNVERIFIED**. The penalty if it does not: **−50 mood at 60
   days** (stages measured: 15d −1 · 20d −5 · 30d −20 · 40d −30 · 50d −40 · 60d −50).

   **This is precisely the failure the owner predicted** — *"they would think
   we're building our own base each time and get upset."* It is wrong for the two
   nomadism systems that were measured, and plausible for exactly this one.

   ⇒ **`Nomadic_Preferred` already does the job safely and is already in the
   file.** It is a *precept*, costs no meme slot, and its reset is proven in
   vanilla IL: `GravshipUtility::ArriveNewMap` unconditionally stamps
   `IdeoManager.lastResettledTick`, the only field its ThoughtWorker reads.
   **Recommend dropping `VME_Nomad` and keeping `Nomadic_Preferred`.**
   ⚠️ If `VME_Nomad` is dropped, drop it from `JawaTribes.xml`'s `forcedMemes` in
   the same commit or the two religions silently diverge.

---

## The approved meme set, as it stands

`AM_Structure_Scavenger` (structure) · `Trader` · `VME_Scrapper` · `VME_Trader` ·
`VME_Nomad` — 4 normal memes, at the cap.

The cap is a **slider, not a constant**: Vanilla Memes Expanded and Alpha Memes
both patch `MemeCountRangeAbsolute`, both run on defaults (no settings file
exists for either), and the slider goes to 8. Raising it to 5 costs no reload.
