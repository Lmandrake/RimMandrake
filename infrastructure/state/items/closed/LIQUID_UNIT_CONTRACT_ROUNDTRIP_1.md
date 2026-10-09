# LIQUID_UNIT_CONTRACT_ROUNDTRIP_1 — FL-6/X-14: FlowWorks: one liquid-unit contract and an offline round-trip selftest (pond, canal, pump, tank, container, pour back)

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row FL-6/X-14 (belt hygiene pass 2 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). Scope: Selftest chaining RM_PumpMath.TankUnitsPerLevel, LiquidDef unitsPerBucket/Barrel/Bottle and RM_ContainerMaterials.UnitsIn proves nothing appears or vanishes when systems join; one-paragraph unit contract in the FlowWorks design doc. Before the tanker and the Bazaar broker move bulk liquid between maps (BAZAAR_BROKER_TAB_1).

The row:

| FL-6 | Robustness: one liquid-unit table, plus a single offline test that carries liquid all the way round. The route is pond → canal → pump → tank → barrel/bucket/bottle (each container material) → pour back. The test proves nothing appears or vanishes when systems join. This matters most once the tanker and the Bazaar broker move bulk liquid between maps. | A selftest that chains RM_PumpMath.TankUnitsPerLevel, LiquidDef unitsPerBucket/Barrel/Bottle and RM_ContainerMaterials.UnitsIn. A one-paragraph unit contract in the FlowWorks design doc. | S | low | FlowWorks; TheBazaar (BAZAAR_BROKER_TAB_1) | RM_PumpMath.cs:9 (5 units per level) and the RM_LiquidDefRegistry.xml unitsPer* fields. FLOWWORKS_CONTAINER_MATERIALS_1 (live) scales capacity by material. The existing conservation tests are kernel-only (Program.cs:426, SequenceFuzz ledger) and never cross into containers. |

| X-14 | **One liquid-unit contract, plus a round-trip test** from pond to canal, pump, tank, barrel, bottle and back, before the Bazaar broker moves bulk liquid between maps. | FL-6 | S | low | FlowWorks, TheBazaar | `RM_PumpMath`, the `unitsPer*` registry fields. The Bazaar already seeds boiling water |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: new selftest case passes with a can-fail (a mutated factor breaks conservation); design doc carries the unit contract paragraph.
