# VENOMVINE_LIVE_VERIFY_1 — quicktest the venomvine's contact venom in a live game

## what is wrong

`VENOMVINE_CONTACT_VENOM_BUILD_1` built the whole mechanism offline and closed:
`RM_Venomvine`, `RM_VenomvineScratch`, `RM_VenomvineVenom`, the
`CompContactVenom` / `MapComponent_ContactVenom` / `ContactVenomImmunity`
triple, three Mod Settings, and the `RUT_Desert` wiring. It compiles clean and
every def validates. **Nothing has been seen running.**

## why a live check is owed — the one line the gate asks for

🔑 **The NEW mechanism never once observed is "a `MapComponent` damages a pawn
for standing on a registered cell."** Nothing in this repo has done that
before: every existing hazard in `mandrake.rm.environmentalhazards` damages
from a gas grid, a hediff comp, a game condition or a death action, never from
a per-tick cell-occupancy sweep. The registration path (a `ThingComp` on a
Long-ticking plant putting its cell into a map-wide set on spawn and taking it
out on despawn) is likewise new, and the failure mode if it is wrong is
SILENT — a stand that simply never scratches reads exactly like a stand nobody
walked into.

Everything else in the build is ordinary and is NOT what this item is for: the
plant def is a plant def, the DamageDef copies Core's own `ScratchToxic`
shape, and the hediff is a hediff.

## the work

`design/Jawa/worldbuilding/desert_shade_plants_design.md` §5, steps 1–6 and 8,
on a quicktest map with all five DLC (`modset_builder.py` tiers all set
`dlc: True` since 2026-09-19):

1. Spawn a stand; walk a colonist through it — exactly one
   `RM_VenomvineScratch` injury on a leg, `RM_VenomvineVenom` at ~0.12,
   decaying to 0 in ~6 h.
2. Park a colonist inside for 3 in-game hours — one scratch per hour, venom
   past 0.30 (serious stage visible). A downed pawn left inside reaches
   `lethalSeverity` in ~9 h with "Contact venom can kill" on, and never with
   it off.
3. Cut a vine from an adjacent non-vine cell — no scratch. Cut one whose only
   adjacent cells are vine — scratch on the hour. (This is intended, per the
   build item's own "Watch out"; do not "fix" it.)
4. A flying creature (any Core bird) crosses the stand — nothing.
5. A race carrying `ContactVenomImmunity` crosses — nothing. Nothing in the
   repo carries that extension yet, so this step needs a throwaway def or a
   runtime-added extension.
6. Full Sharp leg armour — scratch reduced; when reduced to 0, no venom at
   all.
8. Save/load mid-contact — the per-pawn clock survives (`ExposeData`) and no
   double scratch fires on load.

Also worth watching for, since neither can be seen offline:

- The registration path under **map generation**: `RM_Venomvine` is wild-spawned
  by `WildPlantSpawner`, so its comps register during map gen. Confirm a
  wild-grown stand (not a dev-spawned one) is armed.
- `pathCost 60` in practice — a sparse stand should be threaded and a solid
  band detoured when the detour is cheaper, per the design's avoidance rule.

## criteria

Every step above observed, or the defect it found filed. A step that cannot be
staged (step 5 needs a def that does not exist) is recorded as not-run rather
than passed.
