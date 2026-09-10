# Cryptoforge KCSG layouts — authoring reference only

`CRYPTOFORGE_HARVEST_RETIRE_1`. Raw copy of the 38 `KCSG.StructureLayoutDef`
entries (across the 11 `CryptoforgeMaps_*.xml` files below, plus the
`CryptoforgeSettlementLayout.xml` wiring file) from *Vanilla Quests Expanded
- Cryptoforge* (Steam Workshop item 3461526070), taken before that mod is
retired from the mod list.

**Not shippable as-is.** Every grid cell in these files names a third-party
`KCSG.SymbolDef` (or a bare ThingDef/PawnKindDef that resolves only because
Cryptoforge itself supplies it). Before any of this layout grammar is used
to build a real RUT_/RSW_ structure, strip every cell down to symbols we own
— our own `KCSG.SymbolDef` wrappers (see `gen_vault_layouts.py`'s pattern in
`src/RimUtinni/StructureInjectionsRUT/Source/VaultDungeons/`) or vanilla/DLC
bare names. Read as grid GRAMMAR (room shapes, prop density, wall thickness),
never copy a cell verbatim.

Folders mirror the donor's own `Defs/CustomGenDefs/` layout:
`Cryptoforge/` (3), `Cryptoforge_Bow/` (3), `Cryptoforge_Stern/` (3),
`ScanningBase/` (2 layouts + the settlement-layout wiring file).
