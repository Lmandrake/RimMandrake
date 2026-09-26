# MIASMA_FLORA_ROSTER_1 — 19 invented Miasma plants, replacing a donor canopy and a missing signature

**the Miasma**

🔑 **The roster IS the specification — read it, do not re-derive it from here:**
`design/Jawa/worldbuilding/biomes/miasma_flora_roster_2026-09-23.md`. Authored at the owner's
sitting of 2026-09-23. Sheet: `design/Jawa/worldbuilding/biomes/the_miasma.md`.

## why this exists

The Miasma's own sheet makes the rainbow flora **§5 always-true**, **§6 hard ban 2**, and the
whole of **§9's artistic thesis** — and the shipped biome grows **four** plants, three of them
Alpha Biomes' mangroves, not one of them a bloom. The only rainbow row it ever had,
`BMT_RainbowTongue`, was purged when `biomesteam.biomespollutedlands` retired on 2026-09-18 and
nothing replaced it. ⇒ The biome has been shipping its central promise with no plants able to
keep it.

## spec

1. **19 `RM_`-tier plant defs** per the roster's four sections: four mangals (§3), six rainbow
   blooms (§4), five carnivorous predators (§5), four muck-and-silt rows (§6). Every row's
   **silhouette FORM** column is the art commission and the review target.
2. **Organise spawn along the fresh→brine gradient**, which is the sheet's §3 geography and
   already built: `RM_GradientAxisExtension` / `RM_GradientSurgeExtension`, shipped 2026-09-13
   in `RimMandrake.EnvironmentalHazards`.
3. ⭐ **Three rows need more than one graphic and lose their entire point without it** —
   `RM_Ilbareen` (living **and** dead-standing, which is the salt-line record), `RM_Ismerrow`
   (a colour-randomised set, never one sprite), `RM_Braskeen` (open and closed).
4. **The predators draw on the arthropod floor**, not on colonists — owner ruling, decision
   taken by question card. Pair with `MIASMA_FAUNA_FLOOR_ROSTER_1`, which authors the prey.
5. Landing the content onto `RM_Miasma` belongs to `MIASMA_RM_MOD_BUILD_1`; this item owns the
   defs and art.

## verify

- `validate_patch.py <path> --defs …` on every new def file. ⚠️ An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm from a
  post-load def dump.
- Zero new Config errors in `Player.log` — 🔴 grep the log; `validate_patch.py` cannot see them.
- A quicktest map on a **scratch** world whose landing tile is the Miasma, looked at: the
  gradient must be visibly readable, and a band of dead `RM_Ilbareen` must appear where brine
  has reached.
- 🔴 **Before queueing a single art job**, search `infrastructure/artpipe/done/`, `_artsrc/`,
  `registry.jsonl` and any review sheet's `.decisions.json` by subject — the owner's standing
  rule of 2026-09-20. ⚠️ The artpipe daemon does not run on the Mac.

## criteria

Standing in the Miasma, a player sees rainbow blooms in green-gold haze because the plants
delivering that sentence exist; the canopy is ours rather than a donor's, so
`mandrake.rm.miasma` is rich standing alone; and the salt line's last reach is legible from
the landscape.

## Watch out

- 🔴 **Ban 2 binds §4 absolutely and was NOT edited by this sitting.** The blooms are
  beautiful, hopeful and genuinely benign — never a trap, never a mimic, never toxic. ⛔ A
  later pass giving any §4 row a downside has broken the ban. The §5 predators are a
  **separate clade** and are not covered by it; that distinction is the whole content of the
  owner's two-family ruling.
- ⛔ **No medicine row, ever** (sheet ban 3, ruled cut). The attar is the replacement and it is
  a cosmetic luxury.
- ⛔ **Do not add a rain dependency** (ban 5) and ⛔ no Earth-nameable label (ban 7) — the
  predators are modelled on real carnivores' *mechanisms*, never their names.
- ⚠️ **`RM_Wessaline` must not read as a trap.** The Fever Wood already owns the
  deceptive-flat-skin idea with `RM_Skimmel`; a second one dilutes it.
- ⚠️ Three of the five predators work out of sight, and a mechanic a player never sees does
  not exist. Each has a **visible consequence** written into its row on purpose — velluric's
  too-clear water, ommolyn's scuttler-free mud, braskeen's closed blades. Those are not
  decoration.
- 🔴 **Whether a plant can consume a small wild animal at all is UNMEASURABLE on the Mac.**
  Desktop question. The nearest built precedent is `RM_CompVerminBreeder` +
  `RM_MapComponent_VerminPopulation` — read it before writing new C#.
- ⚠️ **Open for the owner:** the attar is given a plant (`RM_Immarel`'s root-bed) rather than
  the terrain the sheet implies, on the precedent of his Fever Wood seep-oils ruling. §10 of
  the roster flags it; one row changes if he wants the terrain route.
- ⚠️ **Dangling reference, not resolved here:** the four purged flora rows cite
  `POLLUTED_LANDS_FLORA_PORT_1`, which exists in neither `items/` nor `items/closed/`.
