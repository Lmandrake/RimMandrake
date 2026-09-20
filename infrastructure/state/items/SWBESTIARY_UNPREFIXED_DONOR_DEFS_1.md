# SWBESTIARY_UNPREFIXED_DONOR_DEFS_1 — donor names and dead bodies left in a shipping mod

## what is wrong

Found 2026-09-20 during `DESERT_PORT_DUPLICATE_DEFS_1`'s dedup, in
`src/RimStarWars/SWBestiary/`:

**1. Un-prefixed defNames inside a mod we ship.**
`Defs/DesertPort/RSW_DesertPortA_BodyParts.xml` defines `SWClaws`,
`SWTailAttackTool`, `SWHornAttackTool`, `SWLeftHoof`, `SWRightHoof`,
`SWLeftArmClawAttackTool`, `SWRightArmClawAttackTool`. `RSW_DesertPortA_Bodies.xml`
carries `Bogwing`, `Dewback`, `FlyingAvian`, `Reek`.

These are donor names carried through the port. Every NEW defName we ship uses
the tier grammar in `design/NAMING_SCHEME_PLAN.md` — `RSW_` for anything Star
Wars. A bare `Dewback` or `SWClaws` in our mod can collide with a donor mod
defining the same name, and RimWorld resolves a collision by keeping the last
def loaded, silently.

**2. Roughly 23 BodyDefs are now referenced by nothing** — the 18 `RSW_Body_*`
in `RSW_DesertPortB_Bodies.xml` plus `Bogwing`, `Dewback`, `FlyingAvian`, `Reek`
and `RSW_Mynock` in `RSW_DesertPortA_Bodies.xml`. The dedup kept the
pre-existing defs, whose races point at the pre-existing bodies, so the port's
bodies were orphaned. Harmless, but dead weight in a loaded mod.

⚠️ **"Roughly 23" is the dedup agent's figure, relayed, not re-measured here.**
Count it yourself before acting — a number briefed to you comes back to you.

## why it matters

The collision risk is the real one; the dead bodies are tidiness. 🔴 **A def
collision does not error.** It is the same silent-failure class the dedup just
cleared 349 of, and the fix is cheap now and expensive after something starts
depending on the bare name.

## the work

1. **Re-measure both lists.** Parse the mod; do not trust the counts above.
2. **Prefix the un-prefixed defNames** and repoint every reference in the same
   change. ⚠️ A `linkedBodyPartsGroup` / `BodyPartGroupDef` rename has to move
   with every tool that names it, or pawns lose attacks silently.
3. **Delete the orphaned BodyDefs** — but ⛔ **prove each is unreferenced across
   all of `src/` first**, including `<body>` on ThingDefs and any patch that
   might inject one. 🔴 A ported creature with a dangling BodyDef is a broken
   creature; this is the class where a wrong delete breaks pawns rather than
   silencing a sound.
4. `RSW_Mynock`'s body is referenced by `MYNOCK_FLIGHT_ART_FIRST_1`'s future
   work — **check that item before deleting that one.**

## Watch out

- ⚠️ **An existence test is not an identity test.** Prove a def is unreferenced
  by parsing, not by `grep`; a bare name like `Reek` or `Dewback` appears in
  prose, comments and other mods' files.
- ⚠️ Do this AFTER the SWBestiary art lands, not during — renaming defs while 251
  art jobs are in flight against those names invites a texPath mismatch. A
  texture binds by `texPath`, not defName, so check which way each art job is
  keyed before renaming anything.

## verify

No defName in `src/RimStarWars/SWBestiary/` lacks its tier prefix. Every BodyDef
in the mod is referenced by at least one def, or is deliberately kept with a
comment saying why. validate_patch clean of new errors; selftests N/N.

## criteria

Nothing we ship can silently win or lose a name collision with a donor mod.
