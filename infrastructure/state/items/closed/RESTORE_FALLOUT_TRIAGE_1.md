# RESTORE_FALLOUT_TRIAGE_1 — the restore brought back children whose families are still cut

## spec
MEASURED off the live Player.log after the 2026-09-11 batch restart (the first
load carrying the 139-reversal CherryPicker restore). Baseline =
`Transient/Player_log_before_overnight_restart_2026-09-09.log`.

| signal | today | baseline |
|---|---|---|
| `^Config error in` | 95 | 23 |
| `Could not resolve cross-reference` | 4 | 0 |
| `XML error` | 15 | 1 |
| `Exception` | 20 | 72 (better) |

The clusters, from the top-offender slice:
1. **Duplicate animal records** — `ZBiome_Grasslands: Duplicate animal record:`
   Zeer / Orray / Nuna / Iriaz / Gizka (2 each). Likely shape: the restored
   mod content re-adds biome entries our generated biome-cast patches already
   added. Hypothesis, not asserted — read the mechanism first.
2. **Orphaned juveniles** — `Could not find parent node named "RSW_<Species>"`
   for Yobshrimp / SiltLamprey / RustNipper / Mee juvenile variants: the
   juvenile defs are back (or were never cut) while their parent RSW_ defs
   remain cut. Per family: either restore the parent too, or re-cut the
   juvenile — never leave the orphan.
3. **Duplicate-key exceptions** — `item with same key already added`:
   AA_Eyeling (×3), RSW_Nuna (×2).
4. **Missing badger sounds** — 4 × `No SoundDef named Pawn_Badger_*` — probably
   a retexture/reskin whose sound donor is cut; small, but a cross-ref is a
   cross-ref.

Also observed this load, separate thread: Oracle (`mandrake.rm.oracle`) and
ScavengerEvents (`mandrake.rut.scavengerevents`) have active packageIds and
deployed DLLs but ZERO log lines — unconfirmed loaded; verify live (bridge)
before trusting either.

## verify
- [ ] Each cluster resolved by a per-family decision (restore-parents vs
      re-cut), recorded against the CherryPicker config, proven by a clean
      grep of the NEXT load's log (`^Config error in` back at/below baseline).
- [ ] `--is-cut` readback proves each change live ("present" means NOT cut).

## traps
- Cherry Picker cuts are invisible to the def dump (commonality 0) — prove
  every un-cut/re-cut against live config readback, never the dump.
- A patch that matches nothing logs nothing — silence is not success.
