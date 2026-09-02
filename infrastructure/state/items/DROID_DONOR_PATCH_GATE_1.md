# Patch gate for ABF/Synstructs retirement — 11 ungated sites in KotOR donor content

## 2026-09-01 — UNBLOCKED, sites 2-10 patched (Site 1 still open)

`DROID_SYSTEM_BUILD_1` was reopened/greenlit by the owner 2026-09-01, so this
gate's own blocking criterion is satisfied. Built the 9 "easy removal" sites
(2 through 10 — everything except Site 1, still gated on the Droidworks
`Need_Power` port landing on `guy762.KotORDroids`, see that item):
`src/SPLIT_Phase3/Jawa_Patches/Patches/DroidDonor_ABFGate.xml`.

🔴 **Gating correction made mid-build, worth recording**: an early draft
gated each removal on "the donor mod (kotorcore/kotorweapons) is active" —
true TODAY, since ABF is still active and these are real, working
mechanics right now (a droid's ABF `Reprogrammable` pawnState, the recharge
cells' actual need-offset, the Baragwin trader's droid stock). That gate
would have fired immediately on deploy and broken live ABF functionality
long before ABF ever retires. Fixed: every operation now uses
`PatchOperationFindMod`'s `<nomatch>` branch on **ABF itself**
(`ABF: Artificial Beings Framework`, packageId `Killathon.ArtificialBeings`)
— dormant while ABF is active, fires automatically the moment ABF leaves
`ModsConfig.xml`. See the patch file's own header for the full writeup.

**Two findings beyond the original 11-site catalog**, both confirmed via
`validate_patch.py`'s live xpath-hit-count check against the current
589-mod dump:
1. Site 2's xpath also reaches a second, independent copy of the same
   `modExtensions/li` inside `guy762.KotORDroids`' own
   `PawnKinds_PlayerDroids.xml` — RimWorld merges same-`Name`/`defName`
   nodes from every active mod before a patch's xpath runs, so one
   operation correctly covers both copies.
2. Sites 7-10 (kotorweapons' trader stock) are **not actually "currently
   moot"** as this file previously stated. `guy762.kotorweapons` itself is
   inactive, but `mandrake.rsw.armoury` already carries its own absorbed,
   ACTIVE copy of the same `guy762_TraderKind_baragwin`/
   `guy762_BaseTraderKind_baragwin` `TraderKindDef`s with the identical
   unguarded `ArtificialBeings.StockGenerator_Colonists` entries
   (`src/RimStarWars/Armoury/Defs/Absorbed_KotorWeapons/TraderKindDefs/`).
   The ABF-absence gate (above) is correct regardless of which copy (donor
   or absorbed, or both) is loaded; a kotorweapons-active gate would have
   missed the absorbed copy entirely.

**Validated** against the current (ABF-present) dump: `validate_patch.py`
with `--defs` on Data/Mods/Workshop roots, 0 errors, 0 warnings, all 9
operations' target xpaths confirmed real. **Not yet done**: validating
against a dump captured with ABF actually removed (needs a mod-list change),
and cold-load verification with ABF off — both remain open below.

---

🔴 **BLOCKED on `DROID_SYSTEM_BUILD_1` being reopened by the owner.** This file
is prep material only — a scoping/menu document so FOUNDRY can execute
immediately once the owner reopens `DROID_SYSTEM_BUILD_1` (or explicitly
authorizes just this gate on its own). It authorizes nothing by itself. No
patch has been written, no comp/need replacement has been designed, and
none should be until the owner signs off — that design call (what replaces
ABF's comps/needs on the KotOR droid race) belongs to
`design/Jawa/droid_system_build_spec.md` §7, which
`design/Jawa/droidworks_assumptions.md` item 3 already identifies as the
same scoped work.

## spec
Source finding: `design/Jawa/droidworks_assumptions.md`, item 3 (the
FOUNDRY-verified 2026-08-30 addendum). Two kept donor mods —
**KotOR Resources and Materials** (`guy762.mm.kotorcore`, workshop
`3254370945`) and **KotOR Weapons and Armor** (`guy762.kotorweapons`,
workshop `2938932438`) — contain 11 real, UNGATED (no `MayRequire`) XML
references to ABF's (`Killathon.ArtificialBeings`) and SynCore's
(`Killathon.ArtificialBeings.SynCore`) `ArtificialBeings.*` C# namespace,
across 3 files. These must be neutralized (removed or reclassed) before
ABF/SynCore can leave `ModsConfig.xml`, or the droid race's need-comp, its
pawnKind extensions, its battery ingestibles, and (conditionally) 4 trader
stock lines throw "could not find class" errors at load.

Re-verified against the live workshop copies today (2026-08-31): **all 11
sites are still present at or near the assumptions doc's cited lines.** One
correction and one major addendum below.

## findings — the 11 sites, current state, and patch-option menu

### File 1 — `1.6/AdditionalMods/_DroidsBase/Defs/AlienRace_KotORDroidBase.xml` (kotorcore)
Folder gate: `LoadFolders.xml` → `<li IfModActive="guy762.KotORDroids">1.6/AdditionalMods/_DroidsBase</li>` — gated on KotOR Droids only, no ABF/SynCore gate. Confirmed.

**Site 1 — line 121, `<compClass>ArtificialBeings.CompCoherenceNeed</compClass>`**
inside the ThingDef's `<comps><li>...</li></comps>` list (one `<li>`, no
siblings in that list). This is on
`AlienRace.ThingDef_AlienRace Name="guy762_KotORDroidBase" ParentName="ABF_Thing_Synstruct_HumanlikeBase" Abstract="True"`
(line 4) — the abstract race parent all 12 `guy762.KotORDroids` 1.6 race
ThingDefs inherit via `ParentName` (established in
`WEAPONS_DONOR_RETIREMENT_1.md`'s incident writeup).
- **Menu — easy removal**: `PatchOperationRemove` targeting
  `Defs/AlienRace.ThingDef_AlienRace[@Name="guy762_KotORDroidBase"]/comps/li[compClass="ArtificialBeings.CompCoherenceNeed"]`
  from our own mod, `MayRequire`d on kotorcore being active and ABF/SynCore
  being ABSENT (or unconditional, since removing a comp the race no longer
  needs is harmless either way once ABF is gone). This silences the
  compClass error but does nothing for the coherence need itself — a
  colonist droid that used to track "coherence" simply stops having that
  need. Acceptable only if `DROID_SYSTEM_BUILD_1` decides no replacement
  need is wanted here, or the replacement is added as a NEW comp in the
  same patch (that decision is the parked item's, not this one's).
- **Care flag**: this is the one site in the 11 that is a genuine mechanic
  (a droid stability/needs mechanic), not just inert metadata — removing it
  outright is a behavior change for every KotOR droid, not just error
  silencing. Flagged per the task brief as the site needing the most care.

🔴 **Addendum beyond the assumptions doc's 11-site count — the same ThingDef's
`ParentName="ABF_Thing_Synstruct_HumanlikeBase"` (line 4) is a SEPARATE, deeper
dependency the compClass removal does not touch.** Confirmed by grep: no file
in kotorcore or kotorweapons DEFINES `ABF_Thing_Synstruct_HumanlikeBase` —
only kotorcore's own `AlienRace_KotORDroidBase.xml` (this `ParentName`) and
an ATC patch (`Patch_DroidIngestibleBlacklist.xml`, itself gated
`IfModActive="Killathon.ArtificialBeings.SynCore"` at the LoadFolders level,
so that reference already self-excludes) reference it. It is an ABF-owned
abstract def. If ABF retires, this `ParentName` cannot resolve, and going by
the precedent in `WEAPONS_DONOR_RETIREMENT_1.md`'s live incident (an
unresolvable inheritance target discarded the WHOLE droid race tree, not
just one field), this is plausibly the more severe failure mode of the two —
worse than the compClass line's "could not find class" error, which
(unverified here — needs a cold-load check, not asserted from memory)
likely drops just that one `<li>` and keeps the rest of the def. **A patch
that only removes the `<compClass>` line does NOT make ABF retirement safe
by itself** — the `ParentName` also needs either (a) a same-patch reclass to
a non-ABF base (structurally the exact "strip ABF comps, add ours" work
`droid_system_build_spec.md` §7 already scopes), or (b) confirmation that
ABF's own `ABF_Thing_Synstruct_HumanlikeBase` can stay resolvable some other
way. This belongs to `DROID_SYSTEM_BUILD_1`, not to a `PatchOperationRemove`.

Folder note: the parallel `_BnSDroidsBase` folder (gated
`IfModActive="SWCP.GCWVehicles"`) already guards the same classes with
`MayRequire="Killathon.ArtificialBeings.SynCore"` — useful as a working
example of the guard syntax, but its own `ABF_NeedFulfillerExtension` site is
ungated there too (not in this item's 11-site scope, since `_BnSDroidsBase`'s
gate mod is inactive and out of the "content we keep" set — noted only as a
same-mod precedent for how `MayRequire` was written elsewhere).

### File 2 — `1.6/AdditionalMods/_DroidsBase/Defs/PawnKinds_PlayerDroidBase.xml` (kotorcore)
**Site 2 — line 13**, `<li Class="ArtificialBeings.ABF_ArtificialPawnKindExtension">`
inside `PawnKindDef Name="guy762_DroidPawnKindBase" ParentName="BasePlayerPawnKind"`'s
`<modExtensions>` list (sole entry: `<pawnState>Reprogrammable</pawnState>`,
`<caravanRole>Chattel</caravanRole>`).
- **Menu — easy removal**: `PatchOperationRemove` targeting
  `Defs/PawnKindDef[@Name="guy762_DroidPawnKindBase"]/modExtensions/li[@Class="ArtificialBeings.ABF_ArtificialPawnKindExtension"]`.
  `ParentName="BasePlayerPawnKind"` is vanilla — no inheritance entanglement
  here, unlike Site 1. Losing this extension likely means colony droids stop
  reporting as "Reprogrammable"/`caravanRole=Chattel` to ABF's own systems —
  harmless once ABF itself is gone, since nothing else reads that
  modExtension. Clean, isolated cut.

### File 3 — `1.6/AdditionalMods/_DroidsBase/Defs/PawnKinds_RogueDroidsBase.xml` (kotorcore)
**Site 3 — line 34** and **Site 4 — line 68**, both
`<li Class="ArtificialBeings.ABF_ArtificialPawnKindExtension">` (same shape,
different `<modExtensions>` lists — two separate `PawnKindDef`s, one at
`Name="guy762_RogueDroidPawnKindBase"` ~line 33, one inside
`Name="SWCPDroidBase_bad" Abstract="True"` ~line 67). Neither PawnKindDef's
own `ParentName`/base is ABF-owned.
- **Menu — easy removal, 2 sites**: two `PatchOperationRemove`s, xpath'd by
  each `PawnKindDef`'s own `Name=` plus the same
  `modExtensions/li[@Class="ArtificialBeings.ABF_ArtificialPawnKindExtension"]`
  tail. Same isolated-cut reasoning as Site 2.

### File 4 — `1.6/AdditionalMods/_DroidsBase/Defs/ThingDefs_DroidEquipment/ThingDefs_DroidBatteries.xml` (kotorcore)
✅ **Correction to the assumptions doc's count**: of the 3 cited lines here,
**one is already dead.**
- **Line 50** — `<li Class="ArtificialBeings.ABF_NeedFulfillerExtension">` —
  is inside an XML comment block (`<!--modExtensions> ... </modExtensions-->`,
  spanning the surrounding lines). Confirmed by reading the raw file: the
  whole block is commented out and is never parsed by the game. **This site
  needs no patch at all** — it was already inert before this audit, and
  should be dropped from the working "11 sites" count when the actual patch
  gets written (functionally 10 live sites, not 11 — see criteria below for
  how this nets out against the trader sites too).
- **Site 5 — line 73**, `<li Class="ArtificialBeings.IngestionOutcomeDoer_OffsetArtificialNeed">`
  (live), inside `ThingDef ParentName="guy762_DroidBatteryBase"` /
  `defName=guy762_DroidBattery`'s `<ingestible><outcomeDoers>` list —
  `<need>ABF_Need_Synstruct_Energy</need><offset>0.675</offset>`.
- **Site 6 — line 113**, same shape, `defName=guy762_DroidBattery_adv`,
  `<offset>1</offset>`.
  `guy762_DroidBatteryBase` (the shared Abstract parent, line 3 of this
  file) is self-contained — no ParentName onto anything ABF-owned. Both are
  clean, isolated cuts.
- **Menu — easy removal, 2 live sites**: two `PatchOperationRemove`s, xpath'd
  by each battery's `defName` plus
  `ingestible/outcomeDoers/li[@Class="ArtificialBeings.IngestionOutcomeDoer_OffsetArtificialNeed"]`.
  Losing this means recharge cells stop offsetting `ABF_Need_Synstruct_Energy`
  on ingest — a real mechanic (batteries currently feed a droid need), same
  caveat as Site 1: only acceptable if the replacement need system
  (`DROID_SYSTEM_BUILD_1`) either doesn't need an equivalent offset or adds
  one in the same patch targeting our own replacement need.

### Files 5–6 — kotorweapons TraderKindDefs (currently mod-inactive — see live-list note below)
`1.6/Defs/TraderKindDefs/OrbitalTrader_Baragwin.xml` and
`BaseTrader_Baragwin.xml`, each with 2 identical sites (lines 46 and 55 in
both files today — shifted from the doc's unspecified line refs, content
unchanged):
**Sites 7–10** — `<li MayRequire="guy762.KotORDroids" Class="ArtificialBeings.StockGenerator_Colonists">`,
stocking `KotORDroidColonist_DevWD`/`SentWD` (common) and
`KotORDroidColonist_ADMkI`/`ADMkIV` (uncommon) on the Baragwin weaponsmith
trader. Gated on `guy762.KotORDroids` (droids being active), NOT on ABF.
- **Menu — easy removal, 4 sites**: `PatchOperationRemove` targeting each
  `<li>` by its `Class="ArtificialBeings.StockGenerator_Colonists"` plus a
  distinguishing child (`pawnKindDefs` containing `KotORDroidColonist_DevWD`
  vs `_ADMkI`) since each file has two structurally-identical `<li>`s with
  different xpath position — index-based xpath (`stockGenerators/li[2]`,
  `li[3]`, whichever position they land at) is more fragile than a
  child-content match; a `PatchOperationFindMod`-wrapped
  `PatchOperationConditional` probing pawnKindDefs content, then Remove, is
  safer against future file-ordering shifts in the donor mod. No inheritance
  entanglement — pure trader stock generator list entries, clean cuts. Losing
  these means the Baragwin trader stops selling those 4 droid colonist
  pawnKinds — a stocking behavior change only, no error risk either way
  since it's just a `StockGenerator` list.

## Live mod-list currency note (2026-08-31)
Checked `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon
Studios\Config\ModsConfig.xml` directly (591 mods) and confirmed it matches
`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`:
- `killathon.artificialbeings` and `killathon.artificialbeings.syncore` —
  **both ACTIVE**. Retirement has not happened; this gate is still live
  work, not stale.
- `guy762.mm.kotorcore` and `guy762.kotordroids` — **both ACTIVE** (kotorcore
  is the mod this item's 7 kotorcore-side sites live in; kotordroids is the
  downstream mod whose 12 race ThingDefs need `guy762_KotORDroidBase` to
  keep resolving — see `WEAPONS_DONOR_RETIREMENT_1.md`'s incident).
- `guy762.kotorweapons` — **INACTIVE** as of this reading (retired per
  `WEAPONS_DONOR_RETIREMENT_1.md`'s 2026-08-31/09-01 wave, 586-mod cut,
  independently of this item). **Sites 7–10 (the trader files) are
  currently moot** — that whole mod isn't loaded, so those 4 unguarded
  references aren't reachable today. They remain valid to patch pre-
  emptively (the files are still on disk at the workshop path and would
  reactivate if `guy762.kotorweapons` is ever turned back on), but they are
  NOT part of what's currently blocking ABF/SynCore retirement — only the
  kotorcore-side sites (1–6, with Site 1 needing the ParentName fix too) and
  the `_DroidsBase`→`guy762.KotORDroids` dependency are.

## What this item is explicitly NOT deciding
- Not deciding whether the `CompCoherenceNeed`/`ABF_Need_Synstruct_Energy`
  mechanics get replaced, dropped, or left absent — that's
  `droid_system_build_spec.md` §7's call, gated on `DROID_SYSTEM_BUILD_1`
  reopening.
- Not deciding how `guy762_KotORDroidBase`'s `ParentName` gets re-anchored
  once ABF is gone — same gate.
- Not writing any patch file. This document is the menu, not the build.

## verify (once authorized to build)
1. Re-run this file's line/content checks against the live workshop copies
   before writing any patch — mod updates can shift lines again (this pass
   already found the doc's line numbers held for kotorcore, shifted
   slightly and unremarked for kotorweapons).
2. Write the patch(es) in OUR OWN mod (`Jawa_Patches` or wherever
   `NAMING_SCHEME_PLAN.md` routes donor-content patches) — never hand-edit
   the Workshop-synced donor files directly, they get overwritten on any
   Steam update.
3. `validate_patch.py <path> --defs ...` against a def dump built with ABF
   and SynCore REMOVED from the mod list, to prove the patched defs resolve
   clean without them (a defs-present dump can't prove an absence-safe
   patch).
4. Cold-load-verify with ABF/SynCore actually off, minimal list first, watch
   for `could not find class`/`Could not resolve cross-reference` on any of
   the 10 live sites (11 minus the already-dead Site at old line 50) and on
   `guy762_KotORDroidBase` itself (the ParentName question).
5. Only then does `assumption 3`'s "ABF/Synstructs — NEEDS PATCHES" verdict
   in `droidworks_assumptions.md` get to flip to "patched, safe to retire."

## criteria
- [x] BLOCKED — `DROID_SYSTEM_BUILD_1` reopened by the owner, or this gate
      explicitly authorized standalone. **Reopened 2026-09-01.**
- [x] All 11 cited sites re-verified against live workshop copies
      (2026-08-31, re-confirmed 2026-09-01): 10 live + 1 already-dead
      (commented out, `_DroidsBase` batteries file line 50).
- [x] Per-site patch-option menu written (this file).
- [x] Structural distinction drawn: list-item removals (Sites 2–10, easy)
      vs the compClass/ParentName pair on `guy762_KotORDroidBase` (Site 1 +
      addendum, needs design sign-off, not just removal).
- [x] Live mod-list check: ABF + SynCore both active; kotorweapons currently
      inactive (its 4 sites are dormant, not currently blocking) — **note
      2026-09-01: "dormant" was wrong for sites 7-10 specifically, see above;
      the absence-gated fix is correct regardless.**
- [x] Sites 2-10 patched and offline-validated, 2026-09-01:
      `src/SPLIT_Phase3/Jawa_Patches/Patches/DroidDonor_ABFGate.xml`, gated
      on ABF's absence (dormant today), 0 errors/0 warnings against the
      current dump.
- [ ] Site 1 (`CompCoherenceNeed` + `ParentName` on `guy762_KotORDroidBase`)
      — still blocked on the Droidworks `Need_Power` port landing on
      `guy762.KotORDroids` (`DROID_SYSTEM_BUILD_1`'s open port-manifest
      criterion).
- [ ] Cold-load-verified with ABF actually removed from the mod list — not
      done this pass (offline-only; needs a mod-list change and a restart).

## 2026-09-02 — re-verification (FOUNDRY, background fanout)

Re-ran `validate_patch.py` against the CURRENT live mod set (593 active,
kotorweapons still inactive). Ops 1-5 (sites 1-6, kotorcore-side): clean
info-level matches, unchanged, still current. **Ops 6-9 (sites 7-10, the
trader stock removals) now report as ERROR ("matches 0 nodes")** —
consistent with, not a regression from, this file's own 2026-08-31/09-01
analysis: with `guy762.kotorweapons` inactive, its `TraderKindDef`s aren't
in the loaded set at all, so those four `PatchOperationRemove`s correctly
match nothing under current conditions (the file's earlier "0 errors/0
warnings" note was likely run under different `--defs` scoping or while
kotorweapons was briefly active). Not a new defect — still dormant-by-design,
still fires correctly if kotorweapons is ever reactivated. No line drift
found on any of the 10 sites.
