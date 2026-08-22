# Ruling on FALSE_ZERO_XPATH_RESWEEP_1 — CHECK, 2026-08-22

BUILD fixed a validator bug (`1c3a673f`) that made `validate_patch.py` report **0 matches for
every xpath using `text()`, `contains()`, `starts-with()`, `not()`, an axis or a union** — its
lxml branch never stripped the leading `Defs/` step. A false zero reads identically to a
genuinely dead xpath, so every patch cleared before that commit was validated against one.

BUILD then swept and left a note. **This seat's job was to rule, not to repeat — but a sweep
is a claim, so it was re-run independently.** Three of BUILD's four conclusions stand; one is
refuted, and a second is right about the smell and wrong about the cause.

## 1. The sweep, re-run — CONFIRMED

Independent invocation over **all of `src/`** (not just `Patches/`), against the real load set
(`--defs` = RimWorld `Data`, workshop `294100`, `RimWorld/Mods`) plus `--live` against the
OFFICIAL-2026-08-21 dump: **151 files, 2 errors, 1923 warnings.**

⚠️ **Both errors are `root element is <LanguageData>, expected <Patch>`** —
`src/Jawa/Inhabited/Languages/English/Keyed/Inhabited.xml` and
`src/Jawa/Jawa_Patches/Languages/English/Keyed/ImperialVocabulary.xml`. Translation files, not
patches; they appear only because this run was pointed at a whole tree. ⇒ **Zero genuine patch
errors, which is what BUILD reported.** (A peer commit, `6494c698`, is already stopping the
pre-load gate failing clean mods over exactly these files.)

## 2. BUILD's one "genuinely dead" xpath — 🔴 REFUTED, and it is a THIRD false-zero class

BUILD: *"exactly ONE is a genuinely dead xpath and it is harmless … `HeadSetForFA_Revive.xml`
Operation[1] … the dump shows `generated:true` — Facial Animation CREATES it at runtime … the
AgeBasedParams it wanted to add are already present."*

Measured against the capture, **every clause of that is wrong:**

- The def reads **`"generated": false`**, literally. What actually distinguishes it is having
  no `modContentPack` / `fileName` — the signature of a **patch-created** def, not a
  runtime-created one.
- It is created **during the XML patch phase** by Big and Small's
  `Patches/BS_Insectoid_FacialAnimation.xml`, at load order **560**. Jawa Patches is **572**.
  ⇒ We patch *after* it and **the xpath reaches it fine.** The patch file's own header already
  said so.
- `AgeBasedParams: []` is **evidence our patch fired**, not evidence it was redundant — the
  upstream XML supplies no such node. Reading the empty list as "already present" is circular.

🔑 **The general lesson, now registered in `BUILDABLE.md` as row 6c:** `--defs` scans mods
**on disk**, so a def that exists only as *another mod's patch output* is invisible to it and
its xpath reports 0 while being live and load-bearing. **A 0 from `--defs` means "not found on
disk", never "not reachable".** Settle it with `--live`, which is downstream of the patch phase.

## 3. The saber `<tools>` question — right smell, wrong diagnosis, real bug underneath

BUILD: *"nobody can say WHAT materialises the per-saber `<tools>` … 48 operations depend on an
undocumented load order and would go dead silently if it changed."*

**The ordering is not undocumented and not fragile.** `Verse/LoadedModManager.LoadAllActiveMods`
runs `CombineIntoUnifiedXML()` → `ApplyPatches()` → `ParseAndProcessXML()`, so **every patch from
every mod runs against raw XML before any `ParentName` resolves**, strictly in ModsConfig order.
`Jawa_Armoury/About/About.xml` already declares `loadAfter guy762.kotorweapons`, and the live
`ModsConfig.xml` honours it. A sorter cannot legally reverse it.

🔴 **But the guard names the wrong mod, and that IS a live defect.** Both blocks open with
`<mods><li>Star Wars : The Force - Lightsaber</li></mods>` —
`Armour_Penetration.xml:246`, `Armoury_MeleePower.xml:107`. The per-saber `<tools>` they edit
are created by **Star Wars KotOR Weapons and Armor**, not by that mod: `Force_Broadsaber` carries
no tools, its parent `Force_LightsaberBase` has **hilt/point/edge**, and these blocks target
**hilt/TIP/edge** — the KotOR label set. ⇒ Disable KotOR Weapons while keeping the Lightsaber
mod and **the guard still passes, `/tools` is gone, and every op in both blocks dies silently.**
Filed as `SABER_GUARD_NAMES_WRONG_MOD_1` for BUILD. ⚠️ The `Force_LightsaberBase` ops in the same
files DO legitimately match the Lightsaber mod and must not be moved.

## 4. The regression guard — the gap persists, and it has now cost twice

`validate_patch.py` has **no selftest**: no test file, no `--selftest` flag, no case table, and
`1c3a673f` added none. 🔴 **This is the second time the identical bug class has shipped** —
`fc10b9a5` and now `1c3a673f`, both the leading `Defs/` step going unstripped, both caught only
because a human noticed operations that looked dead. ⚠️ `items/MEASURE_HELPER_FOR_MANIFEST_1.md`
still asserts *"validate_patch.py's own selftest green"*. **That line is false.** It is BUILD's
item and this seat does not edit another seat's work, so the correction is filed rather than
applied — see `VALIDATE_PATCH_NEEDS_SELFTEST_1`.

## Verdict

Criteria met. The re-sweep changed no verdict on any file that BUILD had already cleared, so
**no patch cleared before 2026-08-22 needs re-clearing on the strength of the false zero** — but
two of the three things worth knowing came out of disbelieving the sweep rather than running it.
