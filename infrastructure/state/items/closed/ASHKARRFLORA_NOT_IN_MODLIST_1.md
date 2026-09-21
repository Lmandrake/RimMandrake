# ASHKARRFLORA_NOT_IN_MODLIST_1 — a mod we ship is in no stored mod list, so two of its plants can never spawn

## what is wrong

`mandrake.rut.ashkarrflora` (`src/RimUtinni/AshkarrFlora`) is **absent from the owner's
618-mod list**. MEASURED 2026-09-21 by parsing `activeMods` out of
`deployed/config/ModsConfig.before-tier-desertplants.xml`, the backup taken of the live
list immediately before this session's tier swap:

```
mandrake.rut.ashkarrflora        NOT ACTIVE
mandrake.rm.environmentalhazards active
mandrake.rut.patches             active
mandrake.rm.creaturebehaviors    active
```

⚠️ Parsed, never grepped — `grep -c '<li>'` on that file returns a wrong number because it
puts many elements on one line.

**Consequence.** `RUT_Desert.xml` lists `RUT_Staggerseed` and `RUT_AridShrubland.xml`
lists `RUT_Fuzz`, both under `MayRequire="mandrake.rut.ashkarrflora"`. A `MayRequire`
whose mod is inactive **strips the entry silently** — no error, no log line — so
`DESERT_STAGGERSEED_BUILD_1`'s cycle plant and the fuzz have never been able to spawn in
the campaign, and never will until the mod is in the list. This is the second half of the
`RUT_Staggerseed` "does not resolve" finding; the first half was a deploy gap and is
fixed (see below).

## already done, do not redo

✅ **The deploy gap is closed.** The deployed folder held only
`Defs/ThingDefs_Plants/RUT_AshkarrFlora_Plants.xml`; `RUT_Staggerseed.xml`,
`RUT_Fuzz.xml` and four more def files existed only in the repo.
`deploy_custom_mods.py --mod AshkarrFlora --apply` wrote seven files on 2026-09-21, and
`selftest_deployed_biome_refs.py` went from **FAIL (2 dangling refs)** to **PASS**.

## the work

Add `mandrake.rut.ashkarrflora` to the stored FULL list, not merely the live one — a tier
restore writes the stored list back and would drop it again. `modset_builder.py` pins our
own mods to the back of the order, which is where this belongs (it is a plain def mod: no
assembly, no patches into other mods).

⚠️ Do this while no tier swap is active, and confirm against the restored list rather than
against a number written in a doc.

## criteria

The restored full `ModsConfig.xml` parses with `mandrake.rut.ashkarrflora` in
`activeMods`, and a load of that list resolves `ThingDef/RUT_Staggerseed` and
`ThingDef/RUT_Fuzz`.

## provenance

Found by `BIOMEFLORA_PATCH_WIPES_WILDPLANTS_1` while chasing that item's "RUT_Staggerseed
did not resolve as a ThingDef" note. The defs exist and are correct; nothing about them
needs building.

## state — CLOSED 2026-09-20 (`ad6d1fd57`)

`mandrake.rut.ashkarrflora` inserted into the stored
`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`, right after
`mandrake.rut.pawnflavor` (index 568) — well after `mandrake.rm.creaturebehaviors`
(index 550), so its own `loadAfter` is satisfied. `modlist_swap.py --restore --apply`
wrote it to the live `ModsConfig.xml` (619 active), and a real Steam-launched cold
load on the full list confirmed by `jawa/get_defs`: `ThingDef/RUT_Staggerseed` and
`ThingDef/RUT_Fuzz` both resolve, `modName`/`packageId` reading `mandrake.rut.ashkarrflora`.

Both defs' `texPath`s still 404 (`Things/Plant/RUT_Staggerseed`,
`Things/Plant/RUT_Fuzz` — no texture found) — pre-existing, already tracked under
`DESERT_STAGGERSEED_BUILD_1`/`STAGGERSEED_SHIPPING_NAME_1` as owed art, out of this
item's scope. The mod list gap this item was filed for is fixed.
