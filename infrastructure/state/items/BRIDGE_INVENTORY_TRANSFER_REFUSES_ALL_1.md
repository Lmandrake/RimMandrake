# BRIDGE_INVENTORY_TRANSFER_REFUSES_ALL_1 — jawa/inventory_transfer refuses everything on the live list

Found 2026-09-01 while live-verifying `SETTLEMENT_VERBS_WAVE_1`'s claim-fee
gizmo (needed a colonist carrying silver to test the "pay" path).

## spec
`jawa/inventory_transfer` (`mode=add`) refused every attempt this session:
2 different colonists (Dora `Thing_Human1073`, Vie `Thing_Human1077`), 2
different item types (`Silver`, `MealSurvivalPack`), counts from 500 down
to 1 — always `TryAddOrTransfer moved 0 of N <def> into <name>'s inventory
- the container refused it (not acceptable, over capacity, or already
there)`. Both target pawns were freshly-spawned quicktest colonists at full
health with no obvious inventory-blocking trait/hediff. This is on the
owner's real 592-mod full list (not the 13-mod minimal list this tool was
presumably built/tested against) — a mod interaction (e.g.
`mehni.pickupandhaul`, or something else overriding
`Pawn_InventoryTracker`'s container acceptance) is the leading suspect,
unconfirmed.

## verify
- Reproduce standalone (not blocking on another item): spawn a quicktest
  colonist, attempt `jawa/inventory_transfer` add for a trivial item
  (`MealSurvivalPack`, count 1), confirm the refusal reproduces in
  isolation.
- Bisect: try on the 13-mod minimal list first (does it work there at all?
  if yes, the full list is where it broke). If it fails there too, the tool
  itself has a defect regardless of mod list.
- If mod-interaction: find which mod's `ThingOwner`/`Pawn_InventoryTracker`
  override is refusing, per `rimbridge-companion` skill's discipline for
  reading the actual acceptance chain (read `CanAcceptAnyAt`/
  `GetContainerCanStoreDefUnderAmbientTemperature` overrides via Harmony
  patch inspection or source, don't guess).
- Fix or document the real cause (companion tool bug vs. a specific mod's
  restriction that needs a different route to work around).

## criteria
`jawa/inventory_transfer` (or a documented alternative route) can actually
place a common item into a live colonist's inventory on the owner's real
mod list — proven by one successful add, not just an absence of the
refusal message.

## Watch out
This blocked a real verification (`SETTLEMENT_VERBS_WAVE_1`'s pay-and-fire
path) from completing — whoever picks this up should re-run that item's
live test once fixed.

## 2026-09-02 (FOUNDRY) — offline mechanism read; mod culprit NOT identified, static search abandoned

Read the actual C# (`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchPawnKitTools.cs`,
the real `jawa/inventory_transfer` implementation — `JawaBenchPawnTools.cs`'s
similarly-named inventory branch is a DIFFERENT tool, `jawa/pawn_kit`, not this
one, don't confuse the two files again). It calls
`p.inventory.innerContainer.TryAddOrTransfer(found, requested, true)` on the
real `ThingOwner<Thing>` — company's own tool logic is correct and matches
its own doc comment.

Traced the real vanilla mechanism (`ThingOwner.TryAdd` → `CanAcceptAnyOf` →
`GetCountCanAccept`, all read via RimSage against decompiled 1.6 source,
`./Source/Verse/ThingOwner.cs`): `GetCountCanAccept` is `virtual`, and when
`maxStacks == 999999` (the default, unlimited) it unconditionally returns
`item.stackCount` — i.e. **a pristine, empty `Pawn_InventoryTracker` should
ALWAYS accept a first item under vanilla rules.** A 100%-refusal across 2
colonists, 2 unrelated defNames and counts 500→1 is therefore near-certainly
either (a) a Harmony patch on the virtual `GetCountCanAccept`/`CanAcceptAnyOf`/
`TryAdd` chain, or (b) something constructing `Pawn_InventoryTracker`'s
container with a non-default `maxStacks`/capacity gate (a "no backpack, no
capacity" pattern). This narrows the hypothesis from "some interaction" to
"specifically a virtual-method override on this exact chain" — a real
finding, not just restating the original suspicion.

**Mod-culprit identification NOT completed.** Grepped
`ModsConfig.FULL.LATEST.xml`'s 593 active packageIds for
backpack/haul/inventory/capacity-shaped names and found 6 real candidates:
`mlie.mercerbackpacks` (name strongly suggests exactly this "no backpack, no
capacity" pattern — the single strongest lead), `mehni.pickupandhaul`
(original suspicion), `fuu.autostriponhaul`, `memegoddess.buildfrominventory`,
`haecriver.injuredcarry`, and our own `mandrake.rm.theft_hauler`. Could NOT
confirm which one via static analysis: a full-text grep across the ~1300-mod
Steam Workshop tree for `mercerbackpack`/`pickupandhaul` (both case-sensitive
and `-i`) returned **zero hits over WSL/9p**, including on mods known to be
installed and active — this filesystem path is not reliably greppable at this
scale (consistent with this project's other documented 9p-slowness pain
points), not evidence the mods are absent. `Player.log`/`Player-prev.log`
don't log mod display names at startup in any greppable form either (checked
against a known-active mod, `mehni.pickupandhaul`, as a control — zero hits
there too, confirming this is a search-method failure, not a real absence).
RimSage's source index (`mcp__rimsage__search_source`) only covers decompiled
VANILLA game source, not mod assemblies — confirmed by a zero-hit control
query. Abandoning the static hunt here per this item's own verify section's
allowance to stop and hand off rather than loop.

**What would resolve this in under a minute, live, that I could not do
offline:** once the bridge is free, `Harmony.GetAllPatchedMethods()` compared
against `AccessTools.Method(typeof(Verse.ThingOwner), "GetCountCanAccept")`
(and `"TryAdd"`, `"CanAcceptAnyOf"`) will show — by name — exactly which
mod's Harmony patch (if any) is intercepting this chain, instantly and
authoritatively, no file-tree search needed. If nothing shows there, check
whether `Pawn_InventoryTracker`'s `innerContainer.maxStacks` reads something
other than `999999` on a live pristine colonist (reflect it via
`jawa/thing_stats` or a raw field read if one exists) — that's the (b)
hypothesis. Either check is a single bridge call once the bridge is free
again; this is genuinely a live-diagnosis problem now, not a source-reading
one.
