## spec — DONE 2026-08-22, recorded so the naming is not re-derived
✅ **OWNER'S RULING:** *"The Hutt settlements that are on oasis should all be named (Hutt
Lord's name)'s Palace. Other oases should occur nearby to that area too using mutators so it
can be seen they 'happen there.' The ones that are not, in the deeper desert, should have
names like (Hutt Lord's name)'s Casino or Market or Station, etc. showing they've been
reduced to providing service rather than just making a Palace."*

Applied by `src/RimMandrake/Utils/ashkarr_hutt_names.py` (deterministic, `--apply` writes).

## the eight lords — AUTHORED HERE, this is the roster
`Gorga the Immense` · `Bloatu the Ninth` · `Vexxa the Unblinking` · `Norba the Wet` ·
`Zeddo the Patient` · `Hurgo the Vast` · `Mokka the Unpaid` · `Rulla the Deep`

🔑 **`Gorga the Immense` is deliberate continuity** — the live game generated that exact name
for this faction (`jawa/inspect_string`, 2026-08-22), so a player who has met him still has.

## the two tiers
**8 PALACES** (oasis-adjacent, ≤3.9°) carry the lord's **full name and epithet**.
**11 POSTS** (deep desert, ≥15.9°) carry only the **first name** plus a job — a lord's
dignity does not travel to a toll booth.
⚠️ **The gap is clean and measured: nothing sits between 3.9° and 15.9°**, so the two tiers
are a real feature of the map, not a threshold I chose.

| palace | post |
|---|---|
| Gorga the Immense's Palace | Norba's Vault · Norba's Toll |
| Bloatu the Ninth's Palace | Bloatu's Market |
| Vexxa the Unblinking's Palace | Vexxa's Spicehouse · Vexxa's Casino |
| Norba the Wet's Palace | Rulla's Skimhouse · Rulla's Market |
| Zeddo the Patient's Palace | Zeddo's Toll · Zeddo's Station |
| Hurgo the Vast's Palace | Hurgo's Waystation · Hurgo's Kennels |
| Mokka the Unpaid's Palace | — |
| Rulla the Deep's Palace | — |

## two mistakes made and corrected — do not reintroduce them
1. ⛔ **Nearest-palace assignment gave ONE lord 8 of the 11 posts** and six lords none,
   because the palaces cluster. It read as a single Hutt owning the desert. Now capped at
   **2 per lord**, assigned shortest-distance-first.
2. ⛔ **A per-lord service counter produced six Casinos and five Markets** and never a Vault
   or Station. The type now derives from **what the place already was** — `Tollwater` →
   Waystation, `Slug Hollow` → Kennels, `The Skim` → Skimhouse, `The Reckoning` → Vault. The
   old names are replaced as ruled, but their character survives in the job.

## the oases
`Oasis` **TileMutatorDef** added to **38 tiles** — each palace tile plus its ring of
neighbours, skipping water. 🔑 **None of the Hutt settlements carried it before**; the oasis
was always the *next* tile over, which is exactly why the fiction did not read on the map.

## what this superseded
`design/Jawa/worldbuilding/faction_roster_v2.md` asserted **"Every compound sits on a
fiercely held oasis tile."** True of 8 of 19. Struck in place with the measurement and the
new two-tier doctrine.

## still open
⚠️ The `Oasis` mutator adds `Plant_TreePalm`, `Plant_RatPalm`, `Plant_Grass`, `Plant_GrayGrass`
and `Plant_Reeds` irrespective of biome — see `PLANT_LIST_MISSES_MUTATOR_ROUTE_1`. Adding 38
tiles of it slightly widens where those five plants appear. Harmless, but it is a real
consequence and the plant candidate list should be re-derived after.
