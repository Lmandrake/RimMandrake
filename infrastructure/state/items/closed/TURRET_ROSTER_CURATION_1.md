# TURRET_ROSTER_CURATION_1 — every turret, spawned and judged with the owner

Owner, 2026-08-29 (verbatim, at the bench): "Add a queue item for you and I to
spawn all the turrets in the game and decide which ones go where, do what, or
are kept at all."

A live bench sitting, not an offline census: spawn every buildable turret on a
map with the owner watching, and for each one record one of — KEEP (with role:
where it belongs, what it defends), CUT (Cherry Picker, per
`rimworld-content-moderation`), or RESKIN/RETUNE (files a follow-up).

## How to run it
1. Roster first, offline: turret ThingDefs from the frozen capture —
   `building.IsTurret` / `Building_Turret` thingClass and modded equivalents;
   count is MEASURED against the capture, and Cherry Picker's existing cuts are
   subtracted (cherrypicker.py is the reader). Expect mortars, IEDs and
   mod-added crew-served pieces to blur the edge — the roster note records the
   inclusion rule chosen.
2. Live, game-up, one bridge driver: spawn them in rows on a scratch area
   (clear terrain first — footprint AND exclusion, per
   [[clear-terrain-before-build]]); the owner looks and rules; BENCH records
   each ruling as data on this item as it lands.
3. Cuts go through Cherry Picker config + the tag/pawnkind re-check the
   moderation skill mandates (a cut turret can orphan a raid strategy or a
   research row the same way a cut weapon disarms a pawnkind).
4. Placement rulings ("goes where") that name real sites (gravship, settlements,
   Homestead walls) file as follow-ups on those structures' items, not here.

## Watch out
- Spawning a turret is not proving it works: powered turrets need a circuit and
  ammo-fed ones a feed before "does what" can be judged — judge LOOKS here, and
  anything mechanical rides a powered test pad (`rimworld-layout-layers`).
- Requested-vs-actual kind: the spawn tool substitutes silently
  ([[census-requested-vs-actual-kind]]) — read back what actually stood up,
  never the request list.

## criteria
- [ ] A roster with a MEASURED count, its inclusion rule stated.
- [ ] Every roster row carries an owner ruling: KEEP(role) / CUT / RETUNE.
- [ ] Cuts landed in Cherry Picker + orphan re-check done; follow-ups filed.

## Resolution (2026-08-29, BENCH — normalization pass, owner rulings + AFK batch)
- Roster: 56 defs MEASURED, canon.yml `turrets.official_roster` (frozen 213032f2).
  Inclusion rule: live spawned array survivors of the owner's three cut passes.
- Every row ruled: decisions in `turret_register.decisions.json` (user/state),
  damage in `design/Jawa/worldbuilding/review/turret_normalization_v1.md` and the
  PLAN of `src/Jawa/Jawa_Armoury/Source/gen_turret_doctrine.py`; policy rulings
  as data in canon.yml `turrets.normalization_*`.
- Cuts: all 37 non-roster turrets now in Cherry Picker (27 added this pass,
  1485→1513 incl. Grenade_TurretPack); orphan re-check done — structure-gen
  references are benign losses; two real orphans handled (turret-pack pair cut,
  Mortars research filed onto TECH_TREE_WEAPON_GROUPS_1).
- Open: live verify at next load (run sheet COLD_LOAD_RUN_SHEET_2, TURRET
  DOCTRINE section); VGE_AnticraftCaster held for the bench; beam/control
  defaults flagged for owner veto.
