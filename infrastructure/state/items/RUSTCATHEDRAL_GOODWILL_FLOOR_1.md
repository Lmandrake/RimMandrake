# RUSTCATHEDRAL_GOODWILL_FLOOR_1

## spec
The Rust Cathedral hum composite is `irritation - goodwill x 0.5` (RM_MapComponent_BiomeAttitude.ComputeBand), with goodwill read from `Faction.OfMechanoids`. In this campaign that is the vanilla Mechanoid faction relabelled the Forgotten Arsenal (UtinniPatches/Patches/ForgottenArsenal.xml), and its def keeps `permanentEnemy true`. RimSage-read 2026-10-03: `Faction.CanChangeGoodwillFor` returns false whenever either side is permanentEnemy, so every `TryAffectGoodwillWith` in the kit (worst-band drain, fishing, drill response) is a no-op; and a permanent enemy's base goodwill is expected to sit at -100, which floors the composite at +50 = band 2 for ever. If so, bands 0-1 (the calm hum, the dance) cannot occur and the slow layer never moves.

MEASURE FIRST: the `calm_bands_reachable` component of `src/RimMandrake/RustCathedral/validation.py` (static_call `RimMandrake.RustCathedral.Hum.RM_RustCathedralHumProof.ProofLadder`) reads the live goodwill. If it reads -100, choose the slow layer's source: a real non-permanent-enemy Forsaken faction, or the component keeping its own standing value. That is a design call; record the choice here before building.

## choice (2026-10-06, FOUNDRY)
The component keeps its own standing. `RM_MapComponent_BiomeAttitude` saves an int `standing` in [-100, 100], seeded from the def's new `standingStart` (0 for the Cathedral), and `ComputeBand` reads it instead of `Faction.OfMechanoids` goodwill. The worst-band drain, the eel catch cost (`RM_CathedralFishing`) and the drill response's -25 all go through `RM_MapComponent_BiomeAttitude.AffectStanding`. The Forgotten Arsenal faction is still the raider and sacred-wall owner, and none of its relations are touched. Proof: `RM_RustCathedralHumProof.ProofLadder` now reports `standing`, and the new `ProofDrain` runs one real drain step and restores. `calm_bands_reachable` in `validation.py` asserts both. Nothing restores standing yet, so it only goes down.

## criteria
calm_bands_reachable PASSES live; the goodwill drain is shown to move the value it reads.
