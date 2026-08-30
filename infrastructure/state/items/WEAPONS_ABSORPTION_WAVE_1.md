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

## verify
1. `python3 src/Jawa/Jawa_Armoury/Source/gen_jds_armory_absorption.py` — re-run is safe and
   idempotent; confirms the guard rail (About.xml packageId check) still resolves the right workshop
   folder before touching anything.
2. `python3 skills/rimworld-modding/scripts/validate_patch.py src/Jawa/Jawa_Armoury/Defs/ --defs
   "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data" --defs "/mnt/c/Program Files
   (x86)/Steam/steamapps/common/RimWorld/Mods" --defs src/Jawa/Jawa_Armoury` — expect 0 errors, 18
   advisory warnings (the `AudioGrain_clip` case defect, inherited from source).
3. Deploy is **NOT** done and should stay that way until rule 5's full-list-load gate: run
   `deploy_custom_mods.py --mod Jawa_Armoury --apply` only after `m3.continued.jangodsoul.starwars.bti`
   is confirmed OFF in the live `ModsConfig.xml` — deploying while it's still active duplicates every
   one of these 70 defNames.

## criteria
- [ ] Generator proven on JDS Armory (this pass) — **done**.
- [ ] Same generator (or a close variant) run on `guy762.kotorweapons` (679 defs, folder
      `2938932438`) — not started.
- [ ] Same generator (or a close variant) run on `guy762.mm.kotorcore`'s materials+apparel subset
      (1235 defs, folder `3254370945`) — not started; needs a plan for its 7 load-bearing DLLs first
      (see 2026-08-30T19:24:56Z note in ledger history: port comps into `Jawa_Armoury`'s own assembly,
      or keep the source DLL active standalone while its `Defs/` retire — undecided).
- [ ] sov.sith's 8 defs ported per the owner's 2026-08-30T20:29:22Z ruling ("Port them anyway") —
      not started; in scope for the same future pass as kotorweapons/kotorcore, not this one.
- [ ] All six source packs confirmed OFF in `ModsConfig.xml` and a full-list load shows zero
      missing-def errors before ANY absorbed pack (eweb, opturret, or this one) is actually deployed
      live — not started, gated on the owner's/FOUNDRY's retirement decision, not a generator concern.

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
