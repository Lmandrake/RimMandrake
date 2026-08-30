## spec
Absorb all Star Wars weapons/gear content into `Jawa_Armoury`, defName-preserving, so the six
source packs can eventually retire. Two of six (the smallest, `maincrep.eweb` 8 defs and
`rpgwanderer.opturret` 3 defs) were hand-ported earlier. This pass builds the generator the item
was asking for ("Droidworks pattern, not hand-porting") and proves it on the smallest of the three
remaining packs, **JDS Armory** (`[JDS] StarWars - Armory`, packageId
`m3.continued.jangodsoul.starwars.bti`, workshop folder `3511954303`).

**Rule-6 DLL check for JDS Armory: clean pass, pure content.** Measured, not guessed — the mod folder
has zero `.dll` anywhere, and every `Class=`/`compClass=`/`verbClass=`/`workerClass=` reference across
its 5 source `Defs/*.xml` files is a stock RimWorld class (`CompProperties_Power`,
`HediffCompProperties_TendDuration`, `DamageWorker_AddInjury`, etc). Nothing to port; unlike
`guy762.mm.kotorcore` (36 DLLs, 7 load-bearing, ported earlier this item), this pack needs no C# work
at all.

**Generator: `src/Jawa/Jawa_Armoury/Source/gen_jds_armory_absorption.py`.** Differs from
`gen_droidworks_defs.py` in shape, not discipline: Droidworks needed a curated `extraction.json` and
hand-written per-field renderers because its source spanned three incompatible art frameworks
needing real classification (chassis buckets, body/head resolution, dedup). JDS Armory's source is
flat raw XML with no such transform needed, so this generator parses the 5 source `Defs/*.xml` files
directly with `ElementTree` (comment-preserving) and re-emits every element through one generic
recursive serializer — still "a generator, not hand-porting": automated, re-runnable, and it verifies
every `texPath`/`uiIconPath`/`clipPath` against the source `Textures/`/`Sounds/` tree before copying,
exactly like `gen_droidworks_defs.py`'s `verify_stem()` discipline, rather than trusting the path text.

**Run measured 74 source elements** (the item's estimate said "74 defs" — this measured count agrees
exactly), of which 70 carry a `defName` and 4 are `Abstract` parent-only defs kept for `ParentName`
resolution. All 74 written, 0 dropped. Output: 6 files across `Defs/ThingDefs/`, `Defs/DamageDefs/`,
`Defs/HediffDefs/`, `Defs/SoundDefs/` (`Absorbed_JDSArmory_{Weapons,Projectiles,Buildings,Damage,
Hediff,Sounds}.xml`). 41 textures + 18 sounds copied at identical relative paths under
`Jawa_Armoury/Textures/`/`Sounds/` (604K + 528K total — nowhere near the 50MB limit). Idempotent:
re-run twice back to back produces byte-identical output (the first run's own collision-check bug —
treating its own prior output as a foreign pack — was caught and fixed before landing; see Watch out).

**Three real defects found in JDS Armory's source, preserved verbatim and flagged, not silently
fixed** (never invent, per CLAUDE.md — a BENCH/owner call, not this script's):
1. **All 18 SoundDefs use `Class="AudioGrain_clip"`** (lowercase "clip"). The real engine class is
   `AudioGrain_Clip` (capital C — confirmed against `Absorbed_Eweb_Sounds.xml` and
   `validate_patch.py --defs`). RimWorld's `Class` attribute is case-sensitive: every one of these
   SoundDefs silently fails to resolve and the whole parent def is discarded — **in the source pack
   too, today, while it's active** (this absorption doesn't introduce the bug, it inherits it).
2. **`JDS_Blaster_Worbench`** (the workbench's abstract base) carries `Parant="BuildingBase"` — a typo
   for `ParentName`. The abstract doesn't actually inherit `BuildingBase`; the one concrete child
   (`JDS_Blastech_Workbench`) still works because it re-declares most fields itself, but anything it
   doesn't re-declare silently falls back to ThingDef's own bare defaults instead of BuildingBase's.
3. **`HediffDef defName="Burn"`** (from `ThingDefs_Hediff.xml`) collides with vanilla Core's own
   `Burn` HediffDef (also `ParentName="BurnBase"`). JDS Armory already overrides vanilla `Burn` today
   while active; the absorbed copy perpetuates the exact same override once the source retires — not
   a new collision, the same one under a new mod.

**Validation:** `validate_patch.py` static pass — 0 errors, 0 warnings (no `--defs`). With `--defs`
against RimWorld's Data + Mods folders plus `Jawa_Armoury` itself: **0 errors, 18 warnings**, all 18
being defect #1 above (the tool independently rediscovered the same case-mismatch this generator
already flagged). `ModsConfig.xml` mod count was observed to fluctuate mid-session (589 mods at one
grep, 4 at a `refresh.py --fingerprint` moments later) — almost certainly another agent's
minimal-modlist swap while holding the bridge (this item never touched the bridge). Treat "JDS Armory
is active in the live ModsConfig" as true at the moment it was grepped, not as a durable fact; it
doesn't change this pass's outcome either way (see Watch out).

## pass 3: kotorweapons + sov.sith (this pass)

**`guy762.kotorweapons` is NOT pure content — measured on two independent axes, neither guessed.**

1. **Rule-6 DLL check.** The pack ships zero of its own DLLs (1.5's `_NO_ForceLightsabers` shim is
   dead, not loaded in 1.6). But its Defs reference `Class=`/`compClass=` values from a dozen external
   namespaces. Traced every one: most (`EBSGFramework.*`, `ModularWeapons2.*`, `AthenaFramework.*`,
   `MVCF.Comps.*`, `VanillaApparelExpanded.*`, `ArtificialBeings.*`,
   `FalloutCurrencies_NonReplacement.*`, `IgnoreConfigErrors.*`) belong to independent framework mods
   outside this absorption wave that stay active regardless. `Lightsaber.ModExtension_Conductive` is
   confirmed (by DLL location) to belong to `lee.theforce.lightsaber` (workshop `3466124712`), a
   wholly separate mod — **not** `guy762.mm.kotorcore` as the earlier note guessed; that guess is now
   resolved. Four namespaces, however, ARE confirmed (by DLL filename match) to live inside
   `guy762.mm.kotorcore`'s own bundled Assemblies: `CompExtraSounds`, `MentalBreakBlocker`,
   `SecondaryMineableYield`, `SelfHediffVerb` — a subset of kotorcore's 7 previously-flagged
   load-bearing DLLs. 63 of kotorweapons' 630 measured elements reference one of these four and were
   **excluded** from this pass's output (not guessed at) — see `Absorbed_KotorWeapons_BLOCKED_manifest.txt`.
2. **New coupling this pass found, not previously recorded:** of 77 unique `ParentName` values
   referenced across kotorweapons' own Defs, only 7 resolve to abstracts defined inside kotorweapons
   itself — **the other 70 resolve to abstract ThingDefs that live in `guy762.mm.kotorcore`**
   (confirmed: `KotORRangedMakeable_OffHand` and 69 others are defined in kotorcore's
   `_BASE_SWKotORWeapons.xml`, not anywhere in kotorweapons). kotorweapons is thin content sitting on
   kotorcore's abstract base layer, not self-contained the way JDS Armory was. Same story for texture
   art: a first asset-copy pass against kotorweapons' own `Textures/` alone reported 68 "missing"
   textures; re-checked against kotorcore's `Textures/` as a fallback source, 67 of those 68 resolve
   there (shared `UI/`/`SWApparel/`/`Items/`/`Weapons/` namespace between guy762's two packs) — only
   **`Other/ShieldBubble`** is genuinely absent from both packs' art trees anywhere (a real
   pre-existing source defect, preserved verbatim, not fixed). Neither coupling blocks writing this
   pass's output (kotorcore stays active throughout, rule 5), but kotorweapons cannot fully retire
   until kotorcore's corresponding abstracts are also absorbed (criterion 2 below, not yet started).

**Generator: `src/Jawa/Jawa_Armoury/Source/gen_kotorweapons_absorption.py`.** Same discipline as
JDS Armory's, two adaptations: output mirrors the source's own ~78-file/8-subfolder layout under
`Defs/Absorbed_KotorWeapons/<subfolder>/` (a manual per-tag `OUT_TARGET` table doesn't scale past a
handful of files); and a per-element blocked-class filter (see point 1) that JDS never needed. Measured
**630 source elements** (the item's earlier "679" was an unmeasured estimate from packageId
confirmation only, not a real count — this generator's 630 is the true measured figure). 567 written
(564 with `defName`, 3 Abstract parent-only), 63 blocked (comp dependency, logged not guessed), 0
collisions. 281 textures/icons copied (67 via kotorcore's shared namespace, flagged as such in the
generator's own notes), 1 genuinely missing (`Other/ShieldBubble`). No Sounds folder in this pack, no
`clipPath` usage — nothing to copy there. Idempotent: re-run twice produced identical counts.

**`Sov.Sith` (Rimwars: Pureblood Xenotype), workshop folder `3485069256`** — the owner's
2026-08-30T20:29:22Z "port them anyway" ruling, carried out, not re-litigated. Note: the real
`About.xml` packageId is `Sov.Sith` (capitalized) — the item's own notes/ledger spelled it lowercase;
corrected here from the source, not guessed. Rule-6: clean, zero DLLs, every `Class=` is stock
(`PawnRenderNodeProperties_Eye`, `Rule_File`); its `ParentName`s (`GeneEyeColor`/`GeneJawBase`/
`HeavyBoneBase`) and its `XenotypeDef`'s ~20-gene list are all vanilla Biotech, no cross-pack coupling.
**Generator: `src/Jawa/Jawa_Armoury/Source/gen_sovsith_absorption.py`** — same shape, one addition:
its `RulePackDef` points at plain-text namer word lists (`Languages/English/Strings/Pure/{First,Last,
Nick}.txt`), copied verbatim alongside the art after the same exists-first verification texPath gets.
All 8 measured elements written (7 with `defName`, 1 abstract), 10 textures + 3 word lists copied, 0
missing, 0 collisions. First use of a `Languages/` folder in `Jawa_Armoury` — no `LoadFolders.xml`
needed (RimWorld auto-loads the standard folder name).

**Validation, both packs together with the rest of `Jawa_Armoury/Defs/` (82 files total):**
`validate_patch.py --defs` against Data + Mods + **the full Steam Workshop content root**
(`steamapps/workshop/content/294100`, required this pass — `--defs Mods` alone reported "555 of 585
active mods have no folder," because most of the live mod list, including both kotorweapons and
kotorcore, are Workshop-subscribed, not copied into the local `Mods/` folder; the earlier JDS Armory
pass's 3-path command happened to work then because the modlist was smaller at that moment, not
because Workshop content is unnecessary in general — future passes should include the Workshop root by
default) — **0 errors, 10 warnings**, all 10 the `Other/ShieldBubble` defect above. Both generators
proven idempotent by rerun.

## verify
1. `python3 src/Jawa/Jawa_Armoury/Source/gen_jds_armory_absorption.py` — re-run is safe and
   idempotent; confirms the guard rail (About.xml packageId check) still resolves the right workshop
   folder before touching anything.
2. `python3 skills/rimworld-modding/scripts/validate_patch.py src/Jawa/Jawa_Armoury/Defs/ --defs
   "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data" --defs "/mnt/c/Program Files
   (x86)/Steam/steamapps/common/RimWorld/Mods" --defs src/Jawa/Jawa_Armoury` — expect 0 errors, 18
   advisory warnings (the `AudioGrain_clip` case defect, inherited from source).
3. `python3 src/Jawa/Jawa_Armoury/Source/gen_kotorweapons_absorption.py` and
   `python3 src/Jawa/Jawa_Armoury/Source/gen_sovsith_absorption.py` — both re-runs are safe and
   idempotent, same About.xml packageId guard rail.
4. `python3 skills/rimworld-modding/scripts/validate_patch.py src/Jawa/Jawa_Armoury/Defs/ --defs
   "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data" --defs "/mnt/c/Program Files
   (x86)/Steam/steamapps/common/RimWorld/Mods" --defs "/mnt/c/Program Files (x86)/Steam/steamapps/
   workshop/content/294100" --defs src/Jawa/Jawa_Armoury` — expect 0 errors, 10 advisory warnings (the
   `Other/ShieldBubble` defect, inherited from kotorweapons' source).
5. Deploy is **NOT** done and should stay that way until rule 5's full-list-load gate: run
   `deploy_custom_mods.py --mod Jawa_Armoury --apply` only after `m3.continued.jangodsoul.starwars.bti`,
   `guy762.KotORWeapons`, and `Sov.Sith` are all confirmed OFF in the live `ModsConfig.xml` — deploying
   while any is still active duplicates its defNames.

## criteria
- [x] Generator proven on JDS Armory — **done** (pass 1).
- [x] Same generator (a close variant) run on `guy762.kotorweapons` (630 measured defs, folder
      `2938932438`) — **done** (pass 3), with 63 of those 630 held back pending the 7-DLL comp-porting
      decision (see below) — those 63 are NOT yet absorbed, tracked in
      `Absorbed_KotorWeapons_BLOCKED_manifest.txt`. Full retirement additionally needs kotorcore's 70
      abstract `ParentName` targets absorbed too (next bullet) — kotorweapons is not self-contained.
- [ ] Same generator (or a close variant) run on `guy762.mm.kotorcore`'s materials+apparel subset
      (1235 defs, folder `3254370945`) — **not started**; needs the 7-DLL comp-porting decision first
      (see 2026-08-30T19:24:56Z note in ledger history: port comps into `Jawa_Armoury`'s own assembly,
      or keep the source DLL active standalone while its `Defs/` retire — still undecided). This pass
      also found kotorweapons hard-depends on ~70 of kotorcore's abstract base ThingDefs and shares its
      texture namespace — kotorcore's absorption is a prerequisite for kotorweapons' full retirement,
      not an independent unit of work.
- [x] sov.sith's 8 defs ported per the owner's 2026-08-30T20:29:22Z ruling ("Port them anyway") —
      **done** (pass 3): all 8 measured elements absorbed clean, 0 blocked, 0 missing assets. Real
      packageId is `Sov.Sith` (capitalized), workshop folder `3485069256`.
- [ ] The 7-DLL comp-porting decision itself (port into `Jawa_Armoury`'s own assembly vs. keep
      kotorcore's DLLs active standalone) — **not started**, blocks both the 63 held-back kotorweapons
      elements and all of kotorcore's materials+apparel subset. An owner/BENCH call, not a generator
      concern.
- [ ] All six source packs confirmed OFF in `ModsConfig.xml` and a full-list load shows zero
      missing-def errors before ANY absorbed pack (eweb, opturret, JDS Armory, kotorweapons' safe
      subset, or Sov.Sith) is actually deployed live — not started, gated on the owner's/FOUNDRY's
      retirement decision, not a generator concern.

**Progress toward full absorption (defs measured across all 6 source packs, ~2260 total):** eweb 8/8,
opturret 3/3, JDS Armory 74/74, Sov.Sith 8/8, kotorweapons 567/630 absorbed + 63/630 blocked (all
630 accounted for, not all deployable), kotorcore 0/1235 (materials+apparel subset; not started). Net:
**660 defs absorbed into `Jawa_Armoury/Defs/` so far, 63 flagged pending the comp-porting decision,
1235 not yet attempted.**

## Watch out
🔴 **The generator's own collision-check is self-destructive if scoped wrong.** First implementation
scanned all of `Jawa_Armoury/Defs/` for "already-absorbed" defNames to collision-check against —
including its OWN prior output. Every rerun after the first treated its own last run as a foreign
pack and skipped 70 of 74 defs. Fixed by excluding files matching its own output-filename prefix
(`Absorbed_JDSArmory_`) from the collision baseline. Caught by literally running it twice before
calling it idempotent — do the same for the kotorweapons/kotorcore variants; a generator that
`glob`s the same dir it writes into needs this exclusion every time.

⚠️ **Graphic_Multi rotation art is not the same lookup as Graphic_Single.** First pass only copied the
bare `texPath.png`; `Things/Building/Blaster_Workbench` (the one `Graphic_Multi` def in this pack)
also needs `_south`/`_north`/`_east` suffixed siblings, which a bare-texPath copy silently misses —
the def would have loaded with a magenta/missing building sprite despite the "art copied, 0 missing"
report looking clean. Fixed: the copier now opportunistically copies any rotation-suffixed sibling
files it finds alongside the base, for every texPath, regardless of the def's own declared
`graphicClass` (cheap insurance, no def parsing needed to know which ones need it).

⛔ **Do not read "18 warnings" as "18 problems this pass introduced."** All 18 map to exactly one
pre-existing source-pack bug (`AudioGrain_clip` case typo). Fixing it is a real option for a future
BENCH pass (flip 18 attribute values, re-run, re-validate) but was deliberately NOT done here — this
generator's whole discipline is "preserve verbatim, flag loudly," matching the `Parant=` typo and the
`Burn` collision. Silently "fixing" source content this generator wasn't asked to fix is exactly the
kind of invention CLAUDE.md rules out.

🔑 **Next pass on kotorweapons (679 defs) or kotorcore (1235 defs, materials+apparel subset) should
reuse this generator's shape almost unchanged** — swap `WORKSHOP_FOLDER`/`EXPECTED_PACKAGE_ID`/
`SOURCE_FILES`/`OUT_TARGET`, keep the generic serializer, the collision-check-excluding-own-output
fix, and the rotation-aware texture copier. kotorcore additionally needs the 7-DLL comp-porting
decision settled first (see criteria) — that's new work this generator's shape doesn't cover, not a
generator bug.

🔴 **"Pure content" is a per-pack finding, never an assumption carried from a sibling pack.** JDS
Armory's clean rule-6 pass (zero DLLs, no cross-pack `ParentName`) did NOT predict kotorweapons —
zero DLLs of its own too, but 91% of its `ParentName`s and most of its "missing" art resolve only
against `guy762.mm.kotorcore`. Two packs sharing an author and a retirement wave can still have
completely different coupling profiles; check `ParentName` targets (not just `Class=`/`compClass=`)
against defNames actually DEFINED in-pack before calling anything self-contained, and check a sibling
pack's `Textures/` before calling a texPath genuinely missing.

⚠️ **`--defs Mods` alone silently under-covers a Workshop-subscribed live modlist.** This pass's first
`--defs` attempt (Data + Mods + Jawa_Armoury, the exact command the JDS Armory pass used and reported
clean) came back `UNMEASURABLE — 555 of 585 active mods have no folder under --defs`: most of the
current 585-mod `ModsConfig.xml` list, including both packs this pass absorbed, live under
`steamapps/workshop/content/294100/<id>/`, not the local `Mods/` folder validate_patch.py was pointed
at. Fixed by adding the Workshop content root as a fourth `--defs` path. The JDS Armory pass's
3-path command wasn't wrong, it was lucky — the modlist was smaller (or more locally-mirrored) at that
moment; a shared worktree's live modlist can and does change under you (see
`shared-worktree-remeasure-before-acting` memory). Include the Workshop content root by default on any
future `--defs` pass against a Workshop-subscribed source pack, not just when the plain attempt fails.

🔑 **A blocked-def manifest is a generated, regenerable artifact, not a decision.** `gen_kotorweapons_
absorption.py` writes `Absorbed_KotorWeapons_BLOCKED_manifest.txt` listing exactly which 63 defNames
were excluded and why (matched comp-class), rather than guessing whether to include or fix them. Re-run
the generator to regenerate it; don't hand-edit it, and don't treat its existence as the comp-porting
decision having been made — it's the input to that decision, not the output.
