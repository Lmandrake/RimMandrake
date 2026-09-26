# SUMP_TAR_VAULT_1 — the tar larder, and extraction as the solvent's economy

Owner ruling 2026-09-24, typed on the question card (his free-text answer),
verbatim:

> "I love this, but it requires solvents to extract things or else they are
> rendered useless. So extraction is a solvent based economic need. Interesting.
> Never seen that mechanic before."

## spec

- **The vault**: a buildable tar-pit store (pit or sunk barrel-rack). Anything
  sealed in it is perfectly preserved — food, corpses, hides never rot. Sealing
  is cheap; the tar does the work. (Fiction: the trap that remembers, working for
  you — and the slow-growing dorvel makes a deep pantry matter.)
- **The catch — extraction is solvent-gated**: retrieving an item without solvent
  yields it tarred/ruined (useless). Cleaning it out costs solvent per item —
  the same acid as `SUMP_GASLIGHT_1`'s reaction (one acid, three uses). Weak
  local acid (seepwax) covers routine use, ruled generous — not a starvation
  mechanism; strong foreign acid trivializes it (trade reward,
  `BIOME_NUISANCE_NORMALIZATION_1`).
- **Implementation**: rot-stop is a container comp (vanilla-adjacent); the gate is
  an extraction bill/job consuming solvent, else the tarred variant comes out.
- **Ship candidate** (`BIOME_SHIP_CONTRIBUTIONS_1`): a vault larder module
  buildable aboard — candidate row, not yet owner-confirmed for the ship list.
- Mod Settings toggle per the standing law; tuning per `SUMP_TAR_NASTINESS_1`'s
  dirty-colony law.

## verify

Quicktest: sealed food never rots; extraction without solvent yields a ruined
item; with solvent, the clean original; solvent consumption scales per item.

## criteria

The planet's best pantry is in its nastiest biome, and the price of the archive
is paid in acid.

## build status — FOUNDRY, 2026-09-26, offline-complete, needs live proof

Built as content-only-on-top-of-existing-mechanism, per this item's own header
hint: RM_TarCoatingUtility/RM_Comp_TarCoatingSource (SUMP_TAR_NASTINESS_1,
mandrake.rm.environmentalhazards) splash tar FILTH onto terrain — the wrong
direction entirely for "seal an item into a storage building" — so this item
gets its own new comp, not a reuse.

**Lives in TheSump's own assembly** (mandrake.rm.thesump), not the shared
EnvironmentalHazards one every other Sump mechanism concentrates generic code
in — EnvironmentalHazards is a sibling FOUNDRY pass's contended file this
session, and this mechanism (one building type) has no cross-biome reuse case
the way tar-coating/tarred-hediff do. `RM_TheSump` (THESUMP_RM_MOD_BUILD_1)
already exists as a real mod with its own .csproj — confirmed this pass, not
assumed.

**The vault** — `RUT_TarVault.xml` (UtinniPatches, RUT-tier — matching
SUMP_TAR_NASTINESS_1/SUMP_GASLIGHT_1's own "RM_TheSump doesn't get the real
retier yet" stopgap posture, since that migration is SUMP_UTINNI_LAYER_1's own
scope, not this item's): `ParentName="StorageShelfBase"` (Data/Core's own
shelf chain, read in full via RimSage) — a real vanilla Building_Storage, not
a hand-rolled container. Default storage filter narrowed to Foods/Corpses/
Leathers. Research-gated on `RUT_TarRendering` — SUMP_GASLIGHT_1's own build
note flagged that ResearchProjectDef as "defined but deliberately left
UNWIRED to anything"; this pass wires it for real (ordinary manually-
completable research, not a discovery trigger — that stays
INDIGENOUS_TECH_REVISIT_1's gated scope).

**Sealing** — `RM_Comp_TarVaultSeal` (new, RM_Comp_TarVaultSeal.cs): scans the
building's own `slotGroup.HeldThings` every 60 ticks. `CompRottable.disabled`
is a real public field (confirmed via RimSage against RimWorld/
CompRottable.cs) — `CompRottable.Active => !disabled` is vanilla's own "do not
rot right now" switch (the same one CompHatcher's disableIfHatcher path
already uses), so sealing needs no RotProgress bookkeeping at all. Newly
arrived items also get `CompForbiddable.Forbidden = true` so ordinary hauling
AI cannot just re-haul them out and defeat the solvent gate. "Sealing is
cheap" needed no new job: vanilla hauling AI already carries a filter-matching
item into any Building_Storage's cells on its own.

**Extraction** — a Gizmo command ("Extract from tar vault"), not a WorkGiver/
JobDriver pair: building a real haul-to-container job needed live
verification this pass had no bridge access for, and CLAUDE.md's "never guess
a RimWorld API" rule argues against shipping an unverified custom job. The
gizmo opens a FloatMenu of sealed contents; picking one searches the whole map
for any `RUT_WeakTarSolvent`/`RUT_StrongTarSolvent` stack (either accepted,
same "either cures it" posture RUT_Tarred_Surgery.xml already uses) and
consumes 1 unit administratively (not a pre-hauled-to-the-building
requirement — flagged as real future work, not this pass's). Found: unseals
the item unchanged ("the clean original", spec's own words). Not found:
destroys the original and spawns `RUT_TarRuinedGoods` (new ThingDef, this
pass) at the same stack count — "the tarred variant comes out" (spec's own
words), one uniform ruined stand-in rather than per-category spoilage, since
food/corpse/hide each ruin differently and the spec gives no per-type
numbers to build against.

**Mod Settings**: `RM_TheSumpSettings.tarVaultEnabled` (new checkbox, default
on) — off, the vault behaves like a plain shelf (no seal, no gate), per the
standing all-off-degrades-gracefully law.

**Art**: checked `infrastructure/artpipe/done/`, `_artsrc/` and
`registry.jsonl` for "tarvault"/"tar vault"/"larder" first — 0 hits, nothing
to reuse. `gen_tarvault_placeholder.py` (UtinniPatches/art/Structures, same
flat-fill-plus-outline posture as every sibling placeholder this build wave)
generated both new textures. Real (hand-authored, reviewed) art is owed.

**Validated offline**: `dotnet build RM_TheSump.csproj -c Release` — 0
warnings/errors (1 new .cs file + csproj entry + 1 new Mod Settings toggle +
checkbox + ExposeData line). `validate_patch.py` against the live 628-mod set
(Data+Mods+Workshop) + a fresh 2026-09-26T01-08-12Z live dump on both new XML
files: 0 errors, 0 warnings — the one info line (new comp's own-assembly
Class unresolved in the dump) is the expected harmless shape a mod shipping
`Assemblies/` always gets from this validator.

**Deployed**: `deploy_custom_mods.py --apply --mod TheSump --mod
UtinniPatches`. TheSump: all of this item's own files (`RUT_TarVault.xml`,
`RUT_TarRuinedGoods.xml`, both textures, the rebuilt DLL + `.srchash`) ->
VERIFIED in sync. UtinniPatches: this item's own 4 new files (2 Defs + 2
textures) deployed and verified in sync; ⚠️ `Assemblies/RimMandrake.Utinni.
UtinniPatches.dll` FAILED to write (RimWorld running, DLL locked) — a
PRE-EXISTING sibling-pass condition, not caused by this item (this pass never
touched UtinniPatches' own C#).

**What a live proof needs** (no bridge access this pass, same as every
sibling Sump item this wave):

1. TheSump is **not currently enabled in ModsConfig** — enabling it (or
   confirming it should stay build-only until THESUMP_RM_MOD_BUILD_1's own
   activation) is a separate call, not this item's.
2. Quicktest: haul food into a built `RUT_TarVault`, confirm it gets sealed
   (forbidden overlay appears, `CompRottable.disabled` reads true via a debug
   inspect) and does not rot over many days.
3. Confirm "Extract from tar vault" gizmo appears, lists sealed contents, and
   with `RUT_WeakTarSolvent` in stock returns the exact original item
   unforbidden and un-sealed (rot resumes normally afterward).
4. Confirm extraction with zero solvent on the map destroys the original and
   spawns `RUT_TarRuinedGoods` at the same stack count.
5. Confirm the Mod Settings checkbox actually gates the mechanism (off ->
   behaves like a plain shelf).

**Known, flagged gaps** (not blocking this close): large corpses are excluded
by StorageShelfBase's own inherited hard filter cap (left unmodified rather
than guessed at); solvent consumption is administrative (map-wide, not
carried to the building first) rather than a real two-stage haul job; the
solvent/ruined-goods defNames are RUT-tier, so a standalone RM_TheSump
install without UtinniPatches degrades to "extraction always ruins" with no
error (`DefDatabase.GetNamedSilentFail`, not a `[DefOf]`) — the real fix is
SUMP_UTINNI_LAYER_1's own retier, not this item's.
