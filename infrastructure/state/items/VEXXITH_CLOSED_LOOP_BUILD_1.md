# VEXXITH_CLOSED_LOOP_BUILD_1 — the vexxith closed loop, after three answers

Split from `CAULDRON_GPT_ENRICHMENT_1` part 3. What already exists: `RM_Vexxith`
(`src/RimMandrake/Cauldron/Defs/ThingDefs_Items/RM_CauldronItems.xml`) is a Metallic stuff with
Flammability 0, high heat armour, MaxHitPoints factor 1.6. Spec: makes durable filter vessels,
vent-cap liners, an acid-proof door and gravship scab-scrapers. It stays a strong general material
(owner ruling 2026-10-03, HP x1.6).

## open questions

1. **Acid immunity hook: RULED AND BUILT.** Harmony lives in the Cauldron mod (owner card 2026-10-08), applied through the shared `PatchApplier` (`_Shared/HarmonyResilience`), toggle `vexxithAcidImmunityEnabled`.
2. **Which recipes?** Filter vessels need the Filter-Works (`CAULDRON_MECHANICS_BUILD_1` part 4);
   vent-cap liners need vents (part 3); a vexxith-stuffed vanilla door is already fireproof — is a
   distinct plate-only door wanted? Gravship scab-scrapers sit next to Scabweight, which the owner
   declined (*"None of these thanks"*) — in or out?
3. **Stance: RULED.** Vexxith stays a strong general material, MaxHitPoints x1.6; there is no "poor for weapons and walls" restriction (owner card 2026-10-08).

## verify
2026-10-09, numbers PROVISIONAL (parts 1 and 3 only; recipes in Q2 are still open and NOT built):
- Offline: `src/RimMandrake/Cauldron/selftest_cauldron.py` passes; `RM_Vexxith` statFactors MaxHitPoints 1.6 unchanged.
- Live (needs bridge): the `RM_VexxithAcidImmunity` chain in `validation.py`, plus the log census line `Harmony: patched N` tagged `RimMandrake.Cauldron` must show the TakeDamage patch applied.
