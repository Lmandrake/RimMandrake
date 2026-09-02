# SHIELD_MODS_LEVERAGE_1 — survey done, scoping (BENCH, 2026-09-02)

Survey: research/Jawa/shield_mods_survey_2026-09-02.md. Recommended shape:
- **Foundation: VEF's shield engine** (`CompShieldField`, MIT, already in our
  stack) — energy-drain-to-EMP-explosion is exactly the ruled
  overheat/collapse behavior, XML-tunable.
- **Extend Odyssey's NATIVE gravship shield slot** rather than duplicating a
  parallel system — two workshop mods already prove that hook works.
- **Module architecture from ED-Shields** (jaxxa, MIT): projector/converter
  modules match the ruling "same shields, install modules to increase
  switching capacity/configuration".
- ⚠️ Verify before building: VFE-Security 1.6 vs native gravship shield
  compat, and VEF point-defense's "slow projectiles intercepted MORE easily"
  reading — that is BACKWARDS from our pass-through canon
  (shd:shield-collapse-evacuate) and must be checked against source.

## Local ground-truth check (FOUNDRY, 2026-09-02) — BENCH's survey was WebSearch-only

BENCH's survey (`research/Jawa/shield_mods_survey_2026-09-02.md`) explicitly
says "No local files, mod list, or game state were touched" — this checks
its top candidates against what is ACTUALLY installed/active on this
mod stack, per the owner's own "download them for study" framing:

- `oskarpotocki.vanillafactionsexpanded.core` (VEF) — **ACTIVE**, confirmed
  in `ModsConfig.FULL.LATEST.xml`'s live 592-entry list.
- `vanillaexpanded.vfesecurity` (VFE Security, the likely actual home of
  `CompShieldField`/point-defense) — **ACTIVE**.
- Odyssey's native gravship system — **ACTIVE** (`knownExpansions` lists
  `ludeon.rimworld.odyssey`); `vanillaexpanded.gravship` is also active,
  which may be a VE compat/extension layer over the native slot, not a
  duplicate — worth confirming which owns the actual shield-slot hook
  before extending it.
- **ED-Shields is NOT present anywhere on this machine** — not in the
  592-mod active list, not found in a `<packageId>`/name scan across the
  installed Workshop tree. BENCH's own survey already flagged this mod's
  1.6 support as unconfirmed/search-snippet-derived; this confirms it also
  isn't downloaded yet. Per the owner's "look them up and download them for
  study" instruction, ED-Shields specifically needs a Workshop subscribe
  before its module-architecture pattern can be studied from real source
  rather than a search snippet.

**Also surveyed independently, before finding BENCH's item file already
existed**: `neronix17.shieldgenerators` (active) is a genuine local match,
but for the WRONG row — its `TabulaRasa.Comp_Shield`/`CompProperties_Shield`
(radius-scalable, EMP-overload-on-collapse, `interceptGroundProjectiles`)
is a kinetic/anti-projectile bubble shield, matching the ruled
`bubble-not-wall` row (a Star-Wars-style deflector, explicitly adjacent to
but distinct from L6's combat shield per the design doc's own framing), NOT
the v1 build-ladder's thermal-veil/particulate-screen environmental shields
— nothing in it models heat/cold radius mitigation. Its
`ShieldGen.CompProperties_PlasmaVenting` + `PipeSystem.CompProperties_ResourceStorage`
plasma-pipe-network IS a useful architectural precedent for the "modulated
plasma field" fuel/power economy language the owner ruled for ALL four
shields, even though the interception logic itself doesn't transfer to a
thermal/cold gate. No local mod was found that already models a
heat/cold-radius environmental gate — that comp is original work regardless
of which foundation mod is chosen.
